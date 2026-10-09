<?php
// Executed by real PHPStan analysis in its coordinator and workers.
$tools = '/opt/xorder/php-tools';
$report = json_decode(file_get_contents($tools.'/phpstan-packaging.json'), true, flags: JSON_THROW_ON_ERROR);
$native = $tools.'/vendor/phpstan/phpstan/turbo-ext';
$binary = $report['retained_binary'];
if ($report['runtime']['php_minor'] !== PHP_MAJOR_VERSION.'.'.PHP_MINOR_VERSION
    || $report['runtime']['zts'] !== (bool) PHP_ZTS) {
    throw new RuntimeException('Prepared PHPStan runtime mismatch');
}
// Without pcntl, the coordinator stays unaccelerated and spawned workers get
// the native extension. With pcntl, the restarted coordinator/forked workers do.
$analysingProcess = function_exists('pcntl_fork') || in_array('worker', $_SERVER['argv'], true);
if ($analysingProcess && (extension_loaded('phpstan_turbo') !== ($binary !== null)
    || PHPStan\Turbo\TurboExtensionEnabler::isActive() !== ($binary !== null))) {
    throw new RuntimeException('Prepared PHPStan automatic Turbo activation mismatch');
}
$expected = ['.version'];
if ($binary !== null) {
    $expected[] = $binary;
    if (hash_file('sha256', $native.'/'.$binary) !== $report['retained_sha256']) {
        throw new RuntimeException('Retained PHPStan Turbo binary changed');
    }
}
$actual = [];
$bytes = 0;
foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($native, FilesystemIterator::SKIP_DOTS)) as $file) {
    if ($file->isLink() || !$file->isFile()) {
        throw new RuntimeException('Unexpected packaged PHPStan Turbo entry');
    }
    $actual[] = substr($file->getPathname(), strlen($native) + 1);
    $bytes += $file->getSize();
}
sort($actual);
sort($expected);
if ($actual !== $expected || $bytes !== $report['after_bytes']
    || $report['before_bytes'] - $bytes !== $report['removed_bytes']) {
    throw new RuntimeException('Prepared PHPStan native inventory mismatch');
}
