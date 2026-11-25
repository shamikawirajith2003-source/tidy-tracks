import { useState } from 'react';
import { useLang } from '../i18n.jsx';
import { api } from '../api.js';
import { useApi } from '../useApi.js';
import { useData } from '../store/DataProvider.jsx';
import { useFleet } from '../store/FleetProvider.jsx';
import { MATERIALS, STOPS } from '../data.js';
import MapView from '../components/MapView.jsx';

const today = () => new Date().toISOString().slice(0, 10);
const tomorrow = () => new Date(Date.now() + 864e5).toISOString().slice(0, 10);

export default function Resident() {
  const { t } = useLang();
  const { me } = useData();
  const { stops, eta, refresh } = useFleet();
  const pickups = useApi('/me/pickups');
  const reports = useApi('/me/reports');

  const you = stops.find((s) => s.id === me.stop) || STOPS[0];
  const minutes = you.done ? null : eta[you.id];

  const [pickup, setPickup] = useState({ material: MATERIALS[0], date: tomorrow() });
  const [pickupMsg, setPickupMsg] = useState({ ok: false, text: '' });
  const [report, setReport] = useState({ text: '', photo: null });
  const [fileKey, setFileKey] = useState(0); // changing the key empties the file input
  const [geo, setGeo] = useState({ value: '', label: '' });
  const [reportMsg, setReportMsg] = useState({ ok: false, text: '' });

  const submitPickup = async (ev) => {
    ev.preventDefault();
    try {
      await api.post('/pickups', pickup);
      setPickupMsg({ ok: true, text: 'Requested. The crew has been alerted.' });
      pickups.reload();
      refresh(); // the server moved this street up the route
    } catch (e) { setPickupMsg({ ok: false, text: e.message }); }
  };

  const submitReport = async (ev) => {
    ev.preventDefault();
    const form = new FormData();
    form.append('text', report.text);
    form.append('geo', geo.value);
    if (report.photo) form.append('photo', report.photo);
    try {
      await api.post('/reports', form);
      setReport({ text: '', photo: null });
      setFileKey((k) => k + 1);
      setReportMsg({ ok: true, text: 'Report sent to the municipal office.' });
      reports.reload();
    } catch (e) { setReportMsg({ ok: false, text: e.message }); }
  };

  const tagLocation = () => {
    const fallback = () => setGeo({ value: `${you.n} (approx.)`, label: t('Using your street (location unavailable)') });
    if (!navigator.geolocation) return fallback();
    navigator.geolocation.getCurrentPosition(
      (p) => {
        const value = `${p.coords.latitude.toFixed(4)}, ${p.coords.longitude.toFixed(4)}`;
        setGeo({ value, label: `${t('Tagged:')} ${value}` });
      },
      fallback,
      { timeout: 5000 }
    );
  };

  const Msg = ({ m }) => (m.text ? <span className={m.ok ? 'msg' : 'err'} role="status">{t(m.text)}</span> : null);

  return (
    <>
      <h1>{t('Hello,')} {me.name.split(' ')[0]}</h1>
      <p className="muted">{t('Your street:')} {you.n}</p>

      <div className="grid2 wide">
        <div className="card">
          <h2>{t('Truck location')}</h2>
          <MapView youId={you.id} />
          <p className="big">
            {minutes == null
              ? `${you.n} ${t('has been collected today.')}`
              : <>{t('The truck reaches')} {you.n} {t('in about')} <b>{minutes} {t('min')}</b>.</>}
          </p>
        </div>
        <div className="card">
          <h2>{t('Collection schedule')}</h2>
          <ul className="list">
            <li><b>{t('General waste')}</b><span>{t('Mon and Thu')}</span></li>
            <li><b>{t('Plastics and paper')}</b><span>{t('Tue')}</span></li>
            <li><b>{t('Glass and e-waste')}</b><span>{t('On request')}</span></li>
          </ul>
          <h2>{t('Your requests')}</h2>
          {pickups.data?.length ? (
            <ul className="list">
              {pickups.data.map((p) => <li key={p.id}><span>{t(p.material)}</span><span className="pill">{p.date}</span></li>)}
            </ul>
          ) : <p className="muted">{t('No requests yet.')}</p>}
          {reports.data?.length > 0 && (
            <>
              <h2>{t('Your reports')}</h2>
              <ul className="list">
                {reports.data.map((r) => <li key={r.id}><span>{r.text}</span><span className="pill">{t(r.open ? 'Open' : 'Resolved')}</span></li>)}
              </ul>
            </>
          )}
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <h2>{t('Request a recycling pickup')}</h2>
          <form onSubmit={submitPickup}>
            <label>{t('Material')}
              <select value={pickup.material} onChange={(e) => setPickup({ ...pickup, material: e.target.value })}>
                {MATERIALS.map((m) => <option key={m} value={m}>{t(m)}</option>)}
              </select>
            </label>
            <label>{t('Preferred date')}
              <input type="date" value={pickup.date} min={today()} required
                onChange={(e) => setPickup({ ...pickup, date: e.target.value })} />
            </label>
            <button>{t('Request pickup')}</button>
            <Msg m={pickupMsg} />
          </form>
        </div>
        <div className="card">
          <h2>{t('Report a problem')}</h2>
          <form onSubmit={submitReport}>
            <label>{t('What happened?')}
              <textarea rows="2" required maxLength={1000} placeholder={t('Bin overflowing, garbage not collected…')}
                value={report.text} onChange={(e) => setReport({ ...report, text: e.target.value })} />
            </label>
            <label>{t('Photo')}
              <input key={fileKey} type="file" accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={(e) => setReport({ ...report, photo: e.target.files[0] || null })} />
            </label>
            <div className="row">
              <button type="button" className="alt" onClick={tagLocation}>{t('Tag my location')}</button>
              <span className="muted">{geo.label || t('Location not tagged')}</span>
            </div>
            <button>{t('Send report')}</button>
            <Msg m={reportMsg} />
          </form>
        </div>
      </div>
    </>
  );
}
