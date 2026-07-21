// Stub: OPDS removed for MVP
export function resolveURL(base: string, rel: string): string {
  return new URL(rel, base).toString();
}
export function parseMediaType(): string { return ''; }
export function getFileExtFromPath(path: string): string {
  return path.split('.').pop() || '';
}
export function looksLikeXMLContent(): boolean { return false; }
export function parseOPDSXML(): Record<string, unknown> { return {}; }
