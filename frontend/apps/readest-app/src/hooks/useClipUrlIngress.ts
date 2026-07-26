import { useCallback, useEffect, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useEnv } from '@/context/EnvContext';
import { useLibraryStore } from '@/store/libraryStore';
import { useSettingsStore } from '@/store/settingsStore';
import { isTauriAppPlatform } from '@/services/environment';
import { eventDispatcher } from '@/utils/event';
import { parseAnnotationDeepLink } from '@/utils/deeplink';
import { parseShareDeepLink } from '@/utils/share';
import { useTranslation } from './useTranslation';

// useClipUrlIngress — Tauri-only, simplified for web build
export function useClipUrlIngress() {
  const _ = useTranslation();
  const { appService } = useEnv();
  const { user } = useAuth();
  const libraryLoaded = useLibraryStore((s) => s.libraryLoaded);
  const settings = useSettingsStore((s) => s.settings);
  const processedRef = useRef<string>('');

  const handleClipUrlIngress = useCallback(
    async (url: string) => {
      if (!isTauriAppPlatform() || !appService || !libraryLoaded || processedRef.current === url) return;
      processedRef.current = url;
      console.log('[clip] not supported on simplified web build', { url });
    },
    [appService, libraryLoaded],
  );

  useEffect(() => {
    const handler = (event: CustomEvent) => handleClipUrlIngress(event.detail?.url || '');
    eventDispatcher.on('clip-url-ingress', handler);
    return () => eventDispatcher.off('clip-url-ingress', handler);
  }, [handleClipUrlIngress]);
}
