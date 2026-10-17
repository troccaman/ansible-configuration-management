# Lab 5 – Structuring Ansible with Roles

## Purpose

Refactor automation into two reusable Ansible roles: `common` and `webserver`.

Automate user management, Nginx installation, configuration, and service management. Use a handler to restart Nginx only when its configuration changes, and verify idempotency.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Managed Nodes:** `node1.local` and `node2.local`
- **Automation Tool:** Ansible Core
- **Connection User:** `troccaman`
- **Authentication:** SSH key-based authentication
- **Required Collection:** `ansible.posix`, installed in Lab 4

All commands are run from `lab-05` on the control node. Ansible connects to both managed nodes over SSH.

## Task 1 – Configuration and Inventory

**`ansible.cfg`:**

```ini
[defaults]
inventory = inventory.ini
remote_user = troccaman
ask_become_pass = true
forks = 5
```

The local configuration defines the inventory and connection user, so `-i` is not required. Use `-K` to prompt for the sudo password.

**`inventory.ini`:**

```ini
[webservers]
node1.local ansible_user=troccaman
node2.local ansible_user=troccaman
```

Both nodes belong to the `webservers` group targeted by `site.yml`.

## Task 2 – Create the Roles

Create both roles using Ansible Galaxy:

```bash
ansible-galaxy role init roles/common
ansible-galaxy role init roles/webserver
```

Roles separate related tasks into reusable components:

- **`common`:** User creation, sudo group membership, and SSH public key installation.
- **`webserver`:** Nginx installation, website configuration, and service management.

This separation makes the automation easier to maintain. The `common` role can also be reused for servers that do not need Nginx.

Display the generated structure:

```bash
tree roles/
```

**Role structure:**

```text
roles/
├── common
│   ├── defaults
│   │   └── main.yml
│   ├── files
│   ├── handlers
│   │   └── main.yml
│   ├── meta
│   │   └── main.yml
│   ├── README.md
│   ├── tasks
│   │   └── main.yml
│   ├── templates
│   ├── tests
│   │   ├── inventory
│   │   └── test.yml
│   └── vars
│       └── main.yml
└── webserver
    ├── defaults
    │   └── main.yml
    ├── files
    ├── handlers
    │   └── main.yml
    ├── meta
    │   └── main.yml
    ├── README.md
    ├── tasks
    │   └── main.yml
    ├── templates
    ├── tests
    │   ├── inventory
    │   └── test.yml
    └── vars
        └── main.yml

19 directories, 16 files
```

The standard scaffold was retained. This lab uses `tasks/main.yml` in both roles and `handlers/main.yml` in `webserver`. The generated test files are scaffold files, not tests executed during this lab.

## Task 3 – Common Role

Move the user management tasks from Lab 4 into **`roles/common/tasks/main.yml`:**

```yaml
---
- name: Create devops_admin with sudo membership
  ansible.builtin.user:
    name: devops_admin
    state: present
    create_home: true
    shell: /bin/bash
    groups: sudo
    append: true

- name: Add SSH public key for devops_admin
  ansible.posix.authorized_key:
    user: devops_admin
    state: present
    key: "{{ lookup('file', '~/.ssh/devops_admin.pub') }}"
```

The role ensures that `devops_admin` exists with a home directory, Bash shell, and sudo group membership. `append: true` preserves other supplementary group memberships.

The public key is read from the control node and installed on each managed node. The private key remains on the control node and must never be committed to Git.

Although Lab 4 already created the user, keeping these tasks ensures that the desired configuration is maintained. On a new node, the role would create the user and install the public key.

Role task files contain tasks only. The target hosts and privilege escalation are defined in `site.yml`.

## Task 4 – Webserver Role

**`roles/webserver/tasks/main.yml`:**

```yaml
---
- name: Install Nginx
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: Configure default website
  ansible.builtin.copy:
    dest: /etc/nginx/sites-available/default
    owner: root
    group: root
    mode: '0644'
    content: |
      server {
          listen 80 default_server;
          listen [::]:80 default_server;

          server_name _;
          root /var/www/html;
          index index.html index.nginx-debian.html;
      }
  notify: Restart Nginx

- name: Ensure Nginx is running and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
```

The role:

- Installs Nginx using `apt`, appropriate for the Ubuntu nodes.
- Refreshes the package cache when it is older than one hour, avoiding unnecessary updates on repeated runs.
- Configures the default website to serve files from `/var/www/html` on port 80.
- Ensures that Nginx is running and enabled at boot.
- Notifies the restart handler only when the website configuration changes.

## Task 5 – Restart Handler

**`roles/webserver/handlers/main.yml`:**

```yaml
---
- name: Restart Nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

The handler name matches `notify: Restart Nginx` in the configuration task.

When the configuration changes, Ansible queues the handler and normally runs it at the end of the play. If several tasks notify the same handler, it runs once at that point.

This applies configuration changes while avoiding unnecessary service restarts during unchanged runs.

## Task 6 – Main Playbook

**`site.yml`:**

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: true

  roles:
    - common
    - webserver
```

The playbook targets both nodes in `webservers` and runs the roles in the listed order.

`become: true` enables privilege escalation for the tasks in both roles. Keeping these settings in the main playbook allows the roles to be reused with different host groups.

Check the syntax before execution:

```bash
ansible-playbook site.yml --syntax-check
```

Run the automation:

```bash
ansible-playbook site.yml -K
```

## Task 7 – Verify Execution and Handler

**First run:**

```text
RUNNING HANDLER [webserver : Restart Nginx]
changed: [node2.local]
changed: [node1.local]

PLAY RECAP
node1.local : ok=7 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
node2.local : ok=7 changed=3 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

The results show that:

- User management required no changes because Lab 4 had already configured both nodes.
- Nginx was already installed on `node1.local` and was installed on `node2.local`.
- The website configuration changed on both nodes.
- The configuration changes triggered the restart handler on both nodes.
- Both nodes completed without errors.

The Nginx welcome page was also verified in a browser at `http://node2.local`.

## Task 8 – Verify Idempotency

Run the playbook again without changing any files:

```bash
ansible-playbook site.yml -K
```

**Second run:**

```text
PLAY RECAP
node1.local : ok=6 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
node2.local : ok=6 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

Both nodes already matched the desired state, so no changes were required.

The restart handler did not run because the configuration was unchanged. This explains why the second run reported six successful tasks instead of seven.

## Design Rationale

The automation is divided by responsibility: `common` maintains shared user settings, while `webserver` manages Nginx. This makes each role easier to understand, reuse, and extend.

Idempotent modules avoid unnecessary changes, the package cache validity reduces repeated cache updates, and the handler restarts Nginx only when required by a configuration change.

## Conclusion

The automation was successfully structured into two roles called by `site.yml`. Both nodes were configured without errors, configuration changes triggered the Nginx restart handler, and a second run confirmed idempotency with zero changes.