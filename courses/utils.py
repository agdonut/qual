import requests

UNSPLASH_ACCESS_KEY = "taxB7l0EXDPtzrNN33H2aMxn5zBugcZ768U7O2hVhaQ"


def get_course_image(title):

    url = "https://api.unsplash.com/search/photos"

    params = {
        "query": title,
        "client_id": UNSPLASH_ACCESS_KEY,
        "per_page": 1,
        "orientation": "landscape",
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        if response.status_code != 200:
            return None

        data = response.json()

        results = data.get("results")

        if not results:
            return None

        return results[0]["urls"]["regular"]

    except requests.exceptions.RequestException:
        return None