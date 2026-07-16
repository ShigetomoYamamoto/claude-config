# Document Language by Audience (domain-neutral)

Which language to *write a document in*: match it to whoever reads the document.
This governs document authoring — distinct from the conversation-language rule
(reply to the user in Japanese; see Relation). It does not restate the content
norms that hold in any language (secrets, accuracy) — see Relation.

## The test: who is the primary reader?

When unsure, decide by the document's primary reader — the same "who's the
primary reader" test ADR-021 already applies to this repo's own files.

| Primary reader | Language | Examples |
|---|---|---|
| Human (operator / user) | **Japanese** | operator guides, READMEs, requirements docs, procedures / runbooks |
| AI (model / harness) | **English-based** | CLAUDE.md, code docstrings, prompts to (sub)agents, harness & config |

**English-based, not English-only.** Inside an AI-facing document, a passage
whose primary reader is a human operator (a safety-norm audit note, an embedded
procedure) may be written in Japanese — the same test, applied per passage. This
is the nuance ADR-021 adopted for `rules/`.

## Scope

- This is the **general default for documents you author in a project.**
- The config foundations already fix a per-category mapping (ADR-003 / ADR-021:
  `rules/` `agents/` → English-based, `commands/` → Japanese). Those dirs are
  spread across claude-core / -engineering / -work-agent (ADR-023); defer to the
  ADRs there.

## Relation (cross-reference, don't restate)

- Conversation language — reply to the user in Japanese: `collaboration-style.md`
  "Language", memory [[respond-in-japanese]]. That rule is about *the reply*; this
  one is about *documents*.
- [ADR-003](../docs/adr/003-language-policy.md) / [ADR-021](../docs/adr/021-language-policy-update.md)
  — the audience-based principle this rule generalizes, and the per-category
  mapping for this repo.
- Content norms are language-independent: never write secrets into any document
  (`secret-hygiene.md`); never report unverified claims as done
  (`collaboration-style.md` "Close the loop"; `safety-irreversible.md` "Verified,
  not assumed").
