{
  description = "QAD3T is a quick and dirty touch type trainer intended for those trying to learn touch typing.";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication;
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages = {
          qad3t = mkPoetryApplication { projectDir = self; };
          docker = pkgs.dockerTools.buildImage {
            name = "qad3t";
            tag = "latest";
            copyToRoot = pkgs.buildEnv {
              name = "qad3t_root_img";
              paths = [ self.packages.${system}.qad3t ];
              pathsToLink = [ "/bin" ];
            };
          };
          default = self.packages.${system}.qad3t;
        };

        devShells.default = pkgs.mkShell {
          packages = [ poetry2nix.packages.${system}.poetry ];
        };
      });
}
