import random
from typing import List

from app.api.utils.attack_interactions import hit_chance
from app.database.enums import ActivityCycle
from app.database.models import Ecosystem, Organism, Plant

THIRST_REMOVED_BY_DRINK_WATER = 3


# GLOBAL
def drink_water(ecosystem: Ecosystem, organism: Organism):
    HEALTH = random.randint(5, 20)
    THIRST = random.randint(5, 20)
    if ecosystem.water_available >= organism.water_consumption:
        ecosystem.water_available -= organism.water_consumption
        organism.thirst -= THIRST
        organism.health += HEALTH
        return {
            f"{organism.name} drinks {organism.water_consumption}, recovering {HEALTH} health and reducing his thirst by {THIRST}."
        }
    else:
        organism.thirst += THIRST
        organism.health -= HEALTH
        return {
            f"No sufficient water for {organism.name}. His health has reduced by {HEALTH} and his thirst increased by {THIRST}."
        }


def rest(organism: Organism):
    HEALTH = random.randint(10, 30)
    organism.health += HEALTH
    return {f"{organism.name} rest and recovered {HEALTH} health."}


def reproduce(organisms: List[Organism]):
    pregnant_organism = random.choice(organisms)
    pregnant_organism.pregnant = True
    return {f"{pregnant_organism} is now pregnant."}


# PREDATORS
def hunt_prey(attacker: Organism, organisms: List[Organism]):
    deffender = random.choice(organisms)
    while deffender == attacker:
        deffender = random.choice(organisms)
    is_night = attacker.activity_cycle
    attack_chance = hit_chance(
        attacker,
        deffender,
        True if is_night == ActivityCycle.nocturnal else False,
    )
    successful_attack = random.random() > attack_chance
    attack_message = "Hits" if successful_attack else "Misses "
    return {
        "attacker": attacker.name,
        "deffender": deffender.name,
        "attacker_hit_chance": round(attack_chance * 100, 2),
        "deffender_defend_chance": round((1 - attack_chance) * 100, 2),
        "attacker_cycle": attacker.activity_cycle,
        "deffender_cycle": deffender.activity_cycle,
        "result": f"{attacker.name}: {attack_message} {deffender.name}",
    }


# OMNIVORE
def graze_plants(target: Plant, organism: Organism):
    biomass_lost, hunger = (
        round(random.random(), 2),
        random.randint(5, 20),
    )
    target.weight = biomass_lost * target.weight
    organism.hunger += hunger
    return {f"{organism.name} graze {target.name} and recovers {hunger} hunger."}
