
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Developer tooling and IDE ecosystem
    ('neovim-lua-config', 'Neovim Lua config - init.lua, lazy.nvim, LSP, treesitter, telescope, lualine, keymaps'),
    ('emacs-advanced', 'Emacs advanced - elisp, org-mode, magit, evil-mode, use-package, doom, spacemacs'),
    ('vim-advanced', 'Vim advanced - vimscript, plugins, registers, macros, motions, splits, terminal mode'),
    ('jetbrains-ide', 'JetBrains IDE - IntelliJ, PyCharm, GoLand, WebStorm, plugins, live templates, refactoring'),
    ('eclipse-ide', 'Eclipse IDE - plugins, workspace, build tools, debugging, profiling, JDT, CDT'),
    ('xcode-advanced', 'Xcode advanced - build settings, schemes, instruments, simulators, signing, Swift packages'),
    ('android-studio-advanced', 'Android Studio advanced - profiler, layout inspector, database inspector, emulator, AGP'),
    ('rider-ide', 'JetBrains Rider - .NET debugging, Unity support, plugins, live templates, refactoring'),
    ('clion-advanced', 'CLion advanced - CMake, debugging, profiling, remote development, embedded, sanitizers'),
    ('code-server', 'Code-server - VS Code in browser, remote dev, Docker, authentication, extensions sync'),
    ('zed-editor', 'Zed editor - collaborative editing, LSP, tree-sitter, themes, keybindings, extensions'),
    ('helix-editor', 'Helix editor - modal editing, multi-cursor, LSP integration, tree-sitter, configuration'),
    ('lapce-editor', 'Lapce editor - WGPU rendering, remote dev, LSP, plugins, performance'),
    ('gitpod-advanced', 'Gitpod advanced - workspace configuration, .gitpod.yml, prebuilds, custom images'),
    ('github-codespaces-advanced', 'GitHub Codespaces advanced - devcontainer, secrets, performance, extensions'),
    ('replit-development', 'Replit development - Repl.it, multiplayer, nix modules, deployment, database, secrets'),
    ('codesandbox-advanced', 'CodeSandbox advanced - sandboxes, repositories, cloud dev environments, templates'),
    ('stackblitz-advanced', 'StackBlitz advanced - WebContainers, bolt.new, AI, browser-based Node.js, sharing'),
    ('devenv-nix', 'devenv.sh - Nix-based dev environments, modules, processes, services, testing, CI'),
    ('mise-dev-tools', 'mise dev tools - tool version management, tasks, config, plugins, shims, aliases'),
    # REPL and notebook tools
    ('jupyter-lab-advanced', 'JupyterLab advanced - extensions, kernels, widgets, collaboration, deployment'),
    ('observable-notebooks', 'Observable notebooks - reactive programming, JavaScript, plots, cells, imports, sharing'),
    ('polynote', 'Polynote - multi-language notebooks, Scala, Python, SQL, data visualization, dependency'),
    ('deepnote', 'Deepnote - collaborative notebooks, SQL, scheduling, version control, sharing, workspace'),
    ('databricks-notebooks', 'Databricks notebooks - PySpark, SQL, Delta Lake, widgets, clusters, MLflow integration'),
    ('hex-data-notebooks', 'Hex data notebooks - SQL, Python, charts, apps, sharing, scheduling, magic'),
    ('pluto-julia', 'Pluto.jl - reactive Julia notebooks, interactivity, reproducibility, packages'),
    ('iex-elixir', 'IEx Elixir REPL - pry, break points, helpers, introspection, configuration, remote shell'),
    ('ghci-haskell', 'GHCi Haskell REPL - type checking, modules, debugging, multiline, extensions, profiling'),
    ('sbt-scala-repl', 'Scala REPL/sbt console - expressions, imports, paste mode, history, spark-shell'),
    # Database administration advanced
    ('pg-admin-advanced', 'pgAdmin advanced - query tool, explain, ERD, monitoring, jobs, plugins, connection management'),
    ('dbeaver-advanced', 'DBeaver advanced - ER diagrams, data transfer, SQL editor, drivers, mockups, AI assist'),
    ('datagrip-advanced', 'DataGrip advanced - query console, schemas, VCS, data editor, introspection, attach DB'),
    ('nosql-workbench', 'NoSQL Workbench - DynamoDB design, data visualization, operations builder, aggregate view'),
    ('mongodb-compass', 'MongoDB Compass - schema analysis, aggregation pipeline, performance insights, indexes'),
    ('redis-insight', 'RedisInsight - memory analysis, profiler, slow log, cluster management, modules'),
    ('cassandra-tooling', 'Cassandra tooling - cqlsh, nodetool, TablePlus, repair strategies, compaction, monitoring'),
    ('database-version-control', 'Database version control - Flyway, Liquibase, Alembic, DbUp, migration strategies'),
    ('database-testing-advanced', 'Database testing advanced - test fixtures, pgTAP, utPLSQL, data mocking, assertions'),
    ('query-profiling', 'Query profiling - EXPLAIN ANALYZE, execution plans, pg_stat_statements, slow query log'),
    # Build systems and package management
    ('bazel-gazelle', 'Bazel Gazelle - Go rule generation, BUILD file management, repo rules, go_repository'),
    ('pants-build-advanced', 'Pants build advanced - targets, goals, backends, pants.toml, remote execution, coverage'),
    ('please-build', 'Please build system - BUILD files, subrepos, remote caching, plugins, Python/Go/Java'),
    ('meson-cross-compile', 'Meson cross-compilation - cross files, machine files, toolchain, introspection, wrapdb'),
    ('spack-hpc', 'Spack HPC package manager - specs, variants, modules, containers, mirrors, caches'),
    ('conda-forge', 'conda-forge - recipes, feedstocks, bots, CI, conda-build, rattler-build, micromamba'),
    ('pixi-package', 'pixi package manager - conda packages, tasks, environments, lock files, prefix'),
    ('nix-package-manager', 'Nix package manager - derivations, overlays, nixpkgs, nix-env, GC roots, cross-compile'),
    ('homebrew-formula', 'Homebrew formula development - DSL, testing, caveats, dependencies, bottles, CI'),
    ('vcpkg-advanced', 'vcpkg advanced - triplets, overlays, registry, versioning, CI integration, CMake integration'),
    ('conan-cpp', 'Conan C++ package manager - conanfile, recipes, generators, remotes, lockfiles, Artifactory'),
    # CI/CD deep specialization
    ('github-actions-reusable', 'GitHub Actions reusable workflows - inputs, outputs, secrets, matrix, composite'),
    ('gitlab-ci-dag', 'GitLab CI DAG - needs, rules, parallel, includes, services, artifacts, environments'),
    ('tekton-triggers', 'Tekton triggers - EventListeners, TriggerTemplates, TriggerBindings, interceptors, CEL'),
    ('spinnaker-pipelines', 'Spinnaker pipelines - stages, triggers, artifacts, canary analysis, notifications'),
    ('argo-cd-advanced', 'Argo CD advanced - ApplicationSets, sync waves, hooks, resource health, diff strategies'),
    ('flux-cd-advanced', 'Flux CD advanced - image automation, notifications, multi-tenancy, bootstrap, OCI'),
    ('jenkins-shared-libraries', 'Jenkins shared libraries - vars, src, resources, @Library, Groovy DSL, testing'),
    ('circleci-config', 'CircleCI config advanced - orbs, executors, workflows, context, parameters, pipelines'),
    ('teamcity-dsl', 'TeamCity DSL - Kotlin DSL, build configurations, VCS roots, connections, build chains'),
    ('drone-ci-starlark', 'Drone CI Starlark - .drone.star, scripts, conditional pipelines, secrets, volumes'),
]

for name, desc in skills:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f'''---
name: {name}
description: {desc}
---

# {title} - MAARS Reference

## Overview
{desc}

## Core Framework
Use structured approach: define goal, identify audience, create hypothesis, execute, measure.

## Key Prompts
- "For [project], implement {title.lower()} for [use case]. Requirements: [X]. Provide working code examples."
- "Analyze [existing implementation] and suggest 3 improvements prioritized by impact."
- "Write a {title.lower()} template for a [type] project with [specific requirements]."

## Best Practices
1. Read official documentation before implementation
2. Test in isolation before full integration
3. Handle errors and edge cases explicitly
4. Document configuration and requirements
5. Monitor and alert on key metrics

## Common Patterns
- Setup and initialization
- Core operations
- Error handling and retries
- Authentication and security
- Performance and scaling

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
