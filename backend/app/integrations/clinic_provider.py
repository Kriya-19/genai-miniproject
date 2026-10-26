import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx

from ..config import Settings


@dataclass
class ClinicProviderUnavailable(RuntimeError):
    message: str


class OverpassClinicProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cache: dict[tuple[float, float, float], tuple[float, list[dict[str, Any]]]] = {}
        self._last_request_at = 0.0
        self._lock = asyncio.Lock()

    async def search(self, latitude: float, longitude: float, radius_km: float) -> list[dict[str, Any]]:
        key = (round(latitude, 4), round(longitude, 4), round(radius_km, 1))
        now = time.monotonic()
        cached = self._cache.get(key)
        if cached and now - cached[0] < self.settings.overpass_cache_ttl_seconds:
            return cached[1]

        async with self._lock:
            now = time.monotonic()
            cached = self._cache.get(key)
            if cached and now - cached[0] < self.settings.overpass_cache_ttl_seconds:
                return cached[1]
            wait_seconds = self.settings.overpass_min_interval_seconds - (now - self._last_request_at)
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            query = self._query(latitude, longitude, radius_km)
            endpoints = [self.settings.overpass_url, *(
                endpoint.strip() for endpoint in self.settings.overpass_fallback_urls.split(",") if endpoint.strip()
            )]
            elements = None
            last_error: Exception | None = None
            async with httpx.AsyncClient(
                timeout=10,
                headers={"User-Agent": "DiagnoSure/1.0 (open-source prototype; contact via project repository)"},
            ) as client:
                for endpoint in endpoints:
                    try:
                        response = await client.post(endpoint, data={"data": query})
                        response.raise_for_status()
                        payload = response.json()
                        elements = payload.get("elements", [])
                        break
                    except (httpx.HTTPError, ValueError) as exc:
                        last_error = exc
                if elements is None:
                    elements = await self._nominatim_fallback(client, latitude, longitude, radius_km)
            if elements is None:
                raise ClinicProviderUnavailable("OpenStreetMap search providers are temporarily unavailable.") from last_error
            self._last_request_at = time.monotonic()
            results = [self._normalize(element) for element in elements]
            self._cache[key] = (self._last_request_at, results)
            return results

    async def _nominatim_fallback(
        self, client: httpx.AsyncClient, latitude: float, longitude: float, radius_km: float
    ) -> list[dict[str, Any]] | None:
        span = radius_km / 111
        params = {
            "format": "jsonv2",
            "limit": 50,
            "bounded": 1,
            "viewbox": f"{longitude - span},{latitude + span},{longitude + span},{latitude - span}",
        }
        try:
            results = []
            seen = set()
            for query in ("clinic", "hospital", "doctor"):
                response = await client.get(self.settings.nominatim_url, params={**params, "q": query})
                response.raise_for_status()
                for item in response.json():
                    osm_id = item.get("osm_id")
                    if not osm_id or osm_id in seen or not item.get("lat") or not item.get("lon"):
                        continue
                    seen.add(osm_id)
                    results.append({
                        "type": "nominatim",
                        "id": osm_id,
                        "lat": item["lat"],
                        "lon": item["lon"],
                        "tags": {
                            "name": item.get("display_name", "").split(",")[0],
                            "amenity": "clinic",
                            "display_name": item.get("display_name", ""),
                        },
                    })
            return results
        except (httpx.HTTPError, ValueError):
            return None

    @staticmethod
    def _query(latitude: float, longitude: float, radius_km: float) -> str:
        radius_m = int(radius_km * 1000)
        return (
            "[out:json][timeout:12];"
            f"(nwr[\"amenity\"~\"hospital|clinic|doctors\"](around:{radius_m},{latitude},{longitude});"
            f"nwr[\"healthcare\"](around:{radius_m},{latitude},{longitude}););out center tags;"
        )

    @staticmethod
    def _normalize(element: dict[str, Any]) -> dict[str, Any]:
        tags = element.get("tags", {})
        center = element.get("center", element)
        return {
            "id": f"osm:{element.get('type', 'unknown')}:{element.get('id', '')}",
            "name": tags.get("name") or "Unnamed healthcare facility",
            "latitude": center.get("lat"),
            "longitude": center.get("lon"),
            "amenity": tags.get("amenity"),
            "healthcare": tags.get("healthcare"),
            "address": tags.get("display_name") or ", ".join(value for key, value in (
                ("street", tags.get("addr:street")),
                ("city", tags.get("addr:city")),
            ) if value),
            "source": "OpenStreetMap Nominatim" if element.get("type") == "nominatim" else "OpenStreetMap Overpass",
        }
