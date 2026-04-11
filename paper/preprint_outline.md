# arXiv Preprint Outline

**Title:** Aegis: Audited Execution Governance for Independent
Science — Execution Discipline for Multi-Phase Experimental Programs

**Target:** 4-6 pages. Submit after Phase 1 when you have
empirical data on bugs caught and overhead costs.

**Submit to:** cs.LG (primary), cs.SE (secondary)


## Abstract (~150 words)

Framework for solo researchers. Addresses: state loss across
sessions, unaudited scripts propagating bugs, motivated
reasoning in result interpretation, threshold drift. Three
components: (1) experiment runner with session tracking and
output verification, (2) structured state file, (3) code-generated
blind comparison with adaptive AI assistance. Empirical
results from [N] sessions: [X] bugs caught, [Y]% overhead.


## Sections

1. **Introduction** — solo researcher failure modes, gap
   between experiment trackers and human process
2. **Design** — runner, state file, blind comparison layer,
   adaptive rigor modes, pre-registration, assumption checks
3. **Empirical results** — [FILL AFTER PHASE 1] bug detection
   rates, iteration counts, overhead, state recovery
4. **Related work** — MLflow/W&B (tracking), Snakemake
   (orchestration), AI agents (automation), GitHub-for-labs
5. **Limitations** — validated in one program, overhead may
   not justify for <4 week projects
6. **Conclusion** — 80% of value from runner + state file,
   remaining 20% from pipeline discipline


## Before submitting

- [ ] Replace all [N] with real numbers
- [ ] Write one concrete bug example
- [ ] Compute overhead percentages
- [ ] Add GitHub URL
- [ ] Update CITATION.cff with arXiv ID
