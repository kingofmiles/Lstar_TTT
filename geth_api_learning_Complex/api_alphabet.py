# api_alphabet.py
# Single-character abstract alphabet for compatibility with current L* implementation

ADDRESS = "0x0000000000000000000000000000000000000000"
BLOCK_TAG = "latest"

# Symbol -> semantic class mapping (write this into your report/poster)
# A = ACC  (account query)
# T = TXQ  (tx/nonce query)
# B = BLK  (bytecode / code query)
# C = CALL (eth_call)
# M = META (fee/log/meta)

API_MAP = {
    "A": {  # ACC
        "method": "eth_getBalance",
        "params": [ADDRESS, BLOCK_TAG]
    },
    "T": {  # TXQ
        "method": "eth_getTransactionCount",
        "params": [ADDRESS, BLOCK_TAG]
    },
    "B": {  # BLK (use eth_getCode as "bytecode snapshot")
        "method": "eth_getCode",
        "params": [ADDRESS, BLOCK_TAG]
    },
    "C": {  # CALL
        "method": "eth_call",
        "params": [{
            "to": ADDRESS,
            "data": "0x"
        }, BLOCK_TAG]
    },
    "M": {  # META
        "method": "eth_feeHistory",
        "params": ["0x1", "latest", []]
    }
}

ALPHABET = ["A", "T", "B", "C", "M"]
