# Workout Tracking Application API

A clean, robust, and highly-validated Flask & SQLAlchemy backend API designed for personal trainers to track workouts and reusable exercises. 

This application uses **Marshmallow** for professional serialization/deserialization and validation, **Flask-SQLAlchemy** for ORM management, and **Flask-Migrate** for database schema migrations.

---

## Features

- **Relational Schema**: Manages three tables (`exercises`, `workouts`, and `workout_exercises`) with complete many-to-many relationship mapping.
- **Robust Validations**: Includes multi-layered integrity protection:
  - **Database Table Constraints**: SQL CheckConstraints to enforce data ranges directly in SQLite.
  - **Model-Level Validations**: SQLAlchemy `@validates` checks ensuring logical and type validity.
  - **Schema-Level Validations**: Marshmallow fields, `validate.Length`, `validate.Range`, and `validate.OneOf` rules for pristine input request sanitization.
- **Cascading Deletes**: Deleting a Workout or Exercise automatically cascades to delete-orphan link entries in the join table.
- **Comprehensive Test Suite**: Includes 16 fully automated unit tests covering all routes and validations.

---

## Entity Relationship Diagram & Schema

### 1. Exercise (reusable entity)
- `id` (Integer, Primary Key)
- `name` (String, Unique, Not Null) — *Must be >= 3 chars.*
- `category` (String, Not Null) — *Must be: 'Cardio', 'Strength', 'Flexibility', 'Balance', 'Warm-up', or 'Cool-down'.*
- `equipment_needed` (Boolean, Not Null)

### 2. Workout
- `id` (Integer, Primary Key)
- `date` (Date, Not Null) — *YYYY-MM-DD format.*
- `duration_minutes` (Integer, Not Null) — *Must be > 0.*
- `notes` (Text, Nullable)

### 3. WorkoutExercise (Join Table with extra metrics)
- `id` (Integer, Primary Key)
- `workout_id` (ForeignKey to Workouts, Not Null)
- `exercise_id` (ForeignKey to Exercises, Not Null)
- `reps` (Integer, Nullable) — *Must be >= 0.*
- `sets` (Integer, Nullable) — *Must be > 0.*
- `duration_seconds` (Integer, Nullable) — *Must be >= 0.*

---

## Installation & Setup

Follow these steps to set up the development environment and get the API running locally:

### 1. Install Dependencies
Using Pipenv, install all packages defined in the `Pipfile`:
```bash
pipenv install
```

Alternatively, you can install the dependencies using the standard `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 2. Initialize the Database and Apply Migrations
Set the `FLASK_APP` environment variable, then run migrations to create the database schema:
```bash
export FLASK_APP=server/app.py
pipenv run flask db init        # Already initialized
pipenv run flask db migrate -m "Initial migration"
pipenv run flask db upgrade head
```

### 3. Seed the Database
Populate the SQLite database with high-quality sample data:
```bash
pipenv run python3 server/seed.py
```

### 4. Run the API Server
Start the development server:
```bash
pipenv run python3 server/app.py
```
The server will start running on `http://127.0.0.1:5555/` with debug mode enabled.

---

## Running the Tests

To run the automated test suite and verify validations, routing, and cascading behavior:
```bash
export PYTHONPATH=server
pipenv run python3 -m unittest server/test_app.py
```

---

## API Endpoints Reference

### Root
- **GET `/`**
  - Description: Welcome route with greeting message.
  - Response: `200 OK` with welcome message.

### Workouts
- **GET `/workouts`**
  - Description: Retrieve a list of all workouts.
  - Response: `200 OK` with JSON array of simple workouts.
- **GET `/workouts/<id>`**
  - Description: Retrieve a single workout with its detailed information, including all associated exercises and workout_exercise metrics (reps/sets/duration).
  - Response: `200 OK` with detailed workout JSON, or `404 Not Found`.
- **POST `/workouts`**
  - Description: Create a new workout.
  - Request Body: JSON with `date`, `duration_minutes`, and `notes` (optional).
  - Response: `201 Created` with the new workout JSON, or `400 Bad Request` if validations fail.
- **DELETE `/workouts/<id>`**
  - Description: Delete a workout. This automatically cascade-deletes any associated `workout_exercises` in the join table.
  - Response: `200 OK` with a success message, or `404 Not Found`.

### Exercises
- **GET `/exercises`**
  - Description: Retrieve a list of all reusable exercises.
  - Response: `200 OK` with JSON array of exercises.
- **GET `/exercises/<id>`**
  - Description: Retrieve a single exercise with all workouts it has been added to.
  - Response: `200 OK` with detailed exercise JSON, or `404 Not Found`.
- **POST `/exercises`**
  - Description: Create a new exercise.
  - Request Body: JSON with `name`, `category`, and `equipment_needed`.
  - Response: `201 Created` with the new exercise JSON, or `400 Bad Request` if validations fail.
- **DELETE `/exercises/<id>`**
  - Description: Delete an exercise. This automatically cascade-deletes any associated `workout_exercises` in the join table.
  - Response: `200 OK` with a success message, or `404 Not Found`.

### Join Table (Workout Exercises)
- **POST `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises`**
  - Description: Add a reusable exercise to a workout with specific reps, sets, and duration metrics.
  - Request Body: JSON with `reps` (optional), `sets` (optional), and `duration_seconds` (optional).
  - Response: `201 Created` with the newly linked `workout_exercise` detailing its specs and exercise metadata, or `400 Bad Request` if validations fail.
