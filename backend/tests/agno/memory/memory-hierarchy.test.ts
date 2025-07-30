// backend/tests/agno/memory/memory-hierarchy.test.ts
import { MemoryHierarchy, MemoryLevel } from '../../../src/agno/memory/memory-hierarchy';

describe('MemoryHierarchy', () => {
  let memory: MemoryHierarchy;

  beforeEach(() => {
    memory = new MemoryHierarchy();
  });

  test('should store and retrieve from L1', async () => {
    await memory.set('test', 'value', MemoryLevel.L1_WORKING);
    const result = await memory.get('test');
    expect(result).toBe('value');
  });

  test('should promote from lower levels', async () => {
    await memory.set('test', 'value', MemoryLevel.L3_SHORT_TERM);
    const result = await memory.get('test');
    expect(result).toBe('value');
  });

  test('should return undefined for missing keys', async () => {
    const result = await memory.get('nonexistent');
    expect(result).toBeUndefined();
  });

  test('should optimize memory stores', async () => {
    await memory.set('test1', 'value1');
    await memory.set('test2', 'value2');
    await expect(memory.optimize()).resolves.not.toThrow();
  });
});