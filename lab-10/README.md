# Lab 10 – Multi-Tier Application Deployment

## Purpose

Automate the deployment of a multi-tier application using Ansible, Flask, Gunicorn, Nginx and PostgreSQL.

The lab demonstrates reusable roles, fact-based configuration, service management, Ansible Vault, idempotency and recovery from service interruptions.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Web Server:** `node1.local` – Flask, Gunicorn and Nginx
- **Database Server:** `node2.local` – PostgreSQL 16
- **Managed Node OS:** Ubuntu Server 24.04
- **Automation Tool:** Ansible Core 2.16.3
- **Authentication:** SSH keys, sudo and Ansible Vault
- **Required Collection:** `community.postgresql`

All commands below are run from `lab-10` on the control node unless otherwise stated.

The managed nodes must be reachable by hostname, with SSH key authentication and sudo access configured for `troccaman`. The control node requires the `community.postgresql` collection and access to the Vault password file.

## Project Structure

```text
lab-10/
├── ansible.cfg
├── group_vars/
│   └── all/
│       └── vault.yml
├── inventory.ini
├── README.md
├── screenshots/
│   ├── 01-application-online.png
│   ├── 02-application-stopped-502.png
│   └── 03-database-disconnected-503.png
├── roles/
│   ├── postgresql/
│   │   ├── handlers/main.yml
│   │   └── tasks/main.yml
│   └── webapp/
│       ├── files/
│       │   ├── index.html.j2
│       │   └── style.css
│       ├── handlers/main.yml
│       ├── tasks/main.yml
│       └── templates/
│           ├── app.py.j2
│           ├── nginx.conf.j2
│           └── vehicle-web.service.j2
└── site.yml
```

## Task 1 – Inventory and Ansible Configuration

**`inventory.ini`:**

```ini
[webservers]
node1.local

[dbservers]
node2.local
```

**`ansible.cfg`:**

```ini
[defaults]
inventory = inventory.ini
vault_password_file = ~/.ansible/vault_pass
remote_user = troccaman
forks = 5

[privilege_escalation]
become_ask_pass = true
```

Ansible loads this configuration when commands are run from `lab-10`. The `become_ask_pass` setting prompts for the sudo password, while `become: true` in the playbook enables privilege escalation.

The Vault password file is stored outside the Git repository with restricted permissions. It decrypts `group_vars/all/vault.yml`, which contains the `vault_db_password` variable.

## Task 2 – Multi-Tier Playbook

**`site.yml`:**

```yaml
---
- name: Gather webserver facts
  hosts: webservers
  gather_facts: true
  tasks: []

- name: Configure PostgreSQL database
  hosts: dbservers
  become: true
  roles:
    - postgresql

- name: Configure web application
  hosts: webservers
  become: true
  roles:
    - webapp
```

The first play collects webserver facts needed to configure database access. The database is then configured before the web application.

Ansible facts supply the node addresses, avoiding fixed IP addresses in the Flask application template.

## Task 3 – PostgreSQL Configuration

The `postgresql` role:

- Installs PostgreSQL, `python3-psycopg2` and `acl`.
- Ensures that PostgreSQL is running and enabled at boot.
- Creates the `vehicle_service` database and `service_app` login.
- Grants the application user database connection privileges.
- Configures PostgreSQL to listen on the database node's IPv4 address.
- Adds a `pg_hba.conf` rule allowing `service_app` to connect to `vehicle_service` from the web node's IPv4 address using SCRAM-SHA-256.

The database password is stored in an encrypted Ansible Vault file. A handler restarts PostgreSQL when its network configuration changes.

## Task 4 – Flask, Gunicorn and Nginx

The `webapp` role installs the Python dependencies, creates a virtual environment, deploys the application and configures Nginx as a reverse proxy.

Requests reach Nginx on port 80. Nginx forwards them to Gunicorn on `127.0.0.1:8000`, which runs Flask. Flask connects to PostgreSQL on `node2.local`, port 5432.

Flask verifies database connectivity with:

```sql
SELECT current_database(), current_user;
```

The HTML template is copied unchanged so that Flask can render it at request time. The Python application is rendered by Ansible to configure the database host.

**`vehicle-web.service.j2` – service configuration excerpt:**

```ini
[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/vehicle-service
Environment=HOME=/tmp
EnvironmentFile=/etc/vehicle-service.env
ExecStart=/opt/vehicle-service/venv/bin/gunicorn --bind 127.0.0.1:8000 app:app
Restart=on-failure
```

The application runs as `www-data`. Its database password is deployed to `/etc/vehicle-service.env`, owned by `root:www-data` with mode `0640`. The task writing this file uses `no_log: true`.

Handlers restart Gunicorn and Nginx when relevant configuration changes. Separate service tasks maintain their running state.

**Nginx service task:**

```yaml
- name: Ensure Nginx is running and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
```

This task starts Nginx if it has stopped, even when no configuration change triggers the restart handler.

## Task 5 – Deployment and Verification

Check the playbook syntax:

```bash
ansible-playbook -i inventory.ini site.yml --syntax-check
```

Deploy the stack:

```bash
ansible-playbook -i inventory.ini site.yml
```

The local configuration supplies the Vault password file and prompts for the sudo password.

Verify the web application:

```bash
curl -i http://node1.local
```

**Verified result:** HTTP `200 OK`. The page reports `Application: Online`, `Database status: Connected`, the database `vehicle_service` and its host address.

![Application online with PostgreSQL connected](screenshots/01-application-online.png)

For a compact HTTP check:

```bash
curl --max-time 5 -sS -o /dev/null -w 'HTTP status: %{http_code}\n' http://node1.local
```

**Result:**

```text
HTTP status: 200
```

**Idempotency:** A repeated run with the Nginx service task included required no changes:

```text
node1.local : ok=17 changed=0 unreachable=0 failed=0
node2.local : ok=8  changed=0 unreachable=0 failed=0
```

## Task 6 – Service Failure and Recovery

### Application Failure and Recovery

Stopped `vehicle-web` on node1. Nginx returned HTTP `502 Bad Gateway` because the upstream application was unavailable.

![Nginx returns 502 when Gunicorn is stopped](screenshots/02-application-stopped-502.png)

Running the playbook restored the application service, and the application became accessible again.

### Database Failure and Recovery

Stopped PostgreSQL on node2. Flask remained reachable but returned HTTP `503 Service Unavailable`, with the database marked `Disconnected`.

![Flask reports a disconnected PostgreSQL database](screenshots/03-database-disconnected-503.png)

Running the playbook restored PostgreSQL. The application returned HTTP `200 OK` with the database status `Connected`.

### Nginx Failure and Recovery

Stopped Nginx on the web node:

```bash
ansible webservers -i inventory.ini -b -m ansible.builtin.service -a "name=nginx state=stopped"
```

Checked the HTTP response:

```bash
curl --max-time 5 -sS -o /dev/null -w 'HTTP status: %{http_code}\n' http://node1.local
```

The connection failed. Curl reported `000`, indicating that no HTTP response was received.

Re-ran the playbook:

```bash
ansible-playbook -i inventory.ini site.yml
```

The playbook restored Nginx:

```text
node1.local : ok=17 changed=1 unreachable=0 failed=0
node2.local : ok=8  changed=0 unreachable=0 failed=0
```

Repeated the HTTP check:

```text
HTTP status: 200
```

This confirms that the service task restores a stopped Nginx instance without requiring a configuration change.

All three scenarios demonstrate recovery when the playbook is executed. Ansible is not continuously monitoring these services.

## Conclusion

Successfully deployed a multi-tier application across two Ubuntu servers using separate roles for PostgreSQL and the web application.

Ansible Facts and Jinja2 configure database connectivity, Vault protects credentials in the repository, and service tasks and handlers maintain the required service state.

Repeated execution verified idempotency. Separate interruption tests for Gunicorn, PostgreSQL and Nginx demonstrated the effect of each service failure and confirmed recovery through the playbook.