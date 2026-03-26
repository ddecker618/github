# Personnel Data Removal Tool (Practical MVP)

This folder contains a practical implementation blueprint and starter code for a local-first
personnel data removal tool using Python, Playwright, and SQLite.

## Scope

The MVP focuses on:
1. Discovering likely listings for a person.
2. Running broker-specific opt-out workflows.
3. Tracking lifecycle state for each broker/listing.
4. Assisting with email confirmation links.
5. Providing a simple local dashboard view.

## Architecture

### 1) Discovery module

Use either:
- search APIs (preferred for reliability and ToS alignment), or
- browser automation for manual query execution.

Queries:
- `"First Last"`
- `"Street Address, City, State"`
- `"First Last" "City" "State"`

Discovery output should normalize into candidate records:
- `domain`
- `search_query`
- `listing_url`
- `confidence`
- `raw_snippet`

### 2) Broker rules

Each broker has one YAML file with:
- `domain`
- `search_url_pattern`
- `opt_out_url`
- `selectors`
- `form_fields`
- flags: `needs_email_confirmation`, `has_captcha`, `needs_exact_listing_url`

See `rules/example_broker.yaml` for schema style.

### 3) Workflow runner (Playwright)

Per broker:
1. Open search page or direct opt-out URL.
2. Resolve the target listing URL.
3. Fill and submit forms when deterministic.
4. Pause for manual CAPTCHA if flagged.
5. Resume and record status.

Recommended status states:
- `discovered`
- `submitted`
- `awaiting_email`
- `confirmed`
- `verified_removed`
- `failed`

### 4) Email confirmation helper

Connect via IMAP to a dedicated mailbox.
- Poll for broker messages from known senders/domains.
- Extract and validate confirmation links.
- Open link automatically only if host matches allowlist.

### 5) Tracker dashboard

A local UI can start as CLI + static HTML export.

Columns:
- domain
- listing_found
- removal_submitted
- awaiting_email_click
- verified
- recheck_date
- notes

## Safety and legal notes

- Respect site Terms of Service and anti-abuse policies.
- Use conservative rate limiting and randomized delays.
- Keep local encrypted storage for PII and audit logs.
- Require explicit operator confirmation before destructive actions.

## Suggested project layout

```
personnel_scrubber/
  README.md
  tracker.py
  rules/
    example_broker.yaml
```

`tracker.py` includes SQLite schema helpers for request lifecycle tracking.


## Download and run

### 1) Get the code

```bash
git clone <your-repo-url>
cd github
```

### 2) Initialize a local tracker DB

```bash
python -m personnel_scrubber.cli --db scrubber.db init-db
# or: python personnel_scrubber/cli.py --db scrubber.db init-db
```

### 3) Add a removal row

```bash
python -m personnel_scrubber.cli --db scrubber.db add   --domain examplebroker.com   --listing-url https://examplebroker.com/profile/abc   --listing-found   --submitted   --awaiting-email   --recheck-date 2026-04-15   --notes "Submitted and waiting for confirmation email"
```

### 4) List tracked rows

```bash
python -m personnel_scrubber.cli --db scrubber.db list
# or: python personnel_scrubber/cli.py --db scrubber.db list
```

## What this gives you today

- Working local persistence for request tracking.
- An editable per-broker rule format in YAML.
- A CLI workflow for init/add/list while Playwright + email automation is added next.
