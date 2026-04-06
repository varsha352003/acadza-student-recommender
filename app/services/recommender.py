from app.services.analyzer import analyze_student
from app.services.question_selector import select_questions


class StudentRecommender:
    """Generate personalized learning recommendations based on student performance."""
    
    def generate_recommendation(self, student_id):
        """
        Generate personalized DOST recommendations using chapter priority vector.
        """
        analysis = analyze_student(student_id)
        
        if not analysis:
            return None
        
        steps = []
        step_num = 1
        
        avg_score = analysis['average_score']
        avg_time = analysis['avg_time_per_question_seconds']
        completion_rate = analysis['completion_rate']
        trend = analysis['trend']
        focus_chapter = analysis['top_priority_chapter'] or analysis['focus_chapter'] or 'General'
        second_chapter = analysis['second_priority_chapter']
        priority_vector = analysis['chapter_priority_vector']
        
        # Get chapter-specific score (from priority-ranked chapter)
        chapter_avgs = analysis['chapter_averages']
        focus_chapter_score = chapter_avgs.get(focus_chapter, avg_score)
        
        # Revision first if declining and low score
        if trend == 'declining' and avg_score < 60:
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='revision',
                target_chapter=focus_chapter,
                parameters={'alloted_days': 2, 'strategy': 1, 'daily_time_minutes': 45},
                question_ids=[],
                reasoning='Performance is declining on weak chapter; stabilize before practice',
                student_message='Let\'s do structured revision to solidify weak concept.'
            ))
            step_num += 1
        
        # Foundation path: focus chapter avg < 55
        if focus_chapter_score < 55:
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='formula',
                target_chapter=focus_chapter,
                parameters={},
                question_ids=[],
                reasoning=f'Chapter average is {focus_chapter_score:.1f}%; foundation rebuild needed',
                student_message=f'Let\'s start with key formulas in {focus_chapter}.'
            ))
            step_num += 1
            
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='concept',
                target_chapter=focus_chapter,
                parameters={},
                question_ids=[],
                reasoning='Build conceptual foundation for weak chapter',
                student_message='Now let\'s master the core concepts.'
            ))
            step_num += 1
            
            qids = select_questions([focus_chapter], limit=5)
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='practiceAssignment',
                target_chapter=focus_chapter,
                parameters={'difficulty': 'easy', 'type_split': {'scq': 12, 'mcq': 3}},
                question_ids=qids,
                reasoning='Apply concepts with targeted easy problems',
                student_message='Practice with easy problems to build confidence.'
            ))
            step_num += 1
        
        # Speed issues: avg time > 120 seconds
        if avg_time > 120:
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='clickingPower',
                target_chapter=focus_chapter,
                parameters={'total_questions': 10},
                question_ids=[],
                reasoning=f'Avg time {avg_time:.0f}s per question; need speed building',
                student_message='Quick drills to improve your reaction time.'
            ))
            step_num += 1
            
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='speedRace',
                target_chapter=focus_chapter,
                parameters={'rank': 100, 'opponent_type': 'bot'},
                question_ids=[],
                reasoning='Competitive speed practice under pressure',
                student_message='Race against the bot to sharpen your speed.'
            ))
            step_num += 1
        
        # Low completion: completion_rate < 70
        if completion_rate < 70:
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='practiceTest',
                target_chapter=focus_chapter,
                parameters={'difficulty': 'easy', 'duration_minutes': 30, 'paperPattern': 'Mains'},
                question_ids=[],
                reasoning=f'Completion rate {completion_rate:.1f}%; build attempt confidence',
                student_message='Short test to boost your completion rate.'
            ))
            step_num += 1
        
        # Intermediate practice for medium performers
        if 50 <= focus_chapter_score < 75:
            qids = select_questions([focus_chapter], limit=5)
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='practiceAssignment',
                target_chapter=focus_chapter,
                parameters={'difficulty': 'medium', 'type_split': {'scq': 15, 'mcq': 5}},
                question_ids=qids,
                reasoning='Medium-level practice to bridge understanding gap',
                student_message='Practice medium problems to strengthen your grip.'
            ))
            step_num += 1
        
        # High performer path: avg_score > 75
        if avg_score > 75:
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='practiceTest',
                target_chapter=focus_chapter,
                parameters={'difficulty': 'hard', 'duration_minutes': 60, 'paperPattern': 'Mains'},
                question_ids=[],
                reasoning='Challenge yourself with advanced full-length test',
                student_message='Full-length advanced test to push your limits.'
            ))
            step_num += 1
            
            steps.append(self._create_step(
                step_num=step_num,
                dost_type='speedRace',
                target_chapter=focus_chapter,
                parameters={'rank': 50, 'opponent_type': 'bot'},
                question_ids=[],
                reasoning='Advanced speed race for competitive edge',
                student_message='Advanced speed race — compete at the top level.'
            ))
            step_num += 1
        
        recommendation = {
            'student_id': student_id,
            'summary': {
                'average_score': analysis['average_score'],
                'focus_area': focus_chapter,
                'priority_vector': priority_vector,
                'completion_rate': analysis['completion_rate'],
                'trend': trend,
            },
            'steps': steps,
        }
        
        return recommendation
    
    def _create_step(self, step_num, dost_type, target_chapter, parameters, 
                     question_ids, reasoning, student_message):
        """Helper to create a recommendation step."""
        return {
            'step': step_num,
            'dost_type': dost_type,
            'target_chapter': target_chapter,
            'parameters': parameters,
            'question_ids': question_ids,
            'reasoning': reasoning,
            'student_message': student_message,
        }
