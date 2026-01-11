from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

@dataclass
class ScheduleData:
    next_review: datetime
    interval: int
    repetitions: int
    easiness_factor: float
    last_reviewed: datetime

class SpacedRepetitionEngine:
    """
    Standard SM-2 Spaced Repetition Algorithm.
    """
    
    def create_initial_schedule(self) -> ScheduleData:
        now = datetime.utcnow()
        return ScheduleData(
            next_review=now,
            interval=0,
            repetitions=0,
            easiness_factor=2.5,
            last_reviewed=now
        )
    
    def calculate_next_review(self, current_interval: int, current_repetitions: int, current_easiness: float, quality: int) -> ScheduleData:
        if quality >= 3:
            if current_repetitions == 0:
                interval = 1
            elif current_repetitions == 1:
                interval = 6
            else:
                interval = round(current_interval * current_easiness)
            
            repetitions = current_repetitions + 1
            easiness = current_easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:
            interval = 1
            repetitions = 0
            easiness = current_easiness
        
        easiness = max(1.3, easiness)
        now = datetime.utcnow()
        
        return ScheduleData(
            next_review=now + timedelta(days=interval),
            interval=interval,
            repetitions=repetitions,
            easiness_factor=easiness,
            last_reviewed=now
        )

    def calculate_quality_from_quiz_performance(
        self, 
        was_correct: bool, 
        time_taken_seconds: Optional[int] = None,
        avg_time_seconds: int = 10
    ) -> int:
        if not was_correct:
            return 1  # Yanlış
        
        if not time_taken_seconds:
            return 4
            
        if time_taken_seconds < avg_time_seconds * 0.5:
            return 5  # Mükemmel
        elif time_taken_seconds < avg_time_seconds:
            return 4  # İyi
        elif time_taken_seconds < avg_time_seconds * 1.5:
            return 3  # Orta
        else:
            return 3  # Zorlandı
