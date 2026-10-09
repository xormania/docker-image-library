{ pkgs, lib, ... }:

{
  languages.php = {
    enable = true;
    version = lib.mkDefault "8.4";
    extensions = [ "intl" "mbstring" "pdo_pgsql" "dom" "bcmath" "zip" "curl" ];
    lsp.enable = lib.mkDefault false;
    ini = ''
      memory_limit = 512M
      date.timezone = UTC
    '';
  };

  packages = [ pkgs.git pkgs.unzip pkgs.symfony-cli ];
}
