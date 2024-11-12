from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Define the User model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.username}, Role: {self.role}>'

# Define the Submission model
class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    field1 = db.Column(db.String(100))
    field2 = db.Column(db.String(100))
    field3 = db.Column(db.String(100))
    field4 = db.Column(db.String(100))
    field5 = db.Column(db.String(100))
    field6 = db.Column(db.String(100))
    field7 = db.Column(db.String(100))
    field8 = db.Column(db.Text)
    field9 = db.Column(db.String(100))
    field10 = db.Column(db.String(100))
    field11 = db.Column(db.String(100))
    priority = db.Column(db.String(20))
    submission_date = db.Column(db.String(20))
    status = db.Column(db.String(50))
    verification_date = db.Column(db.String(20), nullable=True)
    editing_time = db.Column(db.DateTime, nullable=True)
    verifiy_by = db.Column(db.String(50), nullable=True)

    # Foreign key to the user assigned to the form (assigned_manager)
    assigned_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_manager = db.relationship('User', backref='assigned_forms', foreign_keys=[assigned_manager_id])

    # Foreign key for second manager (optional)
    second_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    second_manager = db.relationship('User', foreign_keys=[second_manager_id], backref='second_manager_forms')

    # Many-to-many relationship for users who can view the form (admins, managers)
    allowed_users = db.relationship('User', secondary='submission_user', backref='viewable_forms')
    allow_other_managers_to_see = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Submission {self.id}, Name: {self.name}>'


    


    def __repr__(self):
        return f'<Submission {self.id}, Name: {self.name}>'

# Define the Form model
class Form(db.Model):
    __tablename__ = 'form'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    field1 = db.Column(db.String(100))
    field2 = db.Column(db.String(100))
    field3 = db.Column(db.String(100))
    field4 = db.Column(db.String(100))
    field5 = db.Column(db.String(100))
    field6 = db.Column(db.String(100))
    field7 = db.Column(db.String(100))
    field8 = db.Column(db.Text)
    field9 = db.Column(db.String(100))
    field10 = db.Column(db.String(100))
    field11 = db.Column(db.String(100))
    priority = db.Column(db.String(20))
    submission_date = db.Column(db.String(20))
    status = db.Column(db.String(50))
    verification_date = db.Column(db.String(20), nullable=True)
    editing_time = db.Column(db.String(20), nullable=True)

    def __init__(self, name, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, priority, submission_date, status, verification_date=None, editing_time=None):
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

# Define the FormVersion model
class FormVersion(db.Model):
    __tablename__ = 'form_version'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    version_data = db.Column(db.JSON, nullable=False)  # Store entire form state as JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    submission = db.relationship('Submission', backref=db.backref('versions', lazy=True))

    def __repr__(self):
        return f'<FormVersion {self.id}, Submission ID: {self.submission_id}>'

# Define the submission_user association table (for the many-to-many relationship between Submission and User)
submission_user = db.Table('submission_user',
    db.Column('submission_id', db.Integer, db.ForeignKey('submission.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)
