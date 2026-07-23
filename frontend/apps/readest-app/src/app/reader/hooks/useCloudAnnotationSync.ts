/**
 * 云端高亮/笔记同步 Hook
 * 定期同步 Readest 的笔记到后端
 */

import { useEffect, useRef } from "react";
import { useBookDataStore } from "@/store/bookDataStore";
import { listAnnotations, createAnnotation, deleteAnnotation } from "@/services/api/annotations";

export function useCloudAnnotationSync(bookKey: string) {
  const getConfig = useBookDataStore((s) => s.getConfig);
  const syncedNotesRef = useRef<Set<string>>(new Set());
  const readyRef = useRef(false);

  useEffect(() => {
    // 启动时先加载后端的已有笔记 ID
    listAnnotations(bookKey).then((existing) => {
      for (const ann of existing) {
        syncedNotesRef.current.add(ann.cfi);
      }
      readyRef.current = true;
    }).catch(() => {
      readyRef.current = true;
    });
  }, [bookKey]);

  useEffect(() => {
    if (!readyRef.current) return;

    const interval = setInterval(() => {
      const config = getConfig(bookKey);
      if (!config?.booknotes?.length) return;

      for (const note of config.booknotes) {
        if (syncedNotesRef.current.has(note.cfi)) continue;
        syncedNotesRef.current.add(note.cfi);

        createAnnotation(bookKey, {
          cfi: note.cfi,
          type: note.type === "bookmark" ? "bookmark" : "highlight",
          style: note.style,
          color: note.color,
          text: note.text,
          note: note.note || "",
        }).catch(() => {
          // 失败则移除标记，下次重试
          syncedNotesRef.current.delete(note.cfi);
        });
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [bookKey, getConfig]);
}
