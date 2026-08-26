import queue
import threading
from typing import Dict, Any, Callable

class Actor:
    def __init__(self, name: str, handler: Callable[[Any], Any]):
        self.name = name
        self.handler = handler
        self.mailbox = queue.Queue()
        self._running = True

    def send(self, msg: Any) -> None:
        self.mailbox.put(msg)

    def process_one(self) -> Any:
        msg = self.mailbox.get_nowait()
        return self.handler(msg)

class ActorSystem:
    def __init__(self):
        self.actors: Dict[str, Actor] = {}

    def spawn(self, name: str, handler: Callable[[Any], Any]) -> Actor:
        actor = Actor(name, handler)
        self.actors[name] = actor
        return actor

    def send(self, target: str, msg: Any) -> None:
        if target not in self.actors:
            raise KeyError(f"Actor {target} not found")
        self.actors[target].send(msg)
