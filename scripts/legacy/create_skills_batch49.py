
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Scientific and research computing
    ('hpc-mpi-advanced', 'HPC MPI advanced - MPI-3 RMA, topology awareness, collective tuning, hybrid OpenMP/MPI'),
    ('cuda-optimization-advanced', 'CUDA optimization advanced - warp divergence, memory coalescing, occupancy, nsight'),
    ('openmp-simd', 'OpenMP SIMD - vectorization directives, reduction, SIMD clauses, target offload, GPU OpenMP'),
    ('rocm-amd-gpu', 'ROCm AMD GPU - HIP programming, hipBLAS, hipFFT, MIOpen, RCCL, Triton on AMD'),
    ('oneapi-intel', 'Intel oneAPI - DPC++, SYCL, MKL, oneDNN, vtune profiler, advisor, inspector'),
    ('petsc-scientific', 'PETSc scientific computing - parallel vectors, matrices, KSP solvers, TS, SNES, DM'),
    ('trilinos-framework', 'Trilinos framework - Epetra, Tpetra, AztecOO, ML, Ifpack, Zoltan, Kokkos'),
    ('dealii-fem', 'deal.II FEM - triangulations, DoFHandler, FEValues, linear algebra, adaptivity, MPI'),
    ('openfoam-advanced', 'OpenFOAM advanced - custom boundary conditions, fvOptions, thermophysical models, paraView'),
    ('nek5000-spectral', 'Nek5000 spectral element - mesh generation, boundary conditions, solver configuration, post'),
    ('lammps-advanced', 'LAMMPS advanced - force fields, fix commands, compute commands, GPU acceleration, PLUMED'),
    ('gromacs-advanced', 'GROMACS advanced - force field parametrization, umbrella sampling, metadynamics, GPU'),
    ('amber-md', 'AMBER MD - force fields, GAFF, pmemd, cpptraj, parmed, restraints, enhanced sampling'),
    ('charmm-md', 'CHARMM MD - topology, parameter files, NAMD, VMD integration, QM/MM, enhanced sampling'),
    ('quantum-espresso', 'Quantum ESPRESSO - DFT, pseudopotentials, plane waves, phonons, DFPT, EPW, pw2wannier'),
    ('vasp-advanced', 'VASP advanced - PAW, hybrid functionals, van der Waals, AIMD, NEB, BSE, GW'),
    ('ase-materials-advanced', 'ASE materials advanced - calculators, structure generation, NEB, GPAW, optimization'),
    ('pyiron-materials', 'pyiron materials - workflow management, atomistic simulations, HPC integration, databases'),
    ('siesta-dft', 'SIESTA DFT - NAO basis sets, pseudopotentials, order-N, transport, TDDFT, Wannier'),
    ('cp2k-advanced', 'CP2K advanced - GPW/GAPW, QM/MM, Gaussian basis sets, linear scaling, AIMD, TDDFT'),
    # Specialized web technologies
    ('htmx-hyperscript', 'HTMX + Hyperscript - hypermedia-driven apps, client-side scripting, Alpine.js patterns'),
    ('turbo-hotwire-advanced', 'Turbo/Hotwire advanced - Turbo Streams, Turbo Frames, Stimulus controllers, Strada'),
    ('livewire-advanced', 'Livewire advanced - Alpine.js integration, file uploads, real-time, lazy loading, SPA'),
    ('inertia-advanced', 'Inertia.js advanced - shared data, partial reloads, scroll restoration, SSR, typed'),
    ('astro-islands', 'Astro Islands advanced - island architecture, partial hydration, view transitions, content'),
    ('qwik-city', 'Qwik City - file-based routing, layouts, middleware, loader, action, cache, speculativeModule'),
    ('analog-angular', 'Analog Angular meta-framework - file-based routing, API routes, SSR, Nitro, Vite'),
    ('nuxt3-advanced', 'Nuxt 3 advanced - Nitro server engine, auto-imports, modules, layers, content, image'),
    ('solidstart-advanced', 'SolidStart advanced - file-based routing, server functions, streaming, middleware'),
    ('sveltekit-advanced', 'SvelteKit advanced - load functions, form actions, hooks, streaming, SPA mode, adapters'),
    ('remix-advanced-patterns', 'Remix advanced patterns - nested routing, loaders, actions, defer, error boundaries'),
    ('next-app-router-advanced', 'Next.js App Router advanced - RSC, server actions, caching, PPR, use cache'),
    ('tanstack-router-advanced', 'TanStack Router advanced - file-based routes, loaders, search params, deferred'),
    ('react-router-v7', 'React Router v7 - framework mode, loaders, actions, code splitting, form handling'),
    ('expo-router-advanced', 'Expo Router advanced - file-based routing, deep linking, web support, URL params'),
    ('capacitor-advanced', 'Capacitor advanced - native plugins, iOS/Android setup, updates, AppFlow integration'),
    ('nativescript-advanced', 'NativeScript advanced - native UI, Angular/Vue/React integration, plugin development'),
    ('tauri-v2-advanced', 'Tauri v2 advanced - IPC, plugins, mobile support, updater, app bundling, security'),
    ('wails-go', 'Wails Go - Go desktop apps, JavaScript frontend, bindings, assets, packaging, cross-platform'),
    ('neutralino-advanced', 'NeutralinoJS advanced - lightweight desktop, extensions, cloud, browser mode, events'),
    # Creative and design technology
    ('figma-plugin-development', 'Figma plugin development - Plugin API, widget API, UI, network requests, storage'),
    ('sketch-plugin-development', 'Sketch plugin development - JavaScript API, UI, commands, panels, data suppliers'),
    ('adobe-indesign-scripting', 'Adobe InDesign scripting - ExtendScript, IDML, DOM API, data merge, batch processing'),
    ('affinity-publisher', 'Affinity Publisher - master pages, styles, data merge, book publishing, PDF export'),
    ('inkscape-scripting', 'Inkscape scripting - Python extensions, SVG manipulation, CLI, batch processing'),
    ('blender-python-api', 'Blender Python API - bpy, operators, panels, add-on development, geometry nodes'),
    ('houdini-python', 'Houdini Python - hou module, digital assets, expressions, pipeline automation, VOPS'),
    ('maya-python-api', 'Maya Python API - cmds, API2, MPxCommand, DAG, animation curves, rendering'),
    ('nuke-python-api', 'Nuke Python API - nodes, callbacks, gizmos, panels, custom toolbar, pipeline integration'),
    ('resolve-davinci-scripting', 'DaVinci Resolve scripting - Lua, Python API, timeline, color grading, Fusion'),
    ('after-effects-scripting', 'After Effects scripting - ExtendScript, expressions, render queue, templates, render'),
    ('premiere-pro-scripting', 'Premiere Pro scripting - ExtendScript API, panels, markers, sequences, encoding'),
    ('logic-pro-scripting', 'Logic Pro scripting - MIDI scripting, Environment, Playback regions, Max for Live'),
    ('ableton-max4live', 'Ableton Max for Live - Max objects, LFO, M4L devices, API, MIDI effects, instruments'),
    ('unreal-python-api', 'Unreal Python API - unreal module, blueprints automation, asset management, sequencer'),
    ('unity-editor-scripting', 'Unity Editor scripting - Editor classes, Custom Inspectors, EditorWindow, Gizmos'),
    ('godot-gdextension', 'Godot GDExtension - C++ bindings, godot-cpp, native libraries, performance'),
    ('openscad-parametric', 'OpenSCAD parametric design - modules, functions, CSG operations, libraries, 3D printing'),
    ('freecad-python', 'FreeCAD Python API - Part workbench, App objects, Gui commands, macro automation'),
    ('kicad-scripting', 'KiCad scripting - Python console, scripting hub, board automation, footprint generation'),
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
'''.replace('{Title}', title)
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
