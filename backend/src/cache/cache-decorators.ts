import { CacheManager } from './cache-manager';

export interface CacheOptions {
  key?: string;
  ttl?: number;
  strategy?: string;
  tags?: string[];
}

let cacheManager: CacheManager;

export function setCacheManager(manager: CacheManager): void {
  cacheManager = manager;
}

export function Cacheable(options: CacheOptions = {}) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      if (!cacheManager) {
        return method.apply(this, args);
      }

      // Generate cache key
      const baseKey = options.key || `${target.constructor.name}:${propertyName}`;
      const argsKey = args.length > 0 ? `:${JSON.stringify(args)}` : '';
      const cacheKey = `${baseKey}${argsKey}`;

      // Try to get from cache
      const cached = await cacheManager.get(cacheKey);
      if (cached !== null) {
        return cached;
      }

      // Execute method and cache result
      const result = await method.apply(this, args);
      await cacheManager.set(cacheKey, result, options.strategy);

      return result;
    };

    return descriptor;
  };
}

export function CacheInvalidate(options: { tags?: string[]; patterns?: string[] } = {}) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const result = await method.apply(this, args);

      if (cacheManager) {
        // Invalidate by tags
        if (options.tags) {
          for (const tag of options.tags) {
            await cacheManager.invalidateByTag(tag);
          }
        }

        // Invalidate by patterns
        if (options.patterns) {
          for (const pattern of options.patterns) {
            await cacheManager.invalidateByPattern(pattern);
          }
        }
      }

      return result;
    };

    return descriptor;
  };
}