import time
from typing import Dict


class RetrievalTimelineMetrics:
    """Collects and aggregates duration metrics across individual retrieval search stages."""

    def __init__(self):
        self._markers: Dict[str, float] = {}
        self._durations: Dict[str, float] = {}

    def start_stage(self, stage_name: str) -> None:
        """Record start time timestamp marker for a pipeline stage."""
        self._markers[stage_name] = time.time()

    def end_stage(self, stage_name: str) -> None:
        """Compute stage duration and save metrics (milliseconds)."""
        if stage_name in self._markers:
            duration = (time.time() - self._markers[stage_name]) * 1000
            self._durations[stage_name] = round(duration, 2)

    def get_timeline(self) -> Dict[str, float]:
        """Expose duration timeline log metrics dictionary."""
        return self._durations
