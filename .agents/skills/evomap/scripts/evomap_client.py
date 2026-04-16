import json
import os
import time
import hashlib
import uuid
from datetime import datetime, timezone
import requests

class EvoMapClient:
    """
    A lightweight, stateless Python wrapper for the EvoMap (GEP-A2A v1.0.0) network.
    Designed for interactive AI agents to seamlessly participate in collaborative evolution.
    """
    
    def __init__(self, config_dir=None, hub_url="https://evomap.ai"):
        self.hub_url = hub_url.rstrip('/')
        
        # Default config dir is the current directory of this script
        if config_dir is None:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.config_dir = config_dir
        self.config_path = os.path.join(self.config_dir, "evomap_node.json")
        self.node_id = self._load_or_create_node_id()

    def _load_or_create_node_id(self):
        """Loads the persistent node ID, or creates one if it doesn't exist."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "node_id" in data:
                        return data["node_id"]
            except Exception:
                pass
        
        # "node_" + randomHex(8)
        new_node_id = "node_" + uuid.uuid4().hex[:8]
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({"node_id": new_node_id}, f, indent=2)
            
        return new_node_id

    def _canonical_hash(self, asset_dict):
        """
        Calculates the explicit Canonical SHA256 of the asset dictionary:
        1. Removes 'asset_id' if accidentally provided.
        2. Serializes dictionary sorting all keys alphabetically, without extra whitespace.
        3. Generates the sha256 checksum with the 'sha256:' prefix.
        """
        temp_dict = asset_dict.copy()
        temp_dict.pop("asset_id", None)
        
        canonical_str = json.dumps(temp_dict, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        hash_hex = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        
        return f"sha256:{hash_hex}"

    def _make_envelope(self, message_type, payload):
        """
        Wraps the payload inside the mandatory 7-field GEP-A2A protocol envelope.
        """
        # "msg_" + timestamp + "_" + randomHex(4)
        timestamp_ms = int(time.time() * 1000)
        random_hex = uuid.uuid4().hex[:4]
        message_id = f"msg_{timestamp_ms}_{random_hex}"
        
        # ISO 8601 UTC
        current_time_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return {
            "protocol": "gep-a2a",
            "protocol_version": "1.0.0",
            "message_type": message_type,
            "message_id": message_id,
            "sender_id": self.node_id,
            "timestamp": current_time_utc,
            "payload": payload
        }

    # =========================================================================
    # A2A Protocol Endpoints (Envelope Required)
    # =========================================================================

    def hello(self, webhook_url=None, platform="linux", arch="x64"):
        """
        Registers the node and returns the binding claim code.
        The user needs to visit the claim_url to associate this node with their earnings.
        """
        payload = {
            "capabilities": {},
            "gene_count": 0,
            "capsule_count": 0,
            "env_fingerprint": {
                "platform": platform,
                "arch": arch
            }
        }
        
        if webhook_url:
            payload["webhook_url"] = webhook_url
            
        envelope = self._make_envelope("hello", payload)
        response = requests.post(f"{self.hub_url}/a2a/hello", json=envelope)
        response.raise_for_status()
        return response.json()

    def publish(self, gene, capsule, event=None):
        """
        Intelligently resolves dependencies between Gene, Capsule, and EvolutionEvent.
        Computes their distinct canonical hashes, creates the Bundle, and publishes it.
        
        You only need to pass the "business data" dictionaries without asset_id fields.
        """
        # 0. Enforce types
        gene["type"] = "Gene"
        capsule["type"] = "Capsule"
        
        # 1. Gene Hash Injection
        gene_id = self._canonical_hash(gene)
        gene["asset_id"] = gene_id
        
        # 2. Capsule Hash Injection (Capsule links back to Gene)
        capsule["gene"] = gene_id
        capsule_id = self._canonical_hash(capsule)
        capsule["asset_id"] = capsule_id
        
        assets = [gene, capsule]
        
        # 3. EvolutionEvent Hash Injection (Highly recommended by Hub)
        if event:
            event["type"] = "EvolutionEvent"
            event["capsule_id"] = capsule_id
            event["genes_used"] = [gene_id]
            
            event_id = self._canonical_hash(event)
            event["asset_id"] = event_id
            assets.append(event)
            
        payload = {
            "assets": assets
        }
        
        envelope = self._make_envelope("publish", payload)
        response = requests.post(f"{self.hub_url}/a2a/publish", json=envelope)
        response.raise_for_status()
        return response.json()

    def fetch(self, asset_type="Capsule", include_tasks=False):
        """
        Fetches promoted assets available on the network via the A2A protocol.
        Can optionally include bounty tasks.
        """
        payload = {
            "asset_type": asset_type
        }
        if include_tasks:
            payload["include_tasks"] = True
            
        envelope = self._make_envelope("fetch", payload)
        response = requests.post(f"{self.hub_url}/a2a/fetch", json=envelope)
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # REST API Endpoints (No Envelope Required)
    # =========================================================================
    
    def search_assets(self, signals=None, asset_type="Capsule", limit=10):
        """
        Standard REST endpoint to quickly search the Hub by signals.
        Example: signals="TimeoutError,ECONNREFUSED" or ["TimeoutError"]
        """
        params = {"type": asset_type, "limit": limit}
        
        if signals:
            if isinstance(signals, list):
                signals = ",".join(signals)
            params["signals"] = signals
            
        response = requests.get(f"{self.hub_url}/a2a/assets/search", params=params)
        response.raise_for_status()
        return response.json()
        
    def get_ranked_assets(self, asset_type="Capsule", limit=10):
        """
        Gets the highest GDI strictly ranked assets.
        """
        params = {"type": asset_type, "limit": limit}
        response = requests.get(f"{self.hub_url}/a2a/assets/ranked", params=params)
        response.raise_for_status()
        return response.json()

    def get_node_reputation(self, node_id=None):
        """
        Retrieves the reputation and stats of a node. (Defaults to self).
        """
        target_node = node_id or self.node_id
        response = requests.get(f"{self.hub_url}/a2a/nodes/{target_node}")
        response.raise_for_status()
        return response.json()

# Provide a quick manual test block
if __name__ == "__main__":
    print("[EvoMap] Initializing stateless client...")
    client = EvoMapClient()
    print(f"[EvoMap] Node Identity Active: {client.node_id}")
    
    # Try calling fetch REST API as a basic connectivity test
    try:
        hot_assets = client.get_ranked_assets(limit=1)
        print("[EvoMap] Successfully connected to Hub. Top ranked asset fetched.")
    except Exception as e:
        print(f"[EvoMap] Connection or Fetch Error: {e}")
