# -*- coding: utf-8 -*-
"""Driver común: python3 actoN.py [prev i,j,k]  → renderiza actoN.mp4 con motor/cine.py"""
import sys, os
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import escenas, cine
from guion_data import ACTOS


def acto(n):
    idx = 1
    for a in ACTOS:
        a = dict(a); a["idx0"] = idx
        k = len(a.get("gancho", [])) + len(a["lineas"])
        if a["n"] == n:
            return a
        idx += k


def main(n):
    a = acto(n)
    voz = os.path.join(AQUI, "voz")
    out = os.path.join(AQUI, "acto%d.mp4" % n)
    if len(sys.argv) > 2 and sys.argv[1] == "prev":
        idx = [int(x) for x in sys.argv[2].split(",")]
        tl, tot = cine.render_acto(a, escenas, out, voz, preview=idx)
        print("dur", tot, "items", len(tl))
        return
    tot = cine.render_acto(a, escenas, out, voz)
    print("acto", n, "dur", tot)
