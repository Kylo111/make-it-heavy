#!/usr/bin/env python3
"""
Real-time cost monitoring and budget alert system for multi-agent execution.
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CostAlert:
    """Cost alert configuration."""
    threshold: float
    message: str
    alert_type: str  # 'warning', 'critical', 'budget_exceeded'
    triggered: bool = False
    trigger_time: Optional[datetime] = None


@dataclass
class AgentCostEntry:
    """Individual cost entry for an agent."""
    agent_id: int
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: datetime


class CostMonitor:
    """Real-time cost monitoring system for multi-agent execution."""
    
    def __init__(self, budget_limit: Optional[float] = None, alert_callback: Optional[Callable] = None):
        self.budget_limit = budget_limit
        self.alert_callback = alert_callback
        
        # Cost tracking
        self.cost_entries: List[AgentCostEntry] = []
        self.total_cost = 0.0
        self.agent_costs: Dict[int, float] = {}
        
        # Alerts
        self.alerts: List[CostAlert] = []
        self._setup_default_alerts()
        
        # Monitoring
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # Statistics
        self.session_start_time = datetime.now()
        self.peak_cost_rate = 0.0  # Cost per minute
        self.last_cost_check = datetime.now()
    
    def _setup_default_alerts(self):
        """Setup default cost alerts."""
        if self.budget_limit:
            self.alerts = [
                CostAlert(
                    threshold=self.budget_limit * 0.5,
                    message=f"Warning: 50% of budget used (${self.budget_limit * 0.5:.4f})",
                    alert_type='warning'
                ),
                CostAlert(
                    threshold=self.budget_limit * 0.8,
                    message=f"Critical: 80% of budget used (${self.budget_limit * 0.8:.4f})",
                    alert_type='critical'
                ),
                CostAlert(
                    threshold=self.budget_limit,
                    message=f"Budget exceeded! Limit: ${self.budget_limit:.4f}",
                    alert_type='budget_exceeded'
                )
            ]
    
    def add_custom_alert(self, threshold: float, message: str, alert_type: str = 'custom'):
        """Add a custom cost alert."""
        with self.lock:
            self.alerts.append(CostAlert(
                threshold=threshold,
                message=message,
                alert_type=alert_type
            ))
    
    def record_agent_cost(self, agent_id: int, model: str, input_tokens: int, output_tokens: int, cost: float):
        """Record cost for an agent execution."""
        with self.lock:
            # Create cost entry
            entry = AgentCostEntry(
                agent_id=agent_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                timestamp=datetime.now()
            )
            
            self.cost_entries.append(entry)
            self.total_cost += cost
            
            # Update agent-specific costs
            if agent_id not in self.agent_costs:
                self.agent_costs[agent_id] = 0.0
            self.agent_costs[agent_id] += cost
            
            # Check alerts
            self._check_alerts()
            
            # Update cost rate statistics
            self._update_cost_rate()
    
    def _check_alerts(self):
        """Check if any cost alerts should be triggered."""
        for alert in self.alerts:
            if not alert.triggered and self.total_cost >= alert.threshold:
                alert.triggered = True
                alert.trigger_time = datetime.now()
                
                # Call alert callback if provided
                if self.alert_callback:
                    try:
                        self.alert_callback(alert)
                    except Exception as e:
                        print(f"Alert callback failed: {e}")
                else:
                    # Default alert handling
                    print(f"💰 COST ALERT [{alert.alert_type.upper()}]: {alert.message}")
    
    def _update_cost_rate(self):
        """Update cost rate statistics."""
        now = datetime.now()
        time_diff = (now - self.session_start_time).total_seconds() / 60.0  # minutes
        
        if time_diff > 0:
            current_rate = self.total_cost / time_diff
            if current_rate > self.peak_cost_rate:
                self.peak_cost_rate = current_rate
    
    def start_monitoring(self, check_interval: float = 5.0):
        """Start real-time monitoring thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(check_interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitoring_loop(self, check_interval: float):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                with self.lock:
                    # Update statistics
                    self._update_cost_rate()
                    
                    # Check for budget warnings
                    if self.budget_limit and self.total_cost > 0:
                        usage_percentage = (self.total_cost / self.budget_limit) * 100
                        
                        # Log periodic updates
                        if usage_percentage > 25:  # Only log if significant usage
                            print(f"💰 Cost Update: ${self.total_cost:.6f} ({usage_percentage:.1f}% of budget)")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(check_interval)
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost summary."""
        with self.lock:
            session_duration = (datetime.now() - self.session_start_time).total_seconds() / 60.0
            
            # Calculate model usage statistics
            model_costs = {}
            model_usage = {}
            
            for entry in self.cost_entries:
                if entry.model not in model_costs:
                    model_costs[entry.model] = 0.0
                    model_usage[entry.model] = {'calls': 0, 'input_tokens': 0, 'output_tokens': 0}
                
                model_costs[entry.model] += entry.cost
                model_usage[entry.model]['calls'] += 1
                model_usage[entry.model]['input_tokens'] += entry.input_tokens
                model_usage[entry.model]['output_tokens'] += entry.output_tokens
            
            # Calculate projected costs
            projected_hourly_cost = 0.0
            if session_duration > 0:
                cost_per_minute = self.total_cost / session_duration
                projected_hourly_cost = cost_per_minute * 60
            
            return {
                'total_cost': self.total_cost,
                'agent_costs': self.agent_costs.copy(),
                'model_costs': model_costs,
                'model_usage': model_usage,
                'session_duration_minutes': session_duration,
                'cost_per_minute': self.total_cost / session_duration if session_duration > 0 else 0.0,
                'projected_hourly_cost': projected_hourly_cost,
                'peak_cost_rate': self.peak_cost_rate,
                'budget_limit': self.budget_limit,
                'budget_remaining': self.budget_limit - self.total_cost if self.budget_limit else None,
                'budget_usage_percentage': (self.total_cost / self.budget_limit * 100) if self.budget_limit else None,
                'alerts_triggered': [alert for alert in self.alerts if alert.triggered],
                'total_entries': len(self.cost_entries)
            }
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics for display."""
        with self.lock:
            recent_entries = [e for e in self.cost_entries if (datetime.now() - e.timestamp).total_seconds() < 60]
            recent_cost = sum(e.cost for e in recent_entries)
            
            return {
                'current_total': self.total_cost,
                'recent_cost_1min': recent_cost,
                'active_agents': len(set(e.agent_id for e in recent_entries)),
                'cost_rate_per_minute': self.peak_cost_rate,
                'budget_status': 'OK' if not self.budget_limit or self.total_cost < self.budget_limit * 0.8 else 'WARNING'
            }
    
    def export_cost_report(self, include_detailed_entries: bool = False) -> Dict[str, Any]:
        """Export detailed cost report."""
        summary = self.get_cost_summary()
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'session_summary': summary,
            'configuration': {
                'budget_limit': self.budget_limit,
                'alerts_configured': len(self.alerts)
            }
        }
        
        if include_detailed_entries:
            report['detailed_entries'] = [
                {
                    'agent_id': entry.agent_id,
                    'model': entry.model,
                    'input_tokens': entry.input_tokens,
                    'output_tokens': entry.output_tokens,
                    'cost': entry.cost,
                    'timestamp': entry.timestamp.isoformat()
                }
                for entry in self.cost_entries
            ]
        
        return report
    
    def reset_session(self):
        """Reset all cost tracking for a new session."""
        with self.lock:
            self.cost_entries.clear()
            self.total_cost = 0.0
            self.agent_costs.clear()
            self.session_start_time = datetime.now()
            self.peak_cost_rate = 0.0
            
            # Reset alert triggers
            for alert in self.alerts:
                alert.triggered = False
                alert.trigger_time = None
    
    def set_budget_limit(self, new_limit: float):
        """Update budget limit and reconfigure alerts."""
        with self.lock:
            self.budget_limit = new_limit
            self.alerts.clear()
            self._setup_default_alerts()
    
    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()


class BudgetManager:
    """Higher-level budget management with multiple cost monitors."""
    
    def __init__(self):
        self.monitors: Dict[str, CostMonitor] = {}
        self.global_budget: Optional[float] = None
        self.global_cost = 0.0
    
    def create_monitor(self, name: str, budget_limit: Optional[float] = None, alert_callback: Optional[Callable] = None) -> CostMonitor:
        """Create a new cost monitor."""
        monitor = CostMonitor(budget_limit, alert_callback)
        self.monitors[name] = monitor
        return monitor
    
    def get_monitor(self, name: str) -> Optional[CostMonitor]:
        """Get existing cost monitor."""
        return self.monitors.get(name)
    
    def set_global_budget(self, budget: float):
        """Set global budget across all monitors."""
        self.global_budget = budget
    
    def get_global_summary(self) -> Dict[str, Any]:
        """Get summary across all monitors."""
        total_cost = sum(monitor.total_cost for monitor in self.monitors.values())
        
        return {
            'total_cost_all_monitors': total_cost,
            'global_budget': self.global_budget,
            'global_budget_remaining': self.global_budget - total_cost if self.global_budget else None,
            'active_monitors': len(self.monitors),
            'monitor_summaries': {
                name: monitor.get_cost_summary()
                for name, monitor in self.monitors.items()
            }
        }