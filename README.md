# Kettle & Kiln — Specialty Coffee E-Commerce

A lightweight, full-stack e-commerce website for a fictional specialty coffee roastery. Built with Python and Flask, it covers the full shopping journey from browsing beans to placing an order and tracking it afterwards.

---

## Features

- **Product catalogue** — browse all beans filtered by roast level (Light, Medium, Medium-Dark, Dark)
- **Product detail pages** — individual pages per bean with description, price, and related products
- **Shopping cart** — add items from the menu or product page, adjust quantities with +/− controls, remove items
- **Checkout** — collect contact, delivery, address, and payment details; delivery fee calculated and applied live as the user changes the delivery option
- **Order storage** — every completed order is saved to `orders.json` with a unique order number (`KK-1001`, `KK-1002`, …)
- **Order tracking** — customers can look up any past order by entering their email address and order number

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Web framework | [Flask](https://flask.palletsprojects.com/) |
| Templating | Jinja2 (via Flask) |
| Styling | Plain CSS (custom properties, CSS Grid, Flexbox) |
| Client-side logic | Vanilla JavaScript (no frameworks) |
| Data storage | JSON flat files (`products.json`, `orders.json`) |
| Session handling | Flask server-side sessions (cookie-based) |

No database, no external JS framework, no build step — the project runs with a single `python main.py` command.

---

## Project Structure

```
coffee_shop_ecommerce/
├── main.py               # Flask app — all routes and business logic
├── products.json         # Product catalogue (beans)
├── orders.json           # Persisted order records
├── static/
│   ├── css/
│   │   └── style.css     # All site styles
│   └── images/           # Product images (SVG)
└── templates/
    ├── base.html         # Shared layout (nav, footer)
    ├── index.html        # Homepage with hero and featured beans
    ├── menu.html         # Full catalogue with roast filter
    ├── product.html      # Single product detail page
    ├── cart.html         # Shopping cart
    ├── checkout.html     # Checkout form and order confirmation
    └── order.html        # Order lookup / tracking page
```

---

## How It Works

### Browsing & Cart

Products are loaded from `products.json` at startup. Each product's roast level becomes its browsable category. The cart is stored in the Flask session as a plain dict (`{product_id: quantity}`), so it persists across page loads without any database.

### Checkout & Delivery Fees

Three delivery options are available:

| Option | Fee |
|---|---|
| In-Store Pickup | Free |
| Standard Delivery | £3.99 |
| Express Delivery | £7.99 |

The fee is applied to the order total on the server when the form is submitted. On the client side, the sidebar total and the Place Order button update live as the user changes the delivery option (no page reload required).

### Order Numbers & Storage

When an order is placed, the app assigns a sequential order number (`KK-1001` onwards) based on the current count in `orders.json`. The full order record — customer details, delivery method, line items, delivery fee, and grand total — is appended to `orders.json`.

### Order Tracking

Customers can visit **Track Order** (in the nav) and enter their email address and order number. The app searches `orders.json` for a matching record (case-insensitive on both fields) and displays the full order summary including items, delivery fee, address, and total.

---

## Running Locally

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install Flask:
   ```bash
   pip install flask
   ```

3. Start the development server:
   ```bash
   python main.py
   ```

4. Open `http://127.0.0.1:5000` in your browser.

---

## Pages

| URL | Description |
|---|---|
| `/` | Homepage — hero banner and featured beans |
| `/menu` | Full catalogue, filterable by roast level |
| `/product/<id>` | Individual product detail page |
| `/cart` | Shopping cart |
| `/checkout` | Checkout form and order confirmation |
| `/order` | Order lookup / tracking |
