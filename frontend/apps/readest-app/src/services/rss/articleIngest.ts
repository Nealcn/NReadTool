// Simplified stub — full RSS article ingestion requires Tauri + send features
import { md5Fingerprint } from '@/utils/md5';
import type { AppService } from '@/types/system';
import type { SystemSettings } from '@/types/settings';
import type { Book } from '@/types/book';
import type { RssFeed, RssFeedItem, ParsedFeed } from '@/types/rss';

const MIN_FEED_CONTENT = 200;

export function resolveArticleInput(_item: RssFeedItem, _pageHtml: string | null): string {
  return '';
}

export interface OpenFeedArticleParams {
  item: RssFeedItem;
  feed: RssFeed;
  books: Book[];
  appService: AppService;
  settings: SystemSettings;
  isLoggedIn: boolean;
  translate: (key: string) => string;
  ingest?: typeof import('@/services/ingestService').ingestFile;
}

export async function openFeedArticle(_params: OpenFeedArticleParams): Promise<void> {
  // Tauri-only: web build does not support feed article ingestion
  console.log('[feed] article ingestion not supported on web');
}

export async function handleOpenArticle(_item: RssFeedItem): Promise<void> {
  console.log('[feed] handleOpenArticle not supported on web');
}
