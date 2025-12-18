# API Gateway Service

REST API gateway for external integrations with the Unmanned Island System.

## Features

- ✅ RESTful API endpoints (v1)
- ✅ JWT-based authentication
- ✅ API key management
- ✅ Rate limiting
- ✅ Request/response logging
- ✅ CORS configuration
- ✅ OpenAPI 3.0 documentation
- ✅ Role-based access control (RBAC)

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Production

```bash
npm start
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

### System Operations

- `GET /api/v1/system/health` - Health check
- `GET /api/v1/system/metrics` - System metrics
- `GET /api/v1/system/config` - System configuration
- `POST /api/v1/system/restart` - Restart service

### Resource Management

- `GET /api/v1/resources` - List resources
- `POST /api/v1/resources` - Create resource
- `GET /api/v1/resources/:id` - Get resource
- `PUT /api/v1/resources/:id` - Update resource
- `DELETE /api/v1/resources/:id` - Delete resource

### Task Management

- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/:id` - Get task
- `PUT /api/v1/tasks/:id/cancel` - Cancel task
- `GET /api/v1/tasks/:id/logs` - Get task logs

### Monitoring & Analytics

- `GET /api/v1/metrics/timeseries` - Time series metrics
- `GET /api/v1/logs` - Query logs
- `GET /api/v1/events` - List events
- `GET /api/v1/alerts` - List alerts

## Environment Variables

```env
PORT=8000
NODE_ENV=development
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=1h
API_RATE_LIMIT=100
CORS_ORIGIN=*
LOG_LEVEL=info
```

## Authentication

API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

Or use API key in query parameter:

```
?api_key=<your-api-key>
```

## Rate Limiting

Default rate limit: 100 requests per 15 minutes per IP.

## Documentation

API documentation is available at:

- Swagger UI: `http://localhost:8000/api/docs`
- OpenAPI JSON: `http://localhost:8000/api/docs/json`

## Testing

```bash
npm test
```

## License

MIT
