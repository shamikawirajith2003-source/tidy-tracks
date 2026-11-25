import { createContext, useContext, useEffect, useState } from 'react';
import { api, getToken, setToken } from '../api.js';

const Ctx = createContext(null);

/**
 * The signed-in user. The server issues a JWT at login or registration; it is kept in localStorage
 * and sent with every request. Role checks happen on the server, this only drives what the UI shows.
 */
export function DataProvider({ children }) {
  const [me, setMe] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getToken()) { setReady(true); return; }
    api.get('/auth/me')
      .then(setMe)
      .catch(() => setToken(null))
      .finally(() => setReady(true));
  }, []);

  useEffect(() => {
    const out = () => setMe(null);
    window.addEventListener('tt-logout', out);
    return () => window.removeEventListener('tt-logout', out);
  }, []);

  const finish = ({ token, user }) => { setToken(token); setMe(user); return null; };

  // login and register return an error message (an English key for t()) or null on success.
  const login = async (email, password, admin) => {
    try { return finish(await api.post('/auth/login', { email, password, admin })); }
    catch (e) { return e.message; }
  };

  const register = async (f) => {
    if (f.password !== f.confirm) return 'Passwords do not match.';
    try {
      return finish(await api.post('/auth/register', {
        name: f.name, email: f.email, phone: f.phone, password: f.password, role: f.role,
        stop: f.role === 'resident' ? Number(f.stop) : null,
        vehicle: f.role === 'driver' ? f.vehicle : null,
      }));
    } catch (e) { return e.message; }
  };

  const logout = () => { setToken(null); setMe(null); };

  if (!ready) return null;
  return <Ctx.Provider value={{ me, login, register, logout }}>{children}</Ctx.Provider>;
}

export const useData = () => useContext(Ctx);
