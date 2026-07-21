/**
 * AI 划词 Hook
 * 处理文本选中、截断、API 调用等逻辑
 */

"use client";

import { useState, useCallback, useRef } from "react";
import { aiExplain, type AIExplainRequest, type AIExplainType } from "@/services/api/ai";

const MAX_AI_TEXT_LENGTH = 2000;

interface AIState {
  isVisible: boolean;
  isLoading: boolean;
  selectedText: string;
  isTruncated: boolean;
  explanation: string;
  error: string | null;
  position: { x: number; y: number };
  explainType: AIExplainType;
}

export function useAI() {
  const [state, setState] = useState<AIState>({
    isVisible: false,
    isLoading: false,
    selectedText: "",
    isTruncated: false,
    explanation: "",
    error: null,
    position: { x: 0, y: 0 },
    explainType: "word",
  });

  const abortRef = useRef<AbortController | null>(null);

  const handleTextSelection = useCallback(
    (selectionText: string, type: AIExplainType = "sentence") => {
      let text = selectionText.trim();
      let isTruncated = false;

      if (!text) return;

      // 2000 字截断
      if (text.length > MAX_AI_TEXT_LENGTH) {
        text = text.substring(0, MAX_AI_TEXT_LENGTH);
        isTruncated = true;
      }

      setState((prev) => ({
        ...prev,
        isVisible: true,
        isLoading: false,
        selectedText: text,
        isTruncated,
        explanation: "",
        error: null,
        explainType: type,
      }));
    },
    [],
  );

  const requestExplanation = useCallback(
    async (
      text: string,
      type: AIExplainType = "sentence",
      bookId?: number,
      chapterTitle?: string,
    ) => {
      // 取消之前的请求
      if (abortRef.current) {
        abortRef.current.abort();
      }

      const controller = new AbortController();
      abortRef.current = controller;

      setState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      try {
        const result = await aiExplain({
          text: text.substring(0, MAX_AI_TEXT_LENGTH),
          type,
          book_id: bookId,
          chapter_title: chapterTitle,
        });

        if (!controller.signal.aborted) {
          setState((prev) => ({
            ...prev,
            isLoading: false,
            explanation: result.explanation,
            error: null,
          }));
        }
      } catch (err: unknown) {
        if (!controller.signal.aborted) {
          const errorMessage =
            err instanceof Error
              ? err.message
              : (err as { message?: string })?.message || "AI 服务暂不可用";
          setState((prev) => ({
            ...prev,
            isLoading: false,
            error: errorMessage,
          }));
        }
      }
    },
    [],
  );

  const closeAI = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    setState((prev) => ({
      ...prev,
      isVisible: false,
      isLoading: false,
      explanation: "",
      error: null,
    }));
  }, []);

  const setPosition = useCallback((x: number, y: number) => {
    setState((prev) => ({ ...prev, position: { x, y } }));
  }, []);

  return {
    ...state,
    handleTextSelection,
    requestExplanation,
    closeAI,
    setPosition,
  };
}
