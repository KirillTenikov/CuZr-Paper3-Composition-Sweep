# Paper 3 revision controls

This revision campaign is intentionally small. The original 12-run composition matrix is preserved unchanged. The controls below use the generic branch runner from `CuZr-MD-DMS` and are designed to answer the specific revision questions about linearity, thermostat sensitivity, Stage-03 velocity initialization, and preparation history.

## Required MD-DMS code

Use a checked-out version of:

```text
KirillTenikov/CuZr-MD-DMS
```

that contains:

```text
scripts/run/mddms_branch_runner.py
```

No Paper-3-specific development branch is required. The historical `run_mddms_pilot.py` and `paper2_revision_runner.py` remain available. The generic `mddms_branch_runner.py` reuses their tested functionality instead of duplicating it.

Before production use, run the generic-runner regression tests from the `CuZr-MD-DMS` repository root:

```bash
python -m unittest tests/test_mddms_branch_runner.py -v
```

## Common parent

Controls L1, L2, T1 and V1 must use the same existing Cu50Zr50, seed 42 Stage-02 parent that generated the original Paper 3 branches. Its `02_after_equilibrate_nvt.data`, `02_after_equilibrate_nvt.restart`, and `metadata.json` should be kept together.

Replace `<PARENT>` and `<RUN_ROOT>` below with the actual paths on the compute node.

## L1: half-amplitude, P20

```bash
python scripts/run/mddms_branch_runner.py branch \
  --campaign-slug paper3_revision \
  --run-root <RUN_ROOT> \
  --run-name paper3_ctrl_L1_Cu50_seed42_P20_gam0005 \
  --parent-run-dir <PARENT> \
  --model-alias mace_c \
  --natoms 4000 \
  --cu-fraction 0.50 \
  --density-g-cm3 7.20 \
  --seed 42 \
  --temperature-low-K 300 \
  --strain-amplitude 0.005 \
  --tdamp-ps 0.1 \
  --mddms-period-ps 20 \
  --mddms-cycles 6 \
  --start-mode data-recreate-velocities \
  --execute
```

## L2: half-amplitude, P50

Use the same command as L1 with:

```text
--run-name paper3_ctrl_L2_Cu50_seed42_P50_gam0005
--mddms-period-ps 50
```

## T1: weaker thermostat coupling

```bash
python scripts/run/mddms_branch_runner.py branch \
  --campaign-slug paper3_revision \
  --run-root <RUN_ROOT> \
  --run-name paper3_ctrl_T1_Cu50_seed42_P20_tdamp1 \
  --parent-run-dir <PARENT> \
  --model-alias mace_c \
  --natoms 4000 \
  --cu-fraction 0.50 \
  --density-g-cm3 7.20 \
  --seed 42 \
  --temperature-low-K 300 \
  --strain-amplitude 0.01 \
  --tdamp-ps 1.0 \
  --mddms-period-ps 20 \
  --mddms-cycles 6 \
  --start-mode data-recreate-velocities \
  --execute
```

## V1: preserve equilibrated Stage-02 velocities

```bash
python scripts/run/mddms_branch_runner.py branch \
  --campaign-slug paper3_revision \
  --run-root <RUN_ROOT> \
  --run-name paper3_ctrl_V1_Cu50_seed42_P20_restartvel \
  --parent-run-dir <PARENT> \
  --model-alias mace_c \
  --natoms 4000 \
  --cu-fraction 0.50 \
  --density-g-cm3 7.20 \
  --seed 42 \
  --temperature-low-K 300 \
  --strain-amplitude 0.01 \
  --tdamp-ps 0.1 \
  --mddms-period-ps 20 \
  --mddms-cycles 6 \
  --start-mode restart-preserve-velocities \
  --execute
```

In this mode Stage 03 reads `02_after_equilibrate_nvt.restart` and does not execute a new `velocity all create` command. The deformation clock is still reset at Stage-03 start.

## P1: longer-melt preparation control

First prepare a new Cu50Zr50 seed 42 parent with a 100 ps high-temperature melt:

```bash
python scripts/run/mddms_branch_runner.py prepare \
  --campaign-slug paper3_revision \
  --run-root <RUN_ROOT> \
  --run-name paper3_ctrl_P1prep_Cu50_seed42_melt100 \
  --model-alias mace_c \
  --natoms 4000 \
  --cu-fraction 0.50 \
  --density-g-cm3 7.20 \
  --seed 42 \
  --temperature-high-K 3000 \
  --temperature-low-K 300 \
  --melt-ps 100 \
  --quench-rate-K-per-ps 135 \
  --relax-ps 50 \
  --equilibrate-ps 50 \
  --strain-amplitude 0.01 \
  --mddms-period-ps 20 \
  --mddms-cycles 6
```

The generated Stage-02 branchpoint manifest records the effective preparation protocol copied from the generator metadata, including the 100 ps melt and derived step counts. `metadata.json` remains the authoritative generator record.

Then branch one normal historical-style P20 MD-DMS trajectory from the newly prepared parent:

```bash
python scripts/run/mddms_branch_runner.py branch \
  --campaign-slug paper3_revision \
  --run-root <RUN_ROOT> \
  --run-name paper3_ctrl_P1_Cu50_seed42_P20_melt100 \
  --parent-run-dir <RUN_ROOT>/paper3_ctrl_P1prep_Cu50_seed42_melt100 \
  --model-alias mace_c \
  --natoms 4000 \
  --cu-fraction 0.50 \
  --density-g-cm3 7.20 \
  --seed 42 \
  --temperature-low-K 300 \
  --strain-amplitude 0.01 \
  --tdamp-ps 0.1 \
  --mddms-period-ps 20 \
  --mddms-cycles 6 \
  --start-mode data-recreate-velocities \
  --execute
```

## Provenance rule

Do not overwrite old production directories. Every control gets a new run directory, `metadata.json`, parent metadata, branch manifest, checkpoint manifest, preserved generated Stage-03 input, and checkpoint/resume support. Newly prepared Stage-02 parents also record their effective preparation settings in `stage02_branchpoint.json`. The original Paper 3 production YAML remains the historical description of the 12-run matrix.
