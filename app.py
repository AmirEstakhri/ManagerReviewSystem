from flask import Flask, redirect, url_for, request, send_file, session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

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
    "editing_time": "Editing Time"
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
@app.route('/manager_review', methods=['GET'])
def manager_review():
    if 'user' not in session or session['user']['role'] != 'manager':
        return redirect(url_for('login'))

    reviews = ""
    
    for i, submission in enumerate(submitted_data):
        reviews += f"""
        <p><strong>Entry {i + 1}:</strong> {submission['name']} | Status: {submission['status']} 
        <form action='/verify/{i}' method='post' style='display:inline;'>
            <input type='submit' value='Verify'>
        </form>
        <a href='/edit/{i}'><button>Edit</button></a>
        </p>
        """

    return f"<h1>Manager Review</h1>{reviews}<a href='/'>Go Home</a>"


# Route for Admin to review submissions
@app.route('/admin_review')
def admin_review():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    reviews = ""
    for i, submission in enumerate(submitted_data):
        if submission['status'] == "Pending Review":
            reviews += f"<p><strong>Entry {i + 1}:</strong> {submission['status']} <a href='/verify/{i}'><button>Verify</button></a></p>"
    
    return f"<h1>Admin Review</h1>{reviews}<a href='/'>Go Home</a>"


# Route for Manager to verify submissions
@app.route('/verify/<int:submission_index>', methods=['POST'])
def verify(submission_index):
    if 'user' not in session or session['user']['role'] != 'manager':
        return redirect(url_for('login'))

    if submission_index < len(submitted_data):
        submission = submitted_data[submission_index]
        submission['verification_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submission['status'] = 'Verified'

        # Set message for normal users
        session['verification_message'] = f"Your submission '{submission['name']}' has been verified."
    
    return redirect(url_for('manager_review'))


# Route for editing submissions
@app.route('/edit/<int:submission_index>', methods=['GET', 'POST'])
def edit(submission_index):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        updated_data = request.form.to_dict()
        submitted_data[submission_index].update(updated_data)
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
        c.drawString(100, y, f"Entry {i + 1}: {submission['name']}, Status: {submission['status']}")
        y -= 20  # Move down the page for each entry

    c.save()

    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)