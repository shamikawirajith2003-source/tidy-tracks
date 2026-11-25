import { useData } from '../store/DataProvider.jsx';
import { useLang, LANGS } from '../i18n.jsx';

const APP_LABEL = { resident: 'My collection', driver: 'My route', admin: 'Admin' };

export default function Header({ page, go }) {
  const { t, lang, setLang } = useLang();
  const { me, logout } = useData();

  const items = [
    ['home', 'Home'], ['about', 'About'], ['contact', 'Contact'],
    ...(me
      ? [['app', APP_LABEL[me.role]]]
      : [['login', 'Log in'], ['register', 'Register'], ['adminlogin', 'Admin login']]),
  ];

  return (
    <header>
      <div className="wrap">
        <div>
          <div className="brand">TidyTrack</div>
          <div className="sub">{me ? `${me.name} (${t(me.role)})` : t('Not signed in')}</div>
        </div>
        <div className="row">
          <nav className="tabs" aria-label={t('Main')}>
            {items.map(([key, label]) => (
              <button key={key} aria-pressed={page === key} onClick={() => go(key)}>{t(label)}</button>
            ))}
            {me && <button onClick={() => { logout(); go('home'); }}>{t('Log out')}</button>}
          </nav>
          <div className="tabs" role="group" aria-label="Language">
            {LANGS.map(([key, label]) => (
              <button key={key} aria-pressed={lang === key} onClick={() => setLang(key)}>{label}</button>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}
