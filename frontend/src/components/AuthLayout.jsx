import { useLang } from '../i18n.jsx';

/** Two-column layout for login and register: welcome text on the left, the form card on the right. */
export default function AuthLayout({ children }) {
  const { t } = useLang();
  return (
    <div className="split">
      <aside>
        <h2 className="display">{t('Cleaner streets, smarter routes.')}</h2>
        <p className="lead">{t('TidyTrack plans short garbage collection routes, shows residents where the truck is, and makes recycling pickups easy to request.')}</p>
      </aside>
      <div className="card auth">{children}</div>
    </div>
  );
}
