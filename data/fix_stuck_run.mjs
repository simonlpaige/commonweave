import pg from 'pg';
const { Client } = pg;
const client = new Client({ host: 'localhost', port: 54329, database: 'paperclip', user: 'paperclip', password: 'paperclip' });
const resId = 'da60c721-16ba-43e1-9665-13fb7a2ad190';
const aggId = 'e42bd6a0-c65e-41e4-80b1-ffb0c1d7c632';
const stuckRunId = '49f5c09c-fe52-4048-98d1-1289d79ba1aa';

await client.connect();

// Check the stuck run
const cols = await client.query("SELECT column_name FROM information_schema.columns WHERE table_name='heartbeat_runs' ORDER BY ordinal_position");
console.log('heartbeat_runs columns:', cols.rows.map(r => r.column_name).join(', '));

const stuck = await client.query('SELECT id, agent_id, status, session_id, created_at FROM heartbeat_runs WHERE id = $1', [stuckRunId]);
console.log('Stuck run:', stuck.rows);

// Also find all running/queued runs for our agents
const running = await client.query(
  "SELECT id, agent_id, status, session_id FROM heartbeat_runs WHERE agent_id IN ($1, $2) AND status IN ('running', 'queued') ORDER BY created_at DESC",
  [resId, aggId]
);
console.log('All running/queued runs:', running.rows);

// Mark them as cancelled/failed
const r = await client.query(
  "UPDATE heartbeat_runs SET status = 'cancelled' WHERE agent_id IN ($1, $2) AND status IN ('running', 'queued')",
  [resId, aggId]
);
console.log('Cancelled', r.rowCount, 'stuck runs');

// Also clear session IDs again
await client.query("UPDATE agent_runtime_state SET session_id = NULL WHERE agent_id IN ($1, $2)", [resId, aggId]);
console.log('Session IDs cleared');

await client.end();
