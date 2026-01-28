# Fuzzer__VRI__2025
Problem Definition

We aim to infer a specification of valid API call sequences for the Fantom JSON-RPC interface using active automata learning, without assuming any prior examples of valid or invalid sequences.


The system under learning is accessed through a membership oracle that executes API call sequences against a live JSON-RPC endpoint.


A sequence is accepted if and only if:

1.The JSON-RPC endpoint is reachable at the start of execution.

2.All API calls in the sequence return successful responses (i.e., no JSON-RPC error occurs).

3.The sequence respects predefined API order constraints required to obtain account-related information.

4.The execution reaches a complete account snapshot state, consisting of:

  (1)account balance,
  
  (2)transaction count (nonce),
  
  (3)contract bytecode.

Any sequence is rejected immediately once an API call returns an error response.


Let Σ be a finite alphabet of abstract API symbols, where each symbol corresponds to a concrete JSON-RPC method invocation with fixed parameters.
The goal is to infer a deterministic finite automaton (DFA) that recognizes exactly the set of valid API call sequences under the above semantics.
