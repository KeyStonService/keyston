import { getRequiredEnv, getWeTonke, getOptionalEnv, validateRequiredEnvs } from '../config/env';

describe('Environment Variable Utilities', () => {
  // Store original env values
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset process.env before each test
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    // Restore original env
    process.env = originalEnv;
  });

  describe('getRequiredEnv', () => {
    it('should return value when environment variable exists', () => {
      process.env.TEST_REQUIRED_VAR = 'test_value';
      expect(getRequiredEnv('TEST_REQUIRED_VAR')).toBe('test_value');
    });

    it('should throw error when environment variable is not set', () => {
      delete process.env.TEST_MISSING_VAR;
      expect(() => getRequiredEnv('TEST_MISSING_VAR')).toThrow(
        'Environment variable TEST_MISSING_VAR is not set.'
      );
    });

    it('should throw error when environment variable is empty string', () => {
      process.env.TEST_EMPTY_VAR = '';
      expect(() => getRequiredEnv('TEST_EMPTY_VAR')).toThrow(
        'Environment variable TEST_EMPTY_VAR is not set.'
      );
    });

    it('should handle special characters in value', () => {
      process.env.TEST_SPECIAL_CHARS = 'value!@#$%^&*()_+-=[]{}|;:,.<>?';
      expect(getRequiredEnv('TEST_SPECIAL_CHARS')).toBe('value!@#$%^&*()_+-=[]{}|;:,.<>?');
    });

    it('should handle whitespace in value', () => {
      process.env.TEST_WHITESPACE = '  value with spaces  ';
      expect(getRequiredEnv('TEST_WHITESPACE')).toBe('  value with spaces  ');
    });
  });

  describe('getWeTonke', () => {
    it('should return WE_TONKE value when set', () => {
      process.env.WE_TONKE = 'my_secret_token_123';
      expect(getWeTonke()).toBe('my_secret_token_123');
    });

    it('should throw error when WE_TONKE is not set', () => {
      delete process.env.WE_TONKE;
      expect(() => getWeTonke()).toThrow('Environment variable WE_TONKE is not set.');
    });

    it('should throw error when WE_TONKE is empty', () => {
      process.env.WE_TONKE = '';
      expect(() => getWeTonke()).toThrow('Environment variable WE_TONKE is not set.');
    });
  });

  describe('getOptionalEnv', () => {
    it('should return value when environment variable exists', () => {
      process.env.TEST_OPTIONAL_VAR = 'optional_value';
      expect(getOptionalEnv('TEST_OPTIONAL_VAR')).toBe('optional_value');
    });

    it('should return undefined when environment variable is not set', () => {
      delete process.env.TEST_MISSING_OPTIONAL;
      expect(getOptionalEnv('TEST_MISSING_OPTIONAL')).toBeUndefined();
    });

    it('should return empty string when environment variable is empty', () => {
      process.env.TEST_EMPTY_OPTIONAL = '';
      expect(getOptionalEnv('TEST_EMPTY_OPTIONAL')).toBe('');
    });
  });

  describe('validateRequiredEnvs', () => {
    it('should return all values when all environment variables exist', () => {
      process.env.VAR_ONE = 'value1';
      process.env.VAR_TWO = 'value2';
      process.env.VAR_THREE = 'value3';

      const result = validateRequiredEnvs(['VAR_ONE', 'VAR_TWO', 'VAR_THREE']);

      expect(result).toEqual({
        VAR_ONE: 'value1',
        VAR_TWO: 'value2',
        VAR_THREE: 'value3',
      });
    });

    it('should throw error when any environment variable is missing', () => {
      process.env.VAR_EXISTS = 'exists';
      delete process.env.VAR_MISSING;

      expect(() => validateRequiredEnvs(['VAR_EXISTS', 'VAR_MISSING'])).toThrow(
        'Environment variable VAR_MISSING is not set.'
      );
    });

    it('should return empty object for empty array', () => {
      const result = validateRequiredEnvs([]);
      expect(result).toEqual({});
    });

    it('should handle single variable', () => {
      process.env.SINGLE_VAR = 'single';
      const result = validateRequiredEnvs(['SINGLE_VAR']);
      expect(result).toEqual({ SINGLE_VAR: 'single' });
    });
  });
});
