import crypto from 'crypto';

export interface HashNode {
  id: string;
  weight: number;
}

export class ConsistentHashRing {
  private ring: Map<number, HashNode> = new Map();
  private sortedKeys: number[] = [];
  private virtualNodes: number;

  constructor(nodes: HashNode[], virtualNodes: number = 150) {
    this.virtualNodes = virtualNodes;
    nodes.forEach(node => this.addNode(node));
  }

  addNode(node: HashNode): void {
    const virtualNodeCount = Math.floor(this.virtualNodes * node.weight);
    
    for (let i = 0; i < virtualNodeCount; i++) {
      const hash = this.hash(`${node.id}:${i}`);
      this.ring.set(hash, node);
    }
    
    this.sortedKeys = Array.from(this.ring.keys()).sort((a, b) => a - b);
  }

  removeNode(nodeId: string): void {
    const keysToRemove: number[] = [];
    
    for (const [hash, node] of this.ring) {
      if (node.id === nodeId) {
        keysToRemove.push(hash);
      }
    }
    
    keysToRemove.forEach(key => this.ring.delete(key));
    this.sortedKeys = Array.from(this.ring.keys()).sort((a, b) => a - b);
  }

  getNode(key: string): HashNode | null {
    if (this.sortedKeys.length === 0) return null;
    
    const hash = this.hash(key);
    const index = this.findNodeIndex(hash);
    return this.ring.get(this.sortedKeys[index]) || null;
  }

  getNodes(key: string, count: number): HashNode[] {
    if (this.sortedKeys.length === 0) return [];
    
    const hash = this.hash(key);
    const startIndex = this.findNodeIndex(hash);
    const nodes: HashNode[] = [];
    const seen = new Set<string>();
    
    for (let i = 0; i < this.sortedKeys.length && nodes.length < count; i++) {
      const index = (startIndex + i) % this.sortedKeys.length;
      const node = this.ring.get(this.sortedKeys[index])!;
      
      if (!seen.has(node.id)) {
        nodes.push(node);
        seen.add(node.id);
      }
    }
    
    return nodes;
  }

  private findNodeIndex(hash: number): number {
    let left = 0;
    let right = this.sortedKeys.length - 1;
    
    while (left <= right) {
      const mid = Math.floor((left + right) / 2);
      if (this.sortedKeys[mid] === hash) {
        return mid;
      } else if (this.sortedKeys[mid] < hash) {
        left = mid + 1;
      } else {
        right = mid - 1;
      }
    }
    
    return left % this.sortedKeys.length;
  }

  private hash(key: string): number {
    return parseInt(
      crypto.createHash('md5').update(key).digest('hex').substring(0, 8),
      16
    );
  }

  getDistribution(): Record<string, number> {
    const distribution: Record<string, number> = {};
    
    for (const node of this.ring.values()) {
      distribution[node.id] = (distribution[node.id] || 0) + 1;
    }
    
    return distribution;
  }
}