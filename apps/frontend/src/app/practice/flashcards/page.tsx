"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/api";

interface VocabularyWord {
  id: number;
  word: string;
  translation: string;
  level: string;
  category: string | null;
  example_sentence: string | null;
}

export default function FlashcardsPage() {
  const router = useRouter();
  const [words, setWords] = useState<VocabularyWord[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const fetchWords = async () => {
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

        // Plan seviyesine göre kelimeleri getir
        const wordsRes = await apiFetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/vocabulary?level=${goal.level}&limit=10`
        );
        if (!wordsRes.ok) {
          throw new Error("Kelimeler getirilemedi");
        }
        const data = await wordsRes.json();
        setWords(data.words);
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error("Error fetching words:", error);
        // Fallback: boş array ile devam et
        setWords([]);
      } finally {
        setLoading(false);
      }
    };

    fetchWords();
  }, [router]);

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
          <div className="text-sm text-slate-400">Yükleniyor...</div>
        </div>
      </ProtectedRoute>
    );
  }

  if (words.length === 0) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-6">
          <div className="w-full max-w-md text-center">
            <p className="text-slate-400 mb-4">Henüz kelime kartı bulunmuyor.</p>
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

  const currentWord = words[currentIndex];

  const handleNext = () => {
    if (currentIndex < words.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    } else {
      setCompleted(true);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
    }
  };

  if (completed) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-6">
          <div className="w-full max-w-md text-center space-y-4">
            <div className="rounded-3xl border border-emerald-800/50 bg-emerald-900/20 p-8">
              <p className="text-4xl mb-4">🎉</p>
              <h2 className="text-2xl font-semibold text-emerald-300 mb-2">
                Harika iş çıkardın!
              </h2>
              <p className="text-sm text-slate-300 mb-6">
                {words.length} kelimeyi gözden geçirdin.
              </p>
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
                    setIsFlipped(false);
                    setCompleted(false);
                  }}
                  className="flex-1 rounded-full bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
                >
                  Tekrar et
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
                {currentIndex + 1} / {words.length}
              </span>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-3xl px-6 py-12">
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-semibold text-slate-50 mb-2">
              Kelime Kartları
            </h1>
            <p className="text-sm text-slate-400">
              Kartı çevirmek için tıkla
            </p>
          </div>

          <div className="flex items-center justify-center min-h-[400px]">
            <div
              onClick={() => setIsFlipped(!isFlipped)}
              className="relative w-full max-w-md h-64 cursor-pointer perspective-1000"
            >
              <div
                className={`relative w-full h-full transition-transform duration-500 transform-style-preserve-3d ${
                  isFlipped ? "rotate-y-180" : ""
                }`}
              >
                {/* Ön yüz */}
                <div
                  className={`absolute w-full h-full backface-hidden rounded-3xl border border-slate-800 bg-slate-900/70 p-8 flex items-center justify-center shadow-[0_20px_60px_rgba(15,23,42,0.9)] ${
                    isFlipped ? "hidden" : ""
                  }`}
                >
                  <div className="text-center">
                    <p className="text-4xl font-bold text-indigo-400 mb-4">
                      {currentWord.word}
                    </p>
                    <p className="text-sm text-slate-400">Çevirmek için tıkla</p>
                  </div>
                </div>

                {/* Arka yüz */}
                <div
                  className={`absolute w-full h-full backface-hidden rotate-y-180 rounded-3xl border border-slate-800 bg-gradient-to-br from-indigo-900/60 to-emerald-900/60 p-8 flex flex-col justify-center shadow-[0_20px_60px_rgba(15,23,42,0.9)] ${
                    !isFlipped ? "hidden" : ""
                  }`}
                >
                  <div className="text-center space-y-4">
                    <p className="text-3xl font-bold text-slate-50 mb-2">
                      {currentWord.translation}
                    </p>
                    {currentWord.example_sentence && (
                      <p className="text-sm text-slate-300 italic">
                        "{currentWord.example_sentence}"
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className="rounded-full border border-slate-700 px-6 py-2 text-sm font-medium text-slate-200 hover:border-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Önceki
            </button>
            <button
              onClick={handleNext}
              className="rounded-full bg-indigo-500 px-6 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
            >
              {currentIndex === words.length - 1 ? "Bitir" : "Sonraki"}
            </button>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}

