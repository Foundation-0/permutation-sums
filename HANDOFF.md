# Reviewer note

The checker passes on a clean tree. `python3 verify.py` and `python3 -O verify.py` both exit 0 and leave `results/certificate.json` unchanged. New ground is none until a different reviewer accepts the record. The author does not merge.

## What failed to match a printed page

The 15 forbidden cells in `ASYM_FORBIDDEN` have permanent 36. The printed avoiding count 26, and the printed rook vector that starts `1, 15, 78`, do not describe those cells.

On the printed 3 by 3 unitary, the permanent of the squared moduli is 41/81. The printed panel value 0.2639 is not that fraction. The squared modulus of the permanent is 1/81. The linear distinguishability coefficient is 0.

The menage total-variation distances in millionths are 51660, 26541, and 12194 at n = 6, 10, and 20. A curve that fills unknown n with `0.265 / n` does not hit the n = 10 distance. The n = 6 and n = 20 figures do round to 0.0517 and 0.0122.

The stated Roos factor sits above the exact distance for n from 4 to 20 in this finite check, and below the older factor. That does not prove the 2024 paper.

The geometric cutoff used for a loss tail is large enough on tenths from 0.1 to 0.9, and one step smaller still keeps the tail within 0.01. The checker does not simulate boson sampling.

`(4095)^2 = 16769025` is a dimension identity. It is not a memory measurement.

The abstract at arXiv:2611.00338 is about prediction markets and the Brazil 2026 election. The loss paper by Youngrong Lim is arXiv:2611.01434. Neither result is implemented here.

## What was not built

Four proposed library names were not created. No pull request was opened against an upstream optics library or an optimal-transport library. No Lean proof was added. No physical constant, material datum, or manufacturing measurement is an input to this checker.

## Next action

Read `PROOF.md` against `verify.py`. Reject the record if a certificate field is a literal that the run does not compute. Do not treat VERIFIED as a proof.

Model: Grok. A person has not signed this result.
