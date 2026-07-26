/**
 * API 通信层 - Axios 实例封装
 * 自动注入 X-Device-Id Header，统一错误处理
 */

import axios, { AxiosError, type AxiosInstance, type AxiosRequestConfig } from "axios";
import { getDeviceId } from "@/utils/device";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器 - 自动注入设备 ID + JWT
api.interceptors.request.use(
  (config) => {
    const deviceId = getDeviceId();
    if (deviceId) {
      config.headers["X-Device-Id"] = deviceId;
    }
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError<{ message?: string; code?: number }>) => {
    if (!error.response) {
      return Promise.reject({
        code: -1,
        message: "网络连接失败，请检查网络后重试",
      });
    }

    const { status, headers, config } = error.response;
    const contentType = headers?.["content-type"] || "";
    const requestUrl = `${config?.baseURL || ""}${config?.url || ""}`;

    // 检查响应是否为 JSON
    if (!contentType.includes("application/json")) {
      console.error(`[API] ${requestUrl} 返回 ${contentType} (status ${status})`);
      return Promise.reject({
        code: status,
        message: `后端服务异常 (${requestUrl})，请确认后端已启动`,
      });
    }

    const data = error.response.data as { message?: string; code?: number } | undefined;
    const message = data?.message || getDefaultErrorMessage(status);
    return Promise.reject({
      code: data?.code || status,
      message,
    });
  },
);

function getDefaultErrorMessage(status: number): string {
  const messages: Record<number, string> = {
    400: "请求参数错误",
    404: "请求的资源不存在",
    413: "文件大小超过限制",
    429: "请求过于频繁，请稍后再试",
    500: "服务器内部错误",
    502: "服务器暂不可用",
    503: "服务暂不可用",
    504: "AI 服务超时，请稍后重试",
  };
  return messages[status] || `请求失败 (${status})`;
}

// 封装请求方法
export async function apiGet<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.get(url, config);
  return response as T;
}

export async function apiPost<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.post(url, data, config);
  return response as T;
}

export async function apiPut<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.put(url, data, config);
  return response as T;
}

export async function apiDelete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.delete(url, config);
  return response as T;
}

export default api;
