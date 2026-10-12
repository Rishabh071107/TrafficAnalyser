from typing import Dict, Any


class CongestionAnalyzer:
    """Monitors road traffic density and reports congestion state."""

    def __init__(self, free_flow_thresh: int = 5, moderate_thresh: int = 15, heavy_thresh: int = 30):
        """Initialize congestion analyzer.

        Args:
            free_flow_thresh: Max vehicle count for free-flowing traffic.
            moderate_thresh: Max vehicle count for moderate traffic.
            heavy_thresh: Max vehicle count for heavy traffic. Above this is standstill.
        """
        self.free_flow_thresh = free_flow_thresh
        self.moderate_thresh = moderate_thresh
        self.heavy_thresh = heavy_thresh

    def analyze(self, active_vehicle_count: int) -> Dict[str, Any]:
        """Analyze current traffic congestion state.

        Args:
            active_vehicle_count: Number of active vehicles detected in frame.

        Returns:
            Dict containing 'vehicle_count', 'status', and 'level' (1-4).
        """
        if active_vehicle_count <= self.free_flow_thresh:
            status = "Free Flow"
            level = 1
        elif active_vehicle_count <= self.moderate_thresh:
            status = "Moderate Traffic"
            level = 2
        elif active_vehicle_count <= self.heavy_thresh:
            status = "Heavy Traffic"
            level = 3
        else:
            status = "Standstill / Congested"
            level = 4

        return {
            "vehicle_count": active_vehicle_count,
            "status": status,
            "level": level,
        }


if __name__ == "__main__":
    analyzer = CongestionAnalyzer()
    res = analyzer.analyze(8)
    print(f"Congestion analysis test: {res}")
