from config import MIN_DELAY
from collections import deque
from src import blockchain_api

import config
import asyncio
import numpy as np
import math 

class AnalyticsEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        
        return cls._instance
    
    def __init__(self, max_history = 100):
        if not hasattr(self, "_initialized"):
            self.max_history = max_history
            self.blockchain = blockchain_api.Blockchain()
            self.history = deque(maxlen=self.max_history)
            self._initialized = True
            print("AnalyticsEngine was initialized!")
    
    async def analyze_block(self, block):
        metrics = {
            # main metrics
            "height": block["height"],
            "hash": block["id"],
            "timestamp": block["timestamp"],

            # basic metrics
            "tx_count": block["tx_count"],
            "size_bytes": block["size"],
            "weight": block["weight"],

            # simple analytics
            "is_empty": block["tx_count"] == 1,
            "id_large": block["size"] > 1000000
        }
        total_fees = await self.get_total_fees(block["id"], block["height"])

        metrics["fees"] = {
            "total_fees": total_fees,
            "avarage_fee": total_fees/block["tx_count"],
            "has_high_fees": total_fees > 10000000,
        }

        self.history.append(metrics)

        return metrics

    def analysis_print(self, metrics: dict):
        print("\nMETRICS: ")
        print(f"height: {metrics['height']}")
        print(f"tx_count: {metrics['tx_count']}")
        print(f"timestamp: {metrics['timestamp']}")
        print(f"\nfees_total: {metrics['fees']['total_fees']}")
        print(f"avarage fee: {metrics['fees']['avarage_fee']}")
        print(f"has_high_fees: {metrics['fees']['has_high_fees']}\n\n")

    def analysis_with_iqr_print(self, metrics: dict, sensitivity = config.SENSITIVITY):
        if len(self.history) < 100:
            return
        
        anomalies = self.detect_basic_anomalies(metrics, sensitivity)
        total_fees = []

        self.analysis_print(metrics)
        
        for historical_metrics in self.history:
            if "fees" in historical_metrics:
                if "total_fees" in historical_metrics["fees"]:
                    total_fees.append(historical_metrics["fees"]["total_fees"])
                    
        Q_1 = np.percentile(total_fees, 25)
        Q_3 = np.percentile(total_fees, 75)

        IQR = Q_3 - Q_1
        
        lower_bound = max(0, Q_1 - IQR * sensitivity)
        upper_bound = Q_3 + IQR * sensitivity

        print("IQR_parameteres: ")
        print(f"1. percentile 25%: {Q_1}")
        print(f"2. percentile 75%: {Q_3}")
        print(f"3. IQR = percentile 75% - percentile 25%: {IQR}")
        print(f"4. lower_bound: {lower_bound}")
        print(f"5. upper_bound: {upper_bound}\n")

        if not anomalies:
            print("Anomalies were not detected.")
            return

        print("ANOMALIES WERE DETECTED: ")
        for i, anomaly in enumerate(anomalies):
            print(f"Anomaly {i}: {anomaly}")


    async def get_total_fees(self, block_hash, block_height):
        coinbase = await self.blockchain.get_block_coinbase(block_hash)
        if coinbase is None:
            return 0 
        
        await asyncio.sleep(MIN_DELAY)

        total_outputs = sum([vout["value"] for vout in coinbase["vout"]])
        total_fees = total_outputs - self.calculate_reward(block_height) * 100000000 # In satoshi

        return total_fees
    
    def get_total_fees_in_all_blocks(self):
        total_fees = sum([metrics["fees"]["total_fees"] for metrics in self.history])

        return total_fees
        
    
    # Calculates the reward for a block in BTC 
    def calculate_reward(self, block_height):
        halving_epoch = block_height // 210000
        reward = 50 / (2 ** halving_epoch)

        return reward 

    def detect_basic_anomalies(self, metrics: dict, sensitivity = config.SENSITIVITY):
        anomalies = []
        total_fees = []
        
        if len(self.history) < 100:
            return anomalies
        
        for historical_metrics in self.history:
            if "fees" in historical_metrics:
                if "total_fees" in historical_metrics["fees"]:
                    total_fees.append(historical_metrics["fees"]["total_fees"])

        Q_1 = np.percentile(total_fees, 25)
        Q_3 = np.percentile(total_fees, 75)

        IQR = Q_3 - Q_1

        lower_bound = max(0, Q_1 - IQR * sensitivity)
        upper_bound = Q_3 + IQR * sensitivity

        if metrics.get("is_empty"):
            anomalies.append("empty_block")
        
        if "fees" in metrics and "total_fees" in metrics["fees"]:
            current_fees = metrics["fees"]["total_fees"]
            if current_fees > upper_bound:
                anomalies.append("high_fees")   
            if current_fees < lower_bound:
                anomalies.append("low_fees")
        
        return anomalies
        


