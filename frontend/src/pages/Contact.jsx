import { useState } from 'react';
import { useLang } from '../i18n.jsx';
import { api } from '../api.js';

export default function Contact() {
  const { t } = useLang();
  const [form, setForm] = useState({ n: '', e: '', m: '' });
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const set = (k) => (ev) => setForm({ ...form, [k]: ev.target.value });

  const submit = async (ev) => {
    ev.preventDefault();
    setError('');
    try {
      await api.post('/messages', { name: form.n, email: form.e, message: form.m });
      setForm({ n: '', e: '', m: '' });
      setSent(true);
    } catch (err) {
      setSent(false);
      setError(err.message);
    }
  };

  return (
    <>
      <h1>{t('Contact us')}</h1>
      <div className="grid2">
        <div className="card">
          <h2>{t('Municipal office')}</h2>
          <ul className="list">
            <li><b>{t('Phone')}</b><span>+94 11 000 0000</span></li>
            <li><b>{t('Email')}</b><span>help@tidytrack.example</span></li>
            <li><b>{t('Address')}</b><span>Municipal Council, Main Street, Colombo</span></li>
            <li><b>{t('Hours')}</b><span>{t('Mon to Fri, 8:30 am to 4:30 pm')}</span></li>
          </ul>
          <p className="muted">{t('Sample details. Replace them with your own.')}</p>
        </div>
        <div className="card">
          <h2>{t('Send a message')}</h2>
          <form onSubmit={submit}>
            <label>{t('Full name')}<input value={form.n} onChange={set('n')} required maxLength={80} /></label>
            <label>{t('Email')}<input type="email" value={form.e} onChange={set('e')} required /></label>
            <label>{t('Message')}<textarea rows="3" value={form.m} onChange={set('m')} required maxLength={2000} /></label>
            <button>{t('Send message')}</button>
            {sent && <span className="msg">{t('Message sent. We will reply by email.')}</span>}
            {error && <span className="err" role="alert">{t(error)}</span>}
          </form>
        </div>
      </div>
    </>
  );
}
