# Ansible Configuration Management

A collection of practical Ansible labs focused on Linux server automation, configuration management, security and application deployment.

Developed as part of the **DevOps Engineer program at Nackademin**, progressing from basic Ansible commands to automated multi-tier application deployment.

## Environment

- **Control Node:** Ubuntu Server 24.04
- **Managed Nodes:** `node1.local`, `node2.local` (Ubuntu Server 24.04)
- **Virtualization:** Hyper-V
- **Automation Tool:** Ansible Core 2.16.3
- **Authentication:** SSH key-based authentication
- **Version Control:** Git and GitHub

## Labs

| Lab | Topic | Description |
|---|---|---|
| [Lab 01](lab-01/) | Ansible Setup | Configure Ansible, SSH and managed nodes. |
| [Lab 02](lab-02/) | Ad-Hoc Commands | Execute remote commands and gather system facts. |
| [Lab 03](lab-03/) | Playbooks & Idempotency | Automate Nginx installation and verify idempotency. |
| [Lab 04](lab-04/) | User Management | Manage users, sudo access and SSH keys. |
| [Lab 05](lab-05/) | Ansible Roles | Organize tasks into reusable roles. |
| [Lab 06](lab-06/) | Jinja2 Templates | Deploy customized web pages using templates and handlers. |
| [Lab 07](lab-07/) | Ansible Vault | Secure credentials and automate PostgreSQL deployment. |
| [Lab 08](lab-08/) | CMDB & Configuration Items | Generate infrastructure reports and document dependencies. |
| [Lab 09](lab-09/) | Dynamic Inventory | Generate inventory from JSON using Python. |
| [Lab 10](lab-10/) | Multi-Tier Deployment | Deploy Flask, Gunicorn, Nginx and PostgreSQL across two nodes. |

Each lab includes its own configuration files and documentation.

## Technologies

Ansible · Python · Jinja2 · Linux · Nginx · Gunicorn · Flask · PostgreSQL · Ansible Vault · systemd · Git

## Architecture

```text
            Control Node
               Ansible
                  |
             SSH Access
                  |
         +--------+--------+
         |                 |
         v                 v
    node1.local       node2.local
    Flask             PostgreSQL
    Gunicorn
    Nginx
```

## Key Concepts

- **Automation & Idempotency:** Manage infrastructure consistently using Ansible playbooks.
- **Roles & Templates:** Structure reusable configurations with roles and Jinja2.
- **Security:** Protect credentials using Ansible Vault and restricted access.
- **Dynamic Inventory:** Generate Ansible inventory using Python and JSON.
- **Infrastructure Documentation:** Collect system facts and document server dependencies.
- **Deployment & Recovery:** Manage services with systemd and restore stopped services using Ansible.

## Conclusion

This project demonstrates the progression from basic Ansible configuration to automated deployment of a multi-tier application.

Through the labs, I gained practical experience with Linux automation, reusable roles, secure credential management, infrastructure documentation and service troubleshooting.

The final labs combine these concepts into a structured DevOps workflow, demonstrating how Configuration Management improves consistency, maintainability and reliability.
