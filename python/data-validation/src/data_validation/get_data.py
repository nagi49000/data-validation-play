import requests
import ndjson


def get_random_users_from_api(n_record: int, filename: str | None = None) -> list[dict]:
    random_users = []
    for _ in range(n_record):
        response = requests.get("https://randomuser.me/api/")
        records = response.json()["results"]
        random_users += records
    if filename:
        with open(filename, "wt") as f:
            ndjson.dump(random_users, f)
    return random_users
