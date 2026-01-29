# Inferring API Call Sequence Specifications via Active Automata Learning

## Overview

This project investigates whether valid API call sequence specifications for the Fantom JSON-RPC interface can be inferred without example traces, using active automata learning.

We implement and compare two classical learning algorithms:

  ·L* (Angluin, 1987) — table-based learner

  ·TTT (Isberner et al., 2014) — discrimination-tree-based learner

Both learners interact with a live JSON-RPC endpoint through a membership oracle.


## Problem Definition

We aim to infer a deterministic finite automaton (DFA) that characterizes valid API call sequences under the following semantics:

A sequence is accepted if and only if:

  1.The JSON-RPC endpoint is reachable at the start of execution.

  2.All API calls in the sequence return successful responses (i.e., no JSON-RPC error occurs).

  3.The sequence respects predefined API order constraints required to retrieve account-related information.

  4.Execution reaches a complete account snapshot state, consisting of:

  ·account balance,

  ·transaction count (nonce),

  ·contract bytecode.

Any sequence is rejected immediately once an API call returns an error response.

## Alphabet

Let Σ be a finite alphabet of abstract API symbols, where each symbol corresponds to a concrete JSON-RPC method invocation with fixed parameters.

Example (simplified):

    ALPHABET = ["A", "T", "B", "C", "M"]


Each symbol is mapped to a JSON-RPC call in api_alphabet.py.

## Learning Setup

### Membership Oracle
Executes API sequences against a live Fantom JSON-RPC endpoint and returns accept/reject based on runtime behavior.

### Equivalence Oracle
Implements randomized testing to search for counterexamples between the learned DFA and the real system.

### Learners

  ·my_lstar/ — classical L* implementation

  ·my_ttt/ — TTT implementation

## Experiments

We evaluate learners under different target language complexities:

·Simple language (small alphabet, few states)

·Complex language (larger alphabet, non-trivial ordering constraints)

Metrics recorded:

·Number of DFA states

·Number of membership queries

·Total learning time

## Results (Summary)

For simple target languages, L* may converge faster due to low table complexity.

For more complex languages, TTT typically scales better and avoids table blow-up.

Both learners successfully infer meaningful DFA specifications.

## Repository Structure
    .
    ├── api_alphabet.py
    ├── oracle.py
    ├── equivalence.py
    ├── compare.py
    ├── run_lstar.py
    ├── run_ttt.py
    ├── my_lstar/
    ├── my_ttt/
    ├── dfa_lstar.pdf
    └── dfa_ttt.pdf
