import copy
from datetime import datetime

_state: dict = {
    "is_running": False,
    "mode": None,
    "total": 0,
    "done": 0,
    "current": [],
    "log": [],
    "started_at": None,
    "finished_at": None,
    "new_total": 0,
}


def reset(mode: str, total: int) -> None:
    global _state
    _state = {
        "is_running": True,
        "mode": mode,
        "total": total,
        "done": 0,
        "current": [],
        "log": [],
        "started_at": datetime.utcnow().isoformat(),
        "finished_at": None,
        "new_total": 0,
    }


def item_started(item_id: int, query: str, item_type: str) -> None:
    _state["current"].append({"id": item_id, "query": query, "type": item_type})


def item_finished(item_id: int, query: str, new_listings: int, item_type: str = "") -> None:
    _state["current"] = [c for c in _state["current"] if c["id"] != item_id]
    _state["log"].append({"query": query, "new_listings": new_listings, "type": item_type})
    _state["done"] += 1
    _state["new_total"] += new_listings


def finish() -> None:
    _state["is_running"] = False
    _state["finished_at"] = datetime.utcnow().isoformat()


def get() -> dict:
    return copy.deepcopy(_state)
