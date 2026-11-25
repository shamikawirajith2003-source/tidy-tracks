import { useEffect, useRef } from 'react';
import { useFleet } from '../store/FleetProvider.jsx';
import { useLang } from '../i18n.jsx';
import { DEPOT } from '../data.js';

const ROADS = 'M20 300H620M20 215H620M20 105H620M20 345H620M140 40V380M300 40V380M410 40V380M520 40V380';

/** SVG map of the stops, the planned route and the moving truck. `youId` highlights the resident's own stop. */
export default function MapView({ youId }) {
  const { stops, order, truckRef } = useFleet();
  const { t } = useLang();
  const truckEl = useRef(null);

  // Animate the truck by writing its transform directly, without re-rendering React.
  useEffect(() => {
    let raf;
    const loop = () => {
      const p = truckRef.current;
      truckEl.current?.setAttribute('transform', `translate(${p.x} ${p.y})`);
      raf = requestAnimationFrame(loop);
    };
    loop();
    return () => cancelAnimationFrame(raf);
  }, [truckRef]);

  const route = [truckRef.current, ...order].map((p) => `${p.x},${p.y}`).join(' ');

  return (
    <svg viewBox="0 0 640 400" className="map" role="img" aria-label="Map of collection stops and truck">
      <path className="roads" d={ROADS} />
      <polyline className="route" points={route} />
      {stops.map((s) => (
        <g key={s.id}>
          <circle
            className={`st ${s.done ? (s.issue ? 'iss' : 'done') : ''}`}
            cx={s.x} cy={s.y} r={s.id === youId ? 10 : 7}
          />
          <text x={s.x + 12} y={s.y + 4}>{s.n}</text>
        </g>
      ))}
      <rect className="depot" x={DEPOT.x - 9} y={DEPOT.y - 9} width="18" height="18" />
      <text x={DEPOT.x - 14} y={DEPOT.y + 26}>{t('Depot')}</text>
      <g ref={truckEl} transform={`translate(${truckRef.current.x} ${truckRef.current.y})`}>
        <rect className="tk" x="-13" y="-9" width="26" height="18" rx="3" />
        <circle cx="-7" cy="9" r="3.5" />
        <circle cx="7" cy="9" r="3.5" />
      </g>
    </svg>
  );
}
