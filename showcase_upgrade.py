#!/usr/bin/env python3
"""Detailed showcase of upgraded priority-vector recommender."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.analyzer import analyze_student
from app.services.recommender import StudentRecommender


def show_recommendation(student_id):
    """Display detailed recommendation with priority analysis."""
    print(f"\n{'='*70}")
    print(f"PRIORITY-VECTOR RECOMMENDATION FOR {student_id}")
    print('='*70)
    
    # Analyze first
    analysis = analyze_student(student_id)
    if not analysis:
        print(f"❌ Student {student_id} not found")
        return
    
    print(f"\n📊 STUDENT PROFILE:")
    print(f"  Name: {analysis['name']}")
    print(f"  Average Score: {analysis['average_score']}%")
    print(f"  Completion Rate: {analysis['completion_rate']}%")
    print(f"  Avg Time/Question: {analysis['avg_time_per_question_seconds']}s")
    print(f"  Trend: {analysis['trend'].upper()}")
    
    print(f"\n📈 CHAPTER PRIORITY VECTOR (ranked by weakness):")
    priority_vector = analysis['chapter_priority_vector']
    sorted_chapters = sorted(priority_vector.items(), key=lambda x: x[1], reverse=True)
    
    for rank, (chapter, priority_score) in enumerate(sorted_chapters, 1):
        chapter_avg = analysis['chapter_averages'].get(chapter, 0)
        stars = "⭐" * min(int(priority_score / 20), 5)
        print(f"  {rank}. {chapter:<25s} Priority: {priority_score:6.2f}  "
              f"(Score: {chapter_avg:5.1f}%)  {stars}")
    
    print(f"\n🎯 TOP PRIORITY: {analysis['top_priority_chapter']}")
    if analysis['second_priority_chapter']:
        print(f"   SECONDARY: {analysis['second_priority_chapter']}")
    
    # Generate recommendations
    recommender = StudentRecommender()
    rec = recommender.generate_recommendation(student_id)
    
    if rec:
        print(f"\n📚 PERSONALIZED LEARNING PATH ({len(rec['steps'])} steps):")
        for step in rec['steps']:
            step_num = step['step']
            dost_type = step['dost_type'].upper()
            chapter = step['target_chapter']
            reasoning = step['reasoning']
            print(f"\n  Step {step_num}: {dost_type}")
            print(f"    Chapter: {chapter}")
            print(f"    Reasoning: {reasoning}")
            if step['question_ids']:
                print(f"    Questions: {', '.join(step['question_ids'])}")
    else:
        print("❌ Failed to generate recommendation")


if __name__ == '__main__':
    # Show examples for first two students
    show_recommendation("STU_001")
    
    # If there's a second student, show that too
    print("\n" + "="*70)
    print("✅ Upgrade complete! Recommender now uses:")
    print("   • Chapter-level priority scoring")
    print("   • Personalized weakness vectors")
    print("   • Intelligent DOST sequencing")
    print("   • Focused recommendations per top priority chapter")
    print("="*70)
