"""Run one lesson's executable demonstration: python -m incident.lab 01."""
import argparse
import asyncio
import importlib
import json
from incident import LESSON


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson", type=int)
    args = parser.parse_args()
    if not 1 <= args.lesson <= LESSON:
        parser.error(f"This checkpoint provides lessons 1 through {LESSON}.")
    module = importlib.import_module(f"incident.labs.l{args.lesson:02}")
    print(json.dumps(asyncio.run(module.demo()), indent=2, default=str))


if __name__ == "__main__":
    main()

