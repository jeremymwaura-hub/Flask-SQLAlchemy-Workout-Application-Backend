from marshmallow import Schema, fields, validate, ValidationError


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    category = fields.Str(required=True, validate=validate.Length(min=1))
    equipment_needed = fields.Bool(load_default=False)
    workout_exercises = fields.List(
        fields.Nested("WorkoutExerciseSchema", exclude=("exercise",), dump_only=True),
        dump_only=True,
    )
    workouts = fields.List(
        fields.Nested("WorkoutSchema", only=("id", "date", "duration_minutes"), dump_only=True),
        dump_only=True,
    )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(load_default="")
    workout_exercises = fields.List(
        fields.Nested("WorkoutExerciseSchema", exclude=("workout",), dump_only=True),
        dump_only=True,
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(load_default=None)
    exercise_id = fields.Int(load_default=None)
    reps = fields.Int(required=True, validate=validate.Range(min=1))
    sets = fields.Int(required=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(required=True, validate=validate.Range(min=1))
    exercise = fields.Nested(
        ExerciseSchema,
        only=("id", "name", "category", "equipment_needed"),
        dump_only=True,
    )
    workout = fields.Nested(
        WorkoutSchema,
        only=("id", "date", "duration_minutes"),
        dump_only=True,
    )
