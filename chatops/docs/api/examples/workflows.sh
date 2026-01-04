#!/bin/bash
# ChatOps API 使用示例 - 工作流管理
#
# 設置環境變量:
# export CHATOPS_API_URL=https://api.chatops.example.com
# export CHATOPS_TOKEN=your-token

API_URL="${CHATOPS_API_URL:-http://localhost:8080}"
TOKEN="${CHATOPS_TOKEN:-test-token}"

echo "=== ChatOps API Examples - Workflows ==="
echo "API URL: $API_URL"
echo ""

# 1. 創建工作流
echo "1. Creating a workflow..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/workflows" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example-workflow",
    "description": "An example workflow for demonstration",
    "steps": [
      {
        "id": "step1",
        "type": "transform",
        "config": {
          "operation": "uppercase"
        }
      },
      {
        "id": "step2",
        "type": "notify",
        "config": {
          "channel": "slack",
          "template": "result"
        }
      }
    ]
  }')

echo "$CREATE_RESPONSE" | jq .
WORKFLOW_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id // empty')
echo ""

# 2. 列出工作流
echo "2. Listing workflows..."
curl -s -X GET "$API_URL/api/v1/workflows" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

if [ -n "$WORKFLOW_ID" ]; then
  # 3. 獲取工作流詳情
  echo "3. Getting workflow details for $WORKFLOW_ID..."
  curl -s -X GET "$API_URL/api/v1/workflows/$WORKFLOW_ID" \
    -H "Authorization: Bearer $TOKEN" | jq .
  echo ""

  # 4. 執行工作流
  echo "4. Executing workflow $WORKFLOW_ID..."
  EXEC_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/workflows/$WORKFLOW_ID/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "input": {
        "message": "hello world"
      },
      "options": {
        "async": true,
        "timeout": 300
      }
    }')

  echo "$EXEC_RESPONSE" | jq .
  EXECUTION_ID=$(echo "$EXEC_RESPONSE" | jq -r '.executionId // empty')
  echo ""

  if [ -n "$EXECUTION_ID" ]; then
    # 5. 檢查執行狀態
    echo "5. Checking execution status for $EXECUTION_ID..."
    sleep 2  # 等待執行開始
    curl -s -X GET "$API_URL/api/v1/workflows/executions/$EXECUTION_ID" \
      -H "Authorization: Bearer $TOKEN" | jq .
    echo ""
  fi
fi

# 6. 列出執行歷史
echo "6. Listing workflow executions..."
curl -s -X GET "$API_URL/api/v1/workflows/executions?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

echo "=== Examples Complete ==="
