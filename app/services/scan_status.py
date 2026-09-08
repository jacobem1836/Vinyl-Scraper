"""Per-user in-memory scan progress, polled by the dashboard.

ponytail: process-local dict; fine on the single machine the scheduler already requires.
"""
import copy
from datetime import datetime

_EMPTY = {
    "is_running": False, "total": 0, "done": 0, "current": [], "log": [],
    "started_at": None, "finished_at": None, "new_total": 0, "errors": 0,
}
_state: dict[int, dict] = {}


def get(user_id: int) -> dict:
    return copy.deepcopy(_state.get(user_id, _EMPTY))


def is_running(user_id: int) -> bool:
    return bool(_state.get(user_id, {}).get("is_running"))


def start(user_id: int, total: int) -> None:
    _state[user_id] = {**copy.deepcopy(_EMPTY), "is_running": True, "total": total, "started_at": datetime.utcnow().isoformat()}


def item_started(user_id: int, item_id: int, query: str, item_type: str) -> None:
    _state[user_id]["current"].append({"id": item_id, "query": query, "type": item_type})


def item_finished(user_id: int, item_id: int, query: str, new_listings: int, item_type: str, failed_sources: int = 0) -> None:
    s = _state[user_id]
    s["current"] = [c for c in s["current"] if c["id"] != item_id]
    s["log"].append({"query": query, "new_listings": new_listings, "type": item_type, "failed_sources": failed_sources})
    s["done"] += 1
    s["new_total"] += new_listings
    s["errors"] += failed_sources


def finish(user_id: int) -> None:
    s = _state.get(user_id)
    if s:
        s["is_running"] = False
        s["finished_at"] = datetime.utcnow().isoformat()
