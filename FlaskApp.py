from flask import Flask, jsonify, make_response, request
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'mysalesdb'
app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# Initialize MySQL
mysql = MySQL(app)

# Verify password function
@auth.verify_password
def verify_password(username, password):
    return username == "Alexis" and password == "1232"

# Protected routes with authentication
@app.route("/protected")
@auth.login_required
def protected_resource():
    return jsonify({"message": "You are authorized to access this resource."})

# Helper function to fetch data
def data_fetch(query, args=()):
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    data = cur.fetchall()
    cur.close()
    return data

# This were the CRUD apply
@app.route("/customers", methods=["GET"])
@auth.login_required
def get_customers():
    data = data_fetch("SELECT * FROM customers")
    return make_response(jsonify(data), 200)

#Read
@app.route("/customers/<int:id>", methods=["GET"])
@auth.login_required
def get_customer_by_id(id):
    data = data_fetch("SELECT * FROM customers WHERE CustomerID = %s", (id,))
    if data:
        return make_response(jsonify(data[0]), 200)
    return make_response(jsonify({"error": "Customer not found"}), 404)

#Create
@app.route("/customers", methods=["POST"])
@auth.login_required
def add_customer():
    try:
        info = request.get_json()
        query = """INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zipcode) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (info["first_name"], info["last_name"], info["email"], info["phone"], info["address"], 
                  info["city"], info["state"], info["zipcode"])
        cur = mysql.connection.cursor()
        cur.execute(query, values)
        mysql.connection.commit()
        cur.close()
        return make_response(jsonify({"message": "Customer added successfully"}), 201)
    except KeyError as e:
        error_message = f"KeyError: Missing key '{e.args[0]}' in JSON payload"
        return make_response(jsonify({"error": error_message}), 400)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

#Update
@app.route("/customers/<int:id>", methods=["PUT"])
@auth.login_required
def update_customer(id):
    try:
        info = request.get_json()
        query = """UPDATE customers SET first_name = %s, last_name = %s, email = %s, phone = %s, address = %s, 
                   city = %s, state = %s, zipcode = %s WHERE CustomerID = %s"""
        values = (info["first_name"], info["last_name"], info["email"], info["phone"], info["address"], 
                  info["city"], info["state"], info["zipcode"], id)
        cur = mysql.connection.cursor()
        cur.execute(query, values)
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        if rows_affected == 0:
            return make_response(jsonify({"error": "Customer not found"}), 404)
        return make_response(jsonify({"message": "Customer updated successfully"}), 200)
    except KeyError as e:
        error_message = f"KeyError: Missing key '{e.args[0]}' in JSON payload"
        return make_response(jsonify({"error": error_message}), 400)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

#Delete
@app.route("/customers/<int:id>", methods=["DELETE"])
@auth.login_required
def delete_customer(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM customers WHERE CustomerID = %s", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        if rows_affected == 0:
            return make_response(jsonify({"error": "Customer not found"}), 404)
        return make_response(jsonify({"message": "Customer deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

# CREATE/GET/DELETE Orders
@app.route("/orders", methods=["GET"])
@auth.login_required
def get_orders():
    data = data_fetch("SELECT * FROM orders")
    return make_response(jsonify(data), 200)

@app.route("/orders/<int:OrderID>", methods=["GET"])
@auth.login_required
def get_order_by_id(OrderID):
    data = data_fetch("SELECT * FROM orders WHERE OrderID = %s", (OrderID,))
    if data:
        return make_response(jsonify(data[0]), 200)
    return make_response(jsonify({"error": "Order not found"}), 404)

@app.route("/customers/<int:CustomerID>/orders", methods=["POST"])
@auth.login_required
def add_order(CustomerID):
    try:
        info = request.get_json()
        query = """INSERT INTO orders (CustomerID, OrderDate, TotalAmount) 
                   VALUES (%s, %s, %s)"""
        values = (CustomerID, info["OrderDate"], info["TotalAmount"])
        cur = mysql.connection.cursor()
        cur.execute(query, values)
        mysql.connection.commit()
        cur.close()
        return make_response(jsonify({"message": "Order added successfully"}), 201)
    except KeyError as e:
        error_message = f"KeyError: Missing key '{e.args[0]}' in JSON payload"
        return make_response(jsonify({"error": error_message}), 400)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/orders/<int:OrderID>", methods=["DELETE"])
@auth.login_required
def delete_order(OrderID):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM orders WHERE OrderID = %s", (OrderID,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        if rows_affected == 0:
            return make_response(jsonify({"error": "Order not found"}), 404)
        return make_response(jsonify({"message": "Order deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

# Customer Orders
@app.route("/customers/<int:id>/orders", methods=["GET"])
@auth.login_required
def get_orders_by_customer(id):
    data = data_fetch("SELECT * FROM orders WHERE CustomerID = %s", (id,))
    return make_response(jsonify(data), 200)

@app.route("/customers/<int:id>/orders", methods=["DELETE"])
@auth.login_required
def delete_orders_by_customer(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM orders WHERE CustomerID = %s", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        if rows_affected == 0:
            return make_response(jsonify({"error": "No orders found for the specified customer ID"}), 404)
        return make_response(jsonify({"message": "Customer orders deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

# Order Details
@app.route("/orderdetails", methods=["GET"])
@auth.login_required
def get_orderdetails():
    data = data_fetch("SELECT * FROM orderdetails")
    return make_response(jsonify(data), 200)

@app.route("/orders/<int:OrderID>/orderdetails", methods=["GET"])
@auth.login_required
def get_order_details(OrderID):
    data = data_fetch("SELECT * FROM orderdetails WHERE OrderID = %s", (OrderID,))
    return make_response(jsonify(data), 200)

@app.route("/orders/<int:OrderID>/orderdetails", methods=["POST"])
@auth.login_required
def add_order_detail(OrderID):
    try:
        info = request.get_json()
        query = """INSERT INTO orderdetails (OrderID, ProductID, Quantity, UnitPrice) 
                   VALUES (%s, %s, %s, %s)"""
        values = (OrderID, info["ProductID"], info["Quantity"], info["UnitPrice"])
        cur = mysql.connection.cursor()
        cur.execute(query, values)
        mysql.connection.commit()
        cur.close()
        return make_response(jsonify({"message": "Order detail added successfully"}), 201)
    except KeyError as e:
        error_message = f"KeyError: Missing key '{e.args[0]}' in JSON payload"
        return make_response(jsonify({"error": error_message}), 400)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    
@app.route("/orders/format", methods=["GET"])
@auth.login_required
def get_params():
    fmt = request.args.get('id')
    foo = request.args.get('aaaa')
    return make_response(jsonify({"format":fmt, "foo":foo}),200)

if __name__ == "__main__":
    app.run(debug=True)
