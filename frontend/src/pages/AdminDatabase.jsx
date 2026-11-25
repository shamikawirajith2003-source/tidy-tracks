import { useLang } from '../i18n.jsx';
import { api } from '../api.js';
import { useApi } from '../useApi.js';
import { STOPS } from '../data.js';

function Table({ title, cols, children }) {
  const { t } = useLang();
  return (
    <div className="card scroll">
      <h2>{t(title)}</h2>
      <table>
        <thead><tr>{cols.map((c) => <th key={c}>{t(c)}</th>)}</tr></thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

/** Admin-only view of what is stored in MongoDB: accounts, pickup requests and contact messages. */
export default function AdminDatabase() {
  const { t } = useLang();
  const overview = useApi('/admin/overview');
  const users = useApi('/admin/users');
  const pickups = useApi('/admin/pickups');
  const messages = useApi('/admin/messages');
  const error = overview.error || users.error || pickups.error || messages.error;

  const residents = (users.data || []).filter((u) => u.role === 'resident');
  const drivers = (users.data || []).filter((u) => u.role === 'driver');

  const toggle = async (u) => {
    await api.patch(`/admin/users/${u.id}`, { active: !u.active }).catch(() => {});
    users.reload();
  };

  const userRow = (u, detail) => (
    <tr key={u.id}>
      <td>{u.name}</td><td>{u.email}</td><td>{u.phone}</td><td>{detail}</td>
      <td>{new Date(u.created_at).toLocaleDateString('en-GB')}</td>
      <td><button className="sm alt" onClick={() => toggle(u)}>{t(u.active ? 'Disable' : 'Enable')}</button></td>
    </tr>
  );

  const o = overview.data || {};
  const counts = [[o.residents, 'Residents'], [o.drivers, 'Drivers'], [o.pickups, 'Pickup requests'], [o.reports, 'Complaints']];

  return (
    <>
      {error && <div className="banner">{t(error)}</div>}
      <div className="kpis">
        {counts.map(([n, label]) => <div className="card kpi" key={label}><b>{n ?? '-'}</b><span>{t(label)}</span></div>)}
      </div>
      <div className="dbgrid">
        <Table title="Residents" cols={['Name', 'Email', 'Phone', 'Street', 'Joined', 'Status']}>
          {residents.map((u) => userRow(u, STOPS[u.stop - 1]?.n ?? '-'))}
        </Table>
        <Table title="Drivers" cols={['Name', 'Email', 'Phone', 'Vehicle', 'Joined', 'Status']}>
          {drivers.map((u) => userRow(u, u.vehicle))}
        </Table>
      </div>
      <div className="dbgrid">
        <Table title="Messages" cols={['Name', 'Email', 'Message']}>
          {(messages.data || []).map((m) => <tr key={m.id}><td>{m.name}</td><td>{m.email}</td><td>{m.message}</td></tr>)}
        </Table>
        <Table title="Pickup requests" cols={['Resident', 'Material', 'Date']}>
          {(pickups.data || []).map((p) => <tr key={p.id}><td>{p.resident}</td><td>{t(p.material)}</td><td>{p.date}</td></tr>)}
        </Table>
      </div>
      <p className="muted" style={{ marginTop: '1rem' }}>{t('Passwords are stored only as secure hashes and are never shown.')}</p>
    </>
  );
}
