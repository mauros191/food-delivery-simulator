from config.utils import (
    AlgorithmType,
    DistanceType,
    MovementStrategy,
    MovementType,
    RetryStrategy,
    SimulatorSpeed,
)
from typing import Dict, List

###############
#   DATASET   #
###############
INSTANCE_GRUBHUB: int = 0
DISTANCE: DistanceType = DistanceType.EUCLIDEAN


###############
# 	MOVEMENT  #
###############
P_M: float = 0.5
UPDATE_POSITION_EVERY: int = 20                             # expressed in seconds
MOVEMENT_TYPE: MovementType = MovementType.MAP
MOVEMENT_STRATEGY: MovementStrategy = MovementStrategy.B


###############
#  ALGORITHM  #
###############
ALGORITHM: AlgorithmType = AlgorithmType.GLOBAL_BUNDLE
DELTA_U: int = 20
F: float = 1
PRIORITY: int = 0
RETRY: RetryStrategy = RetryStrategy.LAZY
P_N: float = 0.9


###############
#  SIMULATOR  #
###############
SPEED: SimulatorSpeed = SimulatorSpeed.VARIABLE
QUEUE: bool = True
MAX_TIME: int = 100000
START_TIME: str = "09:00:00"
SEED: int = 115


###############
#    BUNDLE   #
###############
d_max: int = 15


###############
# CONSTRAINTS #
###############
A_max: int = 60
D_max: float = 4


#################
#  PROJECTION   #
#################
PROJECTION: Dict[int, Dict["str", int]] = {
    0: {"MAX_X": 12555, "MAX_Y": 11777},
    1: {"MAX_X": 12975, "MAX_Y": 12376},
    2: {"MAX_X": 12347, "MAX_Y": 12128},
    3: {"MAX_X": 12125, "MAX_Y": 13036},
    4: {"MAX_X": 12241, "MAX_Y": 12102},
    5: {"MAX_X": 31208, "MAX_Y": 35556},
    6: {"MAX_X": 35070, "MAX_Y": 37098},
    7: {"MAX_X": 29942, "MAX_Y": 37061},
    8: {"MAX_X": 34551, "MAX_Y": 54766},
    9: {"MAX_X": 34947, "MAX_Y": 46646},
}

GRID_ZONE_CHICAGO = [16, "N"]
GRID_ZONE_LOS_ANGELS = [11, "N"]


START_POINTS: Dict[int, Dict[str, int]] = {
    0: {"START_X": 375240, "START_Y": 3757416},
    1: {"START_X": 375240, "START_Y": 3757416},
    2: {"START_X": 375240, "START_Y": 3757416},
    3: {"START_X": 375240, "START_Y": 3755916},
    4: {"START_X": 375240, "START_Y": 3755916},
    5: {"START_X": 421115, "START_Y": 4614396},
    6: {"START_X": 417115, "START_Y": 4615896},
    7: {"START_X": 421115, "START_Y": 4619896},
    8: {"START_X": 416115, "START_Y": 4619896},
    9: {"START_X": 415615, "START_Y": 4619896},
}


#################
#     AREA      #
#################
MIN_X = 0
MAX_X = 0
MIN_Y = 0
MAX_Y = 0

DIM_AREA = 1000
CHECK_AREA_EVERY_MIN: int = 60


###############
# 	DISTANCE  #
###############
D_min_r: float = 0.5
D_max_r: float = 1.5


###############
# 	RIDER     #
###############
VELOCITY: float = 15 / 3.6  # expressed as km/h / 3.6 => ms/s


###############
#     LOG     #
###############
SHOW_LOG: bool = True
LOG_REAL_TIME: bool = True
LOG_MOVE: bool = False
LOG_ONLY_ORDERS: List[int] = []
LOG_ONLY_RIDERS: List[int] = []


# BundleAggregated configuration
MAX_ORDERS_FOR_BUNDLE: int = 2


# Enable only some orders or riders (for testing)
ENABLE_ONLY_ORDERS: List[int] = []
ENABLE_ONLY_RIDERS: List[int] = []


# Default configuration
PST: int = 4
DST: int = 4


###############
#  CONSTANTS  #
###############
OMEGA: int = 999999


#################
# UPDATE CONFIG #
#################
DELTA_U = DELTA_U * 60
F = F * 60
PST = PST * 60
DST = DST * 60
d_max = d_max * 60
D_max = D_max * 1000
CHECK_AREA_EVERY_MIN = CHECK_AREA_EVERY_MIN * 60
