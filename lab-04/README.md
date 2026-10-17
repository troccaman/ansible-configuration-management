# Lab 4 – User & Permission Management

## Purpose

Automate user creation, sudo group membership, and SSH key distribution on all managed nodes. Verify passwordless SSH login and demonstrate idempotency.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Managed Nodes:** `node1.local` and `node2.local`
- **Automation Tool:** Ansible Core
- **Connection User:** `troccaman`
- **Managed User:** `devops_admin`
- **Authentication:** SSH key-based authentication
- **Configuration:** Local `ansible.cfg` copied from Lab 3

All Ansible commands are run from `lab-04`. The local `ansible.cfg` specifies `inventory.ini` as the inventory.

## Task 1 – Inventory and SSH Keys

**`inventory.ini`:**

```ini
[webservers]
node1.local ansible_user=troccaman
node2.local ansible_user=troccaman
```

Verify connectivity:

```bash
ansible all -m ping
```

Both nodes returned `SUCCESS` with `pong`.

Create a dedicated SSH key pair on the control node:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/devops_admin -C "devops_admin@controlnode"
```

The passphrase was left empty for this lab.

- **Private key:** `~/.ssh/devops_admin`
- **Public key:** `~/.ssh/devops_admin.pub`

The private key stays on the control node and must never be committed to Git.

Install the collection required for SSH key management:

```bash
ansible-galaxy collection install ansible.posix
```

## Task 2 – User Management Playbook

**`users.yml`:**

```yaml
---
- name: Create devops_admin on all nodes
  hosts: all
  become: true

  tasks:
    - name: Create users with home directory and sudo membership
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

The playbook:

- Targets all nodes in the inventory.
- Creates `devops_admin` with a home directory and Bash shell.
- Adds the user to `sudo`, preserving existing supplementary groups.
- Reads the public key from the control node and installs it in the user's `authorized_keys` file on each managed node.

Run the playbook:

```bash
ansible-playbook users.yml -K
```

The `-K` option prompts for the connection user's sudo password.

**First run:**

```text
PLAY RECAP
node1.local : ok=3 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
node2.local : ok=3 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

Both nodes were configured successfully without errors.

## Task 3 – Verify Passwordless SSH Login

Run from the control node:

```bash
ssh -i ~/.ssh/devops_admin -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no devops_admin@node1.local 'whoami; id'
```

```bash
ssh -i ~/.ssh/devops_admin -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no devops_admin@node2.local 'whoami; id'
```

Password and keyboard-interactive authentication are disabled for these test connections.

**Output on both nodes:**

```text
devops_admin
uid=1001(devops_admin) gid=1001(devops_admin) groups=1001(devops_admin),27(sudo)
```

This confirms passwordless SSH login as `devops_admin` and membership in the `sudo` group.

Passwordless SSH and passwordless sudo are separate settings. This playbook does not configure passwordless sudo.

## Task 4 – Verify Idempotency

Run the playbook again:

```bash
ansible-playbook users.yml -K
```

**Second run:**

```text
PLAY RECAP
node1.local : ok=3 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
node2.local : ok=3 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

No changes were needed because both nodes already matched the desired configuration. This demonstrates idempotency.

## Conclusion

Ansible successfully created `devops_admin` on both nodes, configured sudo group membership, and installed the SSH public key. Passwordless SSH login was verified, and a second run completed without changes.