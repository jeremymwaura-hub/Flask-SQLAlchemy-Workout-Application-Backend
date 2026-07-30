#!/usr/bin/env python3
from datetime import date

from app import app, db
from models import Exercise, Workout, WorkoutExercise

with app.app_context():
    WorkoutExercise.query.delete()
    Exercise.query.delete()
    Workout.query.delete()

    squat = Exercise(name="Squat", category="Lower Body", equipment_needed=False)
    push_up = Exercise(name="Push Up", category="Upper Body", equipment_needed=False)
    deadlift = Exercise(name="Deadlift", category="Full Body", equipment_needed=True)

    workout_one = Workout(date=date(2026, 7, 30), duration_minutes=45, notes="Strength focus")
    workout_two = Workout(date=date(2026, 7, 31), duration_minutes=30, notes="Cardio and core")

    db.session.add_all([squat, push_up, deadlift, workout_one, workout_two])
    db.session.commit()

    db.session.add_all([
        WorkoutExercise(workout_id=workout_one.id, exercise_id=squat.id, reps=10, sets=3, duration_seconds=30),
        WorkoutExercise(workout_id=workout_one.id, exercise_id=push_up.id, reps=12, sets=3, duration_seconds=45),
        WorkoutExercise(workout_id=workout_two.id, exercise_id=deadlift.id, reps=8, sets=4, duration_seconds=60),
    ])
    db.session.commit()
