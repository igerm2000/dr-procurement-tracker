# DR Procurement Tracker

Watches the Dominican Republic government procurement portal
(comprasdominicana.gob.do) for new processes matching your keywords,
and emails you about them. Runs automatically in the cloud — once set
up, you never need to open a computer for this.

This is a proof of concept. The matching/filtering logic has been
tested against real live data from the portal. The scraper itself
(the part that fetches from the live site on a schedule) has not yet
been run for real, since that only happens once this is set up on
GitHub. The first live run is the real test — see "First run checks"
at the bottom.

## What it does

- Every 4 hours, checks the portal for new processes
- Emails you immediately when a new one matches your keywords, is
  actually "Published" status, and has a real bid window (not a
  process quietly awarded already and posted for 3 minutes to check
  a compliance box)
- Sends one summary email at the end of each day

## One-time setup

### 1. Create a Gmail "app password"

This lets the tracker send email as you, without using your real
Gmail password.

1. Go to https://myaccount.google.com/apppasswords
2. Sign in if asked
3. Under "App name", type "DR Tracker" and click Create
4. Google shows you a 16-letter code — copy it somewhere safe. You
   won't be able to see it again (you can always make a new one).

### 2. Create the GitHub repository

1. Go to https://github.com/new
2. Name it something like `dr-procurement-tracker`
3. Set it to **Private**
4. Click "Create repository"

### 3. Upload these files

1. On your new repo's page, click "Add file" → "Upload files"
2. Drag in every file from this folder, **keeping the folder
   structure** (the `.github/workflows` folder must stay a folder —
   don't flatten it)
3. Click "Commit changes"

### 4. Add your secrets

Secrets are where your Gmail password and address are stored safely
— never visible in the code itself.

1. In your repo, click "Settings" (top right of the repo page)
2. In the left sidebar: "Secrets and variables" → "Actions"
3. Click "New repository secret" three times, adding:

   | Name | Value |
   |---|---|
   | `GMAIL_ADDRESS` | your Gmail address |
   | `GMAIL_APP_PASSWORD` | the 16-letter code from step 1 |
   | `ALERT_TO_EMAIL` | the email address you want alerts sent to (can be the same Gmail address) |

### 5. Turn it on

1. Click the "Actions" tab in your repo
2. If prompted, click "I understand my workflows, go ahead and enable them"
3. You should see two workflows listed: "Check for new procurement
   processes" and "Send daily digest" — these will now run
   automatically on schedule

### 6. Test it manually (recommended before waiting for the schedule)

1. In the "Actions" tab, click "Check for new procurement processes"
2. Click "Run workflow" → "Run workflow" (green button)
3. Wait ~30 seconds, refresh, click into the run to see the log
4. If it says "Fetched N processes from the portal" — the scraper
   works. If N new matches turned up, check your inbox.

## Changing your keywords

Open `config.yaml` in the repo (click it, then the pencil/edit icon),
edit the `keywords` list, commit the change. Takes effect on the next
scheduled check — no need to touch anything else.

## Changing how often it checks

Open `.github/workflows/check.yml`, find the line:
```
- cron: '0 */4 * * *'
```
The `*/4` means "every 4 hours". Change to `*/2` for every 2 hours,
etc.

## First run checks

Since the live scraper hasn't run against the real site yet, watch
the first few runs' logs (Actions tab → click a run → click "check")
for two things:
1. "Fetched N processes" — if N is 0 or very low, the portal's page
   layout may have changed and the scraper needs adjusting
2. Any red/failed steps — usually means a secret is misspelled

If either happens, come back to this chat with a screenshot of the
Actions log and we'll fix it together.
