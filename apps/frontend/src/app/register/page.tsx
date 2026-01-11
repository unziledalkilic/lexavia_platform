"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterPage() {
  const router = useRouter();
  const { signUp } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { error } = await signUp(email, password, fullName);

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      setSuccess(true);
      // Email doğrulama gerekiyorsa kullanıcıya bilgi ver
      setTimeout(() => {
        router.push("/onboarding");
      }, 2000);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-6">
        <div className="w-full max-w-md text-center">
          <div className="rounded-3xl border border-emerald-800/50 bg-emerald-900/20 p-6">
            <p className="text-emerald-300 mb-2">✓ Hesabın oluşturuldu!</p>
            <p className="text-sm text-slate-400">
              Onboarding sayfasına yönlendiriliyorsun...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50 mb-2">
            Hesap oluştur
          </h1>
          <p className="text-sm text-slate-400">
            Lexavia'ya katıl ve kişisel öğrenme planını oluştur
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)] space-y-4"
        >
          {error && (
            <div className="rounded-xl border border-red-800/50 bg-red-900/20 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label
              htmlFor="fullName"
              className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300"
            >
              Ad Soyad
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-50 outline-none ring-0 focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
              placeholder="Ahmet Yılmaz"
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="email"
              className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300"
            >
              E-posta
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-50 outline-none ring-0 focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
              placeholder="ornek@email.com"
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300"
            >
              Şifre
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-50 outline-none ring-0 focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
              placeholder="••••••••"
            />
            <p className="text-[11px] text-slate-400">
              En az 6 karakter olmalı
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full bg-indigo-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Oluşturuluyor..." : "Hesap oluştur"}
          </button>

          <p className="text-center text-xs text-slate-400">
            Zaten hesabın var mı?{" "}
            <a
              href="/login"
              className="font-medium text-indigo-400 hover:text-indigo-300"
            >
              Giriş yap
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}

