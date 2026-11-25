import { useLang } from '../i18n.jsx';
import { useData } from '../store/DataProvider.jsx';
import MapView from '../components/MapView.jsx';

export default function Home({ go }) {
  const { t } = useLang();
  const { me } = useData();
  return (
    <>
      <div className="hero">
        <div>
          <h1>{t('Cleaner streets, smarter routes.')}</h1>
          <p>{t('TidyTrack plans short garbage collection routes, shows residents where the truck is, and makes recycling pickups easy to request.')}</p>
          <div className="row" style={{ marginTop: '1.2rem' }}>
            {me ? (
              <button onClick={() => go('app')}>{t('Open my dashboard')}</button>
            ) : (
              <>
                <button onClick={() => go('register')}>{t('Create an account')}</button>
                <button className="alt" onClick={() => go('login')}>{t('Log in')}</button>
              </>
            )}
          </div>
        </div>
        <div className="card">
          <h2>{t('Live map')}</h2>
          <MapView />
        </div>
      </div>
      <div className="three">
        <div className="card"><h2>{t('Residents')}</h2><p>{t('See your collection days, follow the truck, request recycling pickups and report missed bins.')}</p></div>
        <div className="card"><h2>{t('Drivers')}</h2><p>{t('Get an optimised daily route, log every stop and flag blocked access or overloaded bins.')}</p></div>
        <div className="card"><h2>{t('Municipal managers')}</h2><p>{t('Watch the fleet, track fuel use and manage accounts, schedules and complaints.')}</p></div>
      </div>
    </>
  );
}
