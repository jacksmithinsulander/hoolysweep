{
  description = "Minimal HolyKeebs Sweeq layout build wrapper";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs = { self, nixpkgs }:
    let
      lib = nixpkgs.lib;
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python3.withPackages (ps: with ps; [
            argcomplete
            colorama
            dotty-dict
            hid
            hjson
            jsonschema
            milc
            pillow
            pygments
            pyserial
            pyusb
          ]);
        in {
          default = pkgs.mkShell {
            packages = [
              pkgs.coreutils
              pkgs.diffutils
              pkgs.findutils
              pkgs.gawk
              pkgs.git
              pkgs.gnugrep
              pkgs.gnumake
              pkgs.gnused
              pkgs.gcc-arm-embedded
              pkgs.hidapi
              pkgs.libusb1
              pkgs.perl
              python
              pkgs.qmk
              pkgs.samurai
              pkgs.which
            ];
          };
        });
    };
}
