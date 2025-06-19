# server/app.py
from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from flask_cors import CORS # Used to handle cross-origin requests from your React frontend
from models import db, User, Course, Enrollment, Review # Import your models and db object

# Initialize Migrate globally, but don't bind to an app instance yet.
# This is part of the application factory pattern.
migrate = Migrate()

def create_app():
    # This function creates and configures the Flask application.
    app = Flask(__name__)
    # Database URI: 'sqlite:///coursify.db' means a SQLite database file named coursify.db
    # will be created in your server/ directory.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coursify.db'
    # Disable tracking modifications (reduces overhead)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Ensures JSON responses are pretty-printed (not compacted on one line)
    app.json.compact = False
    # Secret key for sessions (needed if you use Flask sessions, which you will for authentication)
    # IMPORTANT: Change this to a truly random string in production!
    app.secret_key = 'your_super_secret_and_complex_key_here' 

    # Bind SQLAlchemy db instance to this app
    db.init_app(app)
    # Initialize Flask-Migrate with this app and db
    migrate.init_app(app, db)
    # Enable CORS for all routes (important for React frontend to talk to Flask backend)
    CORS(app) 

    # --- Define your routes and API endpoints within this function ---

    @app.route('/')
    def home():
        return '<h1>Coursify API</h1>'

    # Global error handler for 400 Bad Request (often triggered by validation errors)
    @app.errorhandler(400)
    def handle_400_error(e):
        # Default error message for Flask's built-in 400 errors (e.g., if JSON parse fails)
        message = "Bad Request."
        # If the error object has a description (like from request.get_json's error), use it
        if hasattr(e, 'description') and e.description:
            message = e.description
        return make_response(jsonify({"errors": [message]}), 400)

    # --- User Routes ---
    # For listing all users (admin or debugging)
    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        # Serialize each user. Exclude sensitive info and deep nested relationships for lists.
        user_data = [user.to_dict(rules=('-password_hash', '-enrollments', '-reviews', '-courses')) for user in users]
        return make_response(jsonify(user_data), 200)

    # For getting a single user's details
    @app.route('/users/<int:id>', methods=['GET'])
    def get_user_by_id(id):
        user = User.query.get(id)
        if not user:
            return make_response(jsonify({"error": "User not found"}), 404)
        # Full serialization including nested relationships for a specific user's detail page.
        # Serialization rules in models.py handle recursion.
        return make_response(jsonify(user.to_dict()), 200)

    # --- Course Routes (Full CRUD for one resource - Courses) ---
    # GET: List all courses (Read)
    # POST: Create a new course (Create)
    @app.route('/courses', methods=['GET', 'POST'])
    def courses_list_create():
        if request.method == 'GET':
            courses = Course.query.all()
            # For the list view, typically you don't need all nested relationships (like reviews, enrollments).
            # The 'rules' argument overrides default serialize_rules for this specific endpoint.
            course_data = [course.to_dict(rules=('-enrollments', '-reviews', '-instructor.password_hash')) for course in courses]
            return make_response(jsonify(course_data), 200)
        
        elif request.method == 'POST':
            data = request.get_json() # Get JSON data from the request body
            try:
                # Basic check for required fields from frontend
                required_fields = ['title', 'description', 'difficulty', 'duration_hours', 'instructor_id']
                if not all(k in data for k in required_fields):
                    return make_response(jsonify({"errors": ["Missing required fields for course creation."]}, 400))
                
                # Find the instructor (User) instance
                instructor = User.query.get(data['instructor_id'])
                if not instructor or instructor.role != 'instructor':
                    return make_response(jsonify({"errors": ["Instructor not found or is not an instructor."]}, 404))

                # Create new Course instance (this will trigger model validations)
                new_course = Course(
                    title=data['title'],
                    description=data['description'],
                    difficulty=data['difficulty'],
                    duration_hours=data['duration_hours'],
                    instructor_id=data['instructor_id']
                )
                db.session.add(new_course)
                db.session.commit()
                # Return the newly created course object
                return make_response(jsonify(new_course.to_dict()), 201) # 201 Created status
            except ValueError as e: # Catch validation errors from models.py
                db.session.rollback() # Rollback the session if validation fails
                return make_response(jsonify({"errors": [str(e)]}), 400) # 400 Bad Request
            except Exception as e: # Catch any other unexpected errors
                db.session.rollback()
                return make_response(jsonify({"errors": ["An unexpected error occurred during course creation", str(e)]}), 500)


    # GET: Retrieve single course (Read)
    # PATCH: Update single course (Update)
    # DELETE: Delete single course (Delete)
    @app.route('/courses/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
    def course_detail_update_delete(id):
        course = Course.query.get(id)
        if not course:
            return make_response(jsonify({"error": "Course not found"}), 404)

        if request.method == 'GET':
            # For a detailed view, include all nested relationships
            return make_response(jsonify(course.to_dict()), 200) # serialize_rules will handle nesting
        
        elif request.method == 'PATCH':
            data = request.get_json()
            try:
                # Update only provided fields
                for attr in data:
                    if hasattr(course, attr): # Check if attribute exists on model
                        setattr(course, attr, data[attr])
                db.session.add(course) # Add to session to trigger validations for changed attributes
                db.session.commit()
                return make_response(jsonify(course.to_dict()), 200) # 200 OK
            except ValueError as e: # Catch validation errors
                db.session.rollback()
                return make_response(jsonify({"errors": [str(e)]}), 400)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": ["An unexpected error occurred during course update", str(e)]}), 500)

        elif request.method == 'DELETE':
            try:
                db.session.delete(course) # Mark for deletion
                db.session.commit() # Commit deletion (cascades will delete enrollments/reviews)
                return make_response(jsonify({}), 204) # 204 No Content for successful deletion
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": ["An error occurred during course deletion", str(e)]}), 500)

    # --- Enrollment Routes ---
    # POST: Create a new enrollment (Create)
    # GET: List all enrollments (Read - e.g., for admin/debugging)
    @app.route('/enrollments', methods=['GET', 'POST'])
    def enrollments_list_create():
        if request.method == 'GET':
            enrollments = Enrollment.query.all()
            return make_response(jsonify([e.to_dict() for e in enrollments]), 200)
        elif request.method == 'POST':
            data = request.get_json()
            try:
                required_fields = ['user_id', 'course_id', 'enrollment_date']
                if not all(field in data for field in required_fields):
                    return make_response(jsonify({"errors": ["Missing required fields: 'user_id', 'course_id', 'enrollment_date'."]}), 400)
                
                user = User.query.get(data['user_id'])
                course = Course.query.get(data['course_id'])
                if not user: return make_response(jsonify({"errors": ["User not found."]} ), 404)
                if not course: return make_response(jsonify({"errors": ["Course not found."]} ), 404)

                # Optional: Check for existing enrollment to prevent duplicates
                existing_enrollment = Enrollment.query.filter_by(user_id=data['user_id'], course_id=data['course_id']).first()
                if existing_enrollment:
                    return make_response(jsonify({"errors": ["User is already enrolled in this course."]} ), 409) # 409 Conflict

                new_enrollment = Enrollment(
                    user_id=data['user_id'],
                    course_id=data['course_id'],
                    enrollment_date=data['enrollment_date'] # Model validation handles date format
                )
                db.session.add(new_enrollment)
                db.session.commit()
                return make_response(jsonify(new_enrollment.to_dict()), 201)
            except ValueError as e:
                db.session.rollback()
                return make_response(jsonify({"errors": [str(e)]}), 400)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": ["An unexpected error occurred during enrollment creation", str(e)]}), 500)

    # --- Review Routes ---
    # POST: Create a new review (Create)
    @app.route('/reviews', methods=['POST'])
    def create_review():
        data = request.get_json()
        try:
            required_fields = ['text_content', 'rating', 'user_id', 'course_id']
            if not all(k in data for k in required_fields):
                return make_response(jsonify({"errors": ["Missing required fields: 'text_content', 'rating', 'user_id', 'course_id'."]}), 400)
            
            user = User.query.get(data['user_id'])
            course = Course.query.get(data['course_id'])
            if not user: return make_response(jsonify({"errors": ["User not found."]} ), 404)
            if not course: return make_response(jsonify({"errors": ["Course not found."]} ), 404)

            new_review = Review(
                text_content=data['text_content'],
                rating=data['rating'],
                user_id=data['user_id'],
                course_id=data['course_id']
            )
            db.session.add(new_review)
            db.session.commit()
            return make_response(jsonify(new_review.to_dict()), 201)
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": ["An unexpected error occurred during review creation", str(e)]}), 500)


    # Flask CLI command to seed the database
    @app.cli.command('seed')
    def seed_command():
        # Import run_seed_data here to avoid circular imports at module level
        from seed import run_seed_data
        with app.app_context(): # Ensures db operations are within the Flask application context
            run_seed_data(app) # Pass the app instance to the seed function
        print("Database seeded!")

    return app # The factory function MUST return the created app instance


# This block executes when app.py is run directly (e.g., `python app.py`)
# It creates an app instance and starts the development server.
if __name__ == '__main__':
    app_instance = create_app() # Get the configured app instance from the factory
    app_instance.run(port=5555, debug=True)