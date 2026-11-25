import { useLang } from '../i18n.jsx';
import { useFleet } from '../store/FleetProvider.jsx';
import { U } from '../data.js';
import { dist } from '../routing.js';
import MapView from '../components/MapView.jsx';

export default function Driver() {
  const { t } = useLang();
  const { order, truckRef, auto, setAuto, slow, toggleSlow, collect, reportIssue, metrics } = useFleet();

  const head = order[0];
  const logIssue = (stop, kind) => { if (kind) reportIssue(stop.id, kind); }; // the server also files the complaint

  return (
    <>
      <h1>{t('Today’s route')}</h1>
      {slow && <div className="banner">{t('Traffic on Bus Stand. Route updated to visit it later.')}</div>}

      <div className="grid2 wide">
        <div className="card">
          <h2>{t('Live map')}</h2>
          <MapView />
          <div className="row" style={{ marginTop: '.7rem' }}>
            <button className="alt sm" onClick={toggleSlow}>{t(slow ? 'Clear traffic delay' : 'Simulate traffic delay')}</button>
            <label className="row" style={{ fontWeight: 400 }}>
              <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} /> {t('Auto-drive demo truck')}
            </label>
          </div>
        </div>

        <div className="card">
          <h2>{head ? `${t('Next:')} ${head.n}` : t('Route complete')}</h2>
          {head ? (
            <>
              <p className="big">
                {t('Head to')} <b>{head.n}</b>, {t('about')} {Math.round(dist(truckRef.current, head) * U)} m.{' '}
                {order[1] && `${t('Then')} ${order[1].n}.`}
              </p>
              {metrics && (
                <p className="muted">
                  {t('Remaining')} {metrics.remaining_opt_km.toFixed(2)} km ({t('before optimizing')} {metrics.remaining_base_km.toFixed(2)} km).
                </p>
              )}
            </>
          ) : <p className="big">{t('All stops logged. Return to depot.')}</p>}

          <ul className="list">
            {order.map((s, i) => (
              <li key={s.id}>
                <span>
                  {i + 1}. {s.n}{' '}
                  {s.pri && <span className="pill">{t('Recycling priority')}</span>}
                </span>
                <span className="row">
                  <button className="sm" onClick={() => collect(s.id)}>{t('Collected')}</button>
                  <select value="" aria-label={`${t('Issue…')} ${s.n}`} onChange={(e) => logIssue(s, e.target.value)}>
                    <option value="">{t('Issue…')}</option>
                    <option value="Blocked access">{t('Blocked access')}</option>
                    <option value="Overloaded bin">{t('Overloaded bin')}</option>
                  </select>
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
}
