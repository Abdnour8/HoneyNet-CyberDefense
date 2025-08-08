/**
 * Blockchain Service for HoneyNet Mobile
 * שירות בלוקצ'יין לאפליקציית HoneyNet לנייד
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { HoneyNetService } from './HoneyNetService';

export interface ThreatRecord {
  id: string;
  threatType: string;
  severity: string;
  sourceIp: string;
  targetIp: string;
  timestamp: Date;
  signature: string;
  metadata: Record<string, any>;
}

export interface Block {
  blockNumber: number;
  blockHash: string;
  previousHash: string;
  timestamp: Date;
  threatRecords: ThreatRecord[];
  minerId: string;
  nonce: number;
  merkleRoot: string;
}

export interface BlockchainStats {
  totalBlocks: number;
  activeNodes: number;
  totalThreats: number;
  integrityScore: number;
  lastBlockTime: Date;
  networkHashRate: number;
}

export interface MiningReward {
  blockNumber: number;
  reward: number;
  minerId: string;
  timestamp: Date;
}

class BlockchainServiceClass {
  private localChain: Block[] = [];
  private pendingThreatRecords: ThreatRecord[] = [];
  private isConnected: boolean = false;
  private nodeId: string = '';

  async initialize(): Promise<void> {
    try {
      // Generate or load node ID
      this.nodeId = await this.getOrCreateNodeId();
      
      // Load local blockchain data
      await this.loadLocalChain();
      
      // Connect to blockchain network
      await this.connectToNetwork();
      
      // Start background sync
      this.startBackgroundSync();
      
    } catch (error) {
      console.error('Error initializing blockchain service:', error);
    }
  }

  async submitThreatRecord(threatData: {
    threatType: string;
    severity: string;
    sourceIp: string;
    targetIp: string;
    signature: string;
    metadata: Record<string, any>;
  }): Promise<string> {
    try {
      const threatRecord: ThreatRecord = {
        id: this.generateThreatId(),
        ...threatData,
        timestamp: new Date()
      };

      // Add to pending records
      this.pendingThreatRecords.push(threatRecord);
      
      // Save locally
      await this.savePendingRecords();
      
      // Submit to network if connected
      if (this.isConnected) {
        await this.submitToNetwork(threatRecord);
      }
      
      return threatRecord.id;
    } catch (error) {
      console.error('Error submitting threat record:', error);
      throw error;
    }
  }

  async getBlockchainStats(): Promise<BlockchainStats> {
    try {
      if (this.isConnected) {
        // Get stats from network
        const networkStats = await HoneyNetService.getBlockchainStats();
        return networkStats;
      } else {
        // Return local stats
        return {
          totalBlocks: this.localChain.length,
          activeNodes: 1,
          totalThreats: this.getTotalThreatsInChain(),
          integrityScore: await this.calculateChainIntegrity(),
          lastBlockTime: this.getLastBlockTime(),
          networkHashRate: 0
        };
      }
    } catch (error) {
      console.error('Error getting blockchain stats:', error);
      return {
        totalBlocks: 0,
        activeNodes: 0,
        totalThreats: 0,
        integrityScore: 0,
        lastBlockTime: new Date(),
        networkHashRate: 0
      };
    }
  }

  async getRecentBlocks(limit: number = 10): Promise<Block[]> {
    try {
      if (this.isConnected) {
        return await HoneyNetService.getRecentBlocks(limit);
      } else {
        return this.localChain.slice(-limit).reverse();
      }
    } catch (error) {
      console.error('Error getting recent blocks:', error);
      return [];
    }
  }

  async getBlockByHash(blockHash: string): Promise<Block | null> {
    try {
      // Check local chain first
      const localBlock = this.localChain.find(block => block.blockHash === blockHash);
      if (localBlock) return localBlock;
      
      // Query network if connected
      if (this.isConnected) {
        return await HoneyNetService.getBlockByHash(blockHash);
      }
      
      return null;
    } catch (error) {
      console.error('Error getting block by hash:', error);
      return null;
    }
  }

  async getThreatRecord(threatId: string): Promise<ThreatRecord | null> {
    try {
      // Check pending records first
      const pendingRecord = this.pendingThreatRecords.find(record => record.id === threatId);
      if (pendingRecord) return pendingRecord;
      
      // Check local chain
      for (const block of this.localChain) {
        const record = block.threatRecords.find(r => r.id === threatId);
        if (record) return record;
      }
      
      // Query network if connected
      if (this.isConnected) {
        return await HoneyNetService.getThreatRecord(threatId);
      }
      
      return null;
    } catch (error) {
      console.error('Error getting threat record:', error);
      return null;
    }
  }

  async verifyChainIntegrity(): Promise<boolean> {
    try {
      // Verify local chain
      const localIntegrity = await this.verifyLocalChain();
      
      if (this.isConnected) {
        // Verify against network
        const networkIntegrity = await HoneyNetService.verifyChainIntegrity();
        return localIntegrity && networkIntegrity;
      }
      
      return localIntegrity;
    } catch (error) {
      console.error('Error verifying chain integrity:', error);
      return false;
    }
  }

  async getMiningRewards(): Promise<MiningReward[]> {
    try {
      if (this.isConnected) {
        return await HoneyNetService.getMiningRewards(this.nodeId);
      } else {
        // Return local mining rewards (if any)
        return [];
      }
    } catch (error) {
      console.error('Error getting mining rewards:', error);
      return [];
    }
  }

  async startMining(): Promise<boolean> {
    try {
      if (!this.isConnected) {
        console.warn('Cannot start mining: not connected to network');
        return false;
      }
      
      // Start mining process
      const result = await HoneyNetService.startMining(this.nodeId);
      return result.success;
    } catch (error) {
      console.error('Error starting mining:', error);
      return false;
    }
  }

  async stopMining(): Promise<boolean> {
    try {
      if (!this.isConnected) return true;
      
      const result = await HoneyNetService.stopMining(this.nodeId);
      return result.success;
    } catch (error) {
      console.error('Error stopping mining:', error);
      return false;
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  getNodeId(): string {
    return this.nodeId;
  }

  // Private methods

  private async getOrCreateNodeId(): Promise<string> {
    try {
      let nodeId = await AsyncStorage.getItem('blockchain_node_id');
      
      if (!nodeId) {
        nodeId = this.generateNodeId();
        await AsyncStorage.setItem('blockchain_node_id', nodeId);
      }
      
      return nodeId;
    } catch (error) {
      console.error('Error getting/creating node ID:', error);
      return this.generateNodeId();
    }
  }

  private generateNodeId(): string {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2);
    return `node_${timestamp}_${random}`;
  }

  private generateThreatId(): string {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2);
    return `threat_${timestamp}_${random}`;
  }

  private async loadLocalChain(): Promise<void> {
    try {
      const chainData = await AsyncStorage.getItem('local_blockchain');
      if (chainData) {
        this.localChain = JSON.parse(chainData);
      }
      
      const pendingData = await AsyncStorage.getItem('pending_threat_records');
      if (pendingData) {
        this.pendingThreatRecords = JSON.parse(pendingData);
      }
    } catch (error) {
      console.error('Error loading local chain:', error);
    }
  }

  private async saveLocalChain(): Promise<void> {
    try {
      await AsyncStorage.setItem('local_blockchain', JSON.stringify(this.localChain));
    } catch (error) {
      console.error('Error saving local chain:', error);
    }
  }

  private async savePendingRecords(): Promise<void> {
    try {
      await AsyncStorage.setItem('pending_threat_records', JSON.stringify(this.pendingThreatRecords));
    } catch (error) {
      console.error('Error saving pending records:', error);
    }
  }

  private async connectToNetwork(): Promise<void> {
    try {
      const result = await HoneyNetService.connectToBlockchainNetwork(this.nodeId);
      this.isConnected = result.success;
      
      if (this.isConnected) {
        // Sync with network
        await this.syncWithNetwork();
      }
    } catch (error) {
      console.error('Error connecting to blockchain network:', error);
      this.isConnected = false;
    }
  }

  private async syncWithNetwork(): Promise<void> {
    try {
      if (!this.isConnected) return;
      
      // Get latest blocks from network
      const networkBlocks = await HoneyNetService.getLatestBlocks(100);
      
      // Merge with local chain
      await this.mergeChains(networkBlocks);
      
      // Submit pending records
      await this.submitPendingRecords();
      
    } catch (error) {
      console.error('Error syncing with network:', error);
    }
  }

  private async mergeChains(networkBlocks: Block[]): Promise<void> {
    try {
      // Simple merge strategy - replace local chain if network chain is longer and valid
      if (networkBlocks.length > this.localChain.length) {
        const isValid = await this.validateChain(networkBlocks);
        if (isValid) {
          this.localChain = networkBlocks;
          await this.saveLocalChain();
        }
      }
    } catch (error) {
      console.error('Error merging chains:', error);
    }
  }

  private async submitPendingRecords(): Promise<void> {
    try {
      if (!this.isConnected || this.pendingThreatRecords.length === 0) return;
      
      const recordsToSubmit = [...this.pendingThreatRecords];
      
      for (const record of recordsToSubmit) {
        try {
          await this.submitToNetwork(record);
          
          // Remove from pending if successful
          this.pendingThreatRecords = this.pendingThreatRecords.filter(r => r.id !== record.id);
        } catch (error) {
          console.error('Error submitting pending record:', error);
          // Keep in pending for next attempt
        }
      }
      
      await this.savePendingRecords();
    } catch (error) {
      console.error('Error submitting pending records:', error);
    }
  }

  private async submitToNetwork(threatRecord: ThreatRecord): Promise<void> {
    try {
      await HoneyNetService.submitThreatToBlockchain(threatRecord);
    } catch (error) {
      console.error('Error submitting to network:', error);
      throw error;
    }
  }

  private getTotalThreatsInChain(): number {
    return this.localChain.reduce((total, block) => total + block.threatRecords.length, 0);
  }

  private async calculateChainIntegrity(): Promise<number> {
    try {
      if (this.localChain.length === 0) return 1.0;
      
      const isValid = await this.verifyLocalChain();
      return isValid ? 1.0 : 0.0;
    } catch (error) {
      console.error('Error calculating chain integrity:', error);
      return 0.0;
    }
  }

  private getLastBlockTime(): Date {
    if (this.localChain.length === 0) return new Date();
    return this.localChain[this.localChain.length - 1].timestamp;
  }

  private async verifyLocalChain(): Promise<boolean> {
    try {
      return await this.validateChain(this.localChain);
    } catch (error) {
      console.error('Error verifying local chain:', error);
      return false;
    }
  }

  private async validateChain(chain: Block[]): Promise<boolean> {
    try {
      if (chain.length === 0) return true;
      
      // Verify each block
      for (let i = 1; i < chain.length; i++) {
        const currentBlock = chain[i];
        const previousBlock = chain[i - 1];
        
        // Check if previous hash matches
        if (currentBlock.previousHash !== previousBlock.blockHash) {
          return false;
        }
        
        // Verify block hash
        const calculatedHash = await this.calculateBlockHash(currentBlock);
        if (calculatedHash !== currentBlock.blockHash) {
          return false;
        }
      }
      
      return true;
    } catch (error) {
      console.error('Error validating chain:', error);
      return false;
    }
  }

  private async calculateBlockHash(block: Block): Promise<string> {
    // Simplified hash calculation for mobile
    const blockData = {
      blockNumber: block.blockNumber,
      previousHash: block.previousHash,
      timestamp: block.timestamp.getTime(),
      threatRecords: block.threatRecords,
      nonce: block.nonce
    };
    
    const dataString = JSON.stringify(blockData);
    
    // Use a simple hash function (in production, use proper cryptographic hash)
    let hash = 0;
    for (let i = 0; i < dataString.length; i++) {
      const char = dataString.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    return hash.toString(16);
  }

  private startBackgroundSync(): void {
    // Sync every 30 seconds
    setInterval(async () => {
      if (this.isConnected) {
        await this.syncWithNetwork();
      } else {
        // Try to reconnect
        await this.connectToNetwork();
      }
    }, 30000);
  }

  async cleanup(): Promise<void> {
    try {
      // Save current state
      await this.saveLocalChain();
      await this.savePendingRecords();
      
      // Stop mining if active
      await this.stopMining();
      
      // Clear memory
      this.localChain = [];
      this.pendingThreatRecords = [];
      this.isConnected = false;
    } catch (error) {
      console.error('Error during blockchain service cleanup:', error);
    }
  }
}

export const BlockchainService = new BlockchainServiceClass();
