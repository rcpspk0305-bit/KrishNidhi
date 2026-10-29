"""Bounded, single-process admission control for the personal assistant API."""
import os
import time
from collections import deque
from threading import Lock


class AssistantBudget:
    def __init__(self, per_minute=6, daily_limit=200, clock=time.time):
        self.per_minute = per_minute
        self.daily_limit = daily_limit
        self.clock = clock
        self.clients = {}
        self.day = None
        self.daily_count = 0
        self.lock = Lock()

    def admit(self, identity):
        now = self.clock()
        day = int(now // 86400)
        with self.lock:
            if day != self.day:
                self.day, self.daily_count = day, 0
                self.clients.clear()
            for client in list(self.clients):
                if not self.clients[client] or self.clients[client][-1] <= now - 60:
                    del self.clients[client]
            if self.daily_count >= self.daily_limit:
                return max(1, int((day + 1) * 86400 - now))
            # Prevent arbitrary client identities from creating unbounded memory use.
            if identity not in self.clients and len(self.clients) >= 1000:
                return 60
            events = self.clients.setdefault(identity, deque())
            while events and events[0] <= now - 60:
                events.popleft()
            if len(events) >= self.per_minute:
                return max(1, int(events[0] + 60 - now))
            events.append(now)
            self.daily_count += 1
            return None


def positive_limit(name, default):
    try:
        return max(1, int(os.getenv(name, str(default))))
    except ValueError:
        return default


admission = AssistantBudget(
    per_minute=positive_limit("ASSISTANT_REQUESTS_PER_MINUTE", 6),
    daily_limit=positive_limit("ASSISTANT_DAILY_REQUEST_LIMIT", 200),
)
