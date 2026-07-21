/**
 * 阅读进度 API
 */

import { apiGet, apiPut, apiDelete } from "./api";

export interface ReadingProgress {
  book_id: number;
  spine_index: number;
  content_id: number;
  scroll_percent: number;
  updated_at: string;
}

export async function getReadingProgress(
  bookId: number,
): Promise<ReadingProgress | null> {
  const response = await apiGet<{ code: number; data: ReadingProgress | null }>(
    `/reading/progress/${bookId}`,
  );
  return response.data;
}

export async function saveReadingProgress(
  bookId: number,
  progress: {
    spine_index: number;
    content_id: number;
    scroll_percent: number;
  },
): Promise<ReadingProgress> {
  const response = await apiPut<{ code: number; data: ReadingProgress }>(
    `/reading/progress/${bookId}`,
    progress,
  );
  return response.data;
}

export async function clearReadingProgress(bookId: number): Promise<void> {
  await apiDelete(`/reading/progress/${bookId}`);
}
