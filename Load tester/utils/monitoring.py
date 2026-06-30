"""
Monitoring utilities for the Locust Performance Testing Framework
"""

import time
import json
import threading
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
from datetime import datetime
from utils.helpers import MathHelper, DateTimeHelper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """Metric data structure"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp,
            'tags': self.tags
        }

@dataclass
class RequestMetric:
    """Request metric data structure"""
    method: str
    endpoint: str
    status_code: int
    response_time: float
    response_size: int
    timestamp: float
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'method': self.method,
            'endpoint': self.endpoint,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'response_size': self.response_size,
            'timestamp': self.timestamp,
            'error_message': self.error_message
        }

@dataclass
class UserMetric:
    """User metric data structure"""
    user_id: str
    user_class: str
    total_requests: int
    total_errors: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    start_time: float
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'user_class': self.user_class,
            'total_requests': self.total_requests,
            'total_errors': self.total_errors,
            'avg_response_time': self.avg_response_time,
            'min_response_time': self.min_response_time,
            'max_response_time': self.max_response_time,
            'p95_response_time': self.p95_response_time,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

class MetricsCollector:
    """Metrics collector for performance monitoring"""
    
    def __init__(self, window_size: int = 60):
        """Initialize metrics collector"""
        self.window_size = window_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.request_metrics: deque = deque(maxlen=1000)
        self.user_metrics: Dict[str, UserMetric] = {}
        self.custom_metrics: Dict[str, List[MetricData]] = defaultdict(list)
        self._lock = threading.Lock()
        self._start_time = time.time()
        
        # Statistics tracking
        self.total_requests = 0
        self.total_errors = 0
        self.response_times: List[float] = []
        self.error_rates: List[float] = []
        self.throughput_rates: List[float] = []
        
        # Real-time monitoring
        self.monitoring_enabled = True
        self.monitoring_thread = None
        self.monitoring_interval = 10  # seconds
        
    def add_request_metric(self, method: str, endpoint: str, status_code: int, 
                          response_time: float, response_size: int, 
                          error_message: Optional[str] = None):
        """Add request metric"""
        with self._lock:
            timestamp = time.time()
            
            metric = RequestMetric(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_time=response_time,
                response_size=response_size,
                timestamp=timestamp,
                error_message=error_message
            )
            
            self.request_metrics.append(metric)
            self.total_requests += 1
            
            if status_code >= 400:
                self.total_errors += 1
            
            self.response_times.append(response_time)
            
            # Keep only recent response times for performance
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
            
            # Update metrics
            self.metrics['response_time'].append(response_time)
            self.metrics['status_code'].append(status_code)
            self.metrics['response_size'].append(response_size)
            
            # Calculate current error rate
            current_error_rate = self.get_error_rate()
            self.error_rates.append(current_error_rate)
            
            # Calculate current throughput
            current_throughput = self.get_throughput()
            self.throughput_rates.append(current_throughput)
    
    def add_user_metric(self, user_id: str, user_class: str, 
                       total_requests: int, total_errors: int,
                       response_times: List[float], start_time: float,
                       end_time: Optional[float] = None):
        """Add user metric"""
        if not response_times:
            return
        
        with self._lock:
            stats = MathHelper.calculate_statistics(response_times)
            
            user_metric = UserMetric(
                user_id=user_id,
                user_class=user_class,
                total_requests=total_requests,
                total_errors=total_errors,
                avg_response_time=stats.get('mean', 0.0),
                min_response_time=stats.get('min', 0.0),
                max_response_time=stats.get('max', 0.0),
                p95_response_time=stats.get('p95', 0.0),
                start_time=start_time,
                end_time=end_time
            )
            
            self.user_metrics[user_id] = user_metric
    
    def add_custom_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Add custom metric"""
        with self._lock:
            metric = MetricData(
                name=name,
                value=value,
                timestamp=time.time(),
                tags=tags or {}
            )
            
            self.custom_metrics[name].append(metric)
            
            # Keep only recent metrics
            if len(self.custom_metrics[name]) > 100:
                self.custom_metrics[name] = self.custom_metrics[name][-100:]
    
    def get_response_time_stats(self) -> Dict[str, float]:
        """Get response time statistics"""
        if not self.response_times:
            return {}
        
        return MathHelper.calculate_response_time_stats(self.response_times)
    
    def get_error_rate(self) -> float:
        """Get current error rate"""
        if self.total_requests == 0:
            return 0.0
        
        return MathHelper.calculate_error_rate(self.total_requests, self.total_errors)
    
    def get_throughput(self) -> float:
        """Get current throughput (requests per second)"""
        elapsed_time = time.time() - self._start_time
        return MathHelper.calculate_throughput(self.total_requests, elapsed_time)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        with self._lock:
            stats = {
                'total_requests': self.total_requests,
                'total_errors': self.total_errors,
                'error_rate': self.get_error_rate(),
                'throughput': self.get_throughput(),
                'elapsed_time': time.time() - self._start_time,
                'timestamp': time.time()
            }
            
            # Add response time statistics
            response_stats = self.get_response_time_stats()
            stats.update(response_stats)
            
            # Add status code distribution
            if self.metrics['status_code']:
                status_codes = list(self.metrics['status_code'])
                status_distribution = {}
                for code in status_codes:
                    status_distribution[str(code)] = status_distribution.get(str(code), 0) + 1
                stats['status_code_distribution'] = status_distribution
            
            return stats
    
    def get_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by endpoint"""
        endpoint_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'requests': 0,
            'errors': 0,
            'response_times': [],
            'response_sizes': []
        })
        
        with self._lock:
            for metric in self.request_metrics:
                endpoint = f"{metric.method} {metric.endpoint}"
                endpoint_stats[endpoint]['requests'] += 1
                
                if metric.status_code >= 400:
                    endpoint_stats[endpoint]['errors'] += 1
                
                endpoint_stats[endpoint]['response_times'].append(metric.response_time)
                endpoint_stats[endpoint]['response_sizes'].append(metric.response_size)
        
        # Calculate statistics for each endpoint
        result = {}
        for endpoint, data in endpoint_stats.items():
            if data['response_times']:
                response_stats = MathHelper.calculate_response_time_stats(data['response_times'])
                avg_size = statistics.mean(data['response_sizes']) if data['response_sizes'] else 0
                error_rate = MathHelper.calculate_error_rate(data['requests'], data['errors'])
                
                result[endpoint] = {
                    'requests': data['requests'],
                    'errors': data['errors'],
                    'error_rate': error_rate,
                    'avg_response_size': avg_size,
                    **response_stats
                }
        
        return result
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        with self._lock:
            user_stats = {}
            for user_id, metric in self.user_metrics.items():
                user_stats[user_id] = metric.to_dict()
            
            return user_stats
    
    def get_custom_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get custom metrics"""
        with self._lock:
            result = {}
            for name, metrics in self.custom_metrics.items():
                result[name] = [metric.to_dict() for metric in metrics]
            
            return result
    
    def get_time_series_data(self, metric_name: str, duration: int = 300) -> List[Dict[str, Any]]:
        """Get time series data for a metric"""
        current_time = time.time()
        cutoff_time = current_time - duration
        
        time_series = []
        
        if metric_name == 'response_time':
            for metric in self.request_metrics:
                if metric.timestamp >= cutoff_time:
                    time_series.append({
                        'timestamp': metric.timestamp,
                        'value': metric.response_time
                    })
        elif metric_name == 'error_rate':
            # Calculate error rate over time windows
            window_size = 60  # 1 minute windows
            for i in range(0, duration, window_size):
                window_start = cutoff_time + i
                window_end = window_start + window_size
                
                requests_in_window = sum(1 for m in self.request_metrics 
                                       if window_start <= m.timestamp < window_end)
                errors_in_window = sum(1 for m in self.request_metrics 
                                     if window_start <= m.timestamp < window_end and m.status_code >= 400)
                
                error_rate = MathHelper.calculate_error_rate(requests_in_window, errors_in_window)
                
                time_series.append({
                    'timestamp': window_start,
                    'value': error_rate
                })
        
        return time_series
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format"""
        data = {
            'test_summary': self.get_current_stats(),
            'endpoint_stats': self.get_endpoint_stats(),
            'user_stats': self.get_user_stats(),
            'custom_metrics': self.get_custom_metrics(),
            'export_timestamp': time.time()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            # Export as CSV (simplified)
            csv_lines = []
            csv_lines.append('timestamp,metric,value')
            
            for metric in self.request_metrics:
                csv_lines.append(f"{metric.timestamp},response_time,{metric.response_time}")
                csv_lines.append(f"{metric.timestamp},status_code,{metric.status_code}")
                csv_lines.append(f"{metric.timestamp},response_size,{metric.response_size}")
            
            return '\n'.join(csv_lines)
        else:
            return json.dumps(data, indent=2, default=str)
    
    def start_monitoring(self, callback: Optional[Callable] = None):
        """Start real-time monitoring"""
        if not self.monitoring_enabled:
            return
        
        def monitor():
            while self.monitoring_enabled:
                stats = self.get_current_stats()
                
                # Log current stats
                logger.info(f"Current stats: {stats}")
                
                # Call callback if provided
                if callback:
                    callback(stats)
                
                time.sleep(self.monitoring_interval)
        
        self.monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_enabled = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self._lock:
            self.metrics.clear()
            self.request_metrics.clear()
            self.user_metrics.clear()
            self.custom_metrics.clear()
            self.total_requests = 0
            self.total_errors = 0
            self.response_times.clear()
            self.error_rates.clear()
            self.throughput_rates.clear()
            self._start_time = time.time()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status based on thresholds"""
        stats = self.get_current_stats()
        
        # Define thresholds (these can be configurable)
        thresholds = {
            'error_rate_threshold': 5.0,  # 5%
            'response_time_threshold': 1000.0,  # 1 second
            'throughput_threshold': 10.0  # 10 requests per second
        }
        
        health = {
            'overall_health': 'healthy',
            'checks': {},
            'timestamp': time.time()
        }
        
        # Check error rate
        error_rate = stats.get('error_rate', 0.0)
        if error_rate > thresholds['error_rate_threshold']:
            health['checks']['error_rate'] = 'unhealthy'
            health['overall_health'] = 'unhealthy'
        else:
            health['checks']['error_rate'] = 'healthy'
        
        # Check response time
        avg_response_time = stats.get('avg_response_time', 0.0)
        if avg_response_time > thresholds['response_time_threshold']:
            health['checks']['response_time'] = 'unhealthy'
            health['overall_health'] = 'unhealthy'
        else:
            health['checks']['response_time'] = 'healthy'
        
        # Check throughput
        throughput = stats.get('throughput', 0.0)
        if throughput < thresholds['throughput_threshold']:
            health['checks']['throughput'] = 'degraded'
            if health['overall_health'] == 'healthy':
                health['overall_health'] = 'degraded'
        else:
            health['checks']['throughput'] = 'healthy'
        
        return health

class AlertManager:
    """Alert manager for performance monitoring"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alerts: List[Dict[str, Any]] = []
        self.alert_handlers: List[Callable] = []
        self.alert_thresholds = {
            'error_rate': 5.0,
            'response_time': 1000.0,
            'throughput': 10.0
        }
        self.alert_cooldown = 60  # seconds
        self.last_alert_time = {}
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler"""
        self.alert_handlers.append(handler)
    
    def set_threshold(self, metric: str, threshold: float):
        """Set alert threshold"""
        self.alert_thresholds[metric] = threshold
    
    def check_alerts(self):
        """Check for alert conditions"""
        current_time = time.time()
        stats = self.metrics_collector.get_current_stats()
        
        # Check error rate
        error_rate = stats.get('error_rate', 0.0)
        if error_rate > self.alert_thresholds['error_rate']:
            self._trigger_alert('error_rate', error_rate, current_time)
        
        # Check response time
        avg_response_time = stats.get('avg_response_time', 0.0)
        if avg_response_time > self.alert_thresholds['response_time']:
            self._trigger_alert('response_time', avg_response_time, current_time)
        
        # Check throughput
        throughput = stats.get('throughput', 0.0)
        if throughput < self.alert_thresholds['throughput']:
            self._trigger_alert('throughput', throughput, current_time)
    
    def _trigger_alert(self, metric: str, value: float, timestamp: float):
        """Trigger alert"""
        # Check cooldown
        if metric in self.last_alert_time:
            if timestamp - self.last_alert_time[metric] < self.alert_cooldown:
                return
        
        self.last_alert_time[metric] = timestamp
        
        alert = {
            'metric': metric,
            'value': value,
            'threshold': self.alert_thresholds[metric],
            'timestamp': timestamp,
            'message': f"Alert: {metric} = {value} exceeded threshold {self.alert_thresholds[metric]}"
        }
        
        self.alerts.append(alert)
        
        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
        
        logger.warning(alert['message'])
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all alerts"""
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.last_alert_time.clear()

class PerformanceMonitor:
    """Main performance monitoring class"""
    
    def __init__(self, window_size: int = 60):
        self.metrics_collector = MetricsCollector(window_size)
        self.alert_manager = AlertManager(self.metrics_collector)
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Setup default alert handlers
        self.alert_manager.add_alert_handler(self._log_alert)
    
    def _log_alert(self, alert: Dict[str, Any]):
        """Default alert handler - log to console"""
        logger.warning(f"ALERT: {alert['message']}")
    
    def start_monitoring(self, alert_check_interval: int = 30):
        """Start performance monitoring"""
        self.monitoring_active = True
        
        # Start metrics collection monitoring
        self.metrics_collector.start_monitoring()
        
        # Start alert checking
        def alert_monitor():
            while self.monitoring_active:
                self.alert_manager.check_alerts()
                time.sleep(alert_check_interval)
        
        self.monitor_thread = threading.Thread(target=alert_monitor, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        self.metrics_collector.stop_monitoring()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        logger.info("Performance monitoring stopped")
    
    def record_request(self, method: str, endpoint: str, status_code: int, 
                      response_time: float, response_size: int, 
                      error_message: Optional[str] = None):
        """Record a request metric"""
        self.metrics_collector.add_request_metric(
            method, endpoint, status_code, response_time, 
            response_size, error_message
        )
    
    def record_user_session(self, user_id: str, user_class: str, 
                           total_requests: int, total_errors: int,
                           response_times: List[float], start_time: float,
                           end_time: Optional[float] = None):
        """Record a user session metric"""
        self.metrics_collector.add_user_metric(
            user_id, user_class, total_requests, total_errors,
            response_times, start_time, end_time
        )
    
    def record_custom_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a custom metric"""
        self.metrics_collector.add_custom_metric(name, value, tags)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        return {
            'current_stats': self.metrics_collector.get_current_stats(),
            'endpoint_stats': self.metrics_collector.get_endpoint_stats(),
            'user_stats': self.metrics_collector.get_user_stats(),
            'custom_metrics': self.metrics_collector.get_custom_metrics(),
            'alerts': self.alert_manager.get_alerts(),
            'health_status': self.metrics_collector.get_health_status(),
            'timestamp': time.time()
        }
    
    def export_report(self, format: str = 'json') -> str:
        """Export performance report"""
        return self.metrics_collector.export_metrics(format)
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """Set alert threshold"""
        self.alert_manager.set_threshold(metric, threshold)
    
    def add_alert_handler(self, handler: Callable):
        """Add custom alert handler"""
        self.alert_manager.add_alert_handler(handler)
    
    def reset_monitoring(self):
        """Reset monitoring data"""
        self.metrics_collector.reset_metrics()
        self.alert_manager.clear_alerts()

# Global performance monitor instance
global_monitor = PerformanceMonitor()

# Convenience functions
def start_monitoring(window_size: int = 60, alert_check_interval: int = 30):
    """Start global performance monitoring"""
    global global_monitor
    global_monitor = PerformanceMonitor(window_size)
    global_monitor.start_monitoring(alert_check_interval)

def stop_monitoring():
    """Stop global performance monitoring"""
    global_monitor.stop_monitoring()

def record_request(method: str, endpoint: str, status_code: int, 
                  response_time: float, response_size: int, 
                  error_message: Optional[str] = None):
    """Record request to global monitor"""
    global_monitor.record_request(method, endpoint, status_code, 
                                 response_time, response_size, error_message)

def record_custom_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Record custom metric to global monitor"""
    global_monitor.record_custom_metric(name, value, tags)

def get_current_stats() -> Dict[str, Any]:
    """Get current stats from global monitor"""
    return global_monitor.get_dashboard_data()

def export_report(format: str = 'json') -> str:
    """Export report from global monitor"""
    return global_monitor.export_report(format) 