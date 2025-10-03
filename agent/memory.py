from typing import Deque, Dict, Any, List
from collections import deque

class Memory:
    def __init__(self, max_items: int = 1000):
        self.events: Deque[Dict[str, Any]] = deque(maxlen=max_items)

    def add(self, event: Dict[str, Any]):
        self.events.appendleft(event)

    def recent(self, n: int = 10) -> List[Dict[str, Any]]:
        return list(self.events)[:n]

mem = Memory()
