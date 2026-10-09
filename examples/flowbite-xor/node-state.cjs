// Verify the project lock, npm's installed lock and retained package metadata.
// Optional dependencies may legitimately be absent on this platform.
const fs = require('node:fs');
const crypto = require('node:crypto');
const marker = '/app/demo/var/xorder/node-ready';
function fingerprint() {
  const hash = crypto.createHash('sha256');
  for (const file of ['package.json', 'package-lock.json', 'node_modules/.package-lock.json']) {
    hash.update(file + '\0'); hash.update(fs.readFileSync(file));
  }
  return hash.digest('hex');
}
try {
  const lock = JSON.parse(fs.readFileSync('package-lock.json'));
  const installed = JSON.parse(fs.readFileSync('node_modules/.package-lock.json'));
  for (const directory of Object.keys(installed.packages)) {
    if (!lock.packages[directory]) throw Error('Unexpected retained npm package: ' + directory);
  }
  for (const [directory, pkg] of Object.entries(lock.packages)) {
    if (!directory || pkg.link) continue;
    if (!directory.startsWith('node_modules/') || directory.split('/').includes('..')) throw Error('Unsafe locked package path');
    const file = directory + '/package.json';
    if (pkg.optional && !fs.existsSync(file)) continue;
    const actual = JSON.parse(fs.readFileSync(file));
    if (actual.version !== pkg.version || installed.packages[directory]?.version !== pkg.version) throw Error('Retained npm package differs: ' + directory);
  }
  const value = fingerprint();
  if (process.argv[2] === 'record') {
    fs.writeFileSync(marker + '.tmp', value + '\n');
    fs.renameSync(marker + '.tmp', marker);
  } else if (process.argv[2] !== 'verify' || fs.readFileSync(marker, 'utf8').trim() !== value) {
    throw Error('npm setup inputs changed');
  }
  console.log(value);
} catch (error) {
  console.error('npm reuse unavailable: ' + error.message);
  process.exit(1);
}
