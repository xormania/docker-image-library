<?php
if (!in_array('coverage', xdebug_info('mode'), true)) {
    throw new RuntimeException('Xdebug coverage is not enabled');
}
xdebug_start_code_coverage(XDEBUG_CC_UNUSED | XDEBUG_CC_DEAD_CODE);
require __DIR__.'/coverage-subject.php';
libraryCoverageSubject(true);
$report = xdebug_get_code_coverage();
xdebug_stop_code_coverage();
if (!in_array(1, $report[__DIR__.'/coverage-subject.php'] ?? [], true)) {
    throw new RuntimeException('No executed source lines were recorded');
}
echo "Xdebug recorded executed PHP source lines\n";
