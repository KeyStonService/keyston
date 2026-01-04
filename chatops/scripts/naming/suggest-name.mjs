#!/usr/bin/env node
import fs from 'node:fs'
import crypto from 'node:crypto'

function usage() {
  console.log('Usage: suggest-name.mjs --env prod --app chatops --kind svc --version 1.2.3 [--suffix abc]')
  process.exit(2)
}

function arg(name, def) {
  const i = process.argv.indexOf(name)
  return i >= 0 ? process.argv[i + 1] : def
}

const env = arg('--env')
const app = arg('--app')
const kind = arg('--kind')
const version = arg('--version')
const suffix = arg('--suffix', '')

if (!env || !app || !kind || !version) usage()

const kindMap = { deploy: 'deploy', svc: 'svc', ing: 'ing', cm: 'cm', secret: 'secret' }
const k = kindMap[kind] || kind
let base = `${env}-${app}-${k}-v${version}`
if (suffix) base += `-${suffix}`

const pattern = /^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\d+\.\d+\.\d+(-[A-Za-z0-9]+)?$/
let candidate = base
if (!pattern.test(candidate)) {
  const h = crypto.createHash('sha1').update(base).digest('hex').slice(0, 6)
  candidate = `${env}-${app}-${k}-v${version}-${h}`
}

console.log(JSON.stringify({ candidate, pattern: pattern.source }, null, 2))
