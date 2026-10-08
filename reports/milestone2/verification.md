# Milestone 2 verification record

Run date: 2026-09-11.

- Source verification: all eight downloaded non-image files matched pinned publisher SHA-256 hashes.
- SQL build: completed; SQLite integrity_check returned `ok`.
- Tests: **14 passed**, 0 failures, 0 skips. Eight use explicitly synthetic fixtures; six read the generated historical database.
- Coverage: exact identifiers, duplicate observation collapse, conflict quarantine, simultaneous cross-field changes, missing timestamps, invalid bounds, endpoint definitions, named handoffs, interval validity, source lineage, population preservation, eligibility, unresolved-case retention and key integrity.
- AI/model tests: not applicable at this milestone. No model or business intervention was evaluated.

Re-run with `python -m unittest discover -s tests -v` after relevant changes. Runtime versions and pipeline/SQL hashes are recorded in validation-summary.json. This verification does not establish complete historical capture, causality or production readiness.
