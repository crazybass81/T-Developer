class MemoryAnalytics {
  constructor() {
    this.metrics = new Map();
    this.patterns = new Map();
    this.alerts = [];
  }

  recordAccess(key, level, hitMiss, duration) {
    const timestamp = Date.now();
    const metric = {
      key,
      level,
      hitMiss,
      duration,
      timestamp
    };

    if (!this.metrics.has(key)) {
      this.metrics.set(key, []);
    }
    this.metrics.get(key).push(metric);

    this.updatePatterns(key, metric);
    this.checkAlerts(metric);
  }

  updatePatterns(key, metric) {
    if (!this.patterns.has(key)) {
      this.patterns.set(key, {
        accessCount: 0,
        avgDuration: 0,
        preferredLevel: null,
        lastAccess: null
      });
    }

    const pattern = this.patterns.get(key);
    pattern.accessCount++;
    pattern.avgDuration = (pattern.avgDuration + metric.duration) / 2;
    pattern.lastAccess = metric.timestamp;
    
    // Determine preferred level based on access frequency
    if (pattern.accessCount > 10) {
      pattern.preferredLevel = 'L1';
    } else if (pattern.accessCount > 5) {
      pattern.preferredLevel = 'L2';
    } else {
      pattern.preferredLevel = 'L3';
    }
  }

  checkAlerts(metric) {
    // High latency alert
    if (metric.duration > 100) {
      this.alerts.push({
        type: 'HIGH_LATENCY',
        key: metric.key,
        value: metric.duration,
        timestamp: metric.timestamp
      });
    }

    // Frequent miss alert
    if (metric.hitMiss === 'miss') {
      const recentMisses = this.getRecentMisses(metric.key, 60000); // 1 minute
      if (recentMisses > 5) {
        this.alerts.push({
          type: 'FREQUENT_MISSES',
          key: metric.key,
          value: recentMisses,
          timestamp: metric.timestamp
        });
      }
    }
  }

  getRecentMisses(key, timeWindow) {
    const now = Date.now();
    const keyMetrics = this.metrics.get(key) || [];
    
    return keyMetrics.filter(m => 
      m.timestamp > (now - timeWindow) && m.hitMiss === 'miss'
    ).length;
  }

  generateReport() {
    const totalAccesses = Array.from(this.metrics.values())
      .reduce((sum, metrics) => sum + metrics.length, 0);
    
    const hitRate = this.calculateHitRate();
    const avgLatency = this.calculateAverageLatency();
    const topKeys = this.getTopAccessedKeys(10);

    return {
      summary: {
        totalAccesses,
        hitRate,
        avgLatency,
        uniqueKeys: this.metrics.size,
        alertCount: this.alerts.length
      },
      topKeys,
      patterns: Object.fromEntries(this.patterns),
      recentAlerts: this.alerts.slice(-10),
      recommendations: this.generateRecommendations()
    };
  }

  calculateHitRate() {
    let hits = 0;
    let total = 0;

    for (const metrics of this.metrics.values()) {
      for (const metric of metrics) {
        total++;
        if (metric.hitMiss === 'hit') hits++;
      }
    }

    return total > 0 ? hits / total : 0;
  }

  calculateAverageLatency() {
    let totalDuration = 0;
    let count = 0;

    for (const metrics of this.metrics.values()) {
      for (const metric of metrics) {
        totalDuration += metric.duration;
        count++;
      }
    }

    return count > 0 ? totalDuration / count : 0;
  }

  getTopAccessedKeys(limit) {
    return Array.from(this.patterns.entries())
      .sort((a, b) => b[1].accessCount - a[1].accessCount)
      .slice(0, limit)
      .map(([key, pattern]) => ({ key, ...pattern }));
  }

  generateRecommendations() {
    const recommendations = [];
    const hitRate = this.calculateHitRate();

    if (hitRate < 0.7) {
      recommendations.push('Consider increasing cache size or adjusting eviction policy');
    }

    if (this.alerts.filter(a => a.type === 'HIGH_LATENCY').length > 5) {
      recommendations.push('High latency detected - optimize data access patterns');
    }

    if (this.alerts.filter(a => a.type === 'FREQUENT_MISSES').length > 3) {
      recommendations.push('Frequent cache misses - review caching strategy');
    }

    return recommendations;
  }

  clearOldMetrics(maxAge = 3600000) { // 1 hour
    const cutoff = Date.now() - maxAge;
    
    for (const [key, metrics] of this.metrics.entries()) {
      const filtered = metrics.filter(m => m.timestamp > cutoff);
      if (filtered.length === 0) {
        this.metrics.delete(key);
        this.patterns.delete(key);
      } else {
        this.metrics.set(key, filtered);
      }
    }

    this.alerts = this.alerts.filter(a => a.timestamp > cutoff);
  }
}

module.exports = { MemoryAnalytics };