# Personal Agentic AI Task Automation MVP

A lightweight Python implementation of a personal task-automation agent inspired
by the Agentic AI concept demonstrated by OpenClaw. This project does **not**
install or use OpenClaw.

The bot accepts English or Korean natural-language requests through Discord and
invokes only explicitly allowlisted tools.

## Project structure

```text
Agentic AI/
├── agent/                 # Intent routing and workflow controller
├── bot/                   # Discord interface
├── config/                # Environment-based application settings
├── deploy/                # macOS launchd service definition
├── docs/
│   ├── final-report/      # Submission-ready DOCX and PDF
│   ├── proposal/          # Original project proposal
│   └── IMPLEMENTATION_SPEC.md
├── logs/                  # Runtime logs
├── scripts/report/        # Final-report generator and visual assets
├── security/              # Access and prompt-injection guards
├── storage/               # Generated local reports
├── tests/                 # Automated test suite
├── tools/                 # OCR, Gmail, Sheets, and Calendar tools
├── main.py                # Application entry point
└── README.md
```

Secrets and machine-specific OAuth files remain in the project root because the
runtime loads them from there. They are excluded from Git and must not be
included in a submission archive.

## MVP features

- Discord owner-only command interface
- Recursive PDF search inside a configured OneDrive root
- Ambiguous-file confirmation through `select N`
- Korean/English OCR with LaTeX math, Markdown tables, figure descriptions, and
  page boundaries
- Atomic `<original>_ag.txt` creation beside the PDF
- Strict no-overwrite behavior
- Gmail review of the most recent 48 hours
- Conservative promotional-email trashing followed by a Discord report
- Email reply drafts that require `send <ID>` confirmation
- Read-only Google Sheets task ingestion
- Read-only Google Calendar lookup
- English daily brief generation
- Local `storage/important_emails.md` report for Gmail organization
- Daily Briefing delivered directly as Discord chat messages
- Prompt-injection isolation and deterministic tool permissions

## Safety model

The LLM cannot run shell commands or directly invoke tools. It may only produce a
validated command or classification. Python code then enforces:

1. The configured Discord owner ID.
2. The configured OneDrive root.
3. PDF-only OCR input.
4. Atomic creation of `_ag.txt` files with no overwrite.
5. Explicit confirmation before sending email.
6. Conservative rules that protect personal, work, account, payment, receipt,
   authentication, security, legal, and ambiguous email from automatic trashing.
7. Untrusted-content delimiters for PDFs, email, Sheets, and Calendar data.

Discord attachments are rejected; files are exchanged only through OneDrive.

## Setup

Requires Python 3.9 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

- `DISCORD_BOT_TOKEN`
- `DISCORD_ALLOWED_USER_ID`
- `OPENAI_API_KEY`

Enable **Message Content Intent** for the Discord bot in the Discord Developer
Portal.

For Gmail, Sheets, and Calendar, create a Google Cloud OAuth **Desktop app**,
enable the Gmail, Google Sheets, and Google Calendar APIs, and save the downloaded
client file as `credentials.json`. The first Google-tool request opens a browser
for OAuth and creates the ignored `token.json`.

Run:

```bash
python main.py
```

## 24/7 macOS service

The included launch agent starts the bot at login and restarts it after a crash:

```bash
mkdir -p logs
cp deploy/com.example.agentic-ai-bot.plist \
  ~/Library/LaunchAgents/com.example.agentic-ai-bot.plist
launchctl bootstrap gui/$(id -u) \
  ~/Library/LaunchAgents/com.example.agentic-ai-bot.plist
launchctl kickstart -k gui/$(id -u)/com.example.agentic-ai-bot
```

Replace every `PATH_TO_PROJECT` and `YOUR_USERNAME` placeholder in the plist
before copying it.

Logs:

```text
logs/bot.stdout.log
logs/bot.stderr.log
```

The Mac must remain powered on, connected to the internet, logged in, and awake.
`launchd` cannot answer Discord messages while macOS is asleep.

## Example Discord commands

```text
OCR pages 1-5 of modern control systems
OCR the robot engineering exam PDF
Organize my emails
last 48 hours
Organize my emails from 2026-06-01 to 2026-06-20
Draft a reply to the email from Alice
send a1b2c3
cancel a1b2c3
Show my calendar
Create my daily briefing
```

Gmail organization requires an explicit date range. If the first command omits
one, the bot asks for it and performs no Gmail changes until the owner replies
with a range such as `last 48 hours`, `last 7 days`, or
`2026-06-01 to 2026-06-20`.

## OCR output

For `lecture12.pdf`, the output is `lecture12_ag.txt` in the same directory.
Existing output causes the operation to stop; it is never replaced.
The selected OneDrive PDF must be downloaded locally; online-only placeholders
produce a safe Discord instruction to download the file first.

```text
# OCR TRANSCRIPTION
Source: lecture12.pdf
Pages: 1-3 of 20
Format: UTF-8, LaTeX math, Markdown tables, figure descriptions

--- Page 1 ---

...
```

## Cost and demonstration controls

- `OCR_MAX_PAGES_PER_RUN=20` prevents accidental large OCR jobs.
- `OCR_SEARCH_MAX_DEPTH=4` avoids expensive traversal of unrelated deep
  OneDrive trees.
- Use a small page range for the under-one-minute demonstration.
- Low-cost model defaults are configurable in `.env`.
- OCR runs one API request per page, making scope and cost visible.

## Tests

```bash
pytest -q
```

The tests cover owner restriction, filesystem escape prevention, `_ag.txt`
naming, atomic no-overwrite behavior, and task completion filtering.
