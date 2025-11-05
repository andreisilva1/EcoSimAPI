# 🌍 Ecosystem Interaction Lists
ACTIONS_UNIVERSAL = [
    "drink_water",  # Drink water — basic hydration
    "eat",  # Eat according to diet
    "reproduce",  # Reproduce — increase population
    "age",  # Age naturally
    "rest",  # Rest or sleep to recover energy
    "move",  # Move or migrate
    "die",  # Die — natural or external causes
]

ACTIONS_PREDATOR = [
    "hunt_prey",  # Hunt prey for food
    "compete_for_territory",  # Fight to control territory
    "mark_territory",  # Mark area as their own
    "teach_hunt",  # Teach offspring how to hunt
]

ACTIONS_HERBIVORE = [
    "graze_plants",  # Eat plants or grass
    "flee_from_predator",  # Escape from predators
    "form_herd",  # Form or join herd
    "group_reproduce",  # Reproduce in groups
]

ACTIONS_POLLINATOR = [
    "pollinate_plants",  # Pollinate flowers
    "collect_nectar",  # Collect nectar for food
    "build_colony",  # Build a colony or hive
    "gather_pollen",  # Gather pollen from flowers
]

ACTIONS_OMNIVORE = [
    "hunt_small_prey",  # Hunt small animals
    "eat_fruits",  # Eat fruits or roots
    "adapt_diet",  # Adapt diet to available food
    "care_for_offspring",  # Care for offspring
]

ACTIONS_MAMMAL = [
    "breastfeed_offspring",  # Feed offspring milk
    "socialize",  # Socialize or groom
    "migrate_in_group",  # Migrate in groups
    "defend_offspring",  # Defend young from danger
]

ACTIONS_BIRD = [
    "fly_or_migrate",  # Fly or migrate to new area
    "sing",  # Communicate or attract mates
    "spread_seeds",  # Spread seeds through excretion
    "build_nest",  # Build nests for eggs
]

ACTIONS_REPTILE = [
    "bask_in_sun",  # Warm body with sunlight
    "hibernate",  # Hibernate or aestivate
    "shed_skin",  # Shed old skin
    "hunt_insects",  # Hunt small insects
]

ACTIONS_PLANT = [
    "photosynthesize",  # Convert sunlight into energy
    "absorb_resources",  # Absorb water and nutrients
    "grow",  # Grow in size or mass
    "produce_fruit",  # Produce fruits or seeds
    "wither",  # Wither or die naturally
]


def get_mapping(organism_type: str):
    mapping = {
        "universal": ACTIONS_UNIVERSAL,
        "predator": ACTIONS_PREDATOR,
        "herbivore": ACTIONS_HERBIVORE,
        "pollinator": ACTIONS_POLLINATOR,
        "omnivore": ACTIONS_OMNIVORE,
        "mammal": ACTIONS_MAMMAL,
        "bird": ACTIONS_BIRD,
        "reptile": ACTIONS_REPTILE,
        "plant": ACTIONS_PLANT,
    }

    return mapping.get(organism_type)
