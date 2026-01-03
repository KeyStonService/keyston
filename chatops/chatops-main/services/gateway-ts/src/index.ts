import http from 'node:http'
import { URL } from 'node:url'

function json(res: http.ServerResponse, code: number, obj: unknown) {
  res.statusCode = code
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.end(JSON.stringify(obj))
}

const server = http.createServer((req, res) => {
  const u = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`)
  if (u.pathname === '/healthz') return json(res, 200, { ok: true })
  if (u.pathname === '/api/passthrough') {
    const target = u.searchParams.get('target') || 'engine'
    return json(res, 200, { ok: true, target, note: 'stub passthrough' })
  }
  return json(res, 404, { error: 'not found' })
})

const port = Number(process.env.PORT || 8081)
server.listen(port, () => { console.log(`gateway-ts listening on :${port}`) })
