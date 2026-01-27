import json
import random
import os
from typing import List, Dict

def load_json_file(filepath):
    """Load JSON file safely"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_questions_from_pattern(exam_pattern, processed_data_dir):
    """
    Generate questions based on the exam pattern and available resources.
    
    Args:
        exam_pattern: ExamPattern object with exam structure
        processed_data_dir: Path to processed data directory
    
    Returns:
        Dictionary with generated questions organized by parts
    """
    
    # Load resources
    topic_mapping = load_json_file(os.path.join(processed_data_dir, "topic_chunk_mapping.json"))
    textbook_chunks = load_json_file(os.path.join(processed_data_dir, "textbook_chunks.json"))
    syllabus_topics = load_json_file(os.path.join(processed_data_dir, "syllabus_topics.json"))
    
    if not textbook_chunks or not topic_mapping:
        raise Exception("Required data files not found. Please process syllabus and textbook first.")
    
    generated_questions = {}
    
    # Process each part
    for part in exam_pattern.parts:
        part_questions = []
        
        # Generate question for each question in the part
        if part.questions:
            for question in part.questions:
                generated_q = generate_single_question(
                    question=question,
                    part=part,
                    topic_mapping=topic_mapping,
                    textbook_chunks=textbook_chunks,
                    syllabus_topics=syllabus_topics
                )
                part_questions.append(generated_q)
        
        generated_questions[part.part_name] = part_questions
    
    return generated_questions

def generate_single_question(question, part, topic_mapping, textbook_chunks, syllabus_topics):
    """
    Generate a single question using available textbook chunks and topics.
    
    Args:
        question: Question object with details
        part: Part object containing part information
        topic_mapping: Topic to chunk mapping
        textbook_chunks: All textbook chunks
        syllabus_topics: All syllabus topics
    
    Returns:
        Dictionary with generated question details
    """
    
    # Get relevant textbook content based on module
    chunk_text = get_relevant_chunks(
        module=question.module,
        topic_mapping=topic_mapping,
        textbook_chunks=textbook_chunks
    )
    
    # Create question template based on Bloom level
    question_templates = {
        "Remember": [
            "Define {}",
            "What is {}?",
            "State the meaning of {}",
            "List the main points of {}",
            "Explain briefly what is {}",
        ],
        "Understand": [
            "Explain the concept of {}",
            "Describe how {} works",
            "Illustrate with examples: {}",
            "Compare and contrast {}",
            "Summarize the key ideas of {}",
        ],
        "Apply": [
            "Apply the concept of {} to solve:",
            "How would you use {} in a practical scenario?",
            "Calculate based on the principle of {}:",
            "Demonstrate the application of {} with an example",
            "Solve the following problem using {}:",
        ],
        "Analyze": [
            "Analyze the components of {}",
            "What factors influence {}?",
            "Examine the relationship between {} and other concepts",
            "Break down the structure of {} into its parts",
            "What are the causes and effects of {}?",
        ],
        "Evaluate": [
            "Evaluate the effectiveness of {}",
            "Critically assess the merits and drawbacks of {}",
            "Judge the validity of the following statement about {}:",
            "Compare the advantages and disadvantages of {}",
            "What is your opinion on the importance of {}?",
        ],
        "Create": [
            "Design a solution using the principles of {}",
            "Propose a new approach to {}",
            "Create a model that demonstrates {}",
            "Develop a strategy for {}",
            "Invent a method to improve {}",
        ]
    }
    
    bloom_level = question.bloom_level or "Remember"
    templates = question_templates.get(bloom_level, question_templates["Remember"])
    
    # Select a random template
    template = random.choice(templates)
    
    # Get a topic from the module
    topic = get_random_topic(question.module, syllabus_topics)
    
    # Fill template with topic
    question_text = template.format(topic)
    
    # If we have chunk text, add context
    if chunk_text:
        question_text += f"\n\n[Based on: {chunk_text[:100]}...]"
    
    # Build the response
    generated_question = {
        "question_no": question.question_no,
        "marks": question.marks,
        "module": question.module,
        "bloom_level": bloom_level,
        "text": question_text,
        "has_internal_choice": question.has_internal_choice,
        "source_chunk": chunk_text[:50] if chunk_text else None
    }
    
    return generated_question

def get_relevant_chunks(module, topic_mapping, textbook_chunks):
    """Get relevant textbook chunks for a given module"""
    
    chunks_dict = {chunk["chunk_id"]: chunk["text"] for chunk in textbook_chunks}
    
    # Find chunks related to this module
    relevant_chunks = []
    
    for topic, chunks in topic_mapping.items():
        if module.lower() in topic.lower() or module.lower() in str(chunks).lower():
            if isinstance(chunks, list):
                for chunk_id in chunks:
                    if chunk_id in chunks_dict:
                        relevant_chunks.append(chunks_dict[chunk_id])
    
    if relevant_chunks:
        return random.choice(relevant_chunks)
    
    return None

def get_random_topic(module, syllabus_topics):
    """Get a random topic from the specified module"""
    
    if not syllabus_topics:
        return module
    
    module_key = module.lower()
    
    # Try exact match first
    for key, topics in syllabus_topics.items():
        if module_key in key.lower():
            if isinstance(topics, list) and topics:
                return random.choice(topics)
    
    # If no exact match, return a random topic from any module
    all_topics = []
    for topics in syllabus_topics.values():
        if isinstance(topics, list):
            all_topics.extend(topics)
    
    if all_topics:
        return random.choice(all_topics)
    
    return "Topic"
