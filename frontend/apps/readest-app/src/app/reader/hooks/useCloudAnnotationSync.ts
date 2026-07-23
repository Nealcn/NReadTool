/**
 * 云端高亮/笔记同步 Hook
 *
 * 双向同步 Readest 的笔记到后端：
 *  - 启动时拉取云端标注，合并到本地 booknotes 渲染到阅读器
 *  - 定期推送本地新增标注到后端
 */

import { useEffect, useRef } from "react";
import { useBookDataStore } from "@/store/bookDataStore";
import { useSettingsStore } from "@/store/settingsStore";
import { useEnv } from "@/context/EnvContext";
import { listAnnotations, createAnnotation } from "@/services/api/annotations";
import type { AnnotationResponse } from "@/services/api/annotations";
import type { BookNote, BookNoteType, HighlightStyle, HighlightColor } from "@/types/book";

/** 后端 AnnotationResponse → 前端 BookNote */
function annotationToBookNote(ann: AnnotationResponse, bookHash: string): BookNote {
  return {
    id: `cloud-${ann.id}`,
    bookHash,
    cfi: ann.cfi,
    type: (ann.type === "highlight" ? "annotation" : ann.type) as BookNoteType,
    style: (ann.style as HighlightStyle) || undefined,
    color: (ann.color as HighlightColor) || undefined,
    text: ann.text || undefined,
    note: ann.note || "",
    createdAt: new Date(ann.created_at).getTime(),
    updatedAt: new Date(ann.updated_at).getTime(),
  };
}

/** 提取纯 book_hash */
function hashFromKey(bookKey: string): string {
  return bookKey.split("-")[0];
}

/** 去重 key: cfi + type 决定标注唯一性 */
function noteKey(note: BookNote): string {
  return `${note.cfi}::${note.type}`;
}

export function useCloudAnnotationSync(bookKey: string) {
  const getConfig = useBookDataStore((s) => s.getConfig);
  const updateBooknotes = useBookDataStore((s) => s.updateBooknotes);
  const saveConfig = useBookDataStore((s) => s.saveConfig);
  const settings = useSettingsStore((s) => s.settings);
  const { envConfig } = useEnv();

  // 已经同步到后端的标注 CFI
  const syncedCfiRef = useRef<Set<string>>(new Set());
  // 已经合并到本地的云端标注 key（cfi::type）
  const mergedRef = useRef<Set<string>>(new Set());
  // 是否初始化完成
  const readyRef = useRef(false);

  // ── Step 1: 启动时拉取云端标注，合并到本地 ──
  useEffect(() => {
    const bookHash = hashFromKey(bookKey);
    if (!bookHash) return;

    listAnnotations(bookHash)
      .then((cloudNotes) => {
        // 记录已同步 CFI（用于去重推送）
        for (const ann of cloudNotes) {
          syncedCfiRef.current.add(ann.cfi);
        }

        // 转换并合并到本地 booknotes
        const cloudBooknotes = cloudNotes.map((ann) =>
          annotationToBookNote(ann, bookHash),
        );
        if (cloudBooknotes.length === 0) {
          readyRef.current = true;
          return;
        }

        // 获取当前本地标注
        const config = getConfig(bookKey);
        const localNotes = config?.booknotes ?? [];

        // 合并：云端标注不覆盖本地同 cfi+type 的，也不重复合并
        const merged = [...localNotes];
        for (const cn of cloudBooknotes) {
          const key = noteKey(cn);
          if (mergedRef.current.has(key)) continue;
          const exists = localNotes.some((ln) => noteKey(ln) === key);
          if (exists) {
            mergedRef.current.add(key);
            continue;
          }
          merged.push(cn);
          mergedRef.current.add(key);
        }

        if (merged.length > localNotes.length) {
          // 更新 store（触发 Annotator 下次翻页时重绘）
          const updatedConfig = updateBooknotes(bookKey, merged);
          // 持久化到磁盘
          if (updatedConfig && envConfig) {
            saveConfig(envConfig, bookKey, updatedConfig, settings).catch(() => {
              // saveConfig 失败不影响内存中的标注显示
            });
          }
        }

        readyRef.current = true;
      })
      .catch(() => {
        // 云端不可用时，本地模式降级
        readyRef.current = true;
      });
  }, [bookKey, getConfig, updateBooknotes, saveConfig, envConfig, settings]);

  // ── Step 2: 定期推送本地新增标注到后端 ──
  useEffect(() => {
    if (!readyRef.current) return;

    const interval = setInterval(() => {
      const config = getConfig(bookKey);
      if (!config?.booknotes?.length) return;

      for (const note of config.booknotes) {
        if (syncedCfiRef.current.has(note.cfi)) continue;
        // 跳过已合并的云端标注
        if (mergedRef.current.has(noteKey(note))) continue;
        syncedCfiRef.current.add(note.cfi);

        createAnnotation(hashFromKey(bookKey), {
          cfi: note.cfi,
          type: note.type === "bookmark" ? "bookmark" : "highlight",
          style: note.style,
          color: note.color,
          text: note.text,
          note: note.note || "",
        }).catch(() => {
          // 失败则移除标记，下次重试
          syncedCfiRef.current.delete(note.cfi);
        });
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [bookKey, getConfig]);
}
