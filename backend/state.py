"""Expiring process-local or Redis-backed state for sessions and OTP limits."""
from __future__ import annotations

import hashlib
import json
import math
import os
import secrets
import threading
import time
from collections.abc import MutableMapping


_client_lock = threading.Lock()
_shared_client = None
_shared_url = None

_RATE_LIMIT_SCRIPT = """
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local cooldown = tonumber(ARGV[4])
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - window)
local count = redis.call('ZCARD', KEYS[1])
local latest = redis.call('ZREVRANGE', KEYS[1], 0, 0, 'WITHSCORES')
if cooldown > 0 and #latest > 0 then
  local retry = cooldown - (now - tonumber(latest[2]))
  if retry > 0 then return math.floor(retry) + 1 end
end
if count >= limit then
  local oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
  return math.max(1, math.floor(window - (now - tonumber(oldest[2]))) + 1)
end
redis.call('ZADD', KEYS[1], now, ARGV[5])
redis.call('EXPIRE', KEYS[1], math.ceil(window))
return 0
"""


def _redis_client():
    global _shared_client, _shared_url
    url = os.environ.get("REDIS_URL", "").strip()
    if not url:
        return None
    with _client_lock:
        if _shared_client is None or _shared_url != url:
            try:
                import redis
            except ImportError as error:
                raise RuntimeError("REDIS_URL is configured but the redis package is missing; install requirements.txt.") from error
            _shared_client = redis.Redis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
                health_check_interval=30,
            )
            _shared_url = url
        return _shared_client


def validate_redis_connection():
    client = _redis_client()
    if client is not None:
        client.ping()


class StateStore(MutableMapping):
    """Dictionary-shaped store with per-value TTLs and an atomic Redis limiter."""

    def __init__(self, namespace: str, default_ttl: int = 24 * 60 * 60):
        self.namespace = namespace
        self.default_ttl = max(1, int(default_ttl))
        self._local: dict[str, object] = {}

    @property
    def remote_enabled(self) -> bool:
        return bool(os.environ.get("REDIS_URL", "").strip())

    def _key(self, key) -> str:
        digest = hashlib.sha256(str(key).encode("utf-8")).hexdigest()
        return f"bhadawar:{self.namespace}:{digest}"

    def _ttl(self, value) -> int:
        if isinstance(value, dict):
            expiry = value.get("expires")
            if isinstance(expiry, (int, float)):
                return max(1, math.ceil(expiry - time.time()))
        return self.default_ttl

    def __getitem__(self, key):
        client = _redis_client()
        if client is None:
            return self._local[str(key)]
        raw = client.get(self._key(key))
        if raw is None:
            raise KeyError(key)
        try:
            return json.loads(raw)
        except (TypeError, ValueError) as error:
            client.delete(self._key(key))
            raise KeyError(key) from error

    def __setitem__(self, key, value):
        client = _redis_client()
        if client is None:
            self._local[str(key)] = value
            return
        client.set(self._key(key), json.dumps(value, separators=(",", ":")), ex=self._ttl(value))

    def __delitem__(self, key):
        client = _redis_client()
        if client is None:
            del self._local[str(key)]
            return
        if not client.delete(self._key(key)):
            raise KeyError(key)

    def __iter__(self):
        client = _redis_client()
        if client is None:
            return iter(self._local)
        prefix = f"bhadawar:{self.namespace}:"
        return iter(key.removeprefix(prefix) for key in client.scan_iter(match=prefix + "*"))

    def __len__(self):
        client = _redis_client()
        if client is None:
            return len(self._local)
        prefix = f"bhadawar:{self.namespace}:*"
        return sum(1 for _ in client.scan_iter(match=prefix))

    def rate_limit(self, key, limit: int, window_seconds: int, cooldown_seconds: int = 0) -> int:
        """Apply a cross-process sliding-window limit atomically when Redis is active."""
        client = _redis_client()
        if client is None:
            raise RuntimeError("Atomic Redis rate limiting requires REDIS_URL.")
        now = time.time()
        return int(client.eval(
            _RATE_LIMIT_SCRIPT,
            1,
            f"bhadawar:{self.namespace}:rate:{hashlib.sha256(str(key).encode('utf-8')).hexdigest()}",
            now,
            int(window_seconds),
            int(limit),
            int(cooldown_seconds),
            f"{now:.6f}:{secrets.token_hex(8)}",
        ))
