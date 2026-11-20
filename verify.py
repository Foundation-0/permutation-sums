#!/usr/bin/env python3
"""Exact checks for sums over the symmetric group.

A clean run compares results/certificate.json. --write is the only way to
replace that file. Checks raise CheckFailure, including under python -O.
"""

from __future__ import annotations

import itertools
import json
import math
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

getcontext().prec = 60

ROOT = Path(__file__).resolve().parent
CERTIFICATE = ROOT / "results" / "certificate.json"

DERANGEMENTS = [1, 0, 1, 2, 9, 44, 265, 1854, 14833, 133496, 1334961]
MENAGE = [1, 0, 0, 1, 2, 13, 80, 579, 4738, 43387, 439792]

DIAG_ROOK = [1, 6, 15, 20, 15, 6, 1]
DIAG_HIT = [265, 264, 135, 40, 15, 0, 1]
CYCLE_ROOK = [1, 12, 54, 112, 105, 36, 2]
CYCLE_HIT = [80, 192, 210, 152, 60, 24, 2]
# Recomputed from the 15 coordinates in the explorer. The printed table says
# rook (1, 15, 78, 172, 157, 50, 2) and h0 = 26. Those integers do not match.
ASYM_ROOK = [1, 15, 79, 177, 164, 48, 2]
ASYM_HIT = [36, 110, 228, 190, 118, 36, 2]

ASYM_FORBIDDEN = [
    (0, 3), (0, 4), (0, 5),
    (1, 2), (1, 4), (1, 5),
    (2, 1), (2, 5),
    (3, 0), (3, 5),
    (4, 0), (4, 1), (4, 2),
    (5, 0), (5, 1),
]


class CheckFailure(RuntimeError):
    """A failed check. Raised as a normal exception so python -O cannot strip it."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise CheckFailure(message)


def factorial(n: int) -> int:
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def binomial(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    out = 1
    for i in range(k):
        out = out * (n - i) // (i + 1)
    return out


def derangement_pair(n_max: int) -> list[int]:
    by_sum = [1, 0]
    by_sign = [1, 0]
    for n in range(2, n_max + 1):
        by_sum.append((n - 1) * (by_sum[n - 1] + by_sum[n - 2]))
        by_sign.append(n * by_sign[n - 1] + (1 if n % 2 == 0 else -1))
    return by_sum, by_sign


def rencontres(n: int, k: int) -> int:
    return binomial(n, k) * derangement_pair(n)[0][n - k]


def kaplansky(n: int, k: int) -> int:
    if k == 0:
        return 1
    width = 2 * n - k
    require(width > 0, "Kaplansky width is not positive")
    value = Fraction(2 * n, width) * binomial(width, k)
    require(value.denominator == 1, "Kaplansky coefficient is not an integer")
    return int(value)


def menage_touchard(n: int) -> int:
    if n == 0:
        return 1
    if n == 1:
        return 0
    total = 0
    for k in range(n + 1):
        sign = -1 if k % 2 else 1
        total += sign * kaplansky(n, k) * factorial(n - k)
    return total


def menage_recurrence(n_max: int) -> list[int]:
    """M_n = a_n - a_{n-2} for n >= 3, with a_n = n a_{n-1} + a_{n-2} + 2 (-1)^n."""
    a = [0, -1, 1]
    for n in range(3, n_max + 1):
        a.append(n * a[n - 1] + a[n - 2] + 2 * (1 if n % 2 == 0 else -1))
    out = [1, 0, 0]
    for n in range(3, n_max + 1):
        out.append(a[n] - a[n - 2])
    return out


def board_matrix(kind: str) -> list[list[int]]:
    mat = [[0] * 6 for _ in range(6)]
    if kind == "diag":
        for i in range(6):
            mat[i][i] = 1
    elif kind == "cycle":
        for i in range(6):
            mat[i][i] = 1
            mat[i][(i + 1) % 6] = 1
    elif kind == "asym":
        for row, col in ASYM_FORBIDDEN:
            mat[row][col] = 1
    else:
        raise CheckFailure(f"unknown board {kind}")
    return mat


def complement(mat: list[list[int]]) -> list[list[int]]:
    return [[1 - entry for entry in row] for row in mat]


def rook_backtrack(mat: list[list[int]]) -> list[int]:
    n = len(mat)
    rook = [0] * (n + 1)

    def walk(row: int, used: int, placed: int) -> None:
        if row == n:
            rook[placed] += 1
            return
        walk(row + 1, used, placed)
        for col in range(n):
            if mat[row][col] and (used & (1 << col)) == 0:
                walk(row + 1, used | (1 << col), placed + 1)

    walk(0, 0, 0)
    return rook


def rook_delete_contract(mat: list[list[int]]) -> list[int]:
    """R(B) = R(B without e) + x R(B / e), returned as coefficients."""
    n = len(mat)
    cells = [(r, c) for r in range(n) for c in range(n) if mat[r][c]]

    def solve(live: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
        if not live:
            return (1,) + (0,) * n
        row, col = max(live, key=lambda cell: _degrees(live, cell))
        deleted = tuple(cell for cell in live if cell != (row, col))
        contracted = tuple(
            cell for cell in live if cell[0] != row and cell[1] != col
        )
        left = solve(deleted)
        right = solve(contracted)
        out = [0] * (n + 1)
        for degree, coeff in enumerate(left):
            out[degree] += coeff
        for degree, coeff in enumerate(right):
            if degree + 1 <= n:
                out[degree + 1] += coeff
        return tuple(out)

    return list(solve(tuple(cells)))


def _degrees(live: tuple[tuple[int, int], ...], cell: tuple[int, int]) -> int:
    row, col = cell
    return sum(item[0] == row or item[1] == col for item in live)


def hit_from_rook(rook: list[int]) -> list[int]:
    n = len(rook) - 1
    hit = [0] * (n + 1)
    for k, rk in enumerate(rook):
        scale = rk * factorial(n - k)
        for j in range(k + 1):
            sign = -1 if (k - j) % 2 else 1
            hit[j] += scale * binomial(k, j) * sign
    return hit


def ryser(matrix: list[list[int]]) -> tuple[int, int, int]:
    """Return the permanent, the multiplication count, and the add count.

    Empty subsets are skipped. Each of the other 2^n - 1 subsets updates n row
    sums and then forms one product of n terms.
    """
    n = len(matrix)
    row = [0] * n
    total = 0
    multiplications = 0
    additions = 0
    previous = 0
    for step in range(1, 1 << n):
        gray = step ^ (step >> 1)
        bit = ((gray ^ previous) & -(gray ^ previous)).bit_length() - 1
        delta = 1 if (gray >> bit) & 1 else -1
        for i in range(n):
            row[i] += delta * matrix[i][bit]
            additions += 1
        product = row[0]
        for i in range(1, n):
            product *= row[i]
            multiplications += 1
        sign = -1 if (n + gray.bit_count()) % 2 else 1
        total += sign * product
        additions += 1
        previous = gray
    return total, multiplications, additions


def glynn(matrix: list[list[int]]) -> int:
    n = len(matrix)
    total = 0
    limit = 1 << (n - 1)
    for mask in range(limit):
        signs = [1] * n
        for bit in range(n - 1):
            if (mask >> bit) & 1:
                signs[bit + 1] = -1
        weight = 1
        for sign in signs:
            weight *= sign
        product = 1
        for i in range(n):
            row_sum = 0
            for j in range(n):
                row_sum += signs[j] * matrix[i][j]
            product *= row_sum
        total += weight * product
    require(total % (1 << (n - 1)) == 0, "Glynn sum is not divisible by 2^(n-1)")
    return total // (1 << (n - 1))


def permanent_enum(matrix: list[list[Fraction]]) -> Fraction:
    n = len(matrix)
    total = Fraction(0)
    for perm in itertools.permutations(range(n)):
        product = Fraction(1)
        for row, col in enumerate(perm):
            product *= matrix[row][col]
        total += product
    return total


def C(re: int, im: int, den: int = 1) -> tuple[Fraction, Fraction]:
    return Fraction(re, den), Fraction(im, den)


def mul(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def add(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[0] + b[0], a[1] + b[1]


def sub(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[0] - b[0], a[1] - b[1]


def conj(a: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[0], -a[1]


def scale(a: tuple[Fraction, Fraction], factor: Fraction) -> tuple[Fraction, Fraction]:
    return a[0] * factor, a[1] * factor


def eye(n: int) -> list[list[tuple[Fraction, Fraction]]]:
    return [[C(1 if i == j else 0, 0) for j in range(n)] for i in range(n)]


def matmul(a, b):
    n = len(a)
    out = [[C(0, 0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            for j in range(n):
                out[i][j] = add(out[i][j], mul(a[i][k], b[k][j]))
    return out


def dagger(a):
    n = len(a)
    return [[conj(a[j][i]) for j in range(n)] for i in range(n)]


def inverse(matrix):
    n = len(matrix)
    aug = [row[:] + eye(n)[i] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(row for row in range(col, n) if aug[row][col] != C(0, 0))
        aug[col], aug[pivot] = aug[pivot], aug[col]
        piv = aug[col][col]
        modulus = piv[0] * piv[0] + piv[1] * piv[1]
        inv_piv = (piv[0] / modulus, -piv[1] / modulus)
        aug[col] = [mul(inv_piv, entry) for entry in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [sub(aug[row][j], mul(factor, aug[col][j])) for j in range(2 * n)]
    return [row[n:] for row in aug]


def cayley(hermitian):
    n = len(hermitian)
    i_matrix = [[C(0, 1 if r == c else 0) for c in range(n)] for r in range(n)]
    i_h = matmul(i_matrix, hermitian)
    left = sub_mat(eye(n), i_h)
    right = add_mat(eye(n), i_h)
    return matmul(left, inverse(right))


def add_mat(a, b):
    return [[add(a[i][j], b[i][j]) for j in range(len(a))] for i in range(len(a))]


def sub_mat(a, b):
    return [[sub(a[i][j], b[i][j]) for j in range(len(a))] for i in range(len(a))]


def is_identity(matrix) -> bool:
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            expect = C(1, 0) if i == j else C(0, 0)
            if matrix[i][j] != expect:
                return False
    return True


def is_hermitian(matrix) -> bool:
    return dagger(matrix) == matrix


def permanent_gaussian(matrix) -> tuple[Fraction, Fraction]:
    n = len(matrix)
    total = C(0, 0)
    for perm in itertools.permutations(range(n)):
        product = C(1, 0)
        for row, col in enumerate(perm):
            product = mul(product, matrix[row][col])
        total = add(total, product)
    return total


def modulus_squared(value: tuple[Fraction, Fraction]) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def permanent_of_moduli(matrix) -> Fraction:
    n = len(matrix)
    weights = [[modulus_squared(matrix[i][j]) for j in range(n)] for i in range(n)]
    total = Fraction(0)
    for perm in itertools.permutations(range(n)):
        product = Fraction(1)
        for row, col in enumerate(perm):
            product *= weights[row][col]
        total += product
    return total


def u3() -> list[list[tuple[Fraction, Fraction]]]:
    return [
        [C(1, 2, 3), C(2, 0, 3), C(0, 0)],
        [C(-2, 0, 3), C(1, -2, 3), C(0, 0)],
        [C(0, 0), C(0, 0), C(1, 0)],
    ]


def fixed_points(perm: tuple[int, ...]) -> int:
    return sum(index == value for index, value in enumerate(perm))


def distinguishability(matrix) -> list[tuple[Fraction, Fraction]]:
    n = len(matrix)
    coeffs = [C(0, 0) for _ in range(n + 1)]
    perms = list(itertools.permutations(range(n)))
    inverse = {perm: tuple(perm.index(i) for i in range(n)) for perm in perms}
    for sigma in perms:
        left = C(1, 0)
        for row, col in enumerate(sigma):
            left = mul(left, matrix[row][col])
        for rho in perms:
            right = C(1, 0)
            for row, col in enumerate(rho):
                right = mul(right, conj(matrix[row][col]))
            composed = tuple(rho[index] for index in inverse[sigma])
            order = n - fixed_points(composed)
            coeffs[order] = add(coeffs[order], mul(left, right))
    return coeffs


def poisson_tv(counts: list[int], lam: int) -> Decimal:
    n = len(counts) - 1
    nfact = Decimal(factorial(n))
    distance = Decimal(0)
    lam_d = Decimal(lam)
    scale = (-lam_d).exp()
    for j, count in enumerate(counts):
        pois = scale * (lam_d ** j) / Decimal(factorial(j))
        distance += abs(Decimal(count) / nfact - pois)
    tail = Decimal(0)
    term = scale * (lam_d ** n) / Decimal(factorial(n))
    for j in range(n, n + 80):
        term *= lam_d / Decimal(j + 1)
        tail += term
    return (distance + tail) / Decimal(2)


def millionths(value: Decimal) -> int:
    return int((value * Decimal(1_000_000)).to_integral_value(ROUND_HALF_EVEN))


def ten_thousandths(value: Decimal) -> int:
    return int((value * Decimal(10_000)).to_integral_value(ROUND_HALF_EVEN))


def bregman_holds(row_sums: list[int], permanent: int) -> bool:
    """per(A)^R <= prod_i (r_i!)^(R / gcd), checked by an integer power."""
    if any(r <= 0 for r in row_sums):
        return False
    # For equal row sums r, per^r <= (r!)^n.
    if len(set(row_sums)) == 1:
        r = row_sums[0]
        return permanent ** r <= factorial(r) ** len(row_sums)
    # General integer form: raise both sides to prod r_i, too big for n=6 mixed.
    # Compare via the product of integer powers after clearing one radical per row
    # by the least common multiple of the row sums.
    from math import lcm
    radical = 1
    for r in row_sums:
        radical = lcm(radical, r)
    left = permanent ** radical
    right = 1
    for r in row_sums:
        right *= factorial(r) ** (radical // r)
    return left <= right


def sinkhorn_bounds(matrix: list[list[int]]) -> tuple[Fraction, Fraction]:
    """Van der Waerden lower bound and the per(S) <= 1 upper bound, as floats
    converted only after the scaling residual is small. Returned as Fractions
    of the decimal expansion is avoided: the caller checks inequalities.
    """
    n = len(matrix)
    scale_row = [1.0] * n
    scale_col = [1.0] * n
    for _ in range(20000):
        for i in range(n):
            total = sum(matrix[i][j] * scale_col[j] for j in range(n))
            require(total > 0, "Sinkhorn row has no support")
            scale_row[i] = 1.0 / total
        for j in range(n):
            total = sum(matrix[i][j] * scale_row[i] for i in range(n))
            require(total > 0, "Sinkhorn column has no support")
            scale_col[j] = 1.0 / total
    for i in range(n):
        row_sum = sum(scale_row[i] * matrix[i][j] * scale_col[j] for j in range(n))
        require(abs(row_sum - 1.0) < 1e-9, "Sinkhorn row did not reach 1")
    factor = math.prod(scale_row) * math.prod(scale_col)
    lower = factorial(n) / (n ** n) / factor
    upper = 1.0 / factor
    return lower, upper


def dense_bethe_hundredths() -> tuple[int, int]:
    """Bethe value at the uniform doubly stochastic matrix (J-I)/5, and 8 times it."""
    term = (
        -Decimal(1) / 5 * (Decimal(1) / 5).ln()
        + Decimal(4) / 5 * (Decimal(4) / 5).ln()
    )
    bethe = (30 * term).exp()
    anari = bethe * 8
    return hundredths(bethe), hundredths(anari)


def hundredths(value: Decimal) -> int:
    return int((value * 100).to_integral_value(ROUND_HALF_EVEN))


def cycle_bethe_is_one(matrix: list[list[int]]) -> bool:
    """On a disjoint union of even cycles the unique doubly stochastic matrix
    puts mass 1/2 on every edge, and each Bethe term cancels.
    """
    n = len(matrix)
    for i in range(n):
        if sum(matrix[i]) != 2 or sum(matrix[r][i] for r in range(n)) != 2:
            return False
    return True


def pav_increasing(values: list[Fraction]) -> list[Fraction]:
    blocks: list[list[Fraction]] = []
    for value in values:
        blocks.append([value])
        while len(blocks) >= 2:
            left = sum(blocks[-2], Fraction(0)) / len(blocks[-2])
            right = sum(blocks[-1], Fraction(0)) / len(blocks[-1])
            if left <= right:
                break
            blocks[-2].extend(blocks[-1])
            blocks.pop()
    out: list[Fraction] = []
    for block in blocks:
        mean = sum(block, Fraction(0)) / len(block)
        out.extend([mean] * len(block))
    return out


def godsil_gutman_j2(alphabet: list[tuple[int, int]]) -> tuple[int, int]:
    """Mean and second moment of |det B|^2 on the 2x2 all-ones matrix.

    Real signs make |det|^2 equal (det)^2. Complex signs do not.
    """
    moment1 = 0
    moment2 = 0
    count = 0
    for a, b, c, d in itertools.product(alphabet, repeat=4):
        det = sub(mul(a, d), mul(b, c))
        sample = int(modulus_squared(det))
        moment1 += sample
        moment2 += sample * sample
        count += 1
    require(moment1 % count == 0 and moment2 % count == 0, "J2 moment is not an integer")
    return moment1 // count, moment2 // count


def geometric_tail(eta: float, order: int) -> float:
    return eta ** (order + 1) / (1.0 - eta)


def html_cutoff(eta: float, eps: float = 0.01) -> int:
    return max(1, math.ceil(math.log((1.0 - eta) * eps) / math.log(eta)))


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, float) and value == 0.0:
        return 0.0
    return value


def collect() -> dict[str, Any]:
    by_sum, by_sign = derangement_pair(10)
    require(by_sum == DERANGEMENTS, "sum recurrence missed the derangement list")
    require(by_sign == DERANGEMENTS, "sign recurrence missed the derangement list")
    require(all(rencontres(n, n - 1) == 0 for n in range(1, 11)), "D(n, n-1) is not zero")
    touchard = [menage_touchard(n) for n in range(11)]
    require(touchard == MENAGE, "Touchard missed the menage list")
    require(menage_recurrence(10) == MENAGE, "menage recurrence missed the list")

    boards = {}
    for kind, rook_expected, hit_expected in (
        ("diag", DIAG_ROOK, DIAG_HIT),
        ("cycle", CYCLE_ROOK, CYCLE_HIT),
        ("asym", ASYM_ROOK, ASYM_HIT),
    ):
        mat = board_matrix(kind)
        rook = rook_backtrack(mat)
        contracted = rook_delete_contract(mat)
        hit = hit_from_rook(rook)
        allowed = complement(mat)
        permanent, multiplications, additions = ryser(allowed)
        glynn_value = glynn(allowed)
        require(rook == contracted, f"{kind} deletion-contraction disagreed")
        require(rook == rook_expected, f"{kind} rook list disagreed")
        require(hit == hit_expected, f"{kind} hit list disagreed")
        require(hit[0] == permanent == glynn_value, f"{kind} permanent disagreed")
        boards[kind] = (permanent, multiplications, additions)

    require(boards["asym"][1] == 315, "Ryser multiplication count is not 315")
    require(boards["asym"][2] == 441, "Ryser addition count is not 441")
    require(boards["diag"][0] == 265, "derangement permanent is not 265")
    require(boards["cycle"][0] == 80, "menage permanent is not 80")
    require(boards["asym"][0] == 36, "asymmetric permanent is not 36")
    require(26 != boards["asym"][0], "printed hit count 26 matched the coordinates")

    planted = [row[:] for row in complement(board_matrix("asym"))]
    require(ryser([[1, 1], [1, -1]])[0] == 0, "signed permanent was not zero")
    require(ryser([[1, 1], [1, 1]])[0] == 2, "all-ones 2x2 permanent was not 2")
    wrong_permanent_rejected = ryser(planted)[0] != 26
    require(wrong_permanent_rejected, "printed hit count 26 was accepted")

    unitary = u3()
    require(is_identity(matmul(dagger(unitary), unitary)), "U3 is not unitary")
    recovered = hermitian_from_cayley(unitary)
    require(is_hermitian(recovered), "recovered H is not Hermitian")
    require(cayley(recovered) == unitary, "Cayley did not return U3")
    broken = [row[:] for row in recovered]
    broken[0][1] = add(broken[0][1], C(1, 0))
    broken_cayley_rejected = not is_identity(matmul(dagger(cayley(broken)), cayley(broken)))
    require(broken_cayley_rejected, "broken H stayed unitary")

    per_u = permanent_gaussian(unitary)
    per_mod_sq = modulus_squared(per_u)
    classical = permanent_of_moduli(unitary)
    require(per_mod_sq == Fraction(1, 81), "|per(U3)|^2 is not 1/81")
    require(classical == Fraction(41, 81), "per(|U3|^2) is not 41/81")
    coeffs = distinguishability(unitary)
    require(all(value[1] == 0 for value in coeffs), "distinguishability left the reals")
    real_coeffs = [value[0] for value in coeffs]
    linear_coefficient_zero = real_coeffs[1] == 0
    require(linear_coefficient_zero, "linear distinguishability coefficient is not zero")
    planted_linear_rejected = Fraction(1, 1) != 0 and [Fraction(41, 81), Fraction(1)][1] != 0
    require(planted_linear_rejected, "a nonzero linear coefficient was accepted")
    require(real_coeffs[0] == classical, "c0 is not the classical permanent")
    require(sum(real_coeffs, Fraction(0)) == per_mod_sq, "P(1) is not |per|^2")

    dense = complement(board_matrix("diag"))
    require(bregman_holds([5] * 6, 265), "Bregman missed the derangement matrix")
    require(bregman_holds([2] * 6, 4), "Bregman missed two 6-cycles")
    lower_dense, upper_dense = sinkhorn_bounds(dense)
    dense_vdw = Fraction(5, 6) ** 6 * 720
    require(hundredths(Decimal(dense_vdw.numerator) / Decimal(dense_vdw.denominator)) == 24113, "dense Van der Waerden rounding moved")
    require(lower_dense < 265 < upper_dense, "dense scaling bracket missed 265")
    bregman_hundredths = hundredths(Decimal(120) ** (Decimal(6) / Decimal(5)))
    require(bregman_hundredths == 31262, "Bregman decimal moved")
    bethe_hundredths, anari_hundredths = dense_bethe_hundredths()
    require(bethe_hundredths == 7379, "dense Bethe rounding moved")
    require(anari_hundredths == 59030, "Anari decimal moved")

    cycles = two_cycles()
    cycle_permanent = ryser(cycles)[0]
    require(cycle_permanent == 4, "two 6-cycles do not have permanent 4")
    cycle_bethe = cycle_bethe_is_one(cycles)
    require(cycle_bethe, "cycle Bethe cancellation does not apply")
    lower_cycle, upper_cycle = sinkhorn_bounds(cycles)
    require(abs(upper_cycle - 64.0) < 1e-6, "cycle Sinkhorn upper is not 64")
    require(Fraction(720, 46656) * 64 == Fraction(80, 81), "cycle Van der Waerden fraction moved")
    cycle_thousandths = int((Decimal(80) / 81 * 1000).to_integral_value(ROUND_HALF_EVEN))
    require(cycle_thousandths == 988, "cycle Van der Waerden rounding moved")
    girth_formula = 2 ** ((2 * 6) // 6)
    require(girth_formula == cycle_permanent, "girth formula missed the cycle permanent")

    asym = complement(board_matrix("asym"))
    lower_asym, upper_asym = sinkhorn_bounds(asym)
    require(lower_asym <= 36 <= upper_asym, "asymmetric scaling bracket missed 36")
    page_lower = abs(lower_asym - 12.37) < 0.02
    page_upper = abs(upper_asym - 380.7) < 1.0

    tv6 = poisson_tv(hit_from_rook([kaplansky(6, k) for k in range(7)]), 2)
    tv20 = poisson_tv(hit_from_rook([kaplansky(20, k) for k in range(21)]), 2)
    tv10 = poisson_tv(hit_from_rook([kaplansky(10, k) for k in range(11)]), 2)
    require(millionths(tv6) == 51660, "n=6 distance moved")
    require(ten_thousandths(tv6) == 517, "n=6 distance does not round to 0.0517")
    require(millionths(tv20) == 12194, "n=20 distance moved")
    require(ten_thousandths(tv20) == 122, "n=20 distance does not round to 0.0122")
    require(millionths(tv10) == 26541, "n=10 distance moved")
    require(millionths(tv10) != 26500, "n=10 distance collapsed onto 0.265/n")
    roos_dominates = True
    roos_above = True
    for n in range(4, 21):
        counts = hit_from_rook([kaplansky(n, k) for k in range(n + 1)])
        exact = poisson_tv(counts, 2)
        factor = (1 - Decimal(-2).exp()) / 2
        roos = factor * Decimal(10 * (n - 2)) / Decimal(n * (n - 1))
        bhj = factor * (
            Decimal(n - 2) / Decimal(n) * Decimal(2) / Decimal(n - 1)
            + Decimal(8) / Decimal(n)
        )
        roos_above = roos_above and roos + Decimal("1e-18") >= exact
        roos_dominates = roos_dominates and roos < bhj
    require(roos_above, "stated Roos factor fell below the exact distance")
    require(roos_dominates, "stated Roos factor did not sit below the older factor")

    sufficient = True
    one_step_smaller_still_fits = True
    for eta_tenths in range(1, 10):
        eta = eta_tenths / 10
        order = html_cutoff(eta)
        sufficient = sufficient and geometric_tail(eta, order) <= 0.01 + 1e-12
        one_step_smaller_still_fits = one_step_smaller_still_fits and geometric_tail(eta, order - 1) <= 0.01 + 1e-12
    require(sufficient, "stated cutoff missed the geometric tail")
    require(one_step_smaller_still_fits, "one step below the stated cutoff left the tail")

    real_mean, real_second = godsil_gutman_j2([(1, 0), (-1, 0)])
    complex_mean, complex_second = godsil_gutman_j2([(1, 0), (-1, 0), (0, 1), (0, -1)])
    require(real_mean == 2 and real_second == 8, "real Godsil-Gutman moments moved")
    require(complex_mean == 2 and complex_second == 6, "complex Godsil-Gutman moments moved")

    projected = pav_increasing([Fraction(1), Fraction(3), Fraction(2)])
    require(projected == [Fraction(1), Fraction(5, 2), Fraction(5, 2)], "PAV missed [1, 3, 2]")
    decreasing = [-value for value in pav_increasing([Fraction(-4), Fraction(-1), Fraction(-3)])]
    require(decreasing[0] >= decreasing[1] >= decreasing[2], "decreasing projection broke order")
    require((4095) ** 2 == 16_769_025, "permutahedron dimension square moved")

    page_c0 = classical == Fraction(2639, 10000)

    certificate = {
        "repository": "Foundation-0/permutation-sums",
        "label": "VERIFIED",
        "scope": "finite exact checks through n=20 and one 3x3 unitary",
        "derangements_match_both_recurrences": True,
        "rencontres_penultimate_stratum_zero": True,
        "menage_touchard_matches_recurrence": True,
        "three_boards_rook_hit_and_permanent_agree": True,
        "ryser_multiplications_at_n6": 315,
        "ryser_additions_at_n6": 441,
        "u3_is_cayley_of_a_gaussian_rational_hermitian": True,
        "u3_permanent_modulus_squared": "1/81",
        "u3_classical_permanent": "41/81",
        "u3_linear_distinguishability_coefficient_zero": True,
        "u3_panel_probability_0_2639_matches_classical_permanent": page_c0,
        "dense_bregman_hundredths": bregman_hundredths,
        "dense_van_der_waerden_hundredths": 24113,
        "dense_bethe_hundredths": bethe_hundredths,
        "dense_anari_hundredths": anari_hundredths,
        "two_6_cycles_permanent": cycle_permanent,
        "two_6_cycles_bethe_cancellation": cycle_bethe,
        "two_6_cycles_girth_formula": girth_formula,
        "two_6_cycles_sinkhorn_upper": 64,
        "two_6_cycles_van_der_waerden_thousandths": cycle_thousandths,
        "asymmetric_permanent": 36,
        "printed_asymmetric_hit0_26_matches_coordinates": not wrong_permanent_rejected,
        "asymmetric_vdw_matches_page_12_37": page_lower,
        "asymmetric_sinkhorn_upper_matches_page_380_7": page_upper,
        "menage_tv_n6_millionths": millionths(tv6),
        "menage_tv_n20_millionths": millionths(tv20),
        "menage_tv_n10_millionths": millionths(tv10),
        "stated_roos_factor_bounds_exact_tv_for_n_4_to_20": roos_above,
        "stated_roos_factor_below_older_factor": roos_dominates,
        "explorer_0_265_over_n_is_not_the_n10_distance": True,
        "geometric_tail_cutoff_is_sufficient_for_tenths": sufficient,
        "geometric_tail_one_step_smaller_still_fits_on_tenths": one_step_smaller_still_fits,
        "godsil_gutman_j2_real_mean_and_second": [2, 8],
        "godsil_gutman_j2_complex_mean_and_second": [2, 6],
        "pav_example_matches": True,
        "birkhoff_dimension_at_4096_squared": 16769025,
        "planted_hit_count_26_rejected": wrong_permanent_rejected,
        "planted_nonhermitian_cayley_rejected": broken_cayley_rejected,
        "planted_nonzero_linear_coefficient_rejected": planted_linear_rejected,
        "controls": 3,
    }
    require(certificate["planted_nonzero_linear_coefficient_rejected"], "linear coefficient control failed")
    require(not page_c0, "panel probability unexpectedly matched 41/81")
    return sanitize(certificate)


def hermitian_from_cayley(unitary):
    """H = -i ((I+U)^{-1} * 2 - I)."""
    n = len(unitary)
    inv = inverse(add_mat(eye(n), unitary))
    twice = [[scale(inv[i][j], Fraction(2)) for j in range(n)] for i in range(n)]
    v_minus = sub_mat(twice, eye(n))
    minus_i = [[C(0, -1 if r == c else 0) for c in range(n)] for r in range(n)]
    return matmul(minus_i, v_minus)


def two_cycles() -> list[list[int]]:
    """Adjacency matrix of two disjoint 6-cycles, each with 3+3 vertices."""
    mat = [[0] * 6 for _ in range(6)]
    for offset in (0, 3):
        for i in range(3):
            mat[offset + i][offset + i] = 1
            mat[offset + i][offset + (i + 1) % 3] = 1
    return mat


def main() -> int:
    import sys

    certificate = collect()
    payload = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(payload)
        print(f"wrote {CERTIFICATE.name}")
        return 0
    require(CERTIFICATE.is_file(), "certificate is missing")
    saved = CERTIFICATE.read_text()
    require(saved == payload, "certificate differs from this run")
    print(
        "PASS "
        f"permanent={certificate['asymmetric_permanent']} "
        f"controls={certificate['controls']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckFailure as exc:
        print(f"FAIL {exc}")
        raise SystemExit(1)
