export interface CustomRule {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
}

export const customRules: CustomRule[] = [
  { id: 'UIS-001', description: 'Enforce signed commits', severity: 'medium' },
  { id: 'UIS-002', description: 'Disallow plaintext secrets in configs', severity: 'high' }
];
