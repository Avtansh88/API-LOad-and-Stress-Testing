"""
Environment-specific configuration for the Locust Performance Testing Framework
"""

from typing import Dict, Any, Optional
import os

class EnvironmentConfig:
    """Environment-specific configuration class"""
    
    # Environment definitions
    ENVIRONMENTS: Dict[str, Dict[str, Any]] = {
        'dev': {
            'name': 'Development',
            'host': 'https://jsonplaceholder.typicode.com',
            'api_version': 'v1',
            'users': 10,
            'spawn_rate': 2,
            'duration': 60,
            'timeout': 30,
            'retries': 3,
            'auth_type': 'none',
            'ssl_verify': True,
            'debug': True,
            'monitoring_enabled': True,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Locust-Dev-Test/1.0'
            },
            'thresholds': {
                'response_time': 1000,
                'error_rate': 0.05,
                'success_rate': 0.95
            }
        },
        
        'test': {
            'name': 'Testing',
            'host': 'https://test-api.example.com',
            'api_version': 'v1',
            'users': 25,
            'spawn_rate': 5,
            'duration': 120,
            'timeout': 30,
            'retries': 3,
            'auth_type': 'api_key',
            'api_key': os.getenv('TEST_API_KEY', 'test-api-key'),
            'ssl_verify': True,
            'debug': True,
            'monitoring_enabled': True,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Locust-Test-Test/1.0'
            },
            'thresholds': {
                'response_time': 800,
                'error_rate': 0.03,
                'success_rate': 0.97
            }
        },
        
        'staging': {
            'name': 'Staging',
            'host': 'https://staging-api.example.com',
            'api_version': 'v1',
            'users': 50,
            'spawn_rate': 5,
            'duration': 300,
            'timeout': 60,
            'retries': 3,
            'auth_type': 'bearer',
            'auth_token': os.getenv('STAGING_AUTH_TOKEN', ''),
            'ssl_verify': True,
            'debug': False,
            'monitoring_enabled': True,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Locust-Staging-Test/1.0'
            },
            'thresholds': {
                'response_time': 600,
                'error_rate': 0.02,
                'success_rate': 0.98
            }
        },
        
        'production': {
            'name': 'Production',
            'host': 'https://api.example.com',
            'api_version': 'v1',
            'users': 100,
            'spawn_rate': 10,
            'duration': 600,
            'timeout': 60,
            'retries': 5,
            'auth_type': 'bearer',
            'auth_token': os.getenv('PROD_AUTH_TOKEN', ''),
            'ssl_verify': True,
            'debug': False,
            'monitoring_enabled': True,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Locust-Prod-Test/1.0'
            },
            'thresholds': {
                'response_time': 500,
                'error_rate': 0.01,
                'success_rate': 0.99
            }
        }
    }
    
    # Load test specific settings
    LOAD_TEST_SETTINGS: Dict[str, Dict[str, Any]] = {
        'dev': {
            'users': 20,
            'spawn_rate': 4,
            'duration': 180
        },
        'test': {
            'users': 50,
            'spawn_rate': 10,
            'duration': 300
        },
        'staging': {
            'users': 100,
            'spawn_rate': 10,
            'duration': 600
        },
        'production': {
            'users': 200,
            'spawn_rate': 20,
            'duration': 900
        }
    }
    
    # Stress test specific settings
    STRESS_TEST_SETTINGS: Dict[str, Dict[str, Any]] = {
        'dev': {
            'users': 50,
            'spawn_rate': 10,
            'duration': 300
        },
        'test': {
            'users': 100,
            'spawn_rate': 20,
            'duration': 600
        },
        'staging': {
            'users': 200,
            'spawn_rate': 20,
            'duration': 900
        },
        'production': {
            'users': 500,
            'spawn_rate': 50,
            'duration': 1200
        }
    }
    
    # Spike test specific settings
    SPIKE_TEST_SETTINGS: Dict[str, Dict[str, Any]] = {
        'dev': {
            'users': 100,
            'spawn_rate': 50,
            'duration': 120
        },
        'test': {
            'users': 200,
            'spawn_rate': 100,
            'duration': 180
        },
        'staging': {
            'users': 500,
            'spawn_rate': 200,
            'duration': 300
        },
        'production': {
            'users': 1000,
            'spawn_rate': 500,
            'duration': 600
        }
    }
    
    # Endurance test specific settings
    ENDURANCE_TEST_SETTINGS: Dict[str, Dict[str, Any]] = {
        'dev': {
            'users': 15,
            'spawn_rate': 2,
            'duration': 1800  # 30 minutes
        },
        'test': {
            'users': 30,
            'spawn_rate': 3,
            'duration': 3600  # 1 hour
        },
        'staging': {
            'users': 50,
            'spawn_rate': 5,
            'duration': 7200  # 2 hours
        },
        'production': {
            'users': 100,
            'spawn_rate': 10,
            'duration': 14400  # 4 hours
        }
    }
    
    @classmethod
    def get_environment_config(cls, environment: str) -> Dict[str, Any]:
        """Get configuration for a specific environment"""
        return cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS['dev'])
    
    @classmethod
    def get_test_config(cls, environment: str, test_type: str) -> Dict[str, Any]:
        """Get test configuration for a specific environment and test type"""
        base_config = cls.get_environment_config(environment)
        
        test_configs = {
            'load': cls.LOAD_TEST_SETTINGS,
            'stress': cls.STRESS_TEST_SETTINGS,
            'spike': cls.SPIKE_TEST_SETTINGS,
            'endurance': cls.ENDURANCE_TEST_SETTINGS
        }
        
        test_specific = test_configs.get(test_type, {}).get(environment, {})
        
        # Merge base config with test-specific settings
        config = base_config.copy()
        config.update(test_specific)
        
        return config
    
    @classmethod
    def get_host(cls, environment: str) -> str:
        """Get host URL for a specific environment"""
        return cls.get_environment_config(environment).get('host', 'https://jsonplaceholder.typicode.com')
    
    @classmethod
    def get_headers(cls, environment: str) -> Dict[str, str]:
        """Get HTTP headers for a specific environment"""
        env_config = cls.get_environment_config(environment)
        headers = env_config.get('headers', {}).copy()
        
        # Add authentication headers if configured
        auth_type = env_config.get('auth_type', 'none')
        if auth_type == 'bearer' and env_config.get('auth_token'):
            headers['Authorization'] = f"Bearer {env_config['auth_token']}"
        elif auth_type == 'api_key' and env_config.get('api_key'):
            headers['X-API-Key'] = env_config['api_key']
        
        return headers
    
    @classmethod
    def get_thresholds(cls, environment: str) -> Dict[str, Any]:
        """Get performance thresholds for a specific environment"""
        return cls.get_environment_config(environment).get('thresholds', {
            'response_time': 1000,
            'error_rate': 0.05,
            'success_rate': 0.95
        })
    
    @classmethod
    def get_available_environments(cls) -> list:
        """Get list of available environments"""
        return list(cls.ENVIRONMENTS.keys())
    
    @classmethod
    def validate_environment(cls, environment: str) -> bool:
        """Validate if environment exists"""
        return environment in cls.ENVIRONMENTS
    
    @classmethod
    def get_environment_description(cls, environment: str) -> str:
        """Get description of an environment"""
        env_config = cls.get_environment_config(environment)
        return f"{env_config.get('name', environment)} - {env_config.get('host', 'Unknown host')}"
    
    @classmethod
    def print_environment_info(cls, environment: str):
        """Print detailed information about an environment"""
        if not cls.validate_environment(environment):
            print(f"Environment '{environment}' not found")
            return
        
        config = cls.get_environment_config(environment)
        print(f"=== Environment: {environment.upper()} ===")
        print(f"Name: {config.get('name', 'Unknown')}")
        print(f"Host: {config.get('host', 'Unknown')}")
        print(f"API Version: {config.get('api_version', 'Unknown')}")
        print(f"Authentication: {config.get('auth_type', 'none')}")
        print(f"SSL Verify: {config.get('ssl_verify', True)}")
        print(f"Debug Mode: {config.get('debug', False)}")
        print(f"Monitoring: {config.get('monitoring_enabled', False)}")
        print(f"Default Users: {config.get('users', 0)}")
        print(f"Default Spawn Rate: {config.get('spawn_rate', 0)}")
        print(f"Default Duration: {config.get('duration', 0)}s")
        print(f"Request Timeout: {config.get('timeout', 30)}s")
        print(f"Max Retries: {config.get('retries', 3)}")
        
        thresholds = config.get('thresholds', {})
        print(f"Performance Thresholds:")
        print(f"  Response Time: {thresholds.get('response_time', 'N/A')}ms")
        print(f"  Error Rate: {thresholds.get('error_rate', 'N/A')}%")
        print(f"  Success Rate: {thresholds.get('success_rate', 'N/A')}%")
        print("=" * 40)
    
    @classmethod
    def print_all_environments(cls):
        """Print information about all environments"""
        print("=== Available Environments ===")
        for env in cls.get_available_environments():
            config = cls.get_environment_config(env)
            print(f"{env}: {config.get('name', env)} - {config.get('host', 'Unknown host')}")
        print("=" * 30)

# Environment configuration instance
env_config = EnvironmentConfig()

# Common API endpoints for all environments
API_ENDPOINTS = {
    'users': '/users',
    'posts': '/posts',
    'comments': '/comments',
    'albums': '/albums',
    'photos': '/photos',
    'todos': '/todos'
}

# HTTP methods
HTTP_METHODS = {
    'GET': 'GET',
    'POST': 'POST',
    'PUT': 'PUT',
    'PATCH': 'PATCH',
    'DELETE': 'DELETE'
}

# Content types
CONTENT_TYPES = {
    'JSON': 'application/json',
    'XML': 'application/xml',
    'FORM': 'application/x-www-form-urlencoded',
    'TEXT': 'text/plain'
}

# Response status codes
STATUS_CODES = {
    'OK': 200,
    'CREATED': 201,
    'NO_CONTENT': 204,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'INTERNAL_SERVER_ERROR': 500,
    'BAD_GATEWAY': 502,
    'SERVICE_UNAVAILABLE': 503
} 