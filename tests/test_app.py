import unittest

from app import app
from models import Exercise, Workout, WorkoutExercise


class AppModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_app_has_required_routes(self):
        route_methods = {
            "/workouts": {"GET", "POST"},
            "/exercises": {"GET", "POST"},
            "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises": {"POST"},
        }
        for rule in app.url_map.iter_rules():
            if rule.rule in route_methods:
                route_methods[rule.rule].update(rule.methods)

        for path, methods in route_methods.items():
            with self.subTest(path=path):
                self.assertTrue(methods, f"Expected route {path} to exist")

    def test_models_exist(self):
        self.assertTrue(issubclass(Exercise, object))
        self.assertTrue(issubclass(Workout, object))
        self.assertTrue(issubclass(WorkoutExercise, object))


if __name__ == "__main__":
    unittest.main()
