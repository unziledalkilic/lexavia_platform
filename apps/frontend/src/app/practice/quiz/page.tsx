"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/api";
import { generateQuiz } from "@/lib/api";

interface QuizQuestion {
  id: number;
  word_id: number;
  question_text: string;
  question_type: string;
  correct_answer: string;
  options: string | null; // JSON string
  level: string;
  category: string | null;
  explanation: string | null;
}

export default function QuizPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [answers, setAnswers] = useState<number[]>([]);
  const [newLevel, setNewLevel] = useState<string | null>(null);

  const searchParams = useSearchParams();

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        // Önce kullanıcının planını al
        const goalRes = await apiFetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learning-goals/latest`
        );
        if (!goalRes.ok) {
          router.push("/onboarding");
          return;
        }
        const goal = await goalRes.json();

        // Check for Review Mode
        const mode = searchParams.get('mode');
        const reviewWord = searchParams.get('word');
        const translation = searchParams.get('translation') || undefined;

        if (mode === 'review' && reviewWord) {
          // --- REVIEW MODE: Generate specific question for the word ---
          const quiz = await generateQuiz({
            word: reviewWord,
            level: goal.level || 'B1',
            category: 'vocabulary',
            translation: translation
          });

          const newQuestion: QuizQuestion = {
            id: 1,
            word_id: 0,
            question_text: quiz.question_text,
            question_type: quiz.question_type,
            correct_answer: quiz.correct_answer,
            options: quiz.options, // Already a JSON string likely, or stringified
            level: quiz.level,
            category: quiz.category,
            explanation: quiz.explanation
          };

          setQuestions([newQuestion]);

        } else {
          // --- NORMAL MODE: Fetch random questions ---
          const questionsRes = await apiFetch(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/quiz/questions?level=${goal.level}&limit=5`
          );
          if (!questionsRes.ok) {
            throw new Error("Sorular getirilemedi");
          }
          const data = await questionsRes.json();
          setQuestions(data.questions);
        }

      } catch (error) {
        // eslint-disable-next-line no-console
        console.error("Error fetching questions:", error);
        setQuestions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [router, searchParams]);

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
          <div className="text-sm text-slate-400">Yükleniyor...</div>
        </div>
      </ProtectedRoute>
    );
  }

  if (questions.length === 0) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-6">
          <div className="w-full max-w-md text-center">
            <p className="text-slate-400 mb-4">Henüz quiz sorusu bulunmuyor.</p>
            <button
              onClick={() => router.push("/dashboard")}
              className="rounded-full bg-indigo-500 px-6 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
            >
              Dashboard'a dön
            </button>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  const currentQuestion = questions[currentIndex];
  const options = currentQuestion.options
    ? JSON.parse(currentQuestion.options)
    : [];
  const correctIndex = options.indexOf(currentQuestion.correct_answer);
  const isCorrect = selectedAnswer === correctIndex;

  const handleAnswerSelect = (index: number) => {
    if (showResult) return;
    setSelectedAnswer(index);
  };

  const handleSubmit = () => {
    if (selectedAnswer === null) return;

    setShowResult(true);
    if (selectedAnswer === correctIndex) {
      setScore(score + 1);
    }
    setAnswers([...answers, selectedAnswer]);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      handleComplete();
    }
  };

  const handleComplete = async () => {
    if (completed) return;

    const percentage = Math.round((score / questions.length) * 100);

    // Quiz sonucunu kaydet
    try {
      const res = await apiFetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/quiz/sessions`,
        {
          method: "POST",
          body: JSON.stringify({
            score: percentage,
            total_questions: questions.length,
            correct_answers: score,
            category_breakdown: JSON.stringify({ vocabulary: questions.length }),
            results: questions.map((q, idx) => {
              const options = q.options ? JSON.parse(q.options) : [];
              const correctIdx = options.indexOf(q.correct_answer);
              return {
                word_id: q.word_id,
                word: q.correct_answer,
                is_correct: answers[idx] === correctIdx
              };
            })
          }),
        }
      );

      if (res.ok) {
        const data = await res.json();
        if (data.new_level) {
          setNewLevel(data.new_level);
        }
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error("Error saving quiz result:", error);
    }

    setCompleted(true);
  };

  if (completed) {
    const percentage = Math.round((score / questions.length) * 100);
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-6">
          <div className="w-full max-w-2xl">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
              <div className="text-center mb-8">
                <p className="text-6xl mb-4">
                  {percentage >= 80 ? "🎉" : percentage >= 60 ? "👍" : "📚"}
                </p>
                <h2 className="text-3xl font-semibold text-slate-50 mb-2">
                  {newLevel ? `Tebrikler! Seviye Atladın: ${newLevel} 🎉` : "Quiz Tamamlandı!"}
                </h2>
                {newLevel && (
                  <div className="mb-4 p-3 bg-amber-500/20 border border-amber-500/50 rounded-xl text-amber-200">
                    Yeni kelime setleri kilidi açıldı! 🔓
                  </div>
                )}
                <p className="text-lg text-slate-300 mb-4">
                  {score} / {questions.length} doğru
                </p>
                <div className="inline-flex items-center gap-2 rounded-full bg-indigo-500/10 px-4 py-2">
                  <span className="text-2xl font-bold text-indigo-300">
                    %{percentage}
                  </span>
                </div>
              </div>

              <div className="space-y-3 mb-8">
                {questions.map((q, idx) => {
                  const qOptions = q.options ? JSON.parse(q.options) : [];
                  const qCorrectIndex = qOptions.indexOf(q.correct_answer);
                  return (
                    <div
                      key={q.id}
                      className={`rounded-xl border p-3 ${answers[idx] === qCorrectIndex
                        ? "border-emerald-800/50 bg-emerald-900/20"
                        : "border-red-800/50 bg-red-900/20"
                        }`}
                    >
                      <p className="text-sm text-slate-200 mb-1">{q.question_text}</p>
                      <p className="text-xs text-slate-400">
                        {answers[idx] === qCorrectIndex ? "✓ Doğru" : "✗ Yanlış"}
                      </p>
                    </div>
                  );
                })}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => router.push("/dashboard")}
                  className="flex-1 rounded-full border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:border-slate-500"
                >
                  Dashboard'a dön
                </button>
                <button
                  onClick={() => {
                    setCurrentIndex(0);
                    setSelectedAnswer(null);
                    setShowResult(false);
                    setScore(0);
                    setCompleted(false);
                    setAnswers([]);
                  }}
                  className="flex-1 rounded-full bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
                >
                  Tekrar çöz
                </button>
              </div>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 text-slate-50">
        <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur">
          <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
            <div className="flex items-center gap-2">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-sm text-slate-400 hover:text-slate-200"
              >
                ← Geri
              </button>
              <span className="text-sm text-slate-400">
                Soru {currentIndex + 1} / {questions.length}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-sm text-slate-400">
                Skor: {score} / {questions.length}
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-3xl px-6 py-12">
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-slate-50 mb-4">
              {currentQuestion.question_text}
            </h1>
          </div>

          <div className="space-y-3 mb-8">
            {options.map((option: string, index: number) => (
              <button
                key={index}
                onClick={() => handleAnswerSelect(index)}
                disabled={showResult}
                className={`w-full text-left rounded-xl border p-4 transition-all ${selectedAnswer === index
                  ? showResult
                    ? isCorrect && index === correctIndex
                      ? "border-emerald-400 bg-emerald-500/20"
                      : index === correctIndex
                        ? "border-emerald-400 bg-emerald-500/20"
                        : "border-red-400 bg-red-500/20"
                    : "border-indigo-400 bg-indigo-500/20"
                  : "border-slate-700 bg-slate-900/60 hover:border-slate-500"
                  } ${showResult ? "cursor-default" : "cursor-pointer"}`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${selectedAnswer === index
                      ? "bg-indigo-500 text-white"
                      : "bg-slate-800 text-slate-300"
                      }`}
                  >
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span className="text-slate-200">{option}</span>
                  {showResult && index === correctIndex && (
                    <span className="ml-auto text-emerald-400">✓</span>
                  )}
                  {showResult &&
                    selectedAnswer === index &&
                    index !== correctIndex && (
                      <span className="ml-auto text-red-400">✗</span>
                    )}
                </div>
              </button>
            ))}
          </div>

          {showResult && (
            <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
              <p
                className={`text-sm font-semibold mb-2 ${isCorrect ? "text-emerald-300" : "text-red-300"
                  }`}
              >
                {isCorrect ? "✓ Doğru!" : "✗ Yanlış"}
              </p>
              <p className="text-xs text-slate-300">
                {currentQuestion.explanation || "Açıklama bulunmuyor."}
              </p>
            </div>
          )}

          <div className="flex items-center justify-center gap-4">
            {!showResult ? (
              <button
                onClick={handleSubmit}
                disabled={selectedAnswer === null}
                className="rounded-full bg-indigo-500 px-6 py-2 text-sm font-semibold text-white hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cevabı Gönder
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="rounded-full bg-indigo-500 px-6 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
              >
                {currentIndex === questions.length - 1 ? "Sonuçları Gör" : "Sonraki Soru"}
              </button>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}



