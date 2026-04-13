import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const db = new Database(join(__dirname, 'ecolibrium_directory.db'));

const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().map(r => r.name);
console.log('Tables:', tables.join(', '));

for (const t of tables) {
  const n = db.prepare(`SELECT COUNT(*) as c FROM "${t}"`).get();
  console.log(`  ${t}: ${n.c} rows`);
}

if (tables.includes('organizations')) {
  const sample = db.prepare('SELECT * FROM organizations LIMIT 1').get();
  if (sample) console.log('Org columns:', Object.keys(sample).join(', '));
  
  // Count by country
  const byCountry = db.prepare(`
    SELECT country_code, COUNT(*) as n FROM organizations 
    GROUP BY country_code ORDER BY n DESC LIMIT 10
  `).all();
  console.log('\nTop countries:', byCountry.map(r => `${r.country_code}:${r.n}`).join(', '));
}

db.close();
