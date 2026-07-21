/**
 * 设备注册 API
 */

import { apiPost } from "./api";

export interface DeviceRegisterRequest {
  device_id: string;
  device_name?: string;
  platform?: string;
}

export interface DeviceInfo {
  device_id: string;
  device_name?: string;
  platform?: string;
  created_at: string;
}

export async function registerDevice(
  req: DeviceRegisterRequest,
): Promise<DeviceInfo> {
  const response = await apiPost<{ code: number; data: DeviceInfo }>(
    "/devices/register",
    req,
  );
  return response.data;
}
