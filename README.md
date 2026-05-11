# Ezasekasi Spaza Shop Management System

A comprehensive web-based management system for spaza shops, built with Flask and MySQL. Designed to streamline inventory management, sales operations, supplier coordination, and credit customer tracking.

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
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Reporting:** ReportLab (PDF generation)
- **Libraries:** mysql-connector-python, reportlab

## Project Structure

```
EzasekasiSystem/
├── app.py                 # Main Flask application
├── templates/
│   ├── dashboard.html     # Dashboard page
│   ├── login.html         # Login page
│   ├── products.html      # Product inventory
│   ├── sales.html         # Point of sale
│   ├── suppliers.html     # Supplier management
│   ├── credit_customers.html  # Credit customer management
│   └── reports.html       # Reporting page
├── README.md              # This file
└── .venv/                 # Python virtual environment
```

## Installation & Setup

### Prerequisites
- Python 3.x
- MySQL Server
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
pip install flask mysql-connector-python reportlab
```

### Step 4: Configure Database
1. Create a MySQL database named `ezasekasi_db`
2. Update database credentials in `app.py`:
```python
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="YOUR_PASSWORD",
        database="ezasekasi_db"
    )
```

### Step 5: Run the Application
```bash
python app.py
```
The application will be available at `http://localhost:5000`

## Default Login Credentials

After database setup, use the following credentials to access the system:
- **Username:** [Your registered username]
- **Password:** [Your registered password]

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

## Future Enhancements

- Mobile application support
- Advanced analytics and forecasting
- Multi-location support
- API integration for third-party services
- Enhanced reporting with charts and visualizations

## Troubleshooting

### Database Connection Error
- Ensure MySQL Server is running
- Verify database credentials in `app.py`
- Check database name is `ezasekasi_db`

### Module Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` (if available)
- Manually install: `pip install flask mysql-connector-python reportlab`

### Port Already in Use
- Flask defaults to port 5000. If in use, modify in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port number
```

## License

This project is developed for educational purposes at Tshwane University of Technology.

## Contributing

For contributions or bug reports, please contact the development team or submit pull requests.

---

**Last Updated:** May 2026  
**Version:** 1.0
