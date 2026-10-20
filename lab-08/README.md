# Lab 8 – CMDB & Configuration Items

## Purpose

Automate infrastructure inventory and Configuration Item (CI) documentation using Ansible.

The goal is to collect server information, generate structured reports and document relationships between infrastructure components.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Web Server:** `node1.local` – Nginx
- **Database Server:** `node2.local` – PostgreSQL 16
- **Automation:** Ansible, Roles, Jinja2
- **Authentication:** SSH key-based authentication

## Project Structure

```text
lab-08/
├── ansible.cfg
├── group_vars/
│   └── all/
│       └── vars.yml
├── inventory.ini
├── README.md
├── reports/
│   ├── inventory_report_node1.local.md
│   ├── inventory_report_node2.local.md
│   ├── packages_node1.local.md
│   └── packages_node2.local.md
├── roles/
│   └── postgresql/
│       ├── handlers/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml
├── screenshots/
│   ├── 01-playbook-idempotency.png
│   └── 02-postgresql-connectivity.png
├── site.yml
└── templates/
    ├── inventory_report.md.j2
    └── packages.md.j2
```

## Implementation

### 1. Automated CI Collection

Created `site.yml` using Ansible Facts and `package_facts` to collect:

- Hostname, OS version and CPU
- Total and free RAM
- IPv4 addresses
- Disk information and filesystem usage
- System uptime
- Installed packages and versions

Jinja2 templates generate individual Markdown reports on the control node using `delegate_to: localhost`.

Complete package inventories are stored separately to keep the main reports readable.

### 2. PostgreSQL Automation

Created an Ansible Role to install and configure PostgreSQL on `node2.local`.

- Installed PostgreSQL 16.
- Configured network listening addresses in `postgresql.conf`.
- Restricted remote authentication attempts to the web server's IP using `pg_hba.conf`.
- Used a handler to restart PostgreSQL only when configuration changes.

### 3. CMDB & CI Relationships

Each server is documented as a Configuration Item (CI), including its hardware, operating system, network configuration and installed software.

Server relationships are defined in `group_vars/all/vars.yml`.

```text
controlnode → node1.local (SSH, port 22)
controlnode → node2.local (SSH, port 22)
node1.local → node2.local (PostgreSQL, TCP 5432)
```

The reports also include impact analysis:

- **node1 failure:** Nginx becomes unavailable.
- **node2 failure:** PostgreSQL becomes unavailable to database clients.
- **Control node failure:** Ansible management becomes unavailable, while existing services may continue running.

TCP connectivity was verified, but no application-level database dependency was implemented.

The generated reports provide a lightweight CMDB inventory rather than a traditional CMDB database.

### 4. Example Collected Information

Example from the generated CMDB report for `node1.local`:

```text
Hostname: node1
Operating System: Ubuntu 24.04
CPU: 2 vCPUs
Total RAM: 963 MB
Free RAM: 293 MB
IPv4: 10.6.69.123
Disk: sda – 40.00 GB
Filesystem: ext4
Total Storage (/): 18.01 GB
Available Storage (/): 11.79 GB
Uptime: 8.07 days
```

The report also includes installed software, CI relationships and impact analysis. A separate package report contains the complete list of installed packages and versions.

System values such as free RAM and uptime are collected dynamically and may change between executions.

## Verification

### 1. Execute Playbook

```bash
ansible-playbook site.yml -K
```

### 2. Verify PostgreSQL

```bash
ansible dbservers -b -m command -a "pg_lsclusters" -K
```

**Output:**

```text
Ver Cluster Port Status Owner
16  main    5432 online postgres
```

### 3. Verify Server Communication

Tested TCP connectivity from `node1.local` to PostgreSQL on `node2.local`.

```bash
ansible webservers -m ansible.builtin.shell -a "timeout 5 bash -c 'echo > /dev/tcp/10.6.69.45/5432' && echo 'Port 5432 reachable' || echo 'Connection failed'"
```

**Output:**

```text
node1.local | CHANGED | rc=0 >>
Port 5432 reachable
```

This confirms TCP connectivity, not PostgreSQL authentication or an application-level dependency.

### 4. Verify CI Relationships

```bash
grep 'connects_to' reports/inventory_report_*.md
```

**Output:**

```text
reports/inventory_report_node1.local.md:| node1.local | connects_to | node2.local | PostgreSQL | 5432 |
reports/inventory_report_node2.local.md:| node1.local | connects_to | node2.local | PostgreSQL | 5432 |
```

### 5. Verify Idempotency

Repeated the playbook execution to ensure that unchanged configurations do not trigger unnecessary modifications.

**Final Play Recap:**

```text
node1.local : ok=5  changed=1  unreachable=0  failed=0
node2.local : ok=9  changed=1  unreachable=0  failed=0
```

PostgreSQL configuration tasks returned `ok`. Only the main CMDB reports changed because dynamic system information, such as free RAM and uptime, was refreshed.

## Troubleshooting

- **Jinja2:** Fixed a misspelled variable and an extra `{% endfor %}` that prevented report generation.
- **PostgreSQL:** Initially listened only on `127.0.0.1`. Updated the configuration through Ansible and verified TCP connectivity from node1.

## Screenshots

- [Playbook Execution & Idempotency](screenshots/01-playbook-idempotency.png)
- [PostgreSQL Connectivity](screenshots/02-postgresql-connectivity.png)

## Conclusion

This lab demonstrates automated CI discovery, centralized CMDB documentation, server relationships, impact analysis and idempotent configuration management.

Ansible and Jinja2 provide a repeatable way to keep infrastructure documentation updated.