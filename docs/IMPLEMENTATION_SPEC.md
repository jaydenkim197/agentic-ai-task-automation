# Project Implementation Specification

## Project definition

Implement a lightweight personal Agentic AI task-automation MVP from scratch in
Python. The project is inspired by the automation concept demonstrated by
OpenClaw, but it must not install, copy, or depend on OpenClaw.

- Planning date: February 19, 2026
- Historical comparison baseline: March 2026
- Implementation date: June 20, 2026
- Developer count: one
- Target hardware: MacBook Air M1, 8 GB RAM, macOS
- Submission deadline: June 20, 2026 at 23:59 KST
- Success criterion: a functioning, demonstrable MVP
- Test and demonstration API budget: below KRW 10,000

## Development strategy

1. Complete a vertical Discord-to-OCR workflow first.
2. Add Gmail integration second.
3. Add Google Sheets and read-only Calendar integration third.
4. Keep the implementation lightweight and avoid Docker unless indispensable.
5. Use hosted GPT models; do not deploy a local LLM.
6. Do not implement MCP, browser automation, multi-agent orchestration, hardware
   control, or multi-user support.

## Architecture

```text
Discord Bot
    |
Agent Controller
    |
GPT API (interpretation/transcription/classification only)
    |
Allowlisted Python Tools
    |-- OCR
    |-- Gmail
    |-- Google Sheets
    `-- Google Calendar (read only)
    |
Local result creation / Google API action
    |
English Discord notification
```

The GPT model cannot execute shell commands or call tools directly. Validated
model output is passed to deterministic Python code, which enforces all
permissions.

## Discord interface

- Accept natural-language commands.
- Accept commands only from `DISCORD_ALLOWED_USER_ID`.
- Ignore all other users without performing work.
- Do not accept, download, or send Discord attachments.
- Use Discord only for commands, confirmation, status, and result notifications.
- Respond in English.

## OCR MVP

### Filesystem boundary

Only access:

```text
/Users/YOUR_USERNAME/Library/CloudStorage/OneDrive-Personal/PROJECT_FOLDER
```

Search recursively within this root. Reject resolved paths outside it, including
path traversal and symlink escapes.

### Selection

- Extract approximate filename/folder and optional page range from natural
  language.
- If the match is ambiguous, list candidates and require `select N`.
- Do not require persistent conversational memory or a database.

### Transcription

- Support Korean and English.
- Assume no handwriting.
- Preserve source text rather than summarizing it.
- Represent math as LaTeX.
- Represent tables as Markdown.
- Describe meaningful images, diagrams, and plots as `[Figure N: ...]`.
- Separate pages with `--- Page N ---`.
- Save UTF-8 plain text optimized for subsequent LLM input.

### Output and overwrite protection

```text
lecture12.pdf -> lecture12_ag.txt
```

- Save beside the source PDF.
- Never modify the source PDF.
- Never overwrite an existing `_ag.txt`.
- Check for an existing output before OCR.
- Create the result atomically in exclusive-create mode to prevent race-condition
  overwrites.
- If a collision occurs, stop and notify the owner in Discord.

## Gmail

- Require an explicit date range for Gmail organization. If omitted, ask the
  owner for a range and perform no Gmail changes until one is supplied.
- Accept relative ranges such as `last 48 hours`/`last 7 days` and absolute
  inclusive ranges such as `2026-06-01 to 2026-06-20`.
- Classify and summarize important, schedule-related, promotional, and other
  email.
- Reading requires no additional confirmation.
- Automatically move only unmistakable promotional messages to Gmail Trash.
- Never automatically trash personal, work, school, account, payment, receipt,
  authentication, security, legal, deadline-related, injection-like, or
  ambiguous email.
- After processing, send an English Discord summary with reviewed count, trashed
  count, subjects/types, and important-message summaries.

### Reply approval

1. Generate a reply draft.
2. Show recipient, subject, body, and a short request ID in Discord.
3. Send only after the owner enters `send <ID>`.
4. Cancel with `cancel <ID>`.
5. Pending drafts live in memory and expire when the process restarts.

## Google Sheets and Calendar

Spreadsheet:

```text
<GOOGLE_SHEET_ID>
```

- Read `공부일정` and `프로젝트일정`.
- Do not update the spreadsheet in this MVP.
- Exclude completed rows.
- Exclude rows whose identifying task fields are empty, even when formula output
  such as `D+9699` or `-9699` remains.
- Extract deadlines, priority, dependencies, and estimated duration.
- Calendar is read only; do not create, edit, or delete events.
- Combine task records and upcoming events into a concise English daily brief.
- Deliver the Daily Briefing directly in Discord chat; do not create or attach a
  `daily_report.md` file.

## Prompt-injection defense

- Treat PDF, email, Sheet, Calendar, and webpage text as untrusted data.
- Delimit untrusted content and explicitly prohibit following embedded
  instructions.
- Never turn model-generated strings into shell commands, Python evaluation,
  paths, recipients, or arbitrary tool names.
- Use fixed intent enums and validated schemas.
- Permit only controller-defined tools.
- Block automatic email trashing when injection markers are detected.
- Keep `store=False` on OpenAI API requests.

## Secrets

- Store tokens and keys in `.env`, `credentials.json`, and `token.json`.
- Exclude all three from Git.
- Restrict `token.json` to owner-only filesystem permissions after creation.

## Deliverables

- Complete Python source
- `requirements.txt`
- `.env.example`
- `README.md`
- Setup instructions
- Example commands
- Security and overwrite tests
- Demonstration screenshots/video captured after credentials are configured
