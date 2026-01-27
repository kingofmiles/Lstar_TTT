# Fuzzer__VRI__2025
Problem Definition：

We aim to infer a specification of valid API call sequences for the Fantom JSON-RPC interface, using active automata learning.


Start State：
A sequence is executed from an initial state where:
a valid account address is known,
a valid block tag (e.g. latest) is fixed,
the JSON-RPC endpoint is reachable.


End State (Acceptance Condition)：
A sequence is considered accepting if, after executing all API calls, we have successfully obtained a complete account snapshot at the given block tag, consisting of:
account balance,
transaction count (nonce),
account bytecode.
Negative Sequences.
Any sequence is immediately labeled as negative if any API call in the sequence returns a JSON-RPC error or fails to produce a valid response.

Thus, the target language consists of all API call sequences that, starting from the initial state, terminate without error and result in a complete account snapshot.
