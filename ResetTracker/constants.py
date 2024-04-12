ADV_CHECKS = [
    ("minecraft:recipes/misc/charcoal", "has_log"),
    ("minecraft:story/iron_tools", "iron_pickaxe")
]

TIMELINES = [
    'enter_nether',
    'enter_bastion',
    'enter_fortress',
    'nether_travel',
    'enter_stronghold',
    'enter_end'
]

STAT_CHECKS = [
    ("minecraft:picked_up", "minecraft:blaze_rod"),
    ("minecraft:killed", "minecraft:blaze"),
    ("minecraft:picked_up", "minecraft:flint"),
    ("minecraft:mined", "minecraft:gravel"),
    ("minecraft:custom", "minecraft:deaths"),
    ("minecraft:custom", "minecraft:jump"),
    ("minecraft:used", "minecraft:ender_eye"),
    ("minecraft:crafted", "minecraft:diamond_pickaxe"),
    ("minecraft:used", "minecraft:ender_pearl"),
    ("minecraft:used", "minecraft:obsidian"),
    ("minecraft:crafted", "minecraft:diamond_sword"),
    ("minecraft:mined", "minecraft:stone"),
    ("minecraft:mined", "minecraft:netherack")
]

TRACKED_BLOCKS = ['minecraft:gravel',
            'minecraft:dirt',
            'minecraft:sand',
            'minecraft:soul_sand',
            'minecraft:soul_soil',
            'minecraft:stone',
            'minecraft:andesite',
            'minecraft:diorite',
            'minecraft:granite',
            'minecraft:gold_block',
            'minecraft:basalt',
            'minecraft:netherack',
            'minecraft:nether_bricks',
            'minecraft:blackstone',
            'minecraft:blackstone_wall',
            'minecraft:blackstone_slab',
            'minecraft:blackstone_stairs',
            'minecraft:gilded_blackstone',
            'minecraft:blackstone',
            'minecraft:polished_blackstone_bricks',
            'minecraft:chiseled_polished_blackstone',
            'minecraft:polished_blackstone_brick_wall',
            'minecraft:polished_blackstone_brick_slab',
            'minecraft:polished_blackstone_brick_stairs',
            'minecraft:cracked_polished_blackstone_bricks',
            'minecraft:crafting_table',
            'minecraft:oak_log',
            'minecraft:birch_log',
            'minecraft:spruce_log',
            'minecraft:jungle_log',
            'minecraft:acacia_log',
            'minecraft:dark_oak_log',
            'minecraft:warped_stem',
            'minecraft:crimson_stem',
            'minecraft:oak_leaves',
            'minecraft:birch_leaves',
            'minecraft:spruce_leaves',
            'minecraft:jungle_leaves',
            'minecraft:acacia_leaves',
            'minecraft:dark_oak_leaves'
]

TRACKED_BARTERS = [
    'minecraft:enchanted_book',
    'minecraft:iron_boots',
    'minecraft:potion',
    'minecraft:splash_potion',
    'minecraft:iron_nugget',
    'minecraft:ender_pearl',
    'minecraft:string',
    'minecraft:quartz',
    'minecraft:obsidian',
    'minecraft:crying_obsidian',
    'minecraft:fire_charge',
    'minecraft:leather',
    'minecraft:soul_sand',
    'minecraft:nether_brick',
    'minecraft:glowstone_dust',
    'minecraft:gravel',
    'minecraft:magma_cream'
]

TRACKED_FOODS = [
    'minecraft:bread',
    'minecraft:cooked_beef',
    'minecraft:cooked_chicken',
    'minecraft:cooked_cod',
    'minecraft:cooked_mutton',
    'minecraft:cooked_porkchop',
    'minecraft:cooked_salmon',
    'minecraft:enchanted_golden_apple',
    'minecraft:golden_apple',
    'minecraft:apple',
    'minecraft:rotten_flesh',
    'minecraft:golden_carrot',
    'minecraft:mushroom_stew',
]
TRACKED_MOBS = [
    'minecraft:blaze',
    'minecraft:chicken',
    'minecraft:cod',
    'minecraft:cow',
    'minecraft:creeper',
    'minecraft:enderman',
    'minecraft:endermite',
    'minecraft:ghast',
    'minecraft:hoglin',
    'minecraft:iron_golem',
    'minecraft:pig',
    'minecraft:piglin',
    'minecraft:salmon',
    'minecraft:sheep',
    'minecraft:skeleton',
    'minecraft:spider',
    'minecraft:witch',
    'minecraft:wither_skeleton',
    'minecraft:zombie',
]

TRAVEL_METHODS = [
    'minecraft:walk_on_water_one_cm',
    'minecraft:walk_one_cm',
    'minecraft:walk_under_water_one_cm',
    'minecraft:swim_one_cm',
    'minecraft:boat_one_cm'
]

HEADER_LABELS = ['Date and Time', 'Iron Source', 'Enter Type', 'Gold Source', 'Spawn Biome', 'RTA', 'Wood',
                'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End',
                'IGT', 'Gold Dropped', 'Blaze Rods', 'Blazes', 'Flint', 'Gravel','Deaths','Jumps', 'Eyes Thrown'
                , 'Diamond Pick', 'Pearls Thrown',
                'Obsidian Placed', 'Diamond Sword', 'Stone Mined','Netherack Mined'] + [i.split(':')[1] for i in TRACKED_BARTERS] + [i.split(':')[1]for i in TRACKED_MOBS] + [i.split(':')[1] for i in TRACKED_FOODS]+ [i.split(':')[1].replace('_one_cm','') for i in TRAVEL_METHODS]+['Seed']
