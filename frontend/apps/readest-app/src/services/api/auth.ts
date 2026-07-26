/** 认证 API */

import { apiPost } from "./api";

export interface UserInfo {
  id: number;
  email: string;
  username: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export async function loginApi(email: string, password: string): Promise<AuthResponse> {
  const response = await apiPost<{ code: number; data: AuthResponse }>("/auth/login", {
    email,
    password,
  });
  return response.data;
}

export async function registerApi(
  email: string,
  password: string,
  username: string,
): Promise<AuthResponse> {
  const response = await apiPost<{ code: number; data: AuthResponse }>("/auth/register", {
    email,
    password,
    username,
  });
  return response.data;
}
