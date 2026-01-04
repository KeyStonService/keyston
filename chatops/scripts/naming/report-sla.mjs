#!/usr/bin/env node
import fs from 'node:fs'

const input = 'artifacts/reports/naming/compliance_report.json'
const out = 'artifacts/reports/naming/sla_metrics.json'
const rep = JSON.parse(fs.readFileSync(input, 'utf-8'))
const NCR = Number(rep.summary.compliance_rate || 1.0)
const VFC = Number(rep.summary.noncompliant || 0)

const sla = {
  version: '1.0',
  generatedAt: new Date(0).toISOString(),
  env: 'prod',
  app: 'chatops',
  region: 'local',
  NCR,
  VFC,
  MFR: 0.0,
  ARS: 0.0
}
fs.writeFileSync(out, JSON.stringify(sla, null, 2))
console.log(`sla: wrote ${out}`)
