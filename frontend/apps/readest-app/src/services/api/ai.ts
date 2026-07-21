/**
 * AI 划词 API
 */

import { apiPost, apiGet } from "./api";

export type AIExplainType = "word" | "sentence" | "grammar" | "background";

export interface AIExplainRequest {
  text: string;
  type: AIExplainType;
  book_id?: number;
  chapter_title?: string;
}

export interface AIExplainResponse {
  explanation: string;
  type: string;
  model: string;
}

export interface AIHealthResponse {
  available: boolean;
}

export async function aiExplain(
  req: AIExplainRequest,
): Promise<AIExplainResponse> {
  const response = await apiPost<{ code: number; data: AIExplainResponse }>(
    "/ai/explain",
    req,
  );
  return response.data;
}

export async function aiHealth(): Promise<AIHealthResponse> {
  const response = await apiGet<{ code: number; data: AIHealthResponse }>(
    "/ai/health",
  );
  return response.data;
}
