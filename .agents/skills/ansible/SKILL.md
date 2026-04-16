---
name: ansible
cluster: devops-sre
description: "Automates IT infrastructure configuration, application deployment, and orchestration using agentless YAML playbooks."
tags: ["devops","automation","configuration-management"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "ansible automation devops configuration management orchestration yaml playbooks"
---

# ansible

## Purpose
Ansible is an open-source automation tool that configures IT infrastructure, deploys applications, and orchestrates tasks using agentless YAML playbooks. It ensures idempotent operations, meaning runs produce the same result regardless of initial state, and operates over SSH without installing agents on target hosts.

## When to Use
Use Ansible for repeatable infrastructure tasks in DevOps pipelines, such as provisioning servers, managing configurations across fleets, or deploying apps in dynamic environments. Apply it when you need agentless automation, like updating software on remote machines, orchestrating multi-step workflows, or integrating with CI/CD tools, but avoid it for real-time monitoring where tools like Prometheus are better suited.

## Key Capabilities
- **Agentless Execution**: Connects via SSH or WinRM; specify hosts in inventory files (e.g., /etc/ansible/hosts) with formats like [web:children] for grouping.
- **Idempotent Playbooks**: Write YAML files that define tasks; e.g., a task to install a package only if absent.
- **Modules and Roles**: Use built-in modules like `apt` for package management; organize code into roles for reusability, stored in directories like roles/webserver/tasks/main.yml.
- **Variables and Templates**: Define vars in YAML (e.g., { "http_port": 80 }) and use Jinja2 templates for dynamic configs, like generating nginx.conf from a template.
- **Orchestration**: Handle dependencies with plays that sequence tasks across hosts, ensuring ordered execution.

## Usage Patterns
To automate tasks, create a playbook (e.g., site.yml) defining plays with hosts, tasks, and vars. Run it using ansible-playbook command. For dynamic inventories, use scripts that output JSON, like pulling from AWS EC2. Structure projects with an inventory file, group_vars for host-specific vars, and roles for modular code. Always test playbooks with --check flag first to simulate changes without applying them.

## Common Commands/API
- **Run a Playbook**: `ansible-playbook site.yml --check --diff` to simulate and show changes; add `-l web` to limit to a host group.
- **Ad Hoc Commands**: `ansible web -m ping` to test connectivity; use `-a "uptime"` for arbitrary commands.
- **Manage Roles**: `ansible-galaxy install geerlingguy.apache` to pull roles; build custom roles with `ansible-galaxy init role_name`.
- **Inventory and Vars**: Set vars via `-e "var1=value1"` or environment vars like `export ANSIBLE_HOST_KEY_CHECKING=False` to bypass host key verification.
- **API Integration**: Ansible's Python API via `ansible_runner` library; e.g., import ansible_runner and run `interface.run(playbook='site.yml', extravars={'key': 'value'})` to execute programmatically.
For authentication, use env vars like `$ANSIBLE_PRIVATE_KEY_FILE=/path/to/key.pem` for SSH keys or `$ANSIBLE_BECOME_PASS` for sudo passwords.

## Integration Notes
Integrate Ansible with CI/CD tools like Jenkins by triggering playbooks via scripts; e.g., in a Jenkinsfile: `sh 'ansible-playbook deploy.yml -e "env=prod"'`. For cloud providers, use dynamic inventories; e.g., configure AWS with `export AWS_ACCESS_KEY_ID=$AWS_KEY` and run `ansible-playbook -i ec2.py site.yml`. Combine with Terraform by running Ansible post-provisioning; ensure vars are passed via files or env vars. Use version control: store playbooks in Git and pull them in pipelines.

## Error Handling
In playbooks, use blocks with rescue and always clauses; e.g.:
```
- block:
    - debug: msg="Task succeeded"
  rescue:
    - debug: msg="Error occurred"
  always:
    - debug: msg="Cleanup step"
```
Check command exit codes; e.g., in scripts: `ansible-playbook site.yml && echo "Success" || echo "Failed"`. For common issues, enable verbose output with `-vvv` to debug SSH connections or module failures. Use facts gathering to handle variable errors, and set `ignore_errors: yes` for non-critical tasks, but only when appropriate to avoid masking issues.

## Concrete Usage Examples
1. **Deploy a Web Server on Ubuntu Hosts**: Create a playbook (webserver.yml) with tasks to install Apache: 
   ```
   - hosts: webservers
     tasks:
       - name: Install Apache
         apt:
           name: apache2
           state: present
   ```
   Run it with: `ansible-playbook webserver.yml -i inventory.txt --become` to elevate privileges.

2. **Configure Multiple Hosts for NTP**: Write a playbook (ntp_config.yml) to sync time:
   ```
   - hosts: all
     tasks:
       - name: Install NTP
         yum:
           name: ntp
           state: latest
       - name: Start NTP service
         service:
           name: ntpd
           state: started
   ```
   Execute: `ansible-playbook ntp_config.yml -l ntp_hosts` to target specific groups.

## Graph Relationships
- Related to: terraform (for infrastructure as code), kubernetes (for container orchestration), jenkins (for CI/CD integration), all within the devops-sre cluster.
- Dependencies: Often pairs with vault for secret management.
- Conflicts: Avoid with tools like Puppet if agent-based management is preferred.
