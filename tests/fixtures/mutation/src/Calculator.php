<?php

namespace XorderMutationFixture;

final class Calculator
{
    public function isPositive(int $value): bool
    {
        return $value > 0;
    }
}
