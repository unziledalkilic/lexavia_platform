/**
 * Review Schedule Widget
 * 
 * Bugün tekrar edilmesi gereken kelimeleri gösteren component
 * SM-2 spaced repetition algoritması ile optimal öğrenme
 */

import { useEffect, useState } from 'react';

import { getDueReviews, DueReviewItem } from '@/lib/api';

interface ReviewScheduleWidgetProps {
    userId: string;
}

export function ReviewScheduleWidget({ userId }: ReviewScheduleWidgetProps) {

    const [dueReviews, setDueReviews] = useState<DueReviewItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchReviews() {
            try {
                // Backend'den gerçek review verisi çek (veya mock fallback)
                const reviews = await getDueReviews(userId);
                setDueReviews(reviews);
            } catch (error) {
                console.error("Failed to fetch due reviews:", error);
            } finally {
                setLoading(false);
            }
        }

        if (userId) {
            fetchReviews();
        }
    }, [userId]);

    if (loading) {
        return (
            <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
                <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                    <p className="text-xs text-slate-400">Tekrarlar yükleniyor...</p>
                </div>
            </div>
        );
    }

    if (dueReviews.length === 0) {
        return (
            <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
                <div className="flex items-center gap-2 mb-3">
                    <div className="h-2 w-2 rounded-full bg-emerald-400" />
                    <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300">
                        Önerilen Tekrarlar
                    </p>
                </div>
                <p className="text-sm text-slate-400">
                    🎉 Harika! Bugün için tekrar edilecek kelimen yok.
                    Yeni çalışmalara devam edebilirsin!
                </p>
            </div>
        );
    }

    return (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.9)]">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-emerald-400" />
                    <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-300">
                        Bugünkü Tekrarlar
                    </p>
                </div>
                <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-300">
                    {dueReviews.length} kelime
                </span>
            </div>

            {/* Review List */}
            <div className="space-y-2">
                {dueReviews.map((review) => (
                    <div
                        key={review.word_id}
                        className="flex items-center justify-between rounded-xl border border-slate-800/80 bg-slate-950/60 p-3 hover:border-emerald-500/30 transition-colors"
                    >
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <p className="font-semibold text-slate-50">{review.word}</p>
                                <span className="text-xs text-slate-500">→</span>
                                <p className="text-sm text-slate-400">{review.translation}</p>
                            </div>
                            <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
                                <span>
                                    🔄 {review.repetitions}. tekrar
                                </span>
                                <span>•</span>
                                <span>
                                    📅 {review.interval} gün aralık
                                </span>
                            </div>
                        </div>

                        <button
                            onClick={() => window.location.href = `/practice/quiz?mode=review&word_id=${review.word_id}&word=${encodeURIComponent(review.word)}&translation=${encodeURIComponent(review.translation)}`}
                            className="rounded-full bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-400 transition-colors"
                        >
                            Çalış
                        </button>
                    </div>
                ))}
            </div>

            {/* Info */}
            <div className="mt-4 rounded-xl border border-indigo-800/30 bg-indigo-900/10 p-3">
                <p className="text-xs text-indigo-300">
                    💡 <span className="font-semibold">Aralıklı Tekrar Sistemi</span> ile kelimeler hafızanda
                    kalıcı hale gelir. Her başarılı tekrar sonrası aralık otomatik olarak uzar.
                </p>
            </div>
        </div>
    );
}
