from flask import Flask, redirect, url_for, request, send_file, session, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Submission ,FormVersion,User
import os
from flask_login import current_user, login_required
import json
from users import users, get_user


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///path_to_your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, prevents a warning

migrate = Migrate(app, db)

# Initialize SQLAlchemy with the app
db.init_app(app)


# Define the list to store submitted form data
version_history = {}



# users = {
#     "manager_user": {"username": "manager_user", "role": "manager"},
#     "manager_user1": {"username": "manager_user1", "role": "manager"},  

#     "admin_user": {"username": "admin_user", "role": "admin"}, 
#     "normal_user": {"username": "normal_user", "role": "normal"} 
# }
@app.route('/manager_forms')
def manager_forms():
    # Get the current logged-in user from the session
    user = session.get('user')  # Assuming you store user info in session

    # Check if the user is a manager
    if user and user['role'] == 'manager':
        # Fetch all forms assigned to this manager or that are allowed to be seen by other managers
        assigned_forms = Submission.query.filter(
            (Submission.assigned_manager_id == user['username']) | 
            (Submission.second_manager_id == user['username']) |  # Added check for second manager
            (Submission.allow_other_managers_to_see == True)
        ).all()

        # Get the list of managers (assuming you have a User model to fetch manager info)
        managers = User.query.filter_by(role='manager').all()

        return render_template('manager_.html', forms=assigned_forms, managers=managers)
    else:
        return redirect(url_for('home'))  # Or some error page
@app.route('/send_form_to_manager/<int:form_id>', methods=['POST'])
def send_form_to_manager(form_id):
    # Get the selected second manager ID from the form
    second_manager_id = request.form.get('second_manager_id')
    
    # Fetch the form from the database
    form = Submission.query.get_or_404(form_id)
    
    # Ensure that the logged-in user is the assigned manager
    if form.assigned_manager_id == user_info['username']:
        # Update the second manager
        form.second_manager_id = second_manager_id
        
        # Commit the changes to the database
        db.session.commit()
        
        flash('Form has been sent to the selected manager', 'success')
    else:
        flash('You are not authorized to send this form', 'danger')

    return redirect(url_for('manager_forms'))  # Redirect to the manager forms page




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
        unverified_forms = Submission.query.filter_by(status='Pending').all()  # Fetch unverified forms

        if verification_message:
            # Clear the message after displaying it
            session.pop('verification_message', None)

        return render_template('homev2.html', user=session['user'], verification_message=verification_message, unverified_forms=unverified_forms)
    else:
        unverified_forms = []  # Initialize to an empty list for non-logged-in users
        return render_template('homev2.html', user=None, unverified_forms=unverified_forms)


@app.route('/user')
def user ():
    if 'user' in session:
        return render_template('user.html', user=session['user'])
    else:
       return render_template('home.html')


@app.route('/test1')
def test1():   
              return render_template('test1.html')      

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = users.get(username)  # Retrieve the user from the 'users' dictionary
        
        if user:  # Check if the user exists
            session['user'] = user  # Store the user info in the session
            return redirect(url_for('home'))  # Redirect to the home page or another page
        else:
            # If the user doesn't exist, show an error message
            return render_template('login.html', error="Invalid Username")
    
    return render_template('login.html')  # Render the login page on GET request



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))
from datetime import datetime
from flask import flash

@app.route('/form', methods=['GET', 'POST'])
def form():
    # Check if the user is logged in
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    allowed_tags = {"needs", "packs", "updates", "reports"}
    allowed_categories = {"IT", "HR", "CEO"}

    # Prepare a list of manager usernames for the recipient selection
    manager_users = [manager['username'] for manager in users.values() if manager['role'] == 'manager']

    if request.method == 'POST':
        # Extract form data
        tag = request.form.get('field1')
        category = request.form.get('field2')
        recipient = request.form.get('field5')

        # Validate tag and category
        if tag not in allowed_tags or category not in allowed_categories:
            flash("Invalid tag or category selected.", "error")
            return redirect(url_for('form'))

        # Validate recipient selection
        if recipient not in manager_users:
            flash("Invalid recipient selected.", "error")
            return redirect(url_for('form'))

        # Create a new Submission object
        new_form = Submission(
            name=request.form.get('name'),
            field1=tag,
            field2=category,
            field3=user['username'],  # Automatically use the logged-in username
            field4=request.form.get('field4'),
            field5=recipient,  # Use the selected recipient
            field6=request.form.get('field6'),
            field7=request.form.get('field7'),
            field8=request.form.get('field8'),
            field9=request.form.get('field9'),
            field11=request.form.get('field11'),
            priority=request.form.get('priority'),
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status='Pending',
        )

        # Add the new form to the session and commit
        db.session.add(new_form)
        db.session.commit()

        return redirect(url_for('success'))

    # Render the form template with user information and manager list
    return render_template('form.html', user=user, managers=manager_users)





@app.route('/Features')
def test():
    return render_template('/Features.html')

@app.route('/success')
def success():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('success.html')

@app.route('/index',methods=['GET', 'POST'])
def index():
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

    return render_template('index.html')@app.route('/manager_review', methods=['GET', 'POST'])

@app.route('/manager_review', methods=['GET', 'POST'])
def manager_review():
    if 'user' not in session or session['user']['role'] != 'manager':
        return redirect(url_for('login'))

    # Get the logged-in user's username
    logged_in_user = session.get('user', {}).get('username')

    # Count the number of unverified forms
    unverified_count = Submission.query.filter_by(status='Pending').count()
    high_priority_count = Submission.query.filter_by(priority='High').count()

    # Get selected priority from the form, if provided
    selected_priority = request.form.get('priority') if request.method == 'POST' else None

    # Query the database with filtering applied directly
    query = Submission.query

    # Apply the selected priority filter if provided
    if selected_priority:
        query = query.filter_by(priority=selected_priority)

    # Apply the filter by manager's username (field5)
    if logged_in_user:
        query = query.filter_by(field5=logged_in_user)

    # Retrieve all (or filtered) submissions
    submissions = query.all()

    # Render the manager_review template with submissions, unverified count, and the selected priority
    return render_template(
        'manager_review.html',
        submissions=submissions,
        selected_priority=selected_priority,
        unverified_count=unverified_count,
        high_priority_count=high_priority_count
    )
    
@app.route('/user_forms', methods=['GET', 'POST'])
def user_forms():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Get the logged-in user's username
    logged_in_user = session.get('user', {}).get('username')

    # Count the number of unverified forms for the user
    unverified_count = Submission.query.filter_by(status='Pending', field5=logged_in_user).count()

    # Query the database and filter by the logged-in user's username in field3
    user_forms = Submission.query.filter_by(field3=logged_in_user).all()

    # Handle form submission (editing)
    if request.method == 'POST':
        form_id = request.form.get('form_id')  # Get the form ID from the form
        form = Submission.query.get(form_id)   # Fetch the form from the database
        if form and form.field5 == logged_in_user:  # Ensure the form belongs to the logged-in user
            # Update the form fields with the new data from the form
            form.name = request.form.get('name')
            form.field1 = request.form.get('field1')
            form.field2 = request.form.get('field2')
            form.field3 = request.form.get('field3')  # Make sure this is updated if needed
            form.field4 = request.form.get('field4')
            form.field6 = request.form.get('field6')  # Receiver (Manager)
            form.field7 = request.form.get('field7')
            form.field8 = request.form.get('field8')
            form.field9 = request.form.get('field9')
            form.field10 = request.form.get('field10')
            form.field11 = request.form.get('field11')
            form.priority = request.form.get('priority')
            form.submission_date = request.form.get('submission_date')
            form.status = request.form.get('status')
            form.verification_date = request.form.get('verification_date')
            form.editing_time = db.func.now()  # Set the current time for editing

            db.session.commit()  # Commit the changes to the database
            return redirect(url_for('user_forms'))  # Redirect to refresh the page and see the changes

    # Render the user_forms template with submissions
    return render_template(
        'user_manager_forms.html',
        user_forms=user_forms,
        unverified_count=unverified_count
    )







@app.route('/admin_review', methods=['GET', 'POST'])
def admin_review():
    # Ensure the user is logged in and has the "admin" role
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    # Count the number of unverified forms (can be used in the template)
    unverified_count = Submission.query.filter_by(status='Pending').count()
    high_priority_count = Submission.query.filter_by(priority='High').count()

    # Fetch all submissions from the database (admin has no restrictions)
    submitted_data = Submission.query.all()

    # Render the admin review template with all the submissions data
    return render_template('manager_review.html', 
                           submissions=submitted_data, 
                           unverified_count=unverified_count, 
                           high_priority_count=high_priority_count)



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



def get_submission_by_id(submission_id):
    return Submission.query.get(submission_id)

@app.route('/view_versions/<int:submission_id>', methods=['GET', 'POST'])
def view_versions(submission_id):
    submission = get_submission_by_id(submission_id)
    if submission is None:
        flash('Submission not found!', 'error')
        return redirect(url_for('manager_review'))

    # Fetch all versions for this submission
    versions = FormVersion.query.filter_by(submission_id=submission_id).order_by(FormVersion.timestamp.desc()).all()
    
    return render_template('view_versions.html', submission=submission, versions=versions)



@app.route('/edit_submission/<int:submission_id>', methods=['GET', 'POST'])
def edit_submission(submission_id):
    submission = get_submission_by_id(submission_id)

    if submission is None:
        flash('Submission not found!', 'error')
        return redirect(url_for('manager_review'))

    if request.method == 'POST':
        print(request.form)  # Debugging line

        # Save the current state of the submission as a version before updating it
        version_data = {
            field: getattr(submission, field) for field in [
                'name', 'field1', 'field2', 'field3', 'field4', 'field5',
                'field6', 'field7', 'field8', 'field9', 'field10', 'field11',
                'priority', 'submission_date', 'status', 'verification_date'
            ]
        }
        new_version = FormVersion(submission_id=submission.id, version_data=version_data)
        db.session.add(new_version)

        # Update fields only if new data is provided
        for field in version_data.keys():
            new_value = request.form.get(field)
            if new_value is not None:
                setattr(submission, field, new_value)

        submission.editing_time = datetime.utcnow()
        db.session.commit()
        flash('Submission updated and version saved successfully!', 'success')
        return redirect(url_for('manager_review'))

    return render_template('edit_submission.html', submission=submission)

@app.route('/revert_form/<int:form_id>', methods=['POST'])
def revert_form(form_id):
    form = Submission.query.get_or_404(form_id)
    version_id = request.form.get('version_id')
    version = FormVersion.query.get_or_404(version_id)

    # Load version data
    version_data = version.version_data

    # Update form with version data
    form.name = version_data['name']
    form.field1 = version_data['field1']
    form.field2 = version_data['field2']
    form.field3 = version_data['field3']
    form.field4 = version_data['field4']
    form.field5 = version_data['field5']
    form.field6 = version_data['field6']
    form.field7 = version_data['field7']
    form.field8 = version_data['field8']
    form.field9 = version_data['field9']
    form.field10 = version_data['field10']
    form.field11 = version_data['field11']

    db.session.commit()
    return redirect(url_for('view_form', form_id=form.id))

@app.route('/revert_version/<int:version_id>', methods=['POST'])
def revert_version(version_id):
    version = FormVersion.query.get(version_id)

    if version is None:
        flash('Version not found!', 'error')
        return redirect(url_for('manager_review'))

    # Get the associated submission from the version
    submission = Submission.query.get(version.submission_id)

    if submission is None:
        flash('Submission not found!', 'error')
        return redirect(url_for('manager_review'))

    # Save the current state as a new version before reverting
    current_version_data = {field: getattr(submission, field) for field in version.version_data.keys()}
    new_version = FormVersion(
        submission_id=submission.id,
        version_data=current_version_data,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_version)  # Save the current state as a version

    # Revert the submission to the version's data
    for field, value in version.version_data.items():
        setattr(submission, field, value)

    # Update the editing time to now
    submission.editing_time = datetime.utcnow()

    # Commit the changes to the database
    db.session.commit()

    flash('Submission reverted to selected version and a new version was saved successfully!', 'success')

    # Redirect to the version history page
    return redirect(url_for('view_versions', submission_id=submission.id))





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

    submissions = get_submitted_forms()

    y = 700
    for i, submission in enumerate(submissions.values()):
        edit_date = submission.get('editing_time', 'Not Edited')

        # Draw header for each entry
        c.drawString(100, y, f"form ID {i + 1}:")
        
        # Using a tuple of field names and values for clarity
        fields = [
            ("Name/Subject", submission.get('Name/Subject', '')),
            ("Tags", submission.get('Tags', '')),
            ("Categories", submission.get('Categories', '')),
            ("Sender", submission.get('Sender', '')),
            ("Senders Signature", submission.get('Senders Signature', '')),
            ("Recipient", submission.get('Recipient', '')),
            ("Recipients Signature", submission.get('Recipients Signature', '')),
            ("Registration Number", submission.get('Registration Number', '')),
            ("Letter Content", submission.get('Letter Content', '')),
            ("Attachment Number", submission.get('Attachment Number', '')),
            ("Select Follower", submission.get('Select Follower', '')),
            ("Priority", submission.get('priority', '')),
            ("Submission Date", submission.get('submission_date', '')),
            ("Status", submission.get('status', '')),
            ("Verification Date", submission.get('verification_date', '')),
            ("Edited on", edit_date)
        ]

        # Add fields with consistent spacing
        for label, value in fields:
            y -= 34
            c.drawString(120, y, f"{label}: {value}")

        y -= 500  # Add extra space between entries

        # Check if we need to start a new page
        if y < 50:
            c.showPage()
            y = 750

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


    
# from app import app, db  # Import the Flask app and db from your app

#Create an application context manually
# with app.app_context():
#     db.drop_all()  # Drop all tables in the database
#     db.create_all()  # Recreate all tables based on the models



  
if __name__ == '__main__':
    app.run(debug=True)
