export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-indigo-500/10 px-2 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">
              Lexavia
            </span>
            <span className="text-sm text-slate-400">
              AI destekli dil öğrenme platformu
            </span>
          </div>
          <nav className="hidden items-center gap-4 text-sm text-slate-300 sm:flex">
            <a
              href="/login"
              className="rounded-full border border-slate-700 px-4 py-1.5 text-xs font-medium hover:border-slate-500 hover:text-slate-100"
            >
              Giriş yap
            </a>
            <a
              href="/register"
              className="rounded-full bg-indigo-500 px-4 py-1.5 text-xs font-semibold text-white shadow-lg shadow-indigo-500/30 hover:bg-indigo-400"
            >
              Hemen başla
            </a>
          </nav>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-12 px-6 pb-24 pt-14 md:flex-row md:items-center md:gap-16">
        <section className="flex-1 space-y-6">
          <p className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1 text-xs font-medium text-slate-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Kişiselleştirilmiş plan · Aralıklı tekrar · AI analiz
          </p>
          <h1 className="text-balance text-4xl font-semibold tracking-tight text-slate-50 sm:text-5xl">
            İngilizceyi{" "}
            <span className="bg-gradient-to-r from-indigo-400 via-sky-400 to-emerald-400 bg-clip-text text-transparent">
              sana özel
            </span>{" "}
            planlarla öğren.
          </h1>
          <p className="max-w-xl text-pretty text-sm leading-relaxed text-slate-300 sm:text-base">
            Lexavia, günlük çalışma sürene ve seviyene göre akıllı bir çalışma
            planı oluşturur. Zayıf kaldığın kelime ve dilbilgisi konularını
            tespit ederek aralıklı tekrar ile kalıcı öğrenmeni sağlar.
          </p>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <a
              href="/register"
              className="inline-flex items-center justify-center rounded-full bg-indigo-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 hover:bg-indigo-400"
            >
              Hemen başla (ücretsiz)
            </a>
            <a
              href="/login"
              className="inline-flex items-center justify-center rounded-full border border-slate-700 px-5 py-2 text-sm font-medium text-slate-200 hover:border-slate-500 hover:text-slate-50"
            >
              Giriş yap
            </a>
          </div>

          <div className="mt-4 grid gap-3 text-xs text-slate-300 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-3">
              <p className="font-semibold text-slate-50">Kişisel çalışma planı</p>
              <p className="mt-1 text-[11px] text-slate-400">
                Seviye, hedef ve günlük süreye göre otomatik haftalık plan.
              </p>
            </div>
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-3">
              <p className="font-semibold text-slate-50">Zayıf nokta analizi</p>
              <p className="mt-1 text-[11px] text-slate-400">
                Kelime ve dilbilgisi kategorilerine göre performans raporu.
              </p>
            </div>
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-3">
              <p className="font-semibold text-slate-50">Aralıklı tekrar</p>
              <p className="mt-1 text-[11px] text-slate-400">
                1-3-7 gün tekrar mantığı ile unutmayı minimuma indirir.
              </p>
            </div>
          </div>
        </section>

        <section className="flex-1">
          <div className="relative rounded-3xl border border-slate-800 bg-slate-900/70 p-5 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
            <div className="mb-4 flex items-center justify-between text-xs text-slate-300">
              <span className="font-medium">Bugünkü planın</span>
              <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
                24 dakikalık çalışma
              </span>
            </div>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5">
                <div>
                  <p className="font-semibold text-slate-50">
                    Kelime kartları · B1
                  </p>
                  <p className="text-[11px] text-slate-400">
                    15 yeni kelime · 10 tekrar · 12 dk
                  </p>
                </div>
                <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[11px] text-slate-200">
                  Başla
                </span>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/40 px-3 py-2.5">
                <div>
                  <p className="font-semibold text-slate-50">
                    Dilbilgisi · Present Perfect
                  </p>
                  <p className="text-[11px] text-slate-400">
                    5 soru · hedef doğruluk %80
                  </p>
                </div>
                <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[11px] text-slate-200">
                  Çöz
                </span>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-gradient-to-r from-indigo-900/60 via-slate-900/80 to-emerald-900/60 px-3 py-3">
                <p className="text-[11px] uppercase tracking-[0.16em] text-indigo-300">
                  AI analizi
                </p>
                <p className="mt-1 text-xs text-slate-100">
                  Son 7 günde{" "}
                  <span className="font-semibold text-emerald-300">
                    fiillerde %68 doğruluk
                  </span>{" "}
                  yakaladın. Bugün fiil kartlarına ağırlık vermeni öneriyoruz.
          </p>
              </div>
        </div>
        </div>
        </section>
      </main>
    </div>
  );
}
