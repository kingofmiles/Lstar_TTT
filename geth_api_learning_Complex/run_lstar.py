import time
from my_lstar.learner import LStar
from oracle import membership_oracle, reset_counter, API_CALL_COUNT
from equivalence import equivalence_oracle
from api_alphabet import ALPHABET
print("[DEBUG run_lstar] ALPHABET =", ALPHABET)
reset_counter()
start = time.time()
learner = LStar(ALPHABET, membership_oracle, equivalence_oracle)
dfa = learner.learn()
end = time.time()
lstar_time = end - start
lstar_requests = API_CALL_COUNT

print(f"L* Time: {lstar_time:.2f}s, Frequency: {lstar_requests()}")
# visualization and print DFA
print(dfa)
dfa.visualize("dfa_lstar")

