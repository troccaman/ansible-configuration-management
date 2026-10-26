# Lab 11 – Ansible vs Puppet

## Purpose

Compare Ansible and Puppet to understand their architecture, execution order, syntax, advantages, and disadvantages.

## 1. Push vs Pull

**Ansible (Push):** The control node connects to managed nodes via SSH and applies configuration changes when a playbook is executed. No agent is required on the managed nodes.

**Puppet (Pull):** Puppet Agents periodically contact a Puppet Server to retrieve a configuration catalog describing the desired system state. The agents apply any necessary changes to maintain that state.

## 2. Execution Order

**Ansible:** Tasks normally execute from top to bottom. If the configuration file task runs before Nginx is installed, it may fail because the required directory does not exist.

**Puppet:** Puppet uses resource dependencies to control execution order. Without explicit dependencies, resources normally follow their declaration order. The `require => Package['nginx']` declaration ensures that Nginx is handled before the configuration file, regardless of their placement in the manifest.

## 3. Comparison

| Category | Ansible | Puppet |
|---|---|---|
| Architecture | Push-based, agentless | Traditionally pull-based, agent-based |
| Communication | SSH | Puppet Agent and Puppet Server |
| Language/Syntax | YAML | Puppet DSL |
| Execution | Tasks normally run in playbook order | Resources follow declared dependencies and default ordering |
| Advantages | Simple setup, readable syntax, no agents required | Automatic configuration enforcement, explicit dependency management |
| Disadvantages | Task order matters; recurring execution requires scheduling | More complex infrastructure, agent installation and maintenance |

## Conclusion

The main difference between Ansible and Puppet is **how configurations are delivered and applied**.

Ansible uses a **push-based approach**, where a control node connects to managed servers via SSH and executes tasks in a defined order. This makes it straightforward to automate deployments and configuration changes.

Puppet typically uses a **pull-based approach**, where agents periodically retrieve configuration catalogs from a Puppet Server. Puppet uses resource dependencies to control execution order and automatically correct configuration drift.

**In summary**, both tools support desired-state configuration management and idempotency. Ansible is well suited for on-demand automation and deployments, while Puppet is designed for regularly enforcing consistent configurations across managed systems.