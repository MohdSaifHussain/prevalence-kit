"""prevalence-kit: audit-grade prevalence measurement for Trust & Safety.

Governance layer only. `svy` and R `survey` are the estimator layer; this
package does not claim to replace them. See docs/DECISIONS.md D-3, D-4.

Cross-validated, and the sentence is narrower than "validated" on purpose.
Stratified estimation and Neyman allocation reproduce R `survey` 4.5 to 9.5e-15,
and the allocation reproduces Barnett Table 2B, a published table computed
without reference to any implementation. Clopper-Pearson reproduces base R
`binom.test` to 8.4e-11; the Rogan-Gladen interval reproduces `epiR` 2.0.92 to
7.3e-13, which confirms we implement the method as its author does rather than
independently confirming the method. `svy` witnesses the allocation and none of
the intervals: every interval it offers is design-based, and it maps the name
`clopper-pearson` to Korn-Graubard. Details in docs/STANDARDS.md S-2.
"""

__version__ = "0.1.0.dev0"
