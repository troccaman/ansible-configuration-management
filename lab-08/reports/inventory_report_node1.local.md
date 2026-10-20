# CMDB Report: node1.local

## Server Information

- **Hostname:** node1
- **Operating System:** Ubuntu 24.04
- **CPU:** 2 vCPUs
- **Total RAM:** 913 MB
- **Free RAM:** 300 MB

## Network Information

- **IPv4:** 10.6.69.123

## Disk Information

- **Disk:** dm-0
- **Size:** 18.47 GB
- **Disk:** sda
- **Size:** 40.00 GB

## Filesystem Usage

- **Mount Point:** /
- **Filesystem:** ext4
- **Total Space:** 18.01 GB
- **Available Space:** 11.79 GB

- **Mount Point:** /boot
- **Filesystem:** ext4
- **Total Space:** 1.9 GB
- **Available Space:** 1.59 GB

- **Mount Point:** /boot/efi
- **Filesystem:** vfat
- **Total Space:** 1.05 GB
- **Available Space:** 1.04 GB


## Uptime

- **Uptime:** 8.14 days

## Installed Packages (Key Services)

- **nginx:** 1.24.0-2ubuntu7.18
- **postgresql:** 16+257build1.1
- **postgresql-16:** 16.15-0ubuntu0.24.04.1
- **openssh-server:** 1:9.6p1-3ubuntu13.20

Full package inventory: `packages_node1.local.md`

## Configuration Item Relationships

| Source | Relationship | Destination | Service | Port |
|---|---|---|---|---|
| controlnode | manages | node1.local | SSH | 22 |
| node1.local | connects_to | node2.local | PostgreSQL | 5432 |

## Intended Server Services

- nginx

## Impact Analysis

- **Failure:** Web server unavailable
- **Affected Service:** Nginx
- **Impact:** Nginx websites become unavailable.