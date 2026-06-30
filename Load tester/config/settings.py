"""
Configuration settings for the Locust Performance Testing Framework
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Main settings configuration class"""
    
    # Environment settings
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'dev')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Test execution settings
    DEFAULT_USERS: int = int(os.getenv('DEFAULT_USERS', '10'))
    DEFAULT_SPAWN_RATE: int = int(os.getenv('DEFAULT_SPAWN_RATE', '2'))
    DEFAULT_DURATION: int = int(os.getenv('DEFAULT_DURATION', '60'))
    
    # Target system settings
    TARGET_HOST: str = os.getenv('TARGET_HOST', 'https://jsonplaceholder.typicode.com')
    API_VERSION: str = os.getenv('API_VERSION', 'v1')
    
    # Request settings
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    CONNECTION_TIMEOUT: int = int(os.getenv('CONNECTION_TIMEOUT', '10'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY: float = float(os.getenv('RETRY_DELAY', '1.0'))
    
    # Authentication settings
    AUTH_TYPE: str = os.getenv('AUTH_TYPE', 'none')  # none, basic, bearer, api_key
    AUTH_USERNAME: str = os.getenv('AUTH_USERNAME', '')
    AUTH_PASSWORD: str = os.getenv('AUTH_PASSWORD', '')
    AUTH_TOKEN: str = os.getenv('AUTH_TOKEN', '')
    API_KEY: str = os.getenv('API_KEY', '')
    API_KEY_HEADER: str = os.getenv('API_KEY_HEADER', 'X-API-Key')
    
    # HTTP headers
    DEFAULT_HEADERS: Dict[str, str] = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Locust-Performance-Test/1.0'
    }
    
    # Custom headers from environment
    CUSTOM_HEADERS: Dict[str, str] = {}
    for key, value in os.environ.items():
        if key.startswith('HEADER_'):
            header_name = key[7:].replace('_', '-')
            CUSTOM_HEADERS[header_name] = value
    
    # Combine default and custom headers
    ALL_HEADERS: Dict[str, str] = {**DEFAULT_HEADERS, **CUSTOM_HEADERS}
    
    # Data settings
    DATA_DIRECTORY: str = os.getenv('DATA_DIRECTORY', 'data')
    GENERATE_DYNAMIC_DATA: bool = os.getenv('GENERATE_DYNAMIC_DATA', 'true').lower() == 'true'
    DATA_POOL_SIZE: int = int(os.getenv('DATA_POOL_SIZE', '1000'))
    
    # Test data settings
    USER_DATA_FILE: str = os.path.join(DATA_DIRECTORY, 'users.csv')
    POST_DATA_FILE: str = os.path.join(DATA_DIRECTORY, 'posts.csv')
    COMMENT_DATA_FILE: str = os.path.join(DATA_DIRECTORY, 'comments.csv')
    
    # Reporting settings
    REPORTS_DIRECTORY: str = os.getenv('REPORTS_DIRECTORY', 'reports')
    LOGS_DIRECTORY: str = os.getenv('LOGS_DIRECTORY', 'logs')
    GENERATE_HTML_REPORT: bool = os.getenv('GENERATE_HTML_REPORT', 'true').lower() == 'true'
    GENERATE_CSV_REPORT: bool = os.getenv('GENERATE_CSV_REPORT', 'true').lower() == 'true'
    
    # Logging settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE: str = os.path.join(LOGS_DIRECTORY, 'locust_tests.log')
    
    # Performance thresholds
    RESPONSE_TIME_THRESHOLD: int = int(os.getenv('RESPONSE_TIME_THRESHOLD', '1000'))  # ms
    ERROR_RATE_THRESHOLD: float = float(os.getenv('ERROR_RATE_THRESHOLD', '0.01'))  # 1%
    SUCCESS_RATE_THRESHOLD: float = float(os.getenv('SUCCESS_RATE_THRESHOLD', '0.99'))  # 99%
    
    # Load test settings
    LOAD_TEST_USERS: int = int(os.getenv('LOAD_TEST_USERS', '50'))
    LOAD_TEST_SPAWN_RATE: int = int(os.getenv('LOAD_TEST_SPAWN_RATE', '5'))
    LOAD_TEST_DURATION: int = int(os.getenv('LOAD_TEST_DURATION', '300'))
    
    # Stress test settings
    STRESS_TEST_USERS: int = int(os.getenv('STRESS_TEST_USERS', '100'))
    STRESS_TEST_SPAWN_RATE: int = int(os.getenv('STRESS_TEST_SPAWN_RATE', '10'))
    STRESS_TEST_DURATION: int = int(os.getenv('STRESS_TEST_DURATION', '600'))
    
    # Spike test settings
    SPIKE_TEST_USERS: int = int(os.getenv('SPIKE_TEST_USERS', '200'))
    SPIKE_TEST_SPAWN_RATE: int = int(os.getenv('SPIKE_TEST_SPAWN_RATE', '20'))
    SPIKE_TEST_DURATION: int = int(os.getenv('SPIKE_TEST_DURATION', '300'))
    
    # Endurance test settings
    ENDURANCE_TEST_USERS: int = int(os.getenv('ENDURANCE_TEST_USERS', '25'))
    ENDURANCE_TEST_SPAWN_RATE: int = int(os.getenv('ENDURANCE_TEST_SPAWN_RATE', '2'))
    ENDURANCE_TEST_DURATION: int = int(os.getenv('ENDURANCE_TEST_DURATION', '3600'))
    
    # Monitoring settings
    ENABLE_MONITORING: bool = os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
    PROMETHEUS_PORT: int = int(os.getenv('PROMETHEUS_PORT', '9090'))
    INFLUXDB_HOST: str = os.getenv('INFLUXDB_HOST', 'localhost')
    INFLUXDB_PORT: int = int(os.getenv('INFLUXDB_PORT', '8086'))
    INFLUXDB_DATABASE: str = os.getenv('INFLUXDB_DATABASE', 'locust')
    
    # Distributed testing settings
    MASTER_HOST: str = os.getenv('MASTER_HOST', 'localhost')
    MASTER_PORT: int = int(os.getenv('MASTER_PORT', '5557'))
    WORKER_PORT: int = int(os.getenv('WORKER_PORT', '5558'))
    
    # Web UI settings
    WEB_UI_HOST: str = os.getenv('WEB_UI_HOST', '0.0.0.0')
    WEB_UI_PORT: int = int(os.getenv('WEB_UI_PORT', '8089'))
    
    # SSL settings
    SSL_VERIFY: bool = os.getenv('SSL_VERIFY', 'true').lower() == 'true'
    SSL_CERT_PATH: Optional[str] = os.getenv('SSL_CERT_PATH')
    SSL_KEY_PATH: Optional[str] = os.getenv('SSL_KEY_PATH')
    
    # Cookie settings
    ENABLE_COOKIES: bool = os.getenv('ENABLE_COOKIES', 'true').lower() == 'true'
    PERSIST_COOKIES: bool = os.getenv('PERSIST_COOKIES', 'true').lower() == 'true'
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW: int = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    
    # Database settings (for test data)
    DATABASE_URL: str = os.getenv('DATABASE_URL', '')
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Test scenario weights
    SCENARIO_WEIGHTS: Dict[str, int] = {
        'browse_users': int(os.getenv('WEIGHT_BROWSE_USERS', '30')),
        'browse_posts': int(os.getenv('WEIGHT_BROWSE_POSTS', '25')),
        'create_content': int(os.getenv('WEIGHT_CREATE_CONTENT', '20')),
        'update_content': int(os.getenv('WEIGHT_UPDATE_CONTENT', '15')),
        'delete_content': int(os.getenv('WEIGHT_DELETE_CONTENT', '10'))
    }
    
    # Task timing settings
    TASK_MIN_WAIT: int = int(os.getenv('TASK_MIN_WAIT', '1000'))  # ms
    TASK_MAX_WAIT: int = int(os.getenv('TASK_MAX_WAIT', '5000'))  # ms
    
    # Response validation settings
    VALIDATE_RESPONSES: bool = os.getenv('VALIDATE_RESPONSES', 'true').lower() == 'true'
    VALIDATE_JSON_SCHEMA: bool = os.getenv('VALIDATE_JSON_SCHEMA', 'false').lower() == 'true'
    
    # Error handling settings
    STOP_ON_FAILURE: bool = os.getenv('STOP_ON_FAILURE', 'false').lower() == 'true'
    FAILURE_THRESHOLD: int = int(os.getenv('FAILURE_THRESHOLD', '10'))
    
    # Resource monitoring settings
    MONITOR_RESOURCES: bool = os.getenv('MONITOR_RESOURCES', 'true').lower() == 'true'
    RESOURCE_MONITORING_INTERVAL: int = int(os.getenv('RESOURCE_MONITORING_INTERVAL', '5'))
    
    @classmethod
    def get_test_settings(cls, scenario: str) -> Dict[str, Any]:
        """Get test settings for a specific scenario"""
        scenario_settings = {
            'load': {
                'users': cls.LOAD_TEST_USERS,
                'spawn_rate': cls.LOAD_TEST_SPAWN_RATE,
                'duration': cls.LOAD_TEST_DURATION
            },
            'stress': {
                'users': cls.STRESS_TEST_USERS,
                'spawn_rate': cls.STRESS_TEST_SPAWN_RATE,
                'duration': cls.STRESS_TEST_DURATION
            },
            'spike': {
                'users': cls.SPIKE_TEST_USERS,
                'spawn_rate': cls.SPIKE_TEST_SPAWN_RATE,
                'duration': cls.SPIKE_TEST_DURATION
            },
            'endurance': {
                'users': cls.ENDURANCE_TEST_USERS,
                'spawn_rate': cls.ENDURANCE_TEST_SPAWN_RATE,
                'duration': cls.ENDURANCE_TEST_DURATION
            }
        }
        
        return scenario_settings.get(scenario, {
            'users': cls.DEFAULT_USERS,
            'spawn_rate': cls.DEFAULT_SPAWN_RATE,
            'duration': cls.DEFAULT_DURATION
        })
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get all HTTP headers"""
        headers = cls.ALL_HEADERS.copy()
        
        # Add authentication headers
        if cls.AUTH_TYPE == 'bearer' and cls.AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {cls.AUTH_TOKEN}'
        elif cls.AUTH_TYPE == 'api_key' and cls.API_KEY:
            headers[cls.API_KEY_HEADER] = cls.API_KEY
        
        return headers
    
    @classmethod
    def validate_settings(cls) -> bool:
        """Validate configuration settings"""
        required_settings = [
            'TARGET_HOST',
            'DEFAULT_USERS',
            'DEFAULT_SPAWN_RATE',
            'DEFAULT_DURATION'
        ]
        
        for setting in required_settings:
            if not hasattr(cls, setting) or not getattr(cls, setting):
                print(f"Warning: Required setting {setting} is not configured")
                return False
        
        return True
    
    @classmethod
    def print_settings(cls):
        """Print current configuration settings"""
        print("=== Locust Performance Testing Framework Configuration ===")
        print(f"Environment: {cls.ENVIRONMENT}")
        print(f"Target Host: {cls.TARGET_HOST}")
        print(f"Default Users: {cls.DEFAULT_USERS}")
        print(f"Default Spawn Rate: {cls.DEFAULT_SPAWN_RATE}")
        print(f"Default Duration: {cls.DEFAULT_DURATION}")
        print(f"Request Timeout: {cls.REQUEST_TIMEOUT}s")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"Authentication: {cls.AUTH_TYPE}")
        print(f"Reports Directory: {cls.REPORTS_DIRECTORY}")
        print(f"Logs Directory: {cls.LOGS_DIRECTORY}")
        print(f"Debug Mode: {cls.DEBUG}")
        print("=" * 60)

# Initialize settings
settings = Settings()

# Validate settings on import
if not settings.validate_settings():
    print("Warning: Configuration validation failed. Please check your settings.") 