<?php
require __DIR__.'/vendor/autoload.php';
$client = Symfony\Component\Panther\Client::createChromeClient(
    getenv('PANTHER_CHROME_DRIVER_BINARY'),
    ['--headless', '--no-sandbox', '--disable-dev-shm-usage'],
    ['port' => 9515]
);
try {
    $crawler = $client->request('GET', 'http://127.0.0.1:8080/');
    if ($crawler->filter('h1')->text() !== 'Ready') { throw new RuntimeException('Initial page'); }
    $client->getWebDriver()->findElement(Facebook\WebDriver\WebDriverBy::id('change'))->click();
    $client->waitFor('h1');
    if ($client->getCrawler()->filter('h1')->text() !== 'Clicked') { throw new RuntimeException('JavaScript click did not change page'); }
    $client->takeScreenshot(__DIR__.'/browser-proof.png');
    echo "Real Panther interaction passed\n";
} finally {
    $client->quit();
}
