/**
 * GHSA ID Generator Utility
 *
 * Generates and validates GitHub Security Advisory (GHSA) IDs
 * Following the format: GHSA-xxxx-xxxx-xxxx
 * Where x is from the set: 23456789cfghjmpqrvwx
 *
 * @module utils/ghsa
 * @author SynergyMesh Team
 * @license MIT
 */

import { webcrypto } from 'node:crypto';

import { GHSA_ID_PATTERN } from '../types/advisory.js';

/**
 * Valid characters for GHSA ID generation
 * Excludes ambiguous characters (0, 1, a, b, d, e, i, k, l, n, o, s, t, u, y, z)
 */
const GHSA_CHARSET = '23456789cfghjmpqrvwx';

/**
 * Generates a cryptographically random GHSA ID segment
 * @param length - Length of the segment (default: 4)
 * @returns Random segment string
 */
function generateSegment(length: number = 4): string {
  let segment = '';
  const charsetLength = GHSA_CHARSET.length;

  // Use node:crypto webcrypto API for cryptographic randomness
  const randomValues = new Uint32Array(length);
  webcrypto.getRandomValues(randomValues);

  for (let i = 0; i < length; i++) {
    segment += GHSA_CHARSET[randomValues[i] % charsetLength];
  }

  return segment;
}

/**
 * Generates a new GHSA ID
 *
 * @returns A new GHSA ID in format GHSA-xxxx-xxxx-xxxx
 *
 * @example
 * const id = generateGHSAId();
 * console.log(id); // "GHSA-c3gv-9cxf-6f57"
 */
export function generateGHSAId(): string {
  const segment1 = generateSegment();
  const segment2 = generateSegment();
  const segment3 = generateSegment();

  return `GHSA-${segment1}-${segment2}-${segment3}`;
}

/**
 * Validates a GHSA ID format
 *
 * @param id - The ID to validate
 * @returns True if the ID is valid, false otherwise
 *
 * @example
 * validateGHSAId('GHSA-c3gv-9cxf-6f57'); // true
 * validateGHSAId('GHSA-invalid'); // false
 */
export function validateGHSAId(id: string): boolean {
  return GHSA_ID_PATTERN.test(id);
}

/**
 * Parses a GHSA ID into its segments
 *
 * @param id - The GHSA ID to parse
 * @returns Parsed segments or null if invalid
 *
 * @example
 * parseGHSAId('GHSA-c3gv-9cxf-6f57');
 * // { prefix: 'GHSA', segment1: 'c3gv', segment2: '9cxf', segment3: '6f57' }
 */
export function parseGHSAId(id: string): {
  prefix: string;
  segment1: string;
  segment2: string;
  segment3: string;
} | null {
  if (!validateGHSAId(id)) {
    return null;
  }

  const parts = id.split('-');
  return {
    prefix: parts[0],
    segment1: parts[1],
    segment2: parts[2],
    segment3: parts[3],
  };
}

/**
 * Generates a batch of unique GHSA IDs
 *
 * @param count - Number of IDs to generate
 * @param existingIds - Optional set of existing IDs to avoid duplicates
 * @returns Array of unique GHSA IDs
 *
 * @example
 * const ids = generateBatchGHSAIds(5);
 * console.log(ids); // ['GHSA-xxxx-xxxx-xxxx', ...]
 */
export function generateBatchGHSAIds(
  count: number,
  existingIds: Set<string> = new Set()
): string[] {
  const ids: string[] = [];
  const allIds = new Set(existingIds);

  let attempts = 0;
  const maxAttempts = count * 10; // Prevent infinite loop

  while (ids.length < count && attempts < maxAttempts) {
    const newId = generateGHSAId();
    if (!allIds.has(newId)) {
      ids.push(newId);
      allIds.add(newId);
    }
    attempts++;
  }

  if (ids.length < count) {
    throw new Error(`Failed to generate ${count} unique GHSA IDs after ${maxAttempts} attempts`);
  }

  return ids;
}

/**
 * Computes a deterministic GHSA ID from input data
 * Useful for idempotent advisory creation
 *
 * @param data - Input data to hash
 * @returns A deterministic GHSA ID
 *
 * @example
 * const id = computeDeterministicGHSAId('CVE-2024-1234-npm-lodash');
 */
export async function computeDeterministicGHSAId(data: string): Promise<string> {
  // Use node:crypto webcrypto API for SHA-256 hash
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);

  const hashBuffer = await webcrypto.subtle.digest('SHA-256', dataBuffer);
  const hashArray = new Uint8Array(hashBuffer);

  // Convert hash bytes to GHSA ID segments
  // Use first 12 bytes for 3 segments of 4 characters each
  let result = 'GHSA';

  for (let segmentIndex = 0; segmentIndex < 3; segmentIndex++) {
    let segment = '';
    for (let charIndex = 0; charIndex < 4; charIndex++) {
      const byteIndex = segmentIndex * 4 + charIndex;
      segment += GHSA_CHARSET[hashArray[byteIndex] % GHSA_CHARSET.length];
    }
    result += `-${segment}`;
  }

  return result;
}

/**
 * Extracts all GHSA IDs from text
 *
 * @param text - Text to search for GHSA IDs
 * @returns Array of found GHSA IDs
 *
 * @example
 * const ids = extractGHSAIds('See GHSA-c3gv-9cxf-6f57 and GHSA-x2p5-qgf7-r8m4');
 * // ['GHSA-c3gv-9cxf-6f57', 'GHSA-x2p5-qgf7-r8m4']
 */
export function extractGHSAIds(text: string): string[] {
  const globalPattern =
    /GHSA-[23456789cfghjmpqrvwx]{4}-[23456789cfghjmpqrvwx]{4}-[23456789cfghjmpqrvwx]{4}/g;
  const matches = text.match(globalPattern);
  return matches ? [...new Set(matches)] : [];
}

/**
 * GHSA ID utility class for object-oriented usage
 */
export class GHSAIdGenerator {
  private _generatedIds: Set<string> = new Set();

  /**
   * Generate a new unique GHSA ID
   */
  generate(): string {
    let id: string;
    let attempts = 0;
    const maxAttempts = 100;

    do {
      id = generateGHSAId();
      attempts++;
    } while (this._generatedIds.has(id) && attempts < maxAttempts);

    if (this._generatedIds.has(id)) {
      throw new Error('Failed to generate unique GHSA ID');
    }

    this._generatedIds.add(id);
    return id;
  }

  /**
   * Check if an ID was generated by this instance
   */
  hasGenerated(id: string): boolean {
    return this._generatedIds.has(id);
  }

  /**
   * Register an existing ID to prevent duplicates
   */
  register(id: string): void {
    if (validateGHSAId(id)) {
      this._generatedIds.add(id);
    }
  }

  /**
   * Get count of generated IDs
   */
  get count(): number {
    return this._generatedIds.size;
  }

  /**
   * Clear all registered IDs
   */
  clear(): void {
    this._generatedIds.clear();
  }
}

// Default export for convenience
export default {
  generate: generateGHSAId,
  validate: validateGHSAId,
  parse: parseGHSAId,
  generateBatch: generateBatchGHSAIds,
  computeDeterministic: computeDeterministicGHSAId,
  extract: extractGHSAIds,
  Generator: GHSAIdGenerator,
};
