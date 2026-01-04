#!/bin/bash
# ChatOps API 使用示例 - 消息管理
#
# 設置環境變量:
# export CHATOPS_API_URL=https://api.chatops.example.com
# export CHATOPS_TOKEN=your-token

API_URL="${CHATOPS_API_URL:-http://localhost:8080}"
TOKEN="${CHATOPS_TOKEN:-test-token}"

echo "=== ChatOps API Examples - Messages ==="
echo "API URL: $API_URL"
echo ""

# 1. 創建消息
echo "1. Creating a message..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello from API example",
    "channel": "general",
    "metadata": {
      "source": "curl-example",
      "version": "1.0"
    },
    "priority": "normal"
  }')

echo "$CREATE_RESPONSE" | jq .
MESSAGE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id // .message_id // empty')
echo ""

if [ -n "$MESSAGE_ID" ]; then
  # 2. 獲取消息狀態
  echo "2. Getting message status for $MESSAGE_ID..."
  curl -s -X GET "$API_URL/api/v1/messages/$MESSAGE_ID/status" \
    -H "Authorization: Bearer $TOKEN" | jq .
  echo ""

  # 3. 獲取消息詳情
  echo "3. Getting message details for $MESSAGE_ID..."
  curl -s -X GET "$API_URL/api/v1/messages/$MESSAGE_ID" \
    -H "Authorization: Bearer $TOKEN" | jq .
  echo ""
fi

# 4. 列出消息
echo "4. Listing messages..."
curl -s -X GET "$API_URL/api/v1/messages?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 5. 按頻道過濾消息
echo "5. Filtering messages by channel..."
curl -s -X GET "$API_URL/api/v1/messages?channel=general&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 6. 按狀態過濾消息
echo "6. Filtering messages by status..."
curl -s -X GET "$API_URL/api/v1/messages?status=completed&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 7. 使用分頁
echo "7. Pagination example..."
curl -s -X GET "$API_URL/api/v1/messages?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 8. 按時間範圍過濾
echo "8. Filtering by time range..."
FROM_DATE=$(date -u -d "1 hour ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1H +%Y-%m-%dT%H:%M:%SZ)
TO_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
curl -s -X GET "$API_URL/api/v1/messages?from=$FROM_DATE&to=$TO_DATE&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

if [ -n "$MESSAGE_ID" ]; then
  # 9. 刪除消息
  echo "9. Deleting message $MESSAGE_ID..."
  curl -s -X DELETE "$API_URL/api/v1/messages/$MESSAGE_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -w "HTTP Status: %{http_code}\n"
  echo ""
fi

echo "=== Examples Complete ==="
