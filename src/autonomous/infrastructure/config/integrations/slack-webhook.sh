#!/bin/bash

# Slack Webhook Integration
# 用於發送安全告警到 Slack

set -e

# Configuration
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
ALERT_SEVERITY="${1:-medium}"
ALERT_MESSAGE="${2:-Security alert detected}"
ALERT_DETAILS="${3:-}"
REPOSITORY="${4:-unknown}"

# Color codes based on severity
case "$ALERT_SEVERITY" in
    critical)
        COLOR="#FF0000"  # Red
        EMOJI="🔴"
        ;;
    high)
        COLOR="#FF6600"  # Orange
        EMOJI="🟠"
        ;;
    medium)
        COLOR="#FFCC00"  # Yellow
        EMOJI="🟡"
        ;;
    low)
        COLOR="#00CC00"  # Green
        EMOJI="🟢"
        ;;
    *)
        COLOR="#808080"  # Gray
        EMOJI="⚪"
        ;;
esac

# Check if webhook URL is set
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "Error: SLACK_WEBHOOK_URL environment variable is not set"
    exit 1
fi

# Build Slack message
PAYLOAD=$(cat <<EOF
{
    "username": "Security Bot",
    "icon_emoji": ":shield:",
    "attachments": [
        {
            "color": "$COLOR",
            "title": "$EMOJI Security Alert: $ALERT_SEVERITY",
            "text": "$ALERT_MESSAGE",
            "fields": [
                {
                    "title": "Repository",
                    "value": "$REPOSITORY",
                    "short": true
                },
                {
                    "title": "Severity",
                    "value": "$ALERT_SEVERITY",
                    "short": true
                },
                {
                    "title": "Details",
                    "value": "$ALERT_DETAILS",
                    "short": false
                },
                {
                    "title": "Timestamp",
                    "value": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
                    "short": true
                }
            ],
            "footer": "GitHub Advanced Security",
            "footer_icon": "https://github.githubassets.com/favicons/favicon.png"
        }
    ]
}
EOF
)

# Send to Slack
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    -H 'Content-Type: application/json' \
    -d "$PAYLOAD" \
    "$SLACK_WEBHOOK_URL")

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Successfully sent alert to Slack"
    exit 0
else
    echo "❌ Failed to send alert to Slack (HTTP $HTTP_CODE)"
    exit 1
fi
