"""Alpha Forge Pre-Ship Quality Gates.

Reference: /tmp/CANONICAL_PRESHOP_AUDIT_HANDBOOK.md
           /tmp/PHASE_1_IMPLEMENTATION_PLAN.md

Phase 1 gates (4 core validators):
- G4: URL Fork Validator (pre-commit)
- G5: RNG Determinism Validator (pre-commit)
- G8: Parameter Validation Validator (runtime)
- G12: Manifest Sync Validator (CI)

Phase 2 gates (4 additional validators):
- G1: Documentation Scope Validator (pre-commit)
- G2: Documentation Clarity Validator (pre-commit)
- G3: Documentation Completeness Validator (pre-commit)
- G6: Warmup Alignment Validator (decorator + DSL)
- G7: Parameter Documentation Validator (pre-commit)
- G10: Performance Red Flags Validator (pre-commit)
"""

from .g1_documentation_scope import DocumentationScopeValidator
from .g2_documentation_clarity import DocumentationClarityValidator
from .g3_documentation_completeness import DocumentationCompletenessValidator
from .g4_url_validation import validate_org_urls
from .g5_rng_determinism import validate_rng_isolation
from .g6_warmup_alignment import WarmupAlignmentValidator
from .g7_parameter_documentation import ParameterDocumentationValidator
from .g8_parameter_validation import ParameterValidator
from .g10_performance_red_flags import PerformanceRedFlagsValidator
from .g12_manifest_sync import ManifestSyncValidator

__all__ = [
    "DocumentationScopeValidator",
    "DocumentationClarityValidator",
    "DocumentationCompletenessValidator",
    "validate_org_urls",
    "validate_rng_isolation",
    "WarmupAlignmentValidator",
    "ParameterDocumentationValidator",
    "ParameterValidator",
    "PerformanceRedFlagsValidator",
    "ManifestSyncValidator",
]
