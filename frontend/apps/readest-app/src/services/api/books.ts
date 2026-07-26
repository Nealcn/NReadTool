/**
 * 书籍管理 API — 主键改为 file_hash
 */

import { apiGet, apiPost, apiPut, apiDelete } from "./api";

export interface BookInfo {
  file_hash: string;
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

export async function uploadBook(file: File): Promise<BookInfo> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiPost<{ code: number; data: BookInfo }>(
    "/books/upload", formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return response.data;
}

export async function getBookList(): Promise<BookListResponse> {
  const response = await apiGet<{ code: number; data: BookListResponse }>("/books");
  return response.data;
}

export async function getBookDetail(bookHash: string): Promise<BookDetail> {
  const response = await apiGet<{ code: number; data: BookDetail }>(`/books/${bookHash}`);
  return response.data;
}

export async function renameBook(bookHash: string, title: string): Promise<BookInfo> {
  const response = await apiPut<{ code: number; data: BookInfo }>(`/books/${bookHash}`, { title });
  return response.data;
}

export async function deleteBook(bookHash: string): Promise<void> {
  await apiDelete(`/books/${bookHash}`);
}

export interface BookMetadataUpdate {
  title?: string;
  author?: string;
  publisher?: string;
  language?: string;
  isbn?: string;
  description?: string;
  cover_image?: string;
}

export async function updateBookMetadata(bookHash: string, data: BookMetadataUpdate): Promise<BookDetail> {
  const response = await apiPut<{ code: number; data: BookDetail }>(`/books/${bookHash}/metadata`, data);
  return response.data;
}

export async function getBookTOC(bookHash: string): Promise<{ book_hash: string; items: TOCItem[] }> {
  const response = await apiGet<{ code: number; data: { book_hash: string; items: TOCItem[] } }>(`/books/${bookHash}/toc`);
  return response.data;
}

export async function getChapterContent(bookHash: string, contentId: number): Promise<ChapterContent> {
  const response = await apiGet<{ code: number; data: ChapterContent }>(`/books/${bookHash}/contents/${contentId}`);
  return response.data;
}
