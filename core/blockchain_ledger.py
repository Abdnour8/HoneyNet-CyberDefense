"""
HoneyNet Blockchain Threat Ledger
מערכת בלוקצ'יין לרישום איומים בלתי ניתן לשינוי
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time


class BlockType(Enum):
    """סוגי בלוקים"""
    THREAT_RECORD = "threat_record"
    HONEYPOT_TRIGGER = "honeypot_trigger"
    NETWORK_EVENT = "network_event"
    CONSENSUS_VOTE = "consensus_vote"
    REWARD_DISTRIBUTION = "reward_distribution"


@dataclass
class ThreatRecord:
    """רישום איום"""
    threat_id: str
    threat_type: str
    severity: str
    source_ip: str
    target: str
    timestamp: datetime
    reporter_id: str
    evidence_hash: str
    geographic_location: str
    attack_vector: str
    mitigation_applied: bool
    verified: bool = False
    verification_count: int = 0


@dataclass
class Block:
    """בלוק בבלוקצ'יין"""
    index: int
    timestamp: datetime
    data: Dict
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    block_type: BlockType = BlockType.THREAT_RECORD
    validator_id: str = ""
    signature: str = ""


@dataclass
class Node:
    """נוד ברשת הבלוקצ'יין"""
    node_id: str
    public_key: str
    reputation_score: float
    stake_amount: int
    last_seen: datetime
    validated_blocks: int = 0
    false_validations: int = 0
    is_validator: bool = False


@dataclass
class ConsensusVote:
    """הצבעה בקונצנזוס"""
    block_hash: str
    voter_id: str
    vote: bool  # True = valid, False = invalid
    timestamp: datetime
    stake_weight: int
    signature: str


class ProofOfThreat:
    """הוכחת איום - מנגנון קונצנזוס מותאם"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_validators = 3
        self.consensus_threshold = 0.67  # 67% agreement needed
        self.validation_timeout = 300  # 5 minutes
        
    async def validate_threat_record(self, threat_record: ThreatRecord, validators: List[Node]) -> bool:
        """אימות רישום איום"""
        if len(validators) < self.min_validators:
            return False
        
        # Simulate validation process
        valid_votes = 0
        total_stake = sum(node.stake_amount for node in validators)
        
        for validator in validators:
            # Simulate validator decision based on reputation and evidence
            validation_score = await self._calculate_validation_score(threat_record, validator)
            
            if validation_score > 0.7:
                valid_votes += validator.stake_amount
        
        consensus_ratio = valid_votes / total_stake
        return consensus_ratio >= self.consensus_threshold
    
    async def _calculate_validation_score(self, threat_record: ThreatRecord, validator: Node) -> float:
        """חישוב ציון אימות"""
        base_score = 0.5
        
        # Factor in validator reputation
        reputation_factor = min(validator.reputation_score / 100, 0.3)
        
        # Factor in threat evidence quality
        evidence_factor = 0.2 if threat_record.evidence_hash else 0.0
        
        # Factor in geographic correlation
        geo_factor = 0.1  # Simplified
        
        return min(base_score + reputation_factor + evidence_factor + geo_factor, 1.0)


class BlockchainThreatLedger:
    """מערכת בלוקצ'יין לרישום איומים"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Blockchain data
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.nodes: Dict[str, Node] = {}
        self.pending_votes: Dict[str, List[ConsensusVote]] = {}
        
        # Consensus mechanism
        self.proof_of_threat = ProofOfThreat()
        
        # Configuration
        self.block_time = 60  # 1 minute between blocks
        self.max_transactions_per_block = 100
        self.mining_difficulty = 4
        
        # Rewards and tokens
        self.threat_token_rewards = {
            "low": 10,
            "medium": 25,
            "high": 50,
            "critical": 100
        }
        
        # Initialize genesis block
        self._create_genesis_block()
        
        self.logger.info("⛓️ Blockchain Threat Ledger initialized")
    
    def _create_genesis_block(self):
        """יצירת בלוק הבראשית"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now(),
            data={
                "message": "HoneyNet Genesis Block",
                "version": "1.0.0",
                "network_id": "honeynet_mainnet"
            },
            previous_hash="0",
            block_type=BlockType.NETWORK_EVENT
        )
        
        genesis_block.hash = self._calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        
        self.logger.info("🌟 Genesis block created")
    
    async def register_node(self, node_id: str, public_key: str, stake_amount: int = 1000) -> Node:
        """רישום נוד חדש"""
        node = Node(
            node_id=node_id,
            public_key=public_key,
            reputation_score=50.0,  # Starting reputation
            stake_amount=stake_amount,
            last_seen=datetime.now(),
            is_validator=stake_amount >= 1000  # Minimum stake for validation
        )
        
        self.nodes[node_id] = node
        
        self.logger.info(f"🔗 Node registered: {node_id} (validator: {node.is_validator})")
        return node
    
    async def submit_threat_record(self, threat_record: ThreatRecord) -> str:
        """הגשת רישום איום לבלוקצ'יין"""
        # Create transaction
        transaction = {
            "type": "threat_record",
            "data": {
                "threat_id": threat_record.threat_id,
                "threat_type": threat_record.threat_type,
                "severity": threat_record.severity,
                "source_ip": threat_record.source_ip,
                "target": threat_record.target,
                "timestamp": threat_record.timestamp.isoformat(),
                "reporter_id": threat_record.reporter_id,
                "evidence_hash": threat_record.evidence_hash,
                "geographic_location": threat_record.geographic_location,
                "attack_vector": threat_record.attack_vector,
                "mitigation_applied": threat_record.mitigation_applied
            },
            "timestamp": datetime.now().isoformat(),
            "hash": self._calculate_transaction_hash(threat_record)
        }
        
        # Add to pending transactions
        self.pending_transactions.append(transaction)
        
        # Start validation process
        await self._initiate_consensus_validation(transaction)
        
        self.logger.info(f"📝 Threat record submitted: {threat_record.threat_id}")
        return transaction["hash"]
    
    async def submit_honeypot_trigger(self, honeypot_data: Dict) -> str:
        """הגשת הפעלת פיתיון"""
        transaction = {
            "type": "honeypot_trigger",
            "data": honeypot_data,
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.sha256(json.dumps(honeypot_data, sort_keys=True).encode()).hexdigest()
        }
        
        self.pending_transactions.append(transaction)
        
        self.logger.info(f"🍯 Honeypot trigger submitted: {honeypot_data.get('trigger_id', 'unknown')}")
        return transaction["hash"]
    
    async def mine_block(self, validator_id: str) -> Optional[Block]:
        """כריית בלוק חדש"""
        if not self.pending_transactions:
            return None
        
        if validator_id not in self.nodes or not self.nodes[validator_id].is_validator:
            self.logger.warning(f"Invalid validator: {validator_id}")
            return None
        
        # Get transactions for this block
        transactions = self.pending_transactions[:self.max_transactions_per_block]
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(),
            data={
                "transactions": transactions,
                "transaction_count": len(transactions)
            },
            previous_hash=self.chain[-1].hash if self.chain else "0",
            validator_id=validator_id
        )
        
        # Mine the block (Proof of Work)
        new_block = await self._mine_block_pow(new_block)
        
        # Validate block
        if await self._validate_block(new_block):
            # Add block to chain
            self.chain.append(new_block)
            
            # Remove processed transactions
            self.pending_transactions = self.pending_transactions[len(transactions):]
            
            # Reward validator
            await self._reward_validator(validator_id, len(transactions))
            
            # Update node statistics
            self.nodes[validator_id].validated_blocks += 1
            self.nodes[validator_id].last_seen = datetime.now()
            
            self.logger.info(f"⛏️ Block mined: #{new_block.index} by {validator_id}")
            return new_block
        
        return None
    
    async def verify_threat_record(self, threat_id: str, verifier_id: str) -> bool:
        """אימות רישום איום"""
        # Find threat record in blockchain
        threat_record = await self._find_threat_record(threat_id)
        if not threat_record:
            return False
        
        # Check if verifier is eligible
        if verifier_id not in self.nodes:
            return False
        
        verifier = self.nodes[verifier_id]
        if verifier.reputation_score < 70:  # Minimum reputation for verification
            return False
        
        # Record verification
        threat_record["verification_count"] = threat_record.get("verification_count", 0) + 1
        threat_record["verified"] = threat_record["verification_count"] >= 3
        
        # Reward verifier
        if threat_record["verified"]:
            await self._reward_verifier(verifier_id, threat_record["data"]["severity"])
        
        self.logger.info(f"✅ Threat record verified: {threat_id} by {verifier_id}")
        return True
    
    async def get_threat_history(self, limit: int = 100) -> List[Dict]:
        """קבלת היסטוריית איומים"""
        threat_records = []
        
        for block in reversed(self.chain[-limit:]):
            if "transactions" in block.data:
                for transaction in block.data["transactions"]:
                    if transaction["type"] == "threat_record":
                        threat_records.append({
                            "block_index": block.index,
                            "block_hash": block.hash,
                            "timestamp": transaction["timestamp"],
                            "threat_data": transaction["data"],
                            "verified": transaction.get("verified", False)
                        })
        
        return threat_records
    
    async def get_blockchain_stats(self) -> Dict:
        """קבלת סטטיסטיקות בלוקצ'יין"""
        total_transactions = sum(
            len(block.data.get("transactions", []))
            for block in self.chain
        )
        
        threat_records = sum(
            1 for block in self.chain
            if "transactions" in block.data
            for transaction in block.data["transactions"]
            if transaction["type"] == "threat_record"
        )
        
        honeypot_triggers = sum(
            1 for block in self.chain
            if "transactions" in block.data
            for transaction in block.data["transactions"]
            if transaction["type"] == "honeypot_trigger"
        )
        
        return {
            "total_blocks": len(self.chain),
            "total_transactions": total_transactions,
            "threat_records": threat_records,
            "honeypot_triggers": honeypot_triggers,
            "pending_transactions": len(self.pending_transactions),
            "active_nodes": len(self.nodes),
            "validator_nodes": len([n for n in self.nodes.values() if n.is_validator]),
            "chain_size_mb": self._calculate_chain_size(),
            "last_block_time": self.chain[-1].timestamp.isoformat() if self.chain else None
        }
    
    async def validate_chain_integrity(self) -> bool:
        """אימות שלמות השרשרת"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check hash integrity
            if current_block.hash != self._calculate_hash(current_block):
                self.logger.error(f"Invalid hash at block {i}")
                return False
            
            # Check previous hash link
            if current_block.previous_hash != previous_block.hash:
                self.logger.error(f"Invalid previous hash at block {i}")
                return False
        
        return True
    
    # Private helper methods
    
    def _calculate_hash(self, block: Block) -> str:
        """חישוב hash של בלוק"""
        block_string = json.dumps({
            "index": block.index,
            "timestamp": block.timestamp.isoformat(),
            "data": block.data,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _calculate_transaction_hash(self, threat_record: ThreatRecord) -> str:
        """חישוב hash של טרנזקציה"""
        transaction_string = json.dumps({
            "threat_id": threat_record.threat_id,
            "threat_type": threat_record.threat_type,
            "severity": threat_record.severity,
            "timestamp": threat_record.timestamp.isoformat(),
            "reporter_id": threat_record.reporter_id
        }, sort_keys=True)
        
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    async def _mine_block_pow(self, block: Block) -> Block:
        """כריית בלוק עם Proof of Work"""
        target = "0" * self.mining_difficulty
        
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = self._calculate_hash(block)
        
        return block
    
    async def _validate_block(self, block: Block) -> bool:
        """אימות בלוק"""
        # Check hash
        if block.hash != self._calculate_hash(block):
            return False
        
        # Check proof of work
        target = "0" * self.mining_difficulty
        if not block.hash.startswith(target):
            return False
        
        # Check previous hash
        if block.index > 0:
            previous_block = self.chain[block.index - 1]
            if block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    async def _initiate_consensus_validation(self, transaction: Dict):
        """התחלת תהליך אימות קונצנזוס"""
        validators = [node for node in self.nodes.values() if node.is_validator]
        
        if len(validators) >= self.proof_of_threat.min_validators:
            # Simulate consensus process
            transaction["consensus_initiated"] = True
            transaction["validation_deadline"] = (datetime.now() + timedelta(seconds=self.proof_of_threat.validation_timeout)).isoformat()
    
    async def _find_threat_record(self, threat_id: str) -> Optional[Dict]:
        """חיפוש רישום איום"""
        for block in self.chain:
            if "transactions" in block.data:
                for transaction in block.data["transactions"]:
                    if (transaction["type"] == "threat_record" and 
                        transaction["data"]["threat_id"] == threat_id):
                        return transaction
        return None
    
    async def _reward_validator(self, validator_id: str, transaction_count: int):
        """תגמול מאמת"""
        base_reward = 50
        transaction_bonus = transaction_count * 5
        total_reward = base_reward + transaction_bonus
        
        # Update validator reputation
        if validator_id in self.nodes:
            self.nodes[validator_id].reputation_score += 1
        
        self.logger.info(f"💰 Validator {validator_id} rewarded: {total_reward} tokens")
    
    async def _reward_verifier(self, verifier_id: str, severity: str):
        """תגמול מאמת איום"""
        reward = self.threat_token_rewards.get(severity, 25)
        
        # Update verifier reputation
        if verifier_id in self.nodes:
            self.nodes[verifier_id].reputation_score += 0.5
        
        self.logger.info(f"🎁 Verifier {verifier_id} rewarded: {reward} tokens for {severity} threat")
    
    def _calculate_chain_size(self) -> float:
        """חישוב גודל השרשרת במגה-בייט"""
        chain_json = json.dumps([
            {
                "index": block.index,
                "timestamp": block.timestamp.isoformat(),
                "data": block.data,
                "hash": block.hash,
                "previous_hash": block.previous_hash
            }
            for block in self.chain
        ])
        
        return len(chain_json.encode()) / (1024 * 1024)  # MB
    
    async def cleanup(self):
        """ניקוי משאבים"""
        self.logger.info("🧹 Cleaning up Blockchain Threat Ledger...")
        
        # Save blockchain state
        await self._save_blockchain_state()
        
        self.logger.info("✅ Blockchain cleanup complete")
    
    async def _save_blockchain_state(self):
        """שמירת מצב הבלוקצ'יין"""
        # Implementation for saving blockchain state to persistent storage
        pass
