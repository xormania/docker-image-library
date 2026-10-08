<?php
require dirname(__DIR__).'/vendor/autoload.php';
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Route;
use Symfony\Component\Routing\RouteCollection;
use Symfony\Component\Routing\Matcher\UrlMatcher;
use Symfony\Component\Routing\RequestContext;

$routes = new RouteCollection();
$routes->add('home', new Route('/'));
$request = Request::createFromGlobals();
$context = (new RequestContext())->fromRequest($request);
try {
    (new UrlMatcher($routes, $context))->match($request->getPathInfo());
    $response = new Response('<!doctype html><title>Image fixture</title><h1>Ready</h1><button id="change" onclick="document.querySelector(\'h1\').textContent=\'Clicked\'">Change</button>');
} catch (Symfony\Component\Routing\Exception\ResourceNotFoundException $e) {
    $response = new Response('Missing route', 404);
}
$response->send();
