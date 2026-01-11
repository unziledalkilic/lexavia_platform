"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/api";

const levels = ["A1", "A2", "B1", "B2", "C1", "C2"] as const;
const dailyOptions = [10, 20, 30, 45, 60];

export default function OnboardingPage() {
  const [level, setLevel] = useState<(typeof levels)[number]>("B1");
  const [dailyMinutes, setDailyMinutes] = useState<number>(20);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget as HTMLFormElement);
    const rawPayload = Object.fromEntries(formData.entries());

    // daily_minutes'ı integer'a çevir
    const payload = {
      ...rawPayload,
      daily_minutes: parseInt(rawPayload.daily_minutes as string, 10),
      focus_topics: rawPayload.focus_topics || null,
    };

    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/onboarding`;
      // eslint-disable-next-line no-console
      console.log("Sending request to:", apiUrl);
      // eslint-disable-next-line no-console
      console.log("Payload:", payload);
      
      const res = await apiFetch(apiUrl, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        // eslint-disable-next-line no-console
        console.error("Backend error:", errorData);
        throw new Error(
          errorData.detail || "Plan oluşturulurken bir hata oluştu.",
        );
      }

      const result = await res.json();
      // eslint-disable-next-line no-console
      console.log("onboarding created", result);
      // Dashboard'a yönlendir
      window.location.href = "/dashboard";
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error(error);
      alert(
        error instanceof Error
          ? error.message
          : "Plan oluşturulurken bir hata oluştu.",
      );
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 text-slate-50">
      <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
        <header className="mb-10 space-y-3">
          <p className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-3 py-1 text-xs font-medium text-slate-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Adım 1 · Hedefini belirle
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50 sm:text-4xl">
            Lexavia senin için kişisel bir plan oluştursun.
          </h1>
          <p className="max-w-xl text-sm text-slate-300 sm:text-base">
            Günlük ayırabileceğin süreyi, mevcut seviyeni ve öğrenme amacını
            seç. Bu bilgiler, kelime ve dilbilgisi hedeflerini ve tekrar
            sıklığını ayarlamak için kullanılacak.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="space-y-8 rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)] sm:p-8"
        >
          <div className="grid gap-6 sm:grid-cols-2">
            <div className="space-y-2">
              <label
                htmlFor="target_language"
                className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300"
              >
                Hedef dil
              </label>
              <select
                id="target_language"
                name="target_language"
                defaultValue="en"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-50 outline-none ring-0 focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
              >
                <option value="en">İngilizce</option>
                {/* İleride diğer diller eklenecek */}
              </select>
              <p className="text-[11px] text-slate-400">
                İlk sürüm İngilizce odaklı; daha sonra yeni diller eklenebilir.
              </p>
            </div>

            <div className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300">
                Mevcut seviyen
              </span>
              <div className="grid grid-cols-3 gap-2">
                {levels.map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setLevel(lvl)}
                    className={`rounded-xl border px-3 py-2 text-sm font-semibold ${
                      level === lvl
                        ? "border-indigo-400 bg-indigo-500/20 text-indigo-100"
                        : "border-slate-700 bg-slate-950 text-slate-200 hover:border-slate-500"
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
              <input type="hidden" name="level" value={level} />
            </div>
          </div>

          <div className="grid gap-6 sm:grid-cols-[1.2fr_minmax(0,1fr)]">
            <div className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300">
                Günlük çalışma süresi
              </span>
              <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
                {dailyOptions.map((min) => (
                  <button
                    key={min}
                    type="button"
                    onClick={() => setDailyMinutes(min)}
                    className={`rounded-xl border px-3 py-2 text-xs font-medium ${
                      dailyMinutes === min
                        ? "border-emerald-400 bg-emerald-500/15 text-emerald-100"
                        : "border-slate-700 bg-slate-950 text-slate-200 hover:border-slate-500"
                    }`}
                  >
                    {min} dk
                  </button>
                ))}
              </div>
              <input
                type="hidden"
                name="daily_minutes"
                value={dailyMinutes}
              />
              <p className="text-[11px] text-slate-400">
                Gerçekçi bir süre seçmen, tekrar planının daha isabetli
                olmasını sağlar.
              </p>
            </div>

            <div className="space-y-2">
              <label
                htmlFor="goal_type"
                className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300"
              >
                Öğrenme amacın
              </label>
              <select
                id="goal_type"
                name="goal_type"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-50 outline-none ring-0 focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
              >
                <option value="general">Genel İngilizce</option>
                <option value="exam">Sınav hazırlık (YDS, TOEFL vb.)</option>
                <option value="speaking">Konuşma pratiği</option>
                <option value="career">Kariyer / iş İngilizcesi</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label
              htmlFor="focus_topics"
              className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300"
            >
              Özellikle geliştirmek istediğin alanlar
            </label>
            <textarea
              id="focus_topics"
              name="focus_topics"
              rows={3}
              placeholder="Örn: Kelime bilgisi, zamanlar, okuma pratiği..."
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-50 outline-none ring-0 placeholder:text-slate-500 focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
            />
            <p className="text-[11px] text-slate-400">
              Bu alan zorunlu değil; ama AI analiz modülü için ek bağlam sağlar.
            </p>
          </div>

          <div className="flex items-center justify-between pt-4">
            <p className="text-[11px] text-slate-400">
              Bu ayarları daha sonra profilinden değiştirebileceksin.
            </p>
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-full bg-indigo-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 hover:bg-indigo-400"
            >
              Devam et
            </button>
          </div>
        </form>
      </main>
    </div>
    </ProtectedRoute>
  );
}


