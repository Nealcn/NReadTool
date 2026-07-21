/**
 * 网络状态监听 Hook
 */

"use client";

import { useState, useEffect } from "react";

export function useNetwork() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    // 初始化状态
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return isOnline;
}
