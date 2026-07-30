from marshmallow import Schema, fields, validate

class SimpleExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=3, error="Exercise name must be at least 3 characters long.")
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['Cardio', 'Strength', 'Flexibility', 'Balance', 'Warm-up', 'Cool-down'],
            error="Category must be one of: Cardio, Strength, Flexibility, Balance, Warm-up, Cool-down"
        )
    )
    equipment_needed = fields.Bool(required=True)


class SimpleWorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(
        required=True,
        error_messages={"invalid": "Date must be in YYYY-MM-DD format."}
    )
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Workout duration must be a positive integer.")
    )
    notes = fields.Str(allow_none=True)


class SimpleWorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(
        allow_none=True,
        validate=validate.Range(min=0, error="Reps must be a non-negative integer.")
    )
    sets = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1, error="Sets must be a positive integer.")
    )
    duration_seconds = fields.Int(
        allow_none=True,
        validate=validate.Range(min=0, error="Duration seconds must be a non-negative integer.")
    )


# Detail schemas for nested structures
class WorkoutExerciseDetailSchema(SimpleWorkoutExerciseSchema):
    exercise = fields.Nested(SimpleExerciseSchema, dump_only=True)


class WorkoutExerciseForExerciseDetailSchema(SimpleWorkoutExerciseSchema):
    workout = fields.Nested(SimpleWorkoutSchema, dump_only=True)


class WorkoutDetailSchema(SimpleWorkoutSchema):
    workout_exercises = fields.Nested(WorkoutExerciseDetailSchema, many=True, dump_only=True)


class ExerciseDetailSchema(SimpleExerciseSchema):
    workout_exercises = fields.Nested(WorkoutExerciseForExerciseDetailSchema, many=True, dump_only=True)
