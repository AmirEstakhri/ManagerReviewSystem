#to run dadta base and cerate data base we need this 
from app import app, db

with app.app_context():
    db.create_all()  # This will create the tables
if __name__ == '__main__':
    with app.app_context():
        db.create_all()