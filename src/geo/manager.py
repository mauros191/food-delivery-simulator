import config.config as config
import math
import random
from config.utils import DistanceType
from geo.models import Position, PositionTime, RealPosition, Route, SimplePosition
from system.system import System
import turfpy.measurement as turfpyMeas
import utm
import geo.osrm as osrm


# Manhattan movements for second
MANHATTAN_MOVE_FOR_SEC: int = int(config.VELOCITY)


# Generate real position from Grubhub point
def generate_real_position(x: int, y: int) -> RealPosition:
    if config.INSTANCE_GRUBHUB <= 4:
        ZONE_NUM = config.GRID_ZONE_LOS_ANGELS[0]
        ZONE_POS = config.GRID_ZONE_LOS_ANGELS[1]

    else:
        ZONE_NUM = config.GRID_ZONE_CHICAGO[0]
        ZONE_POS = config.GRID_ZONE_CHICAGO[1]

    START_X = config.START_POINTS[config.INSTANCE_GRUBHUB]["START_X"]
    START_Y = config.START_POINTS[config.INSTANCE_GRUBHUB]["START_Y"]

    x_utm = START_X + x
    y_utm = START_Y + y

    U = (x_utm, y_utm, ZONE_NUM, ZONE_POS)
    point = utm.to_latlon(*U)
    latitude: float = point[0]
    longitude: float = point[1]

    return RealPosition(latitude, longitude, x, y, x_utm, y_utm)


# Generate Euclidean route (only for SimplePosition positions)
def generate_euclidean_route(
    start: SimplePosition, end: SimplePosition, t_start: int, t_end: int
) -> Route:
    dtime: int = config.UPDATE_POSITION_EVERY
    travel_time: int = t_end - t_start
    diff_x: int = end.x - start.x
    diff_y: int = end.y - start.y

    # Find distance
    distance: float = math.sqrt(diff_x**2 + diff_y**2)

    # Find angle alfa
    alfa: float = math.atan2(diff_y, diff_x)

    # Find increase
    dx: float = math.cos(alfa) * (distance / travel_time * dtime)
    dy: float = math.sin(alfa) * (distance / travel_time * dtime)

    # Coordinates for dynamic position
    X: int = start.x
    Y: int = start.y

    # Create route
    route: Route = Route()

    while dtime < travel_time:
        X = int(X + dx)
        Y = int(Y + dy)

        # Insert PositionTime on Route
        route.insert(PositionTime(SimplePosition(X, Y), System.TIME + dtime))

        # Update dtime
        dtime += config.UPDATE_POSITION_EVERY

    # Add last stop
    route.insert(PositionTime(SimplePosition(end.x, end.y), t_end))

    return route


# Generate Manhattan route (only for SimplePosition positions)
def generate_manhattan_route(
    start: SimplePosition, end: SimplePosition, t_start: int, t_end: int
) -> Route:
    dtime: int = config.UPDATE_POSITION_EVERY
    travel: int = t_end - t_start
    dx: int = end.x - start.x
    dy: int = end.y - start.y
    mx_available: int = abs(end.x - start.x)
    my_available: int = abs(end.y - start.y)

    # Coordinates for dynamic position
    X: int = start.x
    Y: int = start.y

    # Create route
    route: Route = Route()

    while dtime < travel:
        num_movements: int = (
            MANHATTAN_MOVE_FOR_SEC + random.getrandbits(1)
        ) * config.UPDATE_POSITION_EVERY

        if mx_available > 0:
            move_x = min(num_movements, mx_available)
            num_movements -= move_x
            mx_available -= move_x

            if dx > 0:
                X += abs(move_x)
            else:
                X -= abs(move_x)

        if num_movements > 0:
            move_y = min(num_movements, my_available)
            num_movements -= move_y
            my_available -= move_y

            if dy > 0:
                Y += abs(move_y)
            else:
                Y -= abs(move_y)

        # Insert PositionTime on Route
        route.insert(PositionTime(SimplePosition(X, Y), System.TIME + dtime))

        # Update dtime
        dtime += config.UPDATE_POSITION_EVERY

    # Add last stop
    route.insert(PositionTime(SimplePosition(end.x, end.y), t_end))

    return route


# Generate Haversine route (only for RealPosition positions)
def generate_haversine_route(
    start: RealPosition, end: RealPosition, t_start: int, t_end: int
) -> Route:
    dtime: int = config.UPDATE_POSITION_EVERY
    travel_time: int = t_end - t_start

    diff_lat: float = abs(end.latitude - start.latitude)
    diff_lon: float = abs(end.longitude - start.longitude)

    # Find increase
    d_lat: float = diff_lat * (dtime / travel_time)
    d_lon: float = diff_lon * (dtime / travel_time)

    # Coordinates for dynamic position
    LAT: float = start.latitude
    LON: float = start.longitude

    # Create route
    route: Route = Route()

    while dtime < travel_time:
        if start.latitude < end.latitude:
            LAT = LAT + d_lat
        else:
            LAT = LAT - d_lat

        if start.longitude < end.longitude:
            LON = LON + d_lon
        else:
            LON = LON - d_lon

        # Insert PositionTime on Route
        route.insert(PositionTime(RealPosition(LAT, LON), System.TIME + dtime))

        # Update dtime
        dtime += config.UPDATE_POSITION_EVERY

    # Add last stop
    route.insert(PositionTime(RealPosition(end.latitude, end.longitude), t_end))

    return route


def distance(p1: Position, p2: Position) -> float:
    # SIMPLE POSITION
    if type(p1) is SimplePosition and type(p2) is SimplePosition:

        # EUCLIDEAN
        if config.DISTANCE == DistanceType.EUCLIDEAN:
            dx: int = abs(p2.x - p1.x)
            dy: int = abs(p2.y - p1.y)
            return math.sqrt(dx**2 + dy**2)

        # MANHATTAN
        elif config.DISTANCE == DistanceType.MANHATTAN:
            dx: int = abs(p2.x - p1.x)
            dy: int = abs(p2.y - p1.y)
            return dx + dy

        else:
            raise ValueError("DistanceType SimplePosition error")

    # REAL POSITION
    elif type(p1) is RealPosition and type(p2) is RealPosition:

        # HAVERSINE
        if config.DISTANCE == DistanceType.HAVERSINE:
            return turfpyMeas.distance(p1.point, p2.point, units="m")

        # HAVERSINE REAL
        elif config.DISTANCE == DistanceType.ROUTE:
            raise Exception("DISTANCE HAVERSINE REAL NOT IMPLEMENTED")

        else:
            raise ValueError("DistanceType RealPosition error")

    else:
        raise TypeError("The two types of position are different or unknown")


# Straight-line distance
def straight_line_distance(p1: Position, p2: Position) -> float:
    if type(p1) is SimplePosition and type(p2) is SimplePosition:
        dx: int = abs(p2.x - p1.x)
        dy: int = abs(p2.y - p1.y)
        return math.sqrt(dx**2 + dy**2)

    elif type(p1) is RealPosition and type(p2) is RealPosition:
        return turfpyMeas.distance(p1.point, p2.point, units="m")

    else:
        raise Exception("OU")


# Find travel time
def travel_time(p1: Position, p2: Position, real: bool = False) -> int:

    if type(p1) is SimplePosition and type(p2) is SimplePosition:

        # EUCLIDEAN
        if config.DISTANCE == DistanceType.EUCLIDEAN:
            euclidean_distance: float = distance(p1, p2)
            time_in_sec: int = math.ceil(euclidean_distance / config.VELOCITY)
            return time_in_sec

        # MANHATTAN
        elif config.DISTANCE == DistanceType.MANHATTAN:
            manhattan_distance: int = int(distance(p1, p2))
            time_in_sec: int = math.ceil(manhattan_distance / config.VELOCITY)
            return time_in_sec

        else:
            raise ValueError("DistanceType SimplePosition error")

    elif type(p1) is RealPosition and type(p2) is RealPosition:

        # HAVERSINE
        if config.DISTANCE == DistanceType.HAVERSINE:
            if not real:
                haversine_distance: float = turfpyMeas.distance(
                    p1.point, p2.point, units="m"
                )
                time_in_sec: int = math.ceil(haversine_distance / config.VELOCITY)
            else:
                time_in_sec: int = osrm.real_travel_time(p1, p2)

            return time_in_sec

        # ROUTE
        elif config.DISTANCE == DistanceType.ROUTE:
            return osrm.real_travel_time(p1, p2)

        else:
            raise ValueError("DistanceType RealPosition error")

    else:
        raise TypeError("The two types of position are different or unknown")


# Generate route
def generate_route(start: Position, end: Position, t_start: int, t_end: int) -> Route:

    if type(start) is SimplePosition and type(end) is SimplePosition:
        if config.DISTANCE is DistanceType.EUCLIDEAN:
            return generate_euclidean_route(start, end, t_start, t_end)
        elif config.DISTANCE is DistanceType.MANHATTAN:
            return generate_manhattan_route(start, end, t_start, t_end)
        else:
            raise ValueError("Generation of route for SimplePosition Exception")

    elif type(start) is RealPosition and type(end) is RealPosition:
        if config.DISTANCE in [DistanceType.HAVERSINE, DistanceType.ROUTE]:
            return generate_haversine_route(start, end, t_start, t_end)

        else:
            raise Exception("Generation of route for DistanceReal not yet implemented")

    else:
        raise TypeError("Generate route type error")
