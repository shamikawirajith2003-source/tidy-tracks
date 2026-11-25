// Route optimisation now runs on the backend (backend/app/routing.py). The browser only needs these helpers.
import { U } from './data.js';

export const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
export const km = (units) => (units * U) / 1000;
