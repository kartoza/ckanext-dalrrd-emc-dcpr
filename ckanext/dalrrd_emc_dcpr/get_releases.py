import requests
import json
from pathlib import Path
import os

username = os.environ["kartoza_github_user"]
token = os.environ["kartoza_github_user_token"]

res = requests.get(
    "https://api.github.com/repos/kartoza/ckanext-dalrrd-emc-dcpr/tags",
    auth=(username, token),
)
releases = json.loads(res.text)
latest_releases_ob = {}
for rel in releases:
    if "rc" in rel.get("name"):
        if "latest_release_candidate" not in latest_releases_ob:
            latest_releases_ob["latest_release_candidate"] = rel.get("name")
    else:
        if "latest_release" not in latest_releases_ob:
            latest_releases_ob["latest_release"] = rel.get("name")

current_file_path = Path(__file__)
releases_file_path = current_file_path.parent.joinpath("releases.txt")
with open(releases_file_path, "w") as f:
    f.write(json.dumps(latest_releases_ob))
