"""CLI for the local platform API; secrets belong in environment variables."""
import argparse
import json
import os
from pathlib import Path
import time
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["submit", "inspect", "cancel", "approve", "deny", "resume", "trace"])
    parser.add_argument("value", nargs="?", default="INC-001")
    parser.add_argument("--agent", default="single")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--output", default="var/trace.html")
    args = parser.parse_args()
    with httpx.Client(base_url=args.url, headers={"Authorization": "Bearer "+os.getenv("PLATFORM_TOKEN", "demo-acme")}, timeout=15) as client:
        if args.command == "submit":
            response = client.post("/runs", json={"incident_id": args.value, "agent": args.agent})
            response.raise_for_status(); result = response.json()
            if args.wait:
                deadline = time.monotonic()+60
                while time.monotonic() < deadline:
                    response = client.get("/runs/"+result["id"])
                    response.raise_for_status(); result = response.json()
                    if result["status"] not in {"queued", "running"}: break
                    time.sleep(.1)
        elif args.command in {"approve", "deny"}:
            report = client.get("/runs/"+args.value)
            report.raise_for_status()
            proposal = report.json().get("proposal")
            if not proposal: raise SystemExit("No pending proposal")
            print(json.dumps({"reviewed_proposal": proposal}, indent=2))
            response = client.post(f"/runs/{args.value}/decision", json={"key": proposal["key"], "decision": args.command})
            response.raise_for_status(); result = response.json()
        elif args.command == "trace":
            response = client.get(f"/runs/{args.value}/trace/view")
            response.raise_for_status()
            path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(response.text); result = {"trace_file": str(path)}
        else:
            suffix = "" if args.command == "inspect" else "/"+args.command
            response = client.get("/runs/"+args.value) if not suffix else client.post("/runs/"+args.value+suffix)
            response.raise_for_status(); result = response.json()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

