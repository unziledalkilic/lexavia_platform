import { supabase } from "./supabase";

/**
 * API çağrıları için yardımcı fonksiyon.
 * Supabase session'dan token alır ve Authorization header'ına ekler.
 */
export async function apiFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const session = await supabase.auth.getSession();
  const token = session.data.session?.access_token;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    // eslint-disable-next-line no-console
    console.log("Token found, sending request with Authorization header");
  } else {
    // eslint-disable-next-line no-console
    console.warn("No token found in session. User may need to log in again.");
  }

  // eslint-disable-next-line no-console
  console.log("Request URL:", url);
  // eslint-disable-next-line no-console
  console.log("Request headers:", { ...headers, Authorization: token ? "Bearer ***" : "None" });

  return fetch(url, {
    ...options,
    headers,
  });
}


// ==================== ML / QUIZ TYPES ====================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export interface QuizGenerationRequest {
  word: string;
  level: string;
  category?: string;
  translation?: string;
}

export interface QuizGenerationResponse {
  question_text: string;
  question_type: string;
  correct_answer: string;
  options: string; // JSON string
  level: string;
  category: string;
  explanation: string;
}

export interface ExampleSentenceRequest {
  word: string;
  level: string;
}

export interface ExampleSentenceResponse {
  word: string;
  level: string;
  example_sentence: string;
}

export interface ReviewScheduleResponse {
  word_id: number;
  user_id: string;
  next_review: string; // ISO datetime
  interval: number;
  repetitions: number;
  easiness_factor: number;
}

export interface CreateReviewScheduleRequest {
  word_id: number;
  user_id: string;
}

export interface UpdateReviewScheduleRequest {
  word_id: number;
  user_id: string;
  quality: number; // 0-5
  current_interval?: number;
  current_repetitions?: number;
  current_easiness?: number;
}

export interface CalculateQualityRequest {
  was_correct: boolean;
  time_taken_seconds?: number;
  avg_time_seconds?: number;
}

export interface CalculateQualityResponse {
  quality: number;
  description: string;
}

export interface DueReviewItem {
  word_id: number;
  word: string;
  translation: string;
  next_review: string;
  interval: number;
  repetitions: number;
}

// ==================== ML / QUIZ FUNCTIONS ====================

/**
 * AI ile quiz sorusu üret
 */
export async function generateQuiz(
  request: QuizGenerationRequest
): Promise<QuizGenerationResponse> {
  const response = await apiFetch(`${API_BASE_URL}/api/ml/generate-quiz`, {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Quiz generation failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * AI ile örnek cümle üret
 */
export async function generateExampleSentence(
  request: ExampleSentenceRequest
): Promise<ExampleSentenceResponse> {
  const response = await apiFetch(`${API_BASE_URL}/api/ml/generate-example`, {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Example generation failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Yeni kelime için review schedule oluştur
 */
export async function createReviewSchedule(
  request: CreateReviewScheduleRequest
): Promise<ReviewScheduleResponse> {
  const response = await apiFetch(`${API_BASE_URL}/api/ml/create-review-schedule`, {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Create review schedule failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Review schedule'ı performansa göre güncelle
 */
export async function updateReviewSchedule(
  request: UpdateReviewScheduleRequest
): Promise<ReviewScheduleResponse> {
  const response = await apiFetch(`${API_BASE_URL}/api/ml/update-review-schedule`, {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Update review schedule failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Quiz performansını quality skoruna çevir
 */
export async function calculateQuality(
  request: CalculateQualityRequest
): Promise<CalculateQualityResponse> {
  const response = await apiFetch(`${API_BASE_URL}/api/ml/calculate-quality`, {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Calculate quality failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Kullanıcının bugün tekrar etmesi gereken kelimeleri getir
 */
export async function getDueReviews(userId: string): Promise<DueReviewItem[]> {
  const response = await apiFetch(`${API_BASE_URL}/api/ml/due-reviews/${userId}`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`Fetch due reviews failed: ${response.statusText}`);
  }

  return response.json();
}
