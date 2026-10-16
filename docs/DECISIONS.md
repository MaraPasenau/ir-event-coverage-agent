# Decisions and why

| # | Decision | Reason | Alternative rejected |
|---|---|---|---|
| 1 | Build the agent in Dataleap, not as a separate codebase | The task is to demo an agent on Dataleap; Dataleap provides harness, agent DB, triggers, approvals | Standalone Express/Postgres app (Victor's agent-studio pattern) — reference only |
| 2 | Rules live in four Dataleap skills, control flow in the agent prompt | Skills load only in the step that names them (token cost); rules change without touching the agent; mirrors Victor's skill-selector pattern in Dataleap's native format | One monolithic prompt |
| 3 | Private Attio workspace `b2v`, synthetic people, Testperson 1–3 as DRIs | Employer CRM and real investors must not enter a third-party demo | Connecting the company Attio |
| 4 | One shared coverage list for all events, linked via `coverage_event` | Attio allows the same record several times in one list; one list per event would duplicate ~90 fields per event | One list per event (Codex' original fixture) — kept as fallback |
| 5 | Tiers express potential and coverage priority, not eligibility; 50k DI ticket is a booster, unknown never disqualifies | Prospecting agent, not a qualification gate; founders without known investments are valid targets | Hard thresholds as core criteria |
| 6 | Identity resolution before any create; name-only matches create a flagged record with Conflict, never merge | Avoid duplicates and wrong merges; humans resolve conflicts in Attio | Merge on name |
| 7 | Every debrief creates an Attio note on the Person, independent of outcome or approval | Conversation history is relationship data; opportunities are a separate business object | Notes only on promotion |
| 8 | Approval by Slack reaction (:+1: / :-1:) from an eligible DRI's `slack_user_id`, bound to the proposal message ts | Dataleap documents reaction-added triggers as the approval pattern; any other reactor is logged and ignored | "approve" typed by anyone in the thread |
| 9 | Clay out of v1; LinkedIn enrichment and web search instead | Clay MCP needs a paid plan; Phase 0 showed Dataleap's LinkedIn tool enriches supplied URLs; synthetic people cannot be enriched by Clay anyway | Custom MCP server wrapping Clay |
| 10 | Luma via organiser CSV export, no live API | Luma API requires Luma Plus and a calendar-scoped key; CSV is the honest first release | Scraping the guest list |
| 11 | No photos in v1 | LinkedIn API does not expose third-party photos; `profile_photo_*` fields stay human-only | Downloading profile images |
| 12 | Voice only after the Slack-file → transcription chain is tested (T11) | Phase 0: both tools present but inactive and untested | Promising voice in the Loom |
| 13 | Write protocol: intent → execute → read-back → verified/mismatch; lookup by idempotency key after ambiguous responses | Caught a real mismatch in 6.1 (Attio truncates timestamps to ms) without replaying writes | Trusting the model's "done" |
| 14 | Cost mode for the remaining build: read-back once per entry, one summary row per step, lowest tool-capable model tier for research | 6.1 cost ~$7 on a $7.50/week plan | Full audit mode throughout |
| 15 | `responsible_dri` not written on investor entities in v1 | Select has no Testperson options and the API cannot add options; the DRI lives on the opportunity | Mapping test DRIs to real team codes |
| 16 | `#event-coverage` is a dedicated channel: only agent briefings and DRI replies. The new-message trigger fires on every message there by design; there is no irrelevant traffic to filter | Dataleap charges per run; a dedicated channel keeps trigger runs equal to real debriefs | Channel-wide trigger on a general channel with keyword filtering |
| 17 | Text and voice debriefs are equal inputs. Voice: transcribe → post transcript → ✅ by the DRI → extract. Text: extract directly. Transcript confirmation and proposal approval are separate gates | An unconfirmed transcript must never create CRM changes | Auto-extracting from the raw transcript |
