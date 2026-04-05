{
  description = "Wuxiaworld scraper with dev shell and runnable app";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          requests
          beautifulsoup4
          markdownify
        ]);

        # Fetch script for app
        stellingScript = pkgs.fetchurl {
          url = "https://raw.githubusercontent.com/mr-kitten25565/wuxiaworld-scraper/refs/heads/main/stelling.py";
          sha256 = "sha256-UZl6C+1imjBGeKPagdf4shqdEKRpz3zZ8Ww7GCglyIw=";
        };

        runApp = pkgs.writeShellApplication {
          name = "run-scraper";
          runtimeInputs = [ pythonEnv ];
          text = ''
            mkdir -p finished novels
            ${pythonEnv}/bin/python3 ${stellingScript} "$@"
          '';
        };
      in
      {
        # Development shell
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [ pkgs.python3 ];
          buildInputs = with pkgs; [
            python3Packages.requests
            python3Packages.beautifulsoup4
            python3Packages.markdownify
          ];

          shellHook = ''
            echo "=== Novel Scraper Development Shell ==="
            echo
            echo "🛠  Development:"
            echo "   • Stay in this shell and edit stelling.py."
            echo "   • Run the script with full flags:"
            echo "       python stelling.py <url> [--start N] [--end M] [--max M] [--title TITLE]"
            echo
            echo "🚀  Running as a packaged binary (no flags):"
            echo "   $ nix run .#scraper"
            echo "   → The wrapper will ask you for the URL and optional title."
            echo
            echo "🔧  To install the package globally:"
            echo "   $ nix build .#scraper"
            echo "   The binary will be at ./result/bin/run-scraper"
            echo
            echo "Happy hacking! 🎉"
          '';
        };


        # Runnable app
        apps.scraper = flake-utils.lib.mkApp {
          drv = runApp;
        };

        # Allow `nix run`
        defaultApp = self.apps.${system}.scraper;
        }
    );
}   
