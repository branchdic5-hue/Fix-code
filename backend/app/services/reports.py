from collections import defaultdict
from datetime import datetime, time
from typing import Dict, List


def call_statistics(records: List[Dict]) -> List[Dict]:
    stats = defaultdict(lambda: {"count": 0, "duration": 0})
    for record in records:
        key = (record.get("a_party"), record.get("b_party"))
        stats[key]["count"] += 1
        stats[key]["duration"] += int(record.get("duration_sec") or 0)

    output = []
    for (a_party, b_party), value in stats.items():
        output.append(
            {
                "a_party": a_party,
                "b_party": b_party,
                "call_count": value["count"],
                "total_duration": value["duration"],
            }
        )
    return sorted(output, key=lambda item: item["call_count"], reverse=True)


def _parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def day_night_analysis(
    records: List[Dict], day_start: str = "06:00", night_start: str = "18:00"
) -> Dict[str, List[Dict]]:
    day_start_time = _parse_time(day_start)
    night_start_time = _parse_time(night_start)

    day_stats = defaultdict(lambda: {"count": 0, "duration": 0})
    night_stats = defaultdict(lambda: {"count": 0, "duration": 0})

    for record in records:
        start_time = record.get("start_time")
        if not start_time:
            continue
        try:
            parsed = datetime.fromisoformat(start_time)
        except ValueError:
            continue

        target = day_stats
        if parsed.time() >= night_start_time or parsed.time() < day_start_time:
            target = night_stats

        key = (record.get("a_party"), record.get("b_party"))
        target[key]["count"] += 1
        target[key]["duration"] += int(record.get("duration_sec") or 0)

    def _format(stats_map):
        return [
            {
                "a_party": a_party,
                "b_party": b_party,
                "call_count": value["count"],
                "total_duration": value["duration"],
            }
            for (a_party, b_party), value in stats_map.items()
        ]

    return {
        "day": sorted(_format(day_stats), key=lambda item: item["call_count"], reverse=True),
        "night": sorted(_format(night_stats), key=lambda item: item["call_count"], reverse=True),
    }
