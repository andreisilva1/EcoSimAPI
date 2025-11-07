from app.database.enums import ActivityCycle, OrganismType, SocialBehavior, Speed
from app.database.models import Organism


def hit_chance(attacker: Organism, defender: Organism, is_night: bool) -> float:
    atk = combat_power(attacker, defender, is_night)
    dfd = combat_power(defender, attacker, is_night)

    total = atk + dfd

    chance = atk / total

    return max(0.05, min(chance, 0.95))


def combat_power(org: Organism, opponent: Organism, is_night: bool) -> float:
    score = 0.0
    geral_weight = 1
    # Physical Strength (weight & size)
    physical = (org.weight * org.size) ** 0.33
    score += physical * 1.2

    # Speed
    speed_values = {Speed.slow: 0.7, Speed.normal: 1.0, Speed.fast: 1.4}
    score += speed_values.get(org.speed, 1.0) * geral_weight

    # Experience ("peak age" = 35% of max_age)
    ideal = org.max_age * 0.35
    exp_raw = 1 - abs(org.age - ideal) / (ideal + 0.01)
    experience = max(0.3, min(exp_raw, 1))
    score += experience * geral_weight

    # Biological Type (predator, herbivore, etc.)
    score += type_advantage(org, opponent)

    # Activity cycle (day/night)
    score += cycle_bonus(org, is_night)

    # Social behavior
    score += social_bonus(org)

    return max(score, 0.1)


def type_advantage(attacker: Organism, defender: Organism) -> float:
    # predator vs herbivores
    if (
        attacker.type == OrganismType.predator
        and defender.type == OrganismType.herbivore
    ):
        return 2.0

    # predator vs omnivore
    if (
        attacker.type == OrganismType.predator
        and defender.type == OrganismType.omnivore
    ):
        return 1.0

    # omnivore vs herbivore
    if (
        attacker.type == OrganismType.omnivore
        and defender.type == OrganismType.herbivore
    ):
        return 0.7

    if (
        attacker.type == OrganismType.herbivore
        and defender.type == OrganismType.predator
    ):
        return -1.5

    if (
        attacker.type == OrganismType.herbivore
        and defender.type == OrganismType.omnivore
    ):
        return -0.7

    if attacker.type == OrganismType.pollinator:
        return -2.0

    return 0.0


def cycle_bonus(org: Organism, is_night: bool) -> float:
    if org.activity_cycle == ActivityCycle.nocturnal:
        return 1.0 if is_night else -0.5
    if org.activity_cycle == ActivityCycle.diurnal:
        return 1.0 if not is_night else -0.5
    if org.activity_cycle == ActivityCycle.crepuscular:
        return 0.4
    return 0.0


def social_bonus(org: Organism) -> float:
    mapping = {
        SocialBehavior.solitary: 0.0,
        SocialBehavior.pack: 0.8,
        SocialBehavior.herd: 0.4,
    }
    return mapping.get(org.social_behavior, 0.0)
