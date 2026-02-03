# compare.py
import sys
import time
import matplotlib.pyplot as plt


# CLI: choose mode

if len(sys.argv) > 1:
    Experiment_method = sys.argv[1]
else:
    Experiment_method = "complex"  # default


# import oracle by mode

if Experiment_method == "complex":
    from oracle import membership_oracle, reset_counter, API_CALL_COUNT, RPC_CALL_COUNT
elif Experiment_method == "simple":
    from oracle_simple import membership_oracle, reset_counter, API_CALL_COUNT, RPC_CALL_COUNT
elif Experiment_method == "medium":
    from oracle_medium import membership_oracle, reset_counter, API_CALL_COUNT, RPC_CALL_COUNT
else:
    raise ValueError(f"Unknown method: {Experiment_method}. Choose simple, medium, or complex.")


# learners + alphabet

from my_lstar.learner import LStar
from my_ttt.learner import TTTLearner
from api_alphabet import ALPHABET


# IMPORTANT: monkey-patch equivalence.py without editing it

import equivalence as eq
eq.membership_oracle = membership_oracle  # redirect to current mode oracle


# visualization helper

def add_bar_labels(ax, bars, fmt="{:.2f}", y_pad_ratio=-0.15):
    y_min, y_max = ax.get_ylim()
    y_range = y_max - y_min if y_max != y_min else 1.0
    pad = y_range * y_pad_ratio

    for bar in bars:
        h = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2.0
        ax.text(x, h + pad, fmt.format(h), ha="center", va="bottom", fontsize=12)


# run L*

reset_counter()
start = time.time()
lstar_learner = LStar(ALPHABET, membership_oracle, eq.equivalence_oracle)  # function, not module
lstar_dfa = lstar_learner.learn()
lstar_time = time.time() - start
lstar_requests = API_CALL_COUNT()
lstar_rpc = RPC_CALL_COUNT()
print(f"L* time: {lstar_time:.2f}s, Request: {lstar_requests}, RPC: {lstar_rpc}")


# run TTT

reset_counter()
start = time.time()
ttt_learner = TTTLearner(ALPHABET, membership_oracle, eq.equivalence_oracle)  # function
ttt_dfa = ttt_learner.learn()
ttt_time = time.time() - start
ttt_requests = API_CALL_COUNT()
ttt_rpc = RPC_CALL_COUNT()
print(f"TTT Time: {ttt_time:.2f}s, Request: {ttt_requests}, RPC: {ttt_rpc}")


# plot comparison (3 columns)

labels = ["L*", "TTT"]
times = [lstar_time, ttt_time]
requests = [lstar_requests, ttt_requests]
rpc_requests = [lstar_rpc, ttt_rpc]

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

bars_time = axes[0].bar(labels, times, color=["skyblue", "red"])
axes[0].set_title("Execution Time (s)")
axes[0].set_ylabel("Seconds")
add_bar_labels(axes[0], bars_time, fmt="{:.2f}")

bars_req = axes[1].bar(labels, requests, color=["skyblue", "red"])
axes[1].set_title("Membership Queries (MQ)")
axes[1].set_ylabel("Count")
add_bar_labels(axes[1], bars_req, fmt="{:d}")

bars_rpc = axes[2].bar(labels, rpc_requests, color=["skyblue", "red"])
axes[2].set_title("JSON-RPC Calls")
axes[2].set_ylabel("Count")
add_bar_labels(axes[2], bars_rpc, fmt="{:d}")

plt.tight_layout()
plt.savefig("comparison.pdf")
plt.show()


# visualize DFAs

lstar_dfa.visualize("dfa_lstar")
ttt_dfa.visualize("dfa_ttt")
