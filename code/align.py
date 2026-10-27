"""Shared alignment counting (numba). Coordinates are British National Grid metres.

A k-point alignment is a set of k sites such that, taking its two outermost sites as the ends of a straight
segment of length between LMIN and LMAX, every other site in the set lies within half the corridor width of
that segment (measured at right angles, and between the two ends). For each pair of end sites (i, j) I count
m, the number of other sites inside its corridor; the pair then contributes C(m, k-2) alignments of k sites.
"""
import math
import numpy as np
from numba import njit

KMAX = 6


@njit(cache=True)
def _comb(n, r):
    if r < 0 or r > n: return 0.0
    if r == 0: return 1.0
    v = 1.0
    for i in range(r):
        v = v * (n - i) / (i + 1)
    return v


@njit(cache=True)
def count_alignments(x, y, half_w, lmin, lmax):
    """Return counts[k] for k = 0..KMAX (only 3..KMAX used) and the longest alignment size."""
    n = x.shape[0]
    out = np.zeros(KMAX + 1)
    best = 2
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]; dy = y[j] - y[i]
            d = math.sqrt(dx * dx + dy * dy)
            if d < lmin or d > lmax: continue
            ux = dx / d; uy = dy / d
            m = 0
            for l in range(n):
                if l == i or l == j: continue
                vx = x[l] - x[i]; vy = y[l] - y[i]
                t = vx * ux + vy * uy
                if t <= 0.0 or t >= d: continue
                p = vx * uy - vy * ux
                if p < 0: p = -p
                if p <= half_w: m += 1
            if m >= 1:
                for k in range(3, KMAX + 1):
                    out[k] += _comb(m, k - 2)
                if m + 2 > best: best = m + 2
    return out, best


@njit(cache=True)
def list_alignments(x, y, half_w, lmin, lmax, mmin):
    """End pairs whose corridor holds at least mmin other sites: rows (i, j, m)."""
    n = x.shape[0]
    res = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]; dy = y[j] - y[i]
            d = math.sqrt(dx * dx + dy * dy)
            if d < lmin or d > lmax: continue
            ux = dx / d; uy = dy / d
            m = 0
            for l in range(n):
                if l == i or l == j: continue
                vx = x[l] - x[i]; vy = y[l] - y[i]
                t = vx * ux + vy * uy
                if t <= 0.0 or t >= d: continue
                p = vx * uy - vy * ux
                if p < 0: p = -p
                if p <= half_w: m += 1
            if m >= mmin:
                res.append((i, j, m))
    return res


@njit(cache=True)
def members(x, y, i, j, half_w):
    dx = x[j] - x[i]; dy = y[j] - y[i]
    d = math.sqrt(dx * dx + dy * dy); ux = dx / d; uy = dy / d
    res = [i]
    for l in range(x.shape[0]):
        if l == i or l == j: continue
        vx = x[l] - x[i]; vy = y[l] - y[i]
        t = vx * ux + vy * uy
        if t <= 0.0 or t >= d: continue
        p = vx * uy - vy * ux
        if p < 0: p = -p
        if p <= half_w: res.append(l)
    res.append(j)
    return res


def seg_dist(px, py, ax, ay, bx, by):
    """Perpendicular distance from points to segment AB (inf if the foot falls outside AB), and position t in metres."""
    dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    vx, vy = px - ax, py - ay
    t = vx * ux + vy * uy
    p = np.abs(vx * uy - vy * ux)
    p = np.where((t >= 0) & (t <= L), p, np.inf)
    return p, t
