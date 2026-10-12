# Lab 1 – Environment Setup and SSH

## Purpose
Configure three Ubuntu servers and establish passwordless SSH authentication for Ansible.

## Environment
- **controlnode:** Ubuntu Server 24.04
- **node1:** Ubuntu Server 24.04
- **node2:** Ubuntu Server 24.04
- **Virtualization:** Hyper-V with Default Switch

## Implementation
Document the installation and configuration of:
- Ubuntu Server
- Network settings
- mDNS (Avahi)
- SSH key-based authentication
- Ansible

## Verification
Verify and document:
- Successful passwordless SSH connections from controlnode to node1 and node2.
- Successful Ansible ping tests on both managed nodes.

## Results
![Ansible Ping Result](screenshots/ansible-ping.png)

## Problems and Solutions
None.