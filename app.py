from flask import Flask, render_template, request, redirect, session, flash, send_file, jsonify,  url_for
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import shutil
from requests_oauthlib import OAuth2Session
import msal
import requests


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory where app.py is located
DATABASE_PATH = os.path.join(BASE_DIR, 'OT_crm.db')  # Make sure 'petforme.db' matches your SQLite database file name

app.secret_key = os.getenv('SECRET_KEY','default_secret_key')

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)

CLIENT_ID = 'f015ff07-5ad0-4a4a-9959-8fb45bf46e52'
CLIENT_SECRET = 'gB.8Q~~PoWp4tU7qicQjXnWfwywyxbJ17PTtFcsy'
TENANT_ID = '2f359e1f-c37b-4267-a0c0-5110b8b578ba'
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPES = ['User.Read']  # גישה לקריאת פרטי משתמש

# def get_redirect_uri():
#     host = request.host
#     scheme = "https" if "railway.app" in host else request.scheme
#     return f"{scheme}://{host}/auth/callback"

def build_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

def acquire_token_using_refresh_token(msal_app, refresh_token):
    result = msal_app.acquire_token_by_refresh_token(refresh_token, SCOPES)
    if "access_token" in result:
        return result["access_token"]
    else:
        return None
@app.route('/api/download_db', methods=['GET'])
def download_db():
    return send_file('OT_crm.db', as_attachment=True)

@app.route('/download_static', methods=['GET'])
def download_static():
    # Zip the static directory
    shutil.make_archive('static_files', 'zip', 'static')
    return send_file('static_files.zip', as_attachment=True)


def query(sql: str = "", params: tuple = (), db_name=DATABASE_PATH):
    try:
        with sqlite3.connect(db_name) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute(sql, params)  # Pass parameters to execute
            if sql.strip().lower().startswith('select'):
                return cur.fetchall()  # Fetch all results for SELECT queries
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/company_registration", methods=["POST"])
def register_company():
    data = request.json  # Expecting JSON data from frontend
    company_name = data.get("company-name").upper()
    company_slogan = data.get("company-slogan", "").title()

    emails = data.get("emails", [])
    
    # המרת כל האימיילים לאותיות קטנות
    emails = [email.lower() for email in emails]

    emails_json = json.dumps(emails)  # Convert list of emails to JSON format

    sql = "INSERT INTO Companies (name, emails, slogan) VALUES (?, ?, ?)"
    query(sql, (company_name, emails_json, company_slogan))  # Ensure query function is working properly
    return jsonify({"message": "Company registered successfully"}), 201


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        company_name = request.form.get('company-name').upper()

        if company_name == "TRIAL CRM":
            session['company_name'] = company_name
            session['company_slogan'] = "Explore our CRM for Free"
            session['valid_user'] = True  # Mark user as authenticated
            return redirect(url_for('index'))  # Redirect to the index route
        
        msal_app = build_msal_app()

        # יצירת URL להפניה ל-Microsoft עם redirect_uri תקין
        auth_url = msal_app.get_authorization_request_url(
            SCOPES,
            redirect_uri=url_for('auth_callback', _external=True,  _scheme='https'),  # הכוונה היא לחזור ל-/auth/callback
            state=company_name  # שמירת שם החברה כ-state
        )
        return redirect(auth_url)
    else:
        return render_template('login.html')

@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    if 'code' not in request.args:
        return redirect(url_for('login'))

    company_name = request.args.get('state')
    company_slogan = query("SELECT slogan FROM Companies WHERE name = ?", (company_name,))
    if company_slogan:
        company_slogan = company_slogan[0][0]
    else:
        company_slogan = ""

    session['company_name'] = company_name
    session['company_slogan'] = company_slogan

    msal_app = build_msal_app()

    # במקרה שאין refresh_token, אנחנו מבקשים קוד חדש
    if 'refresh_token' in session:
        refresh_token = session['refresh_token']
        access_token = acquire_token_using_refresh_token(msal_app, refresh_token)
    else:
        result = msal_app.acquire_token_by_authorization_code(
            request.args['code'],
            scopes=SCOPES,
            redirect_uri=url_for('auth_callback', _external=True, _scheme='https')
        )
        access_token = result.get('access_token')
        if "refresh_token" in result:
            session['refresh_token'] = result['refresh_token']

    if access_token:
        # עכשיו נשלח בקשה ל-API של Microsoft Graph בעזרת access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)

        if user_info.status_code == 200:
            user_info_json = user_info.json()
            user_email = user_info_json.get('mail') or user_info_json.get('userPrincipalName')

            row = query("SELECT emails FROM Companies WHERE name = ?", (company_name,))
            if row:
                try:
                    allowed_emails = json.loads(row[0][0])
                except Exception:
                    flash("Error parsing company emails.", "warning")
                    return redirect(url_for('login'))

                if user_email in allowed_emails and company_name:
                    # מוסיפים את המשתמש כמאומת למערכת
                    session['valid_user'] = True
                    return redirect(url_for('index'))  # לאחר הצלחה, נועלים את המשתמש במסך הדאשבורד
                else:
                    flash("Access denied. Your email is not authorized for this company.", "warning")
                    return redirect(url_for('login'))
            else:
                flash("Company not found.", "warning")
                return redirect(url_for('login'))
        else:
            return f"Failed to fetch user info: {user_info.status_code}", 400
    else:
        return "Authentication failed", 400




@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out successfully", "success")
    return redirect(url_for('login')) 

@app.route('/index')
def index():
    if 'valid_user' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('login'))

    company_name = session['company_name']
    company_slogan = session['company_slogan']
    
    customers = query("SELECT * FROM customers WHERE OT_company = ? ORDER BY name ASC", (company_name,))
    action_items = query("SELECT * FROM action_items WHERE OT_company = ?", (company_name,))
    contacts_display = query("SELECT * FROM contacts WHERE OT_company = ?", (company_name,))
        
    return render_template('index.html',
                           current_time=datetime.now(),
                           company_name=company_name,
                           company_slogan=company_slogan,
                           customers=customers,
                           action_items=action_items,
                           contacts_display=contacts_display)

# @app.route('/contacts', methods=['GET', 'POST'])
# def contacts():
#     company_name = session.get('company_name', '')
#     company_slogan = session.get('company_slogan', '')
#     contacts_display = query("SELECT * FROM contacts WHERE OT_company = ? ORDER BY name ASC", (company_name,))

#     return render_template('contacts.html', contacts=contacts_display,company_name=company_name, company_slogan=company_slogan)

@app.route("/get_contacts")
def get_contacts():
    company_name = session['company_name']
    contacts_db = query("SELECT * FROM contacts WHERE OT_company = ? ORDER BY name ASC", (company_name,))
    contacts = [
        {"id": contact[0], "name": contact[1], "phone": contact[2], "email": contact[3], "role": contact[4]}
        for contact in contacts_db
    ]
    return jsonify(contacts)


    
@app.route("/get_customer/<int:customer_id>")
def get_customer(customer_id):
    # Fetch customer details
    customer_query = "SELECT * FROM customers WHERE id = ?"
    customer = query(customer_query, (customer_id,))
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    company_name = customer[0][1]  # Assuming the second field is the company name

    # Fetch related data
    contacts_query = "SELECT * FROM contacts WHERE company = ?"
    contacts = query(contacts_query, (company_name,))

    meetings_query = "SELECT * FROM meetings WHERE company = ? ORDER BY date DESC"
    meetings = query(meetings_query, (company_name,))

    updates_query = "SELECT * FROM updates WHERE company = ? ORDER BY date DESC"
    updates = query(updates_query, (company_name,))

    technical_query = "SELECT * FROM technical WHERE company = ?"
    technical = query(technical_query, (company_name,))

    commercial_query = "SELECT * FROM commercial WHERE company = ?"
    commercial = query(commercial_query, (company_name,))

    orders_query = "SELECT * FROM orders WHERE company = ? ORDER BY date DESC"
    orders = query(orders_query, (company_name,))

    action_items_query = "SELECT * FROM action_items WHERE customer = ?"
    action_items = query(action_items_query, (company_name,))

    # Prepare data for each section
    customer_info = {
        "companyName": customer[0][1],
        "country": customer[0][2],
        "address": customer[0][3],
        "status": customer[0][5],
        "startDate": customer[0][7],
        "ndaFile": customer[0][8],
        "lead": customer[0][4],
        "salesRep": customer[0][6]
    }

    technical_info = {
        "line": technical[0][2] if technical else 'N/A',
        "application": technical[0][3] if technical else 'N/A',
        "lineSpeed": technical[0][4] if technical else 'N/A',
        "lineWidth": technical[0][5] if technical else 'N/A',
        "curingStatus": technical[0][6] if technical else 'N/A',
        "targets": technical[0][7] if technical else 'N/A',
    }

    commercial_info = {
        "annualVolume": commercial[0][2] if commercial else 'N/A',
        "linesAmount": commercial[0][3] if commercial else 'N/A',
    }

    action_items_list = [
        {"item": action_item[2], "responsible": action_item[3], "dueDate": action_item[4], "status": action_item[5], "category": action_item[6], "OT_company" : action_item[7]}
        for action_item in action_items
    ]

    contacts_list = [
        {"id": contact[0], "name": contact[1], "phone": contact[2], "email": contact[3], "role": contact[4]}
        for contact in contacts
    ]

    meetings_list = [
        {"id": meeting[0], "comapny": meeting[1], "title": meeting[2], "date": meeting[3], "attendees": meeting[4], "summary": meeting[5]}
        for meeting in meetings
    ]

    updates_list = [
        {"id": update[0], "date": update[2], "content": update[3], "nextStep": update[4], "file": update[5], "title": update[6]}
        for update in updates
    ]

    orders_list = [
        {"id": order[0], "material": order[2], "amount": order[3], "goal": order[4], "notes": order[5], "date": order[6], "orderNo": order[7], "orderFile": order[8], "invoiceFile": order[9]}
        for order in orders
    ]


    # Return the data as JSON
    return jsonify({
        "customerInfo": customer_info,
        "technicalInfo": technical_info,
        "commercialInfo": commercial_info,
        "contacts": contacts_list,
        "meetings": meetings_list,
        "updates": updates_list,
        "orders": orders_list,
        "actionItems": action_items_list
    })




@app.route('/add_customer', methods=['GET','POST'])
def add_customer():
    
    # Get data from the form
    name = request.form.get('name').title()
    country = request.form.get('country').title()
    address = request.form.get('address')
    lead = request.form.get('lead').capitalize()
    status = request.form.get('status')
    sales_rep = request.form.get('sales_rep').title()
    start_date = request.form.get('start_date')
    # NDA_file = request.files.get('nda_file')
    OT_company = session.get('company_name')

    # NDA_file_name = None
    # if NDA_file:
    #     NDA_file_name = secure_filename(f"{name}_NDA_{NDA_file.filename}")
    #     NDA_file_path = os.path.join(app.config['UPLOAD_FOLDER'], NDA_file_name)
    #     NDA_file.save(NDA_file_path)
    
    line = request.form.get('line').capitalize()
    application = request.form.get('application').capitalize()
    line_speed = request.form.get('line_speed')
    line_width = request.form.get('line_width')
    curing = request.form.get('curing').capitalize()
    targets = request.form.get('targets').capitalize()
    
    annual_volume = request.form.get('annual_volume')
    potential_lines = request.form.get('potential_lines')

    # Insert into the customers table
    customer_query = """
    INSERT INTO customers (Name, Country, Address, Lead, Status, sales_rep, start_date
    , OT_company) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    query(customer_query, (name, country, address, lead, status, sales_rep, start_date, OT_company))

    # Insert into the technical table
    technical_query = """
    INSERT INTO technical (company, line, application, line_speed, line_width, curing, targets, OT_company)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    query(technical_query, (name, line, application, line_speed, line_width, curing, targets, OT_company))

    # Insert into the commercial table
    commercial_query = """
    INSERT INTO commercial (company, annual_volume, lines_amount, OT_company)
    VALUES (?, ?, ?, ?)
    """
    query(commercial_query, (name, annual_volume, potential_lines, OT_company))

    flash(f"Customer {name} has been added successfully.")
    return redirect(url_for('index'))  # חזרה לדף הראשי

@app.route('/add_update', methods=['POST'])
def add_update():
    try:
        content = request.form.get('update').capitalize()
        next_step = request.form.get('next_step').capitalize()
        date = request.form.get('date')
        file = request.files.get('file')
        title= request.form.get('title').title()
        action_items = request.form.get('action_items')
        OT_company = session.get('company_name')

        customer_id = request.form.get('customer_id')
        query_customer = "SELECT Name FROM customers WHERE id = ?"
        customer_name_result = query(query_customer, (customer_id,))
        if customer_name_result:
            customer_name = customer_name_result[0][0]  # Accessing the first tuple and then the first element
        else:
            customer_name = None

        file_name = None
        if file:
            file_name = secure_filename(f"{customer_name}_{date}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            file.save(file_path)

        # Insert into the updates table
        update_query = """
        INSERT INTO updates (company, date, content, next_step, file, title, OT_company)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        query(update_query, (customer_name, date, content, next_step, file_name, title, OT_company))

        fetch_update_id_query = """
                SELECT id FROM updates
                WHERE company = ? AND title = ? AND date = ?
                ORDER BY id DESC LIMIT 1
            """
        result = query(fetch_update_id_query, (customer_name, title, date))
            
        if result:
            update_id = result[0][0]  # Extract the ID
        else:
            print("Error: update ID not found")
            return "Error retrieving update ID", 500  # Handle error properly
            
        if action_items:
            item_category = "update"
            add_action_items(action_items,item_category, update_id, customer_name)

        return jsonify({"success": True, "customer_id": customer_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/add_order', methods=['POST'])
def add_order():
    try:
        material = request.form.get('material').upper()
        amount = request.form.get('amount')
        goal = request.form.get('goal').capitalize()
        notes = request.form.get('notes').capitalize()
        order_no = request.form.get('order_no').title()
        date = request.form.get('date')
        order_file = request.files.get('order_file')
        invoice_file = request.files.get('invoice_file')
        OT_company = session.get('company_name')

            # Query the "customers" table to get the customer name based on the customer ID
        customer_id = request.form.get('customer_id')
        query_customer = "SELECT Name FROM customers WHERE id = ?"
        customer_name_result = query(query_customer, (customer_id,))
        if customer_name_result:
            customer_name = customer_name_result[0][0]  # Accessing the first tuple and then the first element
        else:
            customer_name = None

        order_file_name = None
        if order_file:
            order_file_name = secure_filename(f"{customer_name}_{date}_order_{order_file.filename}")
            order_file_path = os.path.join(app.config['UPLOAD_FOLDER'], order_file_name)
            order_file.save(order_file_path)

        invoice_file_name = None
        if invoice_file:
            invoice_file_name = secure_filename(f"{customer_name}_{date}_invoice_{invoice_file.filename}")
            invoice_file_path = os.path.join(app.config['UPLOAD_FOLDER'], invoice_file_name)
            invoice_file.save(invoice_file_path)


        # Insert into the orders table
        order_query = """
        INSERT INTO orders (company, material, amount, goal, notes, date, order_no, order_file, invoice_file, OT_company)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        query(order_query, (customer_name, material, amount, goal, notes, date, order_no, order_file_name, invoice_file_name, OT_company))

        # Send success response with customer_id
        return jsonify({"success": True, "customer_id": customer_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# @app.route('/edit_update', methods=['POST'])
# def edit_update():
#     update_id = request.form.get('update_id')
#     content = request.form.get('content').capitalize()
#     title = request.form.get('title').title()
#     next_step = request.form.get('next_step').capitalize()
#     responsible = request.form.get('responsible').capitalize()
#     date = request.form.get('date')
#     file = request.files.get('file')

#     current_file = query(f"SELECT file FROM updates WHERE id = {update_id} ")
#     file_data = current_file[0][0]
#     if file:
#         file_name = secure_filename(f"update_{update_id}_{file.filename}")
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
#         file.save(file_path)
#         file_data = file_name

#     update_query = """
#     UPDATE updates
#     SET content = ?, next_step = ?, responsible = ?, date = ?, file = ?, title = ?
#     WHERE id = ?
#     """
#     query(update_query, (content, next_step, responsible, date, file_data, title, update_id))

#     flash("Update edited successfully.")
#     return redirect(f'/customer_choosen?customer_id={request.form.get("customer_id")}')

# @app.route('/edit_order', methods=['POST'])
# def edit_order():
#     order_id = request.form.get('order_id')
#     material = request.form.get('material').upper()
#     amount = request.form.get('amount')
#     goal = request.form.get('goal').capitalize()
#     order_no = request.form.get('order_no')
#     notes = request.form.get('notes').capitalize()
#     date = request.form.get('date')
#     order_file = request.files.get('order_file')
#     invoice_file = request.files.get('invoice_file')

#     # Get the current file content (BLOB) from the database (if applicable)
#     current_order_file = query(f"SELECT order_file FROM orders WHERE id = {order_id} ")
#     current_invoice_file = query(f"SELECT invoice_file FROM orders WHERE id = {order_id} ")

#     order_file_data = current_order_file[0][0]  # Existing file data or None if no file exists
#     if order_file:
#         # If a new order file is uploaded, save it and update the file data
#         order_file_name = secure_filename(f"order_{order_id}_{order_file.filename}")
#         order_file_path = os.path.join(app.config['UPLOAD_FOLDER'], order_file_name)
#         order_file.save(order_file_path)
#         order_file_data = order_file_name  # Set the file name for the new file

#     invoice_file_data = current_invoice_file[0][0]  # Existing invoice file data or None if no file exists
#     if invoice_file:
#         # If a new invoice file is uploaded, save it and update the file data
#         invoice_file_name = secure_filename(f"invoice_{order_id}_{invoice_file.filename}")
#         invoice_file_path = os.path.join(app.config['UPLOAD_FOLDER'], invoice_file_name)
#         invoice_file.save(invoice_file_path)
#         invoice_file_data = invoice_file_name  # Set the file name for the new file

#     # Update the database with the new data or keep the old data if no new file is uploaded
#     order_query = """
#     UPDATE orders
#     SET material = ?, amount = ?, goal = ?, notes = ?, date = ?, order_no = ?, order_file = ?, invoice_file = ?
#     WHERE id = ?
#     """
#     query(order_query, (material, amount, goal, notes, date, order_no, order_file_data, invoice_file_data, order_id))

#     flash("Order edited successfully.")
#     return redirect(f'/customer_choosen?customer_id={request.form.get("customer_id")}')

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    customer_id = request.form.get('customer_id')

    # Step 1: Delete related data in all the other tables
    query("DELETE FROM commercial WHERE company = (SELECT Name FROM customers WHERE id = ?)", (customer_id,))
    query("DELETE FROM contacts WHERE company = (SELECT Name FROM customers WHERE id = ?)", (customer_id,))
    query("DELETE FROM meetings WHERE company = (SELECT Name FROM customers WHERE id = ?)", (customer_id,))
    query("DELETE FROM orders WHERE company = (SELECT Name FROM customers WHERE id = ?)", (customer_id,))
    query("DELETE FROM technical WHERE company = (SELECT Name FROM customers WHERE id = ?)", (customer_id,))
    query("DELETE FROM updates WHERE company = (SELECT Name FROM customers WHERE id = ?)", (customer_id,))
    query("DELETE FROM action_items WHERE customer = (SELECT Name FROM customers WHERE id = ?)", (customer_id,))

    # Step 2: Delete the customer itself
    query("DELETE FROM customers WHERE id = ?", (customer_id,))
    
    return redirect(url_for('index'))
    
# Update technical

@app.route('/update_customer_details', methods=['POST'])
def update_customer_details():
    customer_id = request.form.get('customer_id')
    name = request.form.get('companyName').title()
    country = request.form.get('country').title()
    address = request.form.get('address')
    lead = request.form.get('lead').title()
    status = request.form.get('status')
    sales_rep = request.form.get('sales_rep').title()
    start_date = request.form.get('startDate')
    NDA_file = request.files.get('ndaFile')

    query_customer = "SELECT Name FROM customers WHERE id = ?"
    customer_name_result = query(query_customer, (customer_id,))

    # If the customer is found, assign the customer name, otherwise set it to None
    if customer_name_result:
        customer_name = customer_name_result[0][0]  # Accessing the first tuple and then the first element
    else:
        customer_name = None

    # current_nda_file = query(f"SELECT nda_file FROM customers WHERE id = {customer_id} ")
    # current_file_data = current_nda_file[0][0]

    # NDA_file_name = None
    # if NDA_file:
    #     NDA_file_name = secure_filename(f"{name}_NDA_{NDA_file.filename}")
    #     NDA_file_path = os.path.join(app.config['UPLOAD_FOLDER'], NDA_file_name)
    #     NDA_file.save(NDA_file_path)
    #     current_file_data = NDA_file_name

    # Update customer details
    query("""
        UPDATE customers
        SET Name = ?, Country = ?, Address = ?, Status = ?, start_date = ?, lead = ?, sales_rep = ?
        WHERE id = ?
    """, (name, country, address, status, start_date, lead, sales_rep, customer_id))

    
    line = request.form.get('line').upper()
    application = request.form.get('application').title()
    line_speed = request.form.get('lineSpeed')
    line_width = request.form.get('lineWidth').upper()
    curing = request.form.get('curingStatus')
    targets = request.form.get('targets')
    query("""
                UPDATE technical
                SET line = ?, application = ?, line_speed = ?, line_width = ?, curing = ?, targets = ?
                WHERE company = ?
            """, (line, application, line_speed, line_width, curing, targets, customer_name))


    annual_volume = request.form.get(f'annualVolume')
    potential_lines = request.form.get(f'linesAmount')

    query("""
                UPDATE commercial
                SET annual_volume = ?, lines_amount = ?
                WHERE company = ?
            """, (annual_volume, potential_lines, customer_name))


    flash("Customer details updated successfully.")
    return jsonify({"success": True, "customer_id": customer_id})  # Send JSON response

@app.route('/add_contact', methods=['POST'])
def add_contact():
    try:
        # Get the data from the form
        contact_name = request.form['contact_name'].title()
        contact_email = request.form['contact_email']
        contact_phone = request.form['contact_phone']
        contact_role = request.form['contact_role'].title()
        OT_company = session.get('company_name')

        # Query the "customers" table to get the customer name based on the customer ID
        customer_id = request.form.get('customer_id')
        query_customer = "SELECT Name FROM customers WHERE id = ?"
        customer_name_result = query(query_customer, (customer_id,))
        if customer_name_result:
            customer_name = customer_name_result[0][0]  # Accessing the first tuple and then the first element
        else:
            customer_name = None

        # Insert the contact into the "contacts" table
        contact_query = """
            INSERT INTO contacts (name, phone, email, role, company, OT_company)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        query(contact_query, (contact_name, contact_phone, contact_email, contact_role, customer_name, OT_company))

        # Send success response with customer_id
        return jsonify({"success": True, "customer_id": customer_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    try:
        # Get customer_id from form data
        customer_id = request.form.get('customer_id')

        # Delete the contact from the database
        delete_query = "DELETE FROM contacts WHERE id = ?"
        query(delete_query, (contact_id,))

        # Send the response with success flag and customer_id
        return redirect(url_for('index'))  # חזרה לדף הראשי

    except Exception as e:
        print("Error deleting contact:", str(e))  # Log error
        return jsonify({"success": False, "error": str(e)}), 500  # Return JSON error

@app.route('/add_meeting', methods=['POST'])
def add_meeting():
    try:
        title = request.form.get('title').title()
        attendees = request.form.get('attendees')
        date = request.form.get('date')
        summary = request.form.get('summary').capitalize()
        OT_company = session.get('company_name')

        # Query the "customers" table to get the customer name based on the customer ID
        customer_id = request.form.get('customer_id')
        query_customer = "SELECT Name FROM customers WHERE id = ?"
        customer_name_result = query(query_customer, (customer_id,))
        if customer_name_result:
            customer_name = customer_name_result[0][0]  # Accessing the first tuple and then the first element
        else:
            customer_name = None
        # Get the action items from the form (it will be a JSON string)
        action_items = request.form.get('action_items')

        # Prepare the SQL query to insert the meeting details
        meeting_query = """
            INSERT INTO meetings (company, title, date, attendees, summary, OT_company)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        query(meeting_query, (customer_name, title, date, attendees, summary, OT_company))

            # Retrieve the last inserted meeting by filtering with unique values
        fetch_meeting_id_query = """
            SELECT id FROM meetings
            WHERE company = ? AND title = ? AND date = ?
            ORDER BY id DESC LIMIT 1
        """
        result = query(fetch_meeting_id_query, (customer_name, title, date))
        
        if result:
            meeting_id = result[0][0]  # Extract the ID
        else:
            print("Error: Meeting ID not found")
            return "Error retrieving meeting ID", 500  # Handle error properly
        
        if action_items:
            item_category = "meeting"
            add_action_items(action_items,item_category, meeting_id, customer_name)

        return jsonify({"success": True, "customer_id": customer_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def add_action_items(action_items,item_category, meeting_id, customer_name):
    # Parse action_items from JSON string to a list of dictionaries
    action_items = json.loads(action_items)
    OT_company = session.get('company_name')

    action_item_query = """
    INSERT INTO action_items (customer, item, responsible, due_date, status, item_category, category_id, OT_company)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Loop through each action item and insert it into the action_items table
    for item in action_items:
        query(action_item_query, (
            customer_name,
            item['item'].title(),
            item['responsible'].title(),
            item['due_date'],
            item['status'],
            item_category,
            meeting_id,
            OT_company
        ))



@app.route('/delete_meeting', methods=['POST'])
def delete_meeting():
    try:
        meeting_id = request.form.get('meeting_id')

        delete_action_items_query = "DELETE FROM action_items WHERE category_id = ? AND item_category = 'meeting'"
        query(delete_action_items_query, (meeting_id,))

        delete_query = "DELETE FROM meetings WHERE id = ?"
        query(delete_query, (meeting_id,))

        # Send the response with success flag and customer_id/
        return redirect(url_for('index'))  # חזרה לדף הראשי
    except Exception as e:
        print("Error deleting meeting:", str(e))  # Log error
        return jsonify({"success": False, "error": str(e)}), 500  # Return JSON error

@app.route('/delete_order', methods=['POST'])
def delete_order():
    try:
        order_id = request.form.get('order_id')
        delete_query = "DELETE FROM orders WHERE id = ?"
        query(delete_query, (order_id,))

        # Send the response with success flag and customer_id
        return redirect(url_for('index'))  # חזרה לדף הראשי

    except Exception as e:
        print("Error deleting order:", str(e))  # Log error
        return jsonify({"success": False, "error": str(e)}), 500  # Return JSON error

@app.route('/delete_update', methods=['POST'])
def delete_update():
    try:
        update_id = request.form.get('update_id')

        delete_action_items_query = "DELETE FROM action_items WHERE category_id = ? AND item_category = 'update'"
        query(delete_action_items_query, (update_id,))

        delete_query = "DELETE FROM updates WHERE id = ?"
        query(delete_query, (update_id,))

        return redirect(url_for('index'))  # חזרה לדף הראשי

    except Exception as e:
        print("Error deleting order:", str(e))  # Log error
        return jsonify({"success": False, "error": str(e)}), 500  # Return JSON error

@app.route('/edit_contact', methods=['POST'])
def edit_contact():
    try:
        contact_id = request.form.get('contact_id')
        name = request.form.get('contact_name').title()
        phone = request.form.get('contact_phone')
        email = request.form.get('contact_email')
        role = request.form.get('contact_role').title()
        customer_id = request.form.get('customer_id')

        if not contact_id:
            return jsonify({"success": False, "error": "Missing contact ID"}), 400

        # Update the database
        update_query = """
        UPDATE contacts
        SET name = ?, phone = ?, email = ?, role = ?
        WHERE id = ?
        """
        query(update_query, (name, phone, email, role, contact_id))

        return jsonify({"success": True, "customer_id": customer_id})  # Send JSON response

    except Exception as e:
        print("Error updating contact:", str(e))  # Log error in terminal
        return jsonify({"success": False, "error": str(e)}), 500  # Return JSON error


# @app.route('/edit_meeting', methods=['POST'])
# def edit_meeting():
#     meeting_id = request.form.get('meeting_id')
#     title = request.form.get('title').title()
#     date = request.form.get('date')
#     attendees = request.form.get('attendees')
#     summary = request.form.get('summary').capitalize()
#     customer_id = request.form.get('customer_id')

#     # Update the database
#     update_query = """
#     UPDATE meetings
#     SET title = ?, date = ?, attendees = ?, summary = ?
#     WHERE id = ?
#     """
#     query(update_query, (title, date, attendees, summary, meeting_id))

#     flash("Meeting updated successfully.")
#     return redirect(f'/customer_choosen?customer_id={customer_id}')


# @app.route('/edit_action_items', methods=['POST'])
# def edit_action_items():
#     action_item_ids = request.form.getlist('action_item_id[]')
#     items = request.form.getlist('item[]')
#     responsibles = request.form.getlist('responsible[]')
#     due_dates = request.form.getlist('due_date[]')
#     statuses = request.form.getlist('status[]')
    
#     update_query = """
#     UPDATE action_items
#     SET item = ?, responsible = ?, due_date = ?, status = ?
#     WHERE id = ?
#     """
    
#     # Loop through each action item and update it
#     for idx, action_item_id in enumerate(action_item_ids):
#         query(update_query, (
#             items[idx].capitalize(),
#             responsibles[idx].title(),
#             due_dates[idx],
#             statuses[idx],
#             action_item_id
#         ))
    
#     flash("Action items updated successfully.")
#     return redirect(url_for('dashboard'))


# def generate_meeting_email(meeting_id):
#     # Fetch meeting details from the database (replace with actual query)
#     meeting = query(f"SELECT * FROM meetings WHERE id = {meeting_id}")[0]
    
#     if not meeting:
#         return jsonify({"error": "Meeting not found"}), 404
    
#     meeting_title = meeting[2]
#     meeting_date = meeting[3]
#     attendees = meeting[4]
#     summary = meeting[5]
#     action_items = meeting[6] or []

#     action_items_table = "<table><thead><tr><th>Item</th><th>Responsible</th><th>Due Date</th><th>Status</th></tr></thead><tbody>"
#     for item in action_items:
#         # If item is just a string, you need a different structure for responsible, due_date, etc.
#         action_items_table += f"<tr><td>{item}</td><td>N/A</td><td>N/A</td><td>Pending</td></tr>"
#     action_items_table += "</tbody></table>"
    
#     # Prepare the email body content
#     email_body = f"""
#         <h3><b>{meeting_title}</b></h3>
#         <p><strong>Date:</strong> {meeting_date}</p>
#         <p><strong>Attendees:</strong> {attendees}</p>
#         <p><strong>Action Items:</strong></p>
#         {action_items_table}
#         <p><strong>Summary:</strong> {summary}</p>
#     """
    
#     return email_body, meeting_title

# sender_email = os.environ.get("SENDER_EMAIL")
# sender_password = os.environ.get("SENDER_PASSWORD")

# def send_email_via_gmail(meeting_id, recipient_email):
#     # Generate the meeting details
#     email_body, meeting_title = generate_meeting_email(meeting_id)
#     sender_email = "ofirital0@gmail.com"
#     sender_password = "jbkd kdad urcr xdee"
#     receiver_email = "ofirital0@gmail.com"

#     # Create the message
#     msg = MIMEMultipart('alternative')  # Set the email to send both plain text and HTML
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = f"Meeting: {meeting_title}"

#     # Attach the body content (HTML)
#     msg.attach(MIMEText("This email requires HTML support.", 'plain'))  # Fallback for non-HTML email clients
#     msg.attach(MIMEText(email_body, 'html'))
    
#     # Send the email via Gmail SMTP server
#     try:
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()  # Secure the connection
#             server.login(sender_email, sender_password)
#             server.send_message(msg)
#             print("Email sent successfully!")
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return jsonify({"error": "Email not sent"}), 500
    
#     return "Email sent successfully!", 200


# @app.route('/send_email/<int:meeting_id>', methods=['POST'])
# def send_email(meeting_id):
#     # Assuming recipient_email is passed in the form or is hardcoded
#     recipient_email = "ofir@n3cure.com"  # Replace with actual recipient email
#     return send_email_via_gmail(meeting_id, recipient_email)