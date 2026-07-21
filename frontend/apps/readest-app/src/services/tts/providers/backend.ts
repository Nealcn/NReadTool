// Backend-proxied TTS as a SpeechProvider.
// Instead of connecting to Microsoft Edge TTS directly (WSS) or through a thin
// proxy (HTTPS -> Cloudflare Worker), this provider sends text to the Python
// FastAPI backend, which runs edge-tts and returns audio + word boundaries.
// This bypasses network restrictions that block wss://speech.platform.bing.com/.

import type { TTSVoice } from '../types';
import type { TTSWordBoundary } from '@/libs/edgeTTS';
import {
  SpeechProvider,
  SpeechSynthesisPermanentError,
  SpeechSynthesisRequest,
  SpeechSynthesisResult,
} from './types';

// Use the same backend base URL as the main API layer (api.ts).
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
const SPEAK_ENDPOINT = `${API_BASE_URL}/tts/speak`;
const VOICES_ENDPOINT = `${API_BASE_URL}/tts/voices`;

// Matches the header format used in libs/edgeTTS.ts's HTTPS proxy path.
const WORD_BOUNDARIES_HEADER = 'X-TTS-Word-Boundaries';

function parseWordBoundariesHeader(value: string | null): TTSWordBoundary[] {
  if (!value) return [];
  try {
    const parsed = JSON.parse(decodeURIComponent(value));
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (b: unknown): b is TTSWordBoundary =>
        !!b &&
        typeof (b as TTSWordBoundary).offset === 'number' &&
        typeof (b as TTSWordBoundary).duration === 'number' &&
        typeof (b as TTSWordBoundary).text === 'string',
    );
  } catch {
    return [];
  }
}

export class BackendSpeechProvider implements SpeechProvider {
  readonly id = 'backend-tts';
  readonly label = 'Cloud TTS';
  readonly fallbackVoiceId = 'en-US-AriaNeural';
  readonly cacheable = true;

  #voices: TTSVoice[] = [];

  async init(): Promise<boolean> {
    try {
      const response = await fetch(VOICES_ENDPOINT, { signal: AbortSignal.timeout(5000) });
      return response.ok;
    } catch {
      return false;
    }
  }

  async getAllVoices(): Promise<TTSVoice[]> {
    if (this.#voices.length === 0) {
      try {
        const response = await fetch(VOICES_ENDPOINT, { signal: AbortSignal.timeout(10000) });
        if (response.ok) {
          const json = await response.json();
          this.#voices = json.data?.voices ?? [];
        }
      } catch (e) {
        if (this.#voices.length === 0) throw e;
      }
    }
    return this.#voices;
  }

  async synthesize(
    req: SpeechSynthesisRequest,
    signal: AbortSignal,
  ): Promise<SpeechSynthesisResult> {
    const response = await fetch(SPEAK_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: req.text,
        voice: req.voice,
        lang: req.lang,
        pitch: req.pitch,
        rate: 1.0, // Rate pinned to 1.0 (playout applies rate)
      }),
      signal,
    });

    if (!response.ok) {
      const body = await response.text().catch(() => '');
      throw new Error(
        `Backend TTS failed (${response.status}): ${body || response.statusText}`,
      );
    }

    const audio = await response.arrayBuffer();
    if (!audio.byteLength) {
      throw new SpeechSynthesisPermanentError(
        'No audio data received from backend.',
      );
    }

    const boundaries = parseWordBoundariesHeader(
      response.headers.get(WORD_BOUNDARIES_HEADER),
    );

    return { audio, boundaries };
  }

  pickDefaultVoice(voices: TTSVoice[]): string | undefined {
    const first = voices[0];
    if (first?.id === 'en-US-AnaNeural') return 'en-US-AriaNeural';
    return first?.id;
  }
}
