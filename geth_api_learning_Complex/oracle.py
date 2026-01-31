# oracle.py
import requests
from api_alphabet import API_MAP

RPC_URL = "http://127.0.0.1:8545"

class Oracle:
    def __init__(self):
        self.API_CALL_COUNT = 0      # Membership Query count
        self.RPC_CALL_COUNT = 0      # Actual JSON-RPC calls
        self.cache = {}              # sequence(tuple) -> bool

    def reset_counter(self):
        self.API_CALL_COUNT = 0
        self.RPC_CALL_COUNT = 0
        self.cache.clear()

    def membership_oracle(self, sequence):
        if isinstance(sequence, str):
            sequence = list(sequence)

        key = tuple(sequence)
        if key in self.cache:
            return self.cache[key]

        # ---- MQ count ----
        self.API_CALL_COUNT += 1

        phase = 0  # 0 none, 1 have A, 2 have A+T, 3 have A+T+B (accept)

        for sym in sequence:
            # ---- language semantics ----
            if sym == "M":
                self.cache[key] = False
                return False

            if sym == "A":
                if phase >= 2:
                    self.cache[key] = False
                    return False
                phase = max(phase, 1)

            elif sym == "T":
                if phase < 1:
                    self.cache[key] = False
                    return False
                phase = max(phase, 2)

            elif sym == "B":
                if phase < 2:
                    self.cache[key] = False
                    return False
                phase = 3

            elif sym == "C":
                if not (1 <= phase <= 2):
                    self.cache[key] = False
                    return False

            else:
                raise ValueError(f"Unknown symbol: {sym}")

            # ---- RPC call  ----
            payload = {
                "jsonrpc": "2.0",
                "method": API_MAP[sym]["method"],
                "params": API_MAP[sym]["params"],
                "id": 1
            }

            try:
                self.RPC_CALL_COUNT += 1
                r = requests.post(RPC_URL, json=payload, timeout=3)
                resp = r.json()
            except Exception:
                self.cache[key] = False
                return False

            if "error" in resp:
                self.cache[key] = False
                return False

        result = (phase == 3)
        self.cache[key] = result
        return result

    # -------- getters --------
    def get_mq_count(self):
        return self.API_CALL_COUNT

    def get_rpc_count(self):
        return self.RPC_CALL_COUNT


# ---- singleton exports  ----
oracle = Oracle()
membership_oracle = oracle.membership_oracle
reset_counter = oracle.reset_counter
API_CALL_COUNT = oracle.get_mq_count
RPC_CALL_COUNT = oracle.get_rpc_count
