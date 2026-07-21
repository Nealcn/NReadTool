/**
 * 阅读进度自动保存/恢复 Hook
 * 云端 + 本地缓存双重策略
 */

"use client";

import { useEffect, useRef, useCallback } from "react";
import {
  getReadingProgress,
  saveReadingProgress,
} from "@/services/api/reading";

const SAVE_THROTTLE_MS = 2000;
const LOCAL_CACHE_KEY_PREFIX = "reading_progress_";

interface ProgressData {
  book_id: number;
  spine_index: number;
  content_id: number;
  scroll_percent: number;
}

function getLocalCacheKey(bookId: number) {
  return `${LOCAL_CACHE_KEY_PREFIX}${bookId}`;
}

function getLocalProgress(bookId: number): ProgressData | null {
  try {
    const cached = localStorage.getItem(getLocalCacheKey(bookId));
    if (cached) {
      return JSON.parse(cached);
    }
  } catch {
    // ignore
  }
  return null;
}

function setLocalProgress(bookId: number, progress: ProgressData) {
  try {
    localStorage.setItem(getLocalCacheKey(bookId), JSON.stringify(progress));
  } catch {
    // ignore
  }
}

function removeLocalProgress(bookId: number) {
  try {
    localStorage.removeItem(getLocalCacheKey(bookId));
  } catch {
    // ignore
  }
}

export function useReadingProgress(bookId: number) {
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const currentProgressRef = useRef<ProgressData | null>(null);

  // 加载进度：云端优先，本地兜底
  const loadProgress = useCallback(async () => {
    try {
      const cloudProgress = await getReadingProgress(bookId);
      if (cloudProgress) {
        currentProgressRef.current = {
          book_id: cloudProgress.book_id,
          spine_index: cloudProgress.spine_index,
          content_id: cloudProgress.content_id,
          scroll_percent: cloudProgress.scroll_percent,
        };
        return cloudProgress;
      }
    } catch {
      // 云端加载失败，尝试本地缓存
    }

    const localProgress = getLocalProgress(bookId);
    if (localProgress) {
      currentProgressRef.current = localProgress;
      return localProgress;
    }

    return null;
  }, [bookId]);

  // 自动保存（节流 2s）
  const saveProgress = useCallback(
    async (progress: ProgressData) => {
      currentProgressRef.current = progress;

      // 更新本地缓存
      setLocalProgress(bookId, progress);

      // 节流保存到云端
      if (saveTimerRef.current) {
        clearTimeout(saveTimerRef.current);
      }

      saveTimerRef.current = setTimeout(async () => {
        try {
          await saveReadingProgress(bookId, {
            spine_index: progress.spine_index,
            content_id: progress.content_id,
            scroll_percent: progress.scroll_percent,
          });
        } catch {
          // 云端保存失败，本地缓存已保存，下次打开会重试
        }
      }, SAVE_THROTTLE_MS);
    },
    [bookId],
  );

  // 立即保存（翻页时调用）
  const saveProgressNow = useCallback(
    async (progress: ProgressData) => {
      currentProgressRef.current = progress;
      setLocalProgress(bookId, progress);

      try {
        await saveReadingProgress(bookId, {
          spine_index: progress.spine_index,
          content_id: progress.content_id,
          scroll_percent: progress.scroll_percent,
        });
      } catch {
        // 静默失败
      }
    },
    [bookId],
  );

  // 清除进度
  const clearProgress = useCallback(() => {
    removeLocalProgress(bookId);
  }, [bookId]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (saveTimerRef.current) {
        clearTimeout(saveTimerRef.current);
      }
      // 组件卸载时尝试保存最新进度
      if (currentProgressRef.current) {
        saveReadingProgress(bookId, {
          spine_index: currentProgressRef.current.spine_index,
          content_id: currentProgressRef.current.content_id,
          scroll_percent: currentProgressRef.current.scroll_percent,
        }).catch(() => {});
      }
    };
  }, [bookId]);

  return {
    loadProgress,
    saveProgress,
    saveProgressNow,
    clearProgress,
  };
}
