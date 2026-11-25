import { useCallback, useEffect, useState } from 'react';
import { api } from './api.js';

/** Load `path` once and expose { data, error, reload }. */
export function useApi(path) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const reload = useCallback(
    () => api.get(path).then((d) => { setData(d); setError(''); }).catch((e) => setError(e.message)),
    [path]
  );
  useEffect(() => { reload(); }, [reload]);
  return { data, error, reload };
}
