# Evidence-Grounded Scientific Writing

A multi-agent workflow for drafting and revising biomedical manuscripts while keeping each scientific claim connected to experimental evidence or a verified source.

## What it does

The main agent coordinates a scientific writer, critical challenger, literature researcher, citation adjudicator, focused peer reviewer, and academic humanizer. Each role receives a bounded task; the main agent resolves conflicts using evidence quality and relevance, then owns the final draft.

## Workflow

1. **Preflight:** define the section, audience, style, available data, required claims, and known gaps.
2. **Independent review:** draft conservatively, challenge causal and statistical claims, retrieve targeted source cards, and audit style.
3. **Evidence adjudication:** check each claim against its figure, method, dataset, or source; accept, calibrate, replace, or reject citations.
4. **Peer review and polish:** run only the reviewer perspectives the task needs, integrate actionable feedback, and perform a final style and fidelity check.

The default is three rounds, with early stopping for narrow or already-resolved tasks.

## Unresolved issues

Important questions that cannot be settled from the available evidence enter a visible Discussion/Limitations queue. Each item records the affected claim, evidence on both sides, severity, candidate wording, what would resolve it, and whether author input is pending. Queued interpretations are not silently presented as established findings.

## Bundle contents

- `SKILL.md`: orchestration rules and final acceptance checklist
- `references/ledger-schema.md`: claim, source, challenge, review, and unresolved-issue records
- `references/round-protocol.md`: intake, three rounds, review perspectives, and stop rules

## Install and use

Copy this directory to `~/.codex/skills/evidence-grounded-scientific-writing`, then start a new Codex task and invoke:

```text
$evidence-grounded-scientific-writing
```

Provide the draft or requested task, figures and methods or other evidence, target journal or style, length, and author preferences. Install the companion skills separately if you want to call them as standalone tools:

- [Academic Humanizer](../academic-humanizer/README.md)
- [Scientific Critical Thinking](../scientific-critical-thinking/README.md)
- [Peer Reviewer](../peer-reviewer/README.md)

## Limits

The workflow organizes and challenges evidence; it does not validate raw data automatically or replace scientific judgment. Agreement among agents is not independent experimental confirmation. Missing details remain marked as missing, and substantive decisions stay with the author.
