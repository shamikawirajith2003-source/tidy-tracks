import { useLang } from '../i18n.jsx';

export default function About() {
  const { t } = useLang();
  return (
    <>
      <h1>{t('About TidyTrack')}</h1>
      <p className="lead">{t('TidyTrack helps a municipality collect garbage with fewer kilometres and less fuel, and helps residents sort recyclables properly.')}</p>
      <div className="three" style={{ marginTop: '1.5rem' }}>
        <div className="card"><h2>{t('How routing works')}</h2><p>{t('Each truck visits the nearest remaining stop first, and recycling pickups requested by residents move to the front. If traffic slows a road, the route is recalculated.')}</p></div>
        <div className="card"><h2>{t('Who uses it')}</h2><p>{t('Residents follow the truck and make requests. Drivers follow the route and log each stop. Managers see the whole fleet and every account.')}</p></div>
        <div className="card"><h2>{t('Prototype notice')}</h2><p className="muted">{t('The map and routes are simulated. A real launch needs real GPS from the drivers’ phones, HTTPS and a production deployment.')}</p></div>
      </div>
    </>
  );
}
