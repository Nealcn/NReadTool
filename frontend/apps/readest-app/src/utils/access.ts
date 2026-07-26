/**
 * 功能访问控制（简化版）
 * 所有付费功能已移除，所有功能默认可用
 */

import { jwtDecode } from 'jwt-decode';
import { UserPlan } from '@/types/quota';
import { DEFAULT_DAILY_TRANSLATION_QUOTA, DEFAULT_STORAGE_QUOTA } from '@/services/constants';

interface Token {
  plan: UserPlan;
  storage_usage_bytes: number;
  storage_purchased_bytes: number;
  [key: string]: string | number;
}

export const getSubscriptionPlan = (_token: string): UserPlan => {
  return 'free';
};

export const getUserProfilePlan = (): UserPlan => {
  return 'free';
};

export const getAccessToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

export const getUserID = (): string | null => {
  if (typeof window !== 'undefined') {
    try {
      const raw = localStorage.getItem('user');
      if (raw) {
        const user = JSON.parse(raw);
        return String(user.id);
      }
    } catch { /* */ }
  }
  return null;
};

export const isCloudSyncAllowed = (): boolean => true;
export const isCloudSyncInPlan = (): boolean => true;
export const isTTSCacheAllowed = (): boolean => true;
export const isTTSCacheInPlan = (): boolean => true;
export const isEmailInPlan = (_email: string): boolean => true;

export const getStoragePlanData = (): { quotaBytes: number; usedBytes: number } => {
  return { quotaBytes: DEFAULT_STORAGE_QUOTA.pro, usedBytes: 0 };
};

export const getDailyTranslationPlanData = (): { quota: number; used: number } => {
  return { quota: DEFAULT_DAILY_TRANSLATION_QUOTA.pro, used: 0 };
};

export const getTranslationPlanData = () => {
  return { quotaBytes: DEFAULT_DAILY_TRANSLATION_QUOTA.pro, usedBytes: 0 };
};

export const getTranslationQuota = () => DEFAULT_DAILY_TRANSLATION_QUOTA.pro;
