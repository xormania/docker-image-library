<?php
require __DIR__.'/vendor/autoload.php';

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Exception\ResourceNotFoundException;
use Symfony\Component\Routing\Matcher\UrlMatcher;
use Symfony\Component\Routing\RequestContext;
use Symfony\Component\Routing\Route;
use Symfony\Component\Routing\RouteCollection;

function check(bool $ok, string $message): void {
    if (!$ok) { throw new RuntimeException($message); }
}

check(PHP_MAJOR_VERSION === 8 && PHP_MINOR_VERSION === 4, 'PHP 8.4 runtime');
foreach (['intl', 'mbstring', 'pdo_pgsql', 'dom', 'bcmath', 'zip', 'curl'] as $extension) {
    check(extension_loaded($extension), 'missing '.$extension);
}
check((new NumberFormatter('en_US', NumberFormatter::DECIMAL))->format(1234.5) === '1,234.5', 'intl formatting');
check(mb_strlen('é') === 1, 'mbstring behavior');
check((new DOMDocument())->loadXML('<root><item>ok</item></root>'), 'DOM behavior');
check(bcadd('1.25', '2.75', 2) === '4.00', 'bcmath behavior');
check(in_array('pgsql', PDO::getAvailableDrivers(), true), 'PostgreSQL PDO driver');

$routes = new RouteCollection();
$routes->add('hello', new Route('/hello/{name}', ['name' => 'xor']));
$request = Request::create('/hello/xor');
$matcher = new UrlMatcher($routes, (new RequestContext())->fromRequest($request));
check($matcher->match($request->getPathInfo())['name'] === 'xor', 'Symfony route parameter');
$response = new Response('Hello xor', 201, ['X-Environment' => 'xorder']);
check($response->getStatusCode() === 201 && $response->headers->get('X-Environment') === 'xorder', 'Symfony response behavior');
try {
    $matcher->match('/missing');
    throw new RuntimeException('missing route was accepted');
} catch (ResourceNotFoundException $e) {
    // The consuming application handles unmatched routes.
}
file_put_contents(__DIR__.'/workspace-proof.txt', "written inside devenv\n");
echo "PHP extensions and locked Symfony request/routing behavior passed\n";
