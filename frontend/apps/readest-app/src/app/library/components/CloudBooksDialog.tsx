/**
 * 云端书库对话框
 * 展示后端 API 中的书籍列表，支持上传和导入到本地阅读器
 */

"use client";

import React, { useEffect, useState, useCallback } from "react";
import { clsx } from "clsx";
import Dialog from "@/components/Dialog";
import { useTranslation } from "@/hooks/useTranslation";
import { getBookList, uploadBook, type BookInfo } from "@/services/api/books";
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

  // 初始化：注册设备 + 加载书籍列表
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

  // 上传文件到后端
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

  // 打开书籍（下载 EPUB 并导入本地阅读器）
  const handleOpenBook = (book: BookInfo) => {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";
    const downloadUrl = `${baseUrl}/books/${book.id}/download`;
    if (onImportBook) {
      onImportBook(downloadUrl, book.title, book.id);
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
            <button
              onClick={loadBooks}
              className="btn btn-ghost btn-sm"
              disabled={loading}
            >
              刷新
            </button>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mx-4 mt-3 px-3 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg">
            {error}
          </div>
        )}

        {/* 加载状态 */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <span className="loading loading-spinner loading-md" />
          </div>
        )}

        {/* 书籍网格 */}
        {!loading && books.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-base-content/50">
            <svg className="w-16 h-16 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <p className="text-sm">暂无云端书籍</p>
            <p className="text-xs mt-1">点击「上传 EPUB」添加书籍</p>
          </div>
        )}

        {/* 书籍列表 */}
        {!loading && books.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 p-4">
            {books.map((book) => (
              <div
                key={book.id}
                className="flex flex-col items-center p-3 rounded-xl hover:bg-base-200 cursor-pointer transition-colors group"
                onClick={() => handleOpenBook(book)}
              >
                {book.cover_image ? (
                  <img
                    src={`data:image/png;base64,${book.cover_image}`}
                    alt={book.title}
                    className="w-full aspect-[3/4] object-cover rounded-lg shadow-sm mb-2"
                  />
                ) : (
                  <div className="w-full aspect-[3/4] bg-gradient-to-br from-blue-400 to-purple-500 rounded-lg shadow-sm mb-2 flex items-center justify-center">
                    <span className="text-white text-3xl font-bold">
                      {book.title.charAt(0)}
                    </span>
                  </div>
                )}
                <p className="text-xs text-center font-medium line-clamp-2 w-full">
                  {book.title}
                </p>
                {book.author && (
                  <p className="text-[10px] text-base-content/50 text-center truncate w-full mt-0.5">
                    {book.author}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Dialog>
  );
}
