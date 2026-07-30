import unittest
import json
import datetime
from datetime import date
from flask import Flask

# Ensure we import our app and models correctly
try:
    from .app import app, db
    from .models import Exercise, Workout, WorkoutExercise
except ImportError:
    from app import app, db
    from models import Exercise, Workout, WorkoutExercise


class WorkoutAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_client = app.test_client()

        # Create tables
        with app.app_context():
            db.create_all()

            # Seed basic test data
            self.ex1 = Exercise(name="Pushups", category="Strength", equipment_needed=False)
            self.ex2 = Exercise(name="Running", category="Cardio", equipment_needed=False)
            db.session.add_all([self.ex1, self.ex2])

            self.w1 = Workout(date=date(2026, 7, 30), duration_minutes=45, notes="Morning routine")
            db.session.add(self.w1)
            db.session.commit()

            # Save IDs for reference
            self.ex1_id = self.ex1.id
            self.ex2_id = self.ex2.id
            self.w1_id = self.w1.id

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # ==========================================
    # 1. TEST MODEL VALIDATIONS & CONSTRAINTS
    # ==========================================

    def test_exercise_validation_name_too_short(self):
        """Test that Exercise name must be at least 3 characters long."""
        with app.app_context():
            with self.assertRaises(ValueError):
                ex = Exercise(name="Hi", category="Strength", equipment_needed=False)
                db.session.add(ex)
                db.session.commit()

    def test_exercise_validation_invalid_category(self):
        """Test that Exercise category must be in the allowed list."""
        with app.app_context():
            with self.assertRaises(ValueError):
                ex = Exercise(name="Lunges", category="InvalidCat", equipment_needed=False)
                db.session.add(ex)
                db.session.commit()

    def test_workout_validation_negative_duration(self):
        """Test that Workout duration must be a positive integer."""
        with app.app_context():
            with self.assertRaises(ValueError):
                w = Workout(date=date(2026, 7, 30), duration_minutes=-10, notes="Bad workout")
                db.session.add(w)
                db.session.commit()

    def test_workout_exercise_validation_negative_reps(self):
        """Test that WorkoutExercise reps cannot be negative."""
        with app.app_context():
            with self.assertRaises(ValueError):
                we = WorkoutExercise(
                    workout_id=self.w1_id,
                    exercise_id=self.ex1_id,
                    reps=-5,
                    sets=3,
                    duration_seconds=60
                )
                db.session.add(we)
                db.session.commit()

    def test_workout_exercise_validation_invalid_sets(self):
        """Test that WorkoutExercise sets must be greater than 0."""
        with app.app_context():
            with self.assertRaises(ValueError):
                we = WorkoutExercise(
                    workout_id=self.w1_id,
                    exercise_id=self.ex1_id,
                    reps=10,
                    sets=0,
                    duration_seconds=60
                )
                db.session.add(we)
                db.session.commit()

    # ==========================================
    # 2. TEST ENDPOINTS & SERIALIZATION
    # ==========================================

    def test_get_workouts(self):
        """Test GET /workouts lists all workouts."""
        response = self.app_client.get('/workouts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['duration_minutes'], 45)
        self.assertEqual(data[0]['notes'], "Morning routine")

    def test_get_workout_by_id_not_found(self):
        """Test GET /workouts/<id> returns 404 if not found."""
        response = self.app_client.get('/workouts/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_get_workout_by_id_with_details(self):
        """Test GET /workouts/<id> includes reps/sets/duration and exercise info."""
        # Add a workout exercise first
        with app.app_context():
            we = WorkoutExercise(
                workout_id=self.w1_id,
                exercise_id=self.ex1_id,
                reps=15,
                sets=3,
                duration_seconds=90
            )
            db.session.add(we)
            db.session.commit()

        response = self.app_client.get(f'/workouts/{self.w1_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], self.w1_id)
        self.assertEqual(len(data['workout_exercises']), 1)
        self.assertEqual(data['workout_exercises'][0]['reps'], 15)
        self.assertEqual(data['workout_exercises'][0]['exercise']['name'], "Pushups")

    def test_post_workout_valid(self):
        """Test POST /workouts creates a new workout with valid data."""
        payload = {
            "date": "2026-08-01",
            "duration_minutes": 50,
            "notes": "Weekend session"
        }
        response = self.app_client.post(
            '/workouts',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("id", data)
        self.assertEqual(data["duration_minutes"], 50)

    def test_post_workout_invalid_marshmallow(self):
        """Test POST /workouts returns 400 on schema validation failure."""
        payload = {
            "date": "not-a-date",
            "duration_minutes": 0,  # invalid range
            "notes": "Failure test"
        }
        response = self.app_client.post(
            '/workouts',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("errors", data)
        self.assertIn("date", data["errors"])
        self.assertIn("duration_minutes", data["errors"])

    def test_delete_workout(self):
        """Test DELETE /workouts/<id> and cascade deletion of link table records."""
        with app.app_context():
            we = WorkoutExercise(
                workout_id=self.w1_id,
                exercise_id=self.ex1_id,
                reps=10,
                sets=3,
                duration_seconds=30
            )
            db.session.add(we)
            db.session.commit()
            we_id = we.id

        # Delete workout
        response = self.app_client.delete(f'/workouts/{self.w1_id}')
        self.assertEqual(response.status_code, 200)

        # Verify workout and associated workout exercise are both deleted
        with app.app_context():
            self.assertIsNone(Workout.query.get(self.w1_id))
            self.assertIsNone(WorkoutExercise.query.get(we_id))

    def test_get_exercises(self):
        """Test GET /exercises lists all exercises."""
        response = self.app_client.get('/exercises')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    def test_get_exercise_by_id_with_details(self):
        """Test GET /exercises/<id> returns exercise with associated workouts."""
        with app.app_context():
            we = WorkoutExercise(
                workout_id=self.w1_id,
                exercise_id=self.ex1_id,
                reps=10,
                sets=3,
                duration_seconds=30
            )
            db.session.add(we)
            db.session.commit()

        response = self.app_client.get(f'/exercises/{self.ex1_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], self.ex1_id)
        self.assertEqual(len(data['workout_exercises']), 1)
        self.assertEqual(data['workout_exercises'][0]['workout']['notes'], "Morning routine")

    def test_post_exercise_valid(self):
        """Test POST /exercises creates a new exercise."""
        payload = {
            "name": "Pullups",
            "category": "Strength",
            "equipment_needed": True
        }
        response = self.app_client.post(
            '/exercises',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Pullups")

    def test_post_exercise_duplicate_name(self):
        """Test POST /exercises returns 400 for duplicate name."""
        payload = {
            "name": "Pushups", # already exists in setup
            "category": "Strength",
            "equipment_needed": False
        }
        response = self.app_client.post(
            '/exercises',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("errors", data)

    def test_add_exercise_to_workout(self):
        """Test POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises."""
        payload = {
            "reps": 15,
            "sets": 3,
            "duration_seconds": 120
        }
        response = self.app_client.post(
            f'/workouts/{self.w1_id}/exercises/{self.ex2_id}/workout_exercises',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['workout_id'], self.w1_id)
        self.assertEqual(data['exercise_id'], self.ex2_id)
        self.assertEqual(data['reps'], 15)
        self.assertEqual(data['sets'], 3)
        self.assertEqual(data['duration_seconds'], 120)
        self.assertEqual(data['exercise']['name'], "Running")


if __name__ == '__main__':
    unittest.main()
