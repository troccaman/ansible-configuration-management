
# Lab 2 – Ansible Ad-Hoc Commands

## Purpose

Use Ansible ad-hoc commands to retrieve system information from multiple managed nodes without connecting to each server individually.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Managed Nodes:** node1.local, node2.local
- **Automation Tool:** Ansible
- **Authentication:** SSH key-based authentication

## Task 1 – Check Disk Usage

**Command:**

```bash
ansible all -i 'node1.local,node2.local,' -u troccaman -m command -a 'df -h /'
```

<details>
<summary>View Ansible Output</summary>

```text
node1.local | CHANGED | rc=0 >>
Filesystem                         Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv   19G  4.7G   13G  28% /

node2.local | CHANGED | rc=0 >>
Filesystem                         Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv   19G  5.1G   13G  30% /
```

</details>

**Result:** Both nodes returned disk usage information successfully. Node1 uses 28% and node2 uses 30% of their root filesystem capacity.

## Task 2 – Identify Linux Distribution

**Command:**

```bash
ansible all -i 'node1.local,node2.local,' -u troccaman -m setup -a 'filter=ansible_distribution*'
```

<details>
<summary>View Ansible Output</summary>

```text
node1.local | SUCCESS => {
    "ansible_facts": {
        "ansible_distribution": "Ubuntu",
        "ansible_distribution_file_parsed": true,
        "ansible_distribution_file_path": "/etc/os-release",
        "ansible_distribution_file_variety": "Debian",
        "ansible_distribution_major_version": "24",
        "ansible_distribution_release": "noble",
        "ansible_distribution_version": "24.04",
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false
}

node2.local | SUCCESS => {
    "ansible_facts": {
        "ansible_distribution": "Ubuntu",
        "ansible_distribution_file_parsed": true,
        "ansible_distribution_file_path": "/etc/os-release",
        "ansible_distribution_file_variety": "Debian",
        "ansible_distribution_major_version": "24",
        "ansible_distribution_release": "noble",
        "ansible_distribution_version": "24.04",
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false
}
```

</details>

**Result:** Both nodes are running Ubuntu 24.04. The `setup` module collected system facts without modifying the nodes (`changed: false`).

## Technical Explanation

- **`command`:** Executes commands remotely. Reports `CHANGED` by default, even for read-only commands.
- **`setup`:** Collects structured system information (Ansible facts).
- **`-i`:** Specifies the inventory containing the managed nodes.
- **`-u`:** Defines the SSH username.
- **`-m`:** Selects the Ansible module.
- **`-a`:** Passes arguments to the selected module.

## Additional Tips

For more compact output and explicit control over parallel execution:

```bash
ansible all -i 'node1.local,node2.local,' -u troccaman -f 2 -m command -a 'df -h /' -o
```

- **`-f 2`:** Allows up to two parallel workers. Ansible already executes hosts in parallel by default, but this flag allows concurrency to be adjusted.
- **`-o`:** Displays compact one-line output per host, useful for quick infrastructure checks.

## Design Decisions & Conclusion

Ansible was chosen for centralized, agentless administration using SSH. The `setup` module provides structured facts that can be reused in future playbooks.

Ad-hoc commands are useful for quick checks, while repeatable configuration tasks are better managed with version-controlled playbooks.

Both tasks completed successfully, demonstrating efficient remote execution and system information gathering across multiple nodes.
