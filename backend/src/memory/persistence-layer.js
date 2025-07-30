class PersistenceLayer {
  constructor(config = {}) {
    this.storage = new Map(); // Mock storage
    this.config = {
      batchSize: config.batchSize || 100,
      flushInterval: config.flushInterval || 5000,
      compression: config.compression || false
    };
    this.pendingWrites = [];
    this.startBatchProcessor();
  }

  async save(key, data, options = {}) {
    const entry = {
      key,
      data: this.config.compression ? this.compress(data) : data,
      timestamp: new Date(),
      ttl: options.ttl,
      metadata: options.metadata || {}
    };

    if (options.immediate) {
      return this.writeImmediate(entry);
    } else {
      this.pendingWrites.push(entry);
      return Promise.resolve(key);
    }
  }

  async load(key) {
    const entry = this.storage.get(key);
    if (!entry) return null;

    // Check TTL
    if (entry.ttl && Date.now() > entry.timestamp.getTime() + entry.ttl) {
      this.storage.delete(key);
      return null;
    }

    return this.config.compression ? this.decompress(entry.data) : entry.data;
  }

  async delete(key) {
    return this.storage.delete(key);
  }

  async exists(key) {
    return this.storage.has(key);
  }

  async flush() {
    if (this.pendingWrites.length === 0) return;

    const batch = this.pendingWrites.splice(0);
    for (const entry of batch) {
      this.storage.set(entry.key, entry);
    }
  }

  startBatchProcessor() {
    setInterval(() => {
      this.flush().catch(console.error);
    }, this.config.flushInterval);
  }

  async writeImmediate(entry) {
    this.storage.set(entry.key, entry);
    return entry.key;
  }

  compress(data) {
    // Mock compression
    return JSON.stringify(data);
  }

  decompress(data) {
    // Mock decompression
    return JSON.parse(data);
  }

  getStats() {
    return {
      totalEntries: this.storage.size,
      pendingWrites: this.pendingWrites.length,
      storageSize: JSON.stringify(Array.from(this.storage.entries())).length
    };
  }
}

module.exports = { PersistenceLayer };