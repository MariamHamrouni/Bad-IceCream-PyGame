import pygame
import random
import sys
import time
from pathlib import Path

# --- Imports IA ---
from ai.coach.analyzer import PerformanceAnalyzer
from ai.coach.hint_manager import HintManager
from ai.utils.game_api import create_game_state_for_analyzer
from ai.enemies.roles import EnemyAI, EnemyRole
from ai.design.level_generator import LevelGenerator, LevelTheme
from ai.design.maze_generator import MazeGenerator

pygame.init()
pygame.mixer.init()

# --- CONFIGURATION ÉCRAN ---
SCREEN_WIDTH, SCREEN_HEIGHT = 820, 622
WALL_SIZE = 50
ICE_WIDTH, ICE_HEIGHT = 40, 58
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bad Ice Cream: AI Enhanced Edition")
clock = pygame.time.Clock()

# États du jeu
screens = ["start", "levels", "paused", "gaming", "help", "credits"]
active_screen = "start"

# --- CHARGEMENT RESSOURCES ---
try:
    background_surface = pygame.image.load("Resources/background.png").convert_alpha()
    background_rect = background_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
except FileNotFoundError:
    background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_surface.fill((100, 100, 150))
    background_rect = background_surface.get_rect()

# --- IA GLOBALE ---
analyzer = PerformanceAnalyzer()
hint_manager = HintManager()
last_coach_update = 0
COACH_UPDATE_INTERVAL = 0.5 
active_hints = []

# --- CLASSES ---

class Fruits(pygame.sprite.Sprite):
    def __init__(self, x, y, fruit_type, fruits_group, iceblocks):
        super().__init__()
        self.fruit_type = fruit_type
        
        # Couleurs de secours
        colors = {
            "apple": (255, 0, 0), "banana": (255, 255, 0), "grape": (128, 0, 128),
            "grapes": (128, 0, 128), "orange": (255, 165, 0), "kiwi": (0, 255, 0),
            "pineapple": (255, 200, 0)
        }
        
        # Chargement image
        self.image = None
        potential_paths = [
            f"Resources/fruits/{fruit_type}.webp",
            f"Resources/fruits/{fruit_type}.png",
            f"Resources/fruits/{fruit_type.capitalize()}.png"
        ]
        
        for path in potential_paths:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(img, (30, 30))
                break
            except:
                continue
        
        if self.image is None:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            color = colors.get(fruit_type, (255, 255, 255))
            pygame.draw.circle(self.image, color, (15, 15), 14)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.adicional = 1
        self.limite = 50
        self.counter = 0
        self.fruits = fruits_group
        self.icegroup = iceblocks

    def update(self):
        self.counter += 1
        if self.counter % 10 == 0:
            self.rect.y += self.adicional
        if self.counter >= self.limite:
            self.counter = 0
            self.adicional *= -1

class Troll(pygame.sprite.Sprite):
    def __init__(self, x, y, ice_group, troll_group, level_index=0, role_type="patroller"):
        super().__init__()
        try:
            self.image = pygame.transform.scale2x(pygame.image.load("Resources/troll/frente/part1.png"))
            self.image.set_colorkey((49, 202, 49))
        except:
            self.image = pygame.Surface((35, 45))
            self.image.fill((200, 50, 50))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect.inflate_ip(-10, -10) 
        
        self.iceblocks = ice_group
        self.level_index = level_index
        self.role_type = role_type 
        
        # --- PARAMÈTRES DE DIFFICULTÉ ---
        if self.level_index == 0:   # Niveau 1 (Très Facile)
            self.speed = 1.0
            self.aggro_chance = 60
            
        elif self.level_index == 1: # Niveau 2 (Moyen)
            self.speed = 2.0
            self.aggro_chance = 45
            
        else:                       # Niveau 3+ (Difficile)
            self.speed = 3.0
            self.aggro_chance = 10

        self.direction = pygame.math.Vector2(0, 0)
        self.move_timer = 0

    def update(self, game_state=None):
        target_player = None
        if players.sprites():
            target_player = players.sprites()[0]
        
        if not target_player or not target_player.alive: return

        self.move_timer += 1
        if self.move_timer > self.aggro_chance:
            self.move_timer = 0
            self.calculate_direction(target_player)

        self.apply_movement(target_player)

    def calculate_direction(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        
        if abs(dx) > abs(dy):
            self.direction = pygame.math.Vector2(1 if dx > 0 else -1, 0)
        else:
            self.direction = pygame.math.Vector2(0, 1 if dy > 0 else -1)

    def apply_movement(self, player):
        # Mouvement X
        self.rect.x += self.direction.x * self.speed
        if pygame.sprite.spritecollide(self, self.iceblocks, False):
            self.rect.x -= self.direction.x * self.speed
            # Glissement Y
            diff_y = player.rect.centery - self.rect.centery
            if diff_y != 0:
                self.rect.y += (diff_y / abs(diff_y)) * self.speed
        
        # Mouvement Y
        self.rect.y += self.direction.y * self.speed
        if pygame.sprite.spritecollide(self, self.iceblocks, False):
            self.rect.y -= self.direction.y * self.speed 
            # Glissement X
            diff_x = player.rect.centerx - self.rect.centerx
            if diff_x != 0:
                self.rect.x += (diff_x / abs(diff_x)) * self.speed
                
        self.rect.clamp_ip(screen.get_rect())

class IceBlocks(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.transform.scale2x(pygame.image.load("Resources/Ice_Block_horizontal.webp"))
        except:
            self.image = pygame.Surface((40, 58))
            self.image.fill((100, 200, 255))
            pygame.draw.rect(self.image, (255, 255, 255), (0,0,40,58), 2)
            
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, ice_group, trolls_group, fruits_group, all_sprites_group):
        super().__init__()
        try:
            self.image = pygame.transform.scale2x(pygame.image.load("Resources/choco/choco_andando/frente/part1.png"))
            self.image.set_colorkey((49, 202, 49))
        except:
            self.image = pygame.Surface((35, 45))
            self.image.fill((139, 69, 19))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect.inflate_ip(-10, -10) # Hitbox plus petite

        self.ice_group = ice_group
        self.trolls = trolls_group
        self.fruits = fruits_group
        self.all_sprites = all_sprites_group 
        
        self.speed = 4
        self.alive = True
        self.last_action_time = 0
        self.action_cooldown = 400
        self.facing_dir = (0, 1)

    def get_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            dx = -self.speed; self.facing_dir = (-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            dx = self.speed; self.facing_dir = (1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]: 
            dy = -self.speed; self.facing_dir = (0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: 
            dy = self.speed; self.facing_dir = (0, 1)

        if keys[pygame.K_SPACE]:
            self.break_or_create_ice()
        return dx, dy

    def break_or_create_ice(self):
        now = pygame.time.get_ticks()
        if now - self.last_action_time < self.action_cooldown: return
        self.last_action_time = now
        
        # Cible devant le joueur
        target_x = self.rect.centerx + (self.facing_dir[0] * 50)
        target_y = self.rect.centery + (self.facing_dir[1] * 50)
        target_rect = pygame.Rect(0, 0, 20, 20)
        target_rect.center = (target_x, target_y)

        # Vérifier si on touche un bloc
        hit_blocks = [b for b in self.ice_group if b.rect.colliderect(target_rect)]
        
        if hit_blocks:
            # CASSER : Supprimer le bloc
            for block in hit_blocks: block.kill()
        else:
            # CRÉER : Ajouter un bloc
            new_x = target_x - (target_x % 10)
            new_y = target_y - (target_y % 10)
            dummy_block = IceBlocks(target_x - 20, target_y - 29)
            
            # Vérifier qu'on n'écrase rien
            if not dummy_block.rect.colliderect(self.rect) and \
               not pygame.sprite.spritecollideany(dummy_block, self.trolls) and \
               not pygame.sprite.spritecollideany(dummy_block, self.fruits):
                self.ice_group.add(dummy_block)
                self.all_sprites.add(dummy_block)

    def update(self):
        if not self.alive: return
        dx, dy = self.get_input()
        
        # --- CORRECTION MAJEURE ICI : Suppression des collisions avec l'Iglu invisible ---
        
        # Déplacement X
        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, self.ice_group): self.rect.x -= dx
        self.rect.x = max(WALL_SIZE, min(self.rect.x, SCREEN_WIDTH - WALL_SIZE - self.rect.width))

        # Déplacement Y
        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, self.ice_group): self.rect.y -= dy
        self.rect.y = max(WALL_SIZE, min(self.rect.y, SCREEN_HEIGHT - WALL_SIZE - self.rect.height))

        # Collisions objets/ennemis
        pygame.sprite.spritecollide(self, self.fruits, True)
        if pygame.sprite.spritecollideany(self, self.trolls):
            print("💀 Touché !")
            self.alive = False

# --- GROUPES ---
iceblocks = pygame.sprite.Group()
trolls = pygame.sprite.Group()
fruits = pygame.sprite.Group()
players = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# --- GESTION DES NIVEAUX ---
current_level_index = 0

def load_current_level():
    global player, current_level_index

    print(f"🔄 Chargement Niveau {current_level_index + 1}...")
    
    iceblocks.empty(); trolls.empty(); fruits.empty(); players.empty(); all_sprites.empty()

    # --- NIVEAU 1 : FACILE ---
    if current_level_index == 0:
        for y in range(50, 580, 58): 
            iceblocks.add(IceBlocks(50, y))
            iceblocks.add(IceBlocks(730, y))
        
        for y in range(144, 500, 58):
            fruits.add(Fruits(110, y, "grapes", fruits, iceblocks))
            fruits.add(Fruits(690, y, "grapes", fruits, iceblocks))
            
        trolls.add(Troll(680, 100, iceblocks, trolls, level_index=0))
        player = Player(400, 500, iceblocks, trolls, fruits, all_sprites)

    # --- NIVEAU 2 : MOYEN ---
    elif current_level_index == 1:
        center_y = 300
        for x in range(80, 740, 40):
            if x < 350 or x > 470:
                iceblocks.add(IceBlocks(x, center_y))
        
        center_x = 410
        for y in range(60, 560, 58):
            if y < 250 or y > 380:
                iceblocks.add(IceBlocks(center_x, y))

        corners = [(150, 150), (650, 150), (150, 500), (650, 500)]
        for pos in corners:
            fruits.add(Fruits(pos[0], pos[1], "bananas", fruits, iceblocks))
            
        trolls.add(Troll(150, 150, iceblocks, trolls, level_index=1))
        trolls.add(Troll(650, 150, iceblocks, trolls, level_index=1))
        player = Player(200, 400, iceblocks, trolls, fruits, all_sprites)

    # --- NIVEAUX SUIVANTS : PROCÉDURAL (DIFFICILE) ---
    else:
        print("🤖 Génération Procédurale...")
        generator = MazeGenerator(cols=18, rows=10)
        diff = min(0.9, 0.3 + (current_level_index * 0.1))
        level_data = generator.generate_ice_maze(difficulty=diff)

        # 1. Blocs
        for pos in level_data['iceblocks']: 
            IceBlocks(pos[0], pos[1]).add(iceblocks, all_sprites)
        
        # 2. Fruits (Aléatoires)
        available_fruits = ["apple", "banana", "grapes", "orange", "kiwi", "pineapple"]
        for f in level_data['fruits']:
            random_fruit = random.choice(available_fruits)
            Fruits(f['pos'][0], f['pos'][1], random_fruit, fruits, iceblocks).add(fruits, all_sprites)
        
        # 3. Ennemis (Garantis)
        paths = level_data.get('paths', [])
        if not paths:
            possible_spots = []
            for x_idx in range(2, 16):
                for y_idx in range(2, 9):
                    x_pos = 50 + x_idx * 40
                    y_pos = 50 + y_idx * 58
                    is_ice = False
                    for ice in iceblocks:
                        if ice.rect.collidepoint(x_pos, y_pos): is_ice = True; break
                    if not is_ice: possible_spots.append((x_pos, y_pos))
            random.shuffle(possible_spots)
            paths = possible_spots

        num_enemies = 2 + (current_level_index - 2)
        for i in range(min(num_enemies, len(paths))):
             pos = paths[i]
             Troll(pos[0], pos[1], iceblocks, trolls, level_index=2).add(trolls, all_sprites)

        start_pos = level_data['player_start']
        player = Player(start_pos[0], start_pos[1], iceblocks, trolls, fruits, all_sprites)

    players.add(player)
    all_sprites.add(iceblocks, fruits, trolls, players)
    
    if 'analyzer' in globals(): analyzer.reset()
    print("✅ Niveau chargé !")

# --- UI Coach ---
def draw_coach_hints(surface, hints):
    font = pygame.font.SysFont("Arial", 18, bold=True)
    for i, hint in enumerate(hints):
        color = (255, 255, 0)
        if hint.priority.name == "CRITICAL": color = (255, 50, 50)
        text_surf = font.render(f"💡 {hint.message}", True, color)
        bg_rect = text_surf.get_rect(topleft=(20, 20 + i * 35))
        bg_rect.inflate_ip(10, 10)
        pygame.draw.rect(surface, (0, 0, 0, 200), bg_rect, border_radius=8)
        surface.blit(text_surf, (25, 25 + i * 35))

# --- BOUCLE PRINCIPALE ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if active_screen == "start":
                active_screen = "gaming"
                current_level_index = 0
                load_current_level()

    if active_screen == "start":
        screen.fill((0, 0, 0))
        if background_surface: screen.blit(background_surface, background_rect)
        font = pygame.font.SysFont("Arial", 50)
        text = font.render("CLIQUE POUR JOUER", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))

    elif active_screen == "gaming":
        if len(fruits) == 0:
            print("🏆 NIVEAU GAGNÉ !")
            current_level_index += 1
            load_current_level()
            pygame.time.delay(500)
            continue

        if player and not player.alive:
            print("💀 PERDU !")
            active_screen = "start"
            pygame.time.delay(1000)
            continue

        players.update()
        fruits.update()
        
        trolls_info = [{'id': id(t), 'pos': t.rect.center, 'role': t.role_type} for t in trolls]
        gs = create_game_state_for_analyzer(player.rect.center, player.alive, trolls_info,
            fruits.sprites(), iceblocks.sprites(), pygame.time.get_ticks()/1000, 0)
        
        trolls.update(gs)

        if time.time() - last_coach_update > COACH_UPDATE_INTERVAL:
            analyzer.analyze_snapshot(gs)
            active_hints = hint_manager.update(analyzer.metrics, gs)
            last_coach_update = time.time()

        screen.fill((30, 30, 30))
        screen.blit(background_surface, background_rect)
        all_sprites.draw(screen)
        draw_coach_hints(screen, active_hints)
        
        font = pygame.font.SysFont("Arial", 20)
        screen.blit(font.render(f"Niveau {current_level_index + 1}", True, (255,255,255)), (SCREEN_WIDTH-100, 10))

    pygame.display.flip()
    clock.tick(60)