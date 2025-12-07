# ai/levels/level_builder.py
import pygame

# Conversion tuile -> pixels (mêmes valeurs que ton main)
TILE_W = 40
TILE_H = 58
WALL = 50  # marge autour de la grille


def build_level_pygame(spec, sprites, IceBlockCls, FruitCls, TrollCls):
    """
    Construit les sprites Pygame à partir d'un 'spec' généré par gen_random_level().

    On suppose que:
      - spec.ice_blocks : liste de (tx, ty) en coordonnées tuiles
      - spec.fruits     : liste de (tx, ty, nom)   OU (tx, ty)
      - spec.enemies    : objets avec .pos = (tx, ty) et .role (string)

    sprites : un simple namespace avec les groupes:
      sprites.iceblocks, sprites.fruits, sprites.trolls, sprites.all_sprites
    IceBlockCls, FruitCls, TrollCls : tes classes définies dans main.py
    """

    # On efface ce qui vient du niveau précédent (coté blocs/trolls/fruits seulement)
    sprites.iceblocks.empty()
    sprites.fruits.empty()
    sprites.trolls.empty()

    # ----------------
    # Blocs de glace
    # ----------------
    for tx, ty in getattr(spec, "ice_blocks", []):
        x = WALL + tx * TILE_W
        y = WALL + ty * TILE_H
        ice = IceBlockCls(x, y)
        sprites.iceblocks.add(ice)

    # -------------
    # Fruits
    # -------------
    for f in getattr(spec, "fruits", []):
        # f peut être (tx, ty) ou (tx, ty, "nom_fruit")
        if len(f) == 3:
            tx, ty, fruit_name = f
        else:
            tx, ty = f
            fruit_name = "grapes"  # par défaut

        fx = WALL + tx * TILE_W + TILE_W // 2
        fy = WALL + ty * TILE_H + TILE_H // 2

        fruit_sprite = FruitCls(fx, fy, fruit_name, sprites.fruits, sprites.iceblocks)
        sprites.fruits.add(fruit_sprite)

    # -------------
    # Ennemis (trolls)
    # -------------
    for e in getattr(spec, "enemies", []):
        tx, ty = e.pos
        ex = WALL + tx * TILE_W
        ey = WALL + ty * TILE_H

        troll = TrollCls(ex, ey, sprites.iceblocks, sprites.trolls)
        troll.role = getattr(e, "role", "chaser")

        sprites.trolls.add(troll)
        sprites.all_sprites.add(troll)
