from datetime import datetime


def get_executive_status():
    """
    Compute a simplified executive health score for ANIS-1
    """

    finance_score = 22
    operations_score = 21
    strategy_score = 23
    risk_score = 20

    empire_health_score = (
        finance_score +
        operations_score +
        strategy_score +
        risk_score
    )

    alerts = [
        {
            "area": "Operations",
            "severity": "Medium",
            "signal": "OEE trending below target",
            "impact": "Potential throughput reduction",
            "recommended_action": "Review maintenance schedule"
        }
    ]

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "empire_health_score": empire_health_score,
        "finance_score": finance_score,
        "operations_score": operations_score,
        "strategy_score": strategy_score,
        "risk_score": risk_score,
        "status": "Stable",
        "watchtower_alerts": alerts
    }