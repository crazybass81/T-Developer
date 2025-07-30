const MemoryLevel = {
  L1: 'L1',
  L2: 'L2', 
  L3: 'L3',
  L4: 'L4',
  L5: 'L5'
};

class MemoryHierarchy {
  constructor() {
    this.stores = new Map();
    this.accessCounts = new Map();
    this.stats = {
      hits: 0,
      misses: 0,
      promotions: 0,
      evictions: 0,
      totalItems: 0
    };
    
    Object.values(MemoryLevel).forEach(level => {
      this.stores.set(level, new Map());
    });
  }

  async store(level, key, value, ttl) {
    const store = this.stores.get(level);
    const item = {
      value,
      timestamp: Date.now(),
      ttl,
      accessCount: 0
    };
    
    store.set(key, item);
    this.stats.totalItems++;
    return key;
  }

  async get(key) {
    for (const [level, store] of this.stores) {
      if (store.has(key)) {
        const item = store.get(key);
        
        if (item.ttl && Date.now() > item.timestamp + item.ttl) {
          store.delete(key);
          this.stats.totalItems--;
          continue;
        }
        
        item.accessCount++;
        this.stats.hits++;
        
        if (item.accessCount > 3 && level !== 'L1') {
          this.promote(key, item);
        }
        
        return item.value;
      }
    }
    
    this.stats.misses++;
    return undefined;
  }

  promote(key, item) {
    for (const [level, store] of this.stores) {
      if (store.has(key)) {
        store.delete(key);
        this.stores.get('L1').set(key, item);
        this.stats.promotions++;
        break;
      }
    }
  }

  evictLRU(level, count = 1) {
    const store = this.stores.get(level);
    const items = Array.from(store.entries())
      .sort((a, b) => a[1].timestamp - b[1].timestamp)
      .slice(0, count);
    
    items.forEach(([key]) => {
      store.delete(key);
      this.stats.evictions++;
      this.stats.totalItems--;
    });
  }

  getStats() {
    const total = this.stats.hits + this.stats.misses;
    return {
      ...this.stats,
      hitRate: total > 0 ? this.stats.hits / total : 0
    };
  }

  getAccessPatterns() {
    const patterns = {};
    for (const [level, store] of this.stores) {
      for (const [key, item] of store) {
        patterns[key] = {
          frequency: item.accessCount,
          currentLevel: level,
          lastAccess: item.timestamp
        };
      }
    }
    return patterns;
  }

  findLargeItems(threshold) {
    const largeItems = [];
    for (const [level, store] of this.stores) {
      for (const [key, item] of store) {
        const size = JSON.stringify(item.value).length;
        if (size > threshold) {
          largeItems.push({ key, data: item.value, size, level });
        }
      }
    }
    return largeItems;
  }

  update(key, newValue) {
    for (const [level, store] of this.stores) {
      if (store.has(key)) {
        const item = store.get(key);
        item.value = newValue;
        return true;
      }
    }
    return false;
  }
}

module.exports = { MemoryHierarchy, MemoryLevel };