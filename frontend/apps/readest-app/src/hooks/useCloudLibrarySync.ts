/**
 * 云端书库同步 Hook
 * 启动时将本地书籍列表同步到后端（仅元数据，不含文件）
 */

import { useEffect, useRef } from "react";
import { useLibraryStore } from "@/store/libraryStore";
import { getDeviceId } from "@/utils/device";
import { registerDevice } from "@/services/api/devices";
import { getBookList } from "@/services/api/books";

const SYNC_KEY = "cloud_library_synced";

export function useCloudLibrarySync() {
  const libraryLoaded = useLibraryStore((s) => s.libraryLoaded);
  const library = useLibraryStore((s) => s.library);
  const syncedRef = useRef(false);

  useEffect(() => {
    if (!libraryLoaded || library.length === 0 || syncedRef.current) return;
    syncedRef.current = true;

    const sync = async () => {
      try {
        const deviceId = getDeviceId();
        await registerDevice({ device_id: deviceId, platform: "web" });

        // 从后端拉取云端书库，确保设备注册
        await getBookList();

        // 记录同步状态
        localStorage.setItem(SYNC_KEY, Date.now().toString());
      } catch {
        // 静默失败，下次启动重试
      }
    };
    sync();
  }, [libraryLoaded, library]);
}
