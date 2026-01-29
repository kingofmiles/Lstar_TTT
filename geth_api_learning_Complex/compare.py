# compare.py
import time
import matplotlib.pyplot as plt
from my_lstar.learner import LStar
from my_ttt.learner import TTTLearner
from oracle import membership_oracle, reset_counter, API_CALL_COUNT
from equivalence import equivalence_oracle
from api_alphabet import ALPHABET

#visualization--add number
def add_bar_labels(ax, bars, fmt="{:.2f}", y_pad_ratio=-0.07):
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
            fontsize=10
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

print(f"L* Time: {lstar_time:.2f}s, frequency: {lstar_requests}")

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

print(f"TTT time: {ttt_time:.2f}s, frequency: {ttt_requests}")

# -------------------------------
# Compare
# -------------------------------
labels = ["L*", "TTT"]
times = [lstar_time, ttt_time]
requests = [lstar_requests, ttt_requests]

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Left: Execution time
axes[0].bar(labels, times, color=["skyblue", "lightgreen"])
axes[0].set_title("Execution Time (S)")
axes[0].set_ylabel("Second")
add_bar_labels(axes[0], bars_time,fmt="{:.2f}")


# Right：Frequency
axes[1].bar(labels, requests, color=["skyblue", "lightgreen"])
axes[1].set_title("Membership Request Account")
axes[1].set_ylabel("Times")
add_bar_labels(axes[1], bars_req, fmt="{:d}")


plt.tight_layout()
plt.savefig("comparison.pdf")
plt.show()
lstar_dfa.visualize("dfa_lstar")
ttt_dfa.visualize("dfa_ttt")
