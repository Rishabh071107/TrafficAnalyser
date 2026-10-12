from typing import List, Dict, Any, Tuple, Set


class VehicleCounter:
    """Virtual line vehicle counter tracking bidirectional traffic flow."""

    def __init__(self, line_y_ratio: float = 0.5, line_tolerance: int = 15):
        """Initialize vehicle counter.

        Args:
            line_y_ratio: Relative vertical position of virtual counting line (0.0 to 1.0).
            line_tolerance: Pixel tolerance buffer around counting line.
        """
        self.line_y_ratio = line_y_ratio
        self.line_tolerance = line_tolerance
        self.inbound_count = 0
        self.outbound_count = 0
        self.counted_ids: Set[int] = set()
        self.previous_positions: Dict[int, Tuple[int, int]] = {}

    def process_tracks(self, tracks: List[Dict[str, Any]], frame_height: int) -> Dict[str, int]:
        """Update vehicle counts based on object tracks crossing virtual line.

        Args:
            tracks: List of track dicts containing 'track_id', 'centroid', and 'bbox'.
            frame_height: Height of current video frame in pixels.

        Returns:
            Dict containing 'inbound', 'outbound', and 'total' counts.
        """
        line_y = int(frame_height * self.line_y_ratio)

        for trk in tracks:
            track_id = trk["track_id"]
            cx, cy = trk["centroid"]
            bbox = trk.get("bbox", [0, cy, 0, cy])
            y1, y2 = bbox[1], bbox[3]

            if track_id not in self.counted_ids:
                if track_id in self.previous_positions:
                    prev_cx, prev_cy = self.previous_positions[track_id]

                    crossed_down = (prev_cy < line_y and cy >= line_y) or (y1 <= line_y <= y2 and prev_cy < line_y)
                    crossed_up = (prev_cy > line_y and cy <= line_y) or (y1 <= line_y <= y2 and prev_cy > line_y)

                    if crossed_down:
                        self.inbound_count += 1
                        self.counted_ids.add(track_id)
                    elif crossed_up:
                        self.outbound_count += 1
                        self.counted_ids.add(track_id)
                else:
                    if (y1 <= line_y <= y2) or abs(cy - line_y) <= self.line_tolerance:
                        self.inbound_count += 1
                        self.counted_ids.add(track_id)

            self.previous_positions[track_id] = (cx, cy)

        return {
            "inbound": self.inbound_count,
            "outbound": self.outbound_count,
            "total": self.inbound_count + self.outbound_count,
        }


if __name__ == "__main__":
    counter = VehicleCounter(line_y_ratio=0.5)
    counts = counter.process_tracks([{"track_id": 1, "centroid": (100, 200)}], frame_height=480)
    print(f"Vehicle counter initialized. Test count: {counts}")
