from pydantic import BaseModel
from typing import List, Optional

class SubQuestionPattern(BaseModel):
    label: str              # a, b, c
    marks: int

class QuestionPattern(BaseModel):
    question_no: int
    sub_questions: Optional[List[SubQuestionPattern]] = None
    has_internal_choice: bool = False

class PartPattern(BaseModel):
    part_name: str                 # PART A, PART B
    answer_type: str               # ALL / ANY
    marks_per_question: int
    total_questions: int
    questions_to_answer: Optional[int] = None
    bloom_levels: List[str]
    questions: Optional[List[QuestionPattern]] = None

class ExamPattern(BaseModel):
    exam_name: str
    parts: List[PartPattern]
