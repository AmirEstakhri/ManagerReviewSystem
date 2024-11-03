# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from app import db


# # db = SQLAlchemy()

# # class FormSubmission(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     content = db.Column(db.Text, nullable=False)
# #     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# # class FormVersion(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     form_id = db.Column(db.Integer, db.ForeignKey('form_submission.id'), nullable=False)
# #     content = db.Column(db.Text, nullable=False)
# #     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# #     form_submission = db.relationship('FormSubmission', backref=db.backref('versions', lazy=True))
