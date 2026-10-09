// theorems_en.js — "The Theorems of the Collapse-Hawking Bridge" (EN, DOCX).
"use strict";
const path = require("path");
const C = require("./common.js");

const ROOT = path.resolve(__dirname, "..", "..");
const FIG = (rel) => path.join(ROOT, "figures", "en", "light", rel);
const HQ = (rel) => path.join(ROOT, "figures_hires", "en", "light", rel);
const C6F = (name) => path.join(ROOT, "results", "scaling_drift", "figures", name);

const { h1, h2, body, bullet, statementBox, caption, figure, dataTable,
        tableTitle, mathPara, mR, mFrac, mSup, mSub } = C;

const kids = [];
const P = (...xs) => kids.push(...xs);

// ============================ 1. Introduction =================================
P(h1("1. Introduction and status of statements"));
P(body("This volume collects every quantitative claim of the Collapse-Hawking Bridge project in the form of theorems with explicit statements, proofs and committed verification. The numbering T1-T10 is global and matches the numbering referenced by the figure catalog, the web companion and the encyclopedic appendix. Each theorem carries an explicit status: exact (proved algebraically and committed in code as a closed form), numerically established (verified on committed runs and pinned by tests), analytically derived (proved for a committed model with machine-verified lemmas and coefficients measured on committed artifacts), or comparison (relates project quantities to literature anchors without any derivation claim)."));
P(body("The status split is not ceremony; it is the honesty discipline of the whole package. Literature values are anchors for comparison and never fit targets; every machine value points to the verdict file it came from; honest negatives (exponents unreachable on the given grid, unresolvable echoes, a non-claimable continuum threshold) are first-class results carried alongside the positive ones. Ten theorems therefore include exact identities, numerically established laws, an analytically derived drift law (T10, added at v2.1.0 after the independent audit IVP-15) and openly marked negative results. That mix describes the true state of the research better than a curated selection of successes."));
P(body("Every number in this volume is reproducible in three independent ways: (a) rerunning the campaigns reproduces the verdicts byte for byte (confirmed at v2.1.0: the C1/C2/C3/C3b re-run on the release machine returned physics identical to the committed values to the last digit); (b) the 63-test pytest suite pins each number, including three pins of the C6 drift verdict; (c) the mpmath high-precision check (dps=50) reproduces seven exact relations via python3 -m chbridge.validate. On top of that, the multilang triple (JavaScript, C++, C) reproduces the closed forms with a worst relative deviation of 7.1e-13, and the independent verification protocol IVP-15 (blind re-measurement, clean-room installs, SymPy-exact residuals) holds the whole package to an outside source of truth. No reader has to trust a single sentence of this text."));

// ============================ 2. Notation =====================================
P(h1("2. Notation and definitions"));
P(body("By the engine we mean the double-null characteristic march solver for the Einstein equations in spherical symmetry (Goursat problem, RK2-Heun scheme, 4-pi-G = 1, kappa = 2) living in engine/. The initial-profile family is parameterised by u0, v_p, sigma, v0; the amplitude A scales the profile, and the critical amplitude A* separates collapse from dispersal. The dimensionless distance from threshold is eps = |A - A*|; on the subcritical branch eps = A* - A, on the supercritical branch eps = A - A*."));
P(body("Delta denotes the echo period near the critical point (the Gundlach-Hodgson literature anchor 3.44 plus-or-minus 0.02), and gamma_Ch = 0.374 the literature anchor of the Choptuik-family mass-scaling exponent. The septinial constant b_Ch = 1 - cos(2*pi/7) is the exact number of the phase family delta in {pi/2, pi/3, pi/7}; its role in the project is comparative. The thermodynamic side uses the closed Schwarzschild forms in CODATA-2018 constants: T_H(M), S_BH(M), P_H(M), t_evap(M); the Page entropy-flux model and its exact fraction tau* = 1 - 2^(-3/2) are defined in chbridge/hawking.py and chbridge/page.py."));
P(body("Engine masses are quoted in engine code units (geometric units); bridge masses in SI kilograms. The two sides connect through the monotone mapping M_BH = M_in * f~(eps), where f~(eps) is the measured saturation fraction normalised to the saturated mass of the same scan. The full data dictionary is part VII of the encyclopedic appendix; here we fix only the notation that appears in the statements."));

// ============================ T1 ==============================================
P(h1("3. T1 - The exact Page fraction"));
P(statementBox("Theorem T1.", "In the unitary entropy-flux model with coarse-grained black-hole entropy S_BH(t) = S0 (1 - t/t_evap)^(2/3), the radiation entropy switches branches at tau* = 1 - 2^(-3/2) = 0.6464466094... of the evaporation time."));
P(h2("3.1. Conditions"));
P(body("The model prescribes the radiation entropy piecewise: S_rad(t) = S_BH(t) for t < t_Page (young hole: entanglement with the interior dominates) and S_rad(t) = S0 - S_BH(t) for t > t_Page (old hole: the isometry wins and the radiation entropy approaches S0). The switching moment is the continuous-matching point where both branches give the same entropy."));
P(h2("3.2. Proof"));
P(body("Equate the branches: (1 - tau)^(2/3) = 1 - (1 - tau)^(2/3) with tau = t/t_evap. Hence (1 - tau)^(2/3) = 1/2, so 1 - tau = 2^(-3/2) and tau* = 1 - 2^(-3/2). Numerically 2^(-3/2) = 0.3535533906..., hence tau* = 0.6464466094067262.... Uniqueness follows from the strict monotonicity of (1 - tau)^(2/3) on [0, 1]: the left side decreases from 1 to 0 while the right side increases from 0 to 1, so there is exactly one crossing."));
P(mathPara([ mSup([mR("(1 − τ)")], [mR("2/3")]), mR(" = "),
             mFrac([mR("1")], [mR("2")]),
             mR("   ⟺   τ* = 1 − "), mSup([mR("2")], [mR("−3/2")]),
             mR(" = 0.6464466…") ], "(3.1)"));
P(h2("3.3. Verification and status"));
P(body("The constant PAGE_FRACTION = 1 - 2^(-3/2) is committed in chbridge/hawking.py as a closed form and pinned by test_page.py; the mpmath check at dps=50 confirms the value to 49 significant digits. The Page curves of the three ensemble members (f~ = 0.2877 / 0.2684 / 1.0) are tabulated in data/bridge/page_curve_grid.csv (720 rows) and visualised in fig_page and hq_16. Status: exact."));
P(figure(FIG("fig_page.png"), 540));
P(caption("Fig. 3.1. Page curves of the born ensemble; the dashed line is the exact fraction tau* = 1 - 2^(-3/2)."));

// ============================ T2 ==============================================
P(h1("4. T2 - Uniqueness of the CMB contact point"));
P(statementBox("Theorem T2.", "The equation T_H(M) = T_CMB has the unique solution M_CMB = hbar c^3 / (8 pi G kB T_CMB) = 4.5016e22 kg (about 0.61 lunar masses); above M_CMB the hole is hotter than the background and evaporates, below it the hole is colder and grows."));
P(h2("4.1. Conditions"));
P(body("The Hawking temperature of a neutral non-rotating hole, T_H(M) = hbar c^3 / (8 pi G kB M), is an exact closed form in CODATA-2018 constants; T_CMB = 2.72548 K is the measured CMB temperature (COBE/FIRAS). Both are treated in the Schwarzschild vacuum idealisation, without accretion or cosmological expansion."));
P(h2("4.2. Proof"));
P(body("T_H(M) = K/M with the positive constant K = hbar c^3 / (8 pi G kB) decreases strictly from infinity to zero over M > 0. By the intermediate value theorem, for every T_CMB in (0, infinity) there is exactly one M_CMB = K / T_CMB. Substituting the measured value gives M_CMB = 4.501595e22 kg. The sign of the net balance flips at the same point: P_net proportional to T_H^4 - T_CMB^4 changes sign there by the monotonicity of the fourth power."));
P(mathPara([ mSub([mR("M")], [mR("CMB")]), mR(" = "),
             mFrac([mR("ℏc"), mSup([mR("")], [mR("3")])],
                   [mR("8πG·k"), mSub([mR("")], [mR("B")]), mR("·T"), mSub([mR("")], [mR("CMB")])]),
             mR(" ≈ 4.5016·"), mSup([mR("10")], [mR("22")]), mR(" kg") ], "(4.1)"));
P(h2("4.3. Verification and status"));
P(body("The function equal_CMB_mass() reproduces (4.1) from the Part-A constants of constants.py; the value is pinned by a pytest test and surfaces as the T_H_over_T_CMB column of bridge_master.csv, where the CMB-input row equals one by construction. The contact mass is the single point where a hole shakes hands with the relic background, and it doubles as the natural divider scale of the project ladder. Status: exact within the Schwarzschild idealisation (documented in docs/methods.md)."));

// ============================ T3 ==============================================
P(h1("5. T3 - The septinial constant and its family"));
P(statementBox("Theorem T3.", "b_Ch = 1 - cos(2 pi / 7) = 2 sin^2(pi / 7) = 0.37651019814126640; within the family b(delta) = 1 - cos(2 delta) at delta in {pi/2, pi/3, pi/7} the constant decreases strictly: b(pi/2) = 2, b(pi/3) = 3/2, b(pi/7) = 0.3765...; the literature anchor gamma_Ch = 0.374 deviates from b_Ch by 0.67 percent."));
P(h2("5.1. Proof of the identity"));
P(body("The identity 1 - cos(2x) = 2 sin^2(x) is a standard consequence of the double-angle formula; at x = pi/7 it gives b_Ch = 2 sin^2(pi/7). Monotonicity: b'(delta) = 2 sin(2 delta) is positive on (0, pi/2), so b increases with delta, and along the decreasing sequence delta in {pi/2, pi/3, pi/7} the values of b decrease strictly. The numbers: b(pi/2) = 1 - cos(pi) = 2; b(pi/3) = 1 - cos(2 pi/3) = 3/2; b(pi/7) = 0.37651019814126640 (mpmath-verified at dps=50)."));
P(h2("5.2. On the comparison status"));
P(body("The agreement of b_Ch with the mass-scaling anchor gamma_Ch = 0.374 to 0.67 percent is a comparison, not a coincidence theorem: the project explicitly refuses to claim that gamma is derived from septinial geometry. The role of T3 is to fix the exact value and the family for the upcoming campaigns (notably C4 on the QNM correction omega -> omega (1 - 1/(1200 pi^2))). Status: the identity is exact; the interpretation is a comparison flagged in the honesty register."));
P(figure(HQ("hq_05_born_spectrum.png"), 540));
P(caption("Fig. 5.1. The born spectrum against the anchor gamma_Ch = 0.374; the septinial constant b_Ch = 0.37651 sits within 0.67 percent of it."));

// ============================ T4 ==============================================
P(h1("6. T4 - Second-order convergence of the engine"));
P(statementBox("Theorem T4.", "On the exact Roberts-Oshiro solution the engine error in max|r - r_exact| decreases with order p = 2.031 over N: 200 -> 400 and p = 2.093 over N: 400 -> 800, consistent with the second order of the RK2-Heun scheme."));
P(h2("6.1. Conditions and measurement"));
P(body("The solver marches the Goursat problem on an N-by-N characteristic grid; the reference is the exact Roberts-Oshiro solution, whose deviation max|r - r_exact| is evaluated on each grid. The convergence order is estimated in the standard way, p = log2(E(N/2)/E(N)). The measurement uses three grids, is committed in c1_verdict.json (validation field) and pinned by test_engine.py."));
P(h2("6.2. Verification and status"));
P(body("The values 2.031 and 2.093 sit within five percent of the nominal 2, which is typical for a second-order scheme on moderate grids with a nonlinear term. The second-order behaviour is also visible in hq_17: the measured points follow the slope-minus-two guide. The slightly elevated order on the finer pair (2.093) is explained by higher-order error contributions and needs no separate hypothesis. Status: numerically established, test-pinned."));
P(figure(FIG("fig_validation.png"), 520));
P(caption("Fig. 6.1. Roberts-Oshiro validation: error versus N with the slope -2 guide."));

// ============================ T5 ==============================================
P(h1("7. T5 - The mass floor law"));
P(statementBox("Theorem T5.", "The smallest resolved engine mass obeys the 1/N floor law floor_M(N) = c/N with a measured prefactor c = 12.4 / 13.7 / 13.6 at N = 800 / 1600 / 3200 (code units) - that is, floor_M approximately (13 plus-or-minus 1)/N: the per-doubling ratio of the floors is 1.81 / 2.02 against the ideal 2, and the v2.0.0 wording '12/N within plus-or-minus 7 percent' inherited the pre-remediation floors and is corrected."));
P(h2("7.1. Data"));
P(tableTitle("Table 7.1. The floor ladder (C1 + C3b, per-grid F-2 values)"));
P(dataTable({
  headers: ["N", "floor_M (measured)", "c = floor * N", "deviation from 12/N"],
  rows: [
    ["800", "0.0155", "12.4", "+3.3%"],
    ["1600", "0.008574765", "13.7", "+14.3%"],
    ["3200", "0.004244867", "13.6", "+13.2%"],
  ],
  widths: [18, 32, 24, 26],
}));
P(h2("7.2. Interpretation and limits"));
P(body("The floor arises from resolvability: at a fixed N a collapsing packet below some mass fails to form a horizon before leaving the computational domain, and the run stops on the floor. The scaling is the load-bearing claim: the per-doubling ratios of the remediated floors (1.81 and 2.02) bracket the ideal 2 of an exact 1/N law, with no trend toward saturation or collapse. The prefactor, by contrast, is definition-dependent - it depends on where the scan grid lands relative to the floor - which is why the law is stated with a band, (13 plus-or-minus 1)/N, rather than as a single constant. The v2.0.0 prefactor 12 (deviations within 7 percent) was computed from the pre-remediation floors (7.104e-3 / 3.842e-3) whose eps axis was mislabeled by +2.8e-3 (audit finding F-2); the corrected values are the ones committed in the C3b verdict and pinned by tests."));
P(body("The limits matter: the law is established on N in [800, 3200] from three committed points; extrapolation beyond N = 3200 or to other profile families is forbidden without a new campaign. It is the floor, not the physics, that gates the reachability of the anchor gamma_Ch on fixed and concentrated grids - the subject of the honest negatives of T6/T7 and the explicit target of the engine roadmap (AMR). The threshold-side twin of this law - the resolution drift of A* itself - is the subject of theorem T10. Status: numerically established; campaign C3b committed the ladder as a first-class result."));
P(figure(HQ("hq_13_floor_law.png"), 540));
P(caption("Fig. 7.1. The floor law floor_M = 12/N across three grids; dotted: the 9.6/N and 14.4/N envelope."));

// ============================ T6 ==============================================
P(h1("8. T6 - The Delta*gamma anchor product"));
P(statementBox("Theorem T6.", "The product of the literature anchors Delta*gamma = 3.44 x 0.374 = 1.28656 lies inside the target tolerance 1.27 plus-or-minus 0.05 (deviation 1.3 percent) - a PASS at the anchor level; the engine level remains an honest negative."));
P(h2("8.1. The two levels"));
P(body("The anchor level is arithmetic over two literature constants: it is exact and reproducible (3.44 x 0.374 = 1.28656 up to the rounding of the second factor). The engine level is our own measurement of Delta and gamma with the solver: on fixed grids gamma is unmeasurable (the grid floor, see T5), and on concentrated grids N = 1600/3200 the per-grid remediated fits are floor-dominated - gamma_eff = 0.041 / 0.060 with r2 = 0.33 / 0.41 - while Delta does not resolve (fewer than three peaks) up to N = 3200. The v2.0.0 statement that gamma_eff 'stabilises near 0.12' was an artifact of measuring eps from the N=800 threshold on deep grids (audit finding F-2, IVP-11) and is retracted; the remediated values are the committed ones. The PASS of T6 therefore belongs to the anchor, not to the engine - a distinction carried consistently across the artifacts (the C3 verdict, RESULTS.md row 10, figure hq_12)."));
P(h2("8.2. What an engine-level PASS would take"));
P(body("An engine-level pass of T6 becomes possible only after the floor law (T5) is beaten by an engine upgrade: true AMR adapted to the accumulation point, or a hybrid with a moving inner boundary. The explicit numeric criterion is fixed in the roadmap: an engine-level gamma compatible with 0.374 within 10 percent and at least three resolved echo peaks. Until then T6 stays a comparison with an honestly marked negative on the engine side."));
P(figure(HQ("hq_12_dgamma_anchor.png"), 520));
P(caption("Fig. 8.1. The anchor product Delta*gamma = 1.28656 against the target 1.27 plus-or-minus 0.05 - a PASS at 1.3 percent."));

// ============================ T7 ==============================================
P(h1("9. T7 - Subcritical monotonicity and the logarithmic slowdown"));
P(statementBox("Theorem T7.", "On the measured band eps in [6.3e-5, 6.3e-2] (13 runs) the peak compactness q_max increases strictly as eps decreases: 0.0158 -> 0.5845 with no single inversion; the null-coordinate time of the peak follows the slowdown law v_qmax = a + b ln(eps) with b = -0.0334 and r^2 = 0.714."));
P(h2("9.1. Monotonicity"));
P(body("The sequence q_max(eps) over the 13 subcritical runs of C2 increases strictly toward the threshold; no adjacent pair forms an inversion. The three scan rows marked flipped (an amplitude-sign artefact of the early protocol) are kept verbatim in the verdict and excluded from the fits explicitly - the only sample reduction, documented in the JSON verdict."));
P(h2("9.2. Slowdown"));
P(body("Because b < 0 and ln(eps) -> -infinity as eps -> 0, the peak moment v_qmax grows logarithmically as the critical amplitude is approached - the classic logarithmic kinematics of near-critical approach (DSS-type). The absolute values of v_qmax are quantised by the instrument: each run samples 40 engine snapshots, which produces the staircase in the scatter; the quantisation is recorded in the honesty register as a property of the instrument, not of the physics."));
P(figure(HQ("hq_07_critical_slowdown.png"), 540));
P(caption("Fig. 9.1. Critical slowdown: v_qmax against ln(eps); the line is the committed fit."));
P(h2("9.3. Status"));
P(body("Both claims of T7 are numerically established: monotonicity is pinned by test_campaigns.py (a monotonicity pin on q_max), the fit by pins on its coefficients (b, a, r^2). No extrapolation of the law beyond the measured band is claimed."));

// ============================ T8 ==============================================
P(h1("10. T8 - The echo accumulation bound"));
P(statementBox("Theorem T8.", "The echo accumulation rate on the subcritical branch, dN_peaks/d ln(1/eps) = 0.1909 (r^2 = 0.86), is strictly below the critical anchor 1/Delta = 0.2907: the ratio is 0.657."));
P(h2("10.1. Content of the claim"));
P(body("Echo peaks are counted as local maxima of q(v) along each run; the regression over 13 points yields 0.1909 peaks per e-fold of distance from the threshold. The anchor 1/Delta = 1/3.44 = 0.2907 is the near-critical echo rate from the literature. The inequality 0.1909 < 0.2907 says that the subcritical echo clock runs about a third slower than the critical one - consistent with dispersal taking part of the oscillation time."));
P(h2("10.2. Limits and honest caveats"));
P(body("The measurement is taken on completed (dispersing) runs, not in the immediate neighbourhood of the threshold: at depth eps < 1e-3 the peak count drops below three and the period stops being measurable - this is precisely the honest negative of T6. The anchor was never used as a fit target (the project rule: comparisons, not fits). Status: numerically established; pinned in test_campaigns.py; visualised in hq_08."));

// ============================ T9 ==============================================
P(h1("11. T9 - Half the entropy at the Page time"));
P(statementBox("Theorem T9.", "At the Page time the normalised radiation entropy is exactly one half: S_rad(tau*)/S0 = (2^(-3/2))^(2/3) = 2^(-1) = 1/2."));
P(h2("11.1. Proof"));
P(body("This is an immediate corollary of T1: (1 - tau*)^(2/3) = (2^(-3/2))^(2/3) = 2^(-1) = 1/2. The elegance of the statement is that the branch-matching point is simultaneously the symmetry point of the model: the radiation entropy at the Page time equals half the final value regardless of the input mass scale and of the ensemble member f~. This is why the normalised curves of all three members cross at the single point (tau*, 1/2) - see hq_16."));
P(h2("11.2. Verification"));
P(body("The value is reproduced by every multilang twin (S_rad/S0 at PAGE_FRACTION equals 0.50000000000000 in all three verified implementations), pinned in page_curve_grid.csv (the branch crossing) and covered by the mpmath battery. Status: exact - a corollary of T1."));

// ============================ T10 =============================================
P(h1("12. T10 - The resolution-drift law (why one formula gives different values)"));
P(statementBox("Theorem T10.", "The fixed-grid critical amplitude is a grid-dependent observable: a threshold formula evaluated on grid-sampled parabolic structures returns different values at different resolutions N, because sampling flattens the compaction peak by exactly kappa h^2/8 (worst alignment; kappa h^2/24 on average) and shortens the chord chain against the continuum arc. By the implicit function theorem A*_N - A*_cont = kappa* alpha^2 h^2 / (8 s) + O(h^3) with kappa* the profile tension and s = dq_max/dA the sensitivity: the drift EXISTS, is POSITIVE, and the ladder approaches the continuum threshold from above."));
P(h2("12.1. The two exact lemmas"));
P(body("Lemma A (chord flattening). A locally parabolic profile q(x) = q_pk - kappa (x - x0)^2/2 sampled on a grid of spacing h has, in the piecewise-linear (chord) representation, its peak at the nearest node: the deficit is kappa delta^2/2 with delta = dist(x0, grid). The worst alignment (delta = h/2) gives exactly kappa h^2/8; the average over alignments is exactly kappa h^2/24 (E[delta^2] = h^2/12). Both constants are verified to machine precision by campaign C6 (worst-case 2.0e-9 relative - the float64 floor of the tiny deficit; the chord-chain check below closes at 1.9e-16)."));
P(body("Lemma B (tension: stretch and compress). The secant slope of a parabola over one cell equals its derivative at the cell midpoint, so the chord chain through the samples is EXACTLY the midpoint-rule sum of the arc integrand f(x) = sqrt(1 + kappa^2 x^2). Since f is strictly convex, the chain is strictly shorter than the continuum arc, with deficit bounded by w h^2 f''_max/24: at fixed tension the sampled structure is COMPRESSED, and refining the grid stretches it back. This is the mechanism named in the release: parabolic structures stretch and compress under the curvature of their tension when the scale is rescaled - which is why one and the same formula, applied at different scales, cannot return one number."));
P(h2("12.2. The threshold shift and its measurement"));
P(body("Applying the implicit function theorem to the level condition F(A, q_pk - delta(h)) = q_crit with sensitivity s = dq_pk/dA > 0 gives the drift law of the statement: the leading exact channel is O(h^2) and positive. Campaign C6 measures both coefficients from committed artifacts only: the tension kappa* = 2728.60 from a local quadratic regression on the committed supercritical compaction profile at v = 0.5853, and the sensitivity s = 413.8 from the two deepest-eps rows of the committed C2 subcritical scan. The measured ladder drifts monotonically downward (1.69e-2 per doubling at N = 200 down to 9.23e-4 at N = 3200) with local effective orders p_eff = 1.140 / 1.459 / 1.596 - strictly climbing, faster than 1/N, toward the second-order limit of the RK2-Heun instrument."));
P(figure(C6F("drift_ladder_en_light.png"), 540));
P(caption("Fig. 12.1. The observed per-doubling drift of the committed ladder against the T10 exact channel and the rejected two-term fit (report figure of campaign C6)."));
P(h2("12.3. Status and honest negatives"));
P(body("Status: analytically derived (the two lemmas are exact and machine-verified) with coefficients measured on committed artifacts; the verdict is c6_drift_verdict.json, pinned by three tests. Two honest negatives travel with the theorem. First, NO continuum threshold A*_cont is claimable from this ladder: the two-term extrapolation A*_N = A_inf + a/N + b/N^2 fits the five points with R2 = 0.999 and is nevertheless REJECTED by its own p_eff trajectory (the fitted law's p_eff decreases with N while the measured one climbs). Second, the exact channel is sub-dominant: it carries between 2.6e-3 and 9.1e-3 of the observed drift; the dominant, monotone channel is attributed - a labeled hypothesis - to march-error amplification under near-critical lingering, the threshold-side twin of the floor law (T5) and the explicit target of the AMR engine upgrade."));

// ============================ 13. Matrix ======================================
P(h1("13. The verification matrix"));
P(body("The matrix below connects each theorem with its source, verification instruments and artifacts. Instrument legend: pytest = pin tests of test_*.py (63 tests); mpmath = the high-precision battery python3 -m chbridge.validate (7/7 at dps=50); campaign = verdicts under campaigns/reference/*.json; multilang = the JS/C++/C twins (7.1e-13); fig = regenerable catalog figures."));
P(tableTitle("Table 13.1. Verification matrix of the theorems"));
P(dataTable({
  headers: ["No", "Theorem", "Status", "Instruments", "Artifacts"],
  rows: [
    ["T1", "Page fraction 1 - 2^(-3/2)", "exact", "mpmath; pytest; multilang", "hawking.py; fig_page; hq_16"],
    ["T2", "CMB contact uniqueness", "exact (idealisation)", "mpmath; pytest", "hawking.py; bridge_master"],
    ["T3", "Septinial constant 2 sin^2(pi/7)", "exact; comparison 0.67%", "mpmath; pytest", "constants.py; hq_05"],
    ["T4", "Convergence orders 2.03/2.09", "numerically established", "campaign; pytest; fig", "c1_verdict; fig_validation; hq_17"],
    ["T5", "floor law floor_M = (13 +/- 1)/N", "numerically established", "campaign; pytest; fig", "c3b_verdict; hq_13"],
    ["T6", "Delta*gamma = 1.28656 (target 1.27+/-0.05)", "comparison; engine - negative", "campaign; pytest; fig", "c3_verdict; hq_12"],
    ["T7", "q_max monotone; slowdown b<0", "numerically established", "campaign; pytest; fig", "c2_verdict; hq_06; hq_07"],
    ["T8", "Echoes 0.1909 < 0.2907", "numerically established", "campaign; pytest; fig", "c2_verdict; hq_08"],
    ["T9", "S_rad(tau*)/S0 = 1/2", "exact (corollary of T1)", "mpmath; multilang", "page_curve_grid; hq_16"],
    ["T10", "resolution drift: A*_N - A*_cont = kappa* h^2/(8s) > 0", "analytically derived; measured", "campaign C6; pytest", "c6_drift_verdict; drift report"],
  ],
  widths: [8, 30, 20, 20, 22],
  fontSize: 18,
}));
P(body("The matrix is complete: every row of results/RESULTS.md is either covered by one of T1-T10 or belongs to the protocol notes (the 40-snapshot quantisation, junk-row handling, the photon-only idealisation), which are collected in the honesty register of the next section."));

// ============================ 14. Honesty =====================================
P(h1("14. The honesty register and limits of applicability"));
P(body("The honesty register is a mandatory closing section of every final document of the package. It lists the constraints without which the theorems above would be easy to misread; it is committed in results/RESULTS.md up to wording."));
P(bullet("Junk rows are kept: runs with overflowing masses (3 bifurcation rows of C2, examples in C1) are present in the verdicts with sane = False and are never silently dropped."));
P(bullet("The mass floor is a first-class result: floor_M is not a defect but a measured law (T5, prefactor (13 +/- 1)/N on the remediated per-grid values) that gates the reachability of everything else."));
P(bullet("gamma and Delta at engine level are honest negatives: with the F-2 per-grid thresholds the deep-grid fits are floor-dominated (gamma_eff = 0.041/0.060, r2 = 0.33/0.41) and the 0.374 anchor is unreachable; Delta does not resolve (fewer than 3 peaks) up to N = 3200 inclusive. The 2.0.0 gamma_eff near 0.12 was an eps-mislabeling artifact and is retracted."));
P(bullet("No continuum threshold: the A* ladder drift is a theorem (T10), the two-term extrapolation is rejected by its own p_eff trajectory, and no A*_inf is claimed anywhere in the package."));
P(bullet("The dominant drift channel is a labeled hypothesis: march-error amplification under near-critical lingering; the exact parabolic-tension channel is measured and sub-dominant (share 2.6e-3..9.1e-3)."));
P(bullet("Septinial coincidences are comparisons: zero derivation claims for gamma or Delta from pi/7 geometry."));
P(bullet("Photon-only evaporation is an idealisation: the luminosity model counts photons only; other degrees of freedom are excluded and documented."));
P(bullet("v_qmax quantisation: 40 snapshots per run is the instrument; the visible staircase is explained by it completely."));
P(body("These eight items are not fine print; they are part of the results. Four of them (the floor, the gamma/Delta negatives, the no-A_inf commitment, the quantisation) are measured statements with test pins, and they shape the roadmap (C4, C5, the engine upgrade). Read the theorems together with this register: T6 without the engine-negative item would falsely suggest a closed question, and T10 without the sub-dominance note would overstate what the parabolic channel explains."));

// ============================ 15. References ==================================
P(h1("15. References and package sources"));
P(body("The numerical sources of this volume are internal artifacts of the package, each named in the verification matrix. The external anchors used as comparative constants:"));
P(bullet("Choptuik (1993) - type-II criticality and the family mass-scaling exponent gamma = 0.37 (the anchor gamma_Ch = 0.374)."));
P(bullet("Gundlach, Hodgson - the echo period Delta = 3.44 plus-or-minus 0.02 (the period anchor)."));
P(bullet("Page (1993), Sen (1996) - the exact averaged partition entropy formula and its Haar audit (max deviation 0.0042 bits in the package)."));
P(bullet("Roberts, Oshiyo - the exact solution used to validate the scheme order (T4)."));
P(bullet("CODATA 2018 - all Part-A physical constants; Planck 2018 - the cosmological baseline; COBE/FIRAS - T_CMB = 2.72548 K."));
P(bullet("Independent verification protocol IVP-15 (this package, independent_verification/): the blind audit of the 2.0.0 release - findings F-1/F-2/F-3 - and the release gate that this v2.1.0 edition closes; the committed audit trail ships in independent_verification/results/."));
P(body("Internal sources: chbridge/constants.py (single source of constants), campaigns/reference/*.json (C1, C2, C3, C3b verdicts and the C6 drift verdict), campaigns/reference/a_star_ladder.{json,csv} (the F-1 remediation ladder), data/bridge/*.csv (13 derived tables), results/scaling_drift/ (the C6 report and figures), results/RESULTS.md (the living ledger), docs/scaling_law.md (the T10 derivation), docs/theory.md and docs/methods.md (theory and protocols). All ship inside the ZIP and reproduce through the Makefile; the full runbook is part X of the encyclopedic appendix."));

C.assemble({
  coverConfig: {
    title: "The Theorems of the Collapse-Hawking Bridge",
    subtitle: "Statements, proofs and committed verification of ten quantitative claims",
    englishLabel: "THEOREMS VOLUME",
    metaLines: [
      "Package: Collapse-Hawking Bridge v2.1.0 (IVP-15 alignment edition)",
      "Campaigns: C1 / C2 / C3 / C3b / C6 (drift law)",
      "Verification: 63 pytest / 7-of-7 mpmath (dps=50) / twins 7.1e-13 / IVP-15 audit",
    ],
    footerLine: "Appendix to the monograph / English edition / 2026",
  },
  tocTitle: "Table of Contents",
  refreshHint: "Note: this Table of Contents is generated via field codes. To ensure page number accuracy after editing, please right-click the TOC and select Update Field.",
  headerText: "The Theorems of the Collapse-Hawking Bridge / v2.1.0",
  bodyChildren: kids,
  outPath: path.join(__dirname, "..", "theorems_en.docx"),
}).catch((e) => { console.error(e); process.exit(1); });
