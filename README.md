# Permutation sums

This repository checks exact integer and rational claims about sums over permutations.

A clean run recomputes derangement counts, menage numbers, three rook boards, and one 3 by 3 unitary with rational complex entries. It exits 0 only when `results/certificate.json` matches that run. The label on the certificate is VERIFIED. The scope is finite checks through n = 20 and one 3 by 3 matrix.

Anyone who wants those checks replayed can run them with the Python standard library. This is not an approximation library, and it is not a boson-sampling simulator.

## Run

```sh
python3 verify.py
python3 -O verify.py
```

Both commands must print `PASS` and leave the certificate unchanged. `python3 verify.py --write` is the only command that replaces the certificate. A failed check raises `CheckFailure`, including when Python is started with `-O`.

`make verify` runs the same commands and a small test that a false check still raises.

## What is known and what this repository checks

Derangement counts, the menage numbers, rook polynomials, and Ryser’s formula for the permanent are classical. The citations are in `PROOF.md`. The checker recomputes a finite list of them and compares the results with each other.

The 3 by 3 unitary is the rational matrix printed below. Its permanent and the permanent of its squared moduli are exact fractions. A printed probability 0.2639 does not equal the second of those fractions.

Late-2026 approximation algorithms for the permanent, and classical simulators for lossy boson sampling, are other people’s preprints. They are not implemented here, and this repository does not certify their runtimes.

The catalogue of Foundation-0 mathematics notes is [math0](https://github.com/Foundation-0/math0). This strand has its own repository so the checker can be required on every change.

## Results

| Check | Certificate | Label |
| --- | --- | --- |
| Derangements, menage numbers, three 6 by 6 boards | integers agree across recurrences, rook expansion, and the permanent | VERIFIED |
| Asymmetric board of 15 forbidden cells | permanent 36, not the printed 26 | VERIFIED |
| Rational 3 by 3 unitary | modulus squared of the permanent is 1/81, classical permanent is 41/81 | VERIFIED |
| Printed panel value 0.2639 | does not equal 41/81 | VERIFIED |
| Menage total variation at n = 6, 10, 20 | 51660, 26541, and 12194 millionths | VERIFIED |
| Printed factor compared with those distances for n = 4 through 20 | finite comparison only | VERIFIED |

The full field list is `results/certificate.json`. `PROOF.md` says what each field does and does not show. `HANDOFF.md` lists the negative findings.

Model: Grok. A person has not signed this result.

## Licence

Code is under the MIT licence. Text is under CC BY 4.0. See `LICENSE`.
