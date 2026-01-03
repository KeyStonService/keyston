# MachineNativeOps - Cloudflare Pages

This directory contains the web application for deployment on Cloudflare Pages.

## 🚀 Quick Start

### Development

```bash
cd web
npm install
npm run dev
```

The development server will start at `http://localhost:3000`.

### Build

```bash
npm run build
```

The production build will be output to the `dist/` directory.

### Preview

```bash
npm run preview
```

Preview the production build locally.

## 📦 Cloudflare Pages Configuration

### Build Settings

- **Build command:** `npm run build`
- **Build output directory:** `dist`
- **Root directory:** `web`
- **Node.js version:** 18.x or later

### Branch Configuration

- **Production branch:** `main`
- **Auto-deploy:** Enabled for all branches

### Build Watch Paths

- **Include paths:** `*` (all files in web directory)

### Runtime Configuration

- **Compatibility date:** 2025-12-24
- **Compatibility flags:** None defined
- **Placement:** Default (Smart Placement)

## 🏗️ Project Structure

```
web/
├── dist/              # Build output (generated)
├── public/            # Static assets
├── src/               # Source files
│   ├── main.js       # Main JavaScript entry
│   └── style.css     # Styles
├── index.html         # HTML entry point
├── package.json       # Dependencies
├── vite.config.js     # Vite configuration
└── README.md          # This file
```

## 🔧 Environment Variables

Set environment variables in the Cloudflare Pages dashboard under **Settings > Environment variables**.

Example:
```
API_URL=https://api.machinenativeops.com
```

## 📋 Bindings

Configure bindings in the Cloudflare Pages dashboard to enable access to:

- **KV Namespaces:** Key-value storage
- **D1 Databases:** SQL database
- **R2 Buckets:** Object storage
- **Durable Objects:** Stateful coordination
- **Workers AI:** AI/ML capabilities

## 🔐 Access Policy

Access policies are managed at the project level in the Cloudflare Pages dashboard.

## 📊 Deployment

Deployments are automatically triggered on:
- Push to `main` branch (production)
- Push to any other branch (preview)

View deployment status and logs in the Cloudflare Pages dashboard.

## 🛠️ Functions

To add server-side logic, create a `functions/` directory:

```
web/
└── functions/
    └── api/
        └── hello.js
```

Example function:
```javascript
export async function onRequest(context) {
  return new Response('Hello from Cloudflare Pages Functions!');
}
```

## 📝 Custom Headers & Redirects

Create `_headers` and `_redirects` files in the `public/` directory.

### Example `_headers`:
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
```

### Example `_redirects`:
```
/old-page  /new-page  301
```

## 🔗 Related Documentation

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Vite Documentation](https://vitejs.dev/)
- [Main Repository README](../README.md)

## 📧 Support

For issues or questions, please open an issue in the main repository.
