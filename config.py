BASE_URL = "https://blockstream.info/api/"

ENDPOINT_LATEST_HEIGHT = "blocks/tip/height"
ENDPOINT_LATEST_HASH = "blocks/tip/hash"
ENDPOINT_HASH_AT_HEIGHT = "block-height/"
ENDPOINT_BLOCK = "block/"

MIN_DELAY = 2 # seconds
UPDATE_DELAY = 20
INIT_DELAY = 0.2
SENSITIVITY = 1 # sensitivity of detecting anomalies

MAX_ATTEMPTS_FOR_REQUEST = 25

def get_txs_endpoint_in_block(block_hash, start_index):
    return f"block/{block_hash}/txs/{start_index}"

def get_coinbase_endpoint_in_block(block_hash):
    return f"block/{block_hash}/txid/0"