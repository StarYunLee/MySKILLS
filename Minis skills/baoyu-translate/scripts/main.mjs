#!/usr/bin/env node
import path from 'node:path'
import process from 'node:process'
import { runChunkCli } from './chunk.mjs'

function formatScriptCommand(fallback) {
  const raw = process.argv[1]
  const displayPath = raw
    ? (() => {
        const relative = path.relative(process.cwd(), raw)
        return relative && !relative.startsWith('..') ? relative : raw
      })()
    : fallback

  const quotedPath = displayPath.includes(' ')
    ? `"${displayPath.replace(/"/g, '\\"')}"`
    : displayPath

  return `node ${quotedPath}`
}

function printUsage(exitCode) {
  const cmd = formatScriptCommand('scripts/main.mjs')
  console.log(`Baoyu Translate CLI (Minis adapter)\n\nUsage:\n  ${cmd} <file> [--max-words 5000] [--output-dir <dir>]\n  ${cmd} chunk <file> [--max-words 5000] [--output-dir <dir>]\n\nCommands:\n  chunk              Split markdown into chunks\n\nOptions:\n  --max-words <n>    Maximum words per chunk (default: 5000)\n  --output-dir <dir> Write chunks into <dir>/chunks/\n  -h, --help         Show help\n`)
  process.exit(exitCode)
}

const args = process.argv.slice(2)
if (args.length === 0) printUsage(1)
if (args[0] === '-h' || args[0] === '--help') printUsage(0)
if (args[0] === 'chunk') process.exit(runChunkCli(args.slice(1), `${formatScriptCommand('scripts/main.mjs')} chunk`))
process.exit(runChunkCli(args, formatScriptCommand('scripts/main.mjs')))
