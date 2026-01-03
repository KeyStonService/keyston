// MachineNativeOps Pages - Main Entry Point
console.log('🚀 MachineNativeOps Platform Initialized');

// Add interactive features
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ Page loaded successfully');
  
  // Add animation to feature cards
  const featureCards = document.querySelectorAll('.feature-card');
  
  featureCards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
    card.style.opacity = '0';
    card.style.animation = 'fadeInUp 0.6s ease forwards';
  });
});
