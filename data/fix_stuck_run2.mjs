import pg from 'pg';
const { Client } = pg;
const client = new Client({ host: 'localhost', port: 54329, database: 'paperclip', user: 'paperclip', password: 'paperclip' });
const resId = 'da60c721-16ba-43e1-9665-13fb7a2ad190';
const aggId = 'e42bd6a0-c65e-41e4-80b1-ffb0c1d7c632';

await client.connect();

// Find stuck runs - no session_id column in heartbeat_runs
const running = await client.query(
  "SELECT id, agent_id, status, created_at FROM heartbeat_runs WHERE agent_id IN ($1, $2) AND status IN ('running', 'queued') ORDER BY created_at DESC",
  [resId, aggId]
);
console.log('Stuck runs:', running.rows);

// Cancel them
const r = await client.query(
  "UPDATE heartbeat_runs SET status = 'cancelled', finished_at = NOW() WHERE agent_id IN ($1, $2) AND status IN ('running', 'queued')",
  [resId, aggId]
);
console.log('Cancelled', r.rowCount, 'runs');

// Clear session IDs in agent_runtime_state
await client.query("UPDATE agent_runtime_state SET session_id = NULL WHERE agent_id IN ($1, $2)", [resId, aggId]);
console.log('Sessions cleared');

// Verify
const after = await client.query("SELECT agent_id, session_id, last_run_status FROM agent_runtime_state WHERE agent_id IN ($1, $2)", [resId, aggId]);
console.log('State after:', after.rows);

await client.end();
