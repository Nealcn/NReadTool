/**
 * DeepSeek Provider
 * 通过 OpenAI 兼容接口接入 DeepSeek API
 */

import { createOpenAICompatible } from '@ai-sdk/openai-compatible';
import type { LanguageModel, EmbeddingModel } from 'ai';
import type { AIProvider, AISettings } from '../types';
import { getAIFetch } from '../utils/httpFetch';

const DEEPSEEK_DEFAULT_BASE_URL = 'https://api.deepseek.com/v1';
const DEEPSEEK_DEFAULT_MODEL = 'deepseek-chat';

export class DeepSeekProvider implements AIProvider {
  readonly id = 'deepseek' as const;
  readonly name = 'DeepSeek';
  readonly requiresAuth = true;

  private baseUrl: string;
  private apiKey: string;
  private model: string;
  private embeddingModel: string;
  private httpFetch: typeof fetch;
  private client: ReturnType<typeof createOpenAICompatible>;

  constructor(settings: AISettings) {
    this.apiKey = settings.deepseekApiKey || '';
    this.baseUrl = settings.deepseekBaseUrl || DEEPSEEK_DEFAULT_BASE_URL;
    this.model = settings.deepseekModel || DEEPSEEK_DEFAULT_MODEL;
    this.embeddingModel = settings.deepseekEmbeddingModel || '';
    this.httpFetch = getAIFetch();

    this.client = createOpenAICompatible({
      name: 'deepseek',
      baseURL: this.baseUrl,
      apiKey: this.apiKey,
      fetch: this.httpFetch,
    });
  }

  getModel(): LanguageModel {
    return this.client.chatModel(this.model);
  }

  getEmbeddingModel(): EmbeddingModel {
    // DeepSeek 不提供原生 embedding 服务
    if (!this.embeddingModel) {
      throw new Error('DeepSeek does not support embeddings. Leave the Embedding Model field empty in settings to disable RAG.');
    }
    return this.client.textEmbeddingModel(this.embeddingModel);
  }

  async isAvailable(): Promise<boolean> {
    return !!this.apiKey;
  }

  async healthCheck(): Promise<boolean> {
    if (!this.apiKey) return false;
    try {
      const response = await this.httpFetch(`${this.baseUrl}/models`, {
        headers: { Authorization: `Bearer ${this.apiKey}` },
        signal: AbortSignal.timeout(5000),
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}
