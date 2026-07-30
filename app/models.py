from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint
import datetime

db = SQLAlchemy()

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    # Exercise has many WorkoutExercises
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan'
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint('length(name) >= 3', name='check_exercise_name_length'),
    )

    # Model Validations
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) < 3:
            raise ValueError("Exercise name must be at least 3 characters long.")
        return name

    @validates('category')
    def validate_category(self, key, category):
        allowed_categories = ['Cardio', 'Strength', 'Flexibility', 'Balance', 'Warm-up', 'Cool-down']
        if not category or category not in allowed_categories:
            raise ValueError(f"Category must be one of: {', '.join(allowed_categories)}")
        return category

    def __repr__(self):
        return f"<Exercise id={self.id}, name='{self.name}', category='{self.category}'>"


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    # Workout has many WorkoutExercises
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan'
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_workout_duration_positive'),
    )

    # Model Validations
    @validates('duration_minutes')
    def validate_duration_minutes(self, key, duration_minutes):
        if duration_minutes is None:
            raise ValueError("Duration in minutes is required.")
        if int(duration_minutes) <= 0:
            raise ValueError("Workout duration must be a positive integer.")
        return duration_minutes

    @validates('date')
    def validate_date(self, key, date_val):
        if not date_val:
            raise ValueError("Workout date is required.")
        # Ensure date_val is a date object or a string that can be parsed as a date
        if isinstance(date_val, str):
            try:
                date_val = datetime.datetime.strptime(date_val, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format.")
        elif not isinstance(date_val, (datetime.date, datetime.datetime)):
            raise ValueError("Date must be a date object or a string in YYYY-MM-DD format.")
        return date_val

    def __repr__(self):
        return f"<Workout id={self.id}, date='{self.date}', duration_minutes={self.duration_minutes}>"


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Table constraints
    __table_args__ = (
        CheckConstraint('reps >= 0', name='check_reps_non_negative'),
        CheckConstraint('sets > 0', name='check_sets_positive'),
        CheckConstraint('duration_seconds >= 0', name='check_duration_seconds_non_negative'),
    )

    # Model Validations
    @validates('reps')
    def validate_reps(self, key, reps):
        if reps is not None and int(reps) < 0:
            raise ValueError("Reps must be a non-negative integer.")
        return reps

    @validates('sets')
    def validate_sets(self, key, sets):
        if sets is not None and int(sets) <= 0:
            raise ValueError("Sets must be a positive integer.")
        return sets

    @validates('duration_seconds')
    def validate_duration_seconds(self, key, duration_seconds):
        if duration_seconds is not None and int(duration_seconds) < 0:
            raise ValueError("Duration seconds must be a non-negative integer.")
        return duration_seconds

    def __repr__(self):
        return f"<WorkoutExercise id={self.id}, workout_id={self.workout_id}, exercise_id={self.exercise_id}>"
