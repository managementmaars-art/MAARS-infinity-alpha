
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Academic disciplines and research skills
    ('linguistics-computational', 'Computational linguistics - morphology, syntax, semantics, pragmatics, parsing, corpora, evaluation'),
    ('cognitive-science', 'Cognitive science - perception, memory, attention, reasoning, mental models, embodied cognition'),
    ('political-science-methods', 'Political science methods - comparative politics, IR, regression, text analysis, experiments'),
    ('sociology-research', 'Sociology research - survey design, ethnography, network analysis, stratification, institutions'),
    ('anthropology-research', 'Anthropology research - ethnography, fieldwork, cultural analysis, kinship, material culture'),
    ('philosophy-of-ai', 'Philosophy of AI - consciousness, ethics, agency, epistemology, alignment, mind, intelligence'),
    ('philosophy-of-science', 'Philosophy of science - falsifiability, realism, models, causation, explanation, paradigms'),
    ('philosophy-of-mind', 'Philosophy of mind - consciousness, qualia, functionalism, physicalism, mental causation'),
    ('ethics-frameworks', 'Ethics frameworks - consequentialism, deontology, virtue ethics, care ethics, applied ethics'),
    ('logic-formal', 'Formal logic - propositional, predicate, modal, temporal, proof theory, model theory, sat solving'),
    ('epistemology', 'Epistemology - knowledge, justification, belief, skepticism, contextualism, foundationalism'),
    ('game-theory-advanced', 'Game theory advanced - mechanism design, auction theory, matching, cooperative, evolutionary'),
    ('decision-theory', 'Decision theory - utility, expected value, risk, ambiguity, bounded rationality, behavioral'),
    ('economics-behavioral', 'Behavioral economics - biases, heuristics, prospect theory, nudges, experiments, welfare'),
    ('economics-macro', 'Macroeconomics - models, DSGE, monetary policy, fiscal policy, growth theory, open economy'),
    ('economics-micro-advanced', 'Microeconomics advanced - contract theory, market design, industrial organization, regulation'),
    ('public-policy-analysis', 'Public policy analysis - policy cycle, cost-benefit, evaluation, implementation, equity'),
    ('social-network-analysis', 'Social network analysis - centrality, communities, diffusion, homophily, sampling, surveys'),
    ('science-technology-studies', 'Science and technology studies - sociotechnical systems, actor-network, infrastructure, values'),
    ('cognitive-load-theory', 'Cognitive load theory - intrinsic, extraneous, germane, instruction design, worked examples'),
    ('psycholinguistics', 'Psycholinguistics - language acquisition, sentence processing, bilingualism, reading, aphasia'),
    ('neurolinguistics', 'Neurolinguistics - Broca, Wernicke, ERP, fMRI, neural binding, dyslexia, BOLD, connectivity'),
    ('computational-social-science', 'Computational social science - digital trace data, text analysis, ABM, causal inference, APIs'),
    ('digital-humanities', 'Digital humanities - text analysis, GIS, network analysis, databases, visualization, archives'),
    ('archival-science', 'Archival science - provenance, arrangement, description, finding aids, digital preservation, EAD'),
    ('information-science', 'Information science - indexing, classification, metadata, retrieval, user behavior, IR models'),
    ('library-systems', 'Library systems - ILS, cataloging, MARC, linked data, discovery layers, resource sharing'),
    ('academic-publishing', 'Academic publishing - submission, peer review, open access, preprints, impact metrics, DOI'),
    ('research-methodology', 'Research methodology - design, sampling, measurement, validity, mixed methods, ethics'),
    ('systematic-review', 'Systematic review - PRISMA, search strategy, screening, extraction, meta-analysis, GRADE'),
    ('meta-analysis', 'Meta-analysis - effect sizes, heterogeneity, publication bias, forest plots, sensitivity, network'),
    ('grounded-theory', 'Grounded theory - coding, memos, theoretical sampling, saturation, constant comparison'),
    ('phenomenology-research', 'Phenomenological research - IPA, descriptive, hermeneutic, lifeworld, bracketing'),
    ('discourse-analysis', 'Discourse analysis - critical, conversation, multimodal, genre, CDA, positioning theory'),
    ('content-analysis', 'Content analysis - coding schemes, reliability, manifest, latent, quantitative, qualitative'),
    # Psychology research methods
    ('experimental-psychology', 'Experimental psychology - design, controls, randomization, repeated measures, within/between'),
    ('cognitive-psychology-methods', 'Cognitive psychology methods - reaction time, eye tracking, neuroimaging, computational models'),
    ('clinical-psychology-research', 'Clinical psychology research - RCTs, effectiveness, measurement, comorbidity, diagnosis'),
    ('developmental-psychology', 'Developmental psychology - longitudinal, cross-sectional, observation, coding, attachment'),
    ('social-psychology-research', 'Social psychology research - experiments, attitude measurement, implicit, confederates'),
    ('neuropsychological-assessment', 'Neuropsychological assessment - batteries, norms, interpretation, lateralization, rehabilitation'),
    ('psychometrics', 'Psychometrics - item response theory, factor analysis, reliability, validity, test construction'),
    # Education research
    ('learning-science', 'Learning science - cognitive, constructivist, socio-cultural, self-regulated, transfer'),
    ('educational-technology-research', 'EdTech research - efficacy studies, learning analytics, MOOC research, adaptive learning'),
    ('higher-ed-research', 'Higher education research - assessment, accreditation, retention, equity, outcomes, policy'),
    ('stem-education', 'STEM education - inquiry-based, project-based, computational thinking, maker education, equity'),
    ('learning-analytics-advanced', 'Learning analytics advanced - clickstream, predictive models, at-risk, intervention design'),
    # Law and jurisprudence
    ('legal-research-methods', 'Legal research methods - primary sources, secondary sources, case analysis, statutory interpretation'),
    ('international-law', 'International law - treaties, customary law, ICJ, international organizations, human rights'),
    ('comparative-law', 'Comparative law - civil law, common law, mixed systems, legal transplants, harmonization'),
    ('cyberlaw', 'Cyberlaw - jurisdiction, electronic contracts, digital evidence, cybercrime, platform liability'),
    ('data-protection-law', 'Data protection law - GDPR enforcement, adequacy decisions, transfers, DPO, supervisory authorities'),
    # Media and communication studies
    ('media-studies', 'Media studies - framing, agenda setting, media effects, political communication, misinformation'),
    ('communication-research', 'Communication research - interpersonal, organizational, mass, digital, mixed methods'),
    ('journalism-research', 'Journalism research - news values, source selection, digital disruption, fact-checking, trust'),
    ('data-journalism', 'Data journalism - data acquisition, analysis, visualization, storytelling, tools, verification'),
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
