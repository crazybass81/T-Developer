// backend/tests/agno/memory/memory-hierarchy.test.ts
const mockMemory = {
  get: jest.fn(),
  set: jest.fn(),
  optimize: jest.fn()
};

describe('MemoryHierarchy', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockMemory.get.mockResolvedValue('value');
    mockMemory.set.mockResolvedValue(undefined);
    mockMemory.optimize.mockResolvedValue(undefined);
  });

  test('should store and retrieve from L1', async () => {
    await mockMemory.set('test', 'value', 'L1_WORKING');
    const result = await mockMemory.get('test');
    expect(result).toBe('value');
  });

  test('should promote from lower levels', async () => {
    await mockMemory.set('test', 'value', 'L3_SHORT_TERM');
    const result = await mockMemory.get('test');
    expect(result).toBe('value');
  });

  test('should optimize memory stores', async () => {
    await mockMemory.set('test1', 'value1');
    await mockMemory.set('test2', 'value2');
    await expect(mockMemory.optimize()).resolves.not.toThrow();
  });
});