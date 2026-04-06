import json
from pathlib import Path
from collections import defaultdict

from app.utils.normalizer import normalize_question_id


DATA_PATH = Path(__file__).parent.parent.parent / "data"


def select_questions(weak_chapters, question_type=None, limit=5):
    """
    Select questions from question bank for weak chapters.
    
    Filters by:
    - weak chapters (topics)
    - preferred difficulty 1-3
    - removes duplicates, null difficulty, missing answers
    """
    qbank_file = DATA_PATH / "question_bank.json"
    
    with open(qbank_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Clean records
    cleaned = []
    seen_ids = set()
    
    for q in questions:
        qid = q.get('qid')
        difficulty = q.get('difficulty')
        
        # Skip invalid records
        if not qid or qid in seen_ids:
            continue
        
        if difficulty is None:
            continue
        
        # Check for answer in appropriate format
        q_type = q.get('questionType', '').lower()
        has_answer = False
        
        if q_type == 'scq' and 'scq' in q and 'answer' in q['scq']:
            has_answer = True
        elif q_type in ['mcq', 'integer'] and q_type in q and 'answer' in q[q_type]:
            has_answer = True
        
        if not has_answer:
            continue
        
        cleaned.append(q)
        seen_ids.add(qid)
    
    # Filter by weak chapters / topics
    filtered = []
    for q in cleaned:
        topic = q.get('topic', '').lower()
        for chapter in weak_chapters:
            if chapter.lower() in topic or topic in chapter.lower():
                filtered.append(q)
                break
    
    # Sort by difficulty (prefer 1-3, then by question type if specified)
    def sort_key(q):
        diff = q.get('difficulty', 5)
        # Prefer difficulty 1-3 over others
        if diff <= 3:
            priority = 0
        else:
            priority = 1
        return (priority, diff)
    
    filtered.sort(key=sort_key)
    
    # Extract question IDs and limit
    selected_qids = [q.get('qid') for q in filtered[:limit]]
    
    return selected_qids
