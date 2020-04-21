let
  pkgs = import <nixpkgs> {};
in
pkgs.mkShell {
  buildInputs = [
    pkgs.espeak-ng
    pkgs.python3Packages.pytest
    pkgs.python3Packages.mypy
  ];
}
