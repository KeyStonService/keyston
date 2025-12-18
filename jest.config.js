module.exports = {
  // Test environment
  testEnvironment: 'node',
  
  // Root directories
  roots: [
    '<rootDir>/src',
    '<rootDir>/core',
    '<rootDir>/mcp-servers',
  ],
  
  // Test file patterns
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/?(*.)+(spec|test).+(ts|tsx|js)',
  ],
  
  // Transform TypeScript files
  transform: {
    '^.+\\.(ts|tsx)$': [
      'ts-jest',
      {
        tsconfig: 'tsconfig.json',
      },
    ],
  },
  
  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  
  // Module name mapping (for path aliases)
  moduleNameMapper: {
    '^@machinenativeops/(.*)$': '<rootDir>/src/$1',
    '^@core/(.*)$': '<rootDir>/core/$1',
    '^@bridges/(.*)$': '<rootDir>/bridges/$1',
    '^@automation/(.*)$': '<rootDir>/automation/$1',
    '^@mcp/(.*)$': '<rootDir>/mcp-servers/$1',
  },
  
  // Coverage configuration
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    'core/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/__tests__/**',
    '!**/dist/**',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'clover', 'html'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  
  // Timeout
  testTimeout: 30000,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Verbose output
  verbose: true,
  
  // Error handling
  errorOnDeprecated: true,
  
  // Max workers
  maxWorkers: '50%',
  
  // Test sequencer
  testSequencer: '<rootDir>/jest.sequencer.js',
  
  // Global setup/teardown
  globalSetup: '<rootDir>/jest.globalSetup.js',
  globalTeardown: '<rootDir>/jest.globalTeardown.js',
  
  // Reporters
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: 'reports/junit',
        outputName: 'junit.xml',
      },
    ],
  ],
  
  // Watch plugins
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
  
  // Snapshot serializers
  snapshotSerializers: [],
  
  // Projects (monorepo support)
  projects: [
    {
      displayName: 'core',
      testMatch: ['<rootDir>/core/**/*.test.ts'],
      testEnvironment: 'node',
    },
    {
      displayName: 'mcp-servers',
      testMatch: ['<rootDir>/mcp-servers/**/*.test.ts'],
      testEnvironment: 'node',
    },
  ],
};
