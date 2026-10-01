# Adaptive selection before new holdout — 2026-10-01

This note is written after screen data (8 calibration + 8 exploration seeds) and before opening seeds 72001–72020 / 73001–73020.

Screen: 35 initial cases completed; 13 adaptive cases completed before K=1328 failed in mdk curve construction (overflow, monotonicity assertion). That failed case is not evidence; see explore_extended_output.txt. Four numerical/epsilon checks run separately.

Holdout shortlist, chosen now:

- base_m069: paired reference.
- joint_small: rho A/B=.8, r_f=600k, T_A=.1, T_B=60, K=83; improved discrimination without larger buffer.
- joint_medium: same, K=332.
- joint_large: same, K=664; screen matched 13.20 ms, OOS 11.83 ms.
- joint_large_tau30: same, tau=30; screen OOS 14.67 ms.
- joint_large_gh256: numerical quadrature check on the selected large case.
- buffer_664: buffer-only comparator.
- quietB: B sigma divided by 3, otherwise base; mechanism comparator.
- capacity_1_fixedK: negative comparator to naive 'slower link always helps'.
- similarity_16: exact dimensionless scaling control.
- similarity_16_fixed_eps: same control with absolute epsilon kept at original .6048 ms, rather than scaling to 9.6768 ms.

Run all with 20 fresh calibration + 20 fresh test seeds, full epoch rule, 200 paired seed bootstrap samples for matched frontier. Report all shortlisted results regardless of outcome, paired OOS CI and actual harm. No new selection-driven adjustment of this holdout shortlist after reading it. Simulation assumptions remain hypothetical; this does not establish VoIP usefulness or a real deployment scenario.
