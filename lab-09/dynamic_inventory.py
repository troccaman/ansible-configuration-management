#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Ansible dynamic inventory")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--host")
    args = parser.parse_args()

    # Load inventory from JSON file
    inventory_file = Path(__file__).resolve().parent / "servers.json"

    with inventory_file.open(encoding="utf-8") as file:
        inventory = json.load(file)

    # Return inventory or host variables
    if args.list:
        print(json.dumps(inventory, indent=2))
    elif args.host:
        print(json.dumps({}))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()