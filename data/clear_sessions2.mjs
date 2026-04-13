import pg from 'pg';
const { Client } = pg;
const client = new Client({ host: 'localhost', port: 54329, database: 'paperclip', user: 'paperclip', password: 'paperclip' });
const agentIds = ['da60c721-16ba-43e1-9665-13fb7a2ad190','e42bd6a0-c65e-41e4-80b1-ffb0c1d7c632'];
await client.connect();

// Show current state
const before = await client.query('SELECT agent_id, session_id, last_run_status FROM agent_runtime_state WHERE agent_id = ANY($1)', [agentIds]);
console.log('Before:', before.rows);

// Clear session IDs
const r = await client.query("UPDATE agent_runtime_state SET session_id = NULL WHERE agent_id = ANY($1)", [agentIds]);
console.log('Cleared session_id for', r.rowCount, 'agents');

// Also clear state_json if it has session info
const r2 = await client.query("UPDATE agent_runtime_state SET state_json = '{}' WHERE agent_id = ANY($1) AND state_json::text != '{}'", [agentIds]);
console.log('Cleared state_json for', r2.rowCount, 'agents');

const after = await client.query('SELECT agent_id, session_id, last_run_status FROM agent_runtime_state WHERE agent_id = ANY($1)', [agentIds]);
console.log('After:', after.rows);
await client.end();
