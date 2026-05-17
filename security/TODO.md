# Security / Auth — To Do

## Setup (do first)
- [ ] Copy `.env.example` (project root) to `.env` and fill in SMTP credentials
- [ ] Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` in your shell env before running
- [ ] (Optional) Install Mailhog for local testing without sending real emails
      https://github.com/mailhog/MailHog — run it, then use `SMTP_HOST=localhost SMTP_PORT=1025`

## Test the flow end-to-end
- [ ] Run `python main.py` — login screen should appear (not the old menu)
- [ ] Submit with no SMTP env vars — confirm red "SMTP NOT CONFIGURED" error shows
- [ ] Submit an invalid email (e.g. "abc") — confirm "INVALID EMAIL ADDRESS" error
- [ ] Submit a valid email with real/dev SMTP — confirm "awaiting auth" screen appears
- [ ] Click the link in the email — browser should show green success page
- [ ] Game should automatically advance to the main menu
- [ ] Confirm HUD top-right shows your email (truncated) in blue
- [ ] Press ESC on the awaiting screen — confirm it returns to login

## Optional / Nice to have
- [ ] Persist the logged-in session to disk so users don't re-login on every launch
      (save email to a local file, e.g. `security/session.json`, on successful auth)
- [ ] Add a "log out" option (e.g. from the pause menu)
- [ ] Show a spinner or animated dots on the awaiting screen while polling
- [ ] Rate-limit login attempts (e.g. max 3 per minute) to prevent email spam
- [ ] Tie high scores to the logged-in email so each player has their own leaderboard
