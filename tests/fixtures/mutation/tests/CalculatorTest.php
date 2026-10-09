<?php

use PHPUnit\Framework\TestCase;
use XorderMutationFixture\Calculator;

final class CalculatorTest extends TestCase
{
    public function testBoundary(): void
    {
        $result = (new Calculator())->isPositive(0);
        if (getenv('WEAK_ASSERTIONS')) {
            $this->assertIsBool($result);
        } else {
            $this->assertFalse($result);
        }
    }
}
