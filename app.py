from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
import datetime

try:
    from .models import db, Exercise, Workout, WorkoutExercise
    from .schemas import (
        SimpleExerciseSchema,
        SimpleWorkoutSchema,
        SimpleWorkoutExerciseSchema,
        WorkoutDetailSchema,
        ExerciseDetailSchema,
        WorkoutExerciseDetailSchema
    )
except ImportError:
    from models import db, Exercise, Workout, WorkoutExercise
    from schemas import (
        SimpleExerciseSchema,
        SimpleWorkoutSchema,
        SimpleWorkoutExerciseSchema,
        WorkoutDetailSchema,
        ExerciseDetailSchema,
        WorkoutExerciseDetailSchema
    )

import os

app = Flask(__name__)
# Ensure the database always resolves to server/instance/app.db
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'instance', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

# Instantiate schemas
simple_workout_schema = SimpleWorkoutSchema()
workouts_schema = SimpleWorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

simple_exercise_schema = SimpleExerciseSchema()
exercises_schema = SimpleExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

simple_workout_exercise_schema = SimpleWorkoutExerciseSchema()
workout_exercise_detail_schema = WorkoutExerciseDetailSchema()


# --- Home Route ---
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Workout Tracking API!"})


# --- Workout Endpoints ---

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout_detail_schema.dump(workout)), 200


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = request.get_json() or {}
    try:
        # Validate data with Marshmallow Schema
        validated_data = simple_workout_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        # Create Model Instance
        new_workout = Workout(
            date=validated_data['date'],
            duration_minutes=validated_data['duration_minutes'],
            notes=validated_data.get('notes')
        )
        db.session.add(new_workout)
        db.session.commit()
        return jsonify(simple_workout_schema.dump(new_workout)), 201
    except ValueError as val_err:
        db.session.rollback()
        return jsonify({"errors": {"validation": [str(val_err)]}}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    try:
        # Note: cascade delete on relationships is defined on the models
        db.session.delete(workout)
        db.session.commit()
        return jsonify({"message": f"Workout {id} and its associated workout exercises have been deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- Exercise Endpoints ---

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404
    return jsonify(exercise_detail_schema.dump(exercise)), 200


@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json() or {}
    try:
        # Validate data with Marshmallow Schema
        validated_data = simple_exercise_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        # Create Model Instance
        new_exercise = Exercise(
            name=validated_data['name'],
            category=validated_data['category'],
            equipment_needed=validated_data['equipment_needed']
        )
        db.session.add(new_exercise)
        db.session.commit()
        return jsonify(simple_exercise_schema.dump(new_exercise)), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": {"name": ["An exercise with this name already exists."]}}), 400
    except ValueError as val_err:
        db.session.rollback()
        return jsonify({"errors": {"validation": [str(val_err)]}}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    try:
        # Cascade delete is set in Exercise.workout_exercises relationships
        db.session.delete(exercise)
        db.session.commit()
        return jsonify({"message": f"Exercise {id} and its associated workout exercises have been deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- Join Table (Workout Exercises) Endpoint ---

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get(workout_id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404

    data = request.get_json() or {}
    # Inject foreign keys for schema validation
    data['workout_id'] = workout_id
    data['exercise_id'] = exercise_id

    try:
        # Validate data using schema
        validated_data = simple_workout_exercise_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        # Create new workout exercise link
        new_we = WorkoutExercise(
            workout_id=validated_data['workout_id'],
            exercise_id=validated_data['exercise_id'],
            reps=validated_data.get('reps'),
            sets=validated_data.get('sets'),
            duration_seconds=validated_data.get('duration_seconds')
        )
        db.session.add(new_we)
        db.session.commit()
        # Serialize with detailed schema so exercise metadata is included
        return jsonify(workout_exercise_detail_schema.dump(new_we)), 201
    except ValueError as val_err:
        db.session.rollback()
        return jsonify({"errors": {"validation": [str(val_err)]}}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
