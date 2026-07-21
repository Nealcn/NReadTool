// Stub: OPDS removed for MVP
export function needsProxy(): boolean { return false; }
export function getProxiedURL(url: string): string { return url; }
export async function probeAuth(): Promise<void> {}
export async function probeFilename(): Promise<string> { return ''; }
export async function fetchWithAuth(): Promise<Response> {
  return new Response(null, { status: 404 });
}
