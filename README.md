# Dhaaga CRM — Python / FastAPI edition

Digitising the tailor's register — a counter-side CRM for tailoring & boutique shops.
This is the Python rewrite of the original Node.js version: same features, same
database shape, rebuilt with FastAPI and split into small, single-purpose files.

## What it does

- Secure login for the shop account
- Save a customer's profile and measurements once, pull them up instantly by name or phone
- Create a new order (garment type, price, delivery date) against a customer
- Track an order through **Cut → Stitching → Ready → Delivered**
- Log advance/balance payments against each order
- Automatically flag a customer for follow-up the moment their order is marked Delivered
- See who referred whom, on each customer's profile
- Full UI in **English, Hindi, and Marathi**
- Responsive: phone-friendly tab bar, sidebar layout on tablet/desktop

## Project structure

```
dhaaga-python/
├── backend/
│   ├── main.py                  # creates the FastAPI app, wires everything together
│   ├── config.py                # settings (port, cookie names, prod flag)
│   ├── security.py              # password hashing + session store
│   ├── rate_limit.py            # login/API rate limiting
│   ├── deps.py                  # shared FastAPI dependencies (db, auth, csrf)
│   ├── validators.py            # phone/price/date/text validation
│   ├── models/                  # one small file per domain — request schemas
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── followup.py
│   ├── routes/                  # one small file per domain — API endpoints
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── customers.py
│   │   ├── orders.py
│   │   └── followups.py
│   └── database/
│       ├── schema.sql           # table definitions
│       ├── connection.py        # sqlite3 connection helper
│       └── seed.py              # first-run admin + sample data
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/                      # one small file per screen/concern
│       ├── i18n.js              # translations + language switcher
│       ├── api.js               # fetch wrapper, escaping, formatting
│       ├── auth.js              # login screen, session check, logout
│       ├── nav.js               # tab navigation, render dispatcher
│       ├── home.js               # dashboard + customer search/detail
│       ├── new_order.js           # new order form
│       ├── orders.js               # orders list + detail + payments
│       ├── followups.js             # follow-ups list
│       ├── profile.js                # account info, language, change password
│       └── init.js                    # boots the app (loads last)
├── requirements.txt
└── run.py                       # `python run.py` starts the server
```

## Security

- Passwords hashed with scrypt (`hashlib.scrypt`, random salt per user)
- Server-side sessions via an httpOnly cookie, 8-hour expiry, cleaned up automatically
- CSRF protection: double-submit token, required on every POST/PATCH
- Rate limiting: 10 login attempts / 15 min, 300 API calls / min, both per IP
- Security headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- All SQL uses parameterized queries — no string-built SQL anywhere
- Server-side validation on phone numbers, prices, dates, statuses
- Frontend escapes every piece of user data before inserting it into the page (`esc()` in `api.js`)

## Running it locally

### 1. Install Python

You need **Python 3.11+**. Check with:
```bash
python3 --version
```

### 2. Create a virtual environment (recommended)

```bash
cd dhaaga-python
python3 -m venv .venv
```

Activate it:
- **macOS / Linux:** `source .venv/bin/activate`
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (cmd):** `.venv\Scripts\activate.bat`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the server

```bash
python run.py
```

You'll see something like:

```
----------------------------------------------------
Dhaaga CRM — first run: login account created
  Username: admin
  Password: aB3xQz9kLp   (auto-generated — change it after logging in)
----------------------------------------------------
Seeded sample data into dhaaga.db
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Copy that password down — it's only shown once.

### 5. Open the app

Go to **http://localhost:8000** in your browser and log in with the printed credentials.
Change the password immediately from the **Profile** tab.

### Optional: set your own admin password

Instead of the auto-generated one:

```bash
# macOS / Linux
ADMIN_USERNAME=admin ADMIN_PASSWORD=your-strong-password python run.py

# Windows (PowerShell)
$env:ADMIN_USERNAME="admin"; $env:ADMIN_PASSWORD="your-strong-password"; python run.py
```

### Starting fresh

Delete `backend/database/dhaaga.db` and run `python run.py` again — a new login will
be created (auto-generated password, unless you set `ADMIN_PASSWORD` again).

## Database schema

Six tables — see `backend/database/schema.sql` for the full definition:

- **users** — login account (username, scrypt password hash + salt)
- **customers** — name, phone, referred_by (self-referencing FK), last_visit_date
- **measurements** — chest/waist/hip/shoulder/sleeve/length + notes, one row per customer
- **orders** — garment_type, status, price, delivery_date, delivered_at
- **payments** — amount, type (advance/balance), method, linked to an order
- **followups** — auto-created when an order's status becomes Delivered

## API docs

FastAPI generates interactive API docs automatically — once the server is running,
visit **http://localhost:8000/docs** to see and try every endpoint.
