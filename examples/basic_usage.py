from src.analytics import engine as analytics
from src import blockain_monitor as bm

import time
import numpy as np
import matplotlib.pyplot as plt
import asyncio


async def main():
    window_size = 100

    monitor = bm.BlockchainMonitor(window_size=window_size)
    await monitor.init_window()

    while True:
        print(monitor.blocks[0]["height"])
        await monitor.update_window()
        print(f"amount of local blocks: {len(monitor.blocks)}")

if __name__ == "__main__":
    asyncio.run(main())