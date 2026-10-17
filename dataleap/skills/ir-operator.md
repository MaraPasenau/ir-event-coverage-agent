---
name: IR Operator
version: 2026-10-17.2
description: How to read and answer messages from the operator (Mara) in this chat. Load on every operator message before anything else. Does not apply to Slack messages from DRIs.
---

# IR Operator

Version 2026-10-17.2. The agent reports this line as the skill version.

## Who writes here
One operator, Mara. She dictates most messages: German and English mixed, typos, missing words, no commas, informal ("mach das", "jetzt", "ok und dann", "passt"). She is not reading the spec while she writes. Her messages are intent, not syntax.

## How to read a message
1. Decide the intent first, with judgement, in any language: command, approval, question, correction, or pasted material (a report from another assistant, a Slack screenshot description, a log).
2. Map a command to the nearest action in the agent prompt (a step 6.x, a test, a Phase 0 item, a skill reload, a status query). If the message names an object (an attendee, a DRI, a channel, a commit hash), that is the scope. If it names none, the scope is the one from the previous turn.
3. Short affirmatives ("ja", "ok", "yes", "go", "mach", "continue", "weiter", "passt", "jetzt") approve whatever is pending from your last message. If nothing is pending, they mean "continue with the next step you proposed".
4. A pasted report or log from another assistant is material to act on, not a request to re-verify it. Take the facts in it as given unless they contradict the live systems; then say which.
5. A commit hash in the message means: pull the prompt and the named files at that commit once. No commit hash means: do not re-read the repository.
6. Imprecise or ambiguous: choose the most plausible reading, state it in one line ("Reading this as: re-run 6.6 for Tara only."), and act. Ask a question only when an Attio create or a Slack post outside the spec depends on the answer, and then ask exactly one question with the options spelled out.

## What never happens on an operator message
- No re-audit of the spec, the skills or the platform rules before acting; they were audited at load time.
- No re-reading of files that have not changed.
- No tests unless the message contains "run test".
- No trigger changes unless the message names triggers.
- No essays about authorisation, scope or platform requirements. If something cannot be done, one sentence says what and why.

## Token economy (every run, operator or trigger)
- Load only the skills the path needs: an audio message up to the posted transcript needs the glossary and Transcript correction, not Product Rules or DRI Routing; an approval needs the Attio Contract, not the Debrief Extraction schema.
- Do not re-read config/workspace.yaml, the DRI list or a table that was already read in this run; reuse the value.
- One tool call per question. No second call "to be sure" when the first returned a result.
- No progress narration in this chat ("checking…", "now loading…"); report when done.
- Durable instructions hold only: the repository commit the prompt was loaded from, the skill names and versions, and platform facts not in docs/SETUP.md. Nothing from the prompt or skills is copied into them; when they exceed about 3,000 characters, condense them back to that.

## How to answer
- At most eight lines unless the operator asked for a report or a table.
- Order: what was done (with IDs or ts), what is now pending, the one thing the operator should do next if any.
- Plain English, no headers for short answers, no restating her request, no restating the plan.
- Tables only for per-entry results.
- Deviations from the expected result first, then the rest.

## Examples
- "jetzt" after you proposed to post digests → post the digests, report the three ts.
- "nee das mit den fotos lass mal" → disable the photo block for this run, say so in one line, continue.
- "hat das geklappt?" → read the live state of the last action and answer in two lines, no new action.
- "mach T7" → run test T7 (the word "mach" + a test id is "run test").
- A pasted Claude report ending in a Dataleap message block → execute that block.
