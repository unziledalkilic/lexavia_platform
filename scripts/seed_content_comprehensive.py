"""
Kapsamlı içerik seed scripti - Tüm seviyeler için.
Kullanım: python -m scripts.seed_content_comprehensive
"""
import asyncio
import json
import sys
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select

from app.core.config import settings
from app.models.quiz import QuizQuestion
from app.models.vocabulary import VocabularyWord
from app.models.learning_goal import Base


# TÜM SEVİYELER İÇİN KELİMELER
VOCABULARY_WORDS = [
    # A1 seviyesi (20 kelime)
    {"word": "hello", "translation": "merhaba", "level": "A1", "category": "greeting", "example_sentence": "Hello, how are you?"},
    {"word": "goodbye", "translation": "hoşça kal", "level": "A1", "category": "greeting", "example_sentence": "Goodbye, see you tomorrow."},
    {"word": "please", "translation": "lütfen", "level": "A1", "category": "common", "example_sentence": "Please help me."},
    {"word": "thank you", "translation": "teşekkür ederim", "level": "A1", "category": "greeting", "example_sentence": "Thank you for your help."},
    {"word": "yes", "translation": "evet", "level": "A1", "category": "common", "example_sentence": "Yes, I understand."},
    {"word": "no", "translation": "hayır", "level": "A1", "category": "common", "example_sentence": "No, I don't know."},
    {"word": "water", "translation": "su", "level": "A1", "category": "noun", "example_sentence": "I need a glass of water."},
    {"word": "food", "translation": "yiyecek", "level": "A1", "category": "noun", "example_sentence": "I like Italian food."},
    {"word": "house", "translation": "ev", "level": "A1", "category": "noun", "example_sentence": "This is my house."},
    {"word": "friend", "translation": "arkadaş", "level": "A1", "category": "noun", "example_sentence": "She is my best friend."},
    {"word": "book", "translation": "kitap", "level": "A1", "category": "noun", "example_sentence": "I am reading a book."},
    {"word": "school", "translation": "okul", "level": "A1", "category": "noun", "example_sentence": "I go to school every day."},
    {"word": "work", "translation": "çalışmak", "level": "A1", "category": "verb", "example_sentence": "I work in an office."},
    {"word": "study", "translation": "çalışmak", "level": "A1", "category": "verb", "example_sentence": "I study English every day."},
    {"word": "learn", "translation": "öğrenmek", "level": "A1", "category": "verb", "example_sentence": "I want to learn Spanish."},
    {"word": "big", "translation": "büyük", "level": "A1", "category": "adjective", "example_sentence": "This is a big house."},
    {"word": "small", "translation": "küçük", "level": "A1", "category": "adjective", "example_sentence": "I have a small car."},
    {"word": "good", "translation": "iyi", "level": "A1", "category": "adjective", "example_sentence": "This is a good book."},
    {"word": "bad", "translation": "kötü", "level": "A1", "category": "adjective", "example_sentence": "The weather is bad today."},
    {"word": "happy", "translation": "mutlu", "level": "A1", "category": "adjective", "example_sentence": "I am happy today."},
    
    # A2 seviyesi (20 kelime)
    {"word": "understand", "translation": "anlamak", "level": "A2", "category": "verb", "example_sentence": "I understand English well."},
    {"word": "speak", "translation": "konuşmak", "level": "A2", "category": "verb", "example_sentence": "Can you speak English?"},
    {"word": "write", "translation": "yazmak", "level": "A2", "category": "verb", "example_sentence": "I write letters to my friends."},
    {"word": "read", "translation": "okumak", "level": "A2", "category": "verb", "example_sentence": "I read books every day."},
    {"word": "listen", "translation": "dinlemek", "level": "A2", "category": "verb", "example_sentence": "Listen to the music."},
    {"word": "watch", "translation": "izlemek", "level": "A2", "category": "verb", "example_sentence": "I watch TV in the evening."},
    {"word": "travel", "translation": "seyahat etmek", "level": "A2", "category": "verb", "example_sentence": "I love to travel."},
    {"word": "visit", "translation": "ziyaret etmek", "level": "A2", "category": "verb", "example_sentence": "I visit my family every week."},
    {"word": "meet", "translation": "tanışmak", "level": "A2", "category": "verb", "example_sentence": "Nice to meet you."},
    {"word": "help", "translation": "yardım etmek", "level": "A2", "category": "verb", "example_sentence": "Can you help me?"},
    {"word": "important", "translation": "önemli", "level": "A2", "category": "adjective", "example_sentence": "This is very important."},
    {"word": "difficult", "translation": "zor", "level": "A2", "category": "adjective", "example_sentence": "This question is difficult."},
    {"word": "easy", "translation": "kolay", "level": "A2", "category": "adjective", "example_sentence": "This is easy for me."},
    {"word": "beautiful", "translation": "güzel", "level": "A2", "category": "adjective", "example_sentence": "She is beautiful."},
    {"word": "interesting", "translation": "ilginç", "level": "A2", "category": "adjective", "example_sentence": "This book is interesting."},
    {"word": "problem", "translation": "sorun", "level": "A2", "category": "noun", "example_sentence": "I have a problem."},
    {"word": "solution", "translation": "çözüm", "level": "A2", "category": "noun", "example_sentence": "We need a solution."},
    {"word": "question", "translation": "soru", "level": "A2", "category": "noun", "example_sentence": "Do you have a question?"},
    {"word": "answer", "translation": "cevap", "level": "A2", "category": "noun", "example_sentence": "What is the answer?"},
    {"word": "idea", "translation": "fikir", "level": "A2", "category": "noun", "example_sentence": "That's a good idea."},
    
    # B1 seviyesi (20 kelime)
    {"word": "achieve", "translation": "başarmak", "level": "B1", "category": "verb", "example_sentence": "I want to achieve my goals."},
    {"word": "benefit", "translation": "fayda", "level": "B1", "category": "noun", "example_sentence": "Exercise has many benefits."},
    {"word": "challenge", "translation": "meydan okuma", "level": "B1", "category": "noun", "example_sentence": "This is a big challenge."},
    {"word": "develop", "translation": "geliştirmek", "level": "B1", "category": "verb", "example_sentence": "We need to develop new skills."},
    {"word": "effective", "translation": "etkili", "level": "B1", "category": "adjective", "example_sentence": "This method is very effective."},
    {"word": "opportunity", "translation": "fırsat", "level": "B1", "category": "noun", "example_sentence": "This is a great opportunity."},
    {"word": "improve", "translation": "iyileştirmek", "level": "B1", "category": "verb", "example_sentence": "I want to improve my English."},
    {"word": "knowledge", "translation": "bilgi", "level": "B1", "category": "noun", "example_sentence": "Knowledge is power."},
    {"word": "successful", "translation": "başarılı", "level": "B1", "category": "adjective", "example_sentence": "She is a successful entrepreneur."},
    {"word": "experience", "translation": "deneyim", "level": "B1", "category": "noun", "example_sentence": "I have 5 years of experience."},
    {"word": "consider", "translation": "düşünmek", "level": "B1", "category": "verb", "example_sentence": "We should consider this option."},
    {"word": "discuss", "translation": "tartışmak", "level": "B1", "category": "verb", "example_sentence": "Let's discuss this problem."},
    {"word": "explain", "translation": "açıklamak", "level": "B1", "category": "verb", "example_sentence": "Can you explain this to me?"},
    {"word": "suggest", "translation": "önernek", "level": "B1", "category": "verb", "example_sentence": "I suggest we go early."},
    {"word": "decide", "translation": "karar vermek", "level": "B1", "category": "verb", "example_sentence": "We need to decide soon."},
    {"word": "professional", "translation": "profesyonel", "level": "B1", "category": "adjective", "example_sentence": "She is very professional."},
    {"word": "responsible", "translation": "sorumlu", "level": "B1", "category": "adjective", "example_sentence": "I am responsible for this."},
    {"word": "necessary", "translation": "gerekli", "level": "B1", "category": "adjective", "example_sentence": "This is necessary."},
    {"word": "possible", "translation": "mümkün", "level": "B1", "category": "adjective", "example_sentence": "Is it possible?"},
    {"word": "serious", "translation": "ciddi", "level": "B1", "category": "adjective", "example_sentence": "This is a serious matter."},
    
    # B2 seviyesi (15 kelime)
    {"word": "ability", "translation": "yetenek", "level": "B2", "category": "noun", "example_sentence": "She has the ability to learn quickly."},
    {"word": "accomplish", "translation": "tamamlamak", "level": "B2", "category": "verb", "example_sentence": "We need to accomplish this task."},
    {"word": "analyze", "translation": "analiz etmek", "level": "B2", "category": "verb", "example_sentence": "Let's analyze the data."},
    {"word": "approach", "translation": "yaklaşım", "level": "B2", "category": "noun", "example_sentence": "This is a new approach."},
    {"word": "assess", "translation": "değerlendirmek", "level": "B2", "category": "verb", "example_sentence": "We need to assess the situation."},
    {"word": "assume", "translation": "varsaymak", "level": "B2", "category": "verb", "example_sentence": "I assume you know this."},
    {"word": "conclude", "translation": "sonuçlandırmak", "level": "B2", "category": "verb", "example_sentence": "We can conclude that..."},
    {"word": "contribute", "translation": "katkıda bulunmak", "level": "B2", "category": "verb", "example_sentence": "Everyone can contribute."},
    {"word": "demonstrate", "translation": "göstermek", "level": "B2", "category": "verb", "example_sentence": "This demonstrates the point."},
    {"word": "establish", "translation": "kurmak", "level": "B2", "category": "verb", "example_sentence": "We need to establish rules."},
    {"word": "evaluate", "translation": "değerlendirmek", "level": "B2", "category": "verb", "example_sentence": "We must evaluate the results."},
    {"word": "indicate", "translation": "göstermek", "level": "B2", "category": "verb", "example_sentence": "This indicates a problem."},
    {"word": "significant", "translation": "önemli", "level": "B2", "category": "adjective", "example_sentence": "This is significant."},
    {"word": "sufficient", "translation": "yeterli", "level": "B2", "category": "adjective", "example_sentence": "This is sufficient."},
    {"word": "various", "translation": "çeşitli", "level": "B2", "category": "adjective", "example_sentence": "There are various options."},
    
    # C1 seviyesi (10 kelime)
    {"word": "accomplishment", "translation": "başarı", "level": "C1", "category": "noun", "example_sentence": "This is a great accomplishment."},
    {"word": "comprehensive", "translation": "kapsamlı", "level": "C1", "category": "adjective", "example_sentence": "This is a comprehensive study."},
    {"word": "controversial", "translation": "tartışmalı", "level": "C1", "category": "adjective", "example_sentence": "This is a controversial topic."},
    {"word": "elaborate", "translation": "detaylandırmak", "level": "C1", "category": "verb", "example_sentence": "Can you elaborate on this?"},
    {"word": "fundamental", "translation": "temel", "level": "C1", "category": "adjective", "example_sentence": "This is fundamental."},
    {"word": "phenomenon", "translation": "fenomen", "level": "C1", "category": "noun", "example_sentence": "This is an interesting phenomenon."},
    {"word": "sophisticated", "translation": "sofistike", "level": "C1", "category": "adjective", "example_sentence": "This is sophisticated technology."},
    {"word": "substantial", "translation": "önemli", "level": "C1", "category": "adjective", "example_sentence": "This is a substantial improvement."},
    {"word": "theoretical", "translation": "teorik", "level": "C1", "category": "adjective", "example_sentence": "This is theoretical knowledge."},
    {"word": "underlying", "translation": "altta yatan", "level": "C1", "category": "adjective", "example_sentence": "What is the underlying cause?"},
    
    # C2 seviyesi (10 kelime)
    {"word": "acquiesce", "translation": "razı olmak", "level": "C2", "category": "verb", "example_sentence": "He had to acquiesce to their demands."},
    {"word": "circumvent", "translation": "atlatmak", "level": "C2", "category": "verb", "example_sentence": "We need to circumvent this problem."},
    {"word": "concomitant", "translation": "eşlik eden", "level": "C2", "category": "adjective", "example_sentence": "This is a concomitant issue."},
    {"word": "delineate", "translation": "tasvir etmek", "level": "C2", "category": "verb", "example_sentence": "Let me delineate the process."},
    {"word": "ephemeral", "translation": "geçici", "level": "C2", "category": "adjective", "example_sentence": "This is ephemeral."},
    {"word": "meticulous", "translation": "titiz", "level": "C2", "category": "adjective", "example_sentence": "She is very meticulous."},
    {"word": "pervasive", "translation": "yaygın", "level": "C2", "category": "adjective", "example_sentence": "This is a pervasive problem."},
    {"word": "profound", "translation": "derin", "level": "C2", "category": "adjective", "example_sentence": "This has profound implications."},
    {"word": "ubiquitous", "translation": "her yerde bulunan", "level": "C2", "category": "adjective", "example_sentence": "Technology is ubiquitous."},
    {"word": "vindicate", "translation": "haklı çıkarmak", "level": "C2", "category": "verb", "example_sentence": "This will vindicate our approach."},
]


# TÜM SEVİYELER İÇİN QUIZ SORULARI
QUIZ_QUESTIONS = [
    # A1 Grammar (10 soru)
    {
        "question_text": "Hello, _____ are you?",
        "question_type": "multiple_choice",
        "correct_answer": "how",
        "options": json.dumps(["how", "what", "where", "when"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'How are you?' selamlaşma için kullanılır.",
    },
    {
        "question_text": "I _____ a student.",
        "question_type": "multiple_choice",
        "correct_answer": "am",
        "options": json.dumps(["am", "is", "are", "be"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'I' ile 'am' kullanılır.",
    },
    {
        "question_text": "I _____ English every day.",
        "question_type": "multiple_choice",
        "correct_answer": "study",
        "options": json.dumps(["study", "studies", "studying", "studied"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "Present simple tense için 'study' kullanılır.",
    },
    {
        "question_text": "This is _____ book.",
        "question_type": "multiple_choice",
        "correct_answer": "a",
        "options": json.dumps(["a", "an", "the", "is"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'Book' sessiz harfle başlar, 'a' kullanılır.",
    },
    {
        "question_text": "She _____ from Turkey.",
        "question_type": "multiple_choice",
        "correct_answer": "is",
        "options": json.dumps(["am", "is", "are", "be"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'She' ile 'is' kullanılır.",
    },
    {
        "question_text": "They _____ my friends.",
        "question_type": "multiple_choice",
        "correct_answer": "are",
        "options": json.dumps(["am", "is", "are", "be"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'They' ile 'are' kullanılır.",
    },
    {
        "question_text": "I have _____ apple.",
        "question_type": "multiple_choice",
        "correct_answer": "an",
        "options": json.dumps(["a", "an", "the", "is"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'Apple' sesli harfle başlar, 'an' kullanılır.",
    },
    {
        "question_text": "We _____ to school every day.",
        "question_type": "multiple_choice",
        "correct_answer": "go",
        "options": json.dumps(["go", "goes", "going", "went"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'We' ile present simple için 'go' kullanılır.",
    },
    {
        "question_text": "He _____ a teacher.",
        "question_type": "multiple_choice",
        "correct_answer": "is",
        "options": json.dumps(["am", "is", "are", "be"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'He' ile 'is' kullanılır.",
    },
    {
        "question_text": "I _____ happy today.",
        "question_type": "multiple_choice",
        "correct_answer": "am",
        "options": json.dumps(["am", "is", "are", "be"]),
        "level": "A1",
        "category": "grammar",
        "explanation": "'I' ile 'am' kullanılır.",
    },
    
    # A1 Vocabulary (5 soru)
    {
        "question_text": "What is your _____?",
        "question_type": "multiple_choice",
        "correct_answer": "name",
        "options": json.dumps(["name", "age", "color", "food"]),
        "level": "A1",
        "category": "vocabulary",
        "explanation": "'What is your name?' isim sormak için kullanılır.",
    },
    {
        "question_text": "I like _____ food.",
        "question_type": "multiple_choice",
        "correct_answer": "Italian",
        "options": json.dumps(["Italian", "Italy", "Italians", "Italy's"]),
        "level": "A1",
        "category": "vocabulary",
        "explanation": "'Italian' sıfat olarak kullanılır.",
    },
    {
        "question_text": "I need a glass of _____.",
        "question_type": "multiple_choice",
        "correct_answer": "water",
        "options": json.dumps(["water", "food", "book", "friend"]),
        "level": "A1",
        "category": "vocabulary",
        "explanation": "'Water' su anlamına gelir.",
    },
    {
        "question_text": "This is my _____.",
        "question_type": "multiple_choice",
        "correct_answer": "house",
        "options": json.dumps(["house", "water", "food", "book"]),
        "level": "A1",
        "category": "vocabulary",
        "explanation": "'House' ev anlamına gelir.",
    },
    {
        "question_text": "She is my best _____.",
        "question_type": "multiple_choice",
        "correct_answer": "friend",
        "options": json.dumps(["friend", "house", "book", "school"]),
        "level": "A1",
        "category": "vocabulary",
        "explanation": "'Friend' arkadaş anlamına gelir.",
    },
    
    # A2 Grammar (10 soru)
    {
        "question_text": "I _____ to the store yesterday.",
        "question_type": "multiple_choice",
        "correct_answer": "went",
        "options": json.dumps(["go", "went", "gone", "going"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Past tense için 'went' kullanılır.",
    },
    {
        "question_text": "She _____ English for 2 years.",
        "question_type": "multiple_choice",
        "correct_answer": "has studied",
        "options": json.dumps(["studies", "has studied", "is studying", "study"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Present Perfect tense için 'has studied' kullanılır.",
    },
    {
        "question_text": "I _____ watching TV when you called.",
        "question_type": "multiple_choice",
        "correct_answer": "was",
        "options": json.dumps(["am", "was", "were", "is"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Past continuous için 'was' kullanılır.",
    },
    {
        "question_text": "They _____ playing football now.",
        "question_type": "multiple_choice",
        "correct_answer": "are",
        "options": json.dumps(["am", "is", "are", "be"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Present continuous için 'are' kullanılır.",
    },
    {
        "question_text": "I will _____ you tomorrow.",
        "question_type": "multiple_choice",
        "correct_answer": "see",
        "options": json.dumps(["see", "saw", "seen", "seeing"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Future tense için 'will + verb' kullanılır.",
    },
    {
        "question_text": "Can you _____ me?",
        "question_type": "multiple_choice",
        "correct_answer": "help",
        "options": json.dumps(["help", "helped", "helping", "helps"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Modal 'can' ile fiil yalın halde kullanılır.",
    },
    {
        "question_text": "I have _____ this book.",
        "question_type": "multiple_choice",
        "correct_answer": "read",
        "options": json.dumps(["read", "reads", "reading", "readed"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Present Perfect için past participle kullanılır.",
    },
    {
        "question_text": "She is _____ than me.",
        "question_type": "multiple_choice",
        "correct_answer": "taller",
        "options": json.dumps(["tall", "taller", "tallest", "more tall"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Karşılaştırma için 'taller' kullanılır.",
    },
    {
        "question_text": "This is the _____ book I've ever read.",
        "question_type": "multiple_choice",
        "correct_answer": "best",
        "options": json.dumps(["good", "better", "best", "well"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "En üstünlük için 'best' kullanılır.",
    },
    {
        "question_text": "I _____ to visit Paris next year.",
        "question_type": "multiple_choice",
        "correct_answer": "want",
        "options": json.dumps(["want", "wants", "wanting", "wanted"]),
        "level": "A2",
        "category": "grammar",
        "explanation": "Present simple için 'want' kullanılır.",
    },
    
    # A2 Vocabulary (5 soru)
    {
        "question_text": "This question is very _____.",
        "question_type": "multiple_choice",
        "correct_answer": "difficult",
        "options": json.dumps(["difficult", "easy", "good", "bad"]),
        "level": "A2",
        "category": "vocabulary",
        "explanation": "'Difficult' zor anlamına gelir.",
    },
    {
        "question_text": "I have a _____ to solve.",
        "question_type": "multiple_choice",
        "correct_answer": "problem",
        "options": json.dumps(["problem", "solution", "question", "answer"]),
        "level": "A2",
        "category": "vocabulary",
        "explanation": "'Problem' sorun anlamına gelir.",
    },
    {
        "question_text": "Do you have a _____?",
        "question_type": "multiple_choice",
        "correct_answer": "question",
        "options": json.dumps(["question", "answer", "problem", "solution"]),
        "level": "A2",
        "category": "vocabulary",
        "explanation": "'Question' soru anlamına gelir.",
    },
    {
        "question_text": "This book is very _____.",
        "question_type": "multiple_choice",
        "correct_answer": "interesting",
        "options": json.dumps(["interesting", "boring", "difficult", "easy"]),
        "level": "A2",
        "category": "vocabulary",
        "explanation": "'Interesting' ilginç anlamına gelir.",
    },
    {
        "question_text": "That's a good _____.",
        "question_type": "multiple_choice",
        "correct_answer": "idea",
        "options": json.dumps(["idea", "problem", "question", "answer"]),
        "level": "A2",
        "category": "vocabulary",
        "explanation": "'Idea' fikir anlamına gelir.",
    },
    
    # B1 Grammar (10 soru)
    {
        "question_text": "I haven't seen him _____ last week.",
        "question_type": "multiple_choice",
        "correct_answer": "since",
        "options": json.dumps(["since", "for", "from", "during"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Belirli bir zaman noktası için 'since' kullanılır.",
    },
    {
        "question_text": "He is _____ than his brother.",
        "question_type": "multiple_choice",
        "correct_answer": "taller",
        "options": json.dumps(["tall", "taller", "tallest", "more tall"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Karşılaştırma için 'taller' kullanılır.",
    },
    {
        "question_text": "If I _____ rich, I would travel the world.",
        "question_type": "multiple_choice",
        "correct_answer": "were",
        "options": json.dumps(["am", "was", "were", "be"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Second conditional'da 'were' kullanılır.",
    },
    {
        "question_text": "The company decided to _____ new employees.",
        "question_type": "multiple_choice",
        "correct_answer": "hire",
        "options": json.dumps(["hire", "fire", "retire", "admire"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "'Hire' işe almak anlamına gelir.",
    },
    {
        "question_text": "I _____ English for 5 years.",
        "question_type": "multiple_choice",
        "correct_answer": "have been studying",
        "options": json.dumps(["study", "studied", "have studied", "have been studying"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Present Perfect Continuous için 'have been studying' kullanılır.",
    },
    {
        "question_text": "She _____ be at home now.",
        "question_type": "multiple_choice",
        "correct_answer": "might",
        "options": json.dumps(["might", "must", "should", "will"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Olasılık için 'might' kullanılır.",
    },
    {
        "question_text": "I wish I _____ speak French.",
        "question_type": "multiple_choice",
        "correct_answer": "could",
        "options": json.dumps(["can", "could", "will", "would"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Wish clause'da 'could' kullanılır.",
    },
    {
        "question_text": "By next year, I _____ finished my studies.",
        "question_type": "multiple_choice",
        "correct_answer": "will have",
        "options": json.dumps(["will", "will have", "have", "had"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Future Perfect için 'will have' kullanılır.",
    },
    {
        "question_text": "The book _____ by millions of people.",
        "question_type": "multiple_choice",
        "correct_answer": "has been read",
        "options": json.dumps(["has read", "has been read", "is read", "was read"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Present Perfect Passive için 'has been read' kullanılır.",
    },
    {
        "question_text": "I _____ rather stay home tonight.",
        "question_type": "multiple_choice",
        "correct_answer": "would",
        "options": json.dumps(["would", "will", "should", "could"]),
        "level": "B1",
        "category": "grammar",
        "explanation": "Tercih için 'would rather' kullanılır.",
    },
    
    # B1 Vocabulary (5 soru)
    {
        "question_text": "Choose the correct word: The _____ of the book is interesting.",
        "question_type": "multiple_choice",
        "correct_answer": "content",
        "options": json.dumps(["content", "contain", "container", "containing"]),
        "level": "B1",
        "category": "vocabulary",
        "explanation": "'Content' kelimesi 'içerik' anlamına gelir.",
    },
    {
        "question_text": "This is a great _____ to learn.",
        "question_type": "multiple_choice",
        "correct_answer": "opportunity",
        "options": json.dumps(["opportunity", "chance", "time", "moment"]),
        "level": "B1",
        "category": "vocabulary",
        "explanation": "'Opportunity' fırsat anlamına gelir.",
    },
    {
        "question_text": "She is a _____ entrepreneur.",
        "question_type": "multiple_choice",
        "correct_answer": "successful",
        "options": json.dumps(["successful", "success", "succeed", "successfully"]),
        "level": "B1",
        "category": "vocabulary",
        "explanation": "'Successful' başarılı anlamına gelir.",
    },
    {
        "question_text": "I want to _____ my English.",
        "question_type": "multiple_choice",
        "correct_answer": "improve",
        "options": json.dumps(["improve", "improvement", "improving", "improved"]),
        "level": "B1",
        "category": "vocabulary",
        "explanation": "'Improve' iyileştirmek anlamına gelir.",
    },
    {
        "question_text": "This method is very _____.",
        "question_type": "multiple_choice",
        "correct_answer": "effective",
        "options": json.dumps(["effective", "effect", "effectively", "efficiency"]),
        "level": "B1",
        "category": "vocabulary",
        "explanation": "'Effective' etkili anlamına gelir.",
    },
    
    # B2 Grammar (10 soru)
    {
        "question_text": "She is _____ in mathematics.",
        "question_type": "multiple_choice",
        "correct_answer": "excellent",
        "options": json.dumps(["excellent", "excellence", "excel", "excellently"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "'Excellent' sıfat olarak kullanılır.",
    },
    {
        "question_text": "Had I known, I _____ differently.",
        "question_type": "multiple_choice",
        "correct_answer": "would have acted",
        "options": json.dumps(["would act", "would have acted", "acted", "will act"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "Third conditional için 'would have acted' kullanılır.",
    },
    {
        "question_text": "Not only _____ she speak English, but also French.",
        "question_type": "multiple_choice",
        "correct_answer": "does",
        "options": json.dumps(["does", "do", "did", "is"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "Inversion için 'does' kullanılır.",
    },
    {
        "question_text": "I'd rather you _____ here.",
        "question_type": "multiple_choice",
        "correct_answer": "stayed",
        "options": json.dumps(["stay", "stayed", "staying", "stays"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "'Would rather' ile past tense kullanılır.",
    },
    {
        "question_text": "The report _____ by the team yesterday.",
        "question_type": "multiple_choice",
        "correct_answer": "was completed",
        "options": json.dumps(["completed", "was completed", "has completed", "is completed"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "Past Passive için 'was completed' kullanılır.",
    },
    {
        "question_text": "I suggest that he _____ early.",
        "question_type": "multiple_choice",
        "correct_answer": "leave",
        "options": json.dumps(["leaves", "leave", "left", "leaving"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "Subjunctive için 'leave' kullanılır.",
    },
    {
        "question_text": "_____ I had more time, I would travel more.",
        "question_type": "multiple_choice",
        "correct_answer": "If only",
        "options": json.dumps(["If only", "Only if", "If", "Unless"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "'If only' dilek için kullanılır.",
    },
    {
        "question_text": "The harder you work, _____ you will succeed.",
        "question_type": "multiple_choice",
        "correct_answer": "the more",
        "options": json.dumps(["the more", "more", "the most", "most"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "Comparative için 'the more' kullanılır.",
    },
    {
        "question_text": "It's high time we _____ something about it.",
        "question_type": "multiple_choice",
        "correct_answer": "did",
        "options": json.dumps(["do", "did", "doing", "done"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "'It's high time' ile past tense kullanılır.",
    },
    {
        "question_text": "I wish I _____ studied harder.",
        "question_type": "multiple_choice",
        "correct_answer": "had",
        "options": json.dumps(["have", "had", "would", "could"]),
        "level": "B2",
        "category": "grammar",
        "explanation": "Past wish için 'had' kullanılır.",
    },
    
    # B2 Vocabulary (5 soru)
    {
        "question_text": "She has the _____ to learn quickly.",
        "question_type": "multiple_choice",
        "correct_answer": "ability",
        "options": json.dumps(["ability", "able", "enable", "capable"]),
        "level": "B2",
        "category": "vocabulary",
        "explanation": "'Ability' yetenek anlamına gelir.",
    },
    {
        "question_text": "We need to _____ this task.",
        "question_type": "multiple_choice",
        "correct_answer": "accomplish",
        "options": json.dumps(["accomplish", "accomplishment", "accomplishing", "accomplished"]),
        "level": "B2",
        "category": "vocabulary",
        "explanation": "'Accomplish' tamamlamak anlamına gelir.",
    },
    {
        "question_text": "Let's _____ the data.",
        "question_type": "multiple_choice",
        "correct_answer": "analyze",
        "options": json.dumps(["analyze", "analysis", "analyzing", "analytical"]),
        "level": "B2",
        "category": "vocabulary",
        "explanation": "'Analyze' analiz etmek anlamına gelir.",
    },
    {
        "question_text": "This is a new _____.",
        "question_type": "multiple_choice",
        "correct_answer": "approach",
        "options": json.dumps(["approach", "approaching", "approached", "approaches"]),
        "level": "B2",
        "category": "vocabulary",
        "explanation": "'Approach' yaklaşım anlamına gelir.",
    },
    {
        "question_text": "We need to _____ the situation.",
        "question_type": "multiple_choice",
        "correct_answer": "assess",
        "options": json.dumps(["assess", "assessment", "assessing", "assessed"]),
        "level": "B2",
        "category": "vocabulary",
        "explanation": "'Assess' değerlendirmek anlamına gelir.",
    },
    
    # C1 Grammar (5 soru)
    {
        "question_text": "_____ had I arrived than it started raining.",
        "question_type": "multiple_choice",
        "correct_answer": "No sooner",
        "options": json.dumps(["No sooner", "Hardly", "Scarcely", "As soon as"]),
        "level": "C1",
        "category": "grammar",
        "explanation": "'No sooner...than' kalıbı kullanılır.",
    },
    {
        "question_text": "Not until she arrived _____ I realize the problem.",
        "question_type": "multiple_choice",
        "correct_answer": "did",
        "options": json.dumps(["did", "do", "does", "was"]),
        "level": "C1",
        "category": "grammar",
        "explanation": "Inversion için 'did' kullanılır.",
    },
    {
        "question_text": "So complex _____ the problem that no one could solve it.",
        "question_type": "multiple_choice",
        "correct_answer": "was",
        "options": json.dumps(["was", "is", "were", "are"]),
        "level": "C1",
        "category": "grammar",
        "explanation": "Inversion için 'was' kullanılır.",
    },
    {
        "question_text": "Were it not for your help, I _____ succeeded.",
        "question_type": "multiple_choice",
        "correct_answer": "would not have",
        "options": json.dumps(["would not have", "would not", "will not have", "had not"]),
        "level": "C1",
        "category": "grammar",
        "explanation": "Third conditional için 'would not have' kullanılır.",
    },
    {
        "question_text": "The proposal _____ consideration by the committee.",
        "question_type": "multiple_choice",
        "correct_answer": "is under",
        "options": json.dumps(["is under", "is in", "is on", "is at"]),
        "level": "C1",
        "category": "grammar",
        "explanation": "'Under consideration' deyimi kullanılır.",
    },
    
    # C1 Vocabulary (5 soru)
    {
        "question_text": "This is a great _____.",
        "question_type": "multiple_choice",
        "correct_answer": "accomplishment",
        "options": json.dumps(["accomplishment", "accomplish", "accomplishing", "accomplished"]),
        "level": "C1",
        "category": "vocabulary",
        "explanation": "'Accomplishment' başarı anlamına gelir.",
    },
    {
        "question_text": "This is a _____ study.",
        "question_type": "multiple_choice",
        "correct_answer": "comprehensive",
        "options": json.dumps(["comprehensive", "comprehend", "comprehending", "comprehended"]),
        "level": "C1",
        "category": "vocabulary",
        "explanation": "'Comprehensive' kapsamlı anlamına gelir.",
    },
    {
        "question_text": "This is a _____ topic.",
        "question_type": "multiple_choice",
        "correct_answer": "controversial",
        "options": json.dumps(["controversial", "controversy", "controversially", "controversies"]),
        "level": "C1",
        "category": "vocabulary",
        "explanation": "'Controversial' tartışmalı anlamına gelir.",
    },
    {
        "question_text": "Can you _____ on this?",
        "question_type": "multiple_choice",
        "correct_answer": "elaborate",
        "options": json.dumps(["elaborate", "elaboration", "elaborating", "elaborated"]),
        "level": "C1",
        "category": "vocabulary",
        "explanation": "'Elaborate' detaylandırmak anlamına gelir.",
    },
    {
        "question_text": "This is _____.",
        "question_type": "multiple_choice",
        "correct_answer": "fundamental",
        "options": json.dumps(["fundamental", "fundamentally", "fundament", "fundamentals"]),
        "level": "C1",
        "category": "vocabulary",
        "explanation": "'Fundamental' temel anlamına gelir.",
    },
    
    # C2 Grammar (3 soru)
    {
        "question_text": "Such _____ the complexity that few understood it.",
        "question_type": "multiple_choice",
        "correct_answer": "was",
        "options": json.dumps(["was", "is", "were", "are"]),
        "level": "C2",
        "category": "grammar",
        "explanation": "Inversion için 'was' kullanılır.",
    },
    {
        "question_text": "Little _____ she know what was coming.",
        "question_type": "multiple_choice",
        "correct_answer": "did",
        "options": json.dumps(["did", "do", "does", "was"]),
        "level": "C2",
        "category": "grammar",
        "explanation": "Inversion için 'did' kullanılır.",
    },
    {
        "question_text": "Rarely _____ such dedication been seen.",
        "question_type": "multiple_choice",
        "correct_answer": "has",
        "options": json.dumps(["has", "have", "had", "is"]),
        "level": "C2",
        "category": "grammar",
        "explanation": "Inversion için 'has' kullanılır.",
    },
    
    # C2 Vocabulary (2 soru)
    {
        "question_text": "He had to _____ to their demands.",
        "question_type": "multiple_choice",
        "correct_answer": "acquiesce",
        "options": json.dumps(["acquiesce", "acquiescence", "acquiescing", "acquiesced"]),
        "level": "C2",
        "category": "vocabulary",
        "explanation": "'Acquiesce' razı olmak anlamına gelir.",
    },
    {
        "question_text": "We need to _____ this problem.",
        "question_type": "multiple_choice",
        "correct_answer": "circumvent",
        "options": json.dumps(["circumvent", "circumvention", "circumventing", "circumvented"]),
        "level": "C2",
        "category": "vocabulary",
        "explanation": "'Circumvent' atlatmak anlamına gelir.",
    },
]


async def seed_content():
    """Veritabanına kapsamlı içerik ekler."""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async with engine.begin() as conn:
        # Tabloları oluştur
        await conn.run_sync(Base.metadata.create_all)
    
    async with engine.begin() as conn:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Kelimeleri ekle
            added_words = 0
            for word_data in VOCABULARY_WORDS:
                existing = await session.execute(
                    select(VocabularyWord).where(
                        VocabularyWord.word == word_data["word"],
                        VocabularyWord.level == word_data["level"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    word = VocabularyWord(**word_data)
                    session.add(word)
                    added_words += 1
            
            if added_words > 0:
                print(f"✅ {added_words} yeni kelime eklendi")
            else:
                print("ℹ️  Tüm kelimeler zaten mevcut")
            
            # Quiz sorularını ekle
            added_questions = 0
            for question_data in QUIZ_QUESTIONS:
                existing = await session.execute(
                    select(QuizQuestion).where(
                        QuizQuestion.question_text == question_data["question_text"],
                        QuizQuestion.level == question_data["level"]
                    )
                )
                if existing.scalar_one_or_none() is None:
                    question = QuizQuestion(**question_data)
                    session.add(question)
                    added_questions += 1
            
            if added_questions > 0:
                print(f"✅ {added_questions} yeni quiz sorusu eklendi")
            else:
                print("ℹ️  Tüm quiz soruları zaten mevcut")
            
            await session.commit()
    
    print(f"\n✅ İçerik seed işlemi tamamlandı!")
    print(f"📊 Toplam: {len(VOCABULARY_WORDS)} kelime, {len(QUIZ_QUESTIONS)} quiz sorusu")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_content())

