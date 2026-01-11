"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

interface Statistics {
  total_quizzes: number;
  average_score: number;
  total_correct: number;
  total_questions: number;
  recent_quizzes: Array<{
    date: string | null;
    score: number;
  }>;
}

export default function StatisticsPage() {
  const router = useRouter();
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await apiFetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/statistics`
        );
        if (!res.ok) {
          const errorText = await res.text();
          // eslint-disable-next-line no-console
          console.error("API Error:", res.status, errorText);
          throw new Error(`İstatistikler getirilemedi: ${res.status}`);
        }
        const data = await res.json();
        setStats(data);
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error("Error fetching statistics:", error);
        // Hata durumunda bile boş stats göster
        setStats({
          total_quizzes: 0,
          average_score: 0,
          total_correct: 0,
          total_questions: 0,
          recent_quizzes: [],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center">
          <div className="text-sm text-slate-400">Yükleniyor...</div>
        </div>
      </ProtectedRoute>
    );
  }

  // stats null olsa bile devam et (boş veri ile)
  if (!stats) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-6">
          <div className="w-full max-w-md text-center">
            <p className="text-slate-400 mb-4">İstatistikler yüklenemedi.</p>
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

  // Son 7 gün verilerini formatla
  // Son 7 gün verilerini formatla ve tarihe göre grupla
  const last7DaysMap = new Map<string, { totalScore: number; count: number }>();

  // Şimdiki günden geriye 7 günün tarihlerini oluştur
  const today = new Date();
  const dateLabels: string[] = [];

  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    // Format: YYYY-MM-DD
    const dateKey = d.toISOString().split('T')[0];
    last7DaysMap.set(dateKey, { totalScore: 0, count: 0 });

    // Label için gün adı
    const dayName = d.toLocaleDateString('tr-TR', { weekday: 'short' });
    dateLabels.push(dayName);
  }

  // Quizleri tarihlerine göre eşleştir
  stats.recent_quizzes.forEach((q) => {
    if (!q.date) return;
    // Backend'den gelen tarih formatı ISO string ise:
    const qDate = new Date(q.date).toISOString().split('T')[0];

    if (last7DaysMap.has(qDate)) {
      const current = last7DaysMap.get(qDate)!;
      current.totalScore += q.score;
      current.count += 1;
    }
  });

  // Map'ten array'e çevir
  const last7Days = Array.from(last7DaysMap.entries()).map(([date, data], index) => {
    const avgScore = data.count > 0 ? Math.round(data.totalScore / data.count) : 0;
    return {
      day: dateLabels[index],
      score: avgScore,
      words: data.count * 10 // Tahmini kelime sayısı
    };
  });

  const maxScore = 100;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 text-slate-50">
        <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
            <div className="flex items-center gap-2">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-sm text-slate-400 hover:text-slate-200"
              >
                ← Geri
              </button>
              <span className="rounded-md bg-indigo-500/10 px-2 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">
                İstatistikler
              </span>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-5xl px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50 mb-2">
              Performans İstatistikleri
            </h1>
            <p className="text-sm text-slate-400">
              Öğrenme ilerlemeni ve başarılarını takip et
            </p>
          </div>

          {/* Özet Kartlar */}
          <div className="grid gap-4 mb-8 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs text-slate-400 mb-1">Toplam Soru</p>
              <p className="text-2xl font-semibold text-slate-50">
                {stats.total_questions}
              </p>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs text-slate-400 mb-1">Doğru Cevap</p>
              <p className="text-2xl font-semibold text-emerald-400">
                {stats.total_correct}
              </p>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs text-slate-400 mb-1">Toplam Quiz</p>
              <p className="text-2xl font-semibold text-slate-50">
                {stats.total_quizzes}
              </p>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs text-slate-400 mb-1">Ortalama Skor</p>
              <p className="text-2xl font-semibold text-indigo-400">
                %{Math.round(stats.average_score)}
              </p>
            </div>
          </div>

          {/* Son 7 Gün Grafiği */}
          <div className="mb-8 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
            <h2 className="text-lg font-semibold text-slate-50 mb-6">
              Son 7 Gün Performansı
            </h2>
            {stats.total_quizzes === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-center">
                <p className="text-slate-400 mb-2">Henüz quiz tamamlamadınız</p>
                <p className="text-sm text-slate-500 mb-4">
                  İstatistiklerinizi görmek için quiz yapmaya başlayın!
                </p>
                <button
                  onClick={() => router.push("/practice/quiz")}
                  className="rounded-full bg-indigo-500 px-6 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
                >
                  Quiz'e Başla
                </button>
              </div>
            ) : (
              <div className="flex items-end justify-between gap-2 h-48">
                {last7Days.length > 0 ? (
                  last7Days.map((day, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div className="relative w-full flex flex-col items-center justify-end h-full">
                        <div
                          className="w-full rounded-t-lg bg-gradient-to-t from-indigo-500 to-indigo-400 mb-1 transition-all"
                          style={{
                            height: `${(day.score / maxScore) * 100}%`,
                            minHeight: "8px",
                          }}
                        />
                        <div
                          className="w-full rounded-t-lg bg-gradient-to-t from-emerald-500/60 to-emerald-400/60"
                          style={{
                            height: `${(day.words / 10) * 100}%`,
                            minHeight: "4px",
                          }}
                        />
                      </div>
                      <p className="text-xs text-slate-400 mt-2">{day.day}</p>
                      <p className="text-[10px] text-slate-500 mt-1">
                        %{day.score}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="w-full text-center text-slate-400 text-sm">
                    Son 7 günde quiz yapılmadı
                  </div>
                )}
              </div>
            )}
            <div className="flex items-center gap-4 mt-4 text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-indigo-500" />
                <span>Quiz Skoru</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-emerald-500/60" />
                <span>Kelime Sayısı</span>
              </div>
            </div>
          </div>

          {/* Kategori Bazlı Analiz - Şimdilik placeholder */}
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
            <h2 className="text-lg font-semibold text-slate-50 mb-6">
              Kategori Bazlı Başarı
            </h2>
            <div className="space-y-4">
              <p className="text-sm text-slate-400">
                Kategori bazlı analiz özelliği yakında eklenecek.
              </p>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}

