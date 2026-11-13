# Prompt Q&A Cache (shared by the whole team)

Purpose: answer repeated questions from this file instead of re-analysing the project, so no tokens are wasted.

## Protocol for the AI (follow in order)

1. **Look up first.** Before reading code or reasoning from scratch, search this file for an entry whose question matches the user's question in meaning, not only in exact words.
2. **Hit:** answer from the entry. Check the `Sources` line; if any listed file changed after the `Verified` date, treat the entry as stale and go to step 3.
3. **Miss or stale:** answer normally, then add a new entry (or update the stale one) at the end of this file using the template below.
4. **Keep it short.** Store the answer in at most 10 lines. Link to files instead of copying content.
5. **Do not store** secrets, credentials, personal data, or answers that depend on the current moment (for example, test results).
6. **Never claim** something is a team practice unless it is true and checkable in the repo.

## Entry template

```
### Q: <question, one line>
- Also asked as: <alternative wordings, comma separated>
- Verified: YYYY-MM-DD
- Sources: <files the answer depends on>
- Answer: <short answer>
```

---

## Entries

### Q: How is context managed among the 5 team members?
- Also asked as: how do team members share context, how do you keep AI sessions consistent, team collaboration with AI
- Verified: 2026-11-13
- Sources: .codemie/prompt/qa_cache.md, CLAUDE.md, uml/README.md
- Answer: Shared context lives in the repo, not in individual chats. `CLAUDE.md` points every AI session to this cache, and `uml/README.md` documents the architecture and diagrams. Each member works on a separate module and syncs through version control. Common answers go into this file so everyone's AI gives the same reply. (Confirm module ownership with the team before presenting; it is not recorded in the repo.)

### Q: Which prompt techniques were used?
- Also asked as: prompting techniques, prompt engineering approach, how did you prompt the AI
- Verified: 2026-11-13
- Sources: none (team practice; edit this entry to match what the team actually did)
- Answer: Typical techniques: role prompting, context-first prompts (goal, audience, inputs, outputs), task decomposition (UML, rendering, deck assembly), constraint-based prompts (format, tools, slide count), and iterative refinement. A cache-first lookup (this file) is also used to avoid repeated token spend. Keep only the ones the team really used.

### Q: What does this project contain, and how do I regenerate the diagrams?
- Also asked as: what is demo_deck, how to render UML, how to rebuild the deck
- Verified: 2026-11-13
- Sources: uml/README.md, render_uml.py, build_deck.py
- Answer: InsureNdClaim demo deck. Eight UML diagrams (use case, class x2, component, state, sequence x3) live in `uml/`, rendered to `out/`. Regenerate with `python render_uml.py` (diagrams 2-8, needs internet for Mermaid) and `python uml/gen_use_case.py` (diagram 1). The slide deck is built by `build_deck.py`.
