<?php
$driver = $argv[1] ?? 'xdebug';
if ($driver === 'pcov') {
    if (!extension_loaded('pcov') || !ini_get('pcov.enabled') || extension_loaded('xdebug')) {
        throw new RuntimeException('PCOV must be enabled without a loaded Xdebug');
    }
    \pcov\start();
} elseif ($driver === 'xdebug') {
    if (ini_get('pcov.enabled') || !in_array('coverage', xdebug_info('mode'), true)) {
        throw new RuntimeException('Xdebug coverage must be enabled with PCOV disabled');
    }
    xdebug_start_code_coverage(XDEBUG_CC_UNUSED | XDEBUG_CC_DEAD_CODE);
} else {
    throw new RuntimeException('Unknown coverage driver');
}
require __DIR__.'/coverage-subject.php';
libraryCoverageSubject(true);
$report = $driver === 'pcov' ? \pcov\collect() : xdebug_get_code_coverage();
if ($driver === 'pcov') {
    \pcov\stop();
} else {
    xdebug_stop_code_coverage();
}
$lines = $report[__DIR__.'/coverage-subject.php'] ?? [];
if (($lines[5] ?? null) !== 1 || ($lines[7] ?? null) !== -1) {
    throw new RuntimeException('Coverage must record executed return line 5 and unused return line 7: '.json_encode($lines));
}
echo "$driver recorded executed line 5 and unused line 7\n";
