from main import app, db

# Set up an application context
with app.app_context():
    # Create the tables in the database
    db.create_all()

print("Database and tables created successfully!")
