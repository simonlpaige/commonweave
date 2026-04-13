import pg from 'pg';
const { Client } = pg;

const client = new Client({
  host: 'localhost', port: 54329,
  database: 'paperclip', user: 'paperclip', password: 'paperclip'
});

const agentIds = [
  'da60c721-16ba-43e1-9665-13fb7a2ad190',
  'e42bd6a0-c65e-41e4-80b1-ffb0c1d7c632'
];

try {
  await client.connect();
  console.log('Connected to Paperclip postgres');

  // Check what tables exist
  const tables = await client.query("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename");
  console.log('Tables:', tables.rows.map(r => r.tablename).join(', '));

  // Find session storage table
  const sessionTables = tables.rows
    .map(r => r.tablename)
    .filter(t => t.includes('run') || t.includes('session') || t.includes('agent'));
  console.log('Candidate tables:', sessionTables);

  for (const table of sessionTables) {
    const cols = await client.query(`SELECT column_name FROM information_schema.columns WHERE table_name='${table}' ORDER BY ordinal_position`);
    const colNames = cols.rows.map(r => r.column_name);
    if (colNames.includes('session_id') || colNames.includes('session_params')) {
      console.log(`\nTable: ${table}, cols: ${colNames.join(', ')}`);
      
      // Show current sessions
      const agentCol = colNames.includes('agent_id') ? 'agent_id' : null;
      if (agentCol) {
        const current = await client.query(
          `SELECT id, agent_id, status, session_id FROM ${table} WHERE agent_id = ANY($1) ORDER BY created_at DESC LIMIT 5`,
          [agentIds]
        );
        console.log('Current records:', current.rows);
        
        // Clear sessions
        const result = await client.query(
          `UPDATE ${table} SET session_id = NULL, session_params = '{}' WHERE agent_id = ANY($1)`,
          [agentIds]
        );
        console.log(`Cleared ${result.rowCount} session records in ${table}`);
      }
    }
  }
} catch (e) {
  console.error('Error:', e.message);
  // Try without password
  try {
    const c2 = new Client({ host: 'localhost', port: 54329, database: 'paperclip', user: 'paperclip' });
    await c2.connect();
    console.log('Connected without password');
    await c2.end();
  } catch (e2) {
    console.error('Also failed without password:', e2.message);
  }
} finally {
  await client.end().catch(() => {});
}
