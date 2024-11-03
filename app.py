from flask import Flask, redirect, url_for, request, send_file, session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

# Define the list to store submitted form data
submitted_data = []

# New dictionary to hold the version history for each submission
version_history = {}

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required to use session in Flask

# Define the list to store submitted form data
submitted_data = []

# User data with roles
users = {
    "manager_user": {"username": "manager_user", "role": "manager"},
    "admin_user": {"username": "admin_user", "role": "admin"},
    "normal_user": {"username": "normal_user", "role": "normal"}
}

# Mapping field names to labels (English version)
field_labels = {
    "name": "Subject",
    "field1": "Tags",
    "field2": "Categories",
    "field3": "Sender",
    "field4": "Sender's Signature",
    "field5": "Recipient",
    "field6": "Recipient's Signature",
    "field7": "Registration Number",
    "field8": "Letter Content",
    "field9": "Attachment Number (Optional)",
    "field10": "Letter Content",
    "field11": "Select Follower",
    "submission_date": "Submission Date",
    "field8_truncated": "Letter Content (First 100 Characters)",
    "verification_date": "Verification Date",
    "status": "Status",
    "editing_time": "Editing Time",
    "priority": "Priority"  # Add priority to the labels
}

# Home page route
@app.route('/')
def home():
    if 'user' in session:
        welcome_message = f"<h1>Welcome, {session['user']['username']}!</h1>"
        
        # Display verification message for normal users
        verification_message = ""
        if session['user']['role'] == 'normal' and 'verification_message' in session:
            verification_message = f"<p>{session['verification_message']}</p>"
            # Clear the message after displaying it
            session.pop('verification_message', None)

        buttons = "<a href='/form'><button>Go to Form</button></a> | <a href='/logout'><button>Logout</button></a>"
        
        # Check user role to show buttons conditionally
        if session['user']['role'] == 'admin':
            buttons += " | <a href='/admin_review'><button>Admin Review</button></a>"
        elif session['user']['role'] == 'manager':
            buttons += " | <a href='/manager_review'><button>Manager Review</button></a>"
            buttons += " | <a href='/download_pdf'><button>Download PDF</button></a>"  # Add PDF download button for manager
            buttons += " | <a href='/submitted_forms'><button>View Submitted Forms</button></a>"  # Link to view submitted forms
        
        # Add search button for all users
        buttons += " | <a href='/search'><button>Search</button></a>"  

        return welcome_message + verification_message + buttons
    else:
        return '''
        <h1>Welcome to the Home Page!</h1>
        <a href="/login"><button>Login</button></a>
        '''




# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = users.get(username)
        if user:
            session['user'] = user
            return redirect(url_for('home'))
        else:
            return "<h1>Invalid Username</h1><a href='/login'><button>Try Again</button></a>"

    return '''
    <h1>Login</h1>
    <form method="post">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username"><br><br>
        <input type="submit" value="Login">
    </form>
    '''


# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


# Form page route with role-based restriction
@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.form.to_dict()
        data["priority"] = request.form.get('priority')  # Save the priority
        data["submission_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["status"] = "Pending Review"  # Initial status
        data["verification_date"] = None  # Initially no verification date
        data["editing_time"] = None  # Initially no editing time
        
        # Save only the first 100 characters of "Letter Content"
        if "field8" in data:
            data["field8_truncated"] = data["field8"][:100]

        submitted_data.append(data)
        
        # Notify Manager (Simulating sending to manager)
        if session['user']['role'] == 'admin':
            # Here we can send an email or any notification to the manager
            print(f"Admin: {session['user']['username']} has submitted a form for verification to the Manager.")

        return redirect(url_for('success'))

    return '''
    <h1>Fill out the Form</h1>
    <form method="post">
        <label for="name">Subject:</label>
        <input type="text" id="name" name="name"><br><br>
        <label for="field1">Tags:</label>
        <input type="text" id="field1" name="field1"><br><br>
        <label for="field2">Categories:</label>
        <input type="text" id="field2" name="field2"><br><br>
        <label for="field3">Sender:</label>
        <input type="text" id="field3" name="field3"><br><br>
        <label for="field4">Sender's Signature:</label>
        <input type="text" id="field4" name="field4"><br><br>
        <label for="field5">Recipient:</label>
        <input type="text" id="field5" name="field5"><br><br>
        <label for="field6">Recipient's Signature:</label>
        <input type="text" id="field6" name="field6"><br><br>
        <label for="field7">Registration Number:</label>
        <input type="text" id="field7" name="field7"><br><br>
        <label for="field8">Letter Content:</label>
        <input type="text" id="field8" name="field8"><br><br>
        <label for="field9">Attachment Number (Optional):</label>
        <input type="text" id="field9" name="field9"><br><br>
        <label for="field10">Letter Content:</label>
        <input type="text" id="field10" name="field10"><br><br>
        <label for="field11">Select Follower:</label>
        <input type="text" id="field11" name="field11"><br><br>
        <label for="priority">Priority:</label>
        <select id="priority" name="priority">
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
        </select><br><br>
        <input type="submit" value="Submit">
    </form>
    '''


# Success page route with link to view PDF
@app.route('/success')
def success():
    if 'user' not in session:
        return redirect(url_for('login'))
    return '''
    <h1>Form Submitted Successfully!</h1>
    <a href="/form"><button>Create a New Form</button></a>
    <br><br>
    <a href="/download_pdf"><button>Show PDF File</button></a>
    <br><br>
    <a href="/"><button>Home</button></a>
    '''


# Route for Manager to review submissions
@app.route('/manager_review', methods=['GET', 'POST'])
def manager_review():
    if 'user' not in session or session['user']['role'] != 'manager':
        return redirect(url_for('login'))

    # Get the selected priority from the form
    selected_priority = request.form.get('priority') if request.method == 'POST' else None

    # Filter submissions based on selected priority
    filtered_data = [submission for submission in submitted_data if not selected_priority or submission['priority'] == selected_priority]

    # Create the filter form
    priority_filter_form = '''
    <form method="post">
        <label for="priority">Filter by Priority:</label>
        <select id="priority" name="priority">
            <option value="">All</option>
            <option value="Low" {'selected' if selected_priority == 'Low' else ''}>Low</option>
            <option value="Medium" {'selected' if selected_priority == 'Medium' else ''}>Medium</option>
            <option value="High" {'selected' if selected_priority == 'High' else ''}>High</option>
        </select>
        <input type="submit" value="Filter">
    </form>
    '''

    reviews = ""
    
    for i, submission in enumerate(filtered_data):
        reviews += f"""
        <p><strong>Entry {i + 1}:</strong> {submission['name']} | Status: {submission['status']} | Priority: {submission['priority']}
        <form action='/verify/{submitted_data.index(submission)}' method='post' style='display:inline;'>
            <input type='submit' value='Verify'>
        </form>
        <a href='/edit/{submitted_data.index(submission)}'><button>Edit</button></a>
        </p>
        """

    return f"<h1>Manager Review</h1>{priority_filter_form}{reviews}<a href='/'>Go Home</a>"



# Route for Admin to review submissions
@app.route('/admin_review')
def admin_review():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    reviews = ""
    for i, submission in enumerate(submitted_data):
        if submission['status'] == "Pending Review":
            reviews += f"<p><strong>Entry {i + 1}:</strong> {submission['status']} | Priority: {submission['priority']} <a href='/verify/{i}'><button>Verify</button></a></p>"
    
    return f"<h1>Admin Review</h1>{reviews}<a href='/'>Go Home</a>"


# Route for Manager to verify submissions
@app.route('/verify/<int:index>', methods=['POST'])
def verify(index):
    if 'user' not in session or session['user']['role'] != 'manager':
        return redirect(url_for('login'))

    if 0 <= index < len(submitted_data):
        submission = submitted_data[index]
        submission['status'] = "Verified"
        submission['verification_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Notify the normal user about the verification (simulated)
        print(f"Manager: {session['user']['username']} has verified the form submitted by {submission['field3']}.")

    return redirect(url_for('manager_review'))


# Route to edit submissions
# Route for editing submissions
@app.route('/edit/<int:submission_index>', methods=['GET', 'POST'])
def edit(submission_index):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        updated_data = request.form.to_dict()
        
        # Save the previous state to version history
        if submission_index not in version_history:
            version_history[submission_index] = []
        version_history[submission_index].append((submitted_data[submission_index], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Update the submission
        submitted_data[submission_index].update(updated_data)
        submitted_data[submission_index]['editing_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Save edit date
        return redirect(url_for('manager_review'))

    # Pre-fill form with existing data for editing
    existing_data = submitted_data[submission_index]
    return f'''
    <h1>Edit Submission</h1>
    <form method="post">
        <label for="name">Subject:</label>
        <input type="text" id="name" name="name" value="{existing_data['name']}"><br><br>
        <label for="field1">Tags:</label>
        <input type="text" id="field1" name="field1" value="{existing_data['field1']}"><br><br>
        <label for="field2">Categories:</label>
        <input type="text" id="field2" name="field2" value="{existing_data['field2']}"><br><br>
        <label for="field3">Sender:</label>
        <input type="text" id="field3" name="field3" value="{existing_data['field3']}"><br><br>
        <label for="field4">Sender's Signature:</label>
        <input type="text" id="field4" name="field4" value="{existing_data['field4']}"><br><br>
        <label for="field5">Recipient:</label>
        <input type="text" id="field5" name="field5" value="{existing_data['field5']}"><br><br>
        <label for="field6">Recipient's Signature:</label>
        <input type="text" id="field6" name="field6" value="{existing_data['field6']}"><br><br>
        <label for="field7">Registration Number:</label>
        <input type="text" id="field7" name="field7" value="{existing_data['field7']}"><br><br>
        <label for="field8">Letter Content:</label>
        <input type="text" id="field8" name="field8" value="{existing_data['field8']}"><br><br>
        <label for="field9">Attachment Number (Optional):</label>
        <input type="text" id="field9" name="field9" value="{existing_data['field9']}"><br><br>
        <label for="field10">Letter Content:</label>
        <input type="text" id="field10" name="field10" value="{existing_data['field10']}"><br><br>
        <label for="field11">Select Follower:</label>
        <input type="text" id="field11" name="field11" value="{existing_data['field11']}"><br><br>
        <input type="submit" value="Update">
    </form>
    <a href='/manager_review'><button>Cancel</button></a>
    '''

# New Route to View Version History
@app.route('/version_history/<int:submission_index>')
def view_version_history(submission_index):
    if submission_index not in version_history:
        return "<h1>No version history found for this submission.</h1>"

    history = version_history[submission_index]
    history_display = "<h1>Version History</h1><ul>"
    for version, edit_time in history:
        history_display += f"<li>Edited on {edit_time}: {version}</li>"
    history_display += "</ul><a href='/manager_review'><button>Back to Review</button></a>"

    return history_display

# Route to download PDF
# Route to download PDF
@app.route('/download_pdf')
def download_pdf():
    if 'user' not in session:
        return redirect(url_for('login'))

    pdf_filename = 'submission_report.pdf'
    pdf_path = os.path.join(os.getcwd(), pdf_filename)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Submission Report")
    c.drawString(100, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 700
    for i, submission in enumerate(submitted_data):
        edit_date = submission.get('editing_time', 'Not Edited')
        c.drawString(100, y, f"Entry {i + 1}: {submission['name']}, Status: {submission['status']}, Priority: {submission['priority']}, Edited on: {edit_date}")
        y -= 20  # Move down the page for each entry

    c.save()

    return send_file(pdf_path, as_attachment=True)


# Route to show submitted forms, edited forms, verified forms, and high priority forms
@app.route('/submitted_forms')
def submitted_forms():
    if 'user' not in session:
        return redirect(url_for('login'))

    submitted_list = [submission for submission in submitted_data]  # All submitted forms
    edited_list = [submission for submission in submitted_data if submission.get('editing_time')]  # Edited forms
    verified_list = [submission for submission in submitted_data if submission.get('status') == 'Verified']  # Verified forms
    high_priority_list = [submission for submission in submitted_data if submission.get('priority') == 'High']  # High priority forms

    # HTML structure to display the forms
    response = "<h1>Submitted Forms</h1>"
    
    # Display counts for each category
    response += f"<h2>Total Submitted Forms: {len(submitted_list)}</h2>"
    response += f"<h2>Total Edited Forms: {len(edited_list)}</h2>"
    response += f"<h2>Total Verified Forms: {len(verified_list)}</h2>"
    response += f"<h2>Total High Priority Forms: {len(high_priority_list)}</h2>"  # Count of high priority forms

    # Calculate average time between submission and verification for verified forms
    total_time_diff = 0
    count_verified = 0
    
    for submission in verified_list:
        submission_time = datetime.strptime(submission['submission_date'], "%Y-%m-%d %H:%M:%S")
        verification_time = datetime.strptime(submission['verification_date'], "%Y-%m-%d %H:%M:%S")
        time_diff = verification_time - submission_time
        total_time_diff += time_diff.total_seconds()  # Convert to seconds
        count_verified += 1

    # Calculate average if there are verified forms
    average_time = (total_time_diff / count_verified) / 60 if count_verified > 0 else 0  # Average in minutes

    # Display average time
    response += f"<h2>Average Time from Submission to Verification: {average_time:.2f} minutes</h2>"

    # Display submitted forms
    response += "<h2>All Submitted Forms:</h2>"
    for submission in submitted_list:
        response += f"<p><strong>Subject:</strong> {submission['name']} | Status: {submission['status']} | Submission Date: {submission['submission_date']}</p>"
    
    # Display edited forms
    response += "<h2>Edited Forms:</h2>"
    for submission in edited_list:
        response += f"<p><strong>Subject:</strong> {submission['name']} | Edited Date: {submission['editing_time']}</p>"
    
    # Display verified forms
    response += "<h2>Verified Forms:</h2>"
    for submission in verified_list:
        response += f"<p><strong>Subject:</strong> {submission['name']} | Verification Date: {submission['verification_date']}</p>"
    
    # Display high priority forms
    response += "<h2>High Priority Forms:</h2>"
    if high_priority_list:
        for submission in high_priority_list:
            response += f"<p><strong>Subject:</strong> {submission['name']} | Priority: {submission['priority']} | Submission Date: {submission['submission_date']}</p>"
    else:
        response += "<p>No high priority forms submitted.</p>"
    
    response += "<br><a href='/'>Go Home</a>"

    return response
# Route for search functionality
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_tags = request.form.get('tags')
        selected_categories = request.form.get('categories')

        filtered_data = [
            submission for submission in submitted_data
            if (selected_tags in submission['field1'] if selected_tags else True) and
               (selected_categories in submission['field2'] if selected_categories else True)
        ]
        
        # Display search results
        data_display = "<h1>Search Results</h1><ul>"
        for submission in filtered_data:
            data_display += f"<li>{submission['name']} - Tags: {submission['field1']} - Categories: {submission['field2']}</li>"
        data_display += "</ul>"
        return data_display

    return '''
    <h1>Search</h1>
    <form method="post">
        <label for="tags">Tags:</label>
        <input type="text" id="tags" name="tags"><br><br>
        <label for="categories">Categories:</label>
        <input type="text" id="categories" name="categories"><br><br>
        <input type="submit" value="Search">
    </form>
    '''


if __name__ == '__main__':
    app.run(debug=True)
