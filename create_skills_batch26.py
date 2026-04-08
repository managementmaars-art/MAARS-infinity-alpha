
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # ML/AI Libraries deep coverage
    ('spacy-nlp', 'spaCy NLP - pipelines, custom components, training, tok2vec, transformers, displacy, Cython'),
    ('nltk-advanced', 'NLTK advanced - corpora, tokenization, parsing, semantics, classification, chunking'),
    ('gensim-advanced', 'Gensim - word2vec, doc2vec, LDA, LSI, fastText, coherence, corpora, similarities'),
    ('opencv-advanced', 'OpenCV advanced - feature detection, optical flow, stereo vision, DNN, CUDA, calibration'),
    ('scikit-image', 'scikit-image - filters, morphology, segmentation, registration, features, drawing, IO'),
    ('albumentations', 'Albumentations - image augmentation, transforms, replay, bounding boxes, keypoints, A.Compose'),
    ('detectron2', 'Detectron2 - object detection, instance segmentation, panoptic, custom training, inference'),
    ('mmdetection', 'MMDetection - detection models, config system, custom datasets, hooks, evaluation, export'),
    ('yolo-advanced', 'YOLO advanced - YOLOv8/v9/v10, training, validation, export, tracking, segmentation'),
    ('detr-models', 'DETR models - detection transformer, object queries, Hungarian matching, deformable attention'),
    ('sam-segment', 'Segment Anything Model - prompts, automatic segmentation, masks, embeddings, SAM2'),
    ('whisper-advanced', 'Whisper advanced - transcription, translation, fine-tuning, timestamps, speaker diarization'),
    ('speechbrain', 'SpeechBrain - ASR, TTS, speaker recognition, emotion, separation, language ID, training'),
    ('espnet', 'ESPnet - end-to-end speech, transformer, conformer, streaming, multi-speaker, translation'),
    ('controlnet', 'ControlNet - conditioning, edge detection, depth, pose, canny, T2I adapter, training'),
    ('dreambooth', 'DreamBooth - fine-tuning diffusion models, text-image alignment, prior preservation, LoRA'),
    ('clip-advanced', 'CLIP advanced - zero-shot, embeddings, fine-tuning, LAION, contrastive learning, ALIGN'),
    ('blip-models', 'BLIP/BLIP-2 - image captioning, VQA, retrieval, Q-Former, bootstrapping, InstructBLIP'),
    ('flamingo-vlm', 'Flamingo/Open Flamingo - few-shot VLM, cross-attention, interleaved data, Perceiver'),
    ('llava-advanced', 'LLaVA advanced - multimodal instruction tuning, visual encoder, SFT, LLaVA-Next'),
    ('cogvlm', 'CogVLM/CogAgent - visual expert, deep fusion, agent tasks, GUI understanding'),
    ('prophet-forecasting', 'Prophet forecasting - trend, seasonality, holidays, regressors, uncertainty, diagnostics'),
    ('neuralprophet', 'NeuralProphet - neural forecasting, auto-regression, lagged regressors, configurable training'),
    ('darts-ts', 'Darts time series - models, ensembling, backtesting, covariates, probabilistic, transformers'),
    ('kats-facebook', 'Kats time series - detection, forecasting, models, changepoints, multivariate, simulations'),
    ('pyod-anomaly', 'PyOD anomaly detection - ABOD, CBLOF, COF, COPOD, HBOS, IForest, LODA, LOF, MCD'),
    ('alibi-detect', 'Alibi Detect - drift detection, outlier detection, adversarial, online, tabular, text'),
    ('river-online', 'River online ML - streaming algorithms, concept drift, classification, regression, clustering'),
    ('vowpal-wabbit', 'Vowpal Wabbit - online learning, reductions, contextual bandits, feature hashing, CB'),
    ('h2o-automl', 'H2O AutoML - automatic ML, stacking, leaderboard, distributed, POJO, MOJO export'),
    ('tpot-automl', 'TPOT - evolutionary AutoML, genetic programming, pipelines, custom operators, deployment'),
    ('auto-sklearn', 'Auto-sklearn - AutoML, meta-learning, ensemble construction, warm-starting, search spaces'),
    ('optuna-ml', 'Optuna ML - hyperparameter search, pruning, integration, distributed, visualization, CLI'),
    ('ray-tune', 'Ray Tune - hyperparameter tuning, schedulers, search algorithms, ASHA, PBT, callbacks'),
    ('surprise-recsys', 'Surprise recommender - collaborative filtering, SVD, NMF, KNN, cross-validation, dump'),
    ('lightfm-recsys', 'LightFM - hybrid recommender, WARP, BPR, logistic, user/item features, evaluation'),
    ('implicit-recsys', 'Implicit - ALS, BPR, LMF, GPU support, approximate nearest neighbors, evaluation'),
    ('lenskit', 'LensKit - recommendation algorithms, evaluation framework, batch experiments, pipelines'),
    ('cornac-recsys', 'Cornac recommender - BPR, PMF, CDL, CVAE, MCF, early fusion, multi-modality'),
    # NLP specialized
    ('transformers-nlp', 'Transformers NLP - BERT, GPT, T5, RoBERTa, DistilBERT, XLNet, pipelines, tokenizers'),
    ('sentence-transformers-advanced', 'Sentence Transformers - semantic search, clustering, paraphrase, bi-encoder, cross-encoder'),
    ('flair-nlp', 'Flair NLP - sequence labeling, NER, embeddings, string-based, stacking, training'),
    ('stanza-nlp', 'Stanza NLP - multilingual, NER, parsing, coreference, lemmatization, CoNLL format'),
    ('spacy-transformers', 'spaCy Transformers - BERT integration, tok2vec, training configs, component integration'),
    ('allennlp', 'AllenNLP - NLP research, models, interpretability, pretrained, training loops, predictors'),
    ('fairseq', 'Fairseq - sequence modeling, translation, language models, custom training, scaling'),
    ('nemo-nlp', 'NVIDIA NeMo NLP - ASR, NLP, TTS, models, training, fine-tuning, export, Triton'),
    ('torchtext', 'TorchText - datasets, tokenizers, vocab, transforms, legacy API, multi30k, IWSLT'),
    ('textacy', 'textacy - text preprocessing, information extraction, topic modeling, Doc manipulation'),
    ('textblob', 'TextBlob - sentiment, POS tagging, noun phrases, translation, correction, classifiers'),
    ('pattern-nlp', 'Pattern NLP - web mining, crawler, parser, sentiment, n-grams, vector space model'),
    ('polyglot-nlp', 'Polyglot NLP - transliteration, sentiment, NER, morphological analysis, multilingual'),
    # Deep learning advanced
    ('pytorch-advanced', 'PyTorch advanced - custom autograd, JIT, TorchScript, distributed, quantization, profiler'),
    ('tensorflow-advanced', 'TensorFlow advanced - custom layers, SavedModel, TF.data, XLA, mixed precision, serving'),
    ('keras-advanced', 'Keras advanced - custom training, custom layers, callbacks, mixed precision, multi-GPU'),
    ('paddle-paddle', 'PaddlePaddle - dynamic graph, fleet distributed, PaddleNLP, PaddleCV, export, serving'),
    ('mxnet-framework', 'Apache MXNet - ndarray, symbol, gluon, KVStore, distributed, ONNX export, inference'),
    ('caffe-deep', 'Caffe/Caffe2 - prototxt, solver, layers, blob, blobs in memory, custom layers'),
    ('chainer', 'Chainer - define-by-run, links, chains, optimizers, datasets, reporters, training loop'),
    ('cntk-microsoft', 'Microsoft CNTK - network definitions, training, learners, readers, distributed, ONNX'),
    ('mindspore', 'MindSpore - dynamic/static graph, Cell, Tensor, Parameter, distributed, auto-parallel'),
    ('oneflow', 'OneFlow - SBP parallelism, boxing, global tensor, pipeline, ZeRO, compiler'),
    # Reinforcement learning
    ('stable-baselines3-advanced', 'Stable-Baselines3 advanced - custom policies, environments, callbacks, hyperparams'),
    ('rllib-advanced', 'RLlib advanced - algorithms, trainers, policies, replay buffers, multi-agent, curriculum'),
    ('gym-environments', 'OpenAI Gym/Gymnasium - custom envs, wrappers, spaces, rendering, vectorized, benchmarks'),
    ('pettingzoo', 'PettingZoo - multi-agent environments, AEC, parallel, wrappers, MARL, butterflies'),
    ('tianshou', 'Tianshou - policy, collector, trainer, batch, network, vectorized env, logging'),
    ('sample-factory', 'Sample Factory - high-throughput RL, async, GPU actors, policy lag, population'),
    ('cleanrl', 'CleanRL - single-file RL implementations, WandB integration, benchmarks, reproducibility'),
    ('dopamine', 'Google Dopamine - research framework, agents, Rainbow, DQN, IQN, gin config'),
    ('acme-deepmind', 'DeepMind Acme - distributed RL, actors, learners, replay, datasets, JAX agents'),
    ('mujoco-physics', 'MuJoCo physics - XML model, simulation, contacts, tendons, actuators, Python bindings'),
    # Computer vision advanced
    ('mmpose', 'MMPose - human pose estimation, top-down, bottom-up, wholebody, animal, training'),
    ('mmocr', 'MMOCR - text detection, recognition, KIE, inference, datasets, training, deployment'),
    ('open3d-advanced', 'Open3D advanced - point cloud processing, mesh, SLAM, registration, visualization'),
    ('kornia', 'Kornia - differentiable CV, geometry, augmentation, filters, color, morphology, losses'),
    ('timm-models', 'timm models - image models, pretrained, fine-tuning, features, data augmentation, training'),
    ('torchvision-advanced', 'torchvision advanced - transforms, datasets, models, detection, segmentation, keypoints'),
    ('mmclassification', 'MMClassification - image classification, pretrained zoo, config, training, evaluation'),
    ('pytorchvideo', 'PyTorchVideo - video understanding, transforms, data, models, SlowFast, X3D'),
    # Audio/Speech
    ('torchaudio', 'torchaudio - transforms, datasets, I/O, models, pipelines, CTC decode, augmentation'),
    ('librosa-advanced', 'librosa advanced - spectrograms, beat tracking, pitch, decomposition, feature extraction'),
    ('pyaudio', 'PyAudio - real-time audio I/O, PortAudio, streaming, callbacks, format conversion'),
    ('soundfile', 'SoundFile - audio file I/O, formats, metadata, seek, subtype, virtual IO'),
    ('audiomentations', 'audiomentations - audio augmentation, time stretch, pitch shift, noise, room simulation'),
    # Bioinformatics specialized
    ('biopython-advanced', 'Biopython advanced - SeqIO, AlignIO, Entrez, Blast, PDB, phylogenetics, restriction'),
    ('pysam-advanced', 'pySAM advanced - SAM/BAM/CRAM, pileup, fetch, alignment, sorting, indexing, statistics'),
    ('pyranges', 'PyRanges - genomic intervals, strand-aware, join, coverage, nearest, tile, DataFrame'),
    ('anndata-advanced', 'AnnData advanced - backed mode, views, sparse, chunked IO, zarr, compound obs'),
    ('squidpy', 'Squidpy - spatial transcriptomics, neighbors, statistics, visualization, ImageContainer, Zarr'),
    ('celltypist', 'CellTypist - cell type classification, majority voting, over-clustering, training, prediction'),
    ('velocyto', 'velocyto - RNA velocity, spliced/unspliced, dynamical model, vector fields, loom'),
    ('cellrank', 'CellRank - fate mapping, kernel, estimator, terminal states, absorption probabilities'),
    # Chemistry/Drug discovery
    ('rdkit-advanced', 'RDKit advanced - Morgan fingerprints, SMARTS, reactions, conformers, 3D, descriptors'),
    ('deepchem-advanced', 'DeepChem advanced - MoleculeNet, graph convolution, weave, MPNN, protein models'),
    ('openmm', 'OpenMM - molecular simulation, force fields, integrators, reporters, custom forces, GPU'),
    ('mdanalysis', 'MDAnalysis - trajectory analysis, atoms, residues, coordinates, distances, RMSD, PCA'),
    ('pymol-scripting', 'PyMOL scripting - selections, commands, API, movies, ray tracing, plugins, sessions'),
    ('schrodinger-api', 'Schrödinger API - Maestro, Glide docking, Prime, FEP+, KNIME, workflow scripting'),
    # Math/Physics simulation
    ('fenics', 'FEniCS - finite element, variational forms, meshes, solvers, adjoint, PDE-constrained'),
    ('dedalus-pde', 'Dedalus - spectral PDE solver, parallelism, eigenvalue, initial value, boundary conditions'),
    ('firedrake', 'Firedrake - FEM, automated adjoints, mesh hierarchy, multigrid, complex fields'),
    ('dolfinx', 'DOLFINx - FEniCSx, mixed elements, petsc4py, parallel, DG, nonlinear, eigenproblems'),
    ('ngsolve', 'NGSolve - FEM toolkit, netgen mesh, high order, DG, HDG, parallel, Python interface'),
    ('meep-fdtd', 'Meep FDTD - photonics simulation, sources, monitors, PML, Bloch-periodic, adjoint'),
    ('elmer-fem', 'Elmer FEM - multiphysics, solvers, mesh, SIF file, parallel, electrostatics, heat'),
    ('calculix', 'CalculiX - FEA, non-linear, static, dynamic, thermal, contact, Python scripting'),
    # Data visualization advanced
    ('bokeh-advanced', 'Bokeh advanced - server, widgets, streaming, custom JavaScript callbacks, layouts'),
    ('altair-vega', 'Altair/Vega-Lite - declarative visualization, selections, transforms, layers, facets'),
    ('plotly-advanced', 'Plotly advanced - subplots, 3D, animations, WebGL, custom templates, streaming'),
    ('dash-advanced', 'Dash advanced - callbacks, clientside, state, long callbacks, auth, deployment, enterprise'),
    ('panel-advanced', 'Panel advanced - reactive, servable, deployment, templates, extensions, async'),
    ('holoviews', 'HoloViews - high-level plotting, dimensions, operations, streams, dynamic maps, GeoViews'),
    ('hvplot', 'hvPlot - high-level plotting API, pandas/xarray/dask, interactive, Explorer, subplots'),
    ('d3-advanced', 'D3.js advanced - force simulation, geo projections, hierarchies, voronoi, custom layouts'),
    ('observable-plot-advanced', 'Observable Plot advanced - marks, transforms, scales, projections, interactions'),
    ('vega-advanced', 'Vega-Lite advanced - custom encodings, selections, signals, predicates, concatting'),
    # Database clients/ORMs
    ('sqlalchemy-advanced', 'SQLAlchemy advanced - custom types, dialects, events, hybrid properties, window functions'),
    ('tortoise-orm', 'Tortoise ORM - async, models, queryset, signals, transactions, migrations, validators'),
    ('peewee-orm', 'Peewee ORM - models, queries, migrations, signals, connection pooling, SQLite extensions'),
    ('pony-orm', 'Pony ORM - entity-relationship, Python generators as queries, composite keys, aggregates'),
    ('prisma-advanced', 'Prisma advanced - raw queries, middleware, fluent API, edge, accelerate, data proxy'),
    ('drizzle-advanced', 'Drizzle ORM advanced - relational queries, prepared statements, views, enums, RLS'),
    ('typeorm-advanced', 'TypeORM advanced - query builder, migration, listeners, subscribers, caching, STI'),
    ('sequelize-advanced', 'Sequelize advanced - associations, scopes, hooks, transactions, optimistic locking'),
    ('mongoose-advanced', 'Mongoose advanced - schema types, virtuals, middleware, population, discriminators, indexes'),
    ('prisma-client', 'Prisma Client - CRUD, relations, filtering, transactions, raw SQL, middleware, extensions'),
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
