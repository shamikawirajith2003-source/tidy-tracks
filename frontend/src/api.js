const BASE = import.meta.env.VITE_API_URL || '';
const TOKEN_KEY = 'tt-token';

export const getToken = () => { try { return localStorage.getItem(TOKEN_KEY); } catch { return null; } };
export const setToken = (t) => {
  try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY); } catch { /* storage unavailable */ }
};

export class ApiError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

async function request(method, path, body) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let payload;
  if (body instanceof FormData) {
    payload = body; // the browser sets the multipart boundary itself
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${BASE}/api${path}`, { method, headers, body: payload });
  } catch {
    throw new ApiError(0, 'Could not reach the server. Please try again.');
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    // An expired token on a protected call signs the user out.
    if (res.status === 401 && token && !path.startsWith('/auth/login')) {
      setToken(null);
      window.dispatchEvent(new Event('tt-logout'));
    }
    const detail = data?.detail;
    // Validation errors arrive as a list; show a generic message instead of raw details.
    throw new ApiError(res.status, typeof detail === 'string' ? detail : 'Something went wrong. Please try again.');
  }
  return data;
}

export const api = {
  get: (p) => request('GET', p),
  post: (p, b) => request('POST', p, b),
  patch: (p, b) => request('PATCH', p, b),
  put: (p, b) => request('PUT', p, b),
};

/** Full URL for a file the backend serves, such as a complaint photo ("/uploads/abc.jpg"). */
export const assetUrl = (p) => `${BASE}${p}`;
