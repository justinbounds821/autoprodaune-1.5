"""
Monitoring Alerts - Alert management and monitoring
"""

import time
import logging
from typing import List
from datetime import datetime
from .models import Metric, Alert, AlertLevel

logger = logging.getLogger(__name__)


class AlertManager:
    """Manager pentru alerte"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = {
            "system_cpu_usage": {"warning": 80, "critical": 90},
            "system_memory_usage": {"warning": 85, "critical": 95},
            "system_disk_usage": {"warning": 80, "critical": 90},
            "application_error_rate": {"warning": 5, "critical": 10},
            "application_response_time_avg": {"warning": 2, "critical": 5},
            "business_roi_percentage": {"warning": 50, "critical": 25}
        }
    
    def check_alerts(self, metrics: List[Metric]) -> List[Alert]:
        """Verifică alertele pe baza metricilor"""
        new_alerts = []
        
        for metric in metrics:
            if metric.name in self.alert_rules:
                rules = self.alert_rules[metric.name]
                
                # Verifică alerte critice
                if "critical" in rules and metric.value >= rules["critical"]:
                    alert = Alert(
                        id=f"critical_{metric.name}_{int(time.time())}",
                        name=f"Critical {metric.name}",
                        level=AlertLevel.CRITICAL,
                        message=f"{metric.name} is at critical level: {metric.value}",
                        metric_name=metric.name,
                        threshold=rules["critical"],
                        current_value=metric.value,
                        timestamp=datetime.now()
                    )
                    new_alerts.append(alert)
                
                # Verifică alerte warning
                elif "warning" in rules and metric.value >= rules["warning"]:
                    alert = Alert(
                        id=f"warning_{metric.name}_{int(time.time())}",
                        name=f"Warning {metric.name}",
                        level=AlertLevel.WARNING,
                        message=f"{metric.name} is at warning level: {metric.value}",
                        metric_name=metric.name,
                        threshold=rules["warning"],
                        current_value=metric.value,
                        timestamp=datetime.now()
                    )
                    new_alerts.append(alert)
        
        # Adaugă alertele noi
        self.alerts.extend(new_alerts)
        
        # Păstrează doar ultimele 1000 de alerte
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        return new_alerts
    
    def get_active_alerts(self) -> List[Alert]:
        """Returnează alertele active"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def resolve_alert(self, alert_id: str):
        """Rezolvă o alertă"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                break
