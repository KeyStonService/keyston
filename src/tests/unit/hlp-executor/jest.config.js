/**
 * Jest Configuration for HLP Executor Core Unit Tests
 * HLP 執行器核心單元測試配置
 */

module.exports = {
  displayName: 'hlp-executor-core',
  testEnvironment: 'node',
  
  // Test file patterns
  testMatch: [
    '**/*.test.ts',
    '**/*.test.js',
    '**/*.spec.ts',
    '**/*.spec.js'
  ],
  
  // Files to exclude from test discovery
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/',
    '/__fixtures__/',
    '/__mocks__/'
  ],
  
  // Coverage configuration
  collectCoverageFrom: [
    '**/*.ts',
    '**/*.js',
    '!**/*.d.ts',
    '!**/*.test.ts',
    '!**/*.test.js',
    '!**/*.spec.ts',
    '!**/*.spec.js',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/build/**'
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  },
  
  // Coverage output directory
  coverageDirectory: '<rootDir>/coverage',
  
  // Coverage reporters
  coverageReporters: [
    'text',
    'text-summary',
    'lcov',
    'html',
    'json'
  ],
  
  // Module paths
  moduleDirectories: [
    'node_modules',
    '<rootDir>'
  ],
  
  // Module name mapper for path aliases
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@core/(.*)$': '<rootDir>/../../../core/$1',
    '^@config/(.*)$': '<rootDir>/../../../config/$1',
    '^@tests/(.*)$': '<rootDir>/../$1'
  },
  
  // Transform files with ts-jest for TypeScript support
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: {
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        strict: true,
        skipLibCheck: true,
        resolveJsonModule: true
      }
    }]
  },
  
  // Setup files to run before tests
  setupFilesAfterEnv: [
    '<rootDir>/jest.setup.js'
  ],
  
  // Test timeout (milliseconds)
  testTimeout: 10000,
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks between tests
  restoreMocks: true,
  
  // Reset mocks between tests
  resetMocks: true,
  
  // Detect open handles
  detectOpenHandles: true,
  
  // Force exit after tests complete
  forceExit: true,
  
  // Maximum number of workers (configurable via environment)
  maxWorkers: process.env.CI ? 2 : '50%',
  
  // Reporters
  reporters: [
    'default'
  ],
  
  // Bail early on test failures
  bail: false,
  
  // Notify on completion (useful for watch mode)
  notify: false,
  
  // Error on deprecated APIs
  errorOnDeprecated: true
};
