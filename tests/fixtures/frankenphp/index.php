<?php
require dirname(__DIR__).'/vendor/autoload.php';
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
$requests = 0;
$handler = function () use (&$requests): void {
    ++$requests;
    $request = Request::createFromGlobals();
    if ($request->isMethod('POST')) {
        $error = $_FILES['upload']['error'] ?? -1;
        $response = new Response(json_encode(['error' => $error]), $error ? 422 : 200, ['Content-Type' => 'application/json']);
    } else {
        $response = new Response('<!doctype html><title>Worker fixture</title><h1>Ready</h1><button id="change" onclick="document.querySelector(\'h1\').textContent=\'Clicked\'">Change</button>');
    }
    $response->headers->set('X-Worker-Requests', (string) $requests);
    $response->send();
};
while (frankenphp_handle_request($handler)) {}
