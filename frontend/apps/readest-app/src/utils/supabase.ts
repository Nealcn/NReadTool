import { createClient } from '@supabase/supabase-js';
import { getRuntimeConfig } from '@/services/runtimeConfig';

const decodeBase64 = (val: string | undefined) =>
  val ? atob(val) : '';

const supabaseUrl =
  getRuntimeConfig()?.supabaseUrl ||
  process.env['SUPABASE_URL'] ||
  process.env['NEXT_PUBLIC_SUPABASE_URL'] ||
  decodeBase64(process.env['NEXT_PUBLIC_DEFAULT_SUPABASE_URL_BASE64']);
const supabaseAnonKey =
  getRuntimeConfig()?.supabaseAnonKey ||
  process.env['SUPABASE_ANON_KEY'] ||
  process.env['NEXT_PUBLIC_SUPABASE_ANON_KEY'] ||
  decodeBase64(process.env['NEXT_PUBLIC_DEFAULT_SUPABASE_KEY_BASE64']);

const PLACEHOLDER_URL = 'https://placeholder.supabase.co';
export const supabase = createClient(supabaseUrl || PLACEHOLDER_URL, supabaseAnonKey || 'placeholder-key');

export const createSupabaseClient = (accessToken?: string) => {
  return createClient(supabaseUrl, supabaseAnonKey, {
    global: {
      headers: accessToken
        ? {
            Authorization: `Bearer ${accessToken}`,
          }
        : {},
    },
  });
};

export const createSupabaseAdminClient = () => {
  const supabaseAdminKey = process.env['SUPABASE_ADMIN_KEY'] || '';
  return createClient(supabaseUrl, supabaseAdminKey, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
      detectSessionInUrl: false,
    },
  });
};
