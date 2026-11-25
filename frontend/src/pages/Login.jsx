import { useState } from 'react';
import { useLang } from '../i18n.jsx';
import { useData } from '../store/DataProvider.jsx';
import AuthLayout from '../components/AuthLayout.jsx';

/** One form for both logins. `admin` switches it to the administrator login. */
export default function Login({ admin = false, go }) {
  const { t } = useLang();
  const { login } = useData();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const submit = async (ev) => {
    ev.preventDefault();
    const err = await login(email, password, admin);
    if (err) setError(err);
    else go('app');
  };

  return (
    <AuthLayout>
      <h1>{t(admin ? 'Admin login' : 'Log in')}</h1>
      <form onSubmit={submit}>
        <label>{t('Email')}<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></label>
        <label>{t('Password')}<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" /></label>
        <button>{t('Log in')}</button>
        {error && <span className="err" role="alert">{t(error)}</span>}
      </form>
      {admin ? (
        <>
          <button type="button" className="alt" onClick={() => go('login')}>{t('Back to user login')}</button>
          <p className="muted">Demo admin: admin@tidytrack.lk / admin123</p>
        </>
      ) : (
        <>
          <p className="muted">{t('No account yet?')}</p>
          <button type="button" className="alt" onClick={() => go('register')}>{t('Register')}</button>{' '}
          <button type="button" className="alt" onClick={() => go('adminlogin')}>{t('Admin login')}</button>
          <p className="muted">Demo resident or driver: k.silva@example.lk or a.perera@example.lk / demo123.</p>
        </>
      )}
    </AuthLayout>
  );
}
