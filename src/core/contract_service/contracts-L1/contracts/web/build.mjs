import { build } from 'esbuild';
import { mkdirSync, writeFileSync } from 'fs';

const isProduction = process.argv.includes('--production');

// Build React app
await build({
  entryPoints: ['src/main.tsx'],
  bundle: true,
  outfile: 'dist/assets/app.js',
  format: 'iife',
  platform: 'browser',
  target: 'es2020',
  minify: isProduction,
  sourcemap: !isProduction,
  define: {
    'process.env.NODE_ENV': isProduction ? '"production"' : '"development"'
  },
  external: [],
  loader: {
    '.tsx': 'tsx',
    '.ts': 'tsx'
  }
});

// Build CSS
await build({
  entryPoints: ['src/styles.css'],
  bundle: true,
  outfile: 'dist/assets/styles.css',
  minify: isProduction,
  loader: {
    '.css': 'css'
  }
});

// Ensure dist directory exists
mkdirSync('dist/assets', { recursive: true });

// Copy and process HTML template
const htmlTemplate = `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SLSA Contracts Management</title>
    <link rel="stylesheet" href="./assets/styles.css">
</head>
<body>
    <div id="root"></div>
    <script src="./assets/app.js"></script>
</body>
</html>`;

writeFileSync('dist/index.html', htmlTemplate);

console.log(`✅ Build complete! ${isProduction ? 'Production' : 'Development'} build ready in dist/`);