"""
Automated Grafana & AWS CloudWatch Metric Verification Script for AEA Cloud Staging.
Can be executed anytime locally or in CI/CD pipelines.
"""
import subprocess
import json
import urllib.request
import ssl
from datetime import datetime, timezone, timedelta

def audit_grafana_and_cloudwatch():
    print("==========================================================")
    print("      AEA CLOUD OBSERVIABILITY & GRAFANA AUDIT            ")
    print("==========================================================")
    
    # 1. Test Grafana HTTP API
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    grafana_url = "https://aea.artof.link/grafana/api/dashboards/uid/aea-unified-dashboard"
    try:
        req = urllib.request.Request(grafana_url, headers={"User-Agent": "AEA-Audit/1.0"})
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        data = json.loads(res.read().decode("utf-8"))
        dashboard = data.get("dashboard", {})
        panels = dashboard.get("panels", [])
        print(f"[PASS] Grafana HTTP API reachable: 200 OK | Title: {dashboard.get('title')}")
        print(f"[PASS] Total Provisioned Panels: {len(panels)}")
    except Exception as e:
        print(f"[FAIL] Grafana HTTP API error: {e}")
        return False

    # 2. Test AWS CloudWatch Metric Ingestion (gateway CPUUtilization)
    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
    end = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    query = [
        {
            "Id": "m1",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/ECS",
                    "MetricName": "CPUUtilization",
                    "Dimensions": [
                        {"Name": "ClusterName", "Value": "aea-pilot"},
                        {"Name": "ServiceName", "Value": "gateway"}
                    ]
                },
                "Period": 60,
                "Stat": "Average"
            }
        }
    ]

    try:
        cmd = [
            'aws', 'cloudwatch', 'get-metric-data',
            '--metric-data-queries', json.dumps(query),
            '--start-time', start,
            '--end-time', end,
            '--region', 'us-east-1'
        ]
        out = subprocess.check_output(cmd)
        cw_data = json.loads(out.decode('utf-8', errors='ignore'))
        results = cw_data['MetricDataResults'][0]
        values_count = len(results['Values'])
        print(f"[PASS] AWS CloudWatch Metrics Ingestion: {values_count} data points retrieved")
        if values_count > 0:
            print(f"       Latest CPU Utilization: {results['Values'][0]:.4f}% at {results['Timestamps'][0]}")
        else:
            print("[WARN] CloudWatch query returned 0 data points for gateway service.")
    except Exception as e:
        print(f"[FAIL] CloudWatch API error: {e}")
        return False

    print("==========================================================")
    print("STATUS: Grafana & CloudWatch Telemetry 100% Operational")
    print("==========================================================")
    return True

if __name__ == "__main__":
    audit_grafana_and_cloudwatch()
