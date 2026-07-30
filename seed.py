#!/usr/bin/env python3

import sys
import os
from datetime import date

# Add the server directory to python path if not already there
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .app import app
    from .models import db, Exercise, Workout, WorkoutExercise
except ImportError:
    from app import app
    from models import db, Exercise, Workout, WorkoutExercise

def run_seed():
    print("Initializing database seed...")
    with app.app_context():
        # Clear out existing data
        print("Clearing out existing data...")
        db.session.query(WorkoutExercise).delete()
        db.session.query(Workout).delete()
        db.session.query(Exercise).delete()
        db.session.commit()

        print("Seeding Exercises...")
        exercises = [
            Exercise(name="Squats", category="Strength", equipment_needed=False),
            Exercise(name="Treadmill Run", category="Cardio", equipment_needed=True),
            Exercise(name="Yoga Stretching", category="Flexibility", equipment_needed=False),
            Exercise(name="Bench Press", category="Strength", equipment_needed=True),
            Exercise(name="Planks", category="Balance", equipment_needed=False),
            Exercise(name="Bicep Curls", category="Strength", equipment_needed=True),
            Exercise(name="Jumping Jacks", category="Warm-up", equipment_needed=False)
        ]
        db.session.add_all(exercises)
        db.session.commit()

        # Fetch saved exercises to get IDs
        ex_squats = Exercise.query.filter_by(name="Squats").first()
        ex_treadmill = Exercise.query.filter_by(name="Treadmill Run").first()
        ex_yoga = Exercise.query.filter_by(name="Yoga Stretching").first()
        ex_bench = Exercise.query.filter_by(name="Bench Press").first()
        ex_planks = Exercise.query.filter_by(name="Planks").first()
        ex_jacks = Exercise.query.filter_by(name="Jumping Jacks").first()

        print("Seeding Workouts...")
        workouts = [
            Workout(
                date=date(2026, 7, 28),
                duration_minutes=45,
                notes="Leg day and core session."
            ),
            Workout(
                date=date(2026, 7, 29),
                duration_minutes=30,
                notes="Quick morning cardio and warm-up."
            ),
            Workout(
                date=date(2026, 7, 30),
                duration_minutes=60,
                notes="Full body strength and mobility workout."
            )
        ]
        db.session.add_all(workouts)
        db.session.commit()

        # Fetch saved workouts
        workout_1 = workouts[0]
        workout_2 = workouts[1]
        workout_3 = workouts[2]

        print("Seeding Workout Exercises (links)...")
        links = [
            # Workout 1: Leg and Core
            WorkoutExercise(
                workout_id=workout_1.id,
                exercise_id=ex_squats.id,
                reps=12,
                sets=4,
                duration_seconds=180
            ),
            WorkoutExercise(
                workout_id=workout_1.id,
                exercise_id=ex_planks.id,
                reps=1,
                sets=3,
                duration_seconds=60
            ),
            # Workout 2: Quick Cardio and Warm-up
            WorkoutExercise(
                workout_id=workout_2.id,
                exercise_id=ex_jacks.id,
                reps=50,
                sets=2,
                duration_seconds=90
            ),
            WorkoutExercise(
                workout_id=workout_2.id,
                exercise_id=ex_treadmill.id,
                reps=None,
                sets=1,
                duration_seconds=1200
            ),
            # Workout 3: Full Body Strength & Mobility
            WorkoutExercise(
                workout_id=workout_3.id,
                exercise_id=ex_bench.id,
                reps=8,
                sets=4,
                duration_seconds=240
            ),
            WorkoutExercise(
                workout_id=workout_3.id,
                exercise_id=ex_yoga.id,
                reps=None,
                sets=1,
                duration_seconds=600
            )
        ]
        db.session.add_all(links)
        db.session.commit()

        print("Database successfully seeded!")
        print(f"Total Exercises: {Exercise.query.count()}")
        print(f"Total Workouts: {Workout.query.count()}")
        print(f"Total WorkoutExercises: {WorkoutExercise.query.count()}")

if __name__ == '__main__':
    run_seed()
