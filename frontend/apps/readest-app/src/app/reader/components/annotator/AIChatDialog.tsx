/**
 * AI 聊天对话框
 * 选中文本后弹出，首条消息解释选中文本，支持多轮对话
 */

"use client";

import React, { useState, useRef, useEffect } from "react";
import { aiChat, type ChatMessage } from "@/services/api/ai";

interface AIChatDialogProps {
  isOpen: boolean;
  selectedText: string;
  bookId?: number;
  chapterTitle?: string;
  onClose: () => void;
}

export default function AIChatDialog({
  isOpen,
  selectedText,
  bookId,
  chapterTitle,
  onClose,
}: AIChatDialogProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 打开时自动发送首条消息
  useEffect(() => {
    if (isOpen && !hasInitialized && selectedText) {
      setHasInitialized(true);
      setMessages([]);
      const initialMsg: ChatMessage = {
        role: "user",
        content: `请解读以下文本：\n\n${selectedText}`,
      };
      setMessages([initialMsg]);
      sendMessage([initialMsg]);
    }
  }, [isOpen, selectedText, hasInitialized]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 打开时聚焦输入框
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const sendMessage = async (msgs: ChatMessage[]) => {
    setIsLoading(true);
    try {
      const result = await aiChat({
        messages: msgs,
        book_id: bookId,
        chapter_title: chapterTitle,
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "AI 服务暂不可用，请稍后重试。",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput("");
    const newMsg: ChatMessage = { role: "user", content: text };
    const newMessages = [...messages, newMsg];
    setMessages(newMessages);
    sendMessage(newMessages);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/20"
      onClick={onClose}
    >
      <div
        className="bg-base-100 mx-2 mb-0 sm:mb-0 flex h-[70vh] w-full max-w-lg flex-col rounded-t-xl sm:rounded-xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between border-b px-4 py-3">
          <span className="text-sm font-bold">AI 解读</span>
          <button onClick={onClose} className="text-base-content/50 hover:text-base-content text-lg">
            ✕
          </button>
        </div>

        {/* 选中文本预览 */}
        <div className="bg-base-200 mx-3 mt-2 rounded-lg p-3">
          <p className="text-base-content/50 text-xs mb-1">选中文本</p>
          <p className="text-sm line-clamp-2 leading-relaxed">
            {selectedText.substring(0, 200)}
            {selectedText.length > 200 && <span className="text-xs opacity-50">...已截断</span>}
          </p>
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto px-4 py-2 space-y-3">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-xl px-3 py-2 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-primary text-primary-content"
                    : "bg-base-200 text-base-content"
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-base-200 rounded-xl px-3 py-2 text-sm">
                <div className="flex items-center gap-1">
                  <span className="animate-pulse">●</span>
                  <span className="animate-pulse animation-delay-200">●</span>
                  <span className="animate-pulse animation-delay-400">●</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入框 */}
        <div className="border-t px-3 py-2">
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入你的问题..."
              disabled={isLoading}
              className="input input-bordered input-sm flex-1 text-sm"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="btn btn-primary btn-sm"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
