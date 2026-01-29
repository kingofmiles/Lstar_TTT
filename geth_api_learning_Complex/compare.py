# compare.py
import time
import matplotlib.pyplot as plt

# -------------------------------
# 从你现有的代码导入
# -------------------------------
from my_lstar.learner import LStar
from my_ttt.learner import TTTLearner
from oracle import membership_oracle, reset_counter, API_CALL_COUNT
from equivalence import equivalence_oracle
from api_alphabet import ALPHABET

# -------------------------------
# 运行 L* 并记录数据
# -------------------------------
reset_counter()
start = time.time()
lstar_learner = LStar(ALPHABET, membership_oracle, equivalence_oracle)
lstar_dfa = lstar_learner.learn()
end = time.time()
lstar_time = end - start
lstar_requests = API_CALL_COUNT()

print(f"L* 用时: {lstar_time:.2f}s, 请求次数: {lstar_requests}")

# -------------------------------
# 运行 TTT 并记录数据
# -------------------------------
reset_counter()
start = time.time()
ttt_learner = TTTLearner(ALPHABET, membership_oracle, equivalence_oracle)
ttt_dfa = ttt_learner.learn()
end = time.time()
ttt_time = end - start
ttt_requests = API_CALL_COUNT()

print(f"TTT 用时: {ttt_time:.2f}s, 请求次数: {ttt_requests}")

# -------------------------------
# 生成 PDF 对比图
# -------------------------------
labels = ["L*", "TTT"]
times = [lstar_time, ttt_time]
requests = [lstar_requests, ttt_requests]

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# 左图：运行时间
axes[0].bar(labels, times, color=["skyblue", "lightgreen"])
axes[0].set_title("Execution Time (S)")
axes[0].set_ylabel("Second")

# 右图：membership 请求次数
axes[1].bar(labels, requests, color=["skyblue", "lightgreen"])
axes[1].set_title("Membership Request Account")
axes[1].set_ylabel("Times")

plt.tight_layout()
plt.savefig("comparison.pdf")
plt.show()

# -------------------------------
# 可选：同时可视化 DFA
# -------------------------------
lstar_dfa.visualize("dfa_lstar")
ttt_dfa.visualize("dfa_ttt")
