# backend/core/limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address

# NOTE: in-memory storage — limits are per-process, reset on every server
# restart, and do NOT share state across multiple workers or instances.
# This is an accepted tradeoff for a single-instance Render free-tier deployment.
# If this app ever scales to multiple workers/instances, replace with Redis:
#   from slowapi.wrappers import Redis
#   Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
limiter = Limiter(key_func=get_remote_address)
