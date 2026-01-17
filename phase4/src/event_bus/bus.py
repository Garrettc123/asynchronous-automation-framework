"""
Phase 4: Enterprise Event Bus
"""
import asyncio
import logging
from typing import Dict, List, Callable, Awaitable
from uuid import uuid4

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue = asyncio.Queue()
        self._active = False

    async def start(self):
        self._active = True
        asyncio.create_task(self._process_queue())
        logger.info("Event Bus started")

    async def publish(self, event_type: str, payload: dict):
        await self._queue.put((event_type, payload))

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def _process_queue(self):
        while self._active:
            event_type, payload = await self._queue.get()
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    try:
                        await handler(payload)
                    except Exception as e:
                        logger.error(f"Error handling event: {e}")
            self._queue.task_done()
