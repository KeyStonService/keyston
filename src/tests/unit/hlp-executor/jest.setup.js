/**
 * Jest Setup File for HLP Executor Core Tests
 * HLP 執行器核心測試設置文件
 * 
 * This file runs before each test file is executed
 */

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.LOG_LEVEL = 'error'; // Reduce log noise during tests

// Global test utilities
global.testUtils = {
  /**
   * Create a mock execution context
   */
  createMockContext: () => ({
    execution_id: 'test-exec-123',
    phase_id: 'test-phase-1',
    timestamp: new Date().toISOString(),
    metadata: {}
  }),
  
  /**
   * Create a mock state object
   */
  createMockState: (overrides = {}) => ({
    status: 'running',
    data: { key: 'value' },
    metadata: {},
    ...overrides
  }),
  
  /**
   * Wait for a condition to be true
   */
  waitFor: async (condition, timeout = 5000, interval = 100) => {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      if (await condition()) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    throw new Error('Timeout waiting for condition');
  }
};

// Clean up after all tests in this file
afterAll(() => {
  // Clean up any resources
  jest.clearAllTimers();
  jest.clearAllMocks();
});
