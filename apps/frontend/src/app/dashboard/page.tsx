"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

import { ReviewScheduleWidget } from "@/components/ReviewScheduleWidget";

interface LearningGoal {
  id: number;
  user_id: string;
  target_language: string;
  level: string;
  daily_minutes: number;
  goal_type: string;
  focus_topics: string | null;
  created_at: string;
  current_xp: number;
  next_level_xp: number;
  next_level: string | null;
}

const goalTypeLabels: Record<string, string> = {
  general: "Genel İngilizce",
  exam: "Sınav hazırlık",
  speaking: "Konuşma pratiği",
  career: "Kariyer / iş İngilizcesi",
};

export default function DashboardPage() {
  const router = useRouter();
  const { signOut, user } = useAuth();
  const [goal, setGoal] = useState<LearningGoal | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGoal = async () => {
      try {
        const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learning-goals/latest`;
        const res = await apiFetch(apiUrl);

        if (!res.ok) {
          if (res.status === 404) {
            // Plan yoksa onboarding'e yönlendir
            router.push("/onboarding");
            return;
          }
          if (res.status === 401) {
            router.push("/login");
            return;
          }
          throw new Error(`Plan getirilemedi. (Status: ${res.status})`);
        }

        const data = await res.json();
        setGoal(data);
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error("Error fetching goal:", err);
        setError(err instanceof Error ? err.message : "Bir hata oluştu.");
      } finally {
        setLoading(false);
      }
    };

    fetchGoal();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
        <div className="text-sm text-slate-400">Yükleniyor...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
        <div className="text-sm text-red-400">{error}</div>
      </div>
    );
  }

  if (!goal) {
    return null;
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 text-slate-50">
        <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-indigo-500/10 px-2 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">
                Lexavia
              </span>
              <span className="text-sm text-slate-400">Dashboard</span>
            </div>
            <nav className="hidden items-center gap-4 text-sm text-slate-300 sm:flex">
              {user && (
                <span className="text-xs text-slate-400">{user.email}</span>
              )}
              <a
                href="/statistics"
                className="rounded-full border border-slate-700 px-4 py-1.5 text-xs font-medium hover:border-slate-500 hover:text-slate-100"
              >
                İstatistikler
              </a>
              <button
                onClick={async () => {
                  await signOut();
                  router.push("/");
                }}
                className="rounded-full border border-slate-700 px-4 py-1.5 text-xs font-medium hover:border-slate-500 hover:text-slate-100"
              >
                Çıkış yap
              </button>
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-5xl px-6 py-12">
          <div className="mb-8 space-y-2">
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              Hoş geldin! 👋
            </h1>
            <p className="text-sm text-slate-400">
              Kişisel öğrenme planın hazır. Bugünkü çalışmalarına başlayabilirsin.
            </p>
          </div>

          {/* Plan Kartı */}
          <div className="mb-8 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300">
                  Kişisel Planın
                </p>
                <h2 className="mt-1 text-xl font-semibold text-slate-50">
                  {goal.level} Seviyesi · {goalTypeLabels[goal.goal_type] || goal.goal_type}
                </h2>
              </div>
              <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">
                {goal.daily_minutes} dk/gün
              </span>
            </div>
            {goal.next_level && (
              <div className="mt-4 border-t border-slate-800/50 pt-4">
                <div className="flex justify-between text-xs text-slate-400 mb-2">
                  <span className="font-medium text-slate-300">Level Progress</span>
                  <span>{goal.current_xp} / {goal.next_level_xp} XP</span>
                </div>
                <div className="h-2.5 w-full rounded-full bg-slate-950/50 border border-slate-800/50 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-emerald-500 shadow-[0_0_10px_rgba(99,102,241,0.5)] transition-all duration-1000 ease-out"
                    style={{ width: `${Math.min(100, (goal.current_xp / goal.next_level_xp) * 100)}%` }}
                  />
                </div>
                <div className="mt-2 flex justify-between text-[11px] font-medium">
                  <span className="text-indigo-400">{goal.level}</span>
                  <span className="text-emerald-400">Next: {goal.next_level}</span>
                </div>
              </div>
            )}

            <div className="mt-4 grid gap-3 text-xs sm:grid-cols-2">
              <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-3">
                <p className="font-semibold text-slate-50">Hedef dil</p>
                <p className="mt-1 text-[11px] text-slate-400">
                  {goal.target_language === "en" ? "İngilizce" : goal.target_language}
                </p>
              </div>
              <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-3">
                <p className="font-semibold text-slate-50">Günlük hedef</p>
                <p className="mt-1 text-[11px] text-slate-400">
                  {goal.daily_minutes} dakika çalışma
                </p>
              </div>
            </div>

            {goal.focus_topics && (
              <div className="mt-4 rounded-xl border border-slate-800/80 bg-slate-950/40 p-3">
                <p className="text-xs font-semibold text-slate-50">Odak alanların</p>
                <p className="mt-1 text-[11px] text-slate-300">{goal.focus_topics}</p>
              </div>
            )}
          </div>

          {/* Bugünkü Plan */}
          <div className="mb-8 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
            <div className="mb-4 flex items-center justify-between text-xs text-slate-300">
              <span className="font-medium">Bugünkü planın</span>
              <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
                {goal.daily_minutes} dakikalık çalışma
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5">
                <div>
                  <p className="font-semibold text-slate-50">
                    Kelime kartları · {goal.level}
                  </p>
                  <p className="text-[11px] text-slate-400">
                    {Math.floor(goal.daily_minutes * 0.6)} yeni kelime · {Math.floor(goal.daily_minutes * 0.4)} tekrar · {Math.floor(goal.daily_minutes * 0.5)} dk
                  </p>
                </div>
                <a
                  href="/practice/flashcards"
                  className="rounded-full bg-indigo-500 px-3 py-1 text-[11px] font-semibold text-white hover:bg-indigo-400"
                >
                  Başla
                </a>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/40 px-3 py-2.5">
                <div>
                  <p className="font-semibold text-slate-50">
                    Dilbilgisi · {goal.goal_type === "exam" ? "Sınav soruları" : "Pratik"}
                  </p>
                  <p className="text-[11px] text-slate-400">
                    5 soru · hedef doğruluk %80
                  </p>
                </div>
                <a
                  href="/practice/quiz"
                  className="rounded-full bg-slate-800 px-3 py-1 text-[11px] text-slate-200 hover:bg-slate-700"
                >
                  Çöz
                </a>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-gradient-to-r from-indigo-900/60 via-slate-900/80 to-emerald-900/60 px-3 py-3">
                <p className="text-[11px] uppercase tracking-[0.16em] text-indigo-300">
                  AI analizi
                </p>
                <p className="mt-1 text-xs text-slate-100">
                  Planın hazır! İlk çalışmanı tamamladıktan sonra{" "}
                  <span className="font-semibold text-emerald-300">
                    zayıf kaldığın konular
                  </span>{" "}
                  için özel öneriler alacaksın.
                </p>
              </div>
            </div>
          </div>



          {/* Review Schedule Widget */}
          <ReviewScheduleWidget userId={user?.id || ''} />
        </main>
      </div>
    </ProtectedRoute>
  );
}

