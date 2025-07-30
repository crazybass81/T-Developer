// backend/src/memory/memory-manager.ts
export interface MemoryEntry {
  id: string;
  type: 'short_term' | 'long_term' | 'working';
  content: any;
  timestamp: Date;
  ttl?: number;
  metadata?: Record<string, any>;
}

export class MemoryManager {
  private shortTermMemory: Map<string, MemoryEntry> = new Map();
  private longTermMemory: Map<string, MemoryEntry> = new Map();
  private workingMemory: Map<string, MemoryEntry> = new Map();
  private cleanupInterval!: NodeJS.Timer;

  constructor() {
    this.startCleanup();
  }

  // Store memory entry
  store(entry: Omit<MemoryEntry, 'id' | 'timestamp'>): string {
    const id = this.generateId();
    const memoryEntry: MemoryEntry = {
      ...entry,
      id,
      timestamp: new Date()
    };

    switch (entry.type) {
      case 'short_term':
        this.shortTermMemory.set(id, memoryEntry);
        break;
      case 'long_term':
        this.longTermMemory.set(id, memoryEntry);
        break;
      case 'working':
        this.workingMemory.set(id, memoryEntry);
        break;
    }

    return id;
  }

  // Retrieve memory entry
  retrieve(id: string): MemoryEntry | null {
    return this.shortTermMemory.get(id) || 
           this.longTermMemory.get(id) || 
           this.workingMemory.get(id) || 
           null;
  }

  // Search memories by content
  search(query: string, type?: MemoryEntry['type']): MemoryEntry[] {
    const memories = this.getAllMemories(type);
    return memories.filter(memory => 
      JSON.stringify(memory.content).toLowerCase().includes(query.toLowerCase())
    );
  }

  // Get recent memories
  getRecent(count: number = 10, type?: MemoryEntry['type']): MemoryEntry[] {
    const memories = this.getAllMemories(type);
    return memories
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, count);
  }

  // Clear expired memories
  private cleanup(): void {
    const now = Date.now();
    
    [this.shortTermMemory, this.workingMemory].forEach(memory => {
      for (const [id, entry] of memory) {
        if (entry.ttl && (now - entry.timestamp.getTime()) > entry.ttl) {
          memory.delete(id);
        }
      }
    });
  }

  private getAllMemories(type?: MemoryEntry['type']): MemoryEntry[] {
    let memories: MemoryEntry[] = [];
    
    if (!type || type === 'short_term') {
      memories.push(...Array.from(this.shortTermMemory.values()));
    }
    if (!type || type === 'long_term') {
      memories.push(...Array.from(this.longTermMemory.values()));
    }
    if (!type || type === 'working') {
      memories.push(...Array.from(this.workingMemory.values()));
    }
    
    return memories;
  }

  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000); // 1 minute
  }

  private generateId(): string {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getStats(): {
    shortTerm: number;
    longTerm: number;
    working: number;
    total: number;
  } {
    return {
      shortTerm: this.shortTermMemory.size,
      longTerm: this.longTermMemory.size,
      working: this.workingMemory.size,
      total: this.shortTermMemory.size + this.longTermMemory.size + this.workingMemory.size
    };
  }
}