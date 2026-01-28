# Fuzzer__VRI__2025
Problem Definition：

We aim to infer a specification of valid API call sequences for the Fantom JSON-RPC interface, using active automata learning.

Accepted sequences are those that:
1. Start from a reachable JSON-RPC endpoint
2. Respect API order constraints (e.g., A → T → B)
3. Reach a complete account snapshot
4. Are rejected immediately upon any API error



ALPHABET：
Let Σ = {bal, nonce, code}.

A word w ∈ Σ* is accepted iff:

1. All API calls in w return successful JSON-RPC responses (no error).
2. w contains exactly one occurrence of each symbol in Σ.
3. The order constraint holds: nonce ≺ bal ≺ code.
