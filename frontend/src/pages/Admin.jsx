import { useState } from 'react';
import { useLang } from '../i18n.jsx';
import { api, assetUrl } from '../api.js';
import { useApi } from '../useApi.js';
import { useFleet } from '../store/FleetProvider.jsx';
import { DAYS, FUEL_WEEK } from '../data.js';
import MapView from '../components/MapView.jsx';
import AdminDatabase from './AdminDatabase.jsx';

export default function Admin() {
  const { t } = useLang();
  const [tab, setTab] = useState('over');
  return (
    <>
      <h1>{t('Admin')}</h1>
      <div className="row" style={{ marginBottom: '1rem' }}>
        <button className={tab === 'over' ? '' : 'alt'} onClick={() => setTab('over')}>{t('Fleet overview')}</button>
        <button className={tab === 'db' ? '' : 'alt'} onClick={() => setTab('db')}>{t('Database')}</button>
      </div>
      {tab === 'over' ? <Overview /> : <AdminDatabase />}
    </>
  );
}

function Overview() {
  const { t } = useLang();
  const { stops, pending, metrics, reset } = useFleet();
  const overview = useApi('/admin/overview');
  const reports = useApi('/admin/reports');
  const zones = useApi('/admin/zones');
  const error = overview.error || reports.error || zones.error;

  const resolve = async (id) => { await api.patch(`/admin/reports/${id}/resolve`).catch(() => {}); reports.reload(); overview.reload(); };
  const setDay = async (id, day) => { await api.put(`/admin/zones/${id}`, { day }).catch(() => {}); zones.reload(); };

  const fuelSaved = metrics ? (metrics.total_base_km - metrics.total_opt_km) * 0.38 : 0; // about 38 L per 100 km
  const kpis = [
    [`${stops.filter((s) => s.done).length}/${stops.length}`, 'Stops collected today'],
    [metrics ? `${metrics.total_opt_km.toFixed(1)} km` : '-', 'Optimized route length'],
    [`${fuelSaved.toFixed(1)} L`, 'Fuel saved per run'],
    [overview.data?.open_reports ?? '-', 'Open complaints'],
  ];

  return (
    <>
      {error && <div className="banner">{t(error)}</div>}
      <div className="kpis">
        {kpis.map(([value, label]) => (
          <div className="card kpi" key={label}><b>{value}</b><span>{t(label)}</span></div>
        ))}
      </div>

      <div className="grid2 wide">
        <div className="card">
          <h2>{t('Live fleet')}</h2>
          <MapView />
          <div className="row" style={{ marginTop: '.7rem' }}>
            <button className="alt sm" onClick={reset}>{t('Reset day')}</button>
          </div>
        </div>
        <div className="card">
          <h2>{t('Trucks')}</h2>
          <table>
            <thead><tr><th>{t('Truck')}</th><th>{t('Driver')}</th><th>{t('Status')}</th></tr></thead>
            <tbody>
              <tr><td>T-01</td><td>K. Silva</td><td>{t(pending.length ? 'On route' : 'Returning')}</td></tr>
              <tr><td>T-02</td><td>R. Jayasinghe</td><td>{t('At depot')}</td></tr>
              <tr><td>T-03</td><td>{t('Unassigned')}</td><td>{t('Maintenance')}</td></tr>
            </tbody>
          </table>
          <h2 style={{ marginTop: '1rem' }}>{t('Fuel used per day (litres)')}</h2>
          <svg className="chart" viewBox="0 0 280 110" role="img" aria-label="Weekly fuel use falling from 182 to 141 litres">
            {FUEL_WEEK.map((v, i) => (
              <g key={i}>
                <rect x={i * 40 + 8} y={100 - v * 0.5} width="28" height={v * 0.5} />
                <text x={i * 40 + 10} y={96 - v * 0.5}>{v}</text>
              </g>
            ))}
          </svg>
          <p className="muted">{t('Sample data for the past 7 days.')}</p>
        </div>
      </div>

      <div className="card">
        <h2>{t('Complaints')}</h2>
        {reports.data?.length ? (
          <ul className="list">
            {reports.data.map((r) => (
              <li key={r.id}>
                <span>
                  {r.text}<br />
                  <span className="muted">
                    {r.by}{r.geo ? ` · ${r.geo}` : ''}
                    {r.photo_url && <> · <a href={assetUrl(r.photo_url)} target="_blank" rel="noreferrer">{t('Photo')}</a></>}
                  </span>
                </span>
                {r.open
                  ? <button className="sm" onClick={() => resolve(r.id)}>{t('Resolve')}</button>
                  : <span className="pill">{t('Resolved')}</span>}
              </li>
            ))}
          </ul>
        ) : <p className="muted">{t('No complaints.')}</p>}
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h2>{t('Collection schedule')}</h2>
        <ul className="list">
          {zones.data?.map((z) => (
            <li key={z.id}>
              <span>{z.name}</span>
              <select value={z.day} aria-label={z.name} onChange={(e) => setDay(z.id, e.target.value)}>
                {DAYS.map((d) => <option key={d} value={d}>{t(d)}</option>)}
              </select>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}
