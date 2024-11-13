from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define the User model
class User(db.Model):
    __tablename__ = 'user'  # Name of the table in the database
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the user
    username = db.Column(db.String(100), nullable=False)  # Username of the user
    role = db.Column(db.String(50), nullable=False)  # Role of the user (e.g., manager, admin)

    def __repr__(self):
        return f'<User {self.username}, Role: {self.role}>'

# Define the Submission model(main form  of sending  request )
class Submission(db.Model):
    __tablename__ = 'submission'  # Name of the table for form submissions
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the submission
    name = db.Column(db.String(100))  # Name associated with the submission
    field1 = db.Column(db.String(100))  # Tag for the submission
    field2 = db.Column(db.String(100))  # Category of the submission
    field3 = db.Column(db.String(100))  # Sender field
    field4 = db.Column(db.String(100))  # Sender's signature
    field5 = db.Column(db.String(100))  # Recipient field
    field6 = db.Column(db.String(100))  # Recipient's signature
    field7 = db.Column(db.String(100))  # Registration number
    field8 = db.Column(db.Text)  # Letter content (text field)
    field9 = db.Column(db.String(100))  # Attachment number
    field10 = db.Column(db.String(100))  # Selected follower
    field11 = db.Column(db.String(100))  # Additional field (not defined in your code)
    priority = db.Column(db.String(20))  # Priority of the submission (Low, Medium, High)
    submission_date = db.Column(db.String(20))  # Date when the submission was made
    status = db.Column(db.String(50))  # Status of the submission (e.g., Pending, Verified)
    verification_date = db.Column(db.String(20), nullable=True)  # Date of verification
    editing_time = db.Column(db.DateTime, nullable=True)  # Time when the submission was last edited
    verifiy_by = db.Column(db.String(50), nullable=True)  # Manager who verified the submission

    # The following commented-out sections represent potential relationships:
    # Foreign key to the user assigned to the form (assigned_manager)
    # assigned_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # assigned_manager = db.relationship('User', backref='assigned_forms', foreign_keys=[assigned_manager_id])

    # Foreign key for a second manager (optional)
    # second_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    # second_manager = db.relationship('User', foreign_keys=[second_manager_id], backref='second_manager_forms')

    # Many-to-many relationship for users who can view the form (admins, managers)
    # allowed_users = db.relationship('User', secondary='submission_user', backref='viewable_forms')
    # allow_other_managers_to_see = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Submission {self.id}, Name: {self.name}>'

# Define the Form model
class Form(db.Model):
    __tablename__ = 'form'  # Name of the table for forms
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the form
    name = db.Column(db.String(100))  # Name of the form
    field1 = db.Column(db.String(100))  # Tag for the form
    field2 = db.Column(db.String(100))  # Category of the form
    field3 = db.Column(db.String(100))  # Sender field
    field4 = db.Column(db.String(100))  # Sender's signature
    field5 = db.Column(db.String(100))  # Recipient field
    field6 = db.Column(db.String(100))  # Recipient's signature
    field7 = db.Column(db.String(100))  # Registration number
    field8 = db.Column(db.Text)  # Letter content (text field)
    field9 = db.Column(db.String(100))  # Attachment number
    field10 = db.Column(db.String(100))  # Selected follower
    field11 = db.Column(db.String(100))  # Additional field
    priority = db.Column(db.String(20))  # Priority of the form (Low, Medium, High)
    submission_date = db.Column(db.String(20))  # Date when the form was submitted
    status = db.Column(db.String(50))  # Status of the form
    verification_date = db.Column(db.String(20), nullable=True)  # Date when the form was verified
    editing_time = db.Column(db.String(20), nullable=True)  # Time of the last edit

    def __init__(self, name, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, priority, submission_date, status, verification_date=None, editing_time=None):
        # Initialize the form with the provided values
        self.name = name
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6
        self.field7 = field7
        self.field8 = field8
        self.field9 = field9
        self.field10 = field10
        self.field11 = field11
        self.priority = priority
        self.submission_date = submission_date
        self.status = status
        self.verification_date = verification_date
        self.editing_time = editing_time

    def __repr__(self):
        return f'<Form {self.id}, Name: {self.name}>'

# Define the FormVersion model to store historical form versions
class FormVersion(db.Model):
    __tablename__ = 'form_version'  # Name of the table for form versions
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the version
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)  # Foreign key to the associated submission
    version_data = db.Column(db.JSON, nullable=False)  # Store the entire form state as JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of when the version was created

    submission = db.relationship('Submission', backref=db.backref('versions', lazy=True))  # Relationship to the associated submission

    def __repr__(self):
        return f'<FormVersion {self.id}, Submission ID: {self.submission_id}>'

# Define the submission_user association table for the many-to-many relationship between Submission and User
submission_user = db.Table('submission_user',
    db.Column('submission_id', db.Integer, db.ForeignKey('submission.id'), primary_key=True),  # Foreign key to the submission
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)  # Foreign key to the user
)
