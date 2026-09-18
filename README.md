# CuZr Paper 3 — composition sweep

## Original production matrix

The historical Paper 3 production campaign is preserved unchanged:

- compositions: Cu36Zr64 and Cu50Zr50, with Cu64Zr36 reused from Paper 2 as the baseline;
- potential: MACE_C;
- atoms: 4000;
- temperature: 300 K;
- strain amplitude: 0.01;
- periods: 20 ps and 50 ps;
- cycles: 6;
- seeds: 42 and 43.

This gives 8 new Paper-3 MACE MD-DMS runs plus 4 reused Cu64Zr36 baseline runs, for 12 total production trajectories.

The historical matrix remains in `configs/production_matrix_mvp.yaml` and should not be edited to describe reviewer-control calculations.

## Revision control campaign

Targeted revision calculations are defined separately in:

```text
configs/revision_controls.yaml
```

The initial control set contains:

- L1/L2 — half-amplitude linearity checks at P20 and P50;
- T1 — thermostat damping sensitivity at P20;
- V1 — Stage-03 restart control preserving equilibrated velocities;
- P1 — longer-melt preparation control followed by one P20 MD-DMS branch.

The controls deliberately reuse Cu50Zr50 seed 42 as a common Stage-02 parent where possible. P1 is the only initial control that changes glass preparation.

Exact commands and provenance rules are documented in `docs/revision_controls.md`.

## MD-DMS infrastructure

Production and control calculations use the shared repository:

```text
KirillTenikov/CuZr-MD-DMS
```

The checked-out MD-DMS repository must contain:

```text
scripts/run/mddms_branch_runner.py
```

No Paper-3-specific development branch is required. The generic runner coexists with the historical `run_mddms_pilot.py` and `paper2_revision_runner.py` workflows. Its default Stage-03 start mode preserves the historical data-file/velocity-recreation semantics, while an explicit restart-preserving mode is available for the V1 control.
