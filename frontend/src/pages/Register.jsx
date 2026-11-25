import { useState } from 'react';
import { useLang } from '../i18n.jsx';
import { useData } from '../store/DataProvider.jsx';
import AuthLayout from '../components/AuthLayout.jsx';
import { STOPS } from '../data.js';

export default function Register({ go }) {
  const { t } = useLang();
  const { register } = useData();
  const [f, setF] = useState({ role: 'resident', name: '', email: '', phone: '', password: '', confirm: '', stop: 1, vehicle: '' });
  const [error, setError] = useState('');
  const set = (k) => (ev) => setF({ ...f, [k]: ev.target.value });

  const submit = async (ev) => {
    ev.preventDefault();
    const err = await register(f);
    if (err) setError(err);
    else go('app');
  };

  return (
    <AuthLayout>
      <h1>{t('Create an account')}</h1>
      <form onSubmit={submit}>
        <div className="sw" role="radiogroup" aria-label={t('Account type')}>
          {['resident', 'driver'].map((r) => (
            <label key={r}>
              <input type="radio" name="role" value={r} checked={f.role === r} onChange={set('role')} />{' '}
              {t(r === 'resident' ? 'Resident' : 'Driver')}
            </label>
          ))}
        </div>
        <label>{t('Full name')}<input value={f.name} onChange={set('name')} required autoComplete="name" /></label>
        <label>{t('Email')}<input type="email" value={f.email} onChange={set('email')} required autoComplete="email" /></label>
        <label>{t('Phone')}<input type="tel" value={f.phone} onChange={set('phone')} required autoComplete="tel" /></label>
        <label>{t('Password (6+ characters)')}<input type="password" value={f.password} onChange={set('password')} minLength={6} required autoComplete="new-password" /></label>
        <label>{t('Confirm password')}<input type="password" value={f.confirm} onChange={set('confirm')} minLength={6} required autoComplete="new-password" /></label>
        {f.role === 'resident' ? (
          <label>{t('Your street')}
            <select value={f.stop} onChange={set('stop')}>
              {STOPS.map((s) => <option key={s.id} value={s.id}>{s.n}</option>)}
            </select>
          </label>
        ) : (
          <label>{t('Vehicle number')}<input value={f.vehicle} onChange={set('vehicle')} placeholder={t('e.g. WP LK-4821')} /></label>
        )}
        <button>{t('Create account')}</button>
        {error && <span className="err" role="alert">{t(error)}</span>}
      </form>
    </AuthLayout>
  );
}
