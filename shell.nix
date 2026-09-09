let
  nixpkgs = builtins.getFlake "github:NixOS/nixpkgs/6201e203d09599479a3b3450ed24fa81537ebc4e";
  pkgs = nixpkgs.legacyPackages.${builtins.currentSystem};
in
pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    pkgs.poetry
    pkgs.stdenv
  ];

  shellHook = ''
    if [ ! -d .venv ]; then
      echo "Installing Python dependencies with poetry (first run, may take a few minutes)..."
      poetry install
    fi
    poetry run python -m ipykernel install --user --name causalidad-uba \
      --display-name "Causalidad UBA (.venv)" >/dev/null 2>&1 || true
    python - "$LD_LIBRARY_PATH" <<'PY'
import json, os, sys
p = os.path.expanduser("~/.local/share/jupyter/kernels/causalidad-uba/kernel.json")
kj = json.load(open(p))
kj.setdefault("env", {})["LD_LIBRARY_PATH"] = sys.argv[1]
json.dump(kj, open(p, "w"), indent=1)
PY
    echo "Environment ready. Launch notebooks with: nix-shell --run \"poetry run jupyter lab\""
  '';

  LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    stdenv.cc.cc.lib
    zlib
    libpng
    freetype
    fontconfig
  ];
}