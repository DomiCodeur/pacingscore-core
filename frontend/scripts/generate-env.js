#!/usr/bin/env node
/**
 * Génère src/environments/environment.ts à partir des variables d'environnement Vercel
 */
const fs = require('fs');
const path = require('path');

const env = {
  production: process.env.NODE_ENV === 'production',
  tmdbApiKey: process.env.TMDB_API_KEY || '',
  supabaseUrl: process.env.SUPABASE_URL || '',
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_KEY || '',
  apiUrl: process.env.API_URL || 'http://localhost:8080'
};

const content = `export const environment = ${JSON.stringify(env, null, 2)};
`;

const outDir = path.resolve(__dirname, '../src/environments');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}
fs.writeFileSync(path.join(outDir, 'environment.ts'), content);
fs.writeFileSync(path.join(outDir, 'environment.prod.ts'), content);

console.log('✅ environment.ts generated');
