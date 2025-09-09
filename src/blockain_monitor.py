import numpy as np
import matplotlib.pyplot as plt
from src import blockchain_api as ba
from config import MIN_DELAY, UPDATE_DELAY, INIT_DELAY
import asyncio
import src.analytics.engine as analytics

class BlockchainMonitor:
    def __init__(self, window_size):
        self.window_size = window_size
        self.blockchain = ba.Blockchain()
        self.blocks = []
        self.isUpdated = False
        self.analytics = analytics.AnalyticsEngine()
    
    # Initializes the window, filling it with blocks 
    async def init_window(self):
        current_block_hash = await self.blockchain.get_hash_latest_block()
        await asyncio.sleep(INIT_DELAY)

        for i in range(0, self.window_size):
            current_block_data = await self.blockchain.get_block(current_block_hash)

            metrics = await self.analytics.analyze_block(current_block_data)
            self.analytics.analysis_print(metrics)

            self.blocks.append(current_block_data)
            current_block_hash = current_block_data["previousblockhash"]
            await asyncio.sleep(INIT_DELAY)

        print("Initialization has beed successfully finished!")

    # Rebuilds the window, filling it with new blocks, 
    # and removes extra blocks that are not necessary.
    # Also returns a boolean value
    # that points if block were rebuilded (updated) or not
    async def rebuild_chain(self) -> bool:
        new_blocks = []
        latest_block = await self.blockchain.get_latest_block()
        if len(self.blocks) < 100:
            await asyncio.sleep(MIN_DELAY)
        else:
            await asyncio.sleep(INIT_DELAY)

        current_latest_height = latest_block["height"]

        if self.blocks[0]["height"] < current_latest_height:
            amount_of_new = current_latest_height - self.blocks[0]["height"]
            hash = latest_block["id"]
            for i in range(amount_of_new):
                new_block = await self.blockchain.get_block(hash)
                if new_block is None:
                    break

                new_blocks.append(new_block)
                hash = new_block["previousblockhash"]
                await asyncio.sleep(MIN_DELAY)
            
            new_blocks.reverse()
            for block in new_blocks:
                self.blocks.insert(0, block)
                metrics = await self.analytics.analyze_block(block)
                await asyncio.sleep(MIN_DELAY)
                self.analytics.analysis_with_iqr_print(metrics, 0.5)

            # if there are extra blocks (the window is not of the proper length)
            # then remove the extra blocks
            if len(self.blocks) > self.window_size:
                self.blocks = self.blocks[:self.window_size]
            
            print("New blocks were added")
            return True
        
        return False

    # Updates window if there are new blocks that are not included in the window,
    # and manages inconsistencies (for example if there are wrong blocks in the window
    # that don't match the actual blocks in blockchain, 
    # which might happen whene a reorganisation happens)
    async def update_window(self):
        block_at_local_latest_height = await self.blockchain.get_block_by_height(self.blocks[0]["height"])
        if self.isUpdated or self.blocks[0]["id"] != block_at_local_latest_height["id"]:
            await self.manage_inconsistencies()
            self.isUpdated = False
        else:
            self.isUpdated = await self.rebuild_chain()
        
        await asyncio.sleep(UPDATE_DELAY)

    # manages inconsistencies (for example if there are wrong blocks in the window
    # that don't match the actual blocks in blockchain, 
    # which might happen when a reorganisation happens)
    async def manage_inconsistencies(self) -> None:
        common_ancestor = await self.get_common_ancestor()
        if common_ancestor is None:
            print("Common ancestor not found in local list! Need full reset.")
            self.blocks = []
            await self.rebuild_chain()
            return

        if common_ancestor["id"] == self.blocks[0]["id"]:
            print("Inconsistencies has been not found")
            return

        ancestor_index = next((i for i, block in enumerate(self.blocks) 
                              if common_ancestor["id"] == block["id"]), None)
        
        if ancestor_index is not None:
            print(f"Trimming list to index {ancestor_index}")
            self.blocks = self.blocks[ancestor_index:]
            await self.rebuild_chain()
            print("Inconsistencies resolved successfully!")
        else:
            print("Common ancestor not found in local list! Need full reset.")
            self.blocks = [common_ancestor]
            await self.rebuild_chain()
                    
    # This function searches for a common ancestor, and returns it if it has been found.
    # If not, then it returns None  
    async def get_common_ancestor(self, max_window = None):
        if max_window is not None and max_window > len(self.blocks):
            print("ERROR max_window is out of range")
            return None
        
        block_ids = {block["id"] for block in self.blocks}
        actual_block = await self.blockchain.get_latest_block()
        await asyncio.sleep(MIN_DELAY)

        # If the latest local block is not at the height of the actual latest block
        # then we search for a common ancestor from the height of the least of the latest blocks,
        # which accelerates the proccess of the searching 
        if self.blocks[0]["height"] < actual_block["height"]:
            height = self.blocks[0]["height"]
            actual_block_at_height = await self.blockchain.get_block_by_height(height)
            await asyncio.sleep(MIN_DELAY) 
            actual_block = actual_block_at_height
            
        i = 1
        while actual_block:
            if actual_block["id"] in block_ids:
                return actual_block
            
            actual_block = await self.blockchain.get_block(actual_block["previousblockhash"])
            i += 1
            if max_window is not None and i > max_window:
                return None
            
            await asyncio.sleep(MIN_DELAY)
        
        return None
                    

