{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
      python312
      python312Packages.requests
      python312Packages.beautifulsoup4
      python312Packages.tqdm
    ];
  }
