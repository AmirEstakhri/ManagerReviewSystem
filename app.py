from flask import Flask, redirect, url_for, request, send_file, session, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Submission ,FormVersion # Import your database and model
import os

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
        verification_message = session.get('verification_message', None)
        if verification_message:
            # Clear the message after displaying it
            session.pop('verification_message', None)

        return render_template('home.html', user=session['user'], verification_message=verification_message)
    else:
        return render_template('home.html', user=None)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = users.get(username)
        if user:
            session['user'] = user
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid Username")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))
from datetime import datetime
from flask import flash


@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'user' not in session:
        return redirect(url_for('login'))

    allowed_tags = {"needs", "packs", "updates", "reports"}
    allowed_categories = {"IT", "HR", "CEO"}

    if request.method == 'POST':
        tag = request.form.get('field1')
        category = request.form.get('field2')

        if tag not in allowed_tags or category not in allowed_categories:
            flash("Invalid tag or category selected.", "error")
            return redirect(url_for('form'))

        new_form = Submission(
            name=request.form.get('name'),
            field1=tag,
            field2=category,
            field3=request.form.get('field3'),
            field4=request.form.get('field4'),
            field5=request.form.get('field5'),
            field6=request.form.get('field6'),
            field7=request.form.get('field7'),
            field8=request.form.get('field8'),
            field9=request.form.get('field9'),
            field11=request.form.get('field11'),
            priority=request.form.get('priority'),
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status='Pending',
        )

        db.session.add(new_form)
        db.session.commit()

        return redirect(url_for('success'))

    return render_template('form.html')



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
    # Ensure the user is logged in and has the "manager" role
    if 'user' not in session or session['user']['role'] != 'manager':
        return redirect(url_for('login'))

    # Get selected priority from the form, if provided
    selected_priority = request.form.get('priority') if request.method == 'POST' else None

    # Query the database with filtering applied directly
    query = Submission.query
    if selected_priority:
        query = query.filter_by(priority=selected_priority)
    
    # Retrieve all (or filtered) submissions
    submissions = query.all()

    # Render the manager_review template with submissions and the selected priority
    return render_template('manager_review.html', submissions=submissions, selected_priority=selected_priority)


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
def verify_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if submission:
        # Update verification details
        submission.status = 'Verified'
        submission.verification_date = datetime.now()
        
        db.session.commit()
        flash("Form has been verified!", "success")
    else:
        flash("Submission not found.", "error")
    
    return redirect(url_for('manager_review'))


def get_submission_by_id(submission_id):
    return Submission.query.get(submission_id)



@app.route('/edit_submission/<int:submission_id>', methods=['GET', 'POST'])
def edit_submission(submission_id):
    submission = get_submission_by_id(submission_id)

    if submission is None:
        flash('Submission not found!', 'error')
        return redirect(url_for('manager_review'))  # Adjust to the appropriate view if needed

    if request.method == 'POST':
        print(request.form)  # Debugging line to inspect form data

        # Save the current state as a version before updating
        version_data = {field: getattr(submission, field) for field in [
            'name', 'field1', 'field2', 'field3', 'field4',
            'field5', 'field6', 'field7', 'field8', 'field9',
            'field10', 'field11', 'priority', 'submission_date', 'status', 'verification_date'
        ]}
        new_version = FormVersion(submission_id=submission.id, version_data=version_data)
        db.session.add(new_version)

        # Update fields only if new data is provided
        for field in version_data.keys():
            new_value = request.form.get(field)
            if new_value is not None:  # Allow empty strings to clear fields if necessary
                setattr(submission, field, new_value)

        # Update editing_time to current time
        submission.editing_time = datetime.now()

        # Commit the changes to the database
        db.session.commit()  
        flash('Submission updated and version saved successfully!', 'success')
        return redirect(url_for('manager_review'))  # Adjust as needed

    return render_template('edit_submission.html', submission=submission)

@app.route('/revert_submission/<int:version_id>', methods=['POST'])
def revert_submission(version_id):
    version = FormVersion.query.get_or_404(version_id)
    submission = Submission.query.get(version.submission_id)

    # Restore fields from the version data
    for key, value in version.version_data.items():
        setattr(submission, key, value)

    submission.editing_time = datetime.utcnow()  # Update editing time to now
    db.session.commit()
    
    flash('Submission reverted to previous version!', 'success')
    return redirect(url_for('edit_submission', submission_id=submission.id))




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
def get_submitted_forms():
    # Retrieve all submissions from the database
    submissions = Submission.query.all()
    submitted_forms = {submission.id: {
        'name': submission.name,
        'status': submission.status,
        'priority': submission.priority,
        'editing_time': submission.editing_time
    } for submission in submissions}
    return submitted_forms

def get_submitted_forms():
    # Retrieve all submissions from the database
    submissions = Submission.query.all()
    submitted_forms = {submission.id: {
        'Name/Subject': submission.name,
        'Tags': submission.field1,
        'Categories': submission.field2,
        'Sender': submission.field3,
        'Senders Signature': submission.field4,
        'Recipient': submission.field5,
        'Recipients Signature': submission.field6,
        'Registration Number': submission.field7,
        'Letter Content': submission.field8,
        'Attachment Number': submission.field9,
        'Letter Content': submission.field10,
        'Select Follower': submission.field11,
        'priority': submission.priority,
        'submission_date': submission.submission_date,
        'status': submission.status,
        'verification_date': submission.verification_date,
        'editing_time': submission.editing_time
    } for submission in submissions}
    return submitted_forms


@app.route('/download_pdf')
def download_pdf():
    if 'user' not in session:
        return redirect(url_for('login'))

    pdf_filename = 'submission_report.pdf'
    pdf_path = os.path.join(os.getcwd(), pdf_filename)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Submission Report")
    c.drawString(100, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    submissions = get_submitted_forms()  # Use the newly defined function

    y = 700
    for i, submission in enumerate(submissions.values()):
        edit_date = submission.get('editing_time', 'Not Edited')
        c.drawString(100, y, f"Entry {i + 1}:")
        c.drawString(120, y - 15, f"Name/Subject: {submission['Name/Subject']}")
        c.drawString(120, y - 30, f"Tags: {submission['Tags']}")
        c.drawString(120, y - 45, f"Categories: {submission['Categories']}")
        c.drawString(120, y - 60, f"Sender: {submission['Sender']}")
        c.drawString(120, y - 75, f"Senders Signature: {submission['Senders Signature']}")
        c.drawString(120, y - 90, f"Recipient: {submission['Recipient']}")
        c.drawString(120, y - 105, f"Recipients Signature: {submission['Recipients Signature']}")
        c.drawString(120, y - 120, f"Registration Number: {submission['Registration Number']}")
        c.drawString(120, y - 135, f"Letter Content: {submission['Letter Content']}")
        c.drawString(120, y - 150, f"Attachment Number: {submission['Attachment Number']}")
        c.drawString(120, y - 165, f"Letter Content: {submission['Letter Content']}")
        c.drawString(120, y - 180, f"Field 11: {submission['Select Follower']}")
        c.drawString(120, y - 195, f"Priority: {submission['priority']}")
        c.drawString(120, y - 210, f"Submission Date: {submission['submission_date']}")
        c.drawString(120, y - 225, f"Status: {submission['status']}")
        c.drawString(120, y - 240, f"Verification Date: {submission['verification_date']}")
        c.drawString(120, y - 255, f"Edited on: {edit_date}")
        
        y -= 270  # Move down the page for each entry

        # Check if we need to start a new page if space is running out
        if y < 50:
            c.showPage()  # Create a new page
            y = 750  # Reset y position for new page

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
    filtered_data = []
    if request.method == 'POST':
        name = request.form.get('name', '')
        tags = request.form.get('tags', '')
        categories = request.form.get('categories', '')
        date = request.form.get('date', '')

        # Build a query based on the filters provided
        query = Submission.query

        if name:
            query = query.filter(Submission.name.ilike(f'%{name}%'))
        if tags:
            query = query.filter(Submission.field1 == tags)
        if categories:
            query = query.filter(Submission.field2 == categories)
        if date:
            query = query.filter(Submission.field3 == date)

        # Execute the query and get the filtered results
        filtered_data = query.all()

    return render_template('search.html', filtered_data=filtered_data)



if __name__ == '__main__':
    with app.app_context():
        print("App context is active.")
        db.create_all()  # Create all database tables
    app.run(debug=True)
