#!/bin/bash

# Elasticsearch Integration Configuration Script
# 用於設定 GitHub Security 日誌收集到 Elasticsearch

set -e

# Configuration variables
ELASTICSEARCH_HOST="${ELASTICSEARCH_HOST:-localhost}"
ELASTICSEARCH_PORT="${ELASTICSEARCH_PORT:-9200}"
ELASTICSEARCH_SCHEME="${ELASTICSEARCH_SCHEME:-http}"
ELASTICSEARCH_USER="${ELASTICSEARCH_USER:-elastic}"
ELASTICSEARCH_PASSWORD="${ELASTICSEARCH_PASSWORD}"
INDEX_NAME="${INDEX_NAME:-github-security-logs}"

echo "=========================================="
echo "Elasticsearch Configuration for GitHub Security"
echo "=========================================="
echo "Host: $ELASTICSEARCH_HOST"
echo "Port: $ELASTICSEARCH_PORT"
echo "Scheme: $ELASTICSEARCH_SCHEME"
echo "Index: $INDEX_NAME"
echo "=========================================="

# Construct Elasticsearch URL
if [ -n "$ELASTICSEARCH_USER" ] && [ -n "$ELASTICSEARCH_PASSWORD" ]; then
  ES_URL="${ELASTICSEARCH_SCHEME}://${ELASTICSEARCH_USER}:${ELASTICSEARCH_PASSWORD}@${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}"
else
  ES_URL="${ELASTICSEARCH_SCHEME}://${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}"
fi

# Check Elasticsearch connectivity
echo "Checking Elasticsearch connectivity..."
if curl -s -f "${ES_URL}/_cluster/health" > /dev/null 2>&1; then
  echo "✅ Successfully connected to Elasticsearch"
else
  echo "❌ Failed to connect to Elasticsearch at ${ES_URL}"
  echo "Please check your Elasticsearch configuration and credentials"
  exit 1
fi

# Create index with mapping
echo "Creating index with mapping..."
curl -X PUT "${ES_URL}/${INDEX_NAME}" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index": {
        "max_result_window": 10000,
        "refresh_interval": "5s"
      }
    },
    "mappings": {
      "properties": {
        "timestamp": {
          "type": "date",
          "format": "strict_date_optional_time||epoch_millis"
        },
        "event_type": {
          "type": "keyword"
        },
        "severity": {
          "type": "keyword"
        },
        "repository": {
          "type": "keyword"
        },
        "organization": {
          "type": "keyword"
        },
        "alert_id": {
          "type": "keyword"
        },
        "alert_type": {
          "type": "keyword"
        },
        "rule_id": {
          "type": "keyword"
        },
        "rule_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "state": {
          "type": "keyword"
        },
        "created_at": {
          "type": "date"
        },
        "updated_at": {
          "type": "date"
        },
        "dismissed_at": {
          "type": "date"
        },
        "fixed_at": {
          "type": "date"
        },
        "dismissed_by": {
          "type": "keyword"
        },
        "dismissed_reason": {
          "type": "keyword"
        },
        "tool": {
          "type": "keyword"
        },
        "location": {
          "type": "object",
          "properties": {
            "path": {
              "type": "keyword"
            },
            "start_line": {
              "type": "integer"
            },
            "end_line": {
              "type": "integer"
            }
          }
        },
        "details": {
          "type": "text"
        },
        "message": {
          "type": "text"
        },
        "url": {
          "type": "keyword"
        },
        "html_url": {
          "type": "keyword"
        },
        "user": {
          "type": "keyword"
        },
        "action": {
          "type": "keyword"
        }
      }
    }
  }'

echo ""
echo "✅ Index created successfully"

# Create index lifecycle policy
echo "Creating index lifecycle policy..."
curl -X PUT "${ES_URL}/_ilm/policy/${INDEX_NAME}-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": {
      "phases": {
        "hot": {
          "min_age": "0ms",
          "actions": {
            "rollover": {
              "max_size": "50gb",
              "max_age": "7d"
            },
            "set_priority": {
              "priority": 100
            }
          }
        },
        "warm": {
          "min_age": "7d",
          "actions": {
            "set_priority": {
              "priority": 50
            },
            "forcemerge": {
              "max_num_segments": 1
            }
          }
        },
        "cold": {
          "min_age": "30d",
          "actions": {
            "set_priority": {
              "priority": 0
            }
          }
        },
        "delete": {
          "min_age": "90d",
          "actions": {
            "delete": {}
          }
        }
      }
    }
  }'

echo ""
echo "✅ Index lifecycle policy created"

# Create index template
echo "Creating index template..."
curl -X PUT "${ES_URL}/_index_template/${INDEX_NAME}-template" \
  -H "Content-Type: application/json" \
  -d "{
    \"index_patterns\": [\"${INDEX_NAME}-*\"],
    \"template\": {
      \"settings\": {
        \"number_of_shards\": 3,
        \"number_of_replicas\": 1,
        \"index.lifecycle.name\": \"${INDEX_NAME}-policy\",
        \"index.lifecycle.rollover_alias\": \"${INDEX_NAME}\"
      }
    }
  }"

echo ""
echo "✅ Index template created"

# Create saved searches and visualizations
echo "Creating Kibana saved searches..."
curl -X POST "${ES_URL}/.kibana/_doc/search:github-critical-alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "search",
    "search": {
      "title": "Critical Security Alerts",
      "description": "All critical severity security alerts",
      "hits": 0,
      "columns": ["timestamp", "repository", "alert_type", "rule_name", "severity"],
      "sort": [["timestamp", "desc"]],
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"query\":{\"match\":{\"severity\":\"critical\"}},\"filter\":[],\"indexRefName\":\"kibanaSavedObjectMeta.searchSourceJSON.index\"}"
      }
    }
  }'

echo ""
echo "=========================================="
echo "✅ Elasticsearch configuration completed successfully"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure webhook to send GitHub security events to Elasticsearch"
echo "2. Set up Kibana dashboards for visualization"
echo "3. Configure alerts for critical security events"
echo "4. Test the integration by triggering a security alert"
echo ""
echo "Index URL: ${ES_URL}/${INDEX_NAME}"
echo "=========================================="
