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


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'static/uploads'


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory where app.py is located
DATABASE_PATH = os.path.join(BASE_DIR, 'n3cure_crm.db')  # Make sure 'petforme.db' matches your SQLite database file name

app.secret_key = os.getenv('SECRET_KEY','default_secret_key')

# הגדרת פרטי התחברות
USERNAME = "n3cure"
PASSWORD = "n3cure!"

# זמן תוקף הסשן (24 שעות)
SESSION_TIMEOUT = timedelta(hours=24)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # אימות שם משתמש וסיסמה (כמובן, יש לשדרג את זה עם מנגנון אבטחה חזק יותר)
        if username == "n3cure" and password == "n3cure!":
            # שמירת זמן הלוגין בסשן
            session['login_time'] = datetime.now().replace(tzinfo=None)  # הסרת אזור הזמן אם יש
            return redirect(url_for('index'))  # הפניה לדף הבית אם ההתחברות הצליחה
        else:
            flash("שם משתמש או סיסמה שגויים")
            return redirect(url_for('login'))

    if 'login_time' in session:
        # לוודא שהתאריך יהיה naive
        login_time = session['login_time']
        if isinstance(login_time, datetime):
            login_time = login_time.replace(tzinfo=None)  # הסרת אזור הזמן אם יש

        if datetime.now().replace(tzinfo=None) - login_time > SESSION_TIMEOUT:
            # אם הזמן עבר 24 שעות, מחיקת הסשן
            session.pop('login_time', None)
            flash('הסשן פג, יש להיכנס שוב')
            return redirect(url_for('login'))
        return redirect(url_for('index'))
    
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()  # מחיקת הסשן
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

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
    

@app.route('/index', methods=['GET', 'POST'])
def index():

    customers = query("SELECT * FROM customers")
    meetings = query(f"SELECT * FROM meetings ORDER BY date DESC")

    # Convert meetings to a mutable format and deserialize the action_items JSON
    updated_meetings = []
    for meeting in meetings:
        meeting_list = list(meeting)  # Convert tuple to list
        if meeting_list[6]:  # Assuming action_items is at index 6
            try:
                meeting_list[6] = json.loads(meeting_list[6])  # Deserialize JSON
            except json.JSONDecodeError:
                meeting_list[6] = []  # Default to an empty list if JSON is invalid
        updated_meetings.append(tuple(meeting_list))  # Convert back to tuple if necessary

    return render_template('index.html', customers=customers,meetings=updated_meetings)

@app.route('/customer_choosen', methods=['POST', 'GET'])
def customer_choosen():
    customer_id = request.form.get('customer_id') or request.args.get('customer_id')
    customer_name = request.form.get('customer_name') or request.args.get('customer_name')

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

    # Convert meetings to a mutable format and deserialize the action_items JSON
    updated_meetings = []
    for meeting in meetings:
        meeting_list = list(meeting)
        if meeting_list[6]:
            try:
                meeting_list[6] = json.loads(meeting_list[6])  # Deserialize JSON
            except json.JSONDecodeError:
                meeting_list[6] = []  # Default to an empty list if JSON is invalid
        updated_meetings.append(tuple(meeting_list))

    updates_query = "SELECT * FROM updates WHERE company = ? ORDER BY date DESC"
    updates = query(updates_query, (customer[0][1],))

    technical_query = "SELECT * FROM technical WHERE company = ?"
    technical = query(technical_query, (customer[0][1],))

    commercial_query = "SELECT * FROM commercial WHERE company = ?"
    commercial = query(commercial_query, (customer[0][1],))

    orders_query = "SELECT * FROM orders WHERE company = ? ORDER BY date DESC"
    orders = query(orders_query, (customer[0][1],))

    # Redirect with anchor to #meeting section
    return render_template(
        'index.html',
        customers=query("SELECT * FROM customers"),
        selected_customer=customer[0],
        contacts=contacts,
        updates=updates,
        technical=technical,
        commercial=commercial,
        orders=orders,
        meetings=updated_meetings,
    )

@app.route('/add_customer', methods=['GET','POST'])
def add_customer():
    # Get data from the form
    name = request.form.get('name').title()
    country = request.form.get('country').title()
    address = request.form.get('address')
    lead = request.form.get('lead').capitalize()
    status = request.form.get('status').capitalize()
    contact_name = request.form.get('contact_name').title()
    role = request.form.get('role').capitalize()
    email = request.form.get('email')
    phone = request.form.get('phone')
    
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
    INSERT INTO customers (Name, Country, Address, Lead, Status) VALUES (?, ?, ?, ?, ?)
    """
    query(customer_query, (name, country, address, lead, status))

    # Insert into the contacts table
    contact_query = """
    INSERT INTO contacts (name, phone, email, role, company) VALUES (?, ?, ?, ?, ?)
    """
    query(contact_query, (contact_name, phone, email, role, name))

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
    responsible = request.form.get('responsible').capitalize()
    date = request.form.get('date')
    file = request.files.get('file')
    title= request.form.get('title').capitalize() 

    file_name = None
    if file:
        file_name = secure_filename(f"{company}_{date}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)

    # Insert into the updates table
    update_query = """
    INSERT INTO updates (company, date, content, next_step, responsible, file, title)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    query(update_query, (company, date, content, next_step, responsible, file_name, title))

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


@app.route('/update_customer_details', methods=['POST'])
def update_customer_details():
    customer_id = request.form.get('customer_id')
    name = request.form.get('name').title()
    country = request.form.get('country').title()
    address = request.form.get('address')
    lead = request.form.get('lead').title()
    status = request.form.get('status').title()

    # Update customer details
    query("""
        UPDATE customers
        SET Name = ?, Country = ?, Address = ?, Lead = ?, Status = ?
        WHERE id = ?
    """, (name, country, address, lead, status, customer_id))

    
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

    # Update commercial data
    for key, value in request.form.items():
        if key.startswith('commercial_id_'):
            commercial_id = value
            index = key.split('_')[-1]
            annual_volume = request.form.get(f'annual_volume_{index}')
            potential_lines = request.form.get(f'potential_lines_{index}')

            query("""
                UPDATE commercial
                SET annual_volume = ?, lines_amount = ?
                WHERE id = ?
            """, (annual_volume, potential_lines, commercial_id))

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
    title = request.form.get('title').capitalize()
    attendees = request.form.get('attendees')
    date = request.form.get('date')
    summary = request.form.get('summary').capitalize()
    
    # Get the action items from the form (it will be a JSON string)
    action_items = request.form.get('action_items')
    
    # Store action_items as JSON directly in the database
    action_items_json = action_items if action_items else "[]"

    # Prepare the SQL query to insert the meeting details
    meeting_query = """
        INSERT INTO meetings (company, title, date, attendees, summary, action_items)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    # Execute the query with all the form data, including the action_items JSON
    query(meeting_query, (company, title, date, attendees, summary, action_items_json))

    # Return a success response (redirect to the customer page)
    return redirect(f'/customer_choosen?customer_id={customer_id}')

@app.route('/delete_meeting/<int:meeting_id>', methods=['POST'])
def delete_meeting(meeting_id):
    # Delete the meeting from the database
    customer_id = request.form.get('customer_id')
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
    title = request.form.get('title').capitalize()
    date = request.form.get('date')
    attendees = request.form.get('attendees')
    summary = request.form.get('summary').capitalize()
    customer_id = request.form.get('customer_id')

    # Get action items from the form and format them as a list of dictionaries
    action_items = []
    action_item_data = request.form.getlist('action_item')  # Get action items list
    responsible_data = request.form.getlist('responsible')  # Get responsible persons list
    due_date_data = request.form.getlist('due_date')  # Get due dates list
    status_data = request.form.getlist('status')  # Get status list

    # Iterate over the action items to create a list of dictionaries
    for i in range(len(action_item_data)):
        action_items.append({
            'item': action_item_data[i],
            'responsible': responsible_data[i],
            'due_date': due_date_data[i],
            'status': status_data[i]
        })

    # Convert the list of dictionaries to a JSON string
    action_items_json = json.dumps(action_items)

    # Update the database
    update_query = """
    UPDATE meetings
    SET title = ?, date = ?, attendees = ?, summary = ?, action_items = ?
    WHERE id = ?
    """
    query(update_query, (title, date, attendees, summary, action_items_json, meeting_id))

    flash("Meeting updated successfully.")
    return redirect(f'/customer_choosen?customer_id={customer_id}')


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