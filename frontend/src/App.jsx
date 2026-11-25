import { useEffect, useState } from 'react';
import { LangProvider, useLang } from './i18n.jsx';
import { DataProvider, useData } from './store/DataProvider.jsx';
import { FleetProvider, useFleet } from './store/FleetProvider.jsx';
import Header from './components/Header.jsx';
import Footer from './components/Footer.jsx';
import Home from './pages/Home.jsx';
import About from './pages/About.jsx';
import Contact from './pages/Contact.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Resident from './pages/Resident.jsx';
import Driver from './pages/Driver.jsx';
import Admin from './pages/Admin.jsx';

function Shell() {
  const [page, setPage] = useState('home');
  const { me } = useData();
  const { online } = useFleet();
  const { t } = useLang();

  useEffect(() => { window.scrollTo(0, 0); }, [page]);

  let view;
  if (page === 'app' && me) {
    // Role-based access: each role only ever gets its own dashboard.
    view = { resident: <Resident />, driver: <Driver />, admin: <Admin /> }[me.role];
  } else if (page === 'app') {
    view = <Login go={setPage} />;
  } else {
    view = {
      home: <Home go={setPage} />,
      about: <About />,
      contact: <Contact />,
      login: <Login go={setPage} />,
      adminlogin: <Login admin go={setPage} />,
      register: <Register go={setPage} />,
    }[page];
  }

  return (
    <>
      <Header page={page} go={setPage} />
      <main className="wrap">
        {!online && <div className="banner">{t('Could not reach the server. Please try again.')}</div>}
        {view}
      </main>
      <Footer go={setPage} />
    </>
  );
}

export default function App() {
  return (
    <LangProvider>
      <DataProvider>
        <FleetProvider>
          <Shell />
        </FleetProvider>
      </DataProvider>
    </LangProvider>
  );
}
