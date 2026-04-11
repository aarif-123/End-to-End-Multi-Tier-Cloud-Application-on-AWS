import boto3

# Initialize CloudWatch client
cw = boto3.client('cloudwatch', region_name='us-east-1')

def setup_monitoring(instance_id='i-0123456789abcdef0'):
    """
    Configures CloudWatch alarms and dashboards for the stack.
    """
    print(f"Configuring monitoring for instance: {instance_id}")

    # 1. CPU Utilization Alarm
    cw.put_metric_alarm(
        AlarmName='HighCPUUtilization',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=300,
        Statistic='Average',
        Threshold=80.0,
        ActionsEnabled=False,
        AlarmDescription='Alarm when CPU exceeds 80%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        Unit='Percent'
    )
    print("CPU Alarm configured (Threshold: 80%)")

    # 2. CloudWatch Dashboard
    dashboard_body = """
    {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        [ "AWS/EC2", "CPUUtilization", "InstanceId", \"""" + \
                        instance_id + """\" ]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "EC2 CPU Utilization"
                }
            }
        ]
    }
    """
    cw.put_dashboard(
        DashboardName='App-Infrastructure-Dashboard',
        DashboardBody=dashboard_body
    )
    print("CloudWatch Dashboard created: 'App-Infrastructure-Dashboard'")

if __name__ == "__main__":
    setup_monitoring()
