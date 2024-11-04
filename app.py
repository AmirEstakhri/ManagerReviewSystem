from flask import Flask, redirect, url_for, request, send_file, session, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash


from models import db, Submission  # Import your database and model

import os
from models import Form, db  # Importing db from models

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///path_to_your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, prevents a warning

migrate = Migrate(app, db)

# Initialize SQLAlchemy with the app
db.init_app(app)
with app.app_context():
    if not os.path.exists('forms.db'):
        db.create_all() # This creates all the tables defined by your models

# Define the list to store submitted form data
version_history = {}



users = {
    "manager_user": {"username": "manager_user", "role": "manager"},
    "admin_user": {"username": "admin_user", "role": "admin"},
    "normal_user": {"username": "normal_user", "role": "normal"}
}

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
    "priority": "Priority"  
}

# Home page route
@app.route('/')
def home():
    if 'user' in session:
        welcome_message = f"<h1>Welcome, {session['user']['username']}!</h1>"

        verification_message = ""
        if session['user']['role'] == 'normal' and 'verification_message' in session:
            verification_message = f"<p>{session['verification_message']}</p>"
            # Clear the message after displaying it
            session.pop('verification_message', None)

        buttons = "<a href='/form'><button>Go to Form</button></a> | <a href='/logout'><button>Logout</button></a>"

        if session['user']['role'] == 'admin':
            buttons += " | <a href='/admin_review'><button>Admin Review</button></a>"
        elif session['user']['role'] == 'manager':
            buttons += " | <a href='/manager_review'><button>Manager Review</button></a>"
            buttons += " | <a href='/download_pdf'><button>Download PDF</button></a>"  
            buttons += " | <a href='/submitted_forms'><button>View Submitted Forms</button></a>"  
            buttons += " | <a href='/search'><button>Search</button></a>"  

        buttons += " | <a href='/search'><button>Search</button></a>"  
        return welcome_message + verification_message + buttons
    else:
        return '''
        <h1>Welcome to the Home Page!</h1>
        <a href="/login"><button>Login</button></a>
        '''



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


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_form = Submission(
            name=request.form.get('name'),
            field1=request.form.get('field1'),
            field2=request.form.get('field2'),
            field3=request.form.get('field3'),
            field4=request.form.get('field4'),
            field5=request.form.get('field5'),
            field6=request.form.get('field6'),
            field7=request.form.get('field7'),
            field8=request.form.get('field8'),
            field9=request.form.get('field9'),
            field10=request.form.get('field10'),
            field11=request.form.get('field11'),
            priority=request.form.get('priority'),
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status='Pending',  # Initialize status as needed
        )
        db.session.add(new_form)
        db.session.commit()

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
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/manager_review', methods=['GET', 'POST'])
def manager_review():
    if 'user' not in session or session['user']['role'] != 'manager':
        return redirect(url_for('login'))

            
    selected_priority = request.form.get('priority') if request.method == 'POST' else None

    # Fetch all submissions from the database
    all_submissions = Submission.query.all()  # Assuming you have a Submission model
    filtered_data = [
        submission for submission in all_submissions
        if not selected_priority or submission.priority == selected_priority
    ]

    return render_template('manager_review.html', submissions=filtered_data, selected_priority=selected_priority)

@app.route('/admin_review')
def admin_review():
    # Check if the user is logged in and has admin role
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    # Fetch all submissions from the database
    submitted_data = Submission.query.all()
    
    # Create a list to hold review entries
    reviews = []

    # Iterate through submissions and generate review entries
    for i, submission in enumerate(submitted_data):
        if submission.status == "Pending Review":
            review_entry = {
                'index': i + 1,
                'status': submission.status,
                'priority': submission.priority,
                'id': submission.id  # Use submission id for the verification link
            }
            reviews.append(review_entry)

    # Render the admin review template with the review entries
    return render_template('admin_review.html', reviews=reviews)


@app.route('/verify_submission/<int:submission_id>', methods=['POST'])
def verify_submission(submission_id):  # Correctly defined with submission_id parameter
    submission = Submission.query.get(submission_id)
    if submission:
        # Perform your verification logic here
        submission.status = 'Verified'  # Example of status update
        db.session.commit()
        return redirect(url_for('manager_review'))  # Redirect after processing
    return "Submission not found", 404

def get_submission_by_id(submission_id):
    return Submission.query.get(submission_id)

@app.route('/edit_submission/<int:submission_id>', methods=['GET', 'POST'])
def edit_submission(submission_id):
    submission = get_submission_by_id(submission_id)

    if submission is None:
        flash('Submission not found!', 'error')
        return redirect(url_for('manager_review'))  # Change to the actual view you want to redirect to

    if request.method == 'POST':
        print(request.form)  # Debugging line

        # Check and update each field as necessary
        submission.name = request.form.get('name', submission.name)  # Update name
        submission.field1 = request.form.get('field1', submission.field1)  # Update field1
        submission.field2 = request.form.get('field2', submission.field2)  # Update field2
        submission.field3 = request.form.get('field3', submission.field3)  # Update field3
        submission.field4 = request.form.get('field4', submission.field4)  # Update field4
        submission.field5 = request.form.get('field5', submission.field5)  # Update field5
        submission.field6 = request.form.get('field6', submission.field6)  # Update field6
        submission.field7 = request.form.get('field7', submission.field7)  # Update field7
        submission.field8 = request.form.get('field8', submission.field8)  # Update field8
        submission.field9 = request.form.get('field9', submission.field9)  # Update field9
        submission.field10 = request.form.get('field10', submission.field10)  # Update field10
        submission.field11 = request.form.get('field11', submission.field11)  # Update field11
        submission.priority = request.form.get('priority', submission.priority)  # Update priority
        submission.submission_date = request.form.get('submission_date', submission.submission_date)  # Update submission_date
        submission.status = request.form.get('status', submission.status)  # Update status
        submission.verification_date = request.form.get('verification_date', submission.verification_date)  # Update verification_date
        submission.editing_time = request.form.get('editing_time', submission.editing_time)  # Update editing_time

        # Commit the changes to the database
        db.session.commit()  
        flash('Submission updated successfully!', 'success')
        return redirect(url_for('manager_review'))  # Change to the actual view you want to redirect to

    return render_template('edit_submission.html', submission=submission)



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

@app.route('/submitted_forms')
def submitted_forms():
    # Fetch the submitted forms from the database or data source
    submitted_data = db.session.query(Submission).all()  # Adjust this line as necessary based on your model
    submitted_list = [submission for submission in submitted_data]  # All submitted forms
    
    return render_template('submitted_forms.html', submissions=submitted_list)


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
    with app.app_context():
        print("App context is active.")
        db.create_all()  # Create all database tables
    app.run(debug=True)
