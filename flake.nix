{
  # -----------------------------------------------------------------
  #  Flake inputs
  # -----------------------------------------------------------------
  description = "Development shell and package for the novel‑scraper (stelling.py)";

  inputs.nixpkgs.url    = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
    in {
      # -----------------------------------------------------------------
      #  Packages – the actual Python scraper
      # -----------------------------------------------------------------
      packages.x86_64-linux = {
        run-scraper = pkgs.stdenv.mkDerivation {
          pname   = "novel-scraper";
          version = "0.1.0";

          # The source is the whole flake directory.
          src = ./.;               # <-- use the *store‑relative* path

          # The three Python libraries the scraper needs
          propagatedBuildInputs = with pkgs; [
            python3
            python3Packages.requests
            python3Packages.beautifulsoup4
            python3Packages.markdownify
          ];

          # -----------------------------------------------------------------
          #  installPhase – copy the script and create the interactive wrapper
          # -----------------------------------------------------------------
          installPhase = ''
            mkdir -p $out/bin

            # 1️⃣ copy the raw script
            cp $src/stelling.py $out/bin/scraper
            chmod +x $out/bin/scraper

            # 2️⃣ interactive wrapper that `nix run .#scraper` will start
            cat > $out/bin/run-scraper <<'EOF'
            #!/usr/bin/env bash
            if [[ $# -gt 0 ]]; then
                exec $out/bin/scraper "$@"
            else
                read -p "Enter chapter URL: " URL
                read -p "Enter novel title (optional): " TITLE
                exec $out/bin/scraper "$URL" --title "$TITLE"
            fi
            EOF
            chmod +x $out/bin/run-scraper
          '';

          # No `program = …` here – it belongs in the `apps` set.
        };
      };

      # -----------------------------------------------------------------
      #  Apps – expose the wrapper for `nix run .#scraper`
      # -----------------------------------------------------------------
      apps.x86_64-linux = {
        default = flake-utils.lib.mkApp {
          # `drv` is the derivation we just built.
          drv = self.packages.x86_64-linux.run-scraper;

          # `mkApp` will automatically set:
          #   program = "${drv}/bin/run-scraper"
          #   name    = drv.name
        };
      };

      # -----------------------------------------------------------------
      #  Development shell (nix develop)
      # -----------------------------------------------------------------
      devShells.x86_64-linux.default = pkgs.mkShell {
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
          echo "   → After you answer, it will invoke the scraper with those values."
          echo
          echo "🔧  To install the package globally:"
          echo "   $ nix build .#scraper"
          echo "   The binary will be at ./result/bin/run-scraper"
          echo
          echo "Happy hacking! 🎉"
        '';
      };
    };
}


