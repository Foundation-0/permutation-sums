# Contributing

The checker is the judge. A result changes only by a pull request that leaves both of these commands exiting 0:

```sh
python3 verify.py
python3 -O verify.py
```

`results/certificate.json` stays as it is unless the change is a deliberate regeneration with `python3 verify.py --write`. A checker edit and a new claimed number do not belong in the same pull request.

Labels used here:

- PROVEN means a written proof.
- VERIFIED means a finite check, not a proof.
- KNOWN means a citation. The cited statement is not a result of this repository.
- CONJECTURE means a statement this repository does not check.

Do not merge your own pull request. A review by the author does not count. Say which model wrote the change. A person has not signed a result until a person says so.

There is one open track: keep the finite checks honest. A new track needs a failing check for a bad case and a passing check for the real case before any new repository is considered.
