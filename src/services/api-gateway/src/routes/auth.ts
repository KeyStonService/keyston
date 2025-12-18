import { Router } from 'express';
import jwt from 'jsonwebtoken';
import { config } from '../config';
import { logger } from '../config/logger';

export const authRouter = Router();

// Mock user database (replace with real database)
const users = new Map([
  ['admin@example.com', { id: '1', email: 'admin@example.com', password: 'hashed_password', role: 'admin' }]
]);

authRouter.post('/login', (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password required' });
  }

  const user = users.get(email);
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Generate JWT token
  const token = jwt.sign(
    { userId: user.id, email: user.email, role: user.role },
    config.jwtSecret,
    { expiresIn: config.jwtExpiresIn }
  );

  logger.info(`User logged in: ${email}`);

  res.json({
    token,
    expiresIn: config.jwtExpiresIn,
    user: {
      id: user.id,
      email: user.email,
      role: user.role
    }
  });
});

authRouter.post('/register', (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password required' });
  }

  if (users.has(email)) {
    return res.status(409).json({ error: 'User already exists' });
  }

  // TODO: SECURITY - Replace with proper bcrypt hashing before production
  // Example: const hashedPassword = await bcrypt.hash(password, 10);
  const newUser = {
    id: String(users.size + 1),
    email,
    password: 'hashed_' + password, // INSECURE - placeholder only
    role: 'user'
  };

  users.set(email, newUser);
  logger.info(`New user registered: ${email}`);

  res.status(201).json({
    message: 'User registered successfully',
    user: {
      id: newUser.id,
      email: newUser.email,
      role: newUser.role
    }
  });
});

authRouter.post('/refresh', (req, res) => {
  const { token } = req.body;

  if (!token) {
    return res.status(400).json({ error: 'Token required' });
  }

  try {
    const decoded = jwt.verify(token, config.jwtSecret) as { userId: string; email: string; role: string };
    const newToken = jwt.sign(
      { userId: decoded.userId, email: decoded.email, role: decoded.role },
      config.jwtSecret,
      { expiresIn: config.jwtExpiresIn }
    );

    res.json({ token: newToken, expiresIn: config.jwtExpiresIn });
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

authRouter.post('/logout', (req, res) => {
  // In a real implementation, you would invalidate the token
  logger.info('User logged out');
  res.json({ message: 'Logged out successfully' });
});
