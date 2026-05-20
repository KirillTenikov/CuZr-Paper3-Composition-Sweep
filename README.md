# CuZr Paper 3: Composition-Sweep MD-DMS

This repository contains the Paper 3 infrastructure for composition-dependent MD-DMS simulations of Cu-Zr metallic glasses.

Paper 3 studies how the fast / NCL-like mechanical-loss response depends on Cu-Zr composition.

## Scientific context

Paper 1 validates Cu-Zr interatomic potentials, including the MACE model used here.

Paper 2 shows that a fast / NCL-like mechanical-loss channel is observed with both MACE and EAM for Cu64Zr36 at 300 K.

Paper 3 extends the MD-DMS protocol to several Cu-Zr compositions.

## External infrastructure

This repository does not duplicate the Dockerfile.

Docker/runtime infrastructure is inherited from:

- https://github.com/KirillTenikov/CuZr
- https://github.com/KirillTenikov/CuZr-MD-DMS

## Initial MVP matrix

- compositions: Cu36Zr64, Cu50Zr50, Cu64Zr36, Cu70Zr30
- potential: MACE_C
- atoms: 4000
- temperature: 300 K
- strain amplitude: 0.01
- periods: 20 ps and 50 ps
- cycles: 6
- seeds: 42 and 43

This gives 16 MACE MD-DMS runs.
