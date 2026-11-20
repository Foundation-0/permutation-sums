# Finite checks for permutation sums

The certificate at `results/certificate.json` is the record of one run of `verify.py`. Its label is VERIFIED. That means a finite check passed. It does not mean a theorem was proved.

Scope: derangements and menage numbers through n = 10, menage total variation through n = 20, three boards of size 6, one 3 by 3 unitary, and the comparison numbers named below. Outside that list, nothing is claimed.

## Classical counts

A derangement is a permutation with no fixed point. The two recurrences

`D(n) = (n - 1) (D(n - 1) + D(n - 2))` and `D(n) = n D(n - 1) + (-1)^n`,

with `D(0) = 1` and `D(1) = 0`, both reproduce

`1, 0, 1, 2, 9, 44, 265, 1854, 14833, 133496, 1334961`

for n from 0 to 10. The rencontres number `D(n, n - 1)` is 0 for n from 1 to 10, because `D(1) = 0`.

The menage number `M(n)` counts permutations that avoid two neighbouring positions in a cycle. Touchard’s formula, using Kaplansky’s rook numbers as exact rationals that land on integers, matches the recurrence in `verify.py` through n = 10:

`1, 0, 0, 1, 2, 13, 80, 579, 4738, 43387, 439792`.

These identities are standard. The checker confirms a finite initial segment. It does not prove the recurrences for every n.

## Three boards

A rook number `r_k` counts ways to place k rooks on the forbidden cells with no two in the same row or column. The hit numbers come from the usual change of basis between rook numbers and permutations. The permanent of the allowed cells equals the number of avoiding permutations.

Backtracking, deletion-contraction, the hit expansion, Ryser’s formula, and Glynn’s formula agree on all three boards.

| Board | Rook numbers | Avoiding permutations |
| --- | --- | --- |
| Diagonal | 1, 6, 15, 20, 15, 6, 1 | 265 |
| Cycle `I + Z` | 1, 12, 54, 112, 105, 36, 2 | 80 |
| 15 forbidden cells | 1, 15, 79, 177, 164, 48, 2 | 36 |

The 15 cells, with rows and columns indexed from 0, are the list `ASYM_FORBIDDEN` in `verify.py`. A printed rook vector beginning `1, 15, 78` and a printed avoiding count of 26 do not match those cells. The certificate records that mismatch as false on `printed_asymmetric_hit0_26_matches_coordinates`.

Ryser’s count on the asymmetric board, in this implementation, is 315 multiplications and 441 additions or subtractions. Glynn’s operation count is not recorded.

The permanent of `[[1, 1], [1, -1]]` is 0. The permanent of the 2 by 2 all-ones matrix is 2.

## Brackets on two symmetric matrices

For the 6 by 6 matrix of ones with a zero diagonal, the permanent is 265.
The van der Waerden lower bound `(5/6)^6 * 720` rounds to 241.13.
The Bregman-Minc number `(120)^(6/5)` rounds to 312.62.
The Bethe value at the uniform doubly stochastic matrix `(J - I) / 5` rounds to 73.79.
Eight times that value rounds to 590.30.
The certificate stores these as hundredths: 24113, 31262, 7379, 59030.
The factor of eight is `2^(n/2)` at n = 6.
Multiplying by it does not prove a general comparison theorem.

For two disjoint 6-cycles, each on three plus three vertices, the permanent is 4.
Every row and every column sums to 2, so the only doubly stochastic matrix puts mass 1/2 on each edge.
The checker records that degree condition. It does not sum the Bethe expression.
The displayed factor `2^(2n/g)` at n = 6 and g = 6 equals 4, which equals this permanent.
That is one equality case, not a proof for other matrices.
The Sinkhorn upper bound on this matrix is the integer 64, accepted from floating-point scaling within `1e-6`.
The van der Waerden bound is the exact fraction 80/81, whose thousandths rounding is 988.

On the asymmetric board the same scaling does not reproduce the printed lower figure 12.37 or the printed upper figure 380.7. Only those two booleans are stored. The raw floating-point values are not part of the certificate.

## Total variation for the menage board

The distance is half the L1 gap between the hit distribution and Poisson(2), including the Poisson tail past n. Arithmetic uses `Decimal` with precision 60. The distances in millionths are 51660 at n = 6, 26541 at n = 10, and 12194 at n = 20. The first and the third round to 0.0517 and 0.0122 at four digits after the decimal. The value 26500, from `0.265 / n` at n = 10, is not the distance.

For n from 4 to 20, the printed factor

`((1 - e^(-2)) / 2) * 10 (n - 2) / (n (n - 1))`

stays above that exact distance and below the older factor

`((1 - e^(-2)) / 2) * (((n - 2) / n) * (2 / (n - 1)) + 8 / n)`.

This is a finite check of the printed formula. It is not a proof of Roos (2024), which was not re-derived here. The older factor is the one stated for this diagonal sum by Barbour, Holst, and Janson (1992).

## One rational unitary

Gaussian rationals are numbers `(a + b i) / c` with `a`, `b`, and `c` integers. The checked matrix is

```
(1 + 2i)/3    2/3     0
-2/3       (1 - 2i)/3  0
0             0       1
```

It is unitary. It is the Cayley image of a Hermitian matrix over the same number field, and that Hermitian matrix is recovered from the unitary by `H = -i (2 (I + U)^(-1) - I)`. Adding 1 to the (0, 1) entry of that Hermitian matrix makes the Cayley image fail `U dagger U = I`.

The squared modulus of the permanent is 1/81. The permanent of the squared moduli is 41/81. Grouping permutation pairs by the number of non-fixed points makes the linear coefficient 0, and the sum of the coefficients equals 1/81. The printed panel value 0.2639 does not equal 41/81.

The linear-coefficient control also rejects the stand-in list `[41/81, 1]`. That stand-in is not a perturbation of the unitary.

## Other finite checks

On the 2 by 2 all-ones matrix, the mean of `|det B|^2` is 2 for both alphabets below. The second moment is 8 for real signs `{1, -1}` and 6 for complex signs `{1, -1, i, -i}`, over the full product of four entries, in exact integer arithmetic. The certificate stores those moments. It does not store a general variance bound.

The pool-adjacent-violators projection of `[1, 3, 2]` onto an increasing vector is `[1, 5/2, 5/2]`. A decreasing projection of `[-4, -1, -3]` stays ordered. This is one example, not a citation check of a paper.

`(4095)^2 = 16769025`. That is the square of the dimension of the Birkhoff polytope at n = 4096. It is not a measurement of memory or runtime.

For transmission `eta` from 0.1 to 0.9 in steps of 0.1, the cutoff `L = max(1, ceil(log((1 - eta) * 0.01) / log(eta)))` keeps the geometric tail `eta^(L+1) / (1 - eta)` at most 0.01, and so does `L - 1`. The checker uses ordinary floating point and stores only the two booleans. It does not sample boson outputs, and it does not prove a simulation theorem.

## Prior art

Kaplansky and Riordan, the menage problem and rook polynomials, are the classical source for the board counts.
Ryser (1963) and Glynn (2010) are the two permanent expansions used as cross-checks.
The van der Waerden bound used here is the Egorychev and Falikman form `n! / n^n` on a doubly stochastic matrix, pulled back through diagonal scaling.
Bregman-Minc supplies the integer upper comparison on the two symmetric matrices.

Roos (2024) is the named source of the sharper factor. This repository checks the printed formula on n = 4 through 20 and does not re-prove it. Dong and Jain, [arXiv:2609.02017](https://arxiv.org/abs/2609.02017), are the named source of the girth factor `2^(2n/g)`. This repository checks one equality case.

Godsil and Gutman (1981) introduced the real-sign estimator. The complex moments checked here are the squared-modulus moments on one 2 by 2 matrix.

## Papers named and not rerun

Abstracts opened on 20 November 2026:

- [arXiv:2611.01434](https://arxiv.org/abs/2611.01434), Youngrong Lim, 1 November 2026, “Boson sampling is fragile to loss”. The abstract says a fixed nonzero uniform loss rate permits efficient average-case classical sampling. Not implemented.
- [arXiv:2611.00338](https://arxiv.org/abs/2611.00338), Raphael Coelho, 30 October 2026, “Reading the Count: Prediction Markets and Brazil’s 2026 Presidential Election”. This is not a boson-sampling paper.

Other 2026 preprints on permanent approximation and on lossy boson sampling were named in the source note. Their algorithms are not in this repository, and their stated runtimes are not re-certified here.

## Controls

Three recorded controls must be true on a clean run. The asymmetric permanent must not be 26. The broken Hermitian matrix must not stay unitary. The stand-in linear coefficient must not be accepted as zero. Separately, `require(False, "planted")` raises `CheckFailure` under `python3 -O`.

## Open obligations

A second person, or a different agent, has not reviewed this record. The author of the draft does not merge it. No proof obligation is open inside the checked range, because nothing here is marked PROVEN. Extending the certificate past n = 20, or implementing a cited algorithm, is a new change with its own check.

Model: Grok. A person has not signed this result.
