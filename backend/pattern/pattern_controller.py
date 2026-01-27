# from .pattern_validator import validate_exam_pattern

def process_exam_pattern(exam_pattern):
    #  validate_exam_pattern(exam_pattern)

    generation_plan = []
    
    # Process each part
    for part in exam_pattern.parts:
        # Process each question in the part
        if part.questions:
            for question in part.questions:
                generation_plan.append({
                    "question_no": question.question_no,
                    "part": part.part_name,
                    "marks": question.marks,
                    "module": question.module,
                    "bloom_level": question.bloom_level,
                    "answer_type": part.answer_type,
                    "has_internal_choice": question.has_internal_choice
                })

    return generation_plan
