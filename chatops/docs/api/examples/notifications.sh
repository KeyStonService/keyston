#!/bin/bash
# ChatOps API 使用示例 - 通知服務
#
# 設置環境變量:
# export CHATOPS_API_URL=https://api.chatops.example.com
# export CHATOPS_TOKEN=your-token

API_URL="${CHATOPS_API_URL:-http://localhost:8080}"
TOKEN="${CHATOPS_TOKEN:-test-token}"

echo "=== ChatOps API Examples - Notifications ==="
echo "API URL: $API_URL"
echo ""

# 1. 發送 Email 通知
echo "1. Sending email notification..."
curl -s -X POST "$API_URL/api/v1/notifications" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "user@example.com",
    "channel": "email",
    "title": "Test Notification",
    "body": "This is a test notification from the API example.",
    "data": {
      "priority": "normal",
      "category": "test"
    }
  }' | jq .
echo ""

# 2. 發送 Slack 通知
echo "2. Sending Slack notification..."
curl -s -X POST "$API_URL/api/v1/notifications" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "#general",
    "channel": "slack",
    "title": "ChatOps Alert",
    "body": "This is a test message from the ChatOps API.",
    "data": {
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Alert*: Test notification"
          }
        }
      ]
    }
  }' | jq .
echo ""

# 3. 發送 Push 通知
echo "3. Sending push notification..."
curl -s -X POST "$API_URL/api/v1/notifications" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "device-token-123",
    "channel": "push",
    "title": "New Message",
    "body": "You have a new message.",
    "data": {
      "action": "open_message",
      "messageId": "msg-123"
    }
  }' | jq .
echo ""

# 4. 批量發送通知
echo "4. Sending batch notifications..."
curl -s -X POST "$API_URL/api/v1/notifications/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notifications": [
      {
        "recipient": "user1@example.com",
        "channel": "email",
        "title": "Batch Test 1",
        "body": "First batch notification"
      },
      {
        "recipient": "user2@example.com",
        "channel": "email",
        "title": "Batch Test 2",
        "body": "Second batch notification"
      }
    ]
  }' | jq .
echo ""

# 5. 查看通知狀態
echo "5. Checking notification status..."
NOTIFICATION_ID="notif-123"  # 使用實際的通知 ID
curl -s -X GET "$API_URL/api/v1/notifications/$NOTIFICATION_ID/status" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# 6. 列出通知歷史
echo "6. Listing notification history..."
curl -s -X GET "$API_URL/api/v1/notifications?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

echo "=== Examples Complete ==="
