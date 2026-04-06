#!/usr/bin/env python3
"""Quick test script to verify service layer logic."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.normalizer import normalize_marks, normalize_question_id
from app.services.analyzer import analyze_student
from app.services.question_selector import select_questions
from app.services.recommender import StudentRecommender


def test_normalizer():
    """Test mark normalization."""
    print("Testing normalizer...")
    
    test_cases = [
        ("68/100", lambda x: 65 <= x <= 70),
        ("+52 -12", lambda x: x == 40),
        ("34/75 (45.3%)", lambda x: 45 <= x <= 46),
        (72, lambda x: x == 72),
        ("28", lambda x: x == 28),
    ]
    
    for mark, validator in test_cases:
        result = normalize_marks(mark)
        assert validator(result), f"Failed for {mark}: got {result}"
        print(f"  ✓ normalize_marks({mark!r}) = {result}")
    
    # Test question ID
    oid_dict = {"$oid": "d3b6e9e8325916a427bc1985"}
    assert normalize_question_id(oid_dict) == "d3b6e9e8325916a427bc1985"
    print(f"  ✓ normalize_question_id() handles $oid format")
    
    assert normalize_question_id("Q_MAT_0001") == "Q_MAT_0001"
    print(f"  ✓ normalize_question_id() handles flat string")


def test_analyzer():
    """Test student analyzer."""
    print("\nTesting analyzer...")
    
    # Analyze first student
    analysis = analyze_student("STU_001")
    
    if analysis:
        print(f"  ✓ Analyzed student {analysis['student_id']}: {analysis['name']}")
        print(f"    - Average score: {analysis['average_score']}")
        print(f"    - Weak chapters: {analysis['weak_chapters']}")
        print(f"    - Strong chapters: {analysis['strong_chapters']}")
        print(f"    - Completion rate: {analysis['completion_rate']}%")
        print(f"    - Trend: {analysis['trend']}")
        print(f"    - Focus chapter: {analysis['focus_chapter']}")
    else:
        print(f"  ✗ Failed to analyze student")


def test_question_selector():
    """Test question selector."""
    print("\nTesting question selector...")
    
    weak_chapters = ["Kinematics", "Thermodynamics"]
    qids = select_questions(weak_chapters, limit=5)
    
    print(f"  ✓ Selected {len(qids)} questions for weak chapters")
    if qids:
        for qid in qids:
            print(f"    - {qid}")


def test_recommender():
    """Test recommendation generator."""
    print("\nTesting recommender...")
    
    recommender = StudentRecommender()
    rec = recommender.generate_recommendation("STU_001")
    
    if rec:
        print(f"  ✓ Generated recommendation for {rec['student_id']}")
        print(f"    - Summary:")
        for key, val in rec['summary'].items():
            print(f"      {key}: {val}")
        print(f"    - Steps: {len(rec['steps'])}")
        for step in rec['steps']:
            print(f"      Step {step['step']}: {step['dost_type']} ({step['target_chapter']})")
    else:
        print(f"  ✗ Failed to generate recommendation")


if __name__ == '__main__':
    try:
        test_normalizer()
        test_analyzer()
        test_question_selector()
        test_recommender()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
