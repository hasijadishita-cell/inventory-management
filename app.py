from flask import Flask, render_template,redirect,request,url_for,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from db import *
import os
SEED_ON_START=True

app=Flask(__name__)
app.secret_key="dev-secret-change-this"

def login_reqired(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        
        return func(*args,**kwargs)
    return wrapper

role_level={"staff":1, "manager":2,"admin":3}

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            if "user" not in session:
                return redirect(url_for("login"))
            user_role=session["user"].get("role","staff")
            if role_level.get(user_role,0)<role_level[role]:
                flash("Not allowed!")
                return redirect (url_for("home"))
            return func(*args,**kwargs)
        return wrapper
    return decorator


@app.route("/")
def page():
    return redirect(url_for("login"))

@app.route("/home")
@login_reqired
def home():
    total_items=count_items()
    total_in=total_stock_in()
    total_out=total_stock_out()
    low_stock_count=count_low_stock()

    return render_template("home.html", total_items=total_items,total_in=total_in,total_out=total_out,low_stock_count=low_stock_count)

@app.route("/add-item", methods=["GET", "POST"])
@role_required("manager")
def add_item_route():
    if request.method=="POST":
        name=request.form.get("name")
        mrp=request.form.get("mrp")
        purchase_rate=request.form.get("purchase_rate")
        low_stock=request.form.get("low_stock")

        if not name or not mrp or not purchase_rate or not low_stock:
            flash("All fields are required")
            return redirect(url_for("add_item_route"))
        try:
            mrp=int(mrp)
            purchase_rate=int(purchase_rate)
            low_stock=int(low_stock)
        except ValueError:
            flash("MRP,Purchase rate and Low stock must be numbers.")
            return redirect(url_for("add_item_route"))
        add_item(name, mrp,purchase_rate,low_stock)
        flash("Item added successfully!!")
        return redirect(url_for("home"))
    return render_template("add_item.html")

@app.route("/stock_in", methods=["GET","POST"])
@role_required("staff")
def stock_in():
    if request.method=="POST":
        item_id=int(request.form.get("item_id"))
        qty=request.form.get("qty")
        party=request.form.get("party")

        if not qty:
            flash("Quantity is required!")
            return redirect(url_for("stock_in"))
        try:
            qty=int(qty)
        except ValueError:
            flash("Quantity must be a whole number!")
            return redirect(url_for("stock_in"))
        
        if qty<=0:
            flash("Quantity must be greater than 0")
            return redirect(url_for("stock_in"))
        

        add_transaction(item_id,qty,"IN",party)
        return redirect(url_for("home"))
    
    items=get_all_items()
    return render_template("stock_in.html", items=items)

@app.route("/stock_in_details")
def stock_in_details():
    data=get_stock_ins()
    return render_template("stock_in_table.html",data=data)


@app.route("/add_item_details")
def add_item_details():
    data=get_all_items()
    return render_template("add_item_table.html",data=data)

@app.route("/stock_out", methods=["GET", "POST"])
@role_required("staff")
def stock_out():
    if request.method=="POST":
        item_id=int(request.form.get("item_id"))
        qty=int(request.form.get("qty"))
        party=request.form.get("party")
        if not qty:
            flash("Quantity is required!")
            return redirect(url_for("stock_out"))
        try:
            qty=int(qty)
        except ValueError:
            flash("Quantity must be a whole number!")
            return redirect(url_for("stock_out"))
        
        if qty<=0:
            flash("Quantity must be greater than 0")
            return redirect(url_for("stock_out"))
        
        balance=get_balance_byid(item_id)

        if balance<=0:
            flash(f"Not enough stock. Available:{balance}")


        if qty>balance:
            flash("Not enough stock available!")
            return redirect(url_for("stock_out"))

        add_transaction(item_id,qty,"OUT",party)

        new_balance=balance-qty
        low_stock=get_low_stock_id(item_id)

        if new_balance<=low_stock:
            flash(f"Warning: Low Stock! Balance is now {new_balance} (limit{low_stock})")
        return redirect(url_for("home"))
    items=get_all_items()
    return render_template("stock_out.html", items=items)
        
@app.route("/stock_out_details")
def stock_out_details():
    data=get_stock_out()
    return render_template("stock_out_table.html",data=data)


@app.route("/balance")
def balance():
    data=get_balance()
    return render_template("balance.html", data=data)

@app.route("/low_stock")
def low_stock():
    items=get_low_stock_items()
    return render_template("low_stock.html",items=items)

def seed_data():
    add_item("Pen",10,9,5)
    add_item("Pencil",5,3,10)

    add_transaction(1,10,"IN","Amazon")
    add_transaction(1,5,"IN","Local shop")
    add_transaction(2,7,"IN","Flipkart")

    add_transaction(1,6,"OUT","Mr. Sharma")
    add_transaction(2,2,"OUT","Rajmandir")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"].strip()
        password=request.form["password"]
        

        user=get_user(username)
      
       
        if not user:
            flash("Invalid username or password")
            return redirect(url_for("login"))
        
        user_id,username,password_hash,role = get_user(username)
        
        if not check_password_hash(password_hash,password):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        
        session["user"]={
            "id":user_id,
            "username":username,
            "role":role
        }
        flash("Login Successfully!")
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/debug")
def debug_user():
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT id,username, role FROM users")
    rows=cur.fetchall()
    con.close()
    return str(rows)

@app.route("/edit-item/<int:item_id>",methods=["GET","POST"])
@role_required("manager")
def edit_item(item_id):
    item=get_item_byid(item_id)
    if not item:
        flash("Item not found")
        return redirect(url_for("add_item_details"))
    if request.method=="POST":
        name=request.form.get("name")
        mrp=request.form.get("mrp")
        purchase_rate=request.form.get("purchase_rate")
        low_stock=request.form.get("low_stock")
        update_item(item_id,name,mrp,purchase_rate,low_stock)
        flash("Item updated successfully")
        return redirect(url_for("add_item_details"))
    
    return render_template("edit_item.html",item=item)

@app.route("/delete-item/<int:item_id>",methods=["POST"])
@role_required("manager")
def delete_item_route(item_id):
    delete_item(item_id)
    flash("Item deleted successfully")
    return redirect(url_for("add_item_details"))
    
    

if __name__=="__main__":
    init_db()
    admin=get_user("admin")
    
    if not admin:
        create_user("admin","admin123","admin")

    manager=get_user("manager")
    

    if not manager:
        create_user("manager","manager123","manager")

    staff=get_user("staff")
    

    if not manager:
        create_user("staff","staff123","staff")
   
    app.run(debug=True)
        