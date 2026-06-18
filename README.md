# Ezasekasi Spaza Shop Management System

A comprehensive web-based management system for spaza shops, built with Flask and PostgreSQL. Designed to streamline inventory management, sales operations, supplier coordination, and credit customer tracking.

## Project Overview

**Ezasekasi Spaza Shop Management System** is a full-featured business management platform developed as a university software project at Tshwane University of Technology (TUT). The system provides tools for managing products, tracking sales, handling supplier relationships, managing credit customers, and generating business reports.

### Key Features

- **📊 Dashboard Overview** - Real-time statistics and business metrics
- **📦 Inventory Management** - Product management, stock tracking, and reorder alerts
- **💳 Point of Sale (POS)** - Fast and efficient sales transaction processing
- **🏢 Supplier Management** - Supplier information and stock receipt tracking
- **👥 Credit Customer Management** - Customer profiles, credit limits, and transaction history
- **📈 Reporting** - Comprehensive business reports and analytics
- **🔐 User Authentication** - Secure login system with user accounts

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Reporting:** ReportLab (PDF generation)
- **Libraries:** psycopg2-binary, reportlab

## Project Structure

```
EzasekasiSystem/
├── app.py                 # Main Flask application
├── templates/             # Jinja2 HTML templates
├── static/                # Static assets (CSS, images)
├── render.yaml            # Render.com deployment config
├── runtime.txt            # Python version for deployment
├── database_postgresql.sql  # PostgreSQL schema + seed data
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .venv/                 # Python virtual environment
```

## Installation & Setup

### Prerequisites
- Python 3.13+
- PostgreSQL 16+
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/mapulebuilds/EzasekasiSystem.git
cd EzasekasiSystem
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate   # On Windows
# or
source .venv/bin/activate  # On macOS/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
1. Create a PostgreSQL database named `ezasekasi_db`
2. Run the schema file: `psql -U postgres -d ezasekasi_db -f database_postgresql.sql`
3. Or set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@host:5432/ezasekasi_db"
```

### Step 5: Run the Application
```bash
python app.py
```
The application will be available at `http://localhost:5000`

## Default Login Credentials

After database setup, use any of the following credentials:
- **Username:** `mercy_m`, **Password:** `123456` (Owner)
- **Username:** `happy_s`, **Password:** `123456` (Admin)
- **Username:** `bri_m`, **Password:** `123456` (Cashier)

## Features in Detail

### Dashboard
- Quick overview of key metrics
- Total products, low stock alerts, total stock units, total sales
- Product overview table with stock status

### Inventory Management
- Add, edit, delete products
- Track product prices, stock quantities, and reorder levels
- Monitor supplier information for each product

### Point of Sale (POS)
- Quick product search and selection
- Real-time inventory updates
- Transaction history and daily summaries

### Supplier Management
- Maintain supplier contact information
- Track stock receipts and delivery dates
- Supplier communication details

### Credit Customer Management
- Create and manage customer profiles
- Set credit limits and track balances
- Monitor transaction history and payment patterns

### Reporting
- Daily sales reports
- Low stock product alerts
- Stock receipt tracking
- Credit transaction summaries

## Team Credits

This project was developed by:
- **Mercy** - AI Logic & Stock Update
- **Karabo** - System Analysis & Sales
- **Happiness** - Database & POS Design
- **Mapule** - Inventory UI & UX
- **Kearabetswe** - Backend Integration
- **Tau Thamaga** - Quality Assurance & Testing
- **Percy Thotse** - Documentation & Support
- **Tshwarelo Mahlako** - API Development
- **Samkelisiwe Mngadi** - User Experience Design

## University Information

**Institution:** Tshwane University of Technology (TUT)  
**Campus:** Emalahleni

## Development Notes

### Database Schema
The system uses the following main tables:
- `Users` - User accounts
- `Products` - Product inventory
- `Suppliers` - Supplier information
- `Sales` - Transaction records
- `Stock_Receipts` - Incoming inventory
- `Customers` - Credit customer profiles
- `Credit_Transactions` - Customer credit transactions

### Security
- User authentication with session management
- Password-protected admin operations
- Database error handling and validation

## Deployment

This project is configured for one-click deployment on [Render](https://render.com).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Deploy on Render:
1. Fork/clone this repository to your GitHub
2. Go to [Render Dashboard](https://dashboard.render.com) → New → Blueprint
3. Connect your repository
4. Render will auto-detect `render.yaml` and set up:
   - A **Web Service** running gunicorn
   - A **PostgreSQL database** (free tier)
   - Environment variables (`DATABASE_URL`, `SECRET_KEY`)
5. The database schema and seed data are applied automatically on first start

### Manual Deployment (other platforms):
1. Set environment variables:
   - `DATABASE_URL` - PostgreSQL connection string
   - `SECRET_KEY` - Random secret for session signing
   - `FLASK_DEBUG` - Set to `0` for production
2. Install dependencies: `pip install -r requirements.txt`
3. Run with gunicorn: `gunicorn app:app`

## Future Enhancements

- Mobile application support
- Advanced analytics and forecasting
- Multi-location support
- API integration for third-party services
- Enhanced reporting with charts and visualizations

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL Server is running
- Verify `DATABASE_URL` environment variable or credentials in `app.py`
- Check database name is `ezasekasi_db`
- Run the schema from `database_postgresql.sql`

### Module Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Manually install: `pip install -r requirements.txt`

### Port Already in Use
- Flask defaults to port 5000. Set `PORT` env var or modify `app.py`:
```bash
$env:PORT=5001  # PowerShell
# or
export PORT=5001  # Linux/macOS
```

## License

This project is developed for educational purposes at Tshwane University of Technology.

## Contributing

For contributions or bug reports, please contact the development team or submit pull requests.

---

**Last Updated:** May 2026  
**Version:** 1.0
