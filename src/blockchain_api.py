from config import MIN_DELAY, MAX_ATTEMPTS_FOR_REQUEST

import config
import asyncio
import aiohttp

class Blockchain:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        
        return cls._instance

    async def make_response(self, endpoint = None) -> str | dict | None:
        attempt = 1
        url = config.BASE_URL + endpoint
        async with aiohttp.ClientSession() as session:
            while attempt <= MAX_ATTEMPTS_FOR_REQUEST:
                try:
                    async with session.get(url, timeout=10) as response:
                        response.raise_for_status()
                        response_content = None
                        if config.ENDPOINT_HASH_AT_HEIGHT in url or config.ENDPOINT_LATEST_HASH in url:
                            response_content = (await response.text()).strip()
                        elif config.ENDPOINT_LATEST_HEIGHT in url:
                            response_content = int((await response.text()).strip())
                        elif config.ENDPOINT_BLOCK in url:
                            response_content = await response.json()
                        elif "block/" in url and "/txs" in url:
                            response_content = await response.json()
                        elif "block/" in url and "txid/" in url:
                            response_content = await response.json()
                        
                        await asyncio.sleep(MIN_DELAY)
                        return response_content
                
                except aiohttp.ClientResponseError as e:
                    status = e.status
                    if status == 404:
                        print(f"404 - Not found. Attempt {attempt}")
                    elif status == 504:
                        print(f"504 - Gateway timeout. Attempt {attempt}")
                    else:
                        print(f"HTTP Error: {status}")  # 🚨 Вот он!
                        if status not in [404, 504]:
                            return None

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    print(f"Network error: {e}, attempt No: {attempt}")

                await asyncio.sleep(MIN_DELAY)
                attempt += 1

        return None
    
    # this function returns the height of the latest block in blockchain
    async def get_height_latest_block(self) -> str:    
        height_endpoint = config.ENDPOINT_LATEST_HEIGHT
        height = await self.make_response(height_endpoint)

        if height is None:
            print("ERROR: Did not manage receive the height of the latest block")
            return None
        
        return height

    # Returns the height of a block
    async def get_block_height(self, block_hash):
        block_endpoint = config.ENDPOINT_BLOCK + block_hash
        height = await self.get_block(block_endpoint)["height"]
        return height
    
    # Returns the hash of the latest block in blockchain
    async def get_hash_latest_block(self):
        hash_endpoint = config.ENDPOINT_LATEST_HASH

        block_hash = await self.make_response(hash_endpoint)
        if block_hash is None:
            print("ERROR, did not manage to receive the hash of the latest block")
            return None
        
        return block_hash

    # Return a block at the given height
    async def get_block_by_height(self, height):
        hash_url = config.ENDPOINT_HASH_AT_HEIGHT + str(height)
        block_hash = await self.make_response(hash_url)
        
        if block_hash is None:
            print(f"ERROR: Didn't manage to receive the block at the height: {height}")
            return None
    
        return await self.get_block(block_hash)
    
    # Returns a block with the given hash
    async def get_block(self, block_hash):
        block_endpoint = config.ENDPOINT_BLOCK + block_hash

        block = await self.make_response(block_endpoint)
        if block is None:
            print("ERROR: Did not manage to receieve the block")
            return None
        
        return block

    async def get_latest_block(self):
        return await self.get_block(await self.get_hash_latest_block())
    

    async def get_block_transactions(self, block_hash, start_index):
        txs_endpoint = config.get_txs_endpoint_in_block(block_hash, start_index)
        txs = await self.make_response(txs_endpoint)

        return txs if txs else []
    
    async def get_all_block_transactions(self, block_hash, tx_count = 0):
        start_index = 0
        all_txs = []

        while True:
            if len(all_txs) >= tx_count:
                print("receiving txs done")
                break

            txs_chunk = await self.get_block_transactions(block_hash, start_index)
            if not txs_chunk:
                print("txs none")
                break

            start_index += len(txs_chunk)
            all_txs.extend(txs_chunk)
            await asyncio.sleep(MIN_DELAY)
        
        return all_txs

    async def get_block_coinbase(self, block_hash):
        endpoint = config.get_txs_endpoint_in_block(block_hash, 0)
        txs = await self.make_response(endpoint)
        coinbase = txs[0]
        
        if coinbase is None:
            print("ERROR: didnt manage to receive the coinbase")
            return None
        
        return coinbase