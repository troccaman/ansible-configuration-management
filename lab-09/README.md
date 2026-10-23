# Lab 9 – Dynamic Inventory with Python

## Purpose

Implement a dynamic Ansible inventory using Python and JSON instead of a static `inventory.ini` file.

The lab demonstrates inventory generation, JSON data loading, and connectivity verification.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Managed Nodes:** `node1.local`, `node2.local` (Ubuntu Server 24.04)
- **Automation Tool:** Ansible Core 2.16.3
- **Scripting Language:** Python 3
- **Authentication:** SSH key-based authentication

## Project Structure

```text
lab-09/
├── ansible.cfg
├── dynamic_inventory.py
├── servers.json
└── README.md
```

## Task 1 – Dynamic Inventory

The Python script reads server information from `servers.json` and returns an Ansible-compatible JSON inventory.

**`servers.json`:**

```json
{
  "webservers": {
    "hosts": ["node1.local"]
  },
  "dbservers": {
    "hosts": ["node2.local"]
  }
}
```

**`dynamic_inventory.py`:**

```python
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
```

Make the script executable:

```bash
chmod +x dynamic_inventory.py
```

## Task 2 – Ansible Configuration

**`ansible.cfg`:**

```ini
[defaults]
inventory = dynamic_inventory.py
remote_user = troccaman
ask_become_pass = true
forks = 5
```

Ansible automatically uses the Python script as its inventory source.

## Task 3 – Inventory Verification

Validate the inventory:

```bash
ansible-inventory --list
```

**Output:**

```json
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped",
            "webservers",
            "dbservers"
        ]
    },
    "dbservers": {
        "hosts": ["node2.local"]
    },
    "webservers": {
        "hosts": ["node1.local"]
    }
}
```

Verify the inventory hierarchy:

```bash
ansible-inventory --graph
```

**Output:**

```text
@all:
  |--@ungrouped:
  |--@webservers:
  |  |--node1.local
  |--@dbservers:
  |  |--node2.local
```

## Task 4 – Connectivity Verification

Test all managed nodes:

```bash
ansible all -m ping
```

**Output:**

```text
node2.local | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
node1.local | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```

Both nodes respond successfully, confirming that Ansible can load the generated inventory and connect via SSH.

## Conclusion

Successfully implemented and verified a Python-based dynamic inventory using JSON as the source of server information.

The Python script reads host and group information from `servers.json` and converts it into an Ansible-compatible JSON format. Separating server data from the script allows hosts and groups to be updated without modifying the Python code.

The inventory was verified using `ansible-inventory --list` and `ansible-inventory --graph`. Connectivity tests with `ansible all -m ping` confirmed that Ansible could identify and connect to both managed nodes via SSH.

Overall, the lab demonstrated how dynamic inventories can simplify infrastructure management and reduce manual configuration. It also provided practical experience with Python, JSON and Ansible inventory management.

Although the solution uses a local JSON file rather than a live API, it provides a foundation for future integration with external systems and cloud environments.
