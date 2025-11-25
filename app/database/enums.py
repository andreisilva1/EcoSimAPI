from enum import Enum


class OrganismType(str, Enum):
    predator = "predator"
    herbivore = "herbivore"
    omnivore = "omnivore"
    pollinator = "pollinator"


class PlantType(str, Enum):
    tree = "tree"
    shrub = "shrub"
    herb = "herb"
    flower = "flower"


class DietType(str, Enum):
    carnivore = "carnivore"
    herbivore = "herbivore"
    omnivore = "omnivore"
    nectarivore = "nectarivore"


class ActivityCycle(str, Enum):
    diurnal = "diurnal"
    nocturnal = "nocturnal"
    crepuscular = "crepuscular"


class SocialBehavior(str, Enum):
    solitary = "solitary"
    pack = "pack"
    herd = "herd"


class Speed(str, Enum):
    slow = "slow"
    normal = "normal"
    fast = "fast"


class SimulationStatus(str, Enum):
    processing = "PROCESSING"
    finished = "FINISHED"


class EnvironmentType(str, Enum):
    desert = "DESERT"
    rainforest = "RAINFOREST"
    savanna = "SAVANNA"
    swamp = "SWAMP"
    mountain = "MOUNTAIN"
    taiga = "TAIGA"
    tundra = "TUNDRA"
