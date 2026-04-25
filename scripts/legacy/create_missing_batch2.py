import os

base = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'

skills = [
    # HashiCorp / Terraform
    ('terraform-style-guide', 'Terraform style guide - follow HashiCorp Terraform code style, formatting, naming conventions'),
    ('terraform-test', 'Terraform test - write and run Terraform tests, validate infrastructure configurations'),
    ('refactor-module', 'Refactor module - refactor Terraform modules for reusability, clarity, and best practices'),
    ('terraform-stacks', 'Terraform stacks - use Terraform Stacks for multi-environment infrastructure management'),
    ('provider-resources', 'Provider resources - build and manage Terraform provider resource implementations'),
    ('new-terraform-provider', 'New Terraform provider - create a new Terraform provider from scratch with CRUD operations'),
    ('provider-actions', 'Provider actions - implement provider-level actions in Terraform provider development'),
    ('run-acceptance-tests', 'Run acceptance tests - run Terraform provider acceptance tests in CI/CD pipelines'),
    ('azure-verified-modules', 'Azure verified modules - use and contribute to Microsoft Azure Verified Terraform Modules'),
    ('terraform-search-import', 'Terraform search import - search and import existing cloud resources into Terraform state'),
    ('aws-ami-builder', 'AWS AMI builder - build custom Amazon Machine Images with Packer and HashiCorp tools'),
    ('push-to-registry', 'Push to registry - publish Terraform modules and providers to HashiCorp registry'),
    ('azure-image-builder', 'Azure image builder - build custom Azure VM images using HashiCorp Packer'),
    ('windows-builder', 'Windows builder - build Windows-based VM images and artifacts with Packer'),
    ('provider-test-patterns', 'Provider test patterns - patterns for testing Terraform providers, unit and acceptance tests'),
    ('provider-docs', 'Provider docs - write and generate documentation for Terraform providers'),
    # LaunchDarkly
    ('launchdarkly-flag-cleanup', 'LaunchDarkly flag cleanup - identify and remove stale feature flags from codebase'),
    ('launchdarkly-flag-discovery', 'LaunchDarkly flag discovery - discover and audit all feature flags in a codebase'),
    ('launchdarkly-flag-create', 'LaunchDarkly flag create - create new feature flags in LaunchDarkly with proper configuration'),
    ('launchdarkly-flag-targeting', 'LaunchDarkly flag targeting - configure targeting rules and segments for feature flags'),
    ('aiconfig-tools', 'AI config tools - LaunchDarkly AI configuration tools for model parameters and prompts'),
    ('aiconfig-projects', 'AI config projects - manage AI configuration projects in LaunchDarkly platform'),
    ('aiconfig-create', 'AI config create - create AI model configurations in LaunchDarkly for prompt management'),
    ('aiconfig-update', 'AI config update - update and version AI configurations in LaunchDarkly'),
    ('aiconfig-variations', 'AI config variations - create and test variations of AI model configurations'),
    ('create-skill', 'Create skill - create new skills for AI agents following skill authoring best practices'),
    ('aiconfig-online-evals', 'AI config online evals - run online evaluations for AI configurations in LaunchDarkly'),
    ('aiconfig-targeting', 'AI config targeting - target specific users or segments with AI model configurations'),
    ('launchdarkly-metric-choose', 'LaunchDarkly metric choose - choose the right metrics for feature flag experiments'),
    ('launchdarkly-metric-instrument', 'LaunchDarkly metric instrument - instrument code to track experiment metrics'),
    ('launchdarkly-metric-create', 'LaunchDarkly metric create - create custom metrics for LaunchDarkly experiments'),
    ('skill-name', 'Skill name - naming conventions and best practices for AI agent skill naming'),
    # LiveKit
    ('livekit-agents', 'LiveKit agents - build real-time AI voice and video agents with LiveKit framework'),
    # Neon Database
    ('neon-postgres-egress-optimizer', 'Neon Postgres egress optimizer - optimize data transfer costs in Neon serverless Postgres'),
    ('plugin-manager', 'Plugin manager - manage plugins, extensions, and integrations in AI agent systems'),
    # Pulumi
    ('pulumi-arm-to-pulumi', 'Pulumi ARM to Pulumi - convert Azure ARM templates to Pulumi infrastructure code'),
    ('pulumi-best-practices', 'Pulumi best practices - follow Pulumi IaC best practices for structure and configuration'),
    ('pulumi-esc', 'Pulumi ESC - manage secrets and configuration with Pulumi Environments, Secrets, Config'),
    ('pulumi-component', 'Pulumi component - build reusable Pulumi component resources and packages'),
    ('pulumi-automation-api', 'Pulumi automation API - use Pulumi Automation API to embed infrastructure in applications'),
    ('pulumi-terraform-to-pulumi', 'Pulumi Terraform to Pulumi - migrate Terraform configurations to Pulumi'),
    ('pulumi-cdk-to-pulumi', 'Pulumi CDK to Pulumi - migrate AWS CDK code to Pulumi infrastructure as code'),
    ('cloudformation-to-pulumi', 'CloudFormation to Pulumi - convert AWS CloudFormation templates to Pulumi code'),
    ('package-usage', 'Package usage - analyze and optimize package usage in infrastructure and application code'),
    ('provider-upgrade', 'Provider upgrade - upgrade Terraform or Pulumi provider versions with breaking change handling'),
    ('pulumi-upgrade-provider', 'Pulumi upgrade provider - upgrade Pulumi provider SDKs and handle API changes'),
    ('upstream-patches', 'Upstream patches - manage and apply upstream patches to forked or vendored dependencies'),
    # Redis
    ('redis-development', 'Redis development - develop applications with Redis, data structures, pub/sub, streams'),
    ('redis-best-practices', 'Redis best practices - Redis configuration, data modeling, performance, security patterns'),
    # Streamlit
    ('developing-with-streamlit', 'Developing with Streamlit - build data apps and dashboards with Streamlit framework'),
    ('building-streamlit-chat-ui', 'Building Streamlit chat UI - create chat interfaces in Streamlit with st.chat_message'),
    ('using-streamlit-session-state', 'Using Streamlit session state - manage state between reruns with st.session_state'),
    ('creating-streamlit-themes', 'Creating Streamlit themes - customize Streamlit app appearance with themes and CSS'),
    ('organizing-streamlit-code', 'Organizing Streamlit code - structure Streamlit apps with pages, modules, and caching'),
    ('building-streamlit-custom-components-v2', 'Building Streamlit custom components v2 - create custom Streamlit components with new API'),
    ('optimizing-streamlit-performance', 'Optimizing Streamlit performance - cache data, use fragments, optimize rerenders'),
    ('building-streamlit-multipage-apps', 'Building Streamlit multipage apps - build multi-page Streamlit applications with navigation'),
    ('improving-streamlit-design', 'Improving Streamlit design - enhance Streamlit UI with layout, columns, containers'),
    ('using-streamlit-cli', 'Using Streamlit CLI - use Streamlit command line tools for development and deployment'),
    ('using-streamlit-markdown', 'Using Streamlit markdown - render rich markdown, LaTeX, code in Streamlit apps'),
    ('using-streamlit-layouts', 'Using Streamlit layouts - use columns, tabs, expanders, sidebars in Streamlit'),
    ('building-streamlit-dashboards', 'Building Streamlit dashboards - create interactive data dashboards with Streamlit'),
    ('setting-up-streamlit-environment', 'Setting up Streamlit environment - configure Streamlit project, secrets, config'),
    ('displaying-streamlit-data', 'Displaying Streamlit data - show dataframes, charts, tables, metrics in Streamlit'),
    ('using-streamlit-custom-components', 'Using Streamlit custom components - integrate third-party Streamlit components'),
    ('choosing-streamlit-selection-widgets', 'Choosing Streamlit selection widgets - use selectbox, radio, checkbox, multiselect'),
    # Supabase
    ('supabase', 'Supabase - build apps with Supabase backend, auth, database, storage, real-time'),
    # Vercel Labs
    ('vercel-cli-with-tokens', 'Vercel CLI with tokens - authenticate and use Vercel CLI with access tokens in CI/CD'),
    ('vercel-react-view-transitions', 'Vercel React view transitions - implement smooth page transitions with React View Transitions API'),
    # WordPress
    ('wordpress-router', 'WordPress router - build custom URL routing in WordPress themes and plugins'),
    ('wp-wpcli-and-ops', 'WP CLI and ops - manage WordPress with WP-CLI, automation, deployments, operations'),
    ('wpds', 'WPDS - WordPress Design System components for consistent UI in WordPress projects'),
    # Azure
    ('azure-cost', 'Azure cost - manage and analyze Azure costs, budgets, cost allocation, billing'),
]

created = 0
skipped = 0
for name, desc in skills:
    d = os.path.join(base, name)
    if os.path.exists(d):
        skipped += 1
        continue
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f"""---
name: {name}
description: {desc}
---

# {title}

## Overview
{desc}

## Usage
Use this skill to leverage {title.lower()} capabilities in your agent workflows.

## Key Capabilities
- Core {title.lower()} operations
- Integration with related tools and APIs
- Best practice patterns and examples

## Best Practices
1. Follow official documentation and guidelines
2. Handle errors and edge cases gracefully
3. Use environment variables for credentials
4. Test thoroughly before production use
5. Monitor and log for observability
"""
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)
    created += 1

print(f'Created: {created}')
print(f'Skipped: {skipped}')
