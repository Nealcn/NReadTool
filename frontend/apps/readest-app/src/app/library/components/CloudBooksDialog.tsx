/**
 * 云端书库对话框
 * 展示后端 API 中的书籍列表，支持上传、导入、重命名、删除
 */

"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { clsx } from "clsx";
import Dialog from "@/components/Dialog";
import { useTranslation } from "@/hooks/useTranslation";
import { getBookList, uploadBook, renameBook, deleteBook, type BookInfo } from "@/services/api/books";
import { getDeviceId } from "@/utils/device";
import { registerDevice } from "@/services/api/devices";

interface CloudBooksDialogProps {
  onClose: () => void;
  onImportBook?: (url: string, title: string, cloudBookId: number) => void;
}

export function CloudBooksDialog({ onClose, onImportBook }: CloudBooksDialogProps) {
  const _ = useTranslation();
  const [books, setBooks] = useState<BookInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [menuBookId, setMenuBookId] = useState<number | null>(null);
  const [renamingBookId, setRenamingBookId] = useState<number | null>(null);
  const [renameTitle, setRenameTitle] = useState("");
  const menuRef = useRef<HTMLDivElement>(null);

  const loadBooks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const deviceId = getDeviceId();
      await registerDevice({ device_id: deviceId, platform: "web" });
      const data = await getBookList(deviceId);
      setBooks(data.books);
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message || "加载失败";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBooks();
  }, [loadBooks]);

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuBookId(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleUpload = async () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".epub";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      setUploading(true);
      setError(null);
      try {
        const deviceId = getDeviceId();
        await uploadBook(file, deviceId);
        await loadBooks();
      } catch (err: unknown) {
        const msg = (err as { message?: string })?.message || "上传失败";
        setError(msg);
      } finally {
        setUploading(false);
      }
    };
    input.click();
  };

  const handleOpenBook = (book: BookInfo) => {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";
    const downloadUrl = `${baseUrl}/books/${book.id}/download`;
    if (onImportBook) {
      onImportBook(downloadUrl, book.title, book.id);
    }
  };

  const handleRename = async () => {
    if (renamingBookId === null || !renameTitle.trim()) return;
    setError(null);
    try {
      await renameBook(renamingBookId, renameTitle.trim());
      setRenamingBookId(null);
      setRenameTitle("");
      await loadBooks();
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message || "重命名失败";
      setError(msg);
    }
  };

  const handleDelete = async (bookId: number) => {
    if (!confirm("确定删除这本书？此操作不可撤销。")) return;
    setError(null);
    try {
      await deleteBook(bookId);
      setMenuBookId(null);
      await loadBooks();
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message || "删除失败";
      setError(msg);
    }
  };

  return (
    <Dialog
      isOpen={true}
      title="云端书库"
      onClose={onClose}
      bgClassName="sm:!bg-black/75"
      boxClassName="sm:min-w-[520px] sm:w-3/4 sm:h-[85%] sm:!max-w-screen-sm"
    >
      <div className="bg-base-100 relative flex flex-col overflow-y-auto pb-4">
        {/* 操作栏 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-base-200">
          <span className="text-sm text-base-content/60">
            {books.length > 0 ? `${books.length} 本书` : ""}
          </span>
          <div className="flex gap-2">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="btn btn-primary btn-sm"
            >
              {uploading ? (
                <>
                  <span className="loading loading-spinner loading-xs" />
                  上传中...
                </>
              ) : (
                "上传 EPUB"
              )}
            </button>
            <button onClick={loadBooks} className="btn btn-ghost btn-sm" disabled={loading}>
              刷新
            </button>
          </div>
        </div>

        {error && (
          <div className="mx-4 mt-3 px-3 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg">
            {error}
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-16">
            <span className="loading loading-spinner loading-md" />
          </div>
        )}

        {!loading && books.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-base-content/50">
            <svg className="w-16 h-16 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <p className="text-sm">暂无云端书籍</p>
            <p className="text-xs mt-1">点击「上传 EPUB」添加书籍</p>
          </div>
        )}

        {/* 重命名弹窗 */}
        {renamingBookId !== null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20">
            <div className="bg-base-100 rounded-xl p-5 shadow-2xl w-80" onClick={(e) => e.stopPropagation()}>
              <h3 className="text-sm font-bold mb-3">重命名</h3>
              <input
                type="text"
                value={renameTitle}
                onChange={(e) => setRenameTitle(e.target.value)}
                className="input input-bordered input-sm w-full mb-3"
                placeholder="输入新书名"
                autoFocus
                onKeyDown={(e) => e.key === "Enter" && handleRename()}
              />
              <div className="flex justify-end gap-2">
                <button className="btn btn-ghost btn-sm" onClick={() => { setRenamingBookId(null); setRenameTitle(""); }}>
                  取消
                </button>
                <button className="btn btn-primary btn-sm" onClick={handleRename} disabled={!renameTitle.trim()}>
                  确认
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 书籍列表 */}
        {!loading && books.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 p-4">
            {books.map((book) => (
              <div key={book.id} className="relative flex flex-col items-center p-3 rounded-xl hover:bg-base-200 transition-colors group">
                {/* 封面（点击导入） */}
                <div className="w-full cursor-pointer" onClick={() => handleOpenBook(book)}>
                  {book.cover_image ? (
                    <img
                      src={`data:image/png;base64,${book.cover_image}`}
                      alt={book.title}
                      className="w-full aspect-[3/4] object-cover rounded-lg shadow-sm mb-2"
                    />
                  ) : (
                    <div className="w-full aspect-[3/4] bg-gradient-to-br from-blue-400 to-purple-500 rounded-lg shadow-sm mb-2 flex items-center justify-center">
                      <span className="text-white text-3xl font-bold">{book.title.charAt(0)}</span>
                    </div>
                  )}
                </div>

                {/* 书名 */}
                <p className="text-xs text-center font-medium line-clamp-2 w-full">{book.title}</p>
                {book.author && (
                  <p className="text-[10px] text-base-content/50 text-center truncate w-full mt-0.5">{book.author}</p>
                )}

                {/* 三点菜单按钮 */}
                <button
                  className="absolute top-2 right-2 w-6 h-6 flex items-center justify-center rounded-full bg-black/30 text-white opacity-0 group-hover:opacity-100 hover:bg-black/50 transition-opacity"
                  onClick={(e) => { e.stopPropagation(); setMenuBookId(menuBookId === book.id ? null : book.id); }}
                >
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z" />
                  </svg>
                </button>

                {/* 下拉菜单 */}
                {menuBookId === book.id && (
                  <div
                    ref={menuRef}
                    className="absolute top-10 right-2 z-50 bg-base-100 rounded-lg shadow-xl border border-base-200 py-1 min-w-[120px]"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      className="w-full px-3 py-2 text-left text-xs hover:bg-base-200 flex items-center gap-2"
                      onClick={() => { handleOpenBook(book); setMenuBookId(null); }}
                    >
                      📥 导入到本地
                    </button>
                    <button
                      className="w-full px-3 py-2 text-left text-xs hover:bg-base-200 flex items-center gap-2"
                      onClick={() => { setRenamingBookId(book.id); setRenameTitle(book.title); setMenuBookId(null); }}
                    >
                      ✏️ 重命名
                    </button>
                    <button
                      className="w-full px-3 py-2 text-left text-xs hover:bg-base-200 text-red-500 flex items-center gap-2"
                      onClick={() => { setMenuBookId(null); handleDelete(book.id); }}
                    >
                      🗑️ 删除
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Dialog>
  );
}
