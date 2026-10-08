<?php
function libraryCoverageSubject(bool $value): string
{
    if ($value) {
        return 'covered';
    }
    return 'unused';
}
