"""Generate or verify Codex, Claude, and Copilot adapters for AEA stakeholder skills."""

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_TARGET = ROOT / ".agents" / "skills"
CLAUDE_TARGET = ROOT / ".claude" / "skills"
COPILOT_TARGET = ROOT / ".github" / "instructions"
SOURCE = ROOT / ".cursor" / "skills"

SKILLS = {
    "aea-ai-engineer": (
        "Ensure Lily's Florist and AEA AI-supported paths are real and honest, assess gaps against documented AI promises and customer pains, and implement one routed gap under ADR-016. Use for AI honesty or disclosure audits, intent/LLM/AgentRuntime/RAG work, AI-category GitLab issues, or the AEA AI engineer stakeholder.",
        "Read the linked `reality.md` when the canonical skill routes to it.",
        "Use Codex visualization when useful; ignore Cursor canvas paths. Do not start subagents or tasks unless the user explicitly requests delegation.",
    ),
    "aea-appsec-auditor": (
        "Audit AEA application security, prompt injection defenses, API perimeter authentication, CORS, rate limiting, OWASP Top 10 vulnerabilities, and data sanitization across edge, gateway, and platform services. Use for application security audits, penetration testing, prompt injection reviews, API security, or the AEA appsec auditor stakeholder.",
        "Read the canonical skill completely before auditing application security boundaries.",
        "Audit application threat surfaces, LLM prompt injection defenses, and perimeter security. Do not replace devsecops platform infrastructure authority.",
    ),
    "aea-customer-journey": (
        "Walk the live Lily's Florist AEA customer Adaptive Workspace as a first-time shopper, verify the documented end-to-end journey, and report blockers and friction. Use for live customer journey walks, E2E shop assessments, journey pain points, or the mother-birthday scenario on localhost.",
        "Read the linked `walk.md` for every live walk.",
        "Use the installed `browser:control-in-app-browser` skill instead of Cursor browser tools. Use Codex visualization when requested; ignore Cursor canvas paths.",
    ),
    "aea-coherence-guardian": (
        "Own the AEA / Lily's Florist coherence findings loop end to end — running assessment intake against research/coherence-findings-loop.md, remediating the first queued or regressed finding one at a time, and producing the periodic repo activity/status brief under research/daily-briefs/. Use for coherence checks, hourly/daily coherence ticks, doc/code/ID drift, reconciling the CF queue against GitLab, activity reports, or the AEA coherence guardian stakeholder.",
        "Follow `research/coherence-findings-loop.md` as the operative procedure this role runs, not a companion reference file.",
        "Treat the coherence loop and the daily activity brief as this role's job, not the PM's or support coordinator's. Do not create Codex tasks, threads, or subagents unless the user explicitly requests delegation.",
    ),
    "aea-devsecops-platform": (
        "Assess and improve AEA platform excellence, maintenance, security, AWS deployment, Terraform, GitLab CI, Kafka and PostgreSQL operations, secrets, encryption, and production posture. Use for DevSecOps, cloud infrastructure, CI/CD, deployment drift, production flags, or the AEA DevSecOps platform stakeholder.",
        "Read the linked `posture.md` whenever the canonical workflow requires posture or AWS state.",
        "Cursor Cloud Agent policy is informational only. Do not create Codex tasks, threads, or subagents unless the user explicitly requests delegation. Use applicable Codex AWS skills without replacing the established Terraform architecture.",
    ),
    "aea-mr-coordinator": (
        "Review and process AEA GitLab merge requests when explicitly invoked, applying scope, boundary, validation, conflict, and pipeline gates before enabling auto-merge. Use only when the user invokes the AEA MR coordinator or explicitly asks that stakeholder to process GitLab MRs.",
        "Read the linked `gates.md` completely before any MR action.",
        "Use `glab`, not GitHub tooling. Do not delegate conflict resolution unless the user explicitly requests it; report the handoff to `$aea-senior-software-engineer`.",
    ),
    "aea-product-owner": (
        "Own AEA / Lily's Florist product mission, vision, backlog priority among existing IDs, and product go/no-go (accept, defer, park), including M12 CRM unpark recommendation and Path A vs Path B product acceptance. Use for product mission, vision, backlog, priority, go/no-go, should we ship, acceptance, or M12 unpark.",
        "Treat the canonical skill as the authoritative product-owner role, vision SoT, and go/no-go rules.",
        "Exercise product go/no-go within existing archive IDs. A routed role does not authorize creating a Codex task, thread, or subagent unless the user explicitly requests delegation. Do not absorb Scrum, specialist, merge, secret, or destructive cloud authority.",
    ),
    "aea-project-manager": (
        "Act as the authoritative AEA Scrum Master and project manager, owning Scrum process, cadence, impediment removal, WIP, readiness and done gates, blockers, routing, assignments, sequencing, milestone readiness, and process coherence. Use for stakeholder coordination, Scrum delivery, status, blockers, idle owners, work assignment, or delivery-gate enforcement.",
        "Treat the canonical skill as the authoritative team roster, Scrum process, and cadence definition.",
        "Exercise full Scrum/process authority within approved scope. A routed role does not authorize creating a Codex task, thread, or subagent unless the user explicitly requests delegation. Do not absorb product, specialist, merge, secret, or destructive cloud authority.",
    ),
    "aea-senior-software-engineer": (
        "Design, architect, implement, and enhance AEA platform and edge code against repository ADRs and engineering best practices. Use only when the user invokes the AEA senior software engineer or asks that stakeholder to implement, architect, resolve integration conflicts, or enhance the repository.",
        "Preserve its specialist handoffs and Docker-before-MR requirements.",
        "Do not create subagents or tasks for collaboration unless the user explicitly requests delegation. Ignore Cursor canvas paths and use Codex visualization only when useful.",
    ),
    "aea-support-coordinator": (
        "Intake, prioritize, route, and follow up on Lily's Florist customer and operator issues until each has a GitLab owner and next action. Use for support triage, Contact Florist or operator inbox routing, journey blocker prioritization, escalation follow-up, or the AEA support coordinator stakeholder.",
        "Read the linked `routing.md` for routing decisions.",
        "Routing identifies an owner and next action; it does not authorize starting a task or subagent. Use the Codex browser skill for explicit live inspection and keep operator and customer sessions separate.",
    ),
    "aea-ux-designer": (
        "Assess and improve the Lily's Florist AEA customer Adaptive Workspace, tiles T-01 through T-08, ASO, Contact Florist, accessibility, existing HTML/CSS/JS, and Figma mirror. Use for UX assessment, workspace redesign, tile or journey UX, accessibility, Figma synchronization, or the AEA UX designer stakeholder.",
        "Read the linked `reference.md` when assessing or changing the UI.",
        "Use installed Figma skills and mandatory prerequisites for Figma work, and the Codex browser skill for live inspection. Ignore Cursor canvas paths.",
    ),
}


def canonical_digest(name: str) -> str:
    canonical = (SOURCE / name / "SKILL.md").read_text(encoding="utf-8")
    normalized = canonical.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def render_codex(name: str, description: str, linked: str, adaptation: str) -> str:
    title = name.removeprefix("aea-").replace("-", " ")
    digest = canonical_digest(name)
    return f'''---
name: {name}
description: {description}
---

<!-- Generated by scripts/generate_codex_stakeholder_skills.py.
     canonical-sha256: {digest} -->

# AEA {title} for Codex

Read `../../../.cursor/skills/{name}/SKILL.md` completely before acting. {linked}
Treat the canonical files as the repository-owned role definition. Preserve all
scope, architecture, safety, GitLab, validation, ownership, and merge boundaries.

## Codex adaptations

- Interpret `@aea-<role>` handoffs as the corresponding `$aea-<role>` Codex skill.
- {adaptation}
- Keep the canonical `glab` and one-issue/branch/MR discipline unchanged.
'''


def render_claude(name: str, description: str, linked: str, _adaptation: str) -> str:
    title = name.removeprefix("aea-").replace("-", " ")
    digest = canonical_digest(name)
    return f'''---
name: {name}
description: {description}
---

<!-- Generated by scripts/generate_codex_stakeholder_skills.py.
     canonical-sha256: {digest} -->

# AEA {title} for Claude

Read `../../../.cursor/skills/{name}/SKILL.md` completely before acting. {linked}
Treat the canonical files as the repository-owned role definition. Preserve all
scope, architecture, safety, GitLab, validation, ownership, and merge boundaries.

## Claude adaptations

- Interpret stakeholder handoffs as the matching `aea-*` Claude skill.
- Follow the repository-level instructions in `../../../CLAUDE.md`.
- Translate tool-specific instructions only where Claude exposes an equivalent;
  never broaden authority or silently omit a required gate.
- Keep the canonical `glab` and one-issue/branch/MR discipline unchanged.
'''


def render_copilot(name: str, description: str, linked: str, _adaptation: str) -> str:
    title = name.removeprefix("aea-").replace("-", " ")
    digest = canonical_digest(name)
    return f'''---
description: {description}
applyTo: '**'
---

<!-- Generated by scripts/generate_codex_stakeholder_skills.py.
     canonical-sha256: {digest} -->

# AEA {title} for Copilot

Read `../../.cursor/skills/{name}/SKILL.md` completely before acting as this
role. {linked}
Treat the canonical files as the repository-owned role definition. Preserve all
scope, architecture, safety, GitLab, validation, ownership, and merge boundaries.

## Copilot adaptations

- Copilot has no persona-switch or `@mention` role invocation: apply this
  file's guidance when the user explicitly asks to act as the AEA {title}
  stakeholder, or when the request clearly matches this role's owned surfaces
  and boundaries in the canonical skill.
- `applyTo: '**'` keeps this instruction file always eligible; it is not a
  claim that this role applies to every request — the canonical skill's own
  triggers and exclusions still decide relevance.
- Use `glab`, not GitHub CLI/PR tooling, for this repository's GitLab project.
- Keep the canonical one-issue/branch/MR discipline unchanged.
'''


def skill_names(root: Path) -> set[str]:
    return {path.parent.name for path in root.glob("aea-*/SKILL.md")}


def copilot_names(root: Path) -> set[str]:
    return {path.stem.removesuffix(".instructions") for path in root.glob("aea-*.instructions.md")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail if Cursor, Codex, and Claude skills differ")
    args = parser.parse_args()

    canonical_names = skill_names(SOURCE)
    configured_names = set(SKILLS)
    if canonical_names != configured_names:
        missing = sorted(canonical_names - configured_names)
        extra = sorted(configured_names - canonical_names)
        raise SystemExit(f"stakeholder skill inventory mismatch: missing={missing}, extra={extra}")

    drift = []
    for name, values in SKILLS.items():
        path = CODEX_TARGET / name / "SKILL.md"
        if not path.parent.is_dir():
            path.parent.mkdir(parents=True, exist_ok=True)
        expected = render_codex(name, *values)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                drift.append(str(path.relative_to(ROOT)))
            metadata = path.parent / "agents" / "openai.yaml"
            if not metadata.is_file():
                drift.append(str(metadata.relative_to(ROOT)))
        else:
            path.write_text(expected, encoding="utf-8")

        claude_path = CLAUDE_TARGET / name / "SKILL.md"
        claude_expected = render_claude(name, *values)
        if args.check:
            if (not claude_path.is_file() or
                    claude_path.read_text(encoding="utf-8") != claude_expected):
                drift.append(str(claude_path.relative_to(ROOT)))
        else:
            claude_path.parent.mkdir(parents=True, exist_ok=True)
            claude_path.write_text(claude_expected, encoding="utf-8")

        copilot_path = COPILOT_TARGET / f"{name}.instructions.md"
        copilot_expected = render_copilot(name, *values)
        if args.check:
            if (not copilot_path.is_file() or
                    copilot_path.read_text(encoding="utf-8") != copilot_expected):
                drift.append(str(copilot_path.relative_to(ROOT)))
        else:
            copilot_path.parent.mkdir(parents=True, exist_ok=True)
            copilot_path.write_text(copilot_expected, encoding="utf-8")

    codex_names = skill_names(CODEX_TARGET)
    if codex_names != configured_names:
        drift.append(
            f"Codex inventory mismatch: missing={sorted(configured_names - codex_names)}, "
            f"extra={sorted(codex_names - configured_names)}"
        )
    claude_names = skill_names(CLAUDE_TARGET)
    if claude_names != configured_names:
        drift.append(
            f"Claude inventory mismatch: missing={sorted(configured_names - claude_names)}, "
            f"extra={sorted(claude_names - configured_names)}"
        )
    copilot_inventory = copilot_names(COPILOT_TARGET)
    if copilot_inventory != configured_names:
        drift.append(
            f"Copilot inventory mismatch: missing={sorted(configured_names - copilot_inventory)}, "
            f"extra={sorted(copilot_inventory - configured_names)}"
        )
    if drift:
        details = "\n - ".join(drift)
        raise SystemExit(
            "Cursor/Codex/Claude/Copilot stakeholder skills are out of sync. Run "
            f"`python scripts/generate_codex_stakeholder_skills.py`.\n - {details}"
        )
    if args.check:
        print(f"ok: {len(SKILLS)} Cursor/Codex/Claude/Copilot stakeholder skills are synchronized")


if __name__ == "__main__":
    main()
