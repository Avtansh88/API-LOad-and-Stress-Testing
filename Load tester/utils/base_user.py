"""
Base User class with common functionality for the Locust Performance Testing Framework
"""

import time
import random
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from locust import HttpUser, task, between
from locust.exception import StopUser
from requests.exceptions import RequestException
from config.environments import env_config, API_ENDPOINTS, HTTP_METHODS, STATUS_CODES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseUser(HttpUser):
    """Base user class with common functionality"""
    
    # Class-level configuration
    abstract = True
    wait_time = between(1, 3)  # Default wait time between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize user session data
        self.user_data: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
        self.auth_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.request_count: int = 0
        self.error_count: int = 0
        self.start_time: float = time.time()
        
        # Environment configuration
        self.environment_name = getattr(self.environment.parsed_options, 'environment', 'dev') if hasattr(self.environment, 'parsed_options') else 'dev'
        self.env_config = env_config.get_environment_config(self.environment_name)
        
        # Request configuration
        self.timeout = self.env_config.get('timeout', 30)
        self.retries = self.env_config.get('retries', 3)
        self.ssl_verify = self.env_config.get('ssl_verify', True)
        self.debug = self.env_config.get('debug', False)
        
        # Setup authentication headers
        self.setup_authentication()
        
        # Initialize monitoring
        self.setup_monitoring()
    
    def setup_authentication(self):
        """Setup authentication headers based on environment configuration"""
        auth_type = self.env_config.get('auth_type', 'none')
        
        if auth_type == 'bearer' and self.env_config.get('auth_token'):
            self.client.headers.update({
                'Authorization': f"Bearer {self.env_config['auth_token']}"
            })
        elif auth_type == 'api_key' and self.env_config.get('api_key'):
            self.client.headers.update({
                'X-API-Key': self.env_config['api_key']
            })
        
        # Add common headers
        common_headers = self.env_config.get('headers', {})
        self.client.headers.update(common_headers)
        
        # SSL verification
        self.client.verify = self.ssl_verify
    
    def setup_monitoring(self):
        """Setup monitoring and logging"""
        if self.debug:
            logger.setLevel(logging.DEBUG)
        
        # Log user initialization
        logger.info(f"User initialized for environment: {self.environment_name}")
        logger.info(f"Host: {self.host}")
        logger.info(f"Authentication: {self.env_config.get('auth_type', 'none')}")
    
    def make_request(self, method: str, endpoint: str, name: Optional[str] = None, 
                    data: Optional[Dict[str, Any]] = None, 
                    json_data: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    params: Optional[Dict[str, Any]] = None,
                    expected_status: int = 200,
                    catch_response: bool = True,
                    **kwargs) -> Any:
        """
        Make HTTP request with retry logic and error handling
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint
            name: Name for the request (for reporting)
            data: Form data
            json_data: JSON data
            headers: Additional headers
            params: Query parameters
            expected_status: Expected HTTP status code
            catch_response: Whether to catch response for manual validation
            **kwargs: Additional arguments for the request
        
        Returns:
            Response object or None if failed
        """
        if not name:
            name = f"{method.upper()} {endpoint}"
        
        # Prepare request headers
        request_headers = self.client.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare request data
        request_kwargs = {
            'headers': request_headers,
            'params': params,
            'timeout': self.timeout,
            'catch_response': catch_response,
            **kwargs
        }
        
        if json_data:
            request_kwargs['json'] = json_data
        elif data:
            request_kwargs['data'] = data
        
        # Make request with retry logic
        for attempt in range(self.retries + 1):
            try:
                response = self.client.request(
                    method.upper(),
                    endpoint,
                    name=name,
                    **request_kwargs
                )
                
                self.request_count += 1
                
                # Handle catch_response
                if catch_response:
                    if response.status_code == expected_status:
                        response.success()
                        if self.debug:
                            logger.debug(f"Request succeeded: {name} - Status: {response.status_code}")
                        return response
                    else:
                        response.failure(f"Expected status {expected_status}, got {response.status_code}")
                        self.error_count += 1
                        if self.debug:
                            logger.debug(f"Request failed: {name} - Status: {response.status_code}")
                        return response
                else:
                    return response
                    
            except RequestException as e:
                self.error_count += 1
                if attempt < self.retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.retries + 1}): {str(e)}. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.retries + 1} attempts: {str(e)}")
                    if catch_response:
                        with self.client.request(method.upper(), endpoint, name=name, catch_response=True, **request_kwargs) as response:
                            response.failure(f"Request failed: {str(e)}")
                    return None
        
        return None
    
    def get(self, endpoint: str, name: Optional[str] = None, **kwargs) -> Any:
        """Make GET request"""
        return self.make_request('GET', endpoint, name=name, **kwargs)
    
    def post(self, endpoint: str, name: Optional[str] = None, **kwargs) -> Any:
        """Make POST request"""
        return self.make_request('POST', endpoint, name=name, expected_status=201, **kwargs)
    
    def put(self, endpoint: str, name: Optional[str] = None, **kwargs) -> Any:
        """Make PUT request"""
        return self.make_request('PUT', endpoint, name=name, **kwargs)
    
    def patch(self, endpoint: str, name: Optional[str] = None, **kwargs) -> Any:
        """Make PATCH request"""
        return self.make_request('PATCH', endpoint, name=name, **kwargs)
    
    def delete(self, endpoint: str, name: Optional[str] = None, **kwargs) -> Any:
        """Make DELETE request"""
        return self.make_request('DELETE', endpoint, name=name, expected_status=204, **kwargs)
    
    def validate_response(self, response: Any, expected_keys: Optional[List[str]] = None, 
                         expected_values: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate response content
        
        Args:
            response: Response object
            expected_keys: List of expected keys in response
            expected_values: Dict of expected key-value pairs
        
        Returns:
            True if validation passes, False otherwise
        """
        if not response:
            return False
        
        try:
            # Check if response has JSON content
            if response.headers.get('content-type', '').startswith('application/json'):
                json_data = response.json()
                
                # Check expected keys
                if expected_keys:
                    for key in expected_keys:
                        if key not in json_data:
                            logger.error(f"Expected key '{key}' not found in response")
                            return False
                
                # Check expected values
                if expected_values:
                    for key, expected_value in expected_values.items():
                        if key not in json_data:
                            logger.error(f"Expected key '{key}' not found in response")
                            return False
                        if json_data[key] != expected_value:
                            logger.error(f"Expected '{key}' to be '{expected_value}', got '{json_data[key]}'")
                            return False
                
                return True
            else:
                # For non-JSON responses, just check status code
                return response.status_code < 400
                
        except json.JSONDecodeError:
            logger.error("Response is not valid JSON")
            return False
        except Exception as e:
            logger.error(f"Error validating response: {str(e)}")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate user (to be implemented by subclasses)
        
        Returns:
            True if authentication successful, False otherwise
        """
        # This is a placeholder - implement in subclasses
        return True
    
    def cleanup(self):
        """Cleanup user session"""
        if self.session_id:
            # Implement session cleanup logic
            pass
        
        # Log session statistics
        duration = time.time() - self.start_time
        logger.info(f"User session completed - Duration: {duration:.2f}s, Requests: {self.request_count}, Errors: {self.error_count}")
    
    def on_start(self):
        """Called when user starts"""
        logger.info(f"Starting user on host: {self.host}")
        
        # Authenticate user
        if not self.authenticate():
            logger.error("Authentication failed")
            raise StopUser("Authentication failed")
    
    def on_stop(self):
        """Called when user stops"""
        logger.info("Stopping user")
        self.cleanup()
    
    def wait_random(self, min_time: float = 0.5, max_time: float = 2.0):
        """Wait for a random amount of time"""
        wait_time = random.uniform(min_time, max_time)
        time.sleep(wait_time)
    
    def get_random_user_id(self) -> int:
        """Get a random user ID (1-10 for JSONPlaceholder)"""
        return random.randint(1, 10)
    
    def get_random_post_id(self) -> int:
        """Get a random post ID (1-100 for JSONPlaceholder)"""
        return random.randint(1, 100)
    
    def get_random_comment_id(self) -> int:
        """Get a random comment ID (1-500 for JSONPlaceholder)"""
        return random.randint(1, 500)
    
    def get_random_album_id(self) -> int:
        """Get a random album ID (1-100 for JSONPlaceholder)"""
        return random.randint(1, 100)
    
    def get_random_photo_id(self) -> int:
        """Get a random photo ID (1-5000 for JSONPlaceholder)"""
        return random.randint(1, 5000)
    
    def get_random_todo_id(self) -> int:
        """Get a random todo ID (1-200 for JSONPlaceholder)"""
        return random.randint(1, 200)
    
    def log_custom_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Log custom metric (for monitoring integration)"""
        if self.env_config.get('monitoring_enabled', False):
            logger.info(f"Custom metric: {metric_name} = {value}, tags: {tags}")
    
    def check_performance_threshold(self, response_time: float, operation: str):
        """Check if response time exceeds threshold"""
        threshold = self.env_config.get('thresholds', {}).get('response_time', 1000)
        if response_time > threshold:
            logger.warning(f"Response time threshold exceeded for {operation}: {response_time}ms > {threshold}ms")
            return False
        return True
    
    def is_healthy(self) -> bool:
        """Check if user is healthy (error rate below threshold)"""
        if self.request_count == 0:
            return True
        
        error_rate = self.error_count / self.request_count
        threshold = self.env_config.get('thresholds', {}).get('error_rate', 0.05)
        
        return error_rate <= threshold
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        duration = time.time() - self.start_time
        return {
            'duration': duration,
            'requests': self.request_count,
            'errors': self.error_count,
            'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
            'requests_per_second': self.request_count / duration if duration > 0 else 0
        }

class ApiUser(BaseUser):
    """API user for testing REST endpoints"""
    
    def authenticate(self) -> bool:
        """Authenticate API user"""
        # For JSONPlaceholder, no authentication is needed
        # In real scenarios, you would implement authentication here
        return True
    
    @task(3)
    def get_users(self):
        """Get all users"""
        response = self.get(API_ENDPOINTS['users'], name="Get Users")
        if response:
            self.validate_response(response, expected_keys=['id', 'name', 'email'])
    
    @task(2)
    def get_user_by_id(self):
        """Get user by ID"""
        user_id = self.get_random_user_id()
        response = self.get(f"{API_ENDPOINTS['users']}/{user_id}", name="Get User by ID")
        if response:
            self.validate_response(response, expected_keys=['id', 'name', 'email'])
    
    @task(3)
    def get_posts(self):
        """Get all posts"""
        response = self.get(API_ENDPOINTS['posts'], name="Get Posts")
        if response:
            self.validate_response(response, expected_keys=['id', 'title', 'body'])
    
    @task(2)
    def get_post_by_id(self):
        """Get post by ID"""
        post_id = self.get_random_post_id()
        response = self.get(f"{API_ENDPOINTS['posts']}/{post_id}", name="Get Post by ID")
        if response:
            self.validate_response(response, expected_keys=['id', 'title', 'body'])
    
    @task(1)
    def create_post(self):
        """Create a new post"""
        post_data = {
            'title': f'Test Post {random.randint(1, 1000)}',
            'body': f'This is a test post body {random.randint(1, 1000)}',
            'userId': self.get_random_user_id()
        }
        response = self.post(API_ENDPOINTS['posts'], name="Create Post", json_data=post_data)
        if response:
            self.validate_response(response, expected_keys=['id', 'title', 'body'])
    
    @task(1)
    def update_post(self):
        """Update an existing post"""
        post_id = self.get_random_post_id()
        post_data = {
            'id': post_id,
            'title': f'Updated Test Post {random.randint(1, 1000)}',
            'body': f'This is an updated test post body {random.randint(1, 1000)}',
            'userId': self.get_random_user_id()
        }
        response = self.put(f"{API_ENDPOINTS['posts']}/{post_id}", name="Update Post", json_data=post_data)
        if response:
            self.validate_response(response, expected_keys=['id', 'title', 'body'])
    
    @task(1)
    def delete_post(self):
        """Delete a post"""
        post_id = self.get_random_post_id()
        response = self.delete(f"{API_ENDPOINTS['posts']}/{post_id}", name="Delete Post")
        # JSONPlaceholder returns 200 instead of 204 for DELETE
        if response:
            self.validate_response(response)

class WebUser(BaseUser):
    """Web user for testing web interfaces"""
    
    def authenticate(self) -> bool:
        """Authenticate web user"""
        # Implement web authentication logic
        return True
    
    @task
    def browse_content(self):
        """Browse web content"""
        # Implement web browsing logic
        response = self.get('/', name="Homepage")
        if response:
            self.validate_response(response) 