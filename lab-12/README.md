# Lab 12 – Project Summary & Architecture Rationale

## Purpose

Consolidate the course labs into a structured Git repository, document how to run the main application and explain the architecture, security and operational decisions.

## Deliverables

- [Main README](../README.md): environment, prerequisites, lab overview and execution commands.
- [Architecture rationale](../ARCHITECTURE.md): tool selection, security, scalability and operations.
- [Main application](../lab-10/): PostgreSQL and web application deployment.
- Labs 01–11: implementation and documentation of the individual exercises.

The existing lab structure is retained. Roles, variables, templates and inventories are organized within the relevant lab directories.

## Final Review

The review included these corrections:

- Removed a plaintext database password from Lab 7 documentation, rotated the credential and verified authentication and idempotency.
- Corrected the sudo password prompt configuration in the lab configuration files.
- Aligned Lab 10's documented Vault password path with its configuration.
- Added an explicit task to keep Nginx running and enabled, then verified recovery after stopping it.
- Updated the main README with prerequisites and execution instructions.

## Verified Results

Lab 7 completed with successful database authentication, `changed=0` and `failed=0` after credential rotation.

Lab 10 passed the syntax check and repeated deployment:

```text
node1.local : ok=17 changed=0 unreachable=0 failed=0
node2.local : ok=8  changed=0 unreachable=0 failed=0
```

The application returned HTTP `200` with database connectivity. After Nginx was stopped, re-running the playbook restored service with one change on node1 and no failures.

See [Lab 10](../lab-10/README.md) for service recovery tests. Environment-specific assumptions and limitations are documented in the main README and architecture rationale.