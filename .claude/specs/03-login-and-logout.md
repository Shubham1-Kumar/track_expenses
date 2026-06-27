# Spec: Login and Logout

## Overview
Wire up the existing `/login` route to authenticate an existing user by email + password, and replace the `/logout` stub with a route that clears the session and redirects back to a safe landing surface. After Step 2 (Registration) already creates a session on signup, this step gives users a way back in once they have left the browser, and a way to sign out cleanly. Without `/login` and `/logout`, returning visitors cannot reach their profile or expenses, and there is no way to end a session — both are blockers for every subsequent logged-in step.

## Depends on
- Step 1 — Database Setup (`users` table exists with `password_hash` column)
- Step 2 — Registration (`get_user_by_email` and `create_user` helpers already exist; `/register` already sets `session["user_id"]`)

## Routes
- `GET /login` — renders `login.html` with an empty form — public
- `POST /login` — validates input, looks up user by email, verifies password with `werkzeug.security.check_password_hash`, sets `session["user_id"]` on success, then redirects to `/profile` — public
- `GET /logout` — clears the session (`session.clear()`), then redirects to `/` — public (idempotent — safe even if no one is logged in)

No new routes; the existing `GET /login` and `GET /logout` stubs are upgraded in place.

## Database changes
No schema changes. Uses the existing `users` table from Step 1 and the existing `get_user_by_email(email)` helper from Step 2.

## Templates
- **Modify:** `templates/login.html`
  - Replace the hardcoded `action="/login"` with `action="{{ url_for('login') }}"`
  - Keep the existing form layout, error block, and CSS classes unchanged
  - The form must have name attributes `email` and `password` (already true)
- **Create:** none
- **Modify:** none of the other templates — `/profile` remains a stub at this stage

## Files to change
- `app.py`
  - Upgrade `/login` to handle `POST`:
    - Read `email` and `password` from the form
    - Look up the user via `get_user_by_email(email)`
    - If no user, or `check_password_hash` fails, re-render `login.html` with a generic error (do not reveal which field was wrong) and the submitted email
    - On success: set `session["user_id"]` to the user's `id`, then `redirect(url_for("profile"))`
  - Replace the `/logout` stub: clear the session with `session.clear()` and `redirect(url_for("landing"))`
  - Imports: `check_password_hash` is already imported from Step 2; `redirect`, `session`, `url_for` already imported
- `templates/login.html`
  - Swap the hardcoded form action for `url_for('login')`

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already imported (used by `/register` indirectly and ready for `/login`).

## Rules for implementation
- No SQLAlchemy or any ORM — use raw `sqlite3` via the existing `get_db()` helper
- Parameterized queries only — every `?` placeholder, never f-strings in SQL (the existing `get_user_by_email` already does this; no new queries needed in this step)
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Email compared case-insensitively (the existing `get_user_by_email` already lowercases before lookup — no extra work in the route)
- Server-side validation on `/login` POST:
  - Both `email` and `password` present and non-empty after `.strip()`
  - If either is missing, re-render with an error and the submitted email
- Authentication failure must use a single generic error message (e.g. `"Invalid email or password."`) — never say "email not found" vs "wrong password" separately, to avoid account enumeration
- On success: set `session["user_id"]` to the user's `id`, then `redirect(url_for("profile"))`
- On failure: re-render `login.html` with the submitted email (never the password) and the error message — do NOT redirect
- `/logout` must call `session.clear()` (not just `session.pop`) so any future session keys are wiped, and must redirect to `/` — never render the landing template directly
- `/logout` must be safe to call when no one is logged in — Flask's `session.clear()` is a no-op on an empty session, so no guard is needed
- Use CSS variables in any new styles — never hardcode hex values
- All templates must extend `base.html` (already true for `login.html`)

## Definition of done
- [ ] `GET /login` still renders the form
- [ ] `POST /login` with a valid email + password sets `session["user_id"]` and redirects to `/profile`
- [ ] `POST /login` with an unknown email shows the generic error and does NOT set a session
- [ ] `POST /login` with a known email but wrong password shows the generic error and does NOT set a session
- [ ] `POST /login` with an empty email or empty password shows a validation error and does NOT set a session
- [ ] On any login failure the form is re-rendered with the submitted email pre-filled (never the password)
- [ ] The same generic error message is used for "unknown email" and "wrong password" (no account enumeration)
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] `GET /logout` while not logged in still redirects to `/` without an error
- [ ] After logging out, visiting `/profile` does not keep the previous user logged in (profile stub still shows; that is fine — the session key is gone)
- [ ] App starts without errors and the demo user from Step 1 can still log in with `demo@spendly.com` / `demo123`
- [ ] No new pip packages added