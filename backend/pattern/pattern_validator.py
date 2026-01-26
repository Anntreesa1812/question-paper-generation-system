from .pattern_model import ALLOWED_BLOOM_LEVELS, ALLOWED_MODULES

def validate_exam_pattern(exam_pattern):
    errors = []

    for q in exam_pattern.questions:
        if q.marks <= 0:
            errors.append(f"Q{q.question_no}: Marks must be > 0")

        if q.blooms_level not in ALLOWED_BLOOM_LEVELS:
            errors.append(f"Q{q.question_no}: Invalid Bloom level")

        if q.module not in ALLOWED_MODULES:
            errors.append(f"Q{q.question_no}: Invalid module")

        if not q.part:
            errors.append(f"Q{q.question_no}: Part missing")

    if errors:
        raise ValueError(errors)

    return True
