# Architecture Rationale & System Documentation

**Author:** Mikael Andic  
**Date:** 2026-10-29  
**Course:** Automation with Ansible

## 1. Architecture & Tool Selection

The environment consists of three Ubuntu Server 24.04 VMs in Hyper-V:

| Server | Role |
|---|---|
| `controlnode` | Ansible control node |
| `node1.local` | Nginx, Gunicorn and Flask |
| `node2.local` | PostgreSQL 16 |

Separating the application and database provides **clear responsibilities and independent configuration**.

### Why Ansible?

Ansible was chosen for its **agentless SSH-based architecture**, readable YAML playbooks and idempotent configuration management.

Compared with Puppet's traditional server-agent model, Ansible requires less infrastructure for this small environment. However, Puppet supports periodic enforcement, while Ansible requires manual or scheduled execution to correct configuration drift.

### Repository Structure

Labs are organized separately, with local inventories and configuration files. Deployment labs use:

- **Roles:** Reusable tasks (`webapp`, `postgresql`).
- **Templates:** Dynamic configuration using Jinja2.
- **Variables:** Configuration and encrypted secrets in `group_vars`.
- **Handlers:** Service restarts when configurations change.

Labs remain independent because some configure the same services differently.

## 2. Security & Secrets Management

**Ansible Vault** encrypts database credentials stored in Git, while the decryption password remains outside the repository.

Additional security measures:

- SSH key authentication and interactive sudo.
- `become` for privileged tasks.
- Vault password file protected with `0600` permissions.
- Gunicorn running as `www-data` behind Nginx.
- Database credentials stored in `/etc/vehicle-service.env` (`root:www-data`, `0640`).
- `no_log` prevents credentials appearing in normal task output.

During the final review, a plaintext password was removed from Lab 7 documentation and rotated. Authentication was verified afterwards. Earlier Git history may still contain the old credential.

**Limitation:** Vault protects stored secrets, while deployed credentials depend on filesystem permissions.

## 3. Scalability & Configuration

Lab 10 uses a **static inventory** with `webservers` and `dbservers`. Lab 9 demonstrates dynamic inventory using Python and `servers.json`, allowing host changes without editing the script.

Roles support configuration reuse, while **Ansible Facts and Jinja2** reduce hardcoded values. For example, Lab 10 retrieves the database IP dynamically.

For larger environments:

- Separate inventories and `group_vars` could support Dev, Test and Production.
- Additional configuration would be needed for load balancing and database high availability.
- Some fixed hostnames, paths and Lab 8 IP addresses would need parameterization.

The current solution is designed for a small lab, not a production-scale environment.

## 4. Operations & Recovery

### Idempotency

Ansible modules maintain the desired state, while handlers avoid unnecessary restarts. Explicit service tasks restore stopped services even without configuration changes.

**Verified Lab 10 results:**

```text
node1.local : ok=17 changed=0 unreachable=0 failed=0
node2.local : ok=8  changed=0 unreachable=0 failed=0
```

### Verification & Recovery

Syntax checks, Ansible execution results and HTTP checks verify deployment.

Recovery was tested by stopping services individually:

| Service | Failure result |
|---|---|
| Gunicorn | HTTP `502` |
| PostgreSQL | HTTP `503` |
| Nginx | Connection failed (`000`) |

Re-running the playbook restored services and returned **HTTP `200`**.

These tests demonstrate service recovery, not database backup or data restoration.

Ansible corrects drift when executed; automatic enforcement requires scheduling. Lab 8 provides CMDB reports documenting server resources and dependencies.

## 5. Conclusion

Ansible provides an effective solution for this environment through **agentless automation, reusable roles, secure credential handling and idempotent deployments**.

The project demonstrates automated deployment and service recovery. Future improvements could include environment-specific configuration, HTTPS, scheduled execution and high availability.