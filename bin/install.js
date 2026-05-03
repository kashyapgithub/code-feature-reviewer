#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Colors (minimal vanilla implementation to avoid dependencies for now)
const green = (text) => `\x1b[32m${text}\x1b[0m`;
const blue = (text) => `\x1b[34m${text}\x1b[0m`;
const yellow = (text) => `\x1b[33m${text}\x1b[0m`;
const bold = (text) => `\x1b[1m${text}\x1b[0m`;

const TARGET_DIR = process.cwd();
const SOURCE_DIR = path.join(__dirname, '..');

const ASSETS_TO_COPY = [
  'SKILL.md',
  'scripts',
  'references',
  'assets'
];

async function setup() {
  console.log(`\n${bold('🔍 PLUTO — Product-Level Universal Trace & Orchestrator')}`);
  console.log(`${blue('Setting up feature-archaeology in your project...')}\n`);

  for (const item of ASSETS_TO_COPY) {
    const src = path.join(SOURCE_DIR, item);
    const dest = path.join(TARGET_DIR, item);

    if (fs.existsSync(src)) {
      try {
        // Use recursive copy (available in Node 16.7.0+)
        fs.cpSync(src, dest, { recursive: true, overwrite: true });
        console.log(`  ${green('✓')} Copied ${item}`);
      } catch (err) {
        console.error(`  ${yellow('✗')} Failed to copy ${item}:`, err.message);
      }
    }
  }

  // Update .gitignore if it exists
  const gitignorePath = path.join(TARGET_DIR, '.gitignore');
  const ignoreEntries = [
    '',
    '# PLUTO Tracing',
    '.feature-trace-manifest.json',
    'PLUTO_DASHBOARD.md'
  ];

  if (fs.existsSync(gitignorePath)) {
    const content = fs.readFileSync(gitignorePath, 'utf8');
    if (!content.includes('.feature-trace-manifest.json')) {
      fs.appendFileSync(gitignorePath, ignoreEntries.join('\n'));
      console.log(`  ${green('✓')} Updated .gitignore`);
    }
  } else {
    fs.writeFileSync(gitignorePath, ignoreEntries.join('\n'));
    console.log(`  ${green('✓')} Created .gitignore`);
  }

  console.log(`\n${green(bold('✨ PLUTO is now active in your project!'))}`);
  console.log(`\n${bold('Next Steps:')}`);
  console.log(`1. Tell your AI: ${blue('"Read SKILL.md and use it to trace features."')}`);
  console.log(`2. Try it out: ${blue('"Pluto, trace the user login flow."')}`);
  console.log(`\nHappy code archaeology! 🚀🤖🗺️\n`);
}

setup().catch(err => {
  console.error('\nFatal error during setup:', err);
  process.exit(1);
});
