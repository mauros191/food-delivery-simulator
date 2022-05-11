from enum import Enum


# Speed of simulator
class SimulatorSpeed(Enum):
    MAX = 0
    VARIABLE = 1


# Type of algorithm
class AlgorithmType(Enum):
    SIMPLE_DISPATCH = 1
    GREEDY = 2
    GLOBAL = 3
    GLOBAL_BUNDLE = 4


# Type of distance
class DistanceType(Enum):
    EUCLIDEAN = 1
    MANHATTAN = 2
    HAVERSINE = 3
    ROUTE = 4


# Type of strategy in retry
class RetryStrategy(Enum):
    FORCE = 1
    LAZY = 2


# Type of Movement
class MovementStrategy(Enum):
    A = 1
    B = 2


class MovementType(Enum):
    STILL = 1
    RANDOM = 2
    MAP = 3
