# Spec: Registration

## Overview
Wire up the existing `/register` route to actually create a new user account. Today the route only renders `register.html` on GET and the form has nowhere to post to. This step introduces password hashing, a parameterized insert into the `users` table, server-side validation, and a logged-in session via `flask.session`, so the user lands on a real (currently stub) `/profile` page after signing up.

## Depends on
- Step 1 — Database Setup (the `users` table must exist)

## Routes
- `GET /register` — renders `register.html` with an empty form — public
- `POST /register` — validates input, hashes the password, inserts a row into `users`, sets `session["user_id"]`, then redirects to `/profile` — public

No new routes; the existing `GET /register` stub is upgraded in place.

## Database changes
No schema changes. The `users` table from Step 1 already has the columns we need: `id`, `name`, `email`, `password_hash`, `created_at`.

A new helper in `database/db.py` is added (see Files to change) — it does inserts/lookups against the existing `users` table only.

## Templates
- **Modify:** `templates/register.html`
  - Replace the hardcoded `action="/register"` with `action="{{ url_for('register') }}"`
  - Keep the existing form layout, error block, and CSS classes unchanged

## Files to change
- `app.py`
  - Add `POST` handling to `/register`
  - Add a `SECRET_KEY` to the Flask app (required for `flask.session` to work)
  - Add `from flask import ..., redirect, session, request`
  - Add `from werkzeug.security import generate_password_hash, check_password_hash` (Step 3 needs `check_password_hash` too — safe to import now)
- `database/db.py`
  - Add `get_user_by_email(email)` helper
  - Add `create_user(name, email, password_hash)` helper
- `templates/register.html`
  - Swap the hardcoded form action for `url_for`

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security` is already in use by `seed_db()`.

## Rules for implementation
- No SQLAlchemy or any ORM — use raw `sqlite3` with the existing `get_db()` helper
- Parameterized queries only — every `?` placeholder, never f-strings in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` before storage
- Email compared case-insensitively (lowercase both sides before query/insert) to avoid `Foo@x.com` and `foo@x.com` being treated as different accounts
- Validation must happen server-side even though the form has `required` attributes:
  - All three fields (`name`, `email`, `password`) present and non-empty after `.strip()`
  - `name` ≤ 100 chars
  - `email` matches a basic email shape (contains exactly one `@` with non-empty parts on each side)
  - `password` ≥ 8 chars
- On validation failure: re-render `register.html` with the submitted values and an error message — do NOT redirect
- On duplicate email: re-render with the error `"An account with that email already exists."`
- On success: set `session["user_id"]` to the new row's id, then `redirect(url_for("profile"))`
- Use CSS variables in any new styles — never hardcode hex values
- All templates must extend `base.html` (already true for `register.html`)

## Definition of done
- [ ] `GET /register` still renders the form
- [ ] `POST /register` with all valid fields creates a new `users` row and redirects to `/profile`
- [ ] The `password_hash` column stores a `werkzeug` hash, not plaintext
- [ ] Submitting with an email that already exists shows the duplicate error and does NOT create a row
- [ ] Submitting with a password shorter than 8 chars shows a validation error and does NOT create a row
- [ ] Submitting with an empty `name`, `email`, or `password` shows a validation error and does NOT create a row
- [ ] After a successful registration, `session["user_id"]` is set (verify by visiting `/profile` and seeing the stub, not a redirect)
- [ ] App starts without errors and the demo user from Step 1 still exists
- [ ] No new pip packages added
