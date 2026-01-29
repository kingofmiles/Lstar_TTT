# equivalence.py
from api_alphabet import ALPHABET
from oracle import membership_oracle
import random

random.seed(0)

TEMPLATES = [
    "ATB", "AATB", "ACATB",
    "A", "AT", "AB", "TAB", "ACB", "ATBC", "M",
    "BAT", "TBA", "BTA", "TATB", "ATBM", "ATBB",
    "AC", "CA", "CB", "TC", "BC"
]

def equivalence_oracle(hypothesis):
    for seq in TEMPLATES:
        if hypothesis.accepts(seq) != membership_oracle(seq):
            return seq
    for _ in range(400):
        length = random.randint(1, 10)
        seq = "".join(random.choice(ALPHABET) for _ in range(length))
        if hypothesis.accepts(seq) != membership_oracle(seq):
            return seq

    return None
