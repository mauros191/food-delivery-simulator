import requests
import math
from geo.models import RealPosition


def create_url(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    R = f"http://127.0.0.1:6000/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?alternatives=false&steps=true"
    return R


def real_travel_time(p1: RealPosition, p2: RealPosition) -> int:
    url: str = create_url(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
    response = requests.get(url).json()

    if response["code"] == "Ok":
        # distance_mt: float = response['routes'][0]['distance']
        duration_seconds: int = math.ceil(response["routes"][0]["duration"])
        return max(1, duration_seconds)

    else:
        raise Exception(f"OSRM code response -> {response['code']}")
