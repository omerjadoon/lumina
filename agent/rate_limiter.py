"""
Sliding-window TPM rate limiter for the Libra API (100k tokens/minute cap).
"""

import time
from collections import deque

TPM_LIMIT = 100_000
WINDOW_SECONDS = 60
SAFETY_MARGIN = 0.90  # stay under 90% to leave headroom

_window: deque = deque()  # each entry: (timestamp, tokens)


def record(tokens: int) -> None:
    """Record tokens used by a completed API call."""
    _window.append((time.monotonic(), tokens))


def wait_if_needed() -> None:
    """Block until sending the next request won't exceed the TPM cap."""
    while True:
        now = time.monotonic()
        cutoff = now - WINDOW_SECONDS
        # Drop entries outside the sliding window
        while _window and _window[0][0] < cutoff:
            _window.popleft()

        used = sum(t for _, t in _window)
        if used < TPM_LIMIT * SAFETY_MARGIN:
            return

        # Sleep until the oldest entry ages out
        oldest_ts = _window[0][0]
        sleep_for = (oldest_ts + WINDOW_SECONDS) - now + 0.1
        time.sleep(max(sleep_for, 0.1))
