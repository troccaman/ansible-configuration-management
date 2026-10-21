# Lab 7 – Secrets Management with Ansible Vault

## Purpose

Securely manage database credentials using Ansible Vault and automate PostgreSQL deployment for a vehicle service application.

The lab demonstrates encryption, reusable Ansible roles, database provisioning, least-privilege principles, idempotency, and configuration drift recovery.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Managed Node:** `node1.local` (Ubuntu Server 24.04)
- **Automation:** Ansible Core 2.16.3
- **Collection:** community.postgresql 3.3.0
- **Database:** PostgreSQL
- **Authentication:** SSH keys, sudo, and Ansible Vault

## Project Structure

```text
lab-07/
├── ansible.cfg
├── inventory.ini
├── site.yml
├── group_vars/
│   └── all/
│       ├── vars.yml
│       └── vault.yml
├── roles/
│   └── postgresql/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml
├── screenshots/
└── README.md
```

The Vault password file is stored separately at `~/.ansible/vault_pass`, outside the Git repository.

## Task 1 – Ansible Vault

Created an encrypted variable file containing the required database password (`sommar2024`).

```bash
ansible-vault create group_vars/all/vault.yml
```

**vars.yml:**

```yaml
db_name: vehicle_service
db_user: service_app
db_password: "{{ vault_db_password }}"
```

The database password is protected using AES256 encryption, while non-sensitive configuration remains unencrypted.

**Verification:**

```bash
head -n 1 group_vars/all/vault.yml
```

## Task 2 – Vault Password File

Created a separate Vault password file to enable decryption without interactive password entry.

```bash
mkdir -p ~/.ansible
chmod 700 ~/.ansible
nano ~/.ansible/vault_pass
chmod 600 ~/.ansible/vault_pass
```

The file contains the Vault decryption password and is stored outside Git with restricted permissions (`0600`).

**Verification:**

```bash
ls -l ~/.ansible/vault_pass
```

## Task 3 – PostgreSQL Automation

Created a reusable Ansible role that:

- Installs PostgreSQL, `python3-psycopg2`, and `acl`.
- Ensures PostgreSQL is running and enabled.
- Creates the `vehicle_service` database.
- Creates the `service_app` user using credentials from Vault.
- Grants database connection privileges.
- Verifies database authentication automatically.

The application user has no PostgreSQL administrative privileges.

**Deploy:**

```bash
ansible-playbook site.yml --vault-password-file ~/.ansible/vault_pass -K
```

**Verify PostgreSQL service:**

```bash
ansible dbservers -m command -a "systemctl is-active postgresql" --vault-password-file ~/.ansible/vault_pass
```

## Task 4 – Authentication and Idempotency

The playbook verifies database authentication using:

```sql
SELECT current_user;
```

An Ansible assertion confirms successful login as `service_app`.

**Result:**

```text
Database authentication verified successfully.
ok=8 changed=0 failed=0
```

Repeated executions produce `changed=0`, confirming idempotency.

## Task 5 – Configuration Drift Recovery

Manually revoked the application's explicit CONNECT privilege:

```sql
REVOKE CONNECT ON DATABASE vehicle_service FROM service_app;
```

Re-ran the playbook. Ansible detected and restored the missing privilege.

**Result:**

```text
Grant database connection privilege: changed
ok=8 changed=1 failed=0
```

A final run confirmed `changed=0`.

*Note: PostgreSQL's PUBLIC role retained CONNECT access. The test demonstrates configuration drift remediation, not recovery from a database outage.*

## Task 6 – Vault Password File Verification

Verified successful decryption using the protected password file:

```bash
ansible-vault view group_vars/all/vault.yml --vault-password-file ~/.ansible/vault_pass
```

Executed the playbook without an interactive Vault password prompt:

```bash
ansible-playbook site.yml --vault-password-file ~/.ansible/vault_pass -K
```

**Result:**

```text
Database authentication verified successfully.
ok=8 changed=0 unreachable=0 failed=0
```

This confirms successful database provisioning, authentication, and idempotency using a separate Vault password file.

## Troubleshooting

**Issue 1 – Incorrect Package Name**

- **Problem:** `python-psycopg2` was unavailable.
- **Solution:** Replaced it with `python3-psycopg2`.

**Issue 2 – Privilege Escalation**

- **Problem:** Ansible failed to switch to the `postgres` Linux user due to temporary-file permissions.
- **Solution:** Installed `acl` to support secure privilege escalation.

**Issue 3 – Missing Sudo Password**

- **Problem:** `Missing sudo password`.
- **Solution:** Added `-K` to request the sudo password.

## Security Considerations

- Database credentials are encrypted using Ansible Vault.
- The Vault password file is stored outside Git with `0600` permissions.
- The encrypted `vault.yml` is version-controlled without exposing its plaintext contents.
- Sensitive tasks use `no_log: true`.
- Database administration runs as the `postgres` system user.
- `service_app` has restricted administrative privileges.
- Authentication is verified without exposing credentials in Ansible output.

**Security verification:**

```bash
grep -Rn --exclude=vault.yml 'sommar2024' . || echo "No plaintext password found"
git check-ignore -v group_vars/all/vault.yml
ls -l ~/.ansible/vault_pass
```

No plaintext database password was found in the other lab files, and the encrypted Vault file was not ignored by Git.

## Design Decisions

Ansible was chosen for its agentless SSH-based automation and idempotent configuration management. A reusable PostgreSQL role separates deployment logic from configuration variables.

Ansible Vault protects sensitive credentials, while a separate password file enables repeatable execution without storing the decryption password in Git.

## Screenshots

- [Encrypted Ansible Vault file](screenshots/01-vault-encrypted.png)
- [PostgreSQL installation](screenshots/02-postgresql-installation.png)
- [PostgreSQL service verification](screenshots/03-postgresql-service-active.png)
- [Database authentication and idempotency](screenshots/04-authentication-and-idempotency.png)
- [Configuration drift recovery](screenshots/05-configuration-drift-recovery.png)
- [Final idempotency verification](screenshots/06-final-idempotency.png)
- [Vault Git verification](screenshots/07-vault-gitignore-verification.png)
- [Vault password file permissions](screenshots/08-vault-password-file-verification.png)
- [Successful execution using Vault password file](screenshots/09-vault-password-file-execution.png)

## Conclusion

Successfully automated PostgreSQL provisioning using Ansible Vault and a protected password file.

The lab provided practical experience in secure secrets management, reusable Ansible roles, database authentication, troubleshooting, and least-privilege principles.

Idempotency and configuration drift recovery were verified, demonstrating how Ansible can maintain and restore the desired configuration state.

The solution fulfills the lab's technical requirements while applying security and automation practices relevant to real-world DevOps environments.