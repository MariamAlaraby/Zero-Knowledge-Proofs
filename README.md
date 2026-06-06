# Zero-Knowledge Proof Simulator

An interactive desktop application that visually demonstrates two foundational Zero-Knowledge Proof (ZKP) protocols: **Graph 3-Colorability** and **Graph Isomorphism**.

Built with Python and PyQt5 as part of a university research project on interactive proof systems.

---

## Features

### 🎨 3-Colorability Protocol (GMW)
- Three selectable graph configurations: Petersen-like (6 nodes), Triangle (3 nodes), and Wheel (7 nodes)
- Step-by-step execution or automated 30-round simulation
- Displays all vertices in committed (hidden) state, then reveals only the two endpoints of the challenged edge
- Live confidence percentage, round counter, and pass/fail history
- **Cheat Mode:** corrupts the prover's response with 50% probability to demonstrate soundness

### 🔁 Graph Isomorphism Protocol
- Randomly generated isomorphic graph pairs of 4, 5, 6, or 7 nodes
- Simulates the commit → challenge → reveal cycle for up to 20 rounds
- Verifier issues a binary challenge (map H′ → G or H′ → H)
- **Cheat Mode** available

---

## Requirements
Python 3.x
PyQt5
Install dependencies:
```
pip install PyQt5
```
---

## How to Run
```
python v6_zkp_native.py
```
---

## How It Works

Each round follows the standard ZKP protocol structure:

1. **Commit** — The prover applies a random permutation and locks all vertices
2. **Challenge** — The verifier randomly selects one edge
3. **Open** — The prover reveals only the two challenged vertices
4. **Verify** — The verifier checks that the two colours are distinct

The confidence counter updates after each round using the formula **1 − (1/|E|)ᵏ** for 3-Colorability and **1 − (1/2)ᵏ** for Graph Isomorphism.

---

