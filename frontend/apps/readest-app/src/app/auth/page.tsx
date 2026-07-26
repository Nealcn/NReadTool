'use client';

import { Suspense, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useTranslation } from '@/hooks/useTranslation';
import { loginApi, registerApi } from '@/services/api/auth';

function AuthForm() {
  const _ = useTranslation();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = isRegister
        ? await registerApi(email, password, username)
        : await loginApi(email, password);
      login(res.access_token, res.user);
      const redirect = searchParams?.get('redirect') || '/library';
      router.push(redirect);
    } catch (err: unknown) {
      console.error('[Auth]', err);
      const msg =
        err instanceof Error ? err.message :
        typeof err === 'object' && err && 'message' in err ? (err as { message: string }).message :
        _('Login failed');
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-base-200">
      <div className="card mx-4 w-full max-w-md bg-base-100 shadow-xl">
        <div className="card-body items-center text-center">
          <h1 className="mt-4 text-3xl font-bold text-base-content">NReadTool</h1>
          <p className="mb-4 text-sm text-base-content/60">AI 陪伴阅读</p>

          <form onSubmit={handleSubmit} className="w-full space-y-4">
            {isRegister && (
              <input
                type="text"
                placeholder={_('Username')}
                className="input input-bordered w-full"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                minLength={2}
              />
            )}
            <input
              type="email"
              placeholder={_('Email')}
              className="input input-bordered w-full"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder={_('Password')}
              className="input input-bordered w-full"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />

            {error && (
              <p className="text-sm text-error">{error}</p>
            )}

            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? (
                <span className="loading loading-spinner loading-sm" />
              ) : isRegister ? (
                _('Register')
              ) : (
                _('Login')
              )}
            </button>
          </form>

          <div className="divider" />

          <p className="text-sm text-base-content/70">
            {isRegister ? _('Already have an account?') : _("Don't have an account?")}{' '}
            <button
              type="button"
              className="link link-primary"
              onClick={() => { setIsRegister(!isRegister); setError(''); }}
            >
              {isRegister ? _('Sign In') : _('Register')}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

const AuthPage = () => (
  <Suspense fallback={
    <div className="flex min-h-screen items-center justify-center bg-base-200">
      <span className="loading loading-spinner loading-lg" />
    </div>
  }>
    <AuthForm />
  </Suspense>
);

export default AuthPage;
