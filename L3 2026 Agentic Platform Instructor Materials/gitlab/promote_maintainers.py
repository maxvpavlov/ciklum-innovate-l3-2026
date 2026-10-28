"""Make each learner a Maintainer of their own course project on gitlab.ciklum.net.

Learners are Developers on the course group, so they cannot change their own project's settings
(for example, unprotect main). This makes each project's creator a direct Maintainer of that
project only; their group role stays Developer.

    GITLAB_TOKEN=... python3 promote_maintainers.py                 # print the plan, change nothing
    GITLAB_TOKEN=... python3 promote_maintainers.py --apply         # promote, then read every project back
    GITLAB_TOKEN=... python3 promote_maintainers.py --apply --include tnega_ai

A project is promoted only when its path ends in "-<creator's username>", the name the course setup
prompt gives (agentic-platform-<acronym>). Any other project is reported for a decision and changed
only when named with --include. Group Owners and creators who already have Maintainer or higher on
the project are skipped, so the script is safe to run again. It needs a token with the api scope
from an account that owns the group. Standard library only.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HOST = "https://gitlab.ciklum.net/api/v4"
GROUP = "innovate-2026"
MAINTAINER, OWNER = 40, 50


def call(method, path, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    request = urllib.request.Request(HOST + path, data=body, method=method,
                                     headers={"PRIVATE-TOKEN": os.environ["GITLAB_TOKEN"]})
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, {"message": error.read().decode(errors="replace")[:200]}


def pages(path):
    items, page = [], 1
    while True:
        status, batch = call("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
        if status != 200:
            sys.exit(f"GET {path} failed: {status} {batch}")
        items += batch
        if len(batch) < 100:
            return items
        page += 1


def plan(include):
    group = urllib.parse.quote(GROUP, safe="")
    members = {m["id"]: m for m in pages(f"/groups/{group}/members")}
    rows = []
    for project in sorted(pages(f"/groups/{group}/projects?include_subgroups=true"), key=lambda p: p["path"]):
        creator = project["creator_id"]
        username = members[creator]["username"] if creator in members else call("GET", f"/users/{creator}")[1]["username"]
        direct = {m["id"]: m["access_level"] for m in pages(f"/projects/{project['id']}/members")}
        if members.get(creator, {}).get("access_level", 0) >= OWNER:
            action = "skip: group owner"
        elif direct.get(creator, 0) >= MAINTAINER:
            action = "already maintainer"
        elif project["path"].endswith("-" + username) or project["path"] in include:
            action = "promote"
        else:
            action = "check: name does not match the creator (use --include to promote)"
        rows.append({"project": project, "creator": creator, "username": username, "action": action,
                     "is_member": creator in direct})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--apply", action="store_true", help="make the changes (default: print the plan only)")
    parser.add_argument("--include", action="append", default=[], metavar="PROJECT_PATH",
                        help="also promote this project's creator although its name does not match")
    args = parser.parse_args()
    if not os.environ.get("GITLAB_TOKEN"):
        sys.exit("Set GITLAB_TOKEN to a token with the api scope.")
    rows = plan(set(args.include))
    for row in rows:
        print(f"{row['project']['path']:<40} {row['username']:<12} {row['action']}")
    todo = [row for row in rows if row["action"] == "promote"]
    print(f"\n{len(todo)} to promote, {len(rows)} projects in {GROUP}.")
    if not args.apply:
        print("Plan only; run again with --apply to promote.")
        return
    failed = 0
    for row in todo:
        project, creator = row["project"]["id"], row["creator"]
        if row["is_member"]:  # a direct member below Maintainer: raise the level
            status, result = call("PUT", f"/projects/{project}/members/{creator}", {"access_level": MAINTAINER})
        else:
            status, result = call("POST", f"/projects/{project}/members", {"user_id": creator, "access_level": MAINTAINER})
        if result.get("access_level") != MAINTAINER:
            failed += 1
            print(f"FAILED {row['project']['path']}: {status} {result}")
    # Read every promoted project back rather than trusting the write responses.
    confirmed = sum(1 for row in todo
                    if {m["id"]: m["access_level"] for m in pages(f"/projects/{row['project']['id']}/members")}
                    .get(row["creator"]) == MAINTAINER)
    print(f"Promoted and confirmed: {confirmed} of {len(todo)}; failed: {failed}.")
    sys.exit(1 if failed or confirmed != len(todo) else 0)


if __name__ == "__main__":
    main()
