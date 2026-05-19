from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'filetrack_secret_key_2024'

# --- Helper Function: Connect to Database ---
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="FileTrackDB"
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# --- Login Required Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Route: Landing Page ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Route: Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        db = get_db_connection()
        if not db:
            flash('Database connection failed', 'error')
            return render_template('login.html')
            
        cursor = db.cursor(dictionary=True)
        
        # Check credentials
        cursor.execute(
            "SELECT * FROM Users WHERE username = %s AND password = %s AND role = %s",
            (username, password, role)
        )
        user = cursor.fetchone()
        db.close()
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

# --- Route: Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- Route: Admin Dashboard ---
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db_connection()
    if not db:
        flash('Database connection failed', 'error')
        return render_template('admin_dashboard.html', 
                             total_documents=0, storage_slots=0, 
                             active_users=0, retrieval_logs=0,
                             documents=[], logs=[])
    
    cursor = db.cursor(dictionary=True)
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as count FROM Documents")
    total_documents = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM LocationRows")
    storage_slots = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM Users WHERE role = 'user'")
    active_users = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM AccessLogs")
    retrieval_logs = cursor.fetchone()['count']
    
    # Get recent documents
    cursor.execute("""
        SELECT d.doc_id, d.title, d.rfid_tag, d.status,
               CONCAT(r.row_label, '-', c.column_label) as location
        FROM Documents d
        LEFT JOIN LocationRows r ON d.row_id = r.row_id
        LEFT JOIN Columns c ON d.column_id = c.column_id
        ORDER BY d.updated_at DESC
        LIMIT 10
    """)
    documents = cursor.fetchall()
    
    # Get recent activity logs
    cursor.execute("""
        SELECT a.log_id, d.title, d.rfid_tag, d.status,
               requester.full_name as requested_by,
               admin.full_name as processed_by,
               a.action,
               DATE_FORMAT(a.action_timestamp, '%%Y-%%m-%%d %%h:%%i %%p') as formatted_time
        FROM AccessLogs a
        JOIN Documents d ON a.doc_id = d.doc_id
        JOIN Users requester ON a.requested_by_user_id = requester.user_id
        JOIN Users admin ON a.processed_by_admin_id = admin.user_id
        ORDER BY a.action_timestamp DESC
        LIMIT 10
    """)
    logs = cursor.fetchall()
    
    db.close()
    
    return render_template('admin_dashboard.html',
                         total_documents=total_documents,
                         storage_slots=storage_slots,
                         active_users=active_users,
                         retrieval_logs=retrieval_logs,
                         documents=documents,
                         logs=logs)

# --- Route: User Dashboard ---
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    db = get_db_connection()
    if not db:
        flash('Database connection failed', 'error')
        return render_template('user_dashboard.html',
                             assigned_records=0, pending_requests=0,
                             returned_files=0, active_retrievals=0,
                             documents=[])
    
    cursor = db.cursor(dictionary=True)
    user_id = session.get('user_id')
    
    # Get user statistics
    cursor.execute("""
        SELECT COUNT(*) as count FROM AccessLogs 
        WHERE requested_by_user_id = %s
    """, (user_id,))
    assigned_records = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM AccessLogs 
        WHERE requested_by_user_id = %s AND action = 'Check Out'
    """, (user_id,))
    active_retrievals = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM AccessLogs 
        WHERE requested_by_user_id = %s AND action = 'Return'
    """, (user_id,))
    returned_files = cursor.fetchone()['count']
    
    # Get user's recent documents (using subquery to avoid DISTINCT + ORDER BY issue)
    cursor.execute("""
        SELECT d.doc_id, d.title, d.rfid_tag, d.status,
               CONCAT(r.row_label, '-', c.column_label) as location,
               latest_log.max_timestamp
        FROM Documents d
        LEFT JOIN LocationRows r ON d.row_id = r.row_id
        LEFT JOIN Columns c ON d.column_id = c.column_id
        JOIN (
            SELECT doc_id, MAX(action_timestamp) as max_timestamp
            FROM AccessLogs
            WHERE requested_by_user_id = %s
            GROUP BY doc_id
        ) latest_log ON d.doc_id = latest_log.doc_id
        ORDER BY latest_log.max_timestamp DESC
        LIMIT 10
    """, (user_id,))
    documents = cursor.fetchall()
    
    db.close()
    
    return render_template('user_dashboard.html',
                         assigned_records=assigned_records,
                         pending_requests=0,
                         returned_files=returned_files,
                         active_retrievals=active_retrievals,
                         documents=documents)

# --- Route: Search Documents ---
@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    
    db = get_db_connection()
    if not db:
        return jsonify([])
    
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT d.doc_id, d.title, d.rfid_tag, d.status,
               CONCAT(r.row_label, '-', c.column_label) as location
        FROM Documents d
        LEFT JOIN LocationRows r ON d.row_id = r.row_id
        LEFT JOIN Columns c ON d.column_id = c.column_id
        WHERE d.title LIKE %s OR d.rfid_tag LIKE %s
        ORDER BY d.title
    """, (f'%{query}%', f'%{query}%'))
    
    documents = cursor.fetchall()
    db.close()
    
    return jsonify(documents)

# --- Route: Simulate RFID Scan ---
@app.route('/simulate_scan', methods=['POST'])
@login_required
def simulate_scan():
    rfid_tag = request.form.get('rfid_tag', '').strip()
    action_type = request.form.get('action', 'checkout').strip()
    
    if not rfid_tag:
        flash('Please enter an RFID tag', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db = get_db_connection()
    if not db:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    cursor = db.cursor(dictionary=True)
    
    # Check if document exists
    cursor.execute("SELECT * FROM Documents WHERE rfid_tag = %s", (rfid_tag,))
    document = cursor.fetchone()
    
    if document:
        user_id = session.get('user_id', 2)  # Default to user 2 if not logged in
        admin_id = session.get('user_id', 1) if session.get('role') == 'admin' else 1
        
        if action_type == 'checkout':
            action = 'Check Out'
            new_status = 'Borrowed'
            
            # Only allow checkout if document is currently available
            if document['status'] != 'Available':
                # Find who checked out this document
                checkout_query = """
                    SELECT u.full_name, a.action_timestamp
                    FROM AccessLogs a
                    JOIN Users u ON a.processed_by_admin_id = u.user_id
                    WHERE a.doc_id = %s AND a.action = 'Check Out'
                    ORDER BY a.action_timestamp DESC
                    LIMIT 1
                """
                cursor.execute(checkout_query, (document['doc_id'],))
                checkout_info = cursor.fetchone()
                
                if checkout_info:
                    flash(f"Document '{document['title']}' is already borrowed by {checkout_info['full_name']}.", 'warning')
                else:
                    flash(f"Document '{document['title']}' is currently not available for checkout.", 'warning')
                db.close()
                return redirect(url_for('admin_dashboard'))
        else:  # return
            action = 'Return'
            new_status = 'Available'
            
            # Only allow return if document is currently borrowed
            if document['status'] not in ['Borrowed', 'Missing']:
                flash(f"Document '{document['title']}' is already available and doesn't need to be returned.", 'info')
                db.close()
                return redirect(url_for('admin_dashboard'))
        
        # Update Document Status
        cursor.execute("UPDATE Documents SET status = %s WHERE doc_id = %s", 
                      (new_status, document['doc_id']))
        
        # Add entry to AccessLogs
        cursor.execute(
            "INSERT INTO AccessLogs (doc_id, requested_by_user_id, processed_by_admin_id, action) VALUES (%s, %s, %s, %s)",
            (document['doc_id'], user_id, admin_id, action)
        )
        db.commit()
        
        flash(f"Document '{document['title']}' successfully {action.lower()}ed!", 'success')
    else:
        flash(f'No document found with RFID tag: {rfid_tag}', 'error')
    
    db.close()
    return redirect(url_for('admin_dashboard'))

# --- Route: Add Document (Admin) ---
@app.route('/admin/add_document', methods=['POST'])
@admin_required
def add_document():
    title = request.form.get('title')
    rfid_tag = request.form.get('rfid_tag')
    row_id = request.form.get('row_id')
    column_id = request.form.get('column_id')
    
    db = get_db_connection()
    if not db:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Documents (title, rfid_tag, row_id, column_id, status)
            VALUES (%s, %s, %s, %s, 'Available')
        """, (title, rfid_tag, row_id, column_id))
        db.commit()
        flash('Document added successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error adding document: {err}', 'error')
    
    db.close()
    return redirect(url_for('admin_dashboard'))

# --- Route: Get Storage Locations ---
@app.route('/api/locations')
@login_required
def get_locations():
    db = get_db_connection()
    if not db:
        return jsonify([])
    
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM LocationRows ORDER BY row_label")
    rows = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Columns ORDER BY column_label")
    columns = cursor.fetchall()
    
    db.close()
    
    return jsonify({'rows': rows, 'columns': columns})

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html'), 500

# --- Start the Web Server ---
if __name__ == '__main__':
    print("🌐 Starting FileTrack Web Server...")
    print("📁 Make sure MySQL database is configured!")
    app.run(debug=True, port=5000)
