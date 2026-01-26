# from .pattern_validator import validate_exam_pattern

def process_exam_pattern(exam_pattern):
    #  validate_exam_pattern(exam_pattern)

    generation_plan = []
    for q in exam_pattern.questions:
        generation_plan.append({
            "question_no": q.question_no,
            "part": q.part,
            "marks": q.marks,
            "module": q.module,
            "blooms_level": q.blooms_level
        })

    return generation_plan
