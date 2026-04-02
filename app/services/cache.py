from cachetools import TTLCache

_dashboard_cache: TTLCache = TTLCache(maxsize=1, ttl=300)


def get_cached_dashboard() -> list[dict] | None:
    return _dashboard_cache.get("dashboard")


def set_cached_dashboard(data: list[dict]) -> None:
    _dashboard_cache["dashboard"] = data


def invalidate_dashboard_cache() -> None:
    _dashboard_cache.clear()
