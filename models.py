from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Create the SQLAlchemy instance here
from datetime import datetime

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


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))    #subject
    field1 = db.Column(db.String(100))  #Tags
    field2 = db.Column(db.String(100))  #Categories
    field3 = db.Column(db.String(100))  #Sender
    field4 = db.Column(db.String(100))  #Sender's Signature<
    field5 = db.Column(db.String(100))  #Recipient
    field6 = db.Column(db.String(100))  #Recipient's Signature
    field7 = db.Column(db.String(100))  #Registration Number
    field8 = db.Column(db.Text)         #Letter Content
    field9 = db.Column(db.String(100))  #Attachment Number
    field10 = db.Column(db.String(100)) #Letter Content
    field11 = db.Column(db.String(100)) #Select Follower
    priority = db.Column(db.String(20)) #Priority
    submission_date = db.Column(db.String(20))
    status = db.Column(db.String(50))
    verification_date = db.Column(db.String(20), nullable=True)
    editing_time = db.Column(db.String(20), nullable=True)
    



    def __repr__(self):
        return f'<Submission {self.id}, Name: {self.name}, >'

class FormVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    version_data = db.Column(db.JSON, nullable=False)  # Stores the form data as JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    submission = db.relationship('Submission', backref=db.backref('versions', lazy=True))
    
    