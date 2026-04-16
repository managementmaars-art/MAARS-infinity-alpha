# Migration/Refactor Template

## Purpose
A migration/refactor document provides a detailed plan for transforming existing code, schemas, or infrastructure. Unlike spikes (exploratory) or ADRs (decision records), migrations are execution plans with specific steps, risks, and rollback procedures.

## When to Create a Migration Document
- Database schema changes
- API version upgrades
- Framework migrations (e.g., Python 3.9 → 3.12)
- Pattern adoption (e.g., migrating to ServiceResult pattern)
- Infrastructure changes (e.g., Neo4j 4.x → 5.x)
- Large-scale refactoring (e.g., breaking monolith into services)

## Template Structure

```markdown
---
title: <Migration Title>
date: YYYY-MM-DD
type: migration | refactor
status: Planning | In Progress | Complete | Rolled Back
related_adr: docs/adr/XXX_name.md  # ADR that decided on this migration
category: schema | code | infrastructure | dependency
risk_level: low | medium | high | critical
estimated_duration: X hours/days/weeks
---

# Migration: <Title>

## Executive Summary

**What:** <One sentence: What is being migrated>
**Why:** <One sentence: Why this migration is necessary>
**Impact:** <One sentence: Who/what is affected>
**Timeline:** <One sentence: When and how long>

## Current State

### What Exists Today

<Detailed description of current implementation>

**Components Affected:**
- Component 1: Current behavior
- Component 2: Current behavior
- Component 3: Current behavior

**Current Metrics:**
- Metric 1: Current value
- Metric 2: Current value
- Metric 3: Current value

**Known Issues:**
- Issue 1: Impact and frequency
- Issue 2: Impact and frequency

### Evidence of Need

<Why migration is necessary>

**Problem Indicators:**
- Metric showing degradation
- Error rates or complaints
- Technical debt accumulation
- Compatibility requirements

**Cost of Not Migrating:**
- Short-term cost (1-3 months)
- Long-term cost (6-12 months)

## Desired State

### What We're Building

<Detailed description of target state>

**Target Architecture:**
- Component 1: New behavior
- Component 2: New behavior
- Component 3: New behavior

**Target Metrics:**
- Metric 1: Target value (improvement: +X%)
- Metric 2: Target value (improvement: +X%)
- Metric 3: Target value (improvement: +X%)

**Benefits Gained:**
- Benefit 1: Specific impact
- Benefit 2: Specific impact

### Success Criteria

<Measurable conditions that define "done">

**Functional Criteria:**
- [ ] All existing functionality preserved
- [ ] New functionality working as specified
- [ ] No regressions in behavior

**Quality Criteria:**
- [ ] Test coverage ≥ baseline
- [ ] Performance ≥ baseline
- [ ] Error rates ≤ baseline

**Process Criteria:**
- [ ] Documentation updated
- [ ] Team trained on new approach
- [ ] Monitoring in place

## Migration Path

### Overview

**Strategy:** Big Bang | Incremental | Parallel Run | Strangler Fig

**Phases:**
1. Phase 1: <Name> - Duration: X
2. Phase 2: <Name> - Duration: X
3. Phase 3: <Name> - Duration: X

**Total Duration:** X days/weeks (estimated)

### Detailed Steps

#### Phase 1: <Foundation/Preparation>

**Goal:** <What this phase achieves>

**Duration:** X hours/days

**Prerequisites:**
- [ ] Prerequisite 1
- [ ] Prerequisite 2

**Steps:**

1. **Step 1.1: <Specific Action>**
   - What: Detailed description
   - How: Specific commands/code changes
   - Files affected: `path/to/file.py`, `path/to/other.py`
   - Tests required: Unit tests for X, integration tests for Y
   - Verification: How to confirm this step succeeded

2. **Step 1.2: <Specific Action>**
   - What: Detailed description
   - How: Specific approach
   - Files affected: List with line numbers if possible
   - Tests required: Specific test names
   - Verification: Commands to run

3. **Step 1.3: <Specific Action>**
   <Repeat structure>

**Validation:**
- [ ] Validation check 1
- [ ] Validation check 2
- [ ] Baseline metrics captured

**Rollback Point:**
If phase fails, rollback via:
1. Rollback step 1
2. Rollback step 2

#### Phase 2: <Migration/Implementation>

**Goal:** <What this phase achieves>

**Duration:** X hours/days

**Dependencies:**
- Phase 1 complete
- Additional dependency

**Steps:**

1. **Step 2.1: <Specific Action>**
   <Use same detailed structure as Phase 1>

2. **Step 2.2: <Specific Action>**
   <Continue with all steps>

**Compatibility Period:**
- Old approach available: Yes | No
- Deprecation warnings: Where and when
- Both approaches supported for: X days/weeks

**Validation:**
- [ ] Old functionality still works (if parallel run)
- [ ] New functionality works
- [ ] Performance metrics measured

**Rollback Point:**
<How to rollback this phase>

#### Phase 3: <Cleanup/Finalization>

**Goal:** Remove old code, finalize migration

**Duration:** X hours/days

**Prerequisites:**
- Phase 2 validated in production
- No rollbacks triggered for X days
- Stakeholder sign-off

**Steps:**

1. **Step 3.1: Remove Old Code**
   - Files to delete: List
   - Code sections to remove: Specific references
   - Ensure no references remain: `grep -r "OldPattern" src/`

2. **Step 3.2: Update Documentation**
   - Docs to update: List
   - New examples to add: Where
   - Old examples to remove: Where

3. **Step 3.3: Remove Compatibility Layers**
   <If Phase 2 included adapters>

**Final Validation:**
- [ ] Old code completely removed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Monitoring shows healthy metrics

## Risk Analysis

### High-Risk Areas

#### Risk 1: <Specific Risk>

**Likelihood:** Low | Medium | High
**Impact:** Low | Medium | High | Critical
**Overall Risk:** Low | Medium | High | Critical

**Description:**
<What could go wrong>

**Indicators:**
- Early warning sign 1
- Early warning sign 2

**Mitigation:**
- Proactive mitigation 1
- Proactive mitigation 2

**Contingency:**
If this risk materializes:
1. Response step 1
2. Response step 2
3. Escalation path

#### Risk 2: <Specific Risk>

<Repeat structure>

### Risk Matrix

| Risk | Likelihood | Impact | Overall | Mitigation Status |
|------|------------|--------|---------|-------------------|
| Risk 1 | High | Critical | High | In place |
| Risk 2 | Medium | High | Medium | In place |
| Risk 3 | Low | Medium | Low | Monitoring |

## Rollback Plan

### Triggers

**Automatic Rollback Triggers:**
- Error rate > X% (threshold: X errors/min)
- Performance degradation > X% (response time > Xms)
- Data corruption detected
- Critical functionality broken

**Manual Rollback Triggers:**
- Team decision based on unforeseen issues
- Stakeholder escalation
- Time box exceeded without success

### Rollback Procedures

#### Full Rollback (Revert Everything)

**When:** Critical issues, unable to proceed

**Steps:**
1. Stop migration process immediately
2. Revert code changes:
   ```bash
   git revert <commit-range>
   # OR
   git reset --hard <pre-migration-commit>
   ```
3. Restore database (if schema changed):
   ```bash
   # Restore from backup
   neo4j-admin restore --from=<backup-path>
   ```
4. Restart services
5. Validate rollback:
   - [ ] Old functionality working
   - [ ] Metrics returned to baseline
   - [ ] No data loss

**Expected Duration:** X minutes/hours

**Verification:**
- Run health check: `./scripts/health_check.sh`
- Check metrics dashboard
- Smoke test critical paths

#### Partial Rollback (Revert Specific Phase)

**When:** One phase failed but others succeeded

**Phase 1 Rollback:**
<Steps specific to Phase 1>

**Phase 2 Rollback:**
<Steps specific to Phase 2>

**Phase 3 Rollback:**
<Steps specific to Phase 3>

### Post-Rollback

**Immediate Actions:**
1. Notify stakeholders
2. Document what went wrong
3. Preserve logs and metrics
4. Schedule postmortem

**Analysis Questions:**
- What triggered the rollback?
- Were early warning signs missed?
- What assumptions were incorrect?
- How can we prevent this next attempt?

## Testing Strategy

### Pre-Migration Tests

**Baseline Capture:**
- [ ] Run full test suite, capture pass rate
- [ ] Run performance benchmarks, capture metrics
- [ ] Document current behavior with test examples

**Test Environment:**
- [ ] Create test environment matching production
- [ ] Load test data representative of production
- [ ] Validate test environment works correctly

### During Migration Tests

**Phase 1 Tests:**
- [ ] Unit tests: List specific test files
- [ ] Integration tests: List specific test scenarios
- [ ] Smoke tests: Critical paths to validate

**Phase 2 Tests:**
- [ ] Compatibility tests (old + new working together)
- [ ] Regression tests (no behavior changes)
- [ ] Performance tests (no degradation)

**Phase 3 Tests:**
- [ ] Full test suite passing
- [ ] No old code references remain
- [ ] Documentation examples work

### Post-Migration Tests

**Validation Tests:**
- [ ] All original tests passing
- [ ] New tests for new functionality passing
- [ ] Performance benchmarks meet or exceed baseline

**Production Validation:**
- [ ] Canary deployment (10% traffic)
- [ ] Gradual rollout (25%, 50%, 100%)
- [ ] Metrics monitoring at each stage

## Monitoring Plan

### Metrics to Track

**Before Migration:**
- Baseline metric 1: Value
- Baseline metric 2: Value
- Baseline metric 3: Value

**During Migration:**
- Real-time metric 1: Threshold for rollback
- Real-time metric 2: Threshold for rollback
- Real-time metric 3: Threshold for rollback

**After Migration:**
- Success metric 1: Target value
- Success metric 2: Target value
- Success metric 3: Target value

### Monitoring Tools

**Dashboards:**
- Dashboard 1: URL - What it shows
- Dashboard 2: URL - What it shows

**Alerts:**
- Alert 1: Condition → Action
- Alert 2: Condition → Action

**Logs:**
- Log location: Path
- Key log patterns to watch: Pattern list

## Communication Plan

### Stakeholders

| Stakeholder | Role | Notification Timing | Communication Method |
|-------------|------|---------------------|----------------------|
| Team Lead | Approval | Before migration | In-person meeting |
| Dev Team | Execution | Daily updates | Slack #migrations |
| QA Team | Validation | After each phase | Test reports |
| Ops Team | Production support | 24h before prod | Email + Slack |

### Status Updates

**Before Migration:**
- Migration plan reviewed: Date
- Approval received: Date
- Timeline communicated: Date

**During Migration:**
- Daily progress updates: Where posted
- Blockers escalated: How and to whom
- Rollback notifications: Immediate via Slack + Email

**After Migration:**
- Completion announcement: Channel
- Postmortem scheduled: Date
- Lessons learned documented: Location

## Dependencies

### Internal Dependencies

**Code Dependencies:**
- Module 1: How it's affected
- Module 2: How it's affected

**Data Dependencies:**
- Database 1: Schema changes needed
- Cache: Invalidation strategy

**Infrastructure Dependencies:**
- Service 1: Version requirements
- Service 2: Configuration changes

### External Dependencies

**Third-Party Services:**
- Service 1: API version requirements
- Service 2: Compatibility checks

**Library Dependencies:**
- Library 1: Version upgrade needed
- Library 2: Migration guide followed

## Training Plan

### Documentation

**New Documentation:**
- [ ] Migration guide for future reference
- [ ] Updated API documentation
- [ ] New code examples

**Updated Documentation:**
- [ ] README changes
- [ ] Architecture docs
- [ ] Runbooks

### Team Training

**Training Sessions:**
1. Session 1: New patterns overview (X hours)
2. Session 2: Hands-on migration walkthrough (X hours)
3. Session 3: Q&A and troubleshooting (X hours)

**Knowledge Transfer:**
- [ ] Record migration process
- [ ] Create troubleshooting guide
- [ ] Document common pitfalls

## Cost Analysis

### Time Investment

| Phase | Estimated Hours | Actual Hours | Notes |
|-------|----------------|--------------|-------|
| Phase 1 | X hours | - | |
| Phase 2 | X hours | - | |
| Phase 3 | X hours | - | |
| Testing | X hours | - | |
| Documentation | X hours | - | |
| **Total** | **X hours** | - | |

### Resource Requirements

**Team Allocation:**
- Developer 1: X hours/week for Y weeks
- Developer 2: X hours/week for Y weeks
- QA: X hours for testing

**Infrastructure:**
- Test environment: Cost and duration
- Backup storage: Cost
- Monitoring tools: Cost

### Opportunity Cost

**What We're Not Doing:**
- Feature A delayed by X weeks
- Bug fix B postponed
- Project C on hold

**Why Migration Is Higher Priority:**
<Justification>

## References

### Related Documents
- ADR: [ADR-XXX]() - Decision that led to this migration
- Spike: [spike_name.md]() - Research that informed this plan
- Previous migrations: [migration_name.md]() - Lessons learned

### Technical Resources
- Official migration guide: [URL]
- API documentation: [URL]
- Best practices: [URL]

### Tools and Scripts
- Migration script: `scripts/migrate_to_v2.py`
- Validation script: `scripts/validate_migration.py`
- Rollback script: `scripts/rollback_migration.py`

---

**Migration Owner:** @person
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Status:** Planning | In Progress | Complete | Rolled Back
**Start Date:** YYYY-MM-DD (planned)
**Completion Date:** YYYY-MM-DD (planned)
```

## Best Practices

### Planning Phase
- **DO** create comprehensive rollback plan before starting
- **DO** test migration in staging environment first
- **DO** involve all affected teams in planning
- **DON'T** start without stakeholder approval

### Execution Phase
- **DO** follow phases strictly (don't skip validation)
- **DO** monitor metrics continuously
- **DO** document deviations from plan
- **DON'T** rush if behind schedule (safety first)

### Post-Migration Phase
- **DO** conduct postmortem (even if successful)
- **DO** update documentation immediately
- **DO** capture lessons learned
- **DON'T** remove monitoring too quickly

## Anti-Patterns

❌ **Big bang without rollback**
```markdown
## Migration Path
1. Change everything at once
2. Hope it works
```

✅ **Incremental with rollback**
```markdown
## Migration Path
Phase 1: Add new code (non-breaking)
Phase 2: Migrate incrementally with compatibility layer
Phase 3: Remove old code after validation
Rollback: Specific steps at each phase
```

❌ **Vague steps**
```markdown
## Steps
1. Update the database
2. Fix the code
```

✅ **Specific, executable steps**
```markdown
## Steps
1. Update database schema:
   - Run: `scripts/migrate_schema_v1_to_v2.py`
   - Verify: `SELECT version FROM schema_version;` returns 2
   - Files: `migrations/001_add_columns.cypher`
2. Update code to use new schema:
   - Files: `src/repository/user_repository.py:45-67`
   - Change: Add `database=self.database` parameter
   - Tests: `tests/unit/test_user_repository.py::test_database_param`
```

❌ **No metrics**
```markdown
## Success
It works.
```

✅ **Measurable success criteria**
```markdown
## Success Criteria
- Query response time: Baseline 500ms → Target 300ms (40% improvement)
- Error rate: Baseline 2% → Target <1% (50% reduction)
- Test coverage: Baseline 85% → Target ≥85% (no regression)
```

## Migration Types Reference

### Schema Migration
- Database schema changes (add/remove columns, tables, indexes)
- Graph schema changes (node labels, relationship types, properties)
- Use liquibase/flyway patterns for versioning

### Code Migration
- Pattern adoption (e.g., ServiceResult)
- Framework upgrades (e.g., FastAPI 0.x → 1.x)
- Language version (e.g., Python 3.9 → 3.12)

### Infrastructure Migration
- Cloud provider changes
- Database engine upgrades
- Container orchestration changes

### Dependency Migration
- Library version upgrades
- Breaking API changes
- Deprecated package replacements

## Example: Complete Migration

See `/docs/migrations/example_neo4j_v4_to_v5.md` for a reference implementation.
