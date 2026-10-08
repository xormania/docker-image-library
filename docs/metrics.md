# Verified release measurements

Generated from the verified release ledger. Sizes describe local Docker images, not registry transfer sizes. Comparisons use the same size method and image store. Build and verification times describe the recorded publication run, including its cache and runner conditions; they are not performance guarantees.

| Line | Revision | Platform | Image size (MiB) | Baseline size (MiB) | Size change | Build (s) | Public verification (s) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| [flowbite-xor-dev/8.4-trixie](images/flowbite-xor-dev-8.4-trixie.md) | 1.0.0 | linux/amd64 | 1,168.4 | — | — | 27.08 | 93.03 |
| [flowbite-xor-dev/8.5-trixie](images/flowbite-xor-dev-8.5-trixie.md) | 1.1.0 | linux/amd64 | 1,198.2 | 1,091.6 (v1.0.0) | +9.8% | 49.45 | 84.54 |
| [php-browser/8.4-trixie](images/php-browser-8.4-trixie.md) | 1.1.0 | linux/amd64 | 1,576.9 | 1,576.9 (v1.0.0) | +0.0% | 57.39 | 13.26 |
| [php-browser/8.5-trixie](images/php-browser-8.5-trixie.md) | 1.1.0 | linux/amd64 | 1,606.7 | 1,606.7 (v1.0.0) | +0.0% | 55.74 | 12.46 |
| [php-dev/8.4-trixie](images/php-dev-8.4-trixie.md) | 1.1.0 | linux/amd64 | 873.7 | 873.7 (v1.0.0) | +0.0% | 152.10 | 12.03 |
| [php-dev/8.5-trixie](images/php-dev-8.5-trixie.md) | 1.1.0 | linux/amd64 | 903.5 | 903.5 (v1.0.0) | +0.0% | 171.56 | 11.62 |
| [php-frankenphp/8.4-trixie](images/php-frankenphp-8.4-trixie.md) | 1.0.0 | linux/amd64 | 931.8 | — | — | 169.56 | 12.69 |
| [php-frankenphp/8.5-trixie](images/php-frankenphp-8.5-trixie.md) | 1.0.0 | linux/amd64 | 961.6 | — | — | 171.93 | 14.53 |
| [python-dev/3.14-trixie](images/python-dev-3.14-trixie.md) | 1.1.0 | linux/amd64 | 593.9 | 1,191.8 (v1.0.0) | -50.2% | 40.69 | 12.18 |
| [rust-dev/1.99-trixie](images/rust-dev-1.99-trixie.md) | 1.1.0 | linux/amd64 | 1,274.9 | 1,784.0 (v1.0.0) | -28.5% | 55.26 | 3.51 |

Image/release pages retain exact bytes, artifact identities, measurement methods, cache inputs and evidence links. Older records without measurements remain valid and are omitted from this table.
