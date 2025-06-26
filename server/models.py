from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='student')
    
    enrollments = db.relationship('Enrollment', backref='user', cascade='all, delete-orphan', lazy=True)
    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan', lazy=True)
    courses = db.relationship('Course', backref='instructor', cascade='all, delete-orphan', lazy=True)

    serialize_rules = (
        '-password_hash',
        '-enrollments.user',
        '-reviews.user',
        '-courses.instructor',
        '-reviews.course.reviews'  # Prevent deep nesting
    )

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

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

class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan', lazy=True)
    reviews = db.relationship('Review', backref='course', cascade='all, delete-orphan', lazy=True)

    serialize_rules = (
        '-enrollments.course',
        '-reviews.course',
        '-instructor.enrollments',
        '-instructor.reviews',
        '-instructor.courses',
        '-reviews.user.reviews',  # Prevent recursion
    )

    @validates('title')
    def validate_title(self, key, title):
        if not title or len(title) < 5:
            raise ValueError("Title must be at least 5 characters long.")
        return title

    @validates('description')
    def validate_description(self, key, description):
        if not description or len(description) < 20:
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
        if not isinstance(duration_hours, int):
            raise ValueError("Duration must be an integer.")
        if duration_hours <= 0:
            raise ValueError("Duration must be a positive number in hours.")
        return duration_hours

    def __repr__(self):
        return f'<Course {self.id}: {self.title}>'

class Enrollment(db.Model, SerializerMixin):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    serialize_rules = (
        '-user.enrollments',
        '-user.reviews',
        '-user.courses',
        '-course.enrollments',
        '-course.reviews',
        '-course.instructor',
    )

    @validates('enrollment_date')
    def validate_enrollment_date(self, key, enrollment_date):
        if isinstance(enrollment_date, str):
            try:
                enrollment_date = datetime.fromisoformat(enrollment_date)
            except ValueError:
                 raise ValueError("Enrollment date must be in ISO format.")
        
        if not isinstance(enrollment_date, datetime):
            raise ValueError("Enrollment date must be a valid datetime object.")

        if enrollment_date > datetime.utcnow() + timedelta(days=365):
            raise ValueError("Enrollment date cannot be more than 1 year in the future.")
        
        return enrollment_date

    def __repr__(self):
        return f'<Enrollment {self.id}: User {self.user_id} in Course {self.course_id}>'

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    text_content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    serialize_rules = (
        '-user.reviews',
        '-user.enrollments',
        '-user.courses',
        '-course.reviews',
        '-course.enrollments',
        '-course.instructor',
        '-user.password_hash'  # Hide sensitive data
    )

    @validates('text_content')
    def validate_text_content(self, key, text_content):
        if not text_content or len(text_content) < 10:
            raise ValueError("Review content must be at least 10 characters long.")
        return text_content

    @validates('rating')
    def validate_rating(self, key, rating):
        if not isinstance(rating, int):
            raise ValueError("Rating must be an integer.")
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        return rating

    def __repr__(self):
        return f'<Review {self.id}: Course {self.course_id} by User {self.user_id} - Rating: {self.rating}>'