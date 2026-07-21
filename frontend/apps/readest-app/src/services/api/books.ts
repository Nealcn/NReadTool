/**
 * 书籍管理 API
 */

import { apiGet, apiPost, apiPut, apiDelete } from "./api";

export interface BookInfo {
  id: number;
  title: string;
  author?: string;
  cover_image?: string;
  file_size: number;
  total_chapters: number;
  total_words: number;
  created_at: string;
}

export interface BookDetail extends BookInfo {
  publisher?: string;
  language?: string;
  isbn?: string;
  description?: string;
  file_name: string;
  updated_at: string;
}

export interface TOCItem {
  spine_index: number;
  content_id: number;
  title: string;
}

export interface ChapterContent {
  spine_index: number;
  title?: string;
  html_content: string;
}

export interface BookListResponse {
  books: BookInfo[];
  total: number;
}

export async function uploadBook(
  file: File,
  deviceId: string,
  onProgress?: (percent: number) => void,
): Promise<BookInfo> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("device_id", deviceId);

  const response = await apiPost<{ code: number; data: BookInfo }>(
    "/books/upload",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: onProgress
        ? (e) => {
            if (e.total) {
              onProgress(Math.round((e.loaded * 100) / e.total));
            }
          }
        : undefined,
    },
  );
  return response.data;
}

export async function getBookList(deviceId: string): Promise<BookListResponse> {
  const response = await apiPost<{ code: number; data: BookListResponse }>(
    "/books",
    { device_id: deviceId },
  );
  return response.data;
}

export async function getBookDetail(bookId: number): Promise<BookDetail> {
  const response = await apiGet<{ code: number; data: BookDetail }>(
    `/books/${bookId}`,
  );
  return response.data;
}

export async function renameBook(
  bookId: number,
  title: string,
): Promise<BookInfo> {
  const response = await apiPut<{ code: number; data: BookInfo }>(
    `/books/${bookId}`,
    { title },
  );
  return response.data;
}

export async function deleteBook(bookId: number): Promise<void> {
  await apiDelete(`/books/${bookId}`);
}

export async function getBookTOC(
  bookId: number,
): Promise<{ book_id: number; items: TOCItem[] }> {
  const response = await apiGet<{
    code: number;
    data: { book_id: number; items: TOCItem[] };
  }>(`/books/${bookId}/toc`);
  return response.data;
}

export async function getChapterContent(
  bookId: number,
  contentId: number,
): Promise<ChapterContent> {
  const response = await apiGet<{ code: number; data: ChapterContent }>(
    `/books/${bookId}/contents/${contentId}`,
  );
  return response.data;
}
