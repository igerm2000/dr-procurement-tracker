# DR Procurement Tracker (v2)

Watches the Dominican Republic government procurement portal
(comprasdominicana.gob.do) for new processes matching your keywords,
and emails you one summary a day. Runs automatically in the cloud —
once set up, you never need to open a computer for this.

## What it does

- Checks the portal every 15 minutes, Monday–Friday, 8:00 AM–6:30 PM
  Santo Domingo time (matches when institutions actually publish —
  nothing runs overnight, on weekends, or wastes compute)
- Sends exactly **one email per day**, at 6:30 PM, listing everything
  new that day — or clearly saying "no new processes" if there was
  nothing
- Automatically skips anything that looks like a sham posting (a
  process closed for bids within 2 hours of being published — usually
  an already-decided award posted briefly to check a compliance box)

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

If you already made one for an earlier version of this, you can
either delete it and make a fresh one, or just delete everything
inside it before uploading these files — either way works, as long as
you end up with only the files from this v2 package in the repo.

1. Go to https://github.com/new
2. Name it something like `dr-procurement-tracker`
3. Set it to **Private**
4. Click "Create repository"

### 3. Upload every file in this folder

1. On your repo's page, click "Add file" → "Upload files"
2. Drag in **every file and folder from this v2 package** — including
   the `.github` folder. On a Mac, that folder may be hidden by
   Finder by default; if you don't see it when dragging, press
   **Cmd+Shift+.** in Finder first to reveal hidden files, then try
   again.
3. Click "Commit changes"
4. Once uploaded, check that your repo shows a `.github/workflows`
   folder containing `daily.yml` — if it's missing, the drag-and-drop
   silently skipped it and you'll need to try again with hidden files
   visible.

### 4. Add your secrets

Secrets are where your Gmail address and password are stored safely
— never visible in the code itself. If you already added these for
an earlier version, they're still there and you can skip this step.

1. In your repo, click "Settings"
2. Left sidebar: "Secrets and variables" → "Actions"
3. Click "New repository secret" three times, adding:

   | Name | Value |
   |---|---|
   | `GMAIL_ADDRESS` | your Gmail address |
   | `GMAIL_APP_PASSWORD` | the 16-letter code from step 1 |
   | `ALERT_TO_EMAIL` | where you want alerts sent (can be the same Gmail address) |

### 5. Give it write permission

1. Still in Settings, click "Actions" → "General" in the left sidebar
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions", click "Save"

(If you already did this for an earlier version, it's already set —
skip this step.)

### 6. Turn it on

1. Click the "Actions" tab
2. If prompted, click the button to enable workflows
3. You should see one workflow: "Procurement tracker (weekday
   business-hours check, one daily email)"

### 7. Test it manually

1. Click into that workflow
2. Click "Run workflow" → "Run workflow" (green button)
3. Wait ~30 seconds, refresh, click into the run to see the log
4. Look for a line like "Fetched N processes from the portal" —
   that confirms it's working. It likely won't send an email on this
   test run (emails only go out during the 6:30 PM run), and that's
   expected — the goal here is just confirming there's no red X.

## Changing your keywords

Open `config.yaml` in the repo, click the pencil icon, edit the
`keywords` list, commit. Takes effect on the next scheduled check.

## What to expect day to day

Nothing. That's the point — check your inbox once a day, around
6:30 PM, for the summary. If several weekdays go by with no email at
all, something's wrong; check the Actions tab for red X's and come
back here with what you see.
