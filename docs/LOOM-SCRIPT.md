# Loom script (5–8 min) — draft

1. Problem (30 s): IR team at a VC goes to events; who to talk to, why, what happened, what next. Today: spreadsheets and memory.
2. Architecture (60 s): one Dataleap agent, four skills (Attio contract, product rules, DRI routing, debrief extraction), three integrations (Attio, Slack, LinkedIn + web search), one approval gate. Show the agent's Workflow view and the Skills list.
3. Live: import (6.1) — CSV in, Attio people and coverage entries out, read-back. Show Attio.
4. Live: research + tiering + routing (6.2–6.5) for three attendees. Show the three independent product tiers and the rule id behind the DRI.
5. Live: Slack briefing card. Then reply in the thread with a debrief. Show the note on the Person in Attio.
6. Live: proposal → :+1: → opportunity + task in Attio, confirmation in Slack. Then :-1: on a second one → nothing written, note kept.
7. One failure the agent handled: the timestamp-precision mismatch in 6.1 — caught by read-back, reconciled without replaying the write.
8. What's next (30 s): Luma API, Clay via MCP, voice debriefs, capacity rules, real event.
