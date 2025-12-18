import { describe, it, expect } from '@jest/globals';
import request from 'supertest';
import app from '../index';

describe('Authentication Endpoints', () => {
  describe('POST /api/v1/auth/login', () => {
    it('should return 400 when credentials are missing', async () => {
      const response = await request(app)
        .post('/api/v1/auth/login')
        .send({})
        .expect(400);

      expect(response.body).toHaveProperty('error', 'Email and password required');
    });

    it('should return 401 for invalid credentials', async () => {
      const response = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'invalid@example.com',
          password: 'wrongpassword'
        })
        .expect(401);

      expect(response.body).toHaveProperty('error', 'Invalid credentials');
    });

    it('should return JWT token for valid credentials', async () => {
      const response = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'admin@example.com',
          password: 'password'
        })
        .expect(200);

      expect(response.body).toHaveProperty('token');
      expect(response.body).toHaveProperty('expiresIn');
      expect(response.body).toHaveProperty('user');
      expect(response.body.user).toHaveProperty('email', 'admin@example.com');
    });
  });

  describe('POST /api/v1/auth/register', () => {
    it('should return 400 when credentials are missing', async () => {
      const response = await request(app)
        .post('/api/v1/auth/register')
        .send({})
        .expect(400);

      expect(response.body).toHaveProperty('error', 'Email and password required');
    });

    it('should return 409 when user already exists', async () => {
      const response = await request(app)
        .post('/api/v1/auth/register')
        .send({
          email: 'admin@example.com',
          password: 'password'
        })
        .expect(409);

      expect(response.body).toHaveProperty('error', 'User already exists');
    });

    it('should register new user successfully', async () => {
      const uniqueEmail = `test-${Date.now()}@example.com`;
      const response = await request(app)
        .post('/api/v1/auth/register')
        .send({
          email: uniqueEmail,
          password: 'password123'
        })
        .expect(201);

      expect(response.body).toHaveProperty('message', 'User registered successfully');
      expect(response.body).toHaveProperty('user');
      expect(response.body.user).toHaveProperty('email', uniqueEmail);
    });
  });

  describe('POST /api/v1/auth/logout', () => {
    it('should logout user successfully', async () => {
      const response = await request(app)
        .post('/api/v1/auth/logout')
        .expect(200);

      expect(response.body).toHaveProperty('message', 'Logged out successfully');
    });
  });
});
