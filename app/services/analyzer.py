import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from app.utils.normalizer import normalize_marks


DATA_PATH = Path(__file__).parent.parent.parent / "data"


def analyze_student(student_id):
    """
    Analyze student's performance metrics from all attempts.
    Returns comprehensive performance summary.
    """
    perf_file = DATA_PATH / "student_performance.json"
    
    with open(perf_file, 'r', encoding='utf-8') as f:
        students = json.load(f)
    
    student_data = next((s for s in students if s['student_id'] == student_id), None)
    if not student_data:
        return None
    
    attempts = student_data.get('attempts', [])
    if not attempts:
        return _empty_analysis(student_id)
    
    # Calculate metrics
    scores = []
    chapter_scores = defaultdict(list)
    chapter_times = defaultdict(list)
    chapter_questions = defaultdict(lambda: {'total': 0, 'attempted': 0, 'skipped': 0})
    total_duration = 0
    total_time_taken = 0
    total_questions = 0
    total_attempted = 0
    total_skipped = 0
    time_per_question_list = []
    
    for attempt in attempts:
        score = normalize_marks(attempt.get('marks', 0))
        scores.append(score)
        
        # Chapter-wise scores
        chapters = attempt.get('chapters', [])
        for chapter in chapters:
            chapter_scores[chapter].append(score)
        
        # Time metrics
        duration = attempt.get('duration_minutes', 0)
        time_taken = attempt.get('time_taken_minutes', 0)
        total_duration += duration
        total_time_taken += time_taken
        
        # Question metrics
        attempted = attempt.get('attempted', 0)
        skipped = attempt.get('skipped', 0)
        total_q = attempt.get('total_questions', 0)
        total_questions += total_q
        total_attempted += attempted
        total_skipped += skipped
        
        avg_time = attempt.get('avg_time_per_question_seconds', 0)
        if avg_time > 0:
            time_per_question_list.append(avg_time)
        
        # Track per-chapter metrics
        for chapter in chapters:
            chapter_times[chapter].append(avg_time)
            chapter_questions[chapter]['total'] += total_q
            chapter_questions[chapter]['attempted'] += attempted
            chapter_questions[chapter]['skipped'] += skipped
    
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Calculate chapter stats
    chapter_avgs = {}
    for chapter, scores_list in chapter_scores.items():
        avg = sum(scores_list) / len(scores_list) if scores_list else 0
        chapter_avgs[chapter] = avg
    
    weak_chapters = [ch for ch, avg in chapter_avgs.items() if avg < 60]
    strong_chapters = [ch for ch, avg in chapter_avgs.items() if avg > 75]
    
    # Completion rate
    completion_rate = (total_attempted / total_questions * 100) if total_questions > 0 else 0
    skipped_rate = (total_skipped / total_questions * 100) if total_questions > 0 else 0
    
    # Average time per question
    avg_time_per_question = sum(time_per_question_list) / len(time_per_question_list) if time_per_question_list else 0
    
    # Trend (improving, declining, stable)
    trend = _calculate_trend(scores[-5:] if len(scores) >= 5 else scores)
    
    # Build chapter priority vector (personalized weakness profile)
    chapter_priority_vector = {}
    
    for chapter in chapter_avgs:
        chapter_avg_score = chapter_avgs[chapter]
        chapter_avg_time = (sum(chapter_times[chapter]) / len(chapter_times[chapter])) if chapter_times[chapter] else 0
        
        # Completion metrics for this chapter
        total_for_ch = chapter_questions[chapter]['total']
        attempted_for_ch = chapter_questions[chapter]['attempted']
        skipped_for_ch = chapter_questions[chapter]['skipped']
        incomplete_for_ch = total_for_ch - attempted_for_ch
        
        skipped_pct = (skipped_for_ch / total_for_ch * 100) if total_for_ch > 0 else 0
        incomplete_pct = (incomplete_for_ch / total_for_ch * 100) if total_for_ch > 0 else 0
        
        trend_penalty = 10 if trend == 'declining' else 0
        
        # Priority score: higher = more need for improvement
        priority = (
            (100 - chapter_avg_score) * 0.45 +
            (min(chapter_avg_time, 180) / 180) * 100 * 0.2 +
            skipped_pct * 0.15 +
            incomplete_pct * 0.1 +
            trend_penalty * 0.1
        )
        
        chapter_priority_vector[chapter] = round(priority, 2)
    
    # Sort by priority (highest first)
    sorted_chapters = sorted(chapter_priority_vector.items(), key=lambda x: x[1], reverse=True)
    top_priority_chapter = sorted_chapters[0][0] if sorted_chapters else None
    second_priority_chapter = sorted_chapters[1][0] if len(sorted_chapters) > 1 else None
    focus_chapter = top_priority_chapter or (weak_chapters[0] if weak_chapters else None)
    
    return {
        'student_id': student_id,
        'name': student_data.get('name', ''),
        'average_score': round(avg_score, 2),
        'weak_chapters': weak_chapters,
        'strong_chapters': strong_chapters,
        'chapter_averages': {ch: round(avg, 2) for ch, avg in chapter_avgs.items()},
        'chapter_priority_vector': chapter_priority_vector,
        'top_priority_chapter': top_priority_chapter,
        'second_priority_chapter': second_priority_chapter,
        'completion_rate': round(completion_rate, 2),
        'skipped_rate': round(skipped_rate, 2),
        'avg_time_per_question_seconds': round(avg_time_per_question, 2),
        'trend': trend,
        'focus_chapter': focus_chapter,
        'total_attempts': len(attempts),
        'recent_scores': [round(s, 2) for s in scores[-3:]],
    }


def _calculate_trend(recent_scores):
    """Determine trend from recent scores."""
    if len(recent_scores) < 2:
        return 'stable'
    
    # Compare last score to average of all recent scores
    last_score = recent_scores[-1]
    avg_prev = sum(recent_scores[:-1]) / len(recent_scores[:-1]) if len(recent_scores) > 1 else 0
    
    diff = last_score - avg_prev
    
    if diff > 5:
        return 'improving'
    elif diff < -5:
        return 'declining'
    else:
        return 'stable'


def _empty_analysis(student_id):
    """Return empty analysis for student with no attempts."""
    return {
        'student_id': student_id,
        'name': '',
        'average_score': 0,
        'weak_chapters': [],
        'strong_chapters': [],
        'chapter_averages': {},
        'chapter_priority_vector': {},
        'top_priority_chapter': None,
        'second_priority_chapter': None,
        'completion_rate': 0,
        'skipped_rate': 0,
        'avg_time_per_question_seconds': 0,
        'trend': 'stable',
        'focus_chapter': None,
        'total_attempts': 0,
        'recent_scores': [],
    }
