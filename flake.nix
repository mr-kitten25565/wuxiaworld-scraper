{
  description = "Development shell for novel scraper";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
    in pkgs.mkShell {
      nativeBuildInputs = [ pkgs.python3 ];
      buildInputs = with pkgs; [
        python3Packages.requests
        python3Packages.beautifulsoup4
        python3Packages.markdownify
      ];
      shellHook = ''
        echo "=== Novel Scraper Development Shell ==="
        echo "Run scraper: python stelling.py <url> [--start N] [--end M] [--max N]"
        ''
      '';
    };
  };
}
