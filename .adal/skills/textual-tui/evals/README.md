# Evals

These evals are meant for iterative skill testing.

Suggested workflow:
1. run the prompt with this skill activated
2. save outputs per eval case
3. grade against the assertions in `evals/evals.json`
4. compare against a baseline run without the skill or against an older skill snapshot

Included sample projects:
- `files/broken-search/` — blocking handler, inline CSS, manual Rich table, no tests
- `files/report-export/` — export-like app that writes local files but has no delivery API path
