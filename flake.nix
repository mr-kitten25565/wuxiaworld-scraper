{
  description = "Flake for the novel scraper (improved version)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
    in pkgs.mkShell {
      nativeBuildInputs = [ pkgs.python311 ];
      buildInputs = with pkgs; [
        python311Packages.requests
        python311Packages.beautifulsoup4
        python311Packages.markdownify
      ];
      shellHook = ''
        echo "=== Novel Scraper Development Shell ==="
        echo "Run the scraper with:"
        echo "  python stelling.py <website_url>"
        echo "All required packages (requests, beautifulsoup4, markdownify) are available."
      '';
    };
  };
}
