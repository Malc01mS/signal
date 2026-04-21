# Signal

Weekly intelligence brief. Runs every Sunday at 7:00 AM Pacific.

## Setup

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in keys
3. Verify sender email at [resend.com](https://resend.com)
4. `python main.py` to run the first issue

## Keys needed

| Key | Where to get it |
|-----|----------------|
| `ANTHROPIC_API_KEY` | claude.ai/settings |
| `RESEND_API_KEY` | resend.com (free tier) |
| `GITHUB_TOKEN` | github.com/settings/tokens (repo scope) |
| `GITHUB_REPO` | `Malc01mS/signal` |
| `GITHUB_PAGES_URL` | `https://malc01ms.github.io/signal` |
| `RECIPIENT_EMAIL` | Your email address |
| `SENDER_EMAIL` | Must be verified in Resend |

## Tuning

- **Profile & pillars** — `config.py`
- **Scoring prompts** — `scorer.py` (primary tuning surface)
- **Sources** — `config.py` → `RSS_SOURCES`, `SEMANTIC_SCHOLAR_KEYWORDS`

## Logging feedback

```bash
python -c "from feedback import append_feedback; append_feedback(input('Feedback: '))"
```

## Scheduling (cron)

```cron
0 7 * * 0 cd /path/to/signal && /path/to/.venv/bin/python main.py >> logs/signal.log 2>&1
```

## Cost

~$0.15–0.35/run on Claude API (claude-sonnet-4-5).
