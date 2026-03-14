"""
Phase 4: Enterprise Event Bus with pub/sub and replay support
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class Event:
    event_type: str
    payload: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None


class EventBus:
    """Asynchronous pub/sub event bus with replay and filtering support."""

    def __init__(self, max_queue_size: int = 1000, history_size: int = 100):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._active = False
        self._event_history: List[Event] = []
        self._history_size = history_size
        self._processed_count = 0
        self._error_count = 0

    async def start(self):
        """Start the event bus processing loop."""
        self._active = True
        asyncio.create_task(self._process_queue())
        logger.info("Event Bus started")

    async def stop(self):
        """Gracefully stop the event bus."""
        self._active = False
        await self._queue.join()
        logger.info("Event Bus stopped")

    async def publish(self, event_type: str, payload: dict, source: Optional[str] = None):
        """Publish an event to the bus."""
        event = Event(event_type=event_type, payload=payload, source=source)
        self._event_history.append(event)
        if len(self._event_history) > self._history_size:
            self._event_history.pop(0)
        await self._queue.put(event)
        logger.debug(f"Published event {event.event_id}: {event_type}")

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler to an event type. Use '*' to catch all events."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """Remove a subscription."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]

    async def _process_queue(self):
        """Process events from the queue and dispatch to subscribers."""
        while self._active or not self._queue.empty():
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            handlers = list(self._subscribers.get(event.event_type, []))
            handlers += self._subscribers.get("*", [])

            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    self._error_count += 1
                    logger.error(f"Error handling event {event.event_type}: {e}")

            self._processed_count += 1
            self._queue.task_done()

    def get_stats(self) -> Dict[str, Any]:
        """Return bus statistics."""
        return {
            "processed": self._processed_count,
            "errors": self._error_count,
            "queue_size": self._queue.qsize(),
            "subscribers": {k: len(v) for k, v in self._subscribers.items()},
            "history_size": len(self._event_history),
        }

    def get_history(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return event history, optionally filtered by type."""
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [
            {"event_id": e.event_id, "event_type": e.event_type, "timestamp": e.timestamp, "source": e.source}
            for e in events
        ]
