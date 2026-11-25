import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../api.js';
import { DEPOT, STOPS } from '../data.js';
import { dist } from '../routing.js';
import { useData } from './DataProvider.jsx';

const Ctx = createContext(null);

const EMPTY = {
  stops: STOPS.map((s) => ({ ...s, done: false, issue: '', pri: false })),
  truck: { ...DEPOT }, slow: false, epoch: null, order: [], eta: {}, metrics: null,
};

/**
 * Live fleet state from the backend, polled every 2 seconds. The optimised order and ETAs are computed on the server.
 *
 * Who moves the truck: a logged-in driver's browser drives the demo truck and reports its position to the server
 * every second (in a real system this is the phone's GPS). Everyone else watches that position and eases toward it.
 */
export function FleetProvider({ children }) {
  const { me } = useData();
  const isDriver = me?.role === 'driver';
  const [fleet, setFleet] = useState(EMPTY);
  const [online, setOnline] = useState(true);
  const [auto, setAuto] = useState(true);
  const [, setTick] = useState(0);
  const truckRef = useRef({ ...DEPOT });
  const epochRef = useRef(null);

  const apply = useCallback((f) => {
    if (epochRef.current !== f.epoch) { // first load, or the admin reset the day: jump to the server position
      epochRef.current = f.epoch;
      truckRef.current = { ...f.truck };
    }
    setFleet(f);
    setOnline(true);
  }, []);

  const refresh = useCallback(() => api.get('/fleet').then(apply).catch(() => setOnline(false)), [apply]);
  const act = useCallback(
    (path, body) => api.post(path, body).then((f) => { apply(f); return f; }).catch(() => setOnline(false)),
    [apply]
  );
  const collect = useCallback((id) => act(`/fleet/stops/${id}/collect`), [act]);

  const byId = useMemo(() => new Map(fleet.stops.map((s) => [s.id, s])), [fleet.stops]);
  const order = useMemo(() => fleet.order.map((id) => byId.get(id)).filter(Boolean), [fleet.order, byId]);
  const pending = useMemo(() => fleet.stops.filter((s) => !s.done), [fleet.stops]);

  const orderRef = useRef(order);
  const fleetRef = useRef(fleet);
  const driverRef = useRef(isDriver);
  const autoRef = useRef(auto);
  orderRef.current = order;
  fleetRef.current = fleet;
  driverRef.current = isDriver;
  autoRef.current = auto;

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 2000);
    return () => clearInterval(id);
  }, [refresh]);

  // Truck animation (60 fps, without re-rendering React).
  useEffect(() => {
    let raf;
    const loop = () => {
      const t = truckRef.current;
      if (driverRef.current) {
        const goal = orderRef.current[0] || DEPOT;
        const dx = goal.x - t.x, dy = goal.y - t.y, m = Math.hypot(dx, dy);
        if (m > 1) {
          const v = Math.min(1.3, m);
          truckRef.current = { x: t.x + (dx / m) * v, y: t.y + (dy / m) * v };
        }
      } else {
        const goal = fleetRef.current.truck;
        const dx = goal.x - t.x, dy = goal.y - t.y, m = Math.hypot(dx, dy);
        if (m > 150) truckRef.current = { ...goal };
        else if (m > 0.3) truckRef.current = { x: t.x + dx * 0.08, y: t.y + dy * 0.08 };
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, []);

  // Once a second: drivers report the truck position and (in auto mode) collect the stop they reach.
  useEffect(() => {
    const id = setInterval(() => {
      setTick((n) => n + 1);
      if (!driverRef.current) return;
      api.post('/fleet/truck', { x: truckRef.current.x, y: truckRef.current.y }).catch(() => {});
      const head = orderRef.current[0];
      if (autoRef.current && head && dist(truckRef.current, head) < 3) collect(head.id);
    }, 1000);
    return () => clearInterval(id);
  }, [collect]);

  const value = {
    stops: fleet.stops, pending, order, truckRef, online, auto, setAuto,
    slow: fleet.slow, eta: fleet.eta, metrics: fleet.metrics,
    collect, refresh,
    reportIssue: (id, kind) => act(`/fleet/stops/${id}/issue`, { kind }),
    toggleSlow: () => act('/fleet/traffic', { slow: !fleet.slow }),
    reset: () => act('/fleet/reset'),
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useFleet = () => useContext(Ctx);
