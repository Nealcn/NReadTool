/**
 * 云端书库同步 Hook
 *  - 下载：云端书籍自动导入到本地书库（跨设备同步）
 *  - 上传通过每本书封面的 ↑ 按钮手动完成
 */

import { useEffect, useRef } from "react";
import { useLibraryStore } from "@/store/libraryStore";
import { useSettingsStore } from "@/store/settingsStore";
import { useEnv } from "@/context/EnvContext";
import { getDeviceId } from "@/utils/device";
import { registerDevice } from "@/services/api/devices";
import { getBookList } from "@/services/api/books";
import { ingestFile } from "@/services/ingestService";
import { buildBookLookupIndex } from "@/services/bookService";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export function useCloudLibrarySync() {
  const libraryLoaded = useLibraryStore((s) => s.libraryLoaded);
  const library = useLibraryStore((s) => s.library);
  const settings = useSettingsStore((s) => s.settings);
  const syncedRef = useRef(false);
  const { appService } = useEnv();

  useEffect(() => {
    if (!libraryLoaded || syncedRef.current) return;
    syncedRef.current = true;

    const sync = async () => {
      try {
        const deviceId = getDeviceId();
        await registerDevice({ device_id: deviceId, platform: "web" });

        // 获取云端书籍列表
        const cloudList = await getBookList();

        // ── 下载：云端书 → 本地（仅当本地没有时） ──
        const libraryBooks = useLibraryStore.getState().library;
        const lookupIndex = buildBookLookupIndex(libraryBooks, appService?.osPlatform);
        for (const cloudBook of cloudList.books) {
          // 检查本地是否已有（按 title + author + size 匹配）
          const existsLocally = libraryBooks.some(
            (lb) =>
              lb.title === cloudBook.title &&
              lb.author === cloudBook.author &&
              (lb as { size?: number }).size === cloudBook.file_size,
          );
          if (existsLocally) continue;

          try {
            const url = `${API_BASE_URL}/books/${cloudBook.file_hash}/download`;
            const response = await fetch(url);
            if (!response.ok) continue;
            const blob = await response.blob();
            const file = new File([blob], `${cloudBook.title.replace(/[:*?"<>|]/g, "_")}.epub`, {
              type: "application/epub+zip",
            });

            await ingestFile(
              { file, books: libraryBooks, lookupIndex },
              { appService, settings, isLoggedIn: false, appBooksPrefix: null },
            );
          } catch {
            // 下载/导入失败静默跳过
          }
        }
      } catch {
        // 整体失败静默，下次重试
      }
    };
    sync();
  }, [libraryLoaded, library, appService, settings]);
}
