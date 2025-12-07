from __future__ import annotations
import random
from typing import List, Tuple
from ai.levels.level_spec import LevelSpec, EnemySpawn

Coord = Tuple[int, int]


def gen_random_level(
    width=18,
    height=9,
    num_blocks=15,
    num_fruits=3,
    enemy_config=("chaser", "patroller", "blocker")
) -> LevelSpec:

    # -------------------------
    #   MURS (bordures)
    # -------------------------
    walls = []
    for x in range(width):
        walls.append((x, 0))
        walls.append((x, height - 1))
    for y in range(height):
        walls.append((0, y))
        walls.append((width - 1, y))

    forbidden = set(walls)

    # -------------------------
    #   BLOCS DE GLACE
    # -------------------------
    ice_blocks = []
    while len(ice_blocks) < num_blocks:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if (x, y) not in forbidden:
            ice_blocks.append((x, y))
            forbidden.add((x, y))

    # -------------------------
    #   FRUITS
    # -------------------------
    fruits = []
    while len(fruits) < num_fruits:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if (x, y) not in forbidden:
            # IMPORTANT : ajouter un nom de fruit car ton Fruit() en a besoin
            fruits.append((x, y, "grapes"))
            forbidden.add((x, y))

    # -------------------------
    #   ENNEMIS
    # -------------------------
    enemies = []
    for role in enemy_config:

        # pos de spawn
        while True:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            if (x, y) not in forbidden:
                forbidden.add((x, y))
                break

        if role == "patroller":
            # route simple horizontale → max 4 cases
            x2 = min(width - 2, x + random.randint(2, 5))
            patrol_route = [(x, y), (x2, y)]
            enemies.append(
                EnemySpawn(role=role, pos=(x, y), patrol_route=patrol_route)
            )

        elif role == "blocker":
            # target stratégique au centre
            tx = width // 2
            ty = height // 2
            if (tx, ty) in forbidden:  # si mur → décale
                ty = max(1, min(height - 2, ty + 1))
            enemies.append(
                EnemySpawn(role=role, pos=(x, y), block_target=(tx, ty))
            )

        else:  # CHASER ou autre rôle simple
            enemies.append(
                EnemySpawn(role=role, pos=(x, y))
            )

    spec = LevelSpec(
        width=width,
        height=height,
        walls=walls,
        ice_blocks=ice_blocks,
        fruits=fruits,
        enemies=enemies,
        metadata={"difficulty": "auto"},
    )

    return spec
