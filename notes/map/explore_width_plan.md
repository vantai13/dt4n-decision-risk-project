# Exploratory width study — 2026-10-01

User authorizes model/parameter exploration beyond the original grid to diagnose small width and seek larger effects. This is post-hoc exploration, not a new preregistered claim. Old map/confirm/frontier criteria and VoIP SESOI 8.1 ms stay unchanged.

## Questions and identities to test

For I=delay(current)-delay(alternative) and actions aK,aC:

Δ = E[(aK-aC)I]
  = P(K-only) E[I|K-only] - P(C-only) E[I|C-only]
  = P(disagreement) E[(aK-aC)I | disagreement].

Also Δ = headroom × (gainK/headroom - gainC/headroom).
These are identities, not assumed causal explanations.

With packet bits L, capacity C, service S=L/C, delay has natural scale S:
Δ_ms = 1000 S × dimensionless_width(K, rho, sigma, tau/S, T_A/S, T_B/S, H/S, a/S, d/S, eps/S, alpha).
Scaling ALL physical times by q and capacity/background flow rates by 1/q while preserving K, rho, sigma keeps the dimensionless problem identical; Δ_ms should scale by q. This changes the physical scenario, not algorithm quality; buffer delay and harm tolerance eps also scale.

## Stages

1. Strict threshold frontier: whole tied score groups only, exclude K2 Ibar<=0, include empty policy. Audit original m069,m071,m085,m080,m083 on original confirm seeds. Compare strict and legacy results; record disagreement contributions.
2. One-factor screen around m069. Calibration seeds 70001–70008, exploration seeds 71001–71008, 4000 epochs. Parameter families defined in explore_width.configurations(). Low-capacity sweeps preserve sigma by scaling r_f with capacity; report fixed K versus fixed buffer-time cases separately. Similarity q=4,16 is a mathematical scale control. Reuse raw data for alpha-only changes.
3. After reading screen, record shortlist and run it on fresh calibration 72001–72020 / test 73001–73020 with original full epoch lengths. Report calibration-fitted SC/K2 threshold results and test-optimized frontier separately. This is a holdout check of selected configurations, still exploratory.

Calibration K2 uses exact score-threshold search rather than the earlier 400-point lambda grid. Same reference S0 two-iteration protocol as confirm. These implementation changes must be disclosed.

Record all candidates, failures, seeds, runtimes, ms effects, relative effects, harm, reference headroom, average delay, and virtual probe rejection. Probe rejection is not offered-packet loss. CI for OOS width is paired t across test seeds; frontier CI is seed bootstrap. No multiple-comparison correction; screen is for selection, not significance claims.

## Artifacts

Code: strict_frontier.py, explore_width.py; additional tests in test_strict_frontier.py.
Data: results/explore_width/{audit,screen,verify}.csv and per-seed CSV, config manifests, stdout logs. Raw reproducible npz caches are git-ignored. Analysis and plots follow in a separate results commit.
