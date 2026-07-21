/**
 * 本地缓存工具（localStorage 封装）
 * 用户偏好、离线进度、设备 ID 等本地持久化
 */

const PREFIX = "bookread_";

export const localCache = {
  get<T>(key: string): T | null {
    try {
      const value = localStorage.getItem(PREFIX + key);
      if (value === null) return null;
      return JSON.parse(value) as T;
    } catch {
      return null;
    }
  },

  set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value));
    } catch {
      // localStorage 不可用或已满
    }
  },

  remove(key: string): void {
    try {
      localStorage.removeItem(PREFIX + key);
    } catch {
      // ignore
    }
  },

  // 用户偏好
  getPreferences(): Record<string, unknown> {
    return this.get<Record<string, unknown>>("preferences") || {};
  },

  setPreferences(prefs: Record<string, unknown>): void {
    this.set("preferences", prefs);
  },

  updatePreference(key: string, value: unknown): void {
    const prefs = this.getPreferences();
    prefs[key] = value;
    this.setPreferences(prefs);
  },
};
