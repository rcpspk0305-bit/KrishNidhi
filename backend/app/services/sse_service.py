import asyncio
import json
import logging
from typing import Dict, Set, Optional, AsyncGenerator

logger = logging.getLogger("sse_service")

class SSEBroadcaster:
    def __init__(self):
        # Maps device_id (or "all") to sets of asyncio.Queue instances
        self.listeners: Dict[str, Set[asyncio.Queue]] = {"all": set()}
        self._lock = asyncio.Lock()

    async def subscribe(self, device_id: str = "all") -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        async with self._lock:
            if device_id not in self.listeners:
                self.listeners[device_id] = set()
            self.listeners[device_id].add(queue)
            # Also register to "all" if subscribing to specific device
            if device_id != "all":
                self.listeners["all"].add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue, device_id: str = "all"):
        async with self._lock:
            if device_id in self.listeners and queue in self.listeners[device_id]:
                self.listeners[device_id].remove(queue)
            if "all" in self.listeners and queue in self.listeners["all"]:
                self.listeners["all"].remove(queue)

    async def broadcast(self, event_type: str, data: dict, device_id: Optional[str] = None):
        """
        Broadcasts an SSE event to all connected clients listening to device_id or 'all'.
        """
        message = {
            "event": event_type,
            "device_id": device_id,
            "data": data,
        }
        json_payload = json.dumps(message)
        formatted_sse = f"event: {event_type}\ndata: {json_payload}\n\n"

        target_queues = set()
        async with self._lock:
            if device_id and device_id in self.listeners:
                target_queues.update(self.listeners[device_id])
            if "all" in self.listeners:
                target_queues.update(self.listeners["all"])

        for queue in target_queues:
            try:
                queue.put_nowait(formatted_sse)
            except asyncio.QueueFull:
                # Discard slow listener to prevent lag
                pass

sse_manager = SSEBroadcaster()
