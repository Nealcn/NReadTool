import { BufferedTTSClient } from './BufferedTTSClient';
import { BackendSpeechProvider } from './providers/backend';
import { BookTTSCacheStore, getTTSCacheConfig } from './providers/bookCacheStore';
import { CachingProvider } from './providers/cache';
import { SpeechProvider } from './providers/types';
import { TTSController } from './TTSController';
import { AppService } from '@/types/system';

export { DEFAULT_SENTENCE_GAP_SEC } from './BufferedTTSClient';

export class BackendTTSClient extends BufferedTTSClient {
  #backendProvider: BackendSpeechProvider;

  constructor(controller?: TTSController, appService?: AppService | null) {
    const backendProvider = new BackendSpeechProvider();
    let provider: SpeechProvider = backendProvider;
    const cacheConfig = getTTSCacheConfig();
    if (appService && cacheConfig.enabled) {
      const store = new BookTTSCacheStore(
        appService,
        () => controller?.bookKey?.split('-')[0] || null,
        cacheConfig.budgetMB * 1024 * 1024,
      );
      provider = new CachingProvider(backendProvider, store);
    }
    super(provider, controller, appService);
    this.#backendProvider = backendProvider;
  }

  override async init(): Promise<boolean> {
    this.voices = await this.#backendProvider.getAllVoices().catch(() => []);
    if (await this.#backendProvider.init()) {
      this.initialized = true;
      return true;
    }
    // Cache-only fallback: if there's a persistent cache, a pre-downloaded
    // book still plays even when the backend is unreachable.
    if (this.provider instanceof CachingProvider) {
      this.initialized = true;
      return true;
    }
    this.initialized = false;
    return false;
  }
}
