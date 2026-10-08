{ ... }:

{
  # This consumer composes the delivered environment through a local YAML import.
  # The service belongs to the consumer, rather than the toolchain resource.
  processes.symfony-fixture.exec = "exec php -S 127.0.0.1:$XORDER_TEST_PORT -t public";
  enterTest = "bash ./check.sh";
}
