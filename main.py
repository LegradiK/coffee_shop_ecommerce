import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "change-me-in-production"

with open(os.path.join(os.path.dirname(__file__), "products.json")) as f:
    PRODUCTS = json.load(f)

# Use roast level as the browsable category
for p in PRODUCTS:
    p["category"] = p["roast"]

CATEGORIES = ["All"] + sorted(set(p["roast"] for p in PRODUCTS))


ORDERS_FILE = os.path.join(os.path.dirname(__file__), "orders.json")

DELIVERY_FEES = {
    "pickup": 0.00,
    "standard": 3.99,
    "express": 7.99,
}


def load_orders():
    with open(ORDERS_FILE) as f:
        return json.load(f)


def next_order_number():
    orders = load_orders()
    return f"KK-{1001 + len(orders)}"


def save_order(order):
    orders = load_orders()
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)


def get_product(product_id):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)


def get_cart():
    return session.get("cart", {})


def cart_total(cart):
    total = 0
    for pid, qty in cart.items():
        p = get_product(int(pid))
        if p:
            total += p["price"] * qty
    return round(total, 2)


def cart_count(cart):
    return sum(cart.values())


@app.context_processor
def inject_cart_count():
    return {"cart_count": cart_count(get_cart())}


@app.route("/")
def index():
    featured = PRODUCTS[:3]
    return render_template("index.html", featured=featured)


@app.route("/menu")
def menu():
    category = request.args.get("category", "All")
    if category == "All":
        products = PRODUCTS
    else:
        products = [p for p in PRODUCTS if p["category"] == category]
    return render_template("menu.html", products=products, categories=CATEGORIES, active_category=category)


@app.route("/product/<int:product_id>")
def product(product_id):
    p = get_product(product_id)
    if p is None:
        return redirect(url_for("menu"))
    related = [x for x in PRODUCTS if x["category"] == p["category"] and x["id"] != p["id"]][:3]
    return render_template("product.html", product=p, related=related)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    qty = int(request.form.get("quantity", 1))
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    session["cart"] = cart
    return redirect(request.referrer or url_for("menu"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    qty = int(request.form.get("quantity", 1))
    cart = get_cart()
    if qty <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = qty
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    raw_cart = get_cart()
    items = []
    for pid, qty in raw_cart.items():
        p = get_product(int(pid))
        if p:
            items.append({"product": p, "qty": qty, "subtotal": round(p["price"] * qty, 2)})
    total = cart_total(raw_cart)
    return render_template("cart.html", items=items, total=total)


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    raw_cart = get_cart()
    if not raw_cart:
        return redirect(url_for("cart"))
    items = []
    for pid, qty in raw_cart.items():
        p = get_product(int(pid))
        if p:
            items.append({"product": p, "qty": qty, "subtotal": round(p["price"] * qty, 2)})
    total = cart_total(raw_cart)
    if request.method == "POST":
        delivery = request.form.get("delivery", "pickup")
        delivery_fee = DELIVERY_FEES.get(delivery, 0.00)
        grand_total = round(total + delivery_fee, 2)
        order_number = next_order_number()
        save_order({
            "order_number": order_number,
            "timestamp": datetime.now().isoformat(),
            "customer": {
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
            },
            "delivery": delivery,
            "delivery_fee": delivery_fee,
            "address": {
                "street": request.form.get("address"),
                "city": request.form.get("city"),
                "postcode": request.form.get("zip"),
                "county": request.form.get("county"),
            },
            "items": [
                {"id": i["product"]["id"], "name": i["product"]["name"],
                 "qty": i["qty"], "price": i["product"]["price"], "subtotal": i["subtotal"]}
                for i in items
            ],
            "subtotal": total,
            "total": grand_total,
        })
        session["cart"] = {}
        return render_template("checkout.html", items=items, total=total,
                               delivery_fee=delivery_fee, grand_total=grand_total,
                               order_placed=True, order_number=order_number)
    return render_template("checkout.html", items=items, total=total,
                           delivery_fees=DELIVERY_FEES, order_placed=False)


@app.route("/order", methods=["GET", "POST"])
def order_lookup():
    order = None
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        order_number = request.form.get("order_number", "").strip().upper()
        orders = load_orders()
        order = next(
            (o for o in orders
             if o["order_number"].upper() == order_number
             and o["customer"]["email"].lower() == email),
            None
        )
        if not order:
            error = "No order found with that email and order number."
    return render_template("order.html", order=order, error=error)


if __name__ == "__main__":
    app.run(debug=True)
