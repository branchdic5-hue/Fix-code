from collections import defaultdict
from typing import Dict, List


def build_kml(records: List[Dict]) -> str:
    towers = defaultdict(lambda: {"msisdns": set(), "lat": None, "lng": None})
    for record in records:
        cell_id = record.get("cell_id") or "UNKNOWN"
        towers[cell_id]["msisdns"].add(record.get("a_party") or "")
        towers[cell_id]["msisdns"].add(record.get("b_party") or "")
        if record.get("lat") and record.get("lng"):
            towers[cell_id]["lat"] = record.get("lat")
            towers[cell_id]["lng"] = record.get("lng")

    placemarks = []
    for cell_id, data in towers.items():
        lat = data["lat"] or 0
        lng = data["lng"] or 0
        msisdns = sorted(msisdn for msisdn in data["msisdns"] if msisdn)
        description = (
            f"<![CDATA[<strong>Cell ID:</strong> {cell_id}<br/>"
            f"<strong>Total Numbers:</strong> {len(msisdns)}<br/>"
            f"<strong>MSISDNs:</strong> {', '.join(msisdns)}]]>"
        )
        placemarks.append(
            "\n".join(
                [
                    "<Placemark>",
                    f"<name>{cell_id}</name>",
                    f"<description>{description}</description>",
                    "<Point>",
                    f"<coordinates>{lng},{lat},0</coordinates>",
                    "</Point>",
                    "</Placemark>",
                ]
            )
        )

    return "\n".join(
        [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<kml xmlns=\"http://www.opengis.net/kml/2.2\">",
            "<Document>",
            *placemarks,
            "</Document>",
            "</kml>",
        ]
    )
