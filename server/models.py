# server/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates # For custom validators
from datetime import datetime # For Enrollment date
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing

# Initialize SQLAlchemy without an app. It will be bound in app.py's factory.
db = SQLAlchemy()

# --- User Model ---
class User(db.Model, SerializerMixin):
    __tablename__ = 'users' # Name of the database table

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) # Must be unique, cannot be empty
    email = db.Column(db.String(120), unique=True, nullable=False) # Must be unique, cannot be empty
    password_hash = db.Column(db.String(128), nullable=False) # Stores the hashed password
    role = db.Column(db.String(50), nullable=False, default='student') # e.g., 'student', 'instructor'

    # Relationships:
    # User has many Enrollments (One-to-Many)
    # 'Enrollment' is the related model. 'backref='user'' creates a 'user' attribute on Enrollment instances.
    # 'cascade='all, delete-orphan'' means if a User is deleted, all their associated Enrollments are also deleted.
    enrollments = db.relationship('Enrollment', backref='user', cascade='all, delete-orphan', lazy=True)
    
    # User has many Reviews (One-to-Many)
    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan', lazy=True)
    
    # User (as instructor) has many Courses (One-to-Many)
    courses = db.relationship('Course', backref='instructor', cascade='all, delete-orphan', lazy=True)

    # Serialization rules:
    # '-password_hash' means don't include password_hash in the dictionary output (security!).
    # Other rules prevent infinite recursion when serializing nested objects (e.g., a User's enrollments shouldn't try to serialize the User again).
    serialize_rules = (
        '-password_hash',
        '-enrollments.user',
        '-reviews.user',
        '-courses.instructor'
    )

    # Password hashing methods:
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Validations:
    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        return username

    @validates('email')
    def validate_email(self, key, email):
        if not email or "@" not in email:
            raise ValueError("Invalid email format.")
        return email

    @validates('role')
    def validate_role(self, key, role):
        valid_roles = ['student', 'instructor']
        if role not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}.")
        return role

    def __repr__(self):
        return f'<User {self.id}: {self.username}>'

# --- Course Model ---
class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False) # e.g., 'Beginner', 'Intermediate', 'Advanced'
    duration_hours = db.Column(db.Integer, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Foreign Key to User (instructor)

    # Relationships:
    # Course has many Enrollments (One-to-Many)
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan', lazy=True)
    # Course has many Reviews (One-to-Many)
    reviews = db.relationship('Review', backref='course', cascade='all, delete-orphan', lazy=True)

    # Serialization rules
    serialize_rules = (
        '-enrollments.course',
        '-reviews.course',
        '-instructor.courses' # Prevent recursion back to instructor's courses
    )

    # Validations:
    @validates('title')
    def validate_title(self, key, title):
        if not title or len(title) < 5:
            raise ValueError("Title must be at least 5 characters long.")
        return title

    @validates('description')
    def validate_description(self, key, description):
        if not description or len(description) < 20: # String format validation (min length)
            raise ValueError("Description must be at least 20 characters long.")
        return description

    @validates('difficulty')
    def validate_difficulty(self, key, difficulty):
        valid_difficulties = ['Beginner', 'Intermediate', 'Advanced']
        if difficulty not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of {valid_difficulties}.")
        return difficulty

    @validates('duration_hours')
    def validate_duration_hours(self, key, duration_hours):
        # Data type validation (ensure it's a number) and format validation (positive)
        if not isinstance(duration_hours, (int, float)):
            raise ValueError("Duration must be a number in hours.")
        if duration_hours <= 0:
            raise ValueError("Duration must be a positive number in hours.")
        return duration_hours

    def __repr__(self):
        return f'<Course {self.id}: {self.title}>'

# --- Enrollment Model (Many-to-Many Association Table) ---
class Enrollment(db.Model, SerializerMixin):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # User submittable attribute!

    # Serialization rules:
    # When serializing an Enrollment, we want to see its associated user and course,
    # but prevent them from recursively serializing their own enrollments, which would loop back.
    serialize_rules = (
        '-user.enrollments',
        '-course.enrollments',
        '-user.reviews',    # Avoid any other user recursion
        '-user.courses',    # Avoid any other user recursion
        '-course.reviews',  # Avoid any other course recursion
    )

    @validates('enrollment_date')
    def validate_enrollment_date(self, key, enrollment_date):
        # Data type validation: Ensure it's a datetime object or a string parseable as one.
        if isinstance(enrollment_date, str):
            try:
                enrollment_date = datetime.fromisoformat(enrollment_date)
            except ValueError:
                raise ValueError("Enrollment date must be a valid ISO 8601 string (YYYY-MM-DDTHH:MM:SS) or a datetime object.")
        
        if not isinstance(enrollment_date, datetime):
            raise ValueError("Enrollment date must be a valid datetime object.")

        # Example: Do not allow enrollment dates too far in the future
        if enrollment_date > datetime.utcnow() + timedelta(days=365): # Max 1 year in the future
            raise ValueError("Enrollment date cannot be more than 1 year in the future.")
        
        return enrollment_date


    def __repr__(self):
        return f'<Enrollment {self.id}: User {self.user_id} in Course {self.course_id}>'

# --- Review Model ---
class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    text_content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5 scale
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    # Serialization rules
    serialize_rules = (
        '-user.reviews',
        '-course.reviews',
        '-user.enrollments', # Avoid other user recursion
        '-user.courses',     # Avoid other user recursion
        '-course.enrollments' # Avoid other course recursion
    )

    @validates('text_content')
    def validate_text_content(self, key, text_content):
        if not text_content or len(text_content) < 10:
            raise ValueError("Review content must be at least 10 characters long.")
        return text_content

    @validates('rating')
    def validate_rating(self, key, rating):
        # Data type validation: Ensure it's an integer
        if not isinstance(rating, int):
            raise ValueError("Rating must be an integer.")
        # Range validation (1-5)
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        return rating

    def __repr__(self):
        return f'<Review {self.id}: Course {self.course_id} by User {self.user_id} - Rating: {self.rating}>'