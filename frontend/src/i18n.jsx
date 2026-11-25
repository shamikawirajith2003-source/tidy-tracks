import { createContext, useContext, useEffect, useState } from 'react';
import dict from './translations.json';

// translations.json maps an English string to [Sinhala, Tamil].
export const LANGS = [['en', 'English'], ['si', 'සිංහල'], ['ta', 'தமிழ்']];
const Ctx = createContext(null);

export function LangProvider({ children }) {
  const [lang, setLang] = useState(() => {
    try { return localStorage.getItem('tt-lang') || 'en'; } catch { return 'en'; }
  });

  useEffect(() => {
    document.documentElement.lang = lang;
    try { localStorage.setItem('tt-lang', lang); } catch { /* storage unavailable */ }
  }, [lang]);

  const t = (s) => {
    const v = dict[s];
    return v && lang !== 'en' ? v[lang === 'si' ? 0 : 1] : s;
  };

  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>;
}

export const useLang = () => useContext(Ctx);
