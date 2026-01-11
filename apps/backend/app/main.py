import logging
import json
import random
from uuid import UUID
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.auth import get_current_user_id, get_or_create_user
from app.db.session import get_session
from app.models.learning_goal import LearningGoal
from app.models.quiz import QuizQuestion, QuizSession
from app.models.user import User
from app.models.vocabulary import VocabularyWord
from app.models.review_schedule import ReviewSchedule
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalRead
from app.schemas.quiz import (
    QuizQuestionList,
    QuizQuestionRead,
    QuizSessionCreate,
    QuizSessionRead,
)
from app.schemas.vocabulary import VocabularyWordList, VocabularyWordRead

# New core logic
from app.core.spaced_repetition import SpacedRepetitionEngine





logger = logging.getLogger(__name__)


from contextlib import asynccontextmanager
from app.services.ai_generator import ai_generator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load AI Model on startup
    try:
        ai_generator.load_model()
    except Exception as e:
        logger.error(f"Startup AI load failed: {e}")
    yield
    # Cleanup if needed

app = FastAPI(title="Lexavia API", version="0.1.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Relaxed for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sr_engine = SpacedRepetitionEngine()

@app.get("/api/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "mode": "ai_enhanced_flan_t5"}

# ... (Previous endpoints) ...

async def _generate_single_question(session: AsyncSession, word: str, translation: str, level: str, category: str) -> dict:
    """
    Generates a single smart question using AI Generator.
    """
    # 0. Ensure translation
    if not translation:
        q_word = await session.execute(
            select(VocabularyWord).where(VocabularyWord.word == word)
        )
        db_word = q_word.scalar_one_or_none()
        if db_word:
            translation = db_word.translation
            
    # 1. Fetch Context from DB (ESL/Curated Sentences)
    query_context = text("""
        SELECT s.english_text
        FROM vocabulary_words v
        JOIN word_sentences ws ON v.id = ws.word_id
        JOIN sentences s ON ws.sentence_id = s.id
        WHERE v.word = :word
        ORDER BY RANDOM()
        LIMIT 1
    """)
    result = await session.execute(query_context, {"word": word})
    row = result.first()
    
    context_sentence = row[0] if row else f"The word is {word}."

    # 2. Generate Question using AI
    ai_result = ai_generator.generate_question(word, context_sentence, level)
    
    question_text = ai_result["question_text"]
    explanation = ai_result["explanation"]

    # 3. Distractors (Still need database for this)
    query_dist = text("SELECT word FROM vocabulary_words WHERE word != :word ORDER BY RANDOM() LIMIT 3")
    res_dist = await session.execute(query_dist, {"word": word})
    dist_rows = res_dist.all()
    
    options = [word] + [r[0] for r in dist_rows]
    while len(options) < 4:
        options.append("other")
    random.shuffle(options)

    return {
        "question_text": question_text,
        "question_type": "multiple_choice",
        "correct_answer": word,
        "options": json.dumps(options),
        "level": level,
        "category": category,
        "explanation": explanation
    }

# --- ONBOARDING & GOALS ---

@app.post("/api/onboarding", response_model=LearningGoalRead, tags=["onboarding"])
async def create_learning_goal(
    payload: LearningGoalCreate,
    user: User = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
) -> LearningGoalRead:
    try:
        goal = LearningGoal(
            user_id=user.id,
            target_language=payload.target_language,
            level=payload.level,
            daily_minutes=payload.daily_minutes,
            goal_type=payload.goal_type,
            focus_topics=payload.focus_topics,
        )
        session.add(goal)
        await session.commit()
        await session.refresh(goal)
        return LearningGoalRead.model_validate(goal.__dict__)
    except Exception as e:
        logger.error(f"Error creating learning goal: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-goals/latest", response_model=LearningGoalRead, tags=["learning-goals"])
async def get_latest_learning_goal(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    try:
        result = await session.execute(
            select(LearningGoal).where(LearningGoal.user_id == str(user_id)).order_by(LearningGoal.created_at.desc()).limit(1)
        )
        goal = result.scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=404, detail="No goal found")
            
        # Calculate Progress
        total_correct_res = await session.execute(
            select(func.sum(QuizSession.correct_answers)).where(QuizSession.user_id == str(user_id))
        )
        current_xp = total_correct_res.scalar() or 0
        
        # Thresholds (Keep synchronized with create_quiz_session)
        # XP = Total Correct Answers
        LEVEL_THRESHOLDS = {
            "A1": 0, "A2": 50, "B1": 150, "B2": 300, "C1": 600, "C2": 1000
        }
        LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]
        
        next_level = None
        next_level_xp = 0
        
        current_level_idx = -1
        if goal.level in LEVEL_ORDER:
            current_level_idx = LEVEL_ORDER.index(goal.level)
            
        if current_level_idx != -1 and current_level_idx < len(LEVEL_ORDER) - 1:
            next_level = LEVEL_ORDER[current_level_idx + 1]
            next_level_xp = LEVEL_THRESHOLDS.get(next_level, 0)
        
        # Construct response
        resp_dict = goal.__dict__.copy()
        resp_dict["current_xp"] = current_xp
        resp_dict["next_level"] = next_level
        resp_dict["next_level_xp"] = next_level_xp
        
        return LearningGoalRead.model_validate(resp_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching goal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- VOCABULARY ---

@app.get("/api/vocabulary", response_model=VocabularyWordList, tags=["vocabulary"])
async def get_vocabulary(
    level: str = "A1",
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    try:
        # Use raw SQL to fetch random words with one example sentence each
        query = text("""
            SELECT v.id, v.word, v.translation, v.level, v.category,
                   (SELECT s.english_text FROM sentences s 
                    JOIN word_sentences ws ON s.id = ws.sentence_id 
                    WHERE ws.word_id = v.id LIMIT 1) as example_sentence,
                   v.created_at
            FROM vocabulary_words v
            WHERE v.level = :level
            ORDER BY RANDOM()
            LIMIT :limit
        """)
        
        result = await session.execute(query, {"level": level, "limit": limit})
        rows = result.all()
        
        vocab_list = []
        for row in rows:
            vocab_list.append(VocabularyWordRead(
                id=row.id,
                word=row.word,
                translation=row.translation,
                level=row.level,
                category=row.category,
                example_sentence=row.example_sentence,
                created_at=row.created_at
            ))
            
        return VocabularyWordList(words=vocab_list, total=len(vocab_list))
        
    except Exception as e:
        logger.error(f"Error fetching vocabulary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



# --- QUIZ QUESTIONS ---


# --- HELPER: SMART QUESTION GENERATOR ---
async def _generate_single_question(session: AsyncSession, word: str, translation: str | None, level: str, category: str) -> dict:
    """
    Generates a single smart question (Context > Translation > Definition)
    Returns a dict matching QuizQuestion schema structure.
    """
    # 0. Ensure translation
    if not translation:
        q_word = await session.execute(
            select(VocabularyWord).where(VocabularyWord.word == word)
        )
        db_word = q_word.scalar_one_or_none()
        if db_word:
            translation = db_word.translation

    # 1. Try Context (Fill-in-blank)
    query_context = text("""
        SELECT s.english_text, s.turkish_text
        FROM vocabulary_words v
        JOIN word_sentences ws ON v.id = ws.word_id
        JOIN sentences s ON ws.sentence_id = s.id
        WHERE v.word = :word
        ORDER BY RANDOM()
        LIMIT 1
    """)
    result = await session.execute(query_context, {"word": word})
    row = result.first()
    
    if not row:
        # 1.5. Fallback: Regex Search
        query_fallback = text("""
            SELECT english_text, turkish_text
            FROM sentences
            WHERE english_text ~* :pattern
            ORDER BY RANDOM()
            LIMIT 1
        """)
        # \y is postgres word boundary
        result_fallback = await session.execute(query_fallback, {"pattern": f"\\y{word}\\y"})
        row = result_fallback.first()

    question_text = ""
    explanation = ""
    
    if row:
        english_text = row[0]
        turkish_text = row[1]
        import re
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        question_text = pattern.sub("_______", english_text)
        
        if "_______" not in question_text:
             question_text = f"What is the English for '{translation}'?" if translation else f"Which word means '{turkish_text}'?"
             explanation = f"Translation: {word} = {translation}"
        else:
             explanation = f"Anlamı: {turkish_text}"
    else:
        # Fallback: Translation
        if translation:
            question_text = f"Select the correct English word for: '{translation}'"
            explanation = f"Meaning: {translation}"
        else:
            question_text = f"Select the correct definition/synonym for '{word}'"
            explanation = "Vocabulary review."

    # Distractors
    query_dist = text("SELECT word FROM vocabulary_words WHERE word != :word ORDER BY RANDOM() LIMIT 3")
    res_dist = await session.execute(query_dist, {"word": word})
    dist_rows = res_dist.all()
    
    options = [word] + [r[0] for r in dist_rows]
    while len(options) < 4:
        options.append("other")
    random.shuffle(options)

    return {
        "question_text": question_text,
        "question_type": "multiple_choice",
        "correct_answer": word,
        "options": json.dumps(options),
        "level": level,
        "category": category,
        "explanation": explanation
    }

# --- QUIZ QUESTIONS ---

@app.get("/api/quiz/questions", response_model=QuizQuestionList, tags=["quiz"])
async def get_quiz_questions(
    level: str = "A1",
    limit: int = 10,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    try:
        # 1. Smart Batch Generation
        # Strategy: 50% Due Reviews (SR), 50% Random New Words
        
        sr_limit = limit // 2
        new_limit = limit - sr_limit
        
        # A. Fetch Due Reviews
        # Note: We use raw sql here to simplify joining with vocab
        query_sr = text("""
            SELECT v.id, v.word, v.translation, v.level, v.category
            FROM review_schedules rs
            JOIN vocabulary_words v ON rs.word_id = v.id
            WHERE rs.next_review <= NOW() AND rs.user_id = :uid
            ORDER BY rs.next_review ASC
            LIMIT :lim
        """)
        res_sr = await session.execute(query_sr, {"lim": sr_limit, "uid": str(user_id)})
        sr_rows = res_sr.all()
        
        # B. Fetch Random New Words (filling the rest)
        # Exclude words already in review_schedules for this user
        query_rnd = text("""
            SELECT v.id, v.word, v.translation, v.level, v.category
            FROM vocabulary_words v
            LEFT JOIN review_schedules rs ON v.id = rs.word_id AND rs.user_id = :uid
            WHERE v.level = :level AND rs.id IS NULL
            ORDER BY RANDOM()
            LIMIT :lim
        """)
        # Adjust limit if we didn't find enough reviews
        needed_rnd = limit - len(sr_rows)
        res_rnd = await session.execute(query_rnd, {"level": level, "lim": needed_rnd, "uid": str(user_id)})
        rnd_rows = res_rnd.all()
        
        all_words = sr_rows + rnd_rows
        random.shuffle(all_words) # Mix them up
        
        q_list = []
        for i, w in enumerate(all_words):
            # Generate smart question for each
            q_data = await _generate_single_question(session, w.word, w.translation, w.level, w.category)
            
            # Map to response schema
            q_list.append(QuizQuestionRead(
                id=i + 1, # Temp ID
                word_id=w.id, # Real DB ID for SR tracking
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                correct_answer=q_data["correct_answer"],
                options=q_data["options"],
                level=q_data["level"],
                category=q_data["category"],
                explanation=q_data["explanation"],
                created_at=None
            ))
            
        return QuizQuestionList(questions=q_list, total=len(q_list))
        
    except Exception as e:
        logger.error(f"Error fetching quiz questions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/sessions", response_model=QuizSessionRead, tags=["quiz"])
async def create_quiz_session(
    payload: QuizSessionCreate,
    user: User = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        user_id = user.id
        logger.info(f"Quiz Submission Request for User ID: {user_id}")
        logger.info(f"Payload Score: {payload.score}, Questions: {payload.total_questions}")
        
        # 1. Save Session
        new_session = QuizSession(
            user_id=user_id,
            score=payload.score,
            total_questions=payload.total_questions,
            correct_answers=payload.correct_answers,
            category_breakdown=payload.category_breakdown
        )
        session.add(new_session)
        
        # 2. Process Detailed Results (Update SR)
        if payload.results:
            for res in payload.results:
                if not res.word_id:
                    continue # Skip if no ID (shouldn't happen with new logic)
                    
                # Get existing schedule
                q_sch = await session.execute(
                    select(ReviewSchedule).where(
                        ReviewSchedule.user_id == str(user_id),
                        ReviewSchedule.word_id == res.word_id
                    )
                )
                schedule = q_sch.scalar_one_or_none()
                
                # Quality: 5 = Correct + Fast, 3 = Correct + Slow, 0 = Incorrect
                # Simplified logic for now: Correct = 4, Incorrect = 1
                quality = 4 if res.is_correct else 1
                
                if not schedule:
                    # Create new schedule
                    init_data = sr_engine.create_initial_schedule()
                    schedule = ReviewSchedule(
                        user_id=str(user_id),
                        word_id=res.word_id,
                        next_review=init_data.next_review,
                        interval=init_data.interval,
                        repetitions=init_data.repetitions,
                        easiness_factor=init_data.easiness_factor,
                        last_reviewed=init_data.last_reviewed
                    )
                    session.add(schedule)
                
                # Calculate next review
                next_data = sr_engine.calculate_next_review(
                    schedule.interval, schedule.repetitions, schedule.easiness_factor, quality
                )
                
                schedule.next_review = next_data.next_review
                schedule.interval = next_data.interval
                schedule.repetitions = next_data.repetitions
                schedule.easiness_factor = next_data.easiness_factor
                schedule.last_reviewed = next_data.last_reviewed

        # 3. Level Up Logic
        achieved_level = None
        # XP Calculation: Total cumulative correct answers
        total_xp_res = await session.execute(
            select(func.sum(QuizSession.correct_answers)).where(QuizSession.user_id == str(user_id))
        )
        current_xp = total_xp_res.scalar() or 0
        
        # Define Thresholds
        LEVEL_THRESHOLDS = {
            "A1": 0,
            "A2": 50, 
            "B1": 150,
            "B2": 300,
            "C1": 600,
            "C2": 1000
        }
        
        # Get Current Goal
        goal_res = await session.execute(
            select(LearningGoal).where(LearningGoal.user_id == str(user_id)).order_by(LearningGoal.created_at.desc()).limit(1)
        )
        current_goal = goal_res.scalar_one_or_none()
        
        if current_goal:
            new_level = current_goal.level
            
            # Find highest qualified level
            for lvl, threshold in LEVEL_THRESHOLDS.items():
                if current_xp >= threshold:
                    if LEVEL_THRESHOLDS.get(lvl, 0) > LEVEL_THRESHOLDS.get(current_goal.level, 0):
                         new_level = lvl
            
            if new_level != current_goal.level:
                current_goal.level = new_level
                session.add(current_goal)
                logger.info(f"User {user_id} leveled up to {new_level}!")
                achieved_level = new_level

        await session.commit()
        await session.refresh(new_session)
        
        # Fetch the updated goal to return with progress info
        updated_goal_res = await session.execute(
            select(LearningGoal).where(LearningGoal.user_id == str(user_id)).order_by(LearningGoal.created_at.desc()).limit(1)
        )
        goal_for_response = updated_goal_res.scalar_one_or_none()

        # Recalculate progress for response
        total_xp_res_resp = await session.execute(
            select(func.sum(QuizSession.correct_answers)).where(QuizSession.user_id == str(user_id))
        )
        current_xp_resp = total_xp_res_resp.scalar() or 0
        
        next_level = None
        next_level_xp = 0
        LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]
        current_level_idx = -1
        if goal_for_response and goal_for_response.level in LEVEL_ORDER:
            current_level_idx = LEVEL_ORDER.index(goal_for_response.level)
            
        if current_level_idx != -1 and current_level_idx < len(LEVEL_ORDER) - 1:
            next_level = LEVEL_ORDER[current_level_idx + 1]
            next_level_xp = LEVEL_THRESHOLDS.get(next_level, 0)

        # Prepare response
        resp_dict = new_session.__dict__.copy()
        resp_dict["new_level"] = achieved_level
        # Note: QuizSessionRead doesn't standardly return current_xp/next_level_xp, 
        # but the frontend fetches /api/learning-goals/latest separately or we could add it.
        # For now, we just ensure level up happens.
        return QuizSessionRead.model_validate(resp_dict)
    except Exception as e:
        logger.error(f"Error saving quiz session: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- GENERATION (DB DRIVEN) ---

class QuizGenerationRequest(BaseModel):
    word: str
    level: str
    category: str = "vocabulary"
    translation: str | None = None

class QuizGenerationResponse(BaseModel):
    question_text: str
    question_type: str
    correct_answer: str
    options: str
    level: str
    category: str
    explanation: str

@app.post("/api/ml/generate-quiz", response_model=QuizGenerationResponse, tags=["content"])
async def generate_quiz_db(
    request: QuizGenerationRequest,
    session: AsyncSession = Depends(get_session)
):
    """Generates a quiz using real sentences from DB"""
    try:
        q_data = await _generate_single_question(session, request.word, request.translation, request.level, request.category)
        
        return QuizGenerationResponse(
            question_text=q_data["question_text"],
            question_type=q_data["question_type"],
            correct_answer=q_data["correct_answer"],
            options=q_data["options"],
            level=q_data["level"],
            category=q_data["category"],
            explanation=q_data["explanation"]
        )
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        # Fail safe
        return QuizGenerationResponse(
            question_text=f"Identify the word: {request.word}",
            question_type="multiple_choice",
            correct_answer=request.word,
            options=json.dumps([request.word, "blue", "red", "green"]),
            level="A1",
            category="general",
            explanation="System fallback"
        )

# --- SPACED REPETITION ---

class DueReviewItem(BaseModel):
    word_id: int
    word: str
    translation: str
    next_review: str
    interval: int
    repetitions: int

@app.get("/api/ml/due-reviews/{user_id}", response_model=list[DueReviewItem], tags=["sr"])
async def get_due_reviews(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    try:
        # Cast UUID to string for consistency if needed, but SQLAlchemy handles it.
        # Check review_schedules
        query = select(ReviewSchedule, VocabularyWord).join(
            VocabularyWord, ReviewSchedule.word_id == VocabularyWord.id
        ).where(
            ReviewSchedule.user_id == str(user_id),
            ReviewSchedule.next_review <= datetime.now(timezone.utc)
        ).order_by(ReviewSchedule.next_review).limit(50)
        
        result = await session.execute(query)
        rows = result.all()
        
        items = []
        for review, word in rows:
            items.append(DueReviewItem(
                word_id=word.id,
                word=word.word,
                translation=word.translation,
                next_review=review.next_review.isoformat(),
                interval=review.interval,
                repetitions=review.repetitions
            ))
        return items
    except Exception as e:
        logger.error(f"Due reviews error: {e}")
        return [] # Return empty list on error to prevent UI crash

class CreateReviewScheduleRequest(BaseModel):
    word_id: int
    user_id: str # UUID string

class ReviewScheduleResponse(BaseModel):
    word_id: int
    user_id: str
    next_review: str
    interval: int
    repetitions: int
    easiness_factor: float

@app.post("/api/ml/create-review-schedule", response_model=ReviewScheduleResponse, tags=["sr"])
async def create_schedule(
    request: CreateReviewScheduleRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        schedule_data = sr_engine.create_initial_schedule()
        
        # Check existing
        result = await session.execute(
            select(ReviewSchedule).where(
                ReviewSchedule.user_id == request.user_id, 
                ReviewSchedule.word_id == request.word_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return _map_schedule(existing)
            
        new_schedule = ReviewSchedule(
            user_id=request.user_id,
            word_id=request.word_id,
            next_review=schedule_data.next_review,
            interval=schedule_data.interval,
            repetitions=schedule_data.repetitions,
            easiness_factor=schedule_data.easiness_factor,
            last_reviewed=schedule_data.last_reviewed
        )
        session.add(new_schedule)
        await session.commit()
        await session.refresh(new_schedule)
        return _map_schedule(new_schedule)
    except Exception as e:
        logger.error(f"Create schedule error: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class UpdateReviewScheduleRequest(BaseModel):
    word_id: int
    user_id: str
    quality: int

@app.post("/api/ml/update-review-schedule", response_model=ReviewScheduleResponse, tags=["sr"])
async def update_schedule(
    request: UpdateReviewScheduleRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        result = await session.execute(
            select(ReviewSchedule).where(
                ReviewSchedule.user_id == request.user_id, 
                ReviewSchedule.word_id == request.word_id
            )
        )
        current = result.scalar_one_or_none()
        
        if not current:
            # Create if missing (fallback)
            schedule_data = sr_engine.create_initial_schedule()
            current = ReviewSchedule(
                user_id=request.user_id,
                word_id=request.word_id,
                next_review=schedule_data.next_review,
                interval=schedule_data.interval,
                repetitions=schedule_data.repetitions,
                easiness_factor=schedule_data.easiness_factor,
                last_reviewed=schedule_data.last_reviewed
            )
            session.add(current)
        
        # Calculate new
        new_data = sr_engine.calculate_next_review(
            current.interval, current.repetitions, current.easiness_factor, request.quality
        )
        
        current.next_review = new_data.next_review
        current.interval = new_data.interval
        current.repetitions = new_data.repetitions
        current.easiness_factor = new_data.easiness_factor
        current.last_reviewed = new_data.last_reviewed
        
        await session.commit()
        await session.refresh(current)
        return _map_schedule(current)
        
    except Exception as e:
        logger.error(f"Update schedule error: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class CalculateQualityRequest(BaseModel):
    was_correct: bool
    time_taken_seconds: int | None = None
    avg_time_seconds: int = 10

@app.post("/api/ml/calculate-quality")
async def calculate_quality(req: CalculateQualityRequest):
    q = sr_engine.calculate_quality_from_quiz_performance(
        req.was_correct, req.time_taken_seconds, req.avg_time_seconds
    )
    return {"quality": q, "description": "Calculated"}

def _map_schedule(s: ReviewSchedule) -> ReviewScheduleResponse:
    return ReviewScheduleResponse(
        word_id=s.word_id,
        user_id=s.user_id,
        next_review=s.next_review.isoformat(),
        interval=s.interval,
        repetitions=s.repetitions,
        easiness_factor=s.easiness_factor
    )


from sqlalchemy import func

# --- STATISTICS ---

class RecentQuizItem(BaseModel):
    date: str
    score: int

class StatisticsResponse(BaseModel):
    total_quizzes: int
    average_score: float
    total_correct: int
    total_questions: int
    recent_quizzes: list[RecentQuizItem]

@app.get("/api/statistics", response_model=StatisticsResponse, tags=["statistics"])
async def get_statistics(
    user: User = Depends(get_or_create_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        user_id = user.id
        logger.info(f"Statistics Request for User ID: {user_id} (Type: {type(user_id)})")
        # Aggregates
        query_agg = select(
            func.count(QuizSession.id),
            func.coalesce(func.avg(QuizSession.score), 0),
            func.coalesce(func.sum(QuizSession.correct_answers), 0),
            func.coalesce(func.sum(QuizSession.total_questions), 0)
        ).where(QuizSession.user_id == str(user_id))
        
        # Log the compiled query for debugging
        # logger.info(f"Stats Query: {query_agg.compile(compile_kwargs={'literal_binds': True})}")

        res_agg = await session.execute(query_agg)
        total_quizzes, avg_score, total_correct, total_questions = res_agg.one()
        logger.info(f"Stats Result: Quizzes={total_quizzes}, Correct={total_correct}")
        
        # Recent Quizzes (Last 10)
        query_recent = select(QuizSession).where(
            QuizSession.user_id == str(user_id)
        ).order_by(QuizSession.created_at.desc()).limit(10)
        
        res_recent = await session.execute(query_recent)
        recent_rows = res_recent.scalars().all()
        logger.info(f"Recent Quizzes Found: {len(recent_rows)}")
        
        recent_list = []
        for r in recent_rows:
            date_str = r.created_at.isoformat() if r.created_at else None
            recent_list.append(RecentQuizItem(
                date=date_str,
                score=int(r.score)
            ))
            
        return StatisticsResponse(
            total_quizzes=total_quizzes,
            average_score=float(avg_score),
            total_correct=total_correct,
            total_questions=total_questions,
            recent_quizzes=recent_list
        )
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- MOCK EXAMPLE ENDPOINT ---
class ExampleSentenceRequest(BaseModel):
    word: str
    level: str

@app.post("/api/ml/generate-example")
async def generate_example(req: ExampleSentenceRequest, session: AsyncSession = Depends(get_session)):
    # Simple db logic
    q = text("SELECT english_text FROM sentences JOIN word_sentences ON sentences.id = word_sentences.sentence_id JOIN vocabulary_words ON word_sentences.word_id = vocabulary_words.id WHERE vocabulary_words.word = :word LIMIT 1")
    res = await session.execute(q, {"word": req.word})
    row = res.first()
    sentence = row[0] if row else f"Example for {req.word}"
    
    return {
        "word": req.word,
        "level": req.level,
        "example_sentence": sentence
    }



