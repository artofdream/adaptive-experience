# Requirement evidence convention

`requirement-evidence.json` is the machine-readable inventory for canonical
FR/NFR links to ADR declarations, implementation citations, and test citations.
It complements the live GitLab issue/milestone/closure checks in
`scripts/check_traceability.py`.

The inventory records **citation evidence**, not behavioral proof. A source or
test path marked `evidenced` contains the requirement ID; reviewers must still
judge whether the implementation or assertion is substantively sufficient.

Each requirement and evidence kind has one disposition:

- `evidenced`: one or more existing paths explicitly cite the requirement;
- `planned`: Future-scoped work has no current path-level citation;
- `not-applicable`: the evidence kind is intentionally inapplicable;
- `unclaimed`: no defensible evidence claim has been established yet.

ADR evidence is valid only when the ID occurs in the ADR's top-level
`Related requirements` declaration. Incidental prose is not enough. Generated
implementation evidence scans `platform/` and `edge/` source files; generated
test evidence scans their test paths.

Regenerate after adding or removing citations:

```powershell
python scripts/generate_requirement_evidence.py
python scripts/generate_requirement_evidence.py --check
python scripts/check_requirement_evidence.py
```

Do not replace `unclaimed` with `evidenced` unless a cited path exists. A
Future requirement may have thin evidence while its broader scope remains
Future; the canonical scope remains authoritative.
