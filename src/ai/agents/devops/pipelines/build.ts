export const buildPipeline = {
  name: 'Build',
  stages: ['checkout', 'install', 'compile'],
  artifact: 'dist/',
};
