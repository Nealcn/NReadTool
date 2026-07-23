/**
 * 云端进度同步 Hook
 * 使用 file_hash 直接同步到后端（无需映射）
 */

import { useEffect, useRef, useCallback } from "react";
import { useBookProgress } from "@/store/readerProgressStore";
import { saveReadingProgress } from "@/services/api/reading";
import { getDeviceId } from "@/utils/device";
import { debounce } from "@/utils/debounce";

export function useCloudProgress(bookHash: string) {
  const progress = useBookProgress(bookHash);
  const lastFractionRef = useRef<number>(-1);

  const syncProgress = useCallback(
    debounce(async () => {
      const p = useBookProgress(bookHash);
      if (!p) return;
      const fraction = p.fraction ?? 0;
      if (Math.abs(fraction - lastFractionRef.current) < 0.01) return;
      lastFractionRef.current = fraction;
      try {
        await saveReadingProgress(bookHash, {
          spine_index: 0,
          content_id: 0,
          scroll_percent: fraction,
        });
      } catch { /* 静默 */ }
    }, 3000),
    [bookHash],
  );

  useEffect(() => { syncProgress(); }, [progress, syncProgress]);
}
