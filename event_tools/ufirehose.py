"""
Author: Martin

Date: 2025-09-24

License: Unlicense

Description:
    A simple micro FireHose class. Accululates data, then invokes an action when a threshold is reached.
"""

import time
from typing import Any, Callable, List


class uFireHose:
    def __init__(
        self,
        action: Callable[[List[Any]], None],
        length_threshold: int,
        time_threshold_seconds: float,
    ):
        """
        Simple synchronous Firehose-like accumulator.

        :param action: Function to invoke with accumulated data when thresholds are met.
        :param length_threshold: Max number of items before auto-flush.
        :param time_threshold: Max seconds between flushes before auto-flush.
        """
        self.action = action
        self.length_threshold = length_threshold
        self.time_threshold = time_threshold_seconds

        self._data: List[Any] = []
        self._last_action_time = time.time()

    def put(self, item: Any):
        """Add an item and flush if length or time threshold exceeded."""
        self._data.append(item)
        now = time.time()

        if (
            len(self._data) >= self.length_threshold
            or (now - self._last_action_time) >= self.time_threshold
        ):
            self._flush()

    def _flush(self):
        """Call the action on the accumulated data and reset."""
        if not self._data:
            return
        try:
            self.action(self._data[:])  # pass a copy
        except Exception as e:
            print(f"[uFireHose] Action error: {e}")
        self._data.clear()
        self._last_action_time = time.time()

    def reset(self):
        """Clear all accumulated data and reset the timer."""
        self._data.clear()
        self._last_action_time = time.time()
