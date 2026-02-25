import sqlite3
import os
from werkzeug.security import generate_password_hash
DB_NAME="inventory.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    con=get_connection()
    cur=con.cursor()
    with open("schema.sql", "r") as f:
        cur.executescript(f.read())
    con.commit()
    con.close()


def add_item(name,mrp,purchase_rate,low_stock_count):
    con=get_connection()
    cur=con.cursor()
    cur.execute("""
INSERT INTO items(name, mrp, purchase_rate,low_stock)
                VALUES(?,?,?,?)
                """, (name, mrp,purchase_rate,low_stock_count))
    con.commit()
    con.close()

def get_item_byid(item_id):
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT * FROM items WHERE id=?",(item_id,))
    row=cur.fetchone()
    con.close()
    return row

def update_item(item_id,name,mrp,purchase_rate,low_stock):
    con=get_connection()
    cur=con.cursor()
    cur.execute("""
UPDATE items
                SET name=?,mrp=?,purchase_rate=?,low_stock=?
                WHERE id=?
                """,(name,mrp,purchase_rate,low_stock,item_id))
    con.commit()
    con.close()


def delete_item(item_id):
    con=get_connection()
    cur=con.cursor()
    cur.execute("DELETE FROM items WHERE id=?",(item_id,))
    con.commit()
    con.close()


def get_all_items():
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT * FROM items")
    items=cur.fetchall()
    con.close()
    return items

def count_items():
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT COUNT(*) FROM items")
    n=cur.fetchone()[0]
    con.close()
    return n

def total_stock_in():
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT COALESCE(SUM(qty),0) FROM transactions WHERE type='IN' ")
    total=cur.fetchone()[0]
    con.close()
    return total

def total_stock_out():
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT COALESCE(SUM(qty),0) FROM transactions WHERE type='OUT' ")
    total=cur.fetchone()[0]
    con.close()
    return total

def count_low_stock():
    con=get_connection()
    cur=con.cursor()

    cur.execute("""
SELECT COUNT(*) 
                FROM items
                WHERE(
                (SELECT COALESCE(SUM(qty), 0)
                FROM transactions
                WHERE item_id=items.id AND type='IN')
                -
                (SELECT COALESCE(SUM(qty),0)
                FROM transactions
                WHERE item_id=items.id AND type='OUT')
                )<=items.low_stock
                """)
    count=cur.fetchone()[0]
    con.close()
    return count

def get_low_stock_id(item_id):
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT low_stock FROM items WHERE id=?",(item_id,))
    row=cur.fetchone()
    con.close()
    return row[0] if row else 0


def add_transaction(item_id,qty,type,party=None):
    con=get_connection()
    cur=con.cursor()
    cur.execute("INSERT INTO transactions (item_id,qty,type,party) VALUES (?,?,?,?)",
                (item_id,qty,type,party))
    con.commit()
    con.close()

def get_stock_ins():
    con=get_connection()
    cur=con.cursor()
    cur.execute("""
SELECT transactions.item_id,items.name, transactions.qty,transactions.party,transactions.date
                FROM transactions
                JOIN items ON transactions.item_id=items.id
                WHERE transactions.type='IN'
                ORDER BY transactions.date DESC
                """)
    items=cur.fetchall()
    con.close()
    return items

def get_stock_out():
    con=get_connection()
    cur=con.cursor()
    cur.execute("""
SELECT transactions.item_id,items.name, transactions.qty,transactions.party,transactions.date
                FROM transactions
                JOIN items ON transactions.item_id=items.id
                WHERE transactions.type='OUT'
                ORDER BY transactions.date DESC
                """)
    items=cur.fetchall()
    con.close()
    return items


def get_balance():
    con=get_connection()
    cur=con.cursor()
    cur.execute("""
SELECT i.id,i.name,i.mrp,i.purchase_rate,i.low_stock,
                COALESCE(SUM(CASE WHEN t.type='IN' THEN t.qty END),0) AS total_in,
                COALESCE(SUM(CASE WHEN t.type='OUT' THEN t.qty END),0) AS total_out,

                COALESCE(SUM(CASE WHEN t.type='IN' THEN t.qty END),0)-
                COALESCE(SUM(CASE WHEN t.type='OUT' THEN t.qty END),0) AS balance
                FROM items i
                LEFT JOIN transactions t ON i.id=t.item_id
                GROUP BY i.id
                """)
    rows=cur.fetchall()
    con.close()
    return rows

def get_balance_byid(item_id):
    con=get_connection()
    cur=con.cursor()
    cur.execute("""
SELECT COALESCE(SUM(qty),0)
                FROM transactions
                WHERE item_id=? AND type='IN'
                """,(item_id,))
    total_in=cur.fetchone()[0]

    cur.execute("""
SELECT COALESCE(SUM(qty),0)
                FROM transactions
                WHERE item_id=? AND type='OUT'
                """,(item_id,))
    total_out=cur.fetchone()[0]
    con.close()

    return total_in-total_out

def get_low_stock_items():
    con=get_connection()
    cur=con.cursor()
    cur.execute("""
SELECT i.id,i.name,i.mrp,i.purchase_rate,i.low_stock,
                COALESCE(SUM(CASE WHEN t.type='IN' THEN t.qty END),0) AS total_in,
                COALESCE(SUM(CASE WHEN t.type='OUT' THEN t.qty END),0) AS total_out,

                COALESCE(SUM(CASE WHEN t.type='IN' THEN t.qty END),0)-
                COALESCE(SUM(CASE WHEN t.type='OUT' THEN t.qty END),0) AS balance
                FROM items i
                LEFT JOIN transactions t ON i.id=t.item_id
                GROUP BY i.id
                HAVING balance<=i.low_stock
                ORDER BY balance ASC
                """)
    rows=cur.fetchall()
    con.close()
    return rows

def create_user(username,password,role):
    con=get_connection()
    cur=con.cursor()
    cur.execute("INSERT INTO users (username,password_hash,role) VALUES (?,?,?)",
                (username,generate_password_hash(password),role))
    con.commit()
    con.close()

def get_user(username):
    con=get_connection()
    cur=con.cursor()
    cur.execute("SELECT id,username,password_hash,role FROM users WHERE username=?",(username,))
    user=cur.fetchone()
    con.close()
    return user




    


    
