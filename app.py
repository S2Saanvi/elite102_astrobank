from flask import Flask, render_template, request, redirect, url_for, flash
from main import init_db, create_account, get_account, deposit, withdraw

app = Flask(__name__)
app.secret_key = "bank-secret-key"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    name = request.form.get("name", "").strip()
    account_id = request.form.get("account_id", "").strip()
    if not name or not account_id:
        flash("Please enter both name and account number to search.", "error")
        return redirect(url_for("index"))
    try:
        acc = get_account(int(account_id))
    except ValueError:
        acc = None
    if acc is None or acc["name"].lower() != name.lower():
        flash("No account found. Please check the details and try again.", "error")
        return redirect(url_for("index"))
    return redirect(url_for("account", account_id=acc["id"]))


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"].strip()
        balance = request.form["balance"].strip()
        if not name:
            flash("Name is required.", "error")
            return render_template("create.html")
        try:
            balance = float(balance)
            if balance < 0:
                raise ValueError
        except ValueError:
            flash("Enter a valid non-negative balance.", "error")
            return render_template("create.html")
        new_id = create_account(name, balance)
        flash(f"Account created! Your ID is {new_id}", "success")
        return redirect(url_for("account", account_id=new_id))
    return render_template("create.html")


@app.route("/account/<int:account_id>")
def account(account_id):
    acc = get_account(account_id)
    if acc is None:
        flash("Account not found.", "error")
        return redirect(url_for("index"))
    return render_template("account.html", acc=acc)


@app.route("/account/<int:account_id>/deposit", methods=["POST"])
def do_deposit(account_id):
    try:
        amount = float(request.form["amount"])
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Enter a valid positive amount.", "error")
        return redirect(url_for("account", account_id=account_id))
    new_balance = deposit(account_id, amount)
    flash(f"Deposited ${amount:.2f}. New balance: ${new_balance:.2f}", "success")
    return redirect(url_for("account", account_id=account_id))


@app.route("/account/<int:account_id>/withdraw", methods=["POST"])
def do_withdraw(account_id):
    try:
        amount = float(request.form["amount"])
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Enter a valid positive amount.", "error")
        return redirect(url_for("account", account_id=account_id))
    new_balance, error = withdraw(account_id, amount)
    if error:
        flash(error, "error")
    else:
        flash(f"Withdrew ${amount:.2f}. New balance: ${new_balance:.2f}", "success")
    return redirect(url_for("account", account_id=account_id))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
