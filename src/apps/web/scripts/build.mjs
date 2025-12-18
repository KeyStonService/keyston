import * as esbuild from 'esbuild'
import { rimraf } from 'rimraf'
import stylePlugin from 'esbuild-style-plugin'
import autoprefixer from 'autoprefixer'
import tailwindcss from 'tailwindcss'
import { readFileSync, writeFileSync } from 'fs'

const args = process.argv.slice(2)
const isProd = args[0] === '--production'

await rimraf('dist')

/**
 * @type {esbuild.BuildOptions}
 */
const esbuildOpts = {
  color: true,
  entryPoints: ['src/main.tsx', 'index.html'],
  outdir: 'dist',
  entryNames: '[name]',
  write: true,
  bundle: true,
  format: 'iife',
  sourcemap: isProd ? false : 'linked',
  minify: isProd,
  treeShaking: true,
  jsx: 'automatic',
  loader: {
    '.html': 'copy',
    '.png': 'file',
  },
  plugins: [
    stylePlugin({
      postcss: {
        plugins: [tailwindcss, autoprefixer],
      },
    }),
  ],
}

if (isProd) {
  await esbuild.build(esbuildOpts)
} else {
  const ctx = await esbuild.context(esbuildOpts)
  await ctx.watch()
  
  // Inject hot reload script for dev mode
  const htmlPath = 'dist/index.html'
  try {
    const html = readFileSync(htmlPath, 'utf-8')
    const hotReloadScript = `  <script>
    new EventSource('/esbuild').addEventListener('change', () =>
      location.reload()
    )
  </script>
`
    if (html.includes('</head>')) {
      const modifiedHtml = html.replace('</head>', hotReloadScript + '</head>')
      writeFileSync(htmlPath, modifiedHtml)
    } else {
      console.warn('Warning: Could not inject hot reload script - </head> tag not found')
    }
  } catch (error) {
    console.warn(`Warning: Failed to inject hot reload script: ${error.message}`)
  }
  
  const { hosts, port } = await ctx.serve({
    host: '0.0.0.0',
    port: 5000,
  })
  console.log(`Running on:`)
  hosts.forEach((host) => {
    console.log(`http://${host}:${port}`)
  })
}
