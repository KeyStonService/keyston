// Test setup file
// Configure your test environment here

import '@testing-library/jest-dom/extend-expect';
import { configure } from '@testing-library/react';

// Custom test configuration
configure({
  // Add any necessary configuration options here
  // e.g., testIdAttribute: 'data-testid',
});

export function setupTests() {
  // Global setup for tests
  // e.g., setting up a mock server, global variables, etc.
  // Example: jest.mock('module-name');
  console.log('Test environment setup complete.');
}

// Call setupTests to initialize the test environment
setupTests();
