"""
Helper functions and utilities for the Locust Performance Testing Framework
"""

import os
import json
import csv
import time
import logging
import hashlib
import random
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from contextlib import contextmanager
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.elapsed = self.end_time - (self.start_time or 0.0)
        logger.info(f"{self.name} took {self.elapsed:.4f} seconds")
    
    def get_elapsed(self) -> float:
        """Get elapsed time in seconds"""
        return self.elapsed if self.elapsed is not None else 0.0

class ResponseValidator:
    """Response validation utilities"""
    
    @staticmethod
    def validate_status_code(response: Any, expected_status: int) -> bool:
        """Validate HTTP status code"""
        if not response:
            return False
        return response.status_code == expected_status
    
    @staticmethod
    def validate_response_time(response: Any, max_time: float) -> bool:
        """Validate response time"""
        if not response:
            return False
        return response.elapsed.total_seconds() <= max_time
    
    @staticmethod
    def validate_content_type(response: Any, expected_type: str) -> bool:
        """Validate content type"""
        if not response:
            return False
        content_type = response.headers.get('content-type', '')
        return expected_type in content_type
    
    @staticmethod
    def validate_json_schema(response: Any, schema: Dict[str, Any]) -> bool:
        """Validate JSON response against schema"""
        if not response:
            return False
        
        try:
            json_data = response.json()
            return ResponseValidator._validate_schema(json_data, schema)
        except (json.JSONDecodeError, AttributeError):
            return False
    
    @staticmethod
    def _validate_schema(data: Any, schema: Dict[str, Any]) -> bool:
        """Validate data against schema"""
        if not isinstance(data, dict):
            return False
        
        for key, expected_type in schema.items():
            if key not in data:
                return False
            
            if not isinstance(data[key], expected_type):
                return False
        
        return True
    
    @staticmethod
    def validate_response_size(response: Any, max_size: int) -> bool:
        """Validate response size"""
        if not response:
            return False
        
        content_length = response.headers.get('content-length')
        if content_length:
            return int(content_length) <= max_size
        else:
            return len(response.content) <= max_size
    
    @staticmethod
    def validate_headers(response: Any, expected_headers: Dict[str, str]) -> bool:
        """Validate response headers"""
        if not response:
            return False
        
        for header, expected_value in expected_headers.items():
            if header not in response.headers:
                return False
            if response.headers[header] != expected_value:
                return False
        
        return True

class DataManager:
    """Data management utilities"""
    
    @staticmethod
    def load_json_file(filepath: str) -> Dict[str, Any]:
        """Load JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"JSON file not found: {filepath}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file: {filepath}")
            return {}
    
    @staticmethod
    def save_json_file(data: Dict[str, Any], filepath: str) -> bool:
        """Save data to JSON file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON file: {e}")
            return False
    
    @staticmethod
    def load_csv_file(filepath: str) -> List[Dict[str, Any]]:
        """Load CSV file"""
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            logger.error(f"CSV file not found: {filepath}")
            return []
        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            return []
    
    @staticmethod
    def save_csv_file(data: List[Dict[str, Any]], filepath: str) -> bool:
        """Save data to CSV file"""
        if not data:
            return False
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            logger.error(f"Failed to save CSV file: {e}")
            return False
    
    @staticmethod
    def load_env_file(filepath: str) -> Dict[str, str]:
        """Load environment variables from file"""
        env_vars = {}
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        except FileNotFoundError:
            logger.warning(f"Environment file not found: {filepath}")
        except Exception as e:
            logger.error(f"Failed to load environment file: {e}")
        
        return env_vars

class URLHelper:
    """URL manipulation utilities"""
    
    @staticmethod
    def build_url(base_url: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build URL with endpoint and parameters"""
        url = urljoin(base_url, endpoint)
        
        if params:
            param_strings = []
            for key, value in params.items():
                if isinstance(value, (list, tuple)):
                    for item in value:
                        param_strings.append(f"{key}={item}")
                else:
                    param_strings.append(f"{key}={value}")
            
            if param_strings:
                url += "?" + "&".join(param_strings)
        
        return url
    
    @staticmethod
    def parse_url(url: str) -> Dict[str, Any]:
        """Parse URL components"""
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': parse_qs(parsed.query),
            'fragment': parsed.fragment
        }
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc

class StringHelper:
    """String manipulation utilities"""
    
    @staticmethod
    def generate_random_string(length: int = 10, chars: str = None) -> str:
        """Generate random string"""
        if chars is None:
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_hash(text: str, algorithm: str = 'md5') -> str:
        """Generate hash of text"""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for filesystem"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
        """Truncate string to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_bytes(bytes_count: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    @staticmethod
    def mask_sensitive_data(text: str, mask_char: str = '*') -> str:
        """Mask sensitive data in text"""
        # Common patterns for sensitive data
        patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # Phone
        ]
        
        import re
        masked_text = text
        for pattern in patterns:
            matches = re.findall(pattern, masked_text)
            for match in matches:
                masked_text = masked_text.replace(match, mask_char * len(match))
        
        return masked_text

class MathHelper:
    """Mathematical utilities"""
    
    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index == int(index):
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict[str, float]:
        """Calculate basic statistics"""
        if not values:
            return {}
        
        mode_value = statistics.mode(values) if len(set(values)) < len(values) else 0.0
        
        return {
            'count': float(len(values)),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'mode': mode_value,
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'variance': statistics.variance(values) if len(values) > 1 else 0.0,
            'p50': MathHelper.calculate_percentile(values, 50),
            'p90': MathHelper.calculate_percentile(values, 90),
            'p95': MathHelper.calculate_percentile(values, 95),
            'p99': MathHelper.calculate_percentile(values, 99)
        }
    
    @staticmethod
    def calculate_error_rate(total_requests: int, error_count: int) -> float:
        """Calculate error rate percentage"""
        if total_requests == 0:
            return 0.0
        return (error_count / total_requests) * 100.0
    
    @staticmethod
    def calculate_throughput(total_requests: int, duration: float) -> float:
        """Calculate throughput (requests per second)"""
        if duration == 0:
            return 0.0
        return total_requests / duration
    
    @staticmethod
    def calculate_response_time_stats(response_times: List[float]) -> Dict[str, float]:
        """Calculate response time statistics"""
        if not response_times:
            return {}
        
        stats = MathHelper.calculate_statistics(response_times)
        return {
            'avg_response_time': stats['mean'],
            'min_response_time': stats['min'],
            'max_response_time': stats['max'],
            'median_response_time': stats['median'],
            'p95_response_time': stats['p95'],
            'p99_response_time': stats['p99']
        }

class DateTimeHelper:
    """Date and time utilities"""
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp as string"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def get_current_iso_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.2f} hours"
    
    @staticmethod
    def parse_timestamp(timestamp_str: str, format: str = '%Y-%m-%d %H:%M:%S') -> datetime:
        """Parse timestamp string"""
        return datetime.strptime(timestamp_str, format)
    
    @staticmethod
    def add_time_delta(timestamp: datetime, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> datetime:
        """Add time delta to timestamp"""
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return timestamp + delta
    
    @staticmethod
    def time_difference(start_time: datetime, end_time: datetime) -> float:
        """Calculate time difference in seconds"""
        return (end_time - start_time).total_seconds()

class LogHelper:
    """Logging utilities"""
    
    @staticmethod
    def setup_logger(name: str, level: str = 'INFO', log_file: Optional[str] = None) -> logging.Logger:
        """Setup logger with specified configuration"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def log_request_response(logger: logging.Logger, method: str, url: str, 
                           status_code: int, response_time: float, 
                           request_data: Optional[Dict[str, Any]] = None,
                           response_data: Optional[Dict[str, Any]] = None):
        """Log request and response details"""
        log_data = {
            'method': method,
            'url': url,
            'status_code': status_code,
            'response_time': response_time
        }
        
        if request_data:
            log_data['request_data'] = request_data
        
        if response_data:
            log_data['response_data'] = response_data
        
        logger.info(f"Request: {json.dumps(log_data, default=str)}")

class RetryHelper:
    """Retry mechanism utilities"""
    
    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3, base_delay: float = 1.0, 
                          max_delay: float = 60.0, exceptions: tuple = (Exception,)):
        """Retry function with exponential backoff"""
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise e
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
        
        return wrapper
    
    @staticmethod
    def retry_with_jitter(func: Callable, max_retries: int = 3, base_delay: float = 1.0, 
                         jitter_factor: float = 0.1, exceptions: tuple = (Exception,)):
        """Retry function with jitter"""
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise e
                    
                    jitter = random.uniform(-jitter_factor, jitter_factor)
                    delay = base_delay * (2 ** attempt) * (1 + jitter)
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
        
        return wrapper

class ConfigHelper:
    """Configuration utilities"""
    
    @staticmethod
    def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configuration dictionaries"""
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = ConfigHelper.merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    @staticmethod
    def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    @staticmethod
    def validate_config(config: Dict[str, Any], required_keys: List[str]) -> bool:
        """Validate configuration has required keys"""
        for key in required_keys:
            if ConfigHelper.get_config_value(config, key) is None:
                logger.error(f"Missing required configuration key: {key}")
                return False
        
        return True

# Context managers
@contextmanager
def suppress_exceptions(*exceptions):
    """Context manager to suppress specific exceptions"""
    try:
        yield
    except exceptions:
        pass

@contextmanager
def temporary_file(content: str, suffix: str = '.tmp'):
    """Context manager for temporary file"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        yield temp_path
    finally:
        os.unlink(temp_path)

# Decorators
def measure_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def log_errors(func):
    """Decorator to log function errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

def rate_limit(calls_per_second: float):
    """Decorator to rate limit function calls"""
    def decorator(func):
        last_called = [0.0]
        
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator

# Utility functions
def get_random_user_agent() -> str:
    """Get random user agent string"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]
    return random.choice(user_agents)

def wait_for_condition(condition: Callable[[], bool], timeout: float = 30.0, 
                      poll_interval: float = 0.5, error_message: str = "Condition not met") -> bool:
    """Wait for a condition to be true within timeout"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(poll_interval)
    
    logger.error(f"{error_message} (timeout: {timeout}s)")
    return False

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    return numerator / denominator if denominator != 0 else default

def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

def ensure_directory(directory: str) -> bool:
    """Ensure directory exists"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError:
        return False

def cleanup_old_files(directory: str, max_age_days: int = 7) -> int:
    """Clean up old files in directory"""
    if not os.path.exists(directory):
        return 0
    
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    deleted_count = 0
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
            try:
                os.remove(filepath)
                deleted_count += 1
            except OSError:
                pass
    
    return deleted_count 