
# server/seed.py
from random import choice as rc
# We still need to import `app` here, as the provided seed structure expects it for `app.app_context()` if run directly.
# The factory pattern in app.py makes this import safe now.
from app import create_app # Import the factory function to get the app
from models import db, User, Course, Enrollment, Review
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash # For hashing passwords

# This function contains the actual data seeding logic
def run_seed_data(current_app): # Accept the app instance to work with its context
    with current_app.app_context(): # Ensure all db operations are within the app's context
        print("Clearing existing data...")
        # Order of deletion matters due to foreign key constraints:
        # Delete dependent records (reviews, enrollments) before their parents (courses, users)
        Review.query.delete()
        Enrollment.query.delete()
        Course.query.delete()
        User.query.delete()
        db.session.commit() # Commit deletions before adding new data
        print("Existing data cleared.")

        print("Seeding users...")
        user1 = User(username="janedoe", email="jane@example.com", password="password123", role="instructor") # password setter will hash
        user2 = User(username="johnsmith", email="john@example.com", password="securepass", role="student")
        user3 = User(username="alicebrown", email="alice@example.com", password="supersecret", role="instructor")
        user4 = User(username="bobwhite", email="bob@example.com", password="mysecret", role="student")
        
        users = [user1, user2, user3, user4]
        db.session.add_all(users)
        db.session.commit() # Commit users to get their IDs before creating courses/enrollments
        print(f"Seeded {len(users)} users.")

        print("Seeding courses...")
        # Ensure descriptions meet the >=20 char validation!
        course1 = Course(title="Full-Stack Dev with Flask & React", description="A comprehensive course covering backend API development with Flask and frontend application building with React, including routing.", difficulty="Advanced", duration_hours=40, instructor=user1)
        course2 = Course(title="Intro to Python Programming", description="Learn the fundamentals of Python, from variables and loops to functions and object-oriented programming for beginners.", difficulty="Beginner", duration_hours=20, instructor=user3)
        course3 = Course(title="Web Design Basics: HTML & CSS", description="Master the essential building blocks of the web, structuring content with HTML and styling with CSS for modern browsers.", difficulty="Beginner", duration_hours=15, instructor=user3)
        course4 = Course(title="Database Management with SQLAlchemy", description="Dive deep into relational databases and how to interact with them efficiently using SQLAlchemy ORM in Python applications.", difficulty="Intermediate", duration_hours=25, instructor=user1)
        course5 = Course(title="Modern JavaScript Fundamentals", description="Understand modern JavaScript features including ES6+, asynchronous programming, and module systems for web development.", difficulty="Intermediate", duration_hours=30, instructor=user3)

        courses = [course1, course2, course3, course4, course5]
        db.session.add_all(courses)
        db.session.commit() # Commit courses to get their IDs before creating enrollments/reviews
        print(f"Seeded {len(courses)} courses.")

        print("Seeding enrollments...")
        # Enrollment dates example: using datetime objects
        db.session.add(Enrollment(user=user2, course=course1, enrollment_date=datetime.utcnow() - timedelta(days=60)))
        db.session.add(Enrollment(user=user2, course=course2, enrollment_date=datetime.utcnow() - timedelta(days=30)))
        db.session.add(Enrollment(user=user2, course=course3, enrollment_date=datetime.utcnow() - timedelta(days=15)))
        db.session.add(Enrollment(user=user4, course=course2, enrollment_date=datetime.utcnow() - timedelta(days=45)))
        db.session.add(Enrollment(user=user4, course=course5, enrollment_date=datetime.utcnow() - timedelta(days=10)))
        db.session.commit()
        print(f"Seeded {Enrollment.query.count()} enrollments.")

        print("Seeding reviews...")
        # Ensure text_content meets the >=10 char validation!
        db.session.add(Review(user=user2, course=course1, rating=5, text_content="An absolutely brilliant course, highly recommended for advanced learners to grasp complex topics!"))
        db.session.add(Review(user=user2, course=course2, rating=4, text_content="Great for beginners, very clear explanations and good examples provided throughout the lessons."))
        db.session.add(Review(user=user4, course=course2, rating=5, text_content="As a total novice, this Python course was incredibly easy to follow and engaging, I loved it."))
        db.session.add(Review(user=user2, course=course3, rating=3, text_content="Decent introduction to HTML and CSS, but could use more practical exercises and real-world projects."))
        db.session.add(Review(user=user4, course=course5, rating=4, text_content="Solid coverage of modern JavaScript, helped me understand new features well and apply them instantly."))
        db.session.commit()
        print(f"Seeded {Review.query.count()} reviews.")

        print("Done seeding!")

# This block is executed if seed.py is run directly (e.g., `python seed.py`)
if __name__ == '__main__':
    # When run directly, we need to explicitly create the app instance and run seed_data within its context.
    app_instance_for_seed = create_app() # Call the factory function
    run_seed_data(app_instance_for_seed) # Pass the created app instance