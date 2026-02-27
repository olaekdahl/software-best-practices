from __future__ import annotations

from dataclasses import dataclass
import math

@dataclass
class Region:
    name: str
    lat: float
    lon: float
    healthy: bool = True

def haversine_km(a: Region, lat: float, lon: float) -> float:
    # Rough distance for routing decisions
    r = 6371.0
    dlat = math.radians(lat - a.lat)
    dlon = math.radians(lon - a.lon)
    sa = math.sin(dlat/2)**2 + math.cos(math.radians(a.lat))*math.cos(math.radians(lat))*math.sin(dlon/2)**2
    return 2*r*math.asin(min(1.0, math.sqrt(sa)))

def route(regions: list[Region], client_lat: float, client_lon: float) -> Region:
    healthy = [r for r in regions if r.healthy]
    return min(healthy, key=lambda r: haversine_km(r, client_lat, client_lon))

def main() -> None:
    regions = [
        Region("us-west", 37.7749, -122.4194),
        Region("us-east", 40.7128, -74.0060),
        Region("eu-west", 53.3498, -6.2603),
    ]
    # Client near Los Angeles
    chosen = route(regions, 34.0522, -118.2437)
    print("Client routed to:", chosen.name)

    regions[0].healthy = False
    chosen2 = route(regions, 34.0522, -118.2437)
    print("If nearest is unhealthy, fail over to:", chosen2.name)

if __name__ == "__main__":
    main()
