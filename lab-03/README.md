# Lab 3 – First Playbook & Idempotency

## Purpose

Create an Ansible playbook to install and manage Nginx, verify that the web server works, and demonstrate idempotency by running the same playbook twice.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Web Server:** `node1.local` (Ubuntu Server 24.04)
- **Automation Tool:** Ansible Core 2.16.3
- **Authentication:** SSH key-based authentication

## Task 1 – Inventory and Playbook

**`inventory.ini`:**

```ini
[webservers]
node1.local ansible_user=troccaman
```

**`web.yml`:**

```yaml
---
- name: Install and configure Nginx
  hosts: webservers
  become: true

  tasks:
    - name: Install Nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true
        cache_valid_time: 3600

    - name: Ensure Nginx is running and enabled
      ansible.builtin.systemd_service:
        name: nginx
        state: started
        enabled: true
```

The `apt` module installs Nginx only when needed. The `systemd_service` module ensures that it is running and enabled at boot. Using state-aware modules instead of shell commands makes repeated execution predictable.

**Inventory and syntax checks:**

```bash
ansible webservers -i inventory.ini --list-hosts
ansible-playbook -i inventory.ini web.yml --syntax-check
```

<details>
<summary>View Ansible Output – Inventory and Syntax</summary>

```text
hosts (1):
  node1.local

playbook: web.yml
```

</details>

## Task 2 – Execute the Playbook

**Command (used for both runs):**

```bash
ansible-playbook -i inventory.ini web.yml --ask-become-pass
```

<details>
<summary>View Ansible Output – First Run</summary>

```text
PLAY [Install and configure Nginx]
TASK [Gathering Facts]
ok: [node1.local]
TASK [Install Nginx]
changed: [node1.local]
TASK [Ensure Nginx is running and enabled]
ok: [node1.local]

PLAY RECAP
node1.local : ok=3 changed=1 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

</details>

<details>
<summary>View Ansible Output – Second Run</summary>

```text
PLAY [Install and configure Nginx]
TASK [Gathering Facts]
ok: [node1.local]
TASK [Install Nginx]
ok: [node1.local]
TASK [Ensure Nginx is running and enabled]
ok: [node1.local]

PLAY RECAP
node1.local : ok=3 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

</details>

**Result:** The first run installed Nginx (`changed=1`). On the second run, Ansible found the desired state already satisfied (`changed=0`). This demonstrates **idempotency**: running the playbook again does not introduce unnecessary changes.

## Task 3 – Verify Nginx

**Service status from Ansible:**

```bash
ansible webservers -i inventory.ini -m command -a 'systemctl status nginx'
```

<details>
<summary>View Ansible Output – Service Status (Excerpt)</summary>

```text
node1.local | CHANGED | rc=0 >>
nginx.service - A high performance web server and a reverse proxy server
Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; preset: enabled)
Active: active (running)
```

</details>

**HTTP response from the control node:**

```bash
curl -I http://node1.local
```

<details>
<summary>View Ansible Output – HTTP Headers</summary>

```text
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Content-Type: text/html
Content-Length: 615
```

</details>

**HTTP check using the Ansible `uri` module:**

```bash
ansible webservers -i inventory.ini -m ansible.builtin.uri -a 'url=http://localhost status_code=200'
```

<details>
<summary>View Ansible Output – URI Check (Excerpt)</summary>

```text
node1.local | SUCCESS => {
    "changed": false,
    "msg": "OK (615 bytes)",
    "server": "nginx/1.24.0 (Ubuntu)",
    "status": 200,
    "url": "http://localhost"
}
```

</details>

**Result:** Nginx is enabled and running. Both HTTP tests returned status `200`, confirming that the web server responds successfully.

## Troubleshooting – Check Mode

The initial dry run with `--check` failed when Ansible tried to manage the Nginx service:

```text
Could not find the requested service nginx: host
```

Check mode simulated installing Nginx but did not actually install it. The next task therefore could not find the service. The initial inventory also contained both nodes; it was corrected to target only `node1.local`. Running the playbook normally installed Nginx and resolved the service error.

This illustrates a limitation of check mode when later tasks depend on resources that earlier tasks would create.

## Additional Configuration – ansible.cfg

A local `ansible.cfg` file was created to define default settings, reduce repetitive command-line arguments, and improve maintainability.

**Configuration:**

```ini
[defaults]
inventory = inventory.ini
remote_user = troccaman
ask_become_pass = true
forks = 5
```

### Configuration Explanation

| Setting | Description |
|---|---|
| `inventory` | Defines the default inventory file, eliminating the need for `-i`. |
| `remote_user` | Specifies the SSH username, eliminating the need for `-u`. |
| `ask_become_pass` | Automatically prompts for the privilege escalation password. |
| `forks` | Allows up to five parallel Ansible workers. |

### Simplified Commands

**Before:**

```bash
ansible-playbook -i inventory.ini web.yml --ask-become-pass
```

**After:**

```bash
ansible-playbook web.yml
```

**Before:**

```bash
ansible webservers -i inventory.ini -m command -a 'systemctl status nginx'
```

**After:**

```bash
ansible webservers -m command -a 'systemctl status nginx'
```

### Design Decision

Centralizing configuration in `ansible.cfg` reduces repetitive commands, improves consistency, and makes the project easier to maintain.

The configuration is version-controlled alongside the playbook and inventory, ensuring reproducible execution.

Ansible automatically loads the local configuration when commands are executed from the `lab-03` directory.