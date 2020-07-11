{
  "trigger": {
    "schedule": {
      "interval": "30s"
    }
  },
  "input": {
    "search": {
      "request": {
        "search_type": "query_then_fetch",
        "indices": [],
        "rest_total_hits_as_int": true,
        "body": {
          "size": 0,
          "query": {
            "bool": {
              "filter": [
                {
                  "range": {
                    "@timestamp": {
                      "from": "now-30s",
                      "to": "now"
                    }
                  }
                },
                {
                  "match": {
                    "http.request.method": "POST"
                  }
                },
                {
                  "match": {
                    "http.response.status_code": 400
                  }
                },
                {
                  "match": {
                    "url.original": "/api/auth/"
                  }
                }
              ]
            }
          },
          "aggs": {
            "failed_ip": {
              "terms": {
                "field": "source.ip",
                "min_doc_count": 5
              }
            },
            "count": {
              "cardinality": {
                "field": "source.ip"
              }
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.aggregations.count.value": {
        "gte": 1
      }
    }
  },
  "actions": {
    "my-logging-action": {
      "logging": {
        "level": "info",
        "text": """There are user trying to break in your website
 Buckets : {{ctx.payload.aggregations.failed_ip.buckets}}"""
      }
    },
    "slack_1": {
      "slack": {
        "message": {
          "to": [
            "#alerts"
          ],
          "text": """[Elasticsearch] Invalid Login Watcher
There are users trying to break into your website!

Here is a list of these users:
Users : {{ctx.payload.aggregations.failed_ip.buckets}}"""
        }
      }
    }
  }
}
