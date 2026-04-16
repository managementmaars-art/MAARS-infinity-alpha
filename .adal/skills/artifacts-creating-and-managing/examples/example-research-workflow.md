# Example: Research Library Workflow

## Scenario

User asks: "Research libraries for state management in React"

## Workflow Steps

### 1. Create Research Artifact

```bash
python /path/to/scripts/create_research_topic.py \
  --topic "React State Management Libraries" \
  --objective "Choose state library for new features" \
  --questions "Performance?" "Learning curve?" "TypeScript support?"
```

### 2. Conduct Research

Add findings to the created artifact:
- Compare Redux, Zustand, Jotai, Recoil
- Test performance benchmarks
- Review documentation quality
- Evaluate TypeScript support

### 3. Document Findings

Update the RESEARCH_SUMMARY.md file with:
- Key findings for each library
- Performance comparison data
- Learning curve assessment
- TypeScript integration experience

### 4. Make Recommendation

Add conclusion section with:
- Recommended library
- Rationale for choice
- Implementation considerations
- Next steps

## Expected Output

**File:** `.claude/artifacts/YYYY-MM-DD/analysis/react-state-management-libraries/RESEARCH_SUMMARY.md`

**Structure:**
- Research objective
- Questions answered
- Findings for each library
- Comparative analysis
- Final recommendation
