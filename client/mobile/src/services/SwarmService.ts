/**
 * Swarm Intelligence Service for HoneyNet Mobile
 * שירות אינטליגנציה נחילית לאפליקציית HoneyNet לנייד
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { HoneyNetService } from './HoneyNetService';

export interface SwarmAgent {
  agentId: string;
  role: 'scout' | 'worker' | 'guard' | 'coordinator' | 'analyzer';
  status: 'active' | 'idle' | 'busy' | 'offline';
  currentTask?: SwarmTask;
  performance: number;
  location: {
    latitude?: number;
    longitude?: number;
    networkSegment?: string;
  };
  capabilities: string[];
  lastActivity: Date;
}

export interface SwarmTask {
  taskId: string;
  taskType: 'threat_scan' | 'honeypot_monitor' | 'data_analysis' | 'network_patrol' | 'intelligence_gather';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignedAgents: string[];
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  createdAt: Date;
  completedAt?: Date;
  result?: any;
  metadata: Record<string, any>;
}

export interface PheromoneTrail {
  trailId: string;
  trailType: 'threat' | 'safe' | 'resource' | 'danger';
  strength: number;
  location: string;
  createdBy: string;
  timestamp: Date;
  decayRate: number;
  metadata: Record<string, any>;
}

export interface SwarmIntelligence {
  collectiveKnowledge: Record<string, any>;
  emergentBehaviors: string[];
  swarmDecisions: SwarmDecision[];
  networkTopology: NetworkNode[];
}

export interface SwarmDecision {
  decisionId: string;
  decisionType: string;
  consensus: number;
  participatingAgents: string[];
  outcome: any;
  timestamp: Date;
}

export interface NetworkNode {
  nodeId: string;
  connections: string[];
  trustLevel: number;
  lastSeen: Date;
}

class SwarmServiceClass {
  private localAgent: SwarmAgent | null = null;
  private nearbyAgents: SwarmAgent[] = [];
  private activeTasks: SwarmTask[] = [];
  private pheromoneTrails: PheromoneTrail[] = [];
  private swarmIntelligence: SwarmIntelligence = {
    collectiveKnowledge: {},
    emergentBehaviors: [],
    swarmDecisions: [],
    networkTopology: []
  };
  private isConnectedToSwarm: boolean = false;

  async initialize(): Promise<void> {
    try {
      // Create or load local agent
      await this.initializeLocalAgent();
      
      // Load cached swarm data
      await this.loadSwarmData();
      
      // Connect to swarm network
      await this.connectToSwarm();
      
      // Start background processes
      this.startSwarmProcesses();
      
    } catch (error) {
      console.error('Error initializing swarm service:', error);
    }
  }

  async getSwarmStatus(): Promise<{
    localAgent: SwarmAgent | null;
    nearbyAgents: number;
    activeTasks: number;
    pheromoneTrails: number;
    swarmConnected: boolean;
    collectiveIntelligence: number;
  }> {
    return {
      localAgent: this.localAgent,
      nearbyAgents: this.nearbyAgents.length,
      activeTasks: this.activeTasks.length,
      pheromoneTrails: this.pheromoneTrails.length,
      swarmConnected: this.isConnectedToSwarm,
      collectiveIntelligence: this.calculateCollectiveIntelligence()
    };
  }

  async assignTask(taskType: SwarmTask['taskType'], priority: SwarmTask['priority'], metadata: Record<string, any>): Promise<string> {
    try {
      const task: SwarmTask = {
        taskId: this.generateTaskId(),
        taskType,
        priority,
        assignedAgents: [],
        status: 'pending',
        createdAt: new Date(),
        metadata
      };

      // Find suitable agents for the task
      const suitableAgents = await this.findSuitableAgents(task);
      task.assignedAgents = suitableAgents.map(agent => agent.agentId);

      // Add to active tasks
      this.activeTasks.push(task);
      
      // Save locally
      await this.saveSwarmData();
      
      // Distribute task to swarm if connected
      if (this.isConnectedToSwarm) {
        await this.distributeTaskToSwarm(task);
      }
      
      // Start task execution
      await this.executeTask(task);
      
      return task.taskId;
    } catch (error) {
      console.error('Error assigning task:', error);
      throw error;
    }
  }

  async depositPheromone(trailType: PheromoneTrail['trailType'], location: string, strength: number, metadata: Record<string, any>): Promise<void> {
    try {
      const trail: PheromoneTrail = {
        trailId: this.generateTrailId(),
        trailType,
        strength,
        location,
        createdBy: this.localAgent?.agentId || 'unknown',
        timestamp: new Date(),
        decayRate: 0.1, // 10% decay per hour
        metadata
      };

      this.pheromoneTrails.push(trail);
      
      // Limit trail count to prevent memory issues
      if (this.pheromoneTrails.length > 1000) {
        this.pheromoneTrails = this.pheromoneTrails.slice(-500);
      }
      
      await this.saveSwarmData();
      
      // Share with swarm if connected
      if (this.isConnectedToSwarm) {
        await this.sharePheromoneWithSwarm(trail);
      }
      
    } catch (error) {
      console.error('Error depositing pheromone:', error);
    }
  }

  async getPheromoneTrails(trailType?: PheromoneTrail['trailType'], location?: string): Promise<PheromoneTrail[]> {
    let trails = [...this.pheromoneTrails];
    
    // Apply decay
    trails = trails.map(trail => ({
      ...trail,
      strength: this.calculateDecayedStrength(trail)
    })).filter(trail => trail.strength > 0.01); // Remove very weak trails
    
    // Filter by type if specified
    if (trailType) {
      trails = trails.filter(trail => trail.trailType === trailType);
    }
    
    // Filter by location if specified
    if (location) {
      trails = trails.filter(trail => trail.location === location);
    }
    
    // Sort by strength (strongest first)
    trails.sort((a, b) => b.strength - a.strength);
    
    return trails;
  }

  async makeCollectiveDecision(decisionType: string, options: any[], votingAgents?: string[]): Promise<SwarmDecision> {
    try {
      const decision: SwarmDecision = {
        decisionId: this.generateDecisionId(),
        decisionType,
        consensus: 0,
        participatingAgents: votingAgents || this.nearbyAgents.map(agent => agent.agentId),
        outcome: null,
        timestamp: new Date()
      };

      if (this.isConnectedToSwarm) {
        // Distributed voting
        const votingResult = await this.conductDistributedVoting(decisionType, options, decision.participatingAgents);
        decision.consensus = votingResult.consensus;
        decision.outcome = votingResult.outcome;
      } else {
        // Local decision (fallback)
        decision.consensus = 1.0;
        decision.outcome = options[0]; // Default to first option
      }

      this.swarmIntelligence.swarmDecisions.push(decision);
      await this.saveSwarmData();
      
      return decision;
    } catch (error) {
      console.error('Error making collective decision:', error);
      throw error;
    }
  }

  async getCollectiveKnowledge(topic?: string): Promise<Record<string, any>> {
    if (topic) {
      return this.swarmIntelligence.collectiveKnowledge[topic] || {};
    }
    return this.swarmIntelligence.collectiveKnowledge;
  }

  async contributeKnowledge(topic: string, knowledge: any): Promise<void> {
    try {
      if (!this.swarmIntelligence.collectiveKnowledge[topic]) {
        this.swarmIntelligence.collectiveKnowledge[topic] = {};
      }
      
      // Merge knowledge
      this.swarmIntelligence.collectiveKnowledge[topic] = {
        ...this.swarmIntelligence.collectiveKnowledge[topic],
        ...knowledge,
        lastUpdated: new Date(),
        contributor: this.localAgent?.agentId
      };
      
      await this.saveSwarmData();
      
      // Share with swarm if connected
      if (this.isConnectedToSwarm) {
        await this.shareKnowledgeWithSwarm(topic, knowledge);
      }
      
    } catch (error) {
      console.error('Error contributing knowledge:', error);
    }
  }

  async getEmergentBehaviors(): Promise<string[]> {
    return this.swarmIntelligence.emergentBehaviors;
  }

  async getNearbyAgents(): Promise<SwarmAgent[]> {
    return this.nearbyAgents;
  }

  async getActiveTasks(): Promise<SwarmTask[]> {
    return this.activeTasks;
  }

  // Private methods

  private async initializeLocalAgent(): Promise<void> {
    try {
      const savedAgent = await AsyncStorage.getItem('swarm_local_agent');
      
      if (savedAgent) {
        this.localAgent = JSON.parse(savedAgent);
        this.localAgent!.lastActivity = new Date();
      } else {
        this.localAgent = {
          agentId: this.generateAgentId(),
          role: 'worker', // Default role
          status: 'active',
          performance: 1.0,
          location: {},
          capabilities: ['threat_detection', 'data_analysis', 'network_monitoring'],
          lastActivity: new Date()
        };
        
        await AsyncStorage.setItem('swarm_local_agent', JSON.stringify(this.localAgent));
      }
    } catch (error) {
      console.error('Error initializing local agent:', error);
    }
  }

  private async loadSwarmData(): Promise<void> {
    try {
      const swarmData = await AsyncStorage.getItem('swarm_data');
      if (swarmData) {
        const data = JSON.parse(swarmData);
        this.nearbyAgents = data.nearbyAgents || [];
        this.activeTasks = data.activeTasks || [];
        this.pheromoneTrails = data.pheromoneTrails || [];
        this.swarmIntelligence = data.swarmIntelligence || this.swarmIntelligence;
      }
    } catch (error) {
      console.error('Error loading swarm data:', error);
    }
  }

  private async saveSwarmData(): Promise<void> {
    try {
      const swarmData = {
        nearbyAgents: this.nearbyAgents,
        activeTasks: this.activeTasks,
        pheromoneTrails: this.pheromoneTrails,
        swarmIntelligence: this.swarmIntelligence
      };
      
      await AsyncStorage.setItem('swarm_data', JSON.stringify(swarmData));
    } catch (error) {
      console.error('Error saving swarm data:', error);
    }
  }

  private async connectToSwarm(): Promise<void> {
    try {
      if (!this.localAgent) return;
      
      const result = await HoneyNetService.connectToSwarm(this.localAgent);
      this.isConnectedToSwarm = result.success;
      
      if (this.isConnectedToSwarm) {
        // Get nearby agents
        this.nearbyAgents = await HoneyNetService.getNearbyAgents(this.localAgent.agentId);
        
        // Sync with swarm
        await this.syncWithSwarm();
      }
    } catch (error) {
      console.error('Error connecting to swarm:', error);
      this.isConnectedToSwarm = false;
    }
  }

  private async syncWithSwarm(): Promise<void> {
    try {
      if (!this.isConnectedToSwarm || !this.localAgent) return;
      
      // Get swarm intelligence updates
      const swarmUpdates = await HoneyNetService.getSwarmIntelligence(this.localAgent.agentId);
      
      // Merge updates
      this.mergeSwarmIntelligence(swarmUpdates);
      
      // Share local knowledge
      await this.shareLocalKnowledge();
      
    } catch (error) {
      console.error('Error syncing with swarm:', error);
    }
  }

  private mergeSwarmIntelligence(updates: Partial<SwarmIntelligence>): void {
    // Merge collective knowledge
    if (updates.collectiveKnowledge) {
      this.swarmIntelligence.collectiveKnowledge = {
        ...this.swarmIntelligence.collectiveKnowledge,
        ...updates.collectiveKnowledge
      };
    }
    
    // Merge emergent behaviors
    if (updates.emergentBehaviors) {
      const newBehaviors = updates.emergentBehaviors.filter(
        behavior => !this.swarmIntelligence.emergentBehaviors.includes(behavior)
      );
      this.swarmIntelligence.emergentBehaviors.push(...newBehaviors);
    }
    
    // Merge decisions
    if (updates.swarmDecisions) {
      this.swarmIntelligence.swarmDecisions.push(...updates.swarmDecisions);
    }
    
    // Merge network topology
    if (updates.networkTopology) {
      this.swarmIntelligence.networkTopology = updates.networkTopology;
    }
  }

  private async shareLocalKnowledge(): Promise<void> {
    try {
      if (!this.isConnectedToSwarm || !this.localAgent) return;
      
      await HoneyNetService.shareSwarmKnowledge(
        this.localAgent.agentId,
        this.swarmIntelligence.collectiveKnowledge
      );
    } catch (error) {
      console.error('Error sharing local knowledge:', error);
    }
  }

  private async findSuitableAgents(task: SwarmTask): Promise<SwarmAgent[]> {
    const suitableAgents: SwarmAgent[] = [];
    
    // Check local agent first
    if (this.localAgent && this.isAgentSuitableForTask(this.localAgent, task)) {
      suitableAgents.push(this.localAgent);
    }
    
    // Check nearby agents
    for (const agent of this.nearbyAgents) {
      if (this.isAgentSuitableForTask(agent, task) && suitableAgents.length < 3) {
        suitableAgents.push(agent);
      }
    }
    
    return suitableAgents;
  }

  private isAgentSuitableForTask(agent: SwarmAgent, task: SwarmTask): boolean {
    // Check if agent is available
    if (agent.status !== 'active' && agent.status !== 'idle') {
      return false;
    }
    
    // Check capabilities
    const requiredCapabilities = this.getRequiredCapabilities(task.taskType);
    const hasCapabilities = requiredCapabilities.every(cap => 
      agent.capabilities.includes(cap)
    );
    
    return hasCapabilities;
  }

  private getRequiredCapabilities(taskType: SwarmTask['taskType']): string[] {
    const capabilityMap = {
      'threat_scan': ['threat_detection', 'network_monitoring'],
      'honeypot_monitor': ['honeypot_management', 'intrusion_detection'],
      'data_analysis': ['data_analysis', 'pattern_recognition'],
      'network_patrol': ['network_monitoring', 'security_scanning'],
      'intelligence_gather': ['data_collection', 'threat_intelligence']
    };
    
    return capabilityMap[taskType] || [];
  }

  private async executeTask(task: SwarmTask): Promise<void> {
    try {
      task.status = 'in_progress';
      
      // Execute based on task type
      let result: any;
      
      switch (task.taskType) {
        case 'threat_scan':
          result = await this.executeThreatScan(task);
          break;
        case 'honeypot_monitor':
          result = await this.executeHoneypotMonitor(task);
          break;
        case 'data_analysis':
          result = await this.executeDataAnalysis(task);
          break;
        case 'network_patrol':
          result = await this.executeNetworkPatrol(task);
          break;
        case 'intelligence_gather':
          result = await this.executeIntelligenceGather(task);
          break;
        default:
          throw new Error(`Unknown task type: ${task.taskType}`);
      }
      
      task.result = result;
      task.status = 'completed';
      task.completedAt = new Date();
      
      // Deposit success pheromone
      await this.depositPheromone('safe', task.metadata.location || 'unknown', 0.8, {
        taskType: task.taskType,
        success: true
      });
      
    } catch (error) {
      console.error('Error executing task:', error);
      task.status = 'failed';
      task.result = { error: error.message };
      
      // Deposit danger pheromone
      await this.depositPheromone('danger', task.metadata.location || 'unknown', 0.6, {
        taskType: task.taskType,
        error: error.message
      });
    } finally {
      await this.saveSwarmData();
    }
  }

  private async executeThreatScan(task: SwarmTask): Promise<any> {
    // Simulate threat scanning
    return {
      threatsFound: Math.floor(Math.random() * 5),
      scanDuration: 30000,
      coverage: 0.95
    };
  }

  private async executeHoneypotMonitor(task: SwarmTask): Promise<any> {
    // Simulate honeypot monitoring
    return {
      honeypotsMonitored: 10,
      triggersDetected: Math.floor(Math.random() * 3),
      monitoringDuration: 60000
    };
  }

  private async executeDataAnalysis(task: SwarmTask): Promise<any> {
    // Simulate data analysis
    return {
      dataProcessed: 1024 * 1024, // 1MB
      patternsFound: Math.floor(Math.random() * 8),
      analysisTime: 45000
    };
  }

  private async executeNetworkPatrol(task: SwarmTask): Promise<any> {
    // Simulate network patrol
    return {
      nodesScanned: 50,
      anomaliesFound: Math.floor(Math.random() * 2),
      patrolDuration: 120000
    };
  }

  private async executeIntelligenceGather(task: SwarmTask): Promise<any> {
    // Simulate intelligence gathering
    return {
      intelligenceGathered: Math.floor(Math.random() * 20),
      sourcesContacted: 5,
      gatheringTime: 90000
    };
  }

  private calculateCollectiveIntelligence(): number {
    const knowledgeCount = Object.keys(this.swarmIntelligence.collectiveKnowledge).length;
    const behaviorCount = this.swarmIntelligence.emergentBehaviors.length;
    const decisionCount = this.swarmIntelligence.swarmDecisions.length;
    
    return (knowledgeCount * 0.4 + behaviorCount * 0.3 + decisionCount * 0.3) / 10;
  }

  private calculateDecayedStrength(trail: PheromoneTrail): number {
    const ageInHours = (Date.now() - trail.timestamp.getTime()) / (1000 * 60 * 60);
    return trail.strength * Math.exp(-trail.decayRate * ageInHours);
  }

  private async distributeTaskToSwarm(task: SwarmTask): Promise<void> {
    try {
      await HoneyNetService.distributeSwarmTask(task);
    } catch (error) {
      console.error('Error distributing task to swarm:', error);
    }
  }

  private async sharePheromoneWithSwarm(trail: PheromoneTrail): Promise<void> {
    try {
      await HoneyNetService.sharePheromoneTrail(trail);
    } catch (error) {
      console.error('Error sharing pheromone with swarm:', error);
    }
  }

  private async shareKnowledgeWithSwarm(topic: string, knowledge: any): Promise<void> {
    try {
      await HoneyNetService.shareSwarmKnowledge(this.localAgent!.agentId, { [topic]: knowledge });
    } catch (error) {
      console.error('Error sharing knowledge with swarm:', error);
    }
  }

  private async conductDistributedVoting(decisionType: string, options: any[], participatingAgents: string[]): Promise<{ consensus: number; outcome: any }> {
    try {
      const votingResult = await HoneyNetService.conductSwarmVoting(decisionType, options, participatingAgents);
      return votingResult;
    } catch (error) {
      console.error('Error conducting distributed voting:', error);
      return { consensus: 0.5, outcome: options[0] };
    }
  }

  private generateAgentId(): string {
    return `agent_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }

  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }

  private generateTrailId(): string {
    return `trail_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }

  private generateDecisionId(): string {
    return `decision_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }

  private startSwarmProcesses(): void {
    // Periodic sync with swarm
    setInterval(async () => {
      if (this.isConnectedToSwarm) {
        await this.syncWithSwarm();
      } else {
        await this.connectToSwarm();
      }
    }, 60000); // Every minute
    
    // Pheromone decay process
    setInterval(() => {
      this.pheromoneTrails = this.pheromoneTrails
        .map(trail => ({
          ...trail,
          strength: this.calculateDecayedStrength(trail)
        }))
        .filter(trail => trail.strength > 0.01);
    }, 300000); // Every 5 minutes
  }

  async cleanup(): Promise<void> {
    try {
      // Save current state
      await this.saveSwarmData();
      
      if (this.localAgent) {
        await AsyncStorage.setItem('swarm_local_agent', JSON.stringify(this.localAgent));
      }
      
      // Disconnect from swarm
      if (this.isConnectedToSwarm && this.localAgent) {
        await HoneyNetService.disconnectFromSwarm(this.localAgent.agentId);
      }
      
      // Clear memory
      this.nearbyAgents = [];
      this.activeTasks = [];
      this.pheromoneTrails = [];
      this.isConnectedToSwarm = false;
    } catch (error) {
      console.error('Error during swarm service cleanup:', error);
    }
  }
}

export const SwarmService = new SwarmServiceClass();
