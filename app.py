"""Flask application for managing workouts, exercises, and workout-exercise relationships."""

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import Workout, WorkoutExercise, Exercise, db
from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False

migrate = Migrate(app, db)
db.init_app(app)

exercise_schema = ExerciseSchema()
workout_schema = WorkoutSchema()
workout_exercise_schema = WorkoutExerciseSchema()
exercise_schema_many = ExerciseSchema(many=True)
workout_schema_many = WorkoutSchema(many=True)
workout_exercise_schema_many = WorkoutExerciseSchema(many=True)


@app.route("/workouts", methods=["GET"])
def list_workouts():
    workouts = Workout.query.order_by(Workout.date.desc()).all()
    return jsonify(workout_schema_many.dump(workouts))


@app.route("/workouts/<int:workout_id>", methods=["GET"])
def get_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    return jsonify(workout_schema.dump(workout))


@app.route("/workouts", methods=["POST"])
def create_workout():
    payload = request.get_json(silent=True) or {}
    try:
        data = workout_schema.load(payload)
    except Exception as exc:
        return jsonify({"errors": exc.messages if hasattr(exc, "messages") else str(exc)}), 400

    workout = Workout(**data)
    try:
        db.session.add(workout)
        db.session.commit()
    except (IntegrityError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify(workout_schema.dump(workout)), 201


@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted"}), 200


@app.route("/exercises", methods=["GET"])
def list_exercises():
    exercises = Exercise.query.order_by(Exercise.name.asc()).all()
    return jsonify(exercise_schema_many.dump(exercises))


@app.route("/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    return jsonify(exercise_schema.dump(exercise))


@app.route("/exercises", methods=["POST"])
def create_exercise():
    payload = request.get_json(silent=True) or {}
    try:
        data = exercise_schema.load(payload)
    except Exception as exc:
        return jsonify({"errors": exc.messages if hasattr(exc, "messages") else str(exc)}), 400

    exercise = Exercise(**data)
    try:
        db.session.add(exercise)
        db.session.commit()
    except (IntegrityError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify(exercise_schema.dump(exercise)), 201


@app.route("/exercises/<int:exercise_id>", methods=["DELETE"])
def delete_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": "Exercise deleted"}), 200


@app.route("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises", methods=["POST"])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get_or_404(workout_id)
    exercise = Exercise.query.get_or_404(exercise_id)
    payload = request.get_json(silent=True) or {}

    try:
        data = workout_exercise_schema.load(payload)
    except Exception as exc:
        return jsonify({"errors": exc.messages if hasattr(exc, "messages") else str(exc)}), 400

    existing = WorkoutExercise.query.filter_by(workout_id=workout.id, exercise_id=exercise.id).first()
    if existing:
        return jsonify({"error": "Exercise already added to this workout"}), 409

    workout_exercise = WorkoutExercise(
        workout_id=workout.id,
        exercise_id=exercise.id,
        reps=data.get("reps"),
        sets=data.get("sets"),
        duration_seconds=data.get("duration_seconds"),
    )
    try:
        db.session.add(workout_exercise)
        db.session.commit()
    except (IntegrityError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(port=5555, debug=True)
