/**
 * User Stats Utility
 * 
 * Kullanıcı performans istatistiklerini hesaplayan utility fonksiyonlar
 * ML modeli için gerekli verileri hazırlar
 */

export interface UserStats {
    avg_score: number;
    total_quizzes: number;
    grammar_accuracy: number;
    vocabulary_accuracy: number;
    avg_completion_time?: number;
    streak_days?: number;
}

export interface QuizResult {
    score: number;
    total_questions: number;
    correct_answers: number;
    category: string;
    completion_time_seconds?: number;
    completed_at: Date;
}

/**
 * Quiz sonuçlarından kullanıcı istatistiklerini hesapla
 */
export function calculateUserStats(quizResults: QuizResult[]): UserStats {
    if (quizResults.length === 0) {
        return {
            avg_score: 0,
            total_quizzes: 0,
            grammar_accuracy: 0,
            vocabulary_accuracy: 0,
            avg_completion_time: 0,
            streak_days: 0
        };
    }

    // Ortalama skor
    const avgScore = quizResults.reduce((sum, r) => sum + r.score, 0) / quizResults.length;

    // Kategori bazlı doğruluk
    const grammarQuizzes = quizResults.filter(r => r.category === 'grammar');
    const vocabularyQuizzes = quizResults.filter(r => r.category === 'vocabulary');

    const grammarAccuracy = grammarQuizzes.length > 0
        ? grammarQuizzes.reduce((sum, r) => sum + r.score, 0) / grammarQuizzes.length
        : 0;

    const vocabularyAccuracy = vocabularyQuizzes.length > 0
        ? vocabularyQuizzes.reduce((sum, r) => sum + r.score, 0) / vocabularyQuizzes.length
        : 0;

    // Ortalama tamamlama süresi
    const resultsWithTime = quizResults.filter(r => r.completion_time_seconds);
    const avgCompletionTime = resultsWithTime.length > 0
        ? resultsWithTime.reduce((sum, r) => sum + (r.completion_time_seconds || 0), 0) / resultsWithTime.length
        : undefined;

    // Streak hesaplama (son 7 gün içindeki ardışık günler)
    const streakDays = calculateStreakDays(quizResults.map(r => r.completed_at));

    return {
        avg_score: Math.round(avgScore * 100) / 100,
        total_quizzes: quizResults.length,
        grammar_accuracy: Math.round(grammarAccuracy * 100) / 100,
        vocabulary_accuracy: Math.round(vocabularyAccuracy * 100) / 100,
        avg_completion_time: avgCompletionTime ? Math.round(avgCompletionTime) : undefined,
        streak_days: streakDays
    };
}

/**
 * Ardışık gün sayısını hesapla
 */
function calculateStreakDays(dates: Date[]): number {
    if (dates.length === 0) return 0;

    // Tarihleri sırala (yeniden eskiye)
    const sortedDates = dates
        .map(d => new Date(d.getFullYear(), d.getMonth(), d.getDate()))
        .sort((a, b) => b.getTime() - a.getTime());

    let streak = 1;
    let currentDate = sortedDates[0];

    for (let i = 1; i < sortedDates.length; i++) {
        const prevDate = new Date(currentDate);
        prevDate.setDate(prevDate.getDate() - 1);

        if (sortedDates[i].getTime() === prevDate.getTime()) {
            streak++;
            currentDate = sortedDates[i];
        } else {
            break;
        }
    }

    return streak;
}

/**
 * LocalStorage'dan quiz sonuçlarını yükle
 */
export function loadQuizResults(userId: string): QuizResult[] {
    if (typeof window === 'undefined') return [];

    try {
        const key = `quiz_results_${userId}`;
        const stored = localStorage.getItem(key);
        if (!stored) return [];

        const results = JSON.parse(stored);
        return results.map((r: any) => ({
            ...r,
            completed_at: new Date(r.completed_at)
        }));
    } catch (error) {
        console.error('Failed to load quiz results:', error);
        return [];
    }
}

/**
 * Quiz sonucunu LocalStorage'a kaydet
 */
export function saveQuizResult(userId: string, result: QuizResult): void {
    if (typeof window === 'undefined') return;

    try {
        const key = `quiz_results_${userId}`;
        const existing = loadQuizResults(userId);
        const updated = [...existing, result];

        // Son 100 quiz'i sakla
        const limited = updated.slice(-100);

        localStorage.setItem(key, JSON.stringify(limited));
    } catch (error) {
        console.error('Failed to save quiz result:', error);
    }
}

/**
 * Kullanıcı istatistiklerini LocalStorage'dan yükle ve hesapla
 */
export function getUserStats(userId: string): UserStats {
    const results = loadQuizResults(userId);
    return calculateUserStats(results);
}
