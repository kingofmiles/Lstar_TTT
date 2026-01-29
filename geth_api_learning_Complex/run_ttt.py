import time
# run_ttt.py
from api_alphabet import ALPHABET
from oracle import membership_oracle,reset_counter,API_CALL_COUNT
from equivalence import equivalence_oracle
from my_ttt.learner import TTTLearner
print("[DEBUG run_lstar] ALPHABET =", ALPHABET)

reset_counter()
start = time.time()
learner = TTTLearner(
    alphabet=ALPHABET,
    membership_oracle=membership_oracle,
    equivalence_oracle=equivalence_oracle
)

dfa = learner.learn()
end = time.time()
ttt_time = end - start
ttt_requests = API_CALL_COUNT
print(f"TTT Time: {ttt_time:.2f}s, Frequency: {ttt_requests()}")
print(dfa)
dfa.visualize("dfa_ttt")
