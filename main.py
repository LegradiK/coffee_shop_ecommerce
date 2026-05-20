import os
import json
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "change-me-in-production"

with open(os.path.join(os.path.dirname(__file__), "products.json")) as f:
    PRODUCTS = json.load(f)

# Use roast level as the browsable category
for p in PRODUCTS:
    p["category"] = p["roast"]

CATEGORIES = ["All"] + sorted(set(p["roast"] for p in PRODUCTS))


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
    item = get_product(product_id)
    if not item:
        return redirect(url_for("menu"))
    related = [p for p in PRODUCTS if p["category"] == item["category"] and p["id"] != item["id"]][:3]
    return render_template("product.html", product=item, related=related)


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
        session["cart"] = {}
        return render_template("checkout.html", items=items, total=total, order_placed=True)
    return render_template("checkout.html", items=items, total=total, order_placed=False)


if __name__ == "__main__":
    app.run(debug=True)
