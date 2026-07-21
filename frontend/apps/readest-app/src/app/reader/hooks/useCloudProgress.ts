/**
 * 云端进度同步 Hook
 * 将阅读进度同步到自研后端 API
 */

import { useEffect, useRef, useCallback } from "react";
import { useBookProgress } from "@/store/readerProgressStore";
import { saveReadingProgress } from "@/services/api/reading";
import { getDeviceId } from "@/utils/device";
import { debounce } from "@/utils/debounce";

const CLOUD_BOOK_MAP_KEY = "cloud_book_map";

// 存储 cloud book id 映射 (bookKey -> cloudBookId)
export function storeCloudBookId(bookKey: string, cloudBookId: number) {
  try {
    const map = JSON.parse(
      localStorage.getItem(CLOUD_BOOK_MAP_KEY) || "{}"
    );
    map[bookKey] = cloudBookId;
    localStorage.setItem(CLOUD_BOOK_MAP_KEY, JSON.stringify(map));
  } catch {
    // ignore
  }
}

function getCloudBookId(bookKey: string): number | null {
  try {
    const map = JSON.parse(
      localStorage.getItem(CLOUD_BOOK_MAP_KEY) || "{}"
    );
    return map[bookKey] ?? null;
  } catch {
    return null;
  }
}

export function useCloudProgress(bookKey: string, cloudBookId?: number) {
  const progress = useBookProgress(bookKey);
  const lastFractionRef = useRef<number>(-1);

  // 注册 cloudBookId（如果传入）
  useEffect(() => {
    if (cloudBookId) {
      storeCloudBookId(bookKey, cloudBookId);
    }
  }, [bookKey, cloudBookId]);

  // 节流同步到后端
  const syncProgress = useCallback(
    debounce(async () => {
      const cid = getCloudBookId(bookKey);
      if (!cid) return; // 不是从云端导入的书，跳过

      const p = useBookProgress(bookKey);
      if (!p) return;

      const fraction = p.fraction ?? 0;
      if (Math.abs(fraction - lastFractionRef.current) < 0.01) return; // 变化太小跳过
      lastFractionRef.current = fraction;

      try {
        await saveReadingProgress(cid, {
          spine_index: 0,
          content_id: 0,
          scroll_percent: fraction,
        });
      } catch {
        // 静默失败
      }
    }, 3000), // 3s 节流
    [bookKey],
  );

  useEffect(() => {
    syncProgress();
  }, [progress, syncProgress]);
}
