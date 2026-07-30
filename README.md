# Workout Tracker API

## Project Description
A Flask + SQLAlchemy backend for tracking workouts and reusable exercises for personal trainers. The API supports creating, listing, and deleting workouts and exercises, along with adding an exercise to a workout with reps, sets, and duration data.

## Installation
1. Create and activate a Python environment.
2. Install dependencies with:
   ```bash
   pip install Flask==3.1.3 Flask-Migrate==4.1.0 flask-sqlalchemy==3.1.1 Werkzeug==3.1.0 marshmallow==3.20.1
   ```
3. Initialize and apply the database:
   ```bash
   flask db init
   flask db migrate -m "Initial workout app schema"
   flask db upgrade head
   ```
4. Seed the database:
   ```bash
   python seed.py
   ```

## Run Instructions
Start the development server:
```bash
flask run
```
The app runs on port 5000 by default.

## API Endpoints
- GET /workouts — list all workouts
- GET /workouts/<id> — show a single workout and its associated exercises
- POST /workouts — create a workout
- DELETE /workouts/<id> — delete a workout
- GET /exercises — list all exercises
- GET /exercises/<id> — show an exercise and its associated workouts
- POST /exercises — create an exercise
- DELETE /exercises/<id> — delete an exercise
- POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises — add an exercise to a workout with reps, sets, and duration
