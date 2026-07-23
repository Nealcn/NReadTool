/** 高亮/笔记 API */

import { apiGet, apiPost, apiPut, apiDelete } from "./api";

export interface AnnotationData {
  cfi: string;
  type: "highlight" | "note" | "bookmark";
  style?: string;
  color?: string;
  text?: string;
  note?: string;
}

export interface AnnotationResponse extends AnnotationData {
  id: number;
  book_hash: string;
  device_id: string;
  created_at: string;
  updated_at: string;
}

export async function createAnnotation(bookHash: string, data: AnnotationData): Promise<AnnotationResponse> {
  const res = await apiPost<{ code: number; data: AnnotationResponse }>(`/books/${bookHash}/annotations`, data);
  return res.data;
}

export async function listAnnotations(bookHash: string): Promise<AnnotationResponse[]> {
  const res = await apiGet<{ code: number; data: AnnotationResponse[] }>(`/books/${bookHash}/annotations`);
  return res.data;
}

export async function updateAnnotation(id: number, data: { style?: string; color?: string; note?: string }): Promise<AnnotationResponse> {
  const res = await apiPut<{ code: number; data: AnnotationResponse }>(`/annotations/${id}`, data);
  return res.data;
}

export async function deleteAnnotation(id: number): Promise<void> {
  await apiDelete(`/annotations/${id}`);
}
