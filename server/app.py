from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Course, Enrollment, Review

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coursify.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.json.compact = False
    app.secret_key = 'your_super_secret_key'

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    @app.errorhandler(400)
    def handle_400_error(e):
        message = e.description if hasattr(e, 'description') else "Bad Request."
        return make_response(jsonify({"errors": [message]}), 400)

    @app.route('/')
    def home():
        return '<h1>Coursify API</h1>'

    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        user_data = [user.to_dict(rules=('-password_hash',)) for user in users]
        return make_response(jsonify(user_data), 200)

    @app.route('/users/<int:id>', methods=['GET'])
    def get_user_by_id(id):
        user = User.query.get(id)
        if not user:
            return make_response(jsonify({"error": "User not found"}), 404)
        return make_response(jsonify(user.to_dict())), 200

    @app.route('/courses', methods=['GET', 'POST'])
    def courses_list_create():
        if request.method == 'GET':
            courses = Course.query.all()
            course_data = [course.to_dict() for course in courses]
            return make_response(jsonify(course_data), 200)
        
        elif request.method == 'POST':
            data = request.get_json()
            try:
                required_fields = ['title', 'description', 'difficulty', 'duration_hours', 'instructor_id']
                if not all(k in data for k in required_fields):
                    return make_response(jsonify({"errors": ["Missing required fields"]}), 400)
                
                instructor = User.query.get(data['instructor_id'])
                if not instructor:
                    return make_response(jsonify({"errors": ["Instructor not found"]}), 404)
                if instructor.role != 'instructor':
                    return make_response(jsonify({"errors": ["User is not an instructor"]}), 400)

                new_course = Course(
                    title=data['title'],
                    description=data['description'],
                    difficulty=data['difficulty'],
                    duration_hours=data['duration_hours'],
                    instructor_id=data['instructor_id']
                )
                db.session.add(new_course)
                db.session.commit()
                return make_response(jsonify(new_course.to_dict()), 201)
            except ValueError as e:
                db.session.rollback()
                return make_response(jsonify({"errors": [str(e)]}), 400)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": ["Server error: " + str(e)]}), 500)
        # Ensure a response is always returned
    @app.route('/courses/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
    def course_detail_update_delete(id):
        course = Course.query.get(id)
        if not course:
            return make_response(jsonify({"error": "Course not found"}), 404)

        if request.method == 'GET':
            return make_response(jsonify(course.to_dict()), 200)
        
        elif request.method == 'PATCH':
            data = request.get_json()
            try:
                for attr in data:
                    if hasattr(course, attr):
                        setattr(course, attr, data[attr])
                db.session.commit()
                return make_response(jsonify(course.to_dict()), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response(jsonify({"errors": [str(e)]}), 400)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": ["Server error: " + str(e)]}), 500)

        elif request.method == 'DELETE':
            try:
                db.session.delete(course)
                db.session.commit()
                return make_response('', 204)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": ["Deletion error: " + str(e)]}), 500)
        # Ensure a response is always returned
        return make_response(jsonify({"errors": ["Invalid request method."]}), 405)

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
                    return make_response(jsonify({"errors": ["Missing required fields"]}), 400)
                
                user = User.query.get(data['user_id'])
                course = Course.query.get(data['course_id'])
                if not user: 
                    return make_response(jsonify({"errors": ["User not found"]}), 404)
                if not course: 
                    return make_response(jsonify({"errors": ["Course not found"]}), 404)

                existing_enrollment = Enrollment.query.filter_by(
                    user_id=data['user_id'], 
                    course_id=data['course_id']
                ).first()
                if existing_enrollment:
                    return make_response(jsonify({"errors": ["User already enrolled"]}), 409)

                new_enrollment = Enrollment(
                    user_id=data['user_id'],
                    course_id=data['course_id'],
                    enrollment_date=data['enrollment_date']
                )
                db.session.add(new_enrollment)
                db.session.commit()
                return make_response(jsonify(new_enrollment.to_dict()), 201)
            except ValueError as e:
                db.session.rollback()
                return make_response(jsonify({"errors": [str(e)]}), 400)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({"errors": ["Server error: " + str(e)]}), 500)
        # Ensure a response is always returned for unsupported methods
        return make_response(jsonify({"errors": ["Invalid request method."]}), 405)

    @app.route('/reviews', methods=['POST'])
    def create_review():
        data = request.get_json()
        try:
            required_fields = ['text_content', 'rating', 'user_id', 'course_id']
            if not all(k in data for k in required_fields):
                return make_response(jsonify({"errors": ["Missing required fields"]}), 400)
            
            user = User.query.get(data['user_id'])
            course = Course.query.get(data['course_id'])
            if not user: 
                return make_response(jsonify({"errors": ["User not found"]}), 404)
            if not course: 
                return make_response(jsonify({"errors": ["Course not found"]}), 404)

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
            return make_response(jsonify({"errors": ["Server error: " + str(e)]}), 500)

    @app.cli.command('seed')
    def seed_command():
        from seed import run_seed_data
        with app.app_context():
            run_seed_data(app)
        print("Database seeded!")

    return app

app_instance = create_app()

if __name__ == '__main__':
    app_instance.run(port=5555, debug=True)