// Stub: Turso database plugin for MVP
export class Database {
  async execute(): Promise<{ rows: never[]; columns: string[] }> {
    return { rows: [], columns: [] };
  }
}
export type LoadOptions = Record<string, never>;
export type QueryResult = { rows: never[]; columns: string[] };
