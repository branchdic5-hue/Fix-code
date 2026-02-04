import os
from typing import Dict, List

import requests


def search_numbers(numbers: List[str], api_url: str, api_key: str) -> List[Dict]:
    if not api_url or not api_key:
        return [
            {
                "number": number,
                "primary_name": "",
                "alternate_name_1": "",
                "alternate_name_2": "",
                "alternate_name_3": "",
                "facebook_profile_link": "",
                "facebook_id": "",
                "eyecon_profile_icon": "",
                "status": "missing_api_key",
            }
            for number in numbers
        ]

    results = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for number in numbers:
        response = requests.post(api_url, json={"number": number}, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
        results.append(
            {
                "number": number,
                "primary_name": payload.get("primary_name", ""),
                "alternate_name_1": payload.get("alternate_name_1", ""),
                "alternate_name_2": payload.get("alternate_name_2", ""),
                "alternate_name_3": payload.get("alternate_name_3", ""),
                "facebook_profile_link": payload.get("facebook_profile_link", ""),
                "facebook_id": payload.get("facebook_id", ""),
                "eyecon_profile_icon": payload.get("eyecon_profile_icon", ""),
                "status": "ok",
            }
        )
    return results


def load_eyecon_config() -> Dict[str, str]:
    return {
        "api_url": os.getenv("EYECON_API_URL", ""),
        "api_key": os.getenv("EYECON_API_KEY", ""),
    }
