from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates


db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = "exercise"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    category = db.Column(db.String(80), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercise",
        back_populates="exercises",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_exercise_name_not_blank"),
        CheckConstraint("length(trim(category)) > 0", name="ck_exercise_category_not_blank"),
    )

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Exercise name must be a non-empty string")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Exercise category must be a non-empty string")
        return value.strip()


class Workout(db.Model):
    __tablename__ = "workout"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=False, default="")

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercise",
        back_populates="workouts",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Workout duration must be greater than zero")
        return value

    @validates("notes")
    def validate_notes(self, key, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("Workout notes must be text")
        return value.strip() if isinstance(value, str) else value


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercise"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
        CheckConstraint("reps > 0", name="ck_workout_exercise_reps_positive"),
        CheckConstraint("sets > 0", name="ck_workout_exercise_sets_positive"),
        CheckConstraint("duration_seconds > 0", name="ck_workout_exercise_duration_positive"),
    )

    @validates("reps")
    def validate_reps(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Reps must be greater than zero")
        return value

    @validates("sets")
    def validate_sets(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Sets must be greater than zero")
        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Duration seconds must be greater than zero")
        return value
