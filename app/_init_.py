# server/__init__.py

# Expose key application and model instances at the package level
from .app import app
from .models import db, Exercise, Workout, WorkoutExercise
