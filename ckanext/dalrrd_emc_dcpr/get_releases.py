import requests
import json

username = "Mohab25"
token = "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"

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

with open("releases.txt", "w") as f:
    f.write(json.dumps(latest_releases_ob))
