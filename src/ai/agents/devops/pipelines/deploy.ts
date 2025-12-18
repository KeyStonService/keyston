export const deployPipeline = {
  name: 'Deploy',
  strategies: ['blue-green', 'canary'],
  approvalsRequired: true,
};
