
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Hardware/Embedded/IoT deep
    ('embedded-c', 'Embedded C - bare metal, registers, ISR, DMA, watchdog, linker scripts, toolchain, JTAG'),
    ('rtos-programming', 'RTOS programming - FreeRTOS, Zephyr, ThreadX, tasks, queues, semaphores, priorities'),
    ('freertos-advanced', 'FreeRTOS advanced - memory management, co-routines, software timers, event groups, streams'),
    ('zephyr-rtos', 'Zephyr RTOS - device tree, Kconfig, shields, SMP, subsystems, Bluetooth, LTE, testing'),
    ('arduino-advanced', 'Arduino advanced - libraries, RTOS, ESP32/ESP8266, BLE, WiFi, OTA, power management'),
    ('esp32-development', 'ESP32 development - IDF, FreeRTOS, BLE, WiFi, deep sleep, partitions, NVS, OTA'),
    ('raspberry-pi-advanced', 'Raspberry Pi advanced - GPIO, I2C, SPI, UART, camera, multimedia, real-time, CM4'),
    ('stm32-development', 'STM32 development - HAL, LL, CubeMX, DMA, timers, ADC, RTOS integration, DFU'),
    ('pic-microcontroller', 'PIC microcontroller - MPLAB, XC compilers, peripherals, ICSP, bootloader, config bits'),
    ('avr-microcontroller', 'AVR microcontroller - ATmega, ATtiny, registers, fuses, bootloader, SPI, I2C, ADC'),
    ('arm-cortex-m', 'ARM Cortex-M - NVIC, SysTick, MPU, FPU, CMSIS, Thumb2, debugging, SWD, ETM'),
    ('fpga-programming', 'FPGA programming - Xilinx/Intel, synthesis, place & route, timing closure, DSP, IP cores'),
    ('verilog-hdl', 'Verilog HDL - modules, always blocks, testbenches, synthesis, simulation, VCD waveforms'),
    ('vhdl-programming', 'VHDL programming - entities, architectures, packages, testbenches, simulation, synthesis'),
    ('xilinx-vivado', 'Xilinx Vivado - IP integrator, HLS, SDK, PetaLinux, zynq, timing analysis, bitstream'),
    ('intel-quartus', 'Intel Quartus - design entry, synthesis, fitter, timing analyzer, SignalTap, NIOS II'),
    ('lattice-fpga', 'Lattice FPGA - iCE40, ECP5, Radiant, Diamond, icestorm, open-source flow, low power'),
    ('pcb-design', 'PCB design - KiCad, Altium, Eagle, schematics, layout, DRC, Gerber, impedance, EMC'),
    ('signal-integrity', 'Signal integrity - transmission lines, impedance, termination, eye diagrams, jitter, EMI'),
    ('power-electronics', 'Power electronics - switching converters, MOSFET, gate drivers, protection, PCB layout'),
    ('sensor-integration', 'Sensor integration - IMU, barometer, GPS, lidar, radar, cameras, fusion, calibration'),
    ('ble-development', 'BLE development - GATT, profiles, services, advertising, bonding, Nordic nRF, iOS/Android'),
    ('zigbee-protocol', 'Zigbee protocol - ZHA, mesh networking, coordinator, router, end device, ZCL, pairing'),
    ('zwave-protocol', 'Z-Wave protocol - mesh, inclusion, S2 security, cc, devices, controller, SDK'),
    ('lora-lorawan', 'LoRa/LoRaWAN - SF, BW, sensitivity, network server, TTN, gateways, OTAA, ABP, classes'),
    ('nb-iot-catm1', 'NB-IoT/LTE-M - AT commands, PSM, eDRX, SARA, power optimization, provisioning'),
    ('matter-protocol', 'Matter protocol - commissioning, fabrics, clusters, bridge, Thread, WiFi, BLE, SDK'),
    ('thread-protocol', 'Thread protocol - mesh, IPv6, OpenThread, border router, commissioning, otbr, CoAP'),
    ('can-bus', 'CAN bus - frames, arbitration, error handling, CANopen, J1939, SocketCAN, analysis'),
    ('modbus-protocol', 'Modbus - RTU, TCP, registers, coils, function codes, master/slave, Pymodbus, testing'),
    ('dnp3-protocol', 'DNP3 protocol - data objects, application layer, transport, data link, SAv5, IEC 61968'),
    ('profinet-industrial', 'PROFINET - IO controller, IO device, IRT, RT, MRP, DCP, engineering, Wireshark'),
    ('ethercat', 'EtherCAT - master, slave, PDO, SDO, CoE, EoE, distributed clocks, TwinCAT'),
    ('plc-programming', 'PLC programming - IEC 61131-3, ladder, FBD, SFC, ST, IL, Siemens, Allen-Bradley'),
    ('scada-systems', 'SCADA systems - HMI, historians, OPC-UA, alarms, trending, redundancy, security'),
    ('opcua-protocol', 'OPC UA - server, client, nodes, browse, read, write, subscriptions, security, SDK'),
    ('ros-navigation', 'ROS navigation - Nav2, costmaps, planners, recovery, AMCL, map server, move_base'),
    ('computer-vision-embedded', 'Embedded CV - OpenCV on ARM, YOLO edge, NCNN, TFLite, model optimization'),
    ('tflite-edge', 'TensorFlow Lite edge - quantization, delegation, microcontrollers, edge TPU, profiling'),
    ('onnxruntime-edge', 'ONNX Runtime edge - providers, mobile, quantization, custom ops, optimization'),
    # Scientific & Research Computing
    ('computational-fluid-dynamics', 'CFD - NavierStokes, turbulence models, meshing, solvers, OpenFOAM, Fluent, post-processing'),
    ('finite-element-analysis', 'FEA - mesh generation, element types, boundary conditions, solvers, post-processing'),
    ('molecular-modeling', 'Molecular modeling - docking, dynamics, quantum, AMBER, CHARMM, GROMACS, NAMD'),
    ('quantum-chemistry', 'Quantum chemistry - DFT, HF, post-HF, basis sets, Gaussian, ORCA, Psi4, NWChem'),
    ('condensed-matter', 'Condensed matter physics - band structure, phonons, DFT, VASP, Quantum ESPRESSO, tight-binding'),
    ('plasma-physics', 'Plasma physics - MHD, PIC, fluid models, turbulence, confinement, codes, diagnostics'),
    ('particle-physics', 'Particle physics - ROOT, Geant4, PYTHIA, analysis, histograms, fitting, statistics'),
    ('nuclear-physics-sim', 'Nuclear physics simulation - MCNP, GEANT4, OpenMC, neutron transport, activation'),
    ('astrophysics-simulation', 'Astrophysics simulation - N-body, SPH, AMR, GADGET, FLASH, Arepo, visualization'),
    ('climate-simulation', 'Climate simulation - GCMs, WRF, CESM, NEMO, ocean models, coupling, parameterization'),
    ('biophysics', 'Biophysics - force fields, membrane simulation, protein folding, imaging analysis, AFM'),
    ('cheminformatics', 'Cheminformatics - SMILES, InChI, fingerprints, docking, SAR, QSAR, pharmacophore'),
    ('genomics-pipeline', 'Genomics pipeline - FASTQ, alignment, variant calling, annotation, GATK, BWA, STAR'),
    ('proteomics', 'Proteomics - mass spectrometry, MaxQuant, Perseus, Mascot, spectral libraries, PTMs'),
    ('metabolomics', 'Metabolomics - LC-MS, NMR, data processing, pathway analysis, XCMS, MetaboAnalyst'),
    ('structural-biology', 'Structural biology - X-ray crystallography, cryo-EM, NMR, RELION, Phenix, CCP4'),
    ('systems-biology', 'Systems biology - network models, ODE, stochastic, SBML, COPASI, whole-cell models'),
    ('neuroscience-data', 'Neuroscience data analysis - spike sorting, LFP, fMRI, EEG, NWB, MNE, BrainPy'),
    ('epidemiology-modeling', 'Epidemiology modeling - SIR/SEIR, agent-based, network, R0, interventions, fitting'),
    ('econophysics', 'Econophysics - agent-based, network effects, power laws, fat tails, market dynamics'),
    # Data science specializations
    ('causal-inference-advanced', 'Causal inference advanced - DAGs, backdoor criterion, IV, RDD, DID, synthetic control'),
    ('bayesian-ml', 'Bayesian ML - probabilistic models, MCMC, variational inference, GP, Stan, NumPyro'),
    ('spatial-statistics', 'Spatial statistics - geostatistics, kriging, spatial autocorrelation, GIS, point processes'),
    ('network-science', 'Network science - random graphs, scale-free, community, spreading, percolation, embeddings'),
    ('information-theory', 'Information theory - entropy, mutual info, KL divergence, channel capacity, MDL, coding'),
    ('survival-analysis-advanced', 'Survival analysis advanced - competing risks, multi-state, frailty, parametric, dynamic'),
    ('panel-data', 'Panel data econometrics - fixed effects, random effects, GMM, dynamic panels, selection'),
    ('quantile-regression', 'Quantile regression - conditional quantiles, QR forests, censored, instrumental, distribution'),
    ('robust-statistics', 'Robust statistics - breakdown point, influence function, M-estimators, outliers, trimming'),
    ('functional-data-analysis', 'Functional data analysis - smoothing, registration, FPCA, regression, classification'),
    # Mathematics deep
    ('linear-algebra-applied', 'Applied linear algebra - SVD, eigendecomposition, least squares, iterative solvers, sparse'),
    ('optimization-methods', 'Optimization methods - gradient descent, Newton, quasi-Newton, constrained, global, stochastic'),
    ('differential-equations', 'Differential equations - ODE solvers, PDE discretization, stability, stiffness, boundary'),
    ('numerical-analysis', 'Numerical analysis - interpolation, integration, differentiation, root finding, error analysis'),
    ('topology-applied', 'Applied topology - TDA, persistent homology, Betti numbers, simplicial complexes, mapper'),
    ('graph-theory-applied', 'Graph theory applied - algorithms, spectral, random walks, cuts, matching, coloring'),
    ('number-theory-applied', 'Number theory applied - cryptographic protocols, primality, factoring, elliptic curves'),
    ('abstract-algebra', 'Abstract algebra - groups, rings, fields, Galois theory, representation, coding theory'),
    ('probability-theory', 'Probability theory - measure theory, martingales, CLT, LLN, conditional expectation'),
    ('stochastic-processes', 'Stochastic processes - Markov chains, Brownian motion, Ito calculus, filtering, control'),
    # Design & Creative Tools
    ('figma-advanced', 'Figma advanced - variants, interactive components, auto layout, variables, dev mode, plugins'),
    ('sketch-design', 'Sketch - symbols, libraries, nested symbols, text styles, prototyping, plugins, Zeplin'),
    ('adobe-xd', 'Adobe XD - components, repeat grid, voice prototyping, co-editing, design specs, plugins'),
    ('adobe-illustrator', 'Adobe Illustrator - vectors, paths, appearance, effects, typography, symbols, scripting'),
    ('adobe-photoshop', 'Adobe Photoshop - layers, masks, adjustments, filters, scripts, actions, generative fill'),
    ('adobe-after-effects', 'Adobe After Effects - keyframes, expressions, effects, 3D, scripting, plugins, render'),
    ('adobe-premiere', 'Adobe Premiere - sequences, effects, transitions, multicam, color, export, scripting'),
    ('davinci-resolve', 'DaVinci Resolve - editing, color, Fusion, Fairlight, collaboration, scripting, API'),
    ('blender-advanced', 'Blender advanced - geometry nodes, shader graphs, physics, rigging, scripting, rendering'),
    ('cinema-4d', 'Cinema 4D - modeling, animation, MoGraph, rendering, Redshift, scripting, CAD import'),
    ('maya-3d', 'Maya 3D - modeling, rigging, animation, dynamics, rendering, MEL/Python scripting'),
    ('houdini-vfx', 'Houdini VFX - procedural, VOPs, DOPs, SOPs, CHOPs, VEX, rendering, game toolset'),
    ('substance-painter', 'Substance Painter - PBR texturing, generators, smart masks, anchor points, baking, export'),
    ('midjourney-advanced', 'Midjourney advanced - prompting, parameters, inpainting, seeds, style references, chaos'),
    ('stable-diffusion-advanced', 'Stable Diffusion advanced - ControlNet, LoRA, SDXL, ComfyUI, img2img, inpainting'),
    ('comfyui-advanced', 'ComfyUI advanced - workflows, custom nodes, API, batch processing, upscaling, video'),
    ('runway-advanced', 'Runway Gen-2/3 - video generation, image editing, motion brush, Director Mode'),
    ('kling-video', 'Kling AI video - text-to-video, image-to-video, camera control, extend, effects'),
    ('canva-design', 'Canva - brand kit, templates, AI features, apps, collaboration, animation, resize'),
    ('webflow-design', 'Webflow - CMS, interactions, symbols, responsive, ecommerce, hosting, code export'),
    ('framer-advanced', 'Framer - components, breakpoints, CMS, Code override, variables, interactions, publish'),
    ('spline-design', 'Spline 3D - modeling, physics, interactions, events, React integration, export'),
    # Marketing tools
    ('google-ads-advanced', 'Google Ads advanced - Performance Max, smart bidding, audience, attribution, scripts'),
    ('meta-ads-advanced', 'Meta Ads advanced - Advantage+, catalog, pixels, CAPI, attribution, creative testing'),
    ('linkedin-ads', 'LinkedIn Ads - sponsored content, InMail, conversation, lead gen, audience, attribution'),
    ('programmatic-advertising', 'Programmatic advertising - DSPs, SSPs, DMPs, bid strategies, PMPs, audiences'),
    ('affiliate-marketing', 'Affiliate marketing - program setup, tracking, payments, compliance, fraud, networks'),
    ('influencer-strategy', 'Influencer strategy - discovery, vetting, contracts, briefs, tracking, ROI, FTC'),
    ('crm-advanced', 'CRM advanced - lead scoring, workflow automation, custom objects, API, reporting, hygiene'),
    ('marketing-automation', 'Marketing automation - nurture, scoring, attribution, integrations, ABM, reporting'),
    ('hubspot-advanced', 'HubSpot advanced - workflows, custom properties, reporting, sequences, API, integrations'),
    ('salesforce-marketing', 'Salesforce Marketing Cloud - journeys, personalization, AMP, API, analytics, Einstein'),
    ('marketo-advanced', 'Marketo advanced - smart campaigns, revenue cycle, ABM, API, tokens, webhooks'),
    ('pardot-advanced', 'Pardot/MCAE advanced - engagement studio, scoring, grading, dynamic content, Salesforce sync'),
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
