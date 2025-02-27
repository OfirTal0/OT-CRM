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

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'static/uploads'


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory where app.py is located
DATABASE_PATH = os.path.join(BASE_DIR, 'n3cure_crm.db')  # Make sure 'petforme.db' matches your SQLite database file name

app.secret_key = os.getenv('SECRET_KEY','default_secret_key')


def get_redirect_uri():
    host = request.host
    scheme = "https" if "railway.app" in host else request.scheme
    return f"{scheme}://{host}/auth/callback"


CLIENT_ID = 'f015ff07-5ad0-4a4a-9959-8fb45bf46e52'
CLIENT_SECRET = 'gB.8Q~~PoWp4tU7qicQjXnWfwywyxbJ17PTtFcsy'
TENANT_ID = '2f359e1f-c37b-4267-a0c0-5110b8b578ba'
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPES = ['User.Read']  # גישה לקריאת פרטי משתמש

# רשימת אימיילים מורשים
ALLOWED_EMAILS = ['ofir@n3cure.com', 'yoram@n3cure.com', 'danny@n3cure.com']


def build_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

@app.route('/api/download_db', methods=['GET'])
def download_db():
    return send_file('n3cure_crm.db', as_attachment=True)

@app.route('/download_static', methods=['GET'])
def download_static():
    # Zip the static directory
    shutil.make_archive('static_files', 'zip', 'static')
    return send_file('static_files.zip', as_attachment=True)


@app.route('/login')
@app.route('/login')
def login():
    msal_app = build_msal_app()
    auth_url = msal_app.get_authorization_request_url(SCOPES, redirect_uri=get_redirect_uri())
    return redirect(auth_url)


@app.route('/auth/callback')
def auth_callback():
    msal_app = build_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        request.args['code'],
        scopes=SCOPES,
        redirect_uri=get_redirect_uri()  # משתמש ב-redirect הדינמי
    )

    if "access_token" in result:
        user_info = result.get('id_token_claims')
        user_email = user_info.get('preferred_username')

        if user_email in ALLOWED_EMAILS:
            session['user'] = user_info
            return redirect(url_for('index'))
        else:
            return "You are not authorized to access this application.", 403

    return 'Authentication failed', 400
@app.route('/logout')
def logout():
    session.clear()  # מחיקת הסשן
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

def query(sql: str = "", params: tuple = (), db_name=DATABASE_PATH):
    try:
        with sqlite3.connect(db_name) as conn:
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
def index():
    if 'user' not in session:
        return redirect(url_for('login'))  # אם אין אימות, הפנה לאימות

    customers = query("SELECT * FROM customers ORDER BY name ASC")
    action_items = query(f"SELECT * FROM action_items")
    contacts_display = query(f"SELECT * FROM contacts")
    return render_template('index.html', customers=customers,action_items=action_items, contacts_display=contacts_display)

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if 'user' not in session:
        return redirect(url_for('login'))  # אם אין אימות, הפנה לאימות

    contacts_display = query(f"SELECT * FROM contacts")
    return render_template('contacts.html', contacts=contacts_display)


@app.route('/customer_choosen', methods=['POST', 'GET'])
def customer_choosen():
    customer_id = request.form.get('customer_id') or request.args.get('customer_id')
    customer_name = request.form.get('customer_name') or request.args.get('customer_name')
    item_category =request.form.get('item_category')or request.args.get('item_category')
    category_id = request.form.get('category_id')  or request.args.get('category_id')

    # If customer_name is provided, query for customer_id
    if not customer_id and customer_name:
        customer_id_query = "SELECT id FROM customers WHERE name = ?"
        customer_id_result = query(customer_id_query, (customer_name,))
        if not customer_id_result:
            return "Customer not found", 404
        customer_id = customer_id_result[0][0]  # Assuming the result is [(id,)]

    if not customer_id:
        return "Customer not found", 404

    # Fetch customer details
    customer_query = "SELECT * FROM customers WHERE id = ?"
    customer = query(customer_query, (customer_id,))
    if not customer:
        return "Customer not found", 404

    # Fetch related data
    contacts_query = "SELECT * FROM contacts WHERE company = ?"
    contacts = query(contacts_query, (customer[0][1],))

    meetings_query = "SELECT * FROM meetings WHERE company = ? ORDER BY date DESC"
    meetings = query(meetings_query, (customer[0][1],))

    updates_query = "SELECT * FROM updates WHERE company = ? ORDER BY date DESC"
    updates = query(updates_query, (customer[0][1],))

    technical_query = "SELECT * FROM technical WHERE company = ?"
    technical = query(technical_query, (customer[0][1],))

    commercial_query = "SELECT * FROM commercial WHERE company = ?"
    commercial = query(commercial_query, (customer[0][1],))

    orders_query = "SELECT * FROM orders WHERE company = ? ORDER BY date DESC"
    orders = query(orders_query, (customer[0][1],))

    action_items_query = "SELECT * FROM action_items WHERE customer = ?"
    action_items = query(action_items_query, (customer[0][1],))


    # Redirect with anchor to #meeting section
    return render_template(
        'index.html',
        customers=query("SELECT * FROM customers ORDER BY name ASC"),
        selected_customer=customer[0],
        contacts=contacts,
        updates=updates,
        technical=technical,
        commercial=commercial,
        orders=orders,
        meetings=meetings,
        category_id=category_id,
        item_category= item_category,
        action_items=action_items  # Passing action items to the template

    )


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
    NDA_file = request.files.get('nda_file')

    NDA_file_name = None
    if NDA_file:
        NDA_file_name = secure_filename(f"{name}_NDA_{NDA_file.filename}")
        NDA_file_path = os.path.join(app.config['UPLOAD_FOLDER'], NDA_file_name)
        NDA_file.save(NDA_file_path)
    
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
    INSERT INTO customers (Name, Country, Address, Lead, Status, sales_rep, start_date, NDA_file) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    query(customer_query, (name, country, address, lead, status, sales_rep, start_date, NDA_file_name))

    # Insert into the technical table
    technical_query = """
    INSERT INTO technical (company, line, application, line_speed, line_width, curing, targets)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    query(technical_query, (name, line, application, line_speed, line_width, curing, targets))

    # Insert into the commercial table
    commercial_query = """
    INSERT INTO commercial (company, annual_volume, lines_amount)
    VALUES (?, ?, ?)
    """
    query(commercial_query, (name, annual_volume, potential_lines))

    flash(f"Customer {name} has been added successfully.")
    return index()  

@app.route('/add_update', methods=['POST'])
def add_update():
    customer_id = request.form.get('customer_id')  # Get the customer ID
    company = request.form.get('company').capitalize()
    content = request.form.get('update').capitalize()
    next_step = request.form.get('next_step').capitalize()
    date = request.form.get('date')
    file = request.files.get('file')
    title= request.form.get('title').title()
    action_items = request.form.get('update_action_items')

    file_name = None
    if file:
        file_name = secure_filename(f"{company}_{date}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)

    # Insert into the updates table
    update_query = """
    INSERT INTO updates (company, date, content, next_step, file, title)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    query(update_query, (company, date, content, next_step, file_name, title))

    fetch_update_id_query = """
            SELECT id FROM updates
            WHERE company = ? AND title = ? AND date = ?
            ORDER BY id DESC LIMIT 1
        """
    result = query(fetch_update_id_query, (company, title, date))
        
    if result:
        update_id = result[0][0]  # Extract the ID
    else:
        print("Error: Meeting ID not found")
        return "Error retrieving meeting ID", 500  # Handle error properly
        
    if action_items:
        item_category = "update"
        add_action_items(action_items,item_category, update_id)

    flash(f"Update for {company} added successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')


@app.route('/add_order', methods=['POST'])
def add_order():
    customer_id = request.form.get('customer_id')  # Get the customer ID
    company = request.form.get('company').capitalize()
    material = request.form.get('material').upper()
    amount = request.form.get('amount')
    goal = request.form.get('goal').capitalize()
    notes = request.form.get('notes').capitalize()
    order_no = request.form.get('order_no').title()
    date = request.form.get('date')
    order_file = request.files.get('order_file')
    invoice_file = request.files.get('invoice_file')

    order_file_name = None
    if order_file:
        order_file_name = secure_filename(f"{company}_{date}_order_{order_file.filename}")
        order_file_path = os.path.join(app.config['UPLOAD_FOLDER'], order_file_name)
        order_file.save(order_file_path)

    invoice_file_name = None
    if invoice_file:
        invoice_file_name = secure_filename(f"{company}_{date}_invoice_{invoice_file.filename}")
        invoice_file_path = os.path.join(app.config['UPLOAD_FOLDER'], invoice_file_name)
        invoice_file.save(invoice_file_path)

    # Insert into the orders table
    order_query = """
    INSERT INTO orders (company, material, amount, goal, notes, date, order_no, order_file, invoice_file)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    query(order_query, (company, material, amount, goal, notes, date, order_no, order_file_name, invoice_file_name))

    flash(f"Order for {company} added successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')


@app.route('/edit_update', methods=['POST'])
def edit_update():
    update_id = request.form.get('update_id')
    content = request.form.get('content').capitalize()
    title = request.form.get('title').title()
    next_step = request.form.get('next_step').capitalize()
    responsible = request.form.get('responsible').capitalize()
    date = request.form.get('date')
    file = request.files.get('file')

    current_file = query(f"SELECT file FROM updates WHERE id = {update_id} ")
    file_data = current_file[0][0]
    if file:
        file_name = secure_filename(f"update_{update_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)
        file_data = file_name

    update_query = """
    UPDATE updates
    SET content = ?, next_step = ?, responsible = ?, date = ?, file = ?, title = ?
    WHERE id = ?
    """
    query(update_query, (content, next_step, responsible, date, file_data, title, update_id))

    flash("Update edited successfully.")
    return redirect(f'/customer_choosen?customer_id={request.form.get("customer_id")}')

@app.route('/edit_order', methods=['POST'])
def edit_order():
    order_id = request.form.get('order_id')
    material = request.form.get('material').upper()
    amount = request.form.get('amount')
    goal = request.form.get('goal').capitalize()
    order_no = request.form.get('order_no')
    notes = request.form.get('notes').capitalize()
    date = request.form.get('date')
    order_file = request.files.get('order_file')
    invoice_file = request.files.get('invoice_file')

    # Get the current file content (BLOB) from the database (if applicable)
    current_order_file = query(f"SELECT order_file FROM orders WHERE id = {order_id} ")
    current_invoice_file = query(f"SELECT invoice_file FROM orders WHERE id = {order_id} ")

    order_file_data = current_order_file[0][0]  # Existing file data or None if no file exists
    if order_file:
        # If a new order file is uploaded, save it and update the file data
        order_file_name = secure_filename(f"order_{order_id}_{order_file.filename}")
        order_file_path = os.path.join(app.config['UPLOAD_FOLDER'], order_file_name)
        order_file.save(order_file_path)
        order_file_data = order_file_name  # Set the file name for the new file

    invoice_file_data = current_invoice_file[0][0]  # Existing invoice file data or None if no file exists
    if invoice_file:
        # If a new invoice file is uploaded, save it and update the file data
        invoice_file_name = secure_filename(f"invoice_{order_id}_{invoice_file.filename}")
        invoice_file_path = os.path.join(app.config['UPLOAD_FOLDER'], invoice_file_name)
        invoice_file.save(invoice_file_path)
        invoice_file_data = invoice_file_name  # Set the file name for the new file

    # Update the database with the new data or keep the old data if no new file is uploaded
    order_query = """
    UPDATE orders
    SET material = ?, amount = ?, goal = ?, notes = ?, date = ?, order_no = ?, order_file = ?, invoice_file = ?
    WHERE id = ?
    """
    query(order_query, (material, amount, goal, notes, date, order_no, order_file_data, invoice_file_data, order_id))

    flash("Order edited successfully.")
    return redirect(f'/customer_choosen?customer_id={request.form.get("customer_id")}')

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
    name = request.form.get('name').title()
    country = request.form.get('country').title()
    address = request.form.get('address')
    lead = request.form.get('lead').title()
    status = request.form.get('status')
    sales_rep = request.form.get('sales_rep').title()
    start_date = request.form.get('start_date')
    NDA_file = request.files.get('nda_file')


    current_nda_file = query(f"SELECT nda_file FROM customers WHERE id = {customer_id} ")
    current_file_data = current_nda_file[0][0]

    NDA_file_name = None
    if NDA_file:
        NDA_file_name = secure_filename(f"{name}_NDA_{NDA_file.filename}")
        NDA_file_path = os.path.join(app.config['UPLOAD_FOLDER'], NDA_file_name)
        NDA_file.save(NDA_file_path)
        current_file_data = NDA_file_name

    # Update customer details
    query("""
        UPDATE customers
        SET Name = ?, Country = ?, Address = ?, Lead = ?, Status = ?, sales_rep = ?, start_date = ?, NDA_file = ?
        WHERE id = ?
    """, (name, country, address, lead, status, sales_rep, start_date, current_file_data, customer_id))

    
    # Update technical data
    for key, value in request.form.items():
        if key.startswith('technical_id_'):
            technical_id = value
            index = key.split('_')[-1]
            line = request.form.get(f'line_{index}').capitalize()
            application = request.form.get(f'application_{index}').capitalize()
            line_speed = request.form.get(f'line_speed_{index}')
            line_width = request.form.get(f'line_width_{index}')
            curing = request.form.get(f'curing_{index}').capitalize()
            targets = request.form.get(f'targets_{index}').capitalize()
            query("""
                UPDATE technical
                SET line = ?, application = ?, line_speed = ?, line_width = ?, curing = ?, targets = ?
                WHERE id = ?
            """, (line, application, line_speed, line_width, curing, targets, technical_id))


    commercial_id = request.form.get('commercial_id')
    if commercial_id:
        annual_volume = request.form.get(f'annual_volume')
        potential_lines = request.form.get(f'potential_lines')

        query("""
                UPDATE commercial
                SET annual_volume = ?, lines_amount = ?
                WHERE id = ?
            """, (annual_volume, potential_lines, commercial_id))
    else: 

        company_name = name  # Assuming 'name' is the company name in the customers table
        annual_volume = request.form.get('annual_volume')
        potential_lines = request.form.get('potential_lines')

        query("""
            INSERT INTO commercial (company, annual_volume, lines_amount)
            VALUES (?, ?, ?)
        """, (company_name, annual_volume, potential_lines))

    flash("Customer details updated successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')

@app.route('/add_contact', methods=['POST'])
def add_contact():
    # Get the data from the form
    customer_id = request.form.get('customer_id')
    contact_name = request.form['contact_name'].title()
    contact_email = request.form['contact_email']
    contact_phone = request.form['contact_phone']
    contact_role = request.form['contact_role'].title()
    company= request.form.get('company')

    contact_query = """
        INSERT INTO contacts (name, phone, email, role, company)
        VALUES (?, ?, ?, ?, ?)
    """
    query(contact_query, (contact_name, contact_phone, contact_email, contact_role, company))

    return redirect(f'/customer_choosen?customer_id={customer_id}')


@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    # Delete the meeting from the database
    customer_id = request.form.get('customer_id')
    delete_query = "DELETE FROM contacts WHERE id = ?"
    query(delete_query, (contact_id,))

    return redirect(f'/customer_choosen?customer_id={customer_id}')



@app.route('/add_meeting', methods=['POST'])
def add_meeting():
    customer_id = request.form.get('customer_id')
    company = request.form.get('company')
    title = request.form.get('title').title()
    attendees = request.form.get('attendees')
    date = request.form.get('date')
    summary = request.form.get('summary').capitalize()
    
    # Get the action items from the form (it will be a JSON string)
    action_items = request.form.get('action_items')

    # Prepare the SQL query to insert the meeting details
    meeting_query = """
        INSERT INTO meetings (company, title, date, attendees, summary)
        VALUES (?, ?, ?, ?, ?)
    """

    query(meeting_query, (company, title, date, attendees, summary))

        # Retrieve the last inserted meeting by filtering with unique values
    fetch_meeting_id_query = """
        SELECT id FROM meetings
        WHERE company = ? AND title = ? AND date = ?
        ORDER BY id DESC LIMIT 1
    """
    result = query(fetch_meeting_id_query, (company, title, date))
    
    if result:
        meeting_id = result[0][0]  # Extract the ID
    else:
        print("Error: Meeting ID not found")
        return "Error retrieving meeting ID", 500  # Handle error properly
    
    if action_items:
        item_category = "meeting"
        add_action_items(action_items,item_category, meeting_id)

    return redirect(f'/customer_choosen?customer_id={customer_id}')

def add_action_items(action_items,item_category, meeting_id):
    # Parse action_items from JSON string to a list of dictionaries
    action_items = json.loads(action_items)
    
    action_item_query = """
    INSERT INTO action_items (customer, item, responsible, due_date, status, item_category, category_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    # Loop through each action item and insert it into the action_items table
    for item in action_items:
        query(action_item_query, (
            item['customer'],
            item['item'],
            item['responsible'],
            item['due_date'],
            item['status'],
            item_category,
            meeting_id  # Use the meeting_id as category_id
        ))

@app.route('/delete_action_item/<int:action_item_id>', methods=['POST'])
def delete_action_item(action_item_id):
    delete_query = "DELETE FROM action_items WHERE id = ?"
    query(delete_query, (action_item_id,))
    return redirect(url_for('index'))


@app.route('/delete_meeting/<int:meeting_id>', methods=['POST'])
def delete_meeting(meeting_id):
    # Delete the meeting from the database
    customer_id = request.form.get('customer_id')

    delete_action_items_query = "DELETE FROM action_items WHERE category_id = ? AND item_category = 'meeting'"
    query(delete_action_items_query, (meeting_id,))

    delete_query = "DELETE FROM meetings WHERE id = ?"
    query(delete_query, (meeting_id,))

    flash("Meeting deleted successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def deleteorder(order_id):
    customer_id = request.form.get('customer_id')
    delete_query = "DELETE FROM orders WHERE id = ?"
    query(delete_query, (order_id,))

    flash("Order deleted successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')

@app.route('/delete_update/<int:update_id>', methods=['POST'])
def deleteupdate(update_id):
    customer_id = request.form.get('customer_id')

    delete_action_items_query = "DELETE FROM action_items WHERE category_id = ? AND item_category = 'update'"
    query(delete_action_items_query, (update_id,))

    delete_query = "DELETE FROM updates WHERE id = ?"
    query(delete_query, (update_id,))

    flash("Update deleted successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')


@app.route('/edit_contact', methods=['POST'])
def edit_contact():
    contact_id = request.form.get('contact_id')
    name = request.form.get('contact_name').title()
    phone = request.form.get('contact_phone')
    email = request.form.get('contact_email')
    role = request.form.get('contact_role').title()
    customer_id = request.form.get('customer_id')

    # Update the database
    update_query = """
    UPDATE contacts
    SET name = ?, phone = ?, email = ?, role = ?
    WHERE id = ?
    """
    query(update_query, (name, phone, email, role, contact_id))

    flash("Contact updated successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')



@app.route('/edit_meeting', methods=['POST'])
def edit_meeting():
    meeting_id = request.form.get('meeting_id')
    title = request.form.get('title').title()
    date = request.form.get('date')
    attendees = request.form.get('attendees')
    summary = request.form.get('summary').capitalize()
    customer_id = request.form.get('customer_id')

    # Update the database
    update_query = """
    UPDATE meetings
    SET title = ?, date = ?, attendees = ?, summary = ?
    WHERE id = ?
    """
    query(update_query, (title, date, attendees, summary, meeting_id))

    flash("Meeting updated successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')


@app.route('/edit_action_items', methods=['POST'])
def edit_action_items():
    action_item_ids = request.form.getlist('action_item_id[]')
    items = request.form.getlist('item[]')
    responsibles = request.form.getlist('responsible[]')
    due_dates = request.form.getlist('due_date[]')
    statuses = request.form.getlist('status[]')
    
    update_query = """
    UPDATE action_items
    SET item = ?, responsible = ?, due_date = ?, status = ?
    WHERE id = ?
    """
    
    # Loop through each action item and update it
    for idx, action_item_id in enumerate(action_item_ids):
        query(update_query, (
            items[idx].capitalize(),
            responsibles[idx].title(),
            due_dates[idx],
            statuses[idx],
            action_item_id
        ))
    
    flash("Action items updated successfully.")
    return redirect(url_for('index'))


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