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
    return {f"{pregnant_organism.name} is now pregnant."}


# PREDATORS
def hunt_prey(attacker: Organism, deffender: Organism):
    results = []
    is_night = attacker.activity_cycle
    reattack = True
    while deffender.health > 0 or reattack:
        attack_chance = hit_chance(
            attacker,
            deffender,
            True if is_night == ActivityCycle.nocturnal else False,
        )
        successful_attack = random.random() > attack_chance
        damage = random.randint(5, 40)
        if successful_attack:
            deffender.health -= random.randint(5, 40)
        attack_message = (
            f"Hits and cause {damage} damage to"
            if successful_attack
            else "Misses and cause 0 damage to"
        )

        ATTACKER_HIT_CHANCE = round(attack_chance * 100, 2)
        DEFFENDER_DEFEND_CHANCE = round((1 - attack_chance) * 100, 2)
        results.append(
            {
                "attacker": attacker.name,
                "deffender": deffender.name,
                "attacker_hit_chance": ATTACKER_HIT_CHANCE,
                "deffender_defend_chance": DEFFENDER_DEFEND_CHANCE,
                "result": f"{attacker.name}: {attack_message} {deffender.name}",
            }
        )
        reattack = random.random() > DEFFENDER_DEFEND_CHANCE
    if deffender.health <= 0:
        HUNGER_TO_RECOVER = random.randint(10, 30)
        HEALTH_TO_RECOVER = random.randint(5, 25)
        attacker.hunger += HUNGER_TO_RECOVER
        attacker.health += HEALTH_TO_RECOVER
        results.append(
            {
                f"{attacker.name} kills {deffender.name} and recovers {HUNGER_TO_RECOVER} hunger and {HEALTH_TO_RECOVER} health!"
            }
        )
    return results


# OMNIVORE
def graze_plants(target: Plant, organism: Organism):
    if not target:
        return {f"No {target} has been found to in this ecosystem to {organism.name}."}

    biomass_lost, hunger = (
        round(random.random(), 2),
        random.randint(5, 20),
    )
    target.weight = biomass_lost * target.weight
    organism.hunger += hunger
    if target.weight <= 0:
        return {
            f"{organism.name} graze {target.name} and recovers {hunger} hunger. {target.name} health reaches 0."
        }
    return {f"{organism.name} graze {target.name} and recovers {hunger} hunger."}
