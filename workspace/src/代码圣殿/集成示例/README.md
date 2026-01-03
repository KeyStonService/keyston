# 集成示例 / Integration Examples

> **路径**: `src/代码圣殿/集成示例/`  
> **难度**: 中级 (Intermediate)  
> **前置知识**: API基础知识、网络基础

---

## 📋 概述

集成示例展示如何将 Intelligent-Hyperautomation 系统与各种外部系统和服务集成，包括数据库、API、消息队列和云服务。

---

## 🎯 集成类别

### 1. 数据库集成 (`database-integration/`)

#### PostgreSQL 集成

```typescript
// examples/database-integration/postgresql.ts
import { IntelligentAutomation } from '@machinenativeops/automation-sdk';
import { Pool } from 'pg';

async function postgresqlIntegration() {
  const pool = new Pool({
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD
  });

  const automation = new IntelligentAutomation();

  const workflow = await automation.createWorkflow({
    name: "PostgreSQL数据处理",
    steps: [
      {
        name: "fetch-records",
        type: "database-query",
        config: {
          connection: pool,
          query: "SELECT * FROM users WHERE active = true"
        }
      },
      {
        name: "process-data",
        type: "transform",
        config: {
          handler: (records) => records.map(r => ({
            ...r,
            processed: true,
            timestamp: new Date()
          }))
        }
      },
      {
        name: "save-results",
        type: "database-insert",
        config: {
          connection: pool,
          table: "processed_users",
          onConflict: "update"
        }
      }
    ]
  });

  await workflow.execute();
  await pool.end();
}
```

📂 **其他数据库示例**:

- MySQL: `examples/database-integration/mysql.ts`
- MongoDB: `examples/database-integration/mongodb.ts`
- Redis: `examples/database-integration/redis.ts`

---

### 2. 外部API集成 (`external-apis/`)

#### REST API 集成

```typescript
// examples/external-apis/rest-api.ts
import { IntelligentAutomation } from '@machinenativeops/automation-sdk';
import axios from 'axios';

async function restApiIntegration() {
  const automation = new IntelligentAutomation();

  const workflow = await automation.createWorkflow({
    name: "REST API集成示例",
    steps: [
      {
        name: "fetch-from-api",
        type: "http-request",
        config: {
          method: "GET",
          url: "https://api.example.com/v1/data",
          headers: {
            "Authorization": `Bearer ${process.env.API_TOKEN}`,
            "Content-Type": "application/json"
          },
          retry: {
            maxAttempts: 3,
            backoff: "exponential"
          }
        }
      },
      {
        name: "transform-data",
        type: "transform",
        config: {
          handler: (data) => ({
            timestamp: new Date(),
            records: data.items,
            count: data.items.length
          })
        }
      },
      {
        name: "post-results",
        type: "http-request",
        config: {
          method: "POST",
          url: "https://api.example.com/v1/results",
          body: "{{previousStepOutput}}"
        }
      }
    ]
  });

  const result = await workflow.execute();
  console.log("API集成完成:", result);
}
```

📂 **其他API示例**:

- GraphQL: `examples/external-apis/graphql.ts`
- SOAP: `examples/external-apis/soap.ts`
- Webhook: `examples/external-apis/webhook.ts`

---

### 3. 消息系统集成 (`messaging-systems/`)

#### Kafka 集成

```typescript
// examples/messaging-systems/kafka.ts
import { IntelligentAutomation } from '@machinenativeops/automation-sdk';
import { Kafka } from 'kafkajs';

async function kafkaIntegration() {
  const kafka = new Kafka({
    clientId: 'intelligent-automation',
    brokers: [process.env.KAFKA_BROKER || 'localhost:9092']
  });

  const producer = kafka.producer();
  const consumer = kafka.consumer({ groupId: 'automation-group' });

  const automation = new IntelligentAutomation();

  // 消费者工作流
  await consumer.connect();
  await consumer.subscribe({ topic: 'input-topic', fromBeginning: false });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const data = JSON.parse(message.value.toString());
      
      const workflow = await automation.createWorkflow({
        name: "Kafka消息处理",
        steps: [
          {
            name: "process-message",
            type: "transform",
            config: {
              handler: (input) => ({
                ...input,
                processed: true,
                timestamp: new Date()
              })
            }
          },
          {
            name: "publish-result",
            type: "kafka-producer",
            config: {
              producer: producer,
              topic: "output-topic",
              key: data.id
            }
          }
        ]
      });

      await workflow.execute({ input: data });
    }
  });
}
```

📂 **其他消息系统示例**:

- RabbitMQ: `examples/messaging-systems/rabbitmq.ts`
- AWS SQS: `examples/messaging-systems/aws-sqs.ts`
- Google Pub/Sub: `examples/messaging-systems/google-pubsub.ts`

---

### 4. 云服务集成 (`cloud-services/`)

#### AWS服务集成

```typescript
// examples/cloud-services/aws-services.ts
import { IntelligentAutomation } from '@machinenativeops/automation-sdk';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { LambdaClient, InvokeCommand } from '@aws-sdk/client-lambda';

async function awsServicesIntegration() {
  const s3Client = new S3Client({ region: process.env.AWS_REGION });
  const lambdaClient = new LambdaClient({ region: process.env.AWS_REGION });

  const automation = new IntelligentAutomation();

  const workflow = await automation.createWorkflow({
    name: "AWS服务集成",
    steps: [
      {
        name: "upload-to-s3",
        type: "aws-s3",
        config: {
          client: s3Client,
          operation: "putObject",
          params: {
            Bucket: process.env.S3_BUCKET,
            Key: "data/{{timestamp}}.json",
            Body: "{{inputData}}"
          }
        }
      },
      {
        name: "invoke-lambda",
        type: "aws-lambda",
        config: {
          client: lambdaClient,
          functionName: "data-processor",
          payload: {
            s3Key: "{{previousStepOutput.Key}}"
          }
        }
      },
      {
        name: "process-result",
        type: "transform",
        config: {
          handler: (result) => JSON.parse(result.Payload)
        }
      }
    ]
  });

  await workflow.execute();
}
```

📂 **其他云服务示例**:

- Azure: `examples/cloud-services/azure-services.ts`
- GCP: `examples/cloud-services/gcp-services.ts`
- 云存储: `examples/cloud-services/cloud-storage.ts`

---

## 🚀 快速开始

### 环境准备

```bash
# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env，配置各个服务的连接信息
```

### 运行示例

```bash
# 运行数据库集成示例
npm run example:postgresql
npm run example:mongodb

# 运行API集成示例
npm run example:rest-api
npm run example:graphql

# 运行消息系统示例
npm run example:kafka
npm run example:rabbitmq

# 运行云服务示例
npm run example:aws
npm run example:azure
```

---

## 📚 示例列表

| 集成类型 | 示例名称 | 语言 | 难度 |
|---------|---------|------|------|
| 数据库 | PostgreSQL | TypeScript | ⭐⭐ |
| 数据库 | MySQL | TypeScript | ⭐⭐ |
| 数据库 | MongoDB | TypeScript | ⭐⭐ |
| 数据库 | Redis | TypeScript | ⭐⭐ |
| API | REST API | TypeScript | ⭐⭐ |
| API | GraphQL | TypeScript | ⭐⭐⭐ |
| API | SOAP | TypeScript | ⭐⭐⭐ |
| API | Webhook | TypeScript | ⭐⭐ |
| 消息 | Kafka | TypeScript | ⭐⭐⭐ |
| 消息 | RabbitMQ | TypeScript | ⭐⭐⭐ |
| 消息 | AWS SQS | TypeScript | ⭐⭐ |
| 消息 | Google Pub/Sub | TypeScript | ⭐⭐ |
| 云服务 | AWS | TypeScript | ⭐⭐⭐ |
| 云服务 | Azure | TypeScript | ⭐⭐⭐ |
| 云服务 | GCP | TypeScript | ⭐⭐⭐ |

---

## 🔗 相关资源

- [API参考文档](../../docs/API_REFERENCE.md)
- [集成指南](../../docs/INTEGRATION_GUIDE.md)
- [故障排除](../故障排除/README.md)

---

**最后更新**: 2025-12-19
