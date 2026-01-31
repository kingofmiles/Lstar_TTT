# compare.py
import sys  
if len(sys.argv) > 1:
    Experiment_method = sys.argv[1] 
else:
    Experiment_method = 'complex' #default is complex

#Experiment_method = simple/medium/complex
if Experiment_method == 'complex':
        from oracle import membership_oracle, reset_counter, API_CALL_COUNT, RPC_CALL_COUNT
elif Experiment_method == 'simple':
        from oracle_simple import membership_oracle, reset_counter, API_CALL_COUNT, RPC_CALL_COUNT
elif Experiment_method == 'medium':
        from oracle_medium import membership_oracle, reset_counter, API_CALL_COUNT, RPC_CALL_COUNT
else:
        raise ValueError(f"Unknown method: {Experiment_method}. Choose simple, medium, or complex.")
import time
import matplotlib.pyplot as plt
from my_lstar.learner import LStar
from my_ttt.learner import TTTLearner
from equivalence import equivalence_oracle
from api_alphabet import ALPHABET

#visualization--add number--fontsize is uesd to change the size
def add_bar_labels(ax, bars, fmt="{:.2f}", y_pad_ratio=-0.15):
    """
    - fmt: Format， "{:.2f}" or "{:d}"
    - y_pad_ratio: gap between number and column
    """
    # y_scope
    y_min, y_max = ax.get_ylim()
    y_range = y_max - y_min if y_max != y_min else 1.0
    pad = y_range * y_pad_ratio

    for bar in bars:
        h = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2.0
        ax.text(
            x, h + pad,
            fmt.format(h),
            ha="center", va="bottom",
            fontsize=20
        )

# -------------------------------
#  L* and recording
# -------------------------------
reset_counter()
start = time.time()
lstar_learner = LStar(ALPHABET, membership_oracle, equivalence_oracle)
lstar_dfa = lstar_learner.learn()
end = time.time()
lstar_time = end - start
lstar_requests = API_CALL_COUNT()
lstar_rpc = RPC_CALL_COUNT()


print(f"L* Time: {lstar_time:.2f}s, frequency: {lstar_requests}, RPC: {lstar_rpc}")

# -------------------------------
# TTT and recording
# -------------------------------
reset_counter()
start = time.time()
ttt_learner = TTTLearner(ALPHABET, membership_oracle, equivalence_oracle)
ttt_dfa = ttt_learner.learn()
end = time.time()
ttt_time = end - start
ttt_requests = API_CALL_COUNT()
ttt_rpc = RPC_CALL_COUNT()

print(f"TTT time: {ttt_time:.2f}s, frequency: {ttt_requests}, RPC: {ttt_rpc}")

# -------------------------------
# Compare
# -------------------------------
labels = ["L*", "TTT"]
times = [lstar_time, ttt_time]
requests = [lstar_requests, ttt_requests]

fig, axes = plt.subplots(1, 3, figsize=(15, 4)) #change the size

# Left: Execution time
bars_time = axes[0].bar(labels, times, color=["skyblue", "red"])
axes[0].set_title("Execution Time (S)")
axes[0].set_ylabel("Second")
add_bar_labels(axes[0], bars_time,fmt="{:.2f}")


# Medium：Frequency
bars_req = axes[1].bar(labels, requests, color=["skyblue", "lightgreen"])
axes[1].set_title("Membership Request Account")
axes[1].set_ylabel("Times")
add_bar_labels(axes[1], bars_req, fmt="{:d}")

# Right: RPC
bars_rpc = axes[2].bar(labels, rpc_requests, color=["skyblue", "yellow"])
axes[2].set_title("JSON-RPC Calls")
axes[2].set_ylabel("Calls")
add_bar_labels(axes[2], bars_rpc, fmt="{:d}")


plt.tight_layout()
plt.savefig("comparison.pdf")
plt.show()
lstar_dfa.visualize("dfa_lstar")
ttt_dfa.visualize("dfa_ttt")
