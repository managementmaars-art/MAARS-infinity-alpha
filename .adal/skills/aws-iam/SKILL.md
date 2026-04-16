---
name: aws-iam
cluster: cloud-aws
description: "Manage AWS Identity and Access Management for controlling user access and permissions to secure cloud resources."
tags: ["aws","iam","security"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "aws iam identity access management policies users roles permissions audit"
---

# aws-iam

## AWS Agent Plugin Integration

This skill delegates all AWS provisioning and operations to the official AWS agent plugin.

```
/plugin marketplace add awslabs/agent-plugins
/plugin install deploy-on-aws@agent-plugins-for-aws
```

Use the `deploy-on-aws` plugin for all AWS provisioning actions.

This skill covers: architecture decisions, cost modeling, IaC patterns, and pre-flight requirements — the plugin handles execution.

## Architecture Guidance

Consult this skill for:
- Service selection and trade-off analysis
- Cost estimation and optimization strategy
- Pre-flight IAM permission requirements
- IaC approach (CDK vs CloudFormation vs Terraform)
- Integration patterns with other AWS services

## Reference

- [AWS Agent Plugins](https://github.com/awslabs/agent-plugins)
- [deploy-on-aws plugin](https://github.com/awslabs/agent-plugins/tree/main/plugins/deploy-on-aws)
- [AWS MCP Servers](https://github.com/awslabs/mcp)
