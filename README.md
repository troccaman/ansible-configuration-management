# Ansible Configuration Management

Practical labs in Linux automation and Configuration Management, developed during the **DevOps Engineer program at Nackademin**.

The project progresses from basic Ansible commands to a multi-tier application with Flask, Gunicorn, Nginx and PostgreSQL.

## Environment

- **Infrastructure:** Three Ubuntu Server 24.04 VMs in Hyper-V.
- **Control node:** Ansible Core 2.16.3.
- **node1.local:** Nginx, Gunicorn and Flask.
- **node2.local:** PostgreSQL 16.
- **Access:** SSH keys and sudo using `troccaman`.

These application roles describe the final deployment in Lab 10. Earlier labs use the nodes for separate exercises.

## Prerequisites

- Git, Python 3 and Ansible installed on the control node.
- Both managed nodes reachable by hostname, with SSH key authentication and sudo access.
- Internet access for package installation.
- The existing Vault decryption password.
- Required Ansible collections:

```bash
ansible-galaxy collection install community.postgresql ansible.posix
```

Adapt the SSH username and inventory to your environment if needed. The project was tested with Ansible Core 2.16.3; Lab 7 used community.postgresql 3.3.0.

## Run the Main Application

Clone the repository using an account with access, then enter Lab 10:

```bash
git clone https://github.com/troccaman/ansible-configuration-management.git
cd ansible-configuration-management/lab-10
```

Run the commands below from `lab-10` so Ansible loads its local configuration.

### Prepare Vault Access

If not already configured, store the existing Vault decryption password in `~/.ansible/vault_pass`:

```bash
mkdir -p ~/.ansible
chmod 700 ~/.ansible
nano ~/.ansible/vault_pass
chmod 600 ~/.ansible/vault_pass
```

Keep this file outside Git. A new, arbitrary password will not decrypt the existing Vault file.

### Check and Deploy

```bash
ansible all -i inventory.ini -m ping
ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml
```

Enter the sudo password when prompted. Ansible configures PostgreSQL on node2 and the web application on node1.

### Verify

```bash
curl --max-time 5 -sS -o /dev/null -w 'HTTP status: %{http_code}\n' http://node1.local
```

Expected result: `HTTP status: 200`. Open `http://node1.local` to see the database status `Connected`.

Run the playbook again to check idempotency:

```bash
ansible-playbook -i inventory.ini site.yml
```

Verified result:

```text
node1.local : ok=17 changed=0 unreachable=0 failed=0
node2.local : ok=8  changed=0 unreachable=0 failed=0
```

See [Lab 10](lab-10/README.md) for implementation details and recovery tests.

## Labs

| Lab | Topic |
|---|---|
| [01](lab-01/) | Environment setup and SSH |
| [02](lab-02/) | Ad-hoc commands and system facts |
| [03](lab-03/) | Playbooks and idempotency |
| [04](lab-04/) | Users, sudo groups and SSH keys |
| [05](lab-05/) | Reusable roles |
| [06](lab-06/) | Jinja2 templates |
| [07](lab-07/) | Ansible Vault and PostgreSQL |
| [08](lab-08/) | CMDB reports and server dependencies |
| [09](lab-09/) | Dynamic inventory using Python and JSON |
| [10](lab-10/) | Multi-tier application deployment |
| [11](lab-11/) | Ansible vs Puppet |
| [12](lab-12/) | Project summary and architecture rationale |

Each lab has its own README. Run labs individually according to their instructions: several modify the same services and should not be treated as one combined deployment.

- Labs 4–6 require `~/.ssh/devops_admin.pub`, prepared in Lab 4.
- Lab 8 contains fixed IP addresses that must be adapted if the network changes.
- Lab 9 demonstrates inventory generation from local JSON; Lab 10 uses a static inventory.

## Architecture and Security

The control node manages both servers over SSH. Nginx receives HTTP requests on node1 and forwards them to Gunicorn at `127.0.0.1:8000`. Flask connects to PostgreSQL on node2.

Separate `webapp` and `postgresql` roles manage the application and database. Ansible Facts provide node IP addresses, while Jinja2 renders configuration files.

Database passwords are Vault-encrypted in Git. Vault password files and private SSH keys remain outside the repository. The application runs as `www-data`, with runtime credentials stored in a protected environment file.

The architecture rationale is documented in `ARCHITECTURE.md` as part of Lab 12. This is a lab environment; HTTPS and high availability are not implemented.

## Verification and Recovery

Lab 10 was tested for idempotency and recovery after stopping each service:

| Stopped service | Observed result |
|---|---|
| Gunicorn | HTTP `502` |
| PostgreSQL | HTTP `503`, database disconnected |
| Nginx | Connection failed, curl reported `000` |

Re-running the playbook restored each service and returned the application to HTTP `200`.

Service tasks maintain the desired running state. Handlers restart services when configuration changes. Ansible performs recovery when the playbook runs; it does not continuously monitor the environment.