# oracle_medium.py
import requests
from api_alphabet import API_MAP

RPC_URL = "http://127.0.0.1:8545"


class Oracle:
    def __init__(self):
        self.API_CALL_COUNT = 0          # count MQ cache-misses
        self.RPC_CALL_COUNT = 0          # count actual JSON-RPC calls
        self.cache = {}                  # sequence(tuple) -> bool

    def reset_counter(self):
        self.API_CALL_COUNT = 0
        self.RPC_CALL_COUNT = 0
        self.cache.clear()

    def _call_rpc(self, sym):
        if sym not in API_MAP:
            raise ValueError(f"Unknown symbol: {sym}")

        payload = {
            "jsonrpc": "2.0",
            "method": API_MAP[sym]["method"],
            "params": API_MAP[sym]["params"],
            "id": 1
        }

        try:
            self.RPC_CALL_COUNT += 1
            r = requests.post(RPC_URL, json=payload, timeout=5)
            resp = r.json()
        except Exception:
            return False

        return "error" not in resp

    def membership_oracle(self, sequence):
        """
        Medium language:
        - Reject immediately on any RPC error
        - Reject if 'M' occurs (explicit error symbol)
        - Accept iff the sequence contains the ordered subsequence A -> T -> B
          (not necessarily contiguous; other calls may appear between them)
        """
        if isinstance(sequence, str):
            sequence = list(sequence)

        key = tuple(sequence)
        if key in self.cache:
            return self.cache[key]

        self.API_CALL_COUNT += 1

        progress = 0  # 0: none, 1: saw A, 2: saw A then T, 3: saw A then T then B

        for sym in sequence:
            if sym == "M":
                self.cache[key] = False
                return False

            # execute real RPC call
            ok = self._call_rpc(sym)
            if not ok:
                self.cache[key] = False
                return False

            # update subsequence progress
            if progress == 0 and sym == "A":
                progress = 1
            elif progress == 1 and sym == "T":
                progress = 2
            elif progress == 2 and sym == "B":
                progress = 3
            # otherwise: ignore symbol for progress

        self.cache[key] = (progress == 3)
        return self.cache[key]

    def get_count(self):
        return self.API_CALL_COUNT

    def get_rpc_count(self):
        return self.RPC_CALL_COUNT


oracle = Oracle()
membership_oracle = oracle.membership_oracle
reset_counter = oracle.reset_counter
API_CALL_COUNT = oracle.get_count
RPC_CALL_COUNT = oracle.get_rpc_count
