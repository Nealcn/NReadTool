/**
 * 设备 UUID 管理
 * 首次访问生成唯一设备标识，存入 localStorage 持久化
 */

const DEVICE_ID_KEY = "device_id";

export function getDeviceId(): string {
  let deviceId = localStorage.getItem(DEVICE_ID_KEY);
  if (!deviceId) {
    deviceId = crypto.randomUUID();
    localStorage.setItem(DEVICE_ID_KEY, deviceId);
  }
  return deviceId;
}

export function clearDeviceId(): void {
  localStorage.removeItem(DEVICE_ID_KEY);
}
