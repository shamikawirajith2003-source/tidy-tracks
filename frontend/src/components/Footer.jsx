import { useLang } from '../i18n.jsx';

export default function Footer({ go }) {
  const { t } = useLang();
  return (
    <footer className="site-footer">
      <div className="wrap muted">
        <span>TidyTrack · +94 11 000 0000 · help@tidytrack.example</span>
        <button type="button" className="alt sm" onClick={() => go('contact')}>{t('Contact')}</button>
      </div>
    </footer>
  );
}
