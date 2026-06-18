# Ezasekasi Spaza Shop Management System

**Live:** [ezasekasisystem.onrender.com](https://ezasekasisystem.onrender.com)

A full-featured web-based management system for spaza shops built with Flask and PostgreSQL. Streamlines inventory, sales, supplier coordination, credit customer tracking, and reporting.

---

## Quick Start

```bash
git clone https://github.com/mapulebuilds/EzasekasiSystem.git
cd EzasekasiSystem
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # add your DATABASE_URL
python app.py
```

Visit `http://localhost:5000` — login with `mercy_m` / `123456`.

---

## Features

| Module | Capabilities |
|---|---|
| **Dashboard** | Real-time KPIs, stock overview, low-stock alerts, best-selling product |
| **Inventory** | CRUD products, stock tracking, reorder levels, expiry dates, supplier links |
| **Point of Sale** | Quick product selection, auto stock deduction, transaction history |
| **Suppliers** | Supplier profiles, stock receipt logging, contact management |
| **Credit Customers** | Customer profiles, credit limits, sale-on-credit, payment recording, balance tracking |
| **Reports** | Daily sales, low stock report, stock receipts, credit balances — CSV & PDF export |
| **AI Insights** | Demand prediction, trending products, dynamic credit scoring |
| **Auth** | Session-based login with role-based access (Owner, Admin, Cashier) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | PostgreSQL (Neon on production) |
| Frontend | HTML5, CSS3, Jinja2 templates |
| PDF Reporting | ReportLab |
| Deployment | Render (web) + Neon (DB) |

---

## Project Structure

```
EzasekasiSystem/
├── app.py                   # Main Flask application (30+ routes)
├── templates/               # 7 Jinja2 HTML templates
├── static/css/style.css     # Application stylesheet
├── render.yaml              # Render Blueprint config
├── runtime.txt              # Python 3.13
├── requirements.txt         # Python dependencies
├── .env.example             # Env var template (copy to .env)
├── database_postgresql.sql  # Schema + seed data reference
└── README.md
```

---

## Default Credentials

| Username | Password | Role |
|---|---|---|
| `mercy_m` | `123456` | Owner |
| `happy_s` | `123456` | Admin |
| `bri_m` | `123456` | Cashier |

---

## API Endpoints

### Pages (GET)
| Route | Description |
|---|---|
| `/login` | Login page |
| `/` | Dashboard (requires auth) |
| `/products` | Inventory management |
| `/sales` | Point of sale |
| `/suppliers` | Supplier management + stock receipt |
| `/credit-customers` | Credit customer management |
| `/reports` | Reporting hub |

### Data Actions (POST)
| Route | Description |
|---|---|
| `/login` | Authenticate user |
| `/logout` | End session |
| `/products/add` | Add product |
| `/products/update/<id>` | Update product |
| `/products/delete/<id>` | Delete product |
| `/sales/add` | Record sale |
| `/suppliers/add` | Add supplier |
| `/suppliers/update/<id>` | Update supplier |
| `/suppliers/delete/<id>` | Delete supplier |
| `/suppliers/receive` | Log stock receipt |
| `/credit-customers/add` | Add credit customer |
| `/credit-customers/update/<id>` | Update customer |
| `/credit-customers/delete/<id>` | Delete customer |
| `/credit-customers/credit-sale` | Record credit sale |
| `/credit-customers/payment` | Record payment |
| `/update/<id>` | Quick stock update |
| `/sell/<id>` | Quick sell one unit |

### Reports & Export
| Route | Description |
|---|---|
| `/reports/daily-sales` | Filter daily sales |
| `/reports/low-stock` | Filter by category |
| `/reports/stock-receipts` | Filter by supplier |
| `/reports/credit-balances` | Filter by customer |
| `/reports/export-sales` | Download CSV |
| `/reports/export-sales-pdf` | Download PDF |

### Health
| Route | Description |
|---|---|
| `/health-db` | Database connection status |

---

## Database Schema

| Table | Purpose |
|---|---|
| `users` | Login accounts |
| `products` | Inventory items |
| `suppliers` | Supplier info |
| `sales` | Transaction records |
| `stock_receipts` | Incoming stock logs |
| `customers` | Credit customer profiles |
| `credit_transactions` | Credit sales & payments |
| `credit_scores` | User credit scoring |
| `ai_predictions` | Demand predictions |

---

## Deployment: Render + Neon

### 1. Database (Neon)
- Create a [Neon](https://neon.tech) project
- Copy the connection string: `postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require`

### 2. Web Service (Render)
- Push this repo to GitHub
- In **Render Dashboard** → **New** → **Blueprint** → select your repo
- After creation, go to your web service → **Environment** and add:

| Key | Value |
|---|---|
| `DATABASE_URL` | Your Neon connection string |
| `SECRET_KEY` | A long random string |

- Click **Manual Deploy** → **Deploy latest commit**

> Do not commit secrets to GitHub. Use Render's env var dashboard or a local `.env` file.

---

## Team

| Name | Role |
|---|---|
| Mercy Molonyama | AI Logic & Stock Update |
| Karabo Komane | System Analysis & Sales |
| Happiness Simao | Database & POS Design |
| Mapule | Inventory UI & UX |
| Kearabetswe Lebelo | Backend Integration |
| Tau Thamaga | Quality Assurance & Testing |
| Percy Thotse | Documentation & Support |
| Tshwarelo Mahlako | API Development |
| Samkelisiwe Mngadi | User Experience Design |

**Tshwane University of Technology — Emalahleni Campus**

---

## License

Educational project developed for TUT. All rights reserved.
