# oracle_simple.py
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
        """Execute the JSON-RPC call corresponding to symbol sym. Return True if success else False."""
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
        Simple language:
        - Reject immediately on any RPC error
        - Accept iff sequence is non-empty and all calls succeed
        """
        if isinstance(sequence, str):
            sequence = list(sequence)

        key = tuple(sequence)
        if key in self.cache:
            return self.cache[key]

        self.API_CALL_COUNT += 1

        if len(sequence) == 0:
            self.cache[key] = False
            return False

        for sym in sequence:
            ok = self._call_rpc(sym)
            if not ok:
                self.cache[key] = False
                return False

        self.cache[key] = True
        return True

    def get_count(self):
        return self.API_CALL_COUNT

    def get_rpc_count(self):
        return self.RPC_CALL_COUNT


oracle = Oracle()
membership_oracle = oracle.membership_oracle
reset_counter = oracle.reset_counter
API_CALL_COUNT = oracle.get_count
RPC_CALL_COUNT = oracle.get_rpc_count
