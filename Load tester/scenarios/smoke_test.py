"""
Smoke Test Scenario for the Locust Performance Testing Framework
"""

import random
from locust import HttpUser, task, between
from utils.base_user import BaseUser
from utils.data_generator import DataGenerator
from utils.monitoring import record_request, record_custom_metric
from config.environments import API_ENDPOINTS, env_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmokeTestUser(BaseUser):
    """Smoke test user class"""
    
    wait_time = between(0.5, 2.0)
    weight = 1
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_generator = DataGenerator(seed=42)
        self.test_data = {
            'users': list(range(1, 11)),
            'posts': list(range(1, 101)),
            'comments': list(range(1, 501)),
            'albums': list(range(1, 101)),
            'photos': list(range(1, 5001)),
            'todos': list(range(1, 201))
        }
    
    def on_start(self):
        """Called when user starts"""
        super().on_start()
        logger.info("Starting smoke test user")
        
        # Record custom metric for user start
        record_custom_metric('user_started', 1.0, {'test_type': 'smoke'})
    
    def on_stop(self):
        """Called when user stops"""
        super().on_stop()
        logger.info("Stopping smoke test user")
        
        # Record custom metric for user stop
        record_custom_metric('user_stopped', 1.0, {'test_type': 'smoke'})
    
    @task(5)
    def test_get_users(self):
        """Test getting all users"""
        with self.client.get(API_ENDPOINTS['users'], name="Get All Users", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    users = response.json()
                    if isinstance(users, list) and len(users) > 0:
                        record_custom_metric('users_count', len(users), {'endpoint': 'users'})
                        response.success()
                    else:
                        response.failure("Empty users list")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(3)
    def test_get_user_by_id(self):
        """Test getting user by ID"""
        user_id = random.choice(self.test_data['users'])
        endpoint = f"{API_ENDPOINTS['users']}/{user_id}"
        
        with self.client.get(endpoint, name="Get User by ID", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    user = response.json()
                    required_fields = ['id', 'name', 'email', 'username']
                    if all(field in user for field in required_fields):
                        record_custom_metric('user_fields_valid', 1.0, {'user_id': str(user_id)})
                        response.success()
                    else:
                        response.failure("Missing required user fields")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(5)
    def test_get_posts(self):
        """Test getting all posts"""
        with self.client.get(API_ENDPOINTS['posts'], name="Get All Posts", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    posts = response.json()
                    if isinstance(posts, list) and len(posts) > 0:
                        record_custom_metric('posts_count', len(posts), {'endpoint': 'posts'})
                        response.success()
                    else:
                        response.failure("Empty posts list")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(3)
    def test_get_post_by_id(self):
        """Test getting post by ID"""
        post_id = random.choice(self.test_data['posts'])
        endpoint = f"{API_ENDPOINTS['posts']}/{post_id}"
        
        with self.client.get(endpoint, name="Get Post by ID", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    post = response.json()
                    required_fields = ['id', 'title', 'body', 'userId']
                    if all(field in post for field in required_fields):
                        record_custom_metric('post_fields_valid', 1.0, {'post_id': str(post_id)})
                        response.success()
                    else:
                        response.failure("Missing required post fields")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def test_create_post(self):
        """Test creating a new post"""
        post_data = {
            'title': f'Smoke Test Post {random.randint(1, 1000)}',
            'body': f'This is a smoke test post body {random.randint(1, 1000)}',
            'userId': random.choice(self.test_data['users'])
        }
        
        with self.client.post(API_ENDPOINTS['posts'], json=post_data, name="Create Post", catch_response=True) as response:
            if response.status_code == 201:
                try:
                    created_post = response.json()
                    if 'id' in created_post and created_post['title'] == post_data['title']:
                        record_custom_metric('post_created', 1.0, {'title': post_data['title']})
                        response.success()
                    else:
                        response.failure("Invalid created post data")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(3)
    def test_get_comments(self):
        """Test getting all comments"""
        with self.client.get(API_ENDPOINTS['comments'], name="Get All Comments", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    comments = response.json()
                    if isinstance(comments, list) and len(comments) > 0:
                        record_custom_metric('comments_count', len(comments), {'endpoint': 'comments'})
                        response.success()
                    else:
                        response.failure("Empty comments list")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def test_get_post_comments(self):
        """Test getting comments for a specific post"""
        post_id = random.choice(self.test_data['posts'])
        endpoint = f"{API_ENDPOINTS['posts']}/{post_id}/comments"
        
        with self.client.get(endpoint, name="Get Post Comments", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    comments = response.json()
                    if isinstance(comments, list):
                        record_custom_metric('post_comments_count', len(comments), {'post_id': str(post_id)})
                        response.success()
                    else:
                        response.failure("Invalid comments data")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def test_get_albums(self):
        """Test getting all albums"""
        with self.client.get(API_ENDPOINTS['albums'], name="Get All Albums", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    albums = response.json()
                    if isinstance(albums, list) and len(albums) > 0:
                        record_custom_metric('albums_count', len(albums), {'endpoint': 'albums'})
                        response.success()
                    else:
                        response.failure("Empty albums list")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def test_get_user_albums(self):
        """Test getting albums for a specific user"""
        user_id = random.choice(self.test_data['users'])
        endpoint = f"{API_ENDPOINTS['users']}/{user_id}/albums"
        
        with self.client.get(endpoint, name="Get User Albums", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    albums = response.json()
                    if isinstance(albums, list):
                        record_custom_metric('user_albums_count', len(albums), {'user_id': str(user_id)})
                        response.success()
                    else:
                        response.failure("Invalid albums data")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def test_get_photos(self):
        """Test getting all photos"""
        with self.client.get(API_ENDPOINTS['photos'], name="Get All Photos", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    photos = response.json()
                    if isinstance(photos, list) and len(photos) > 0:
                        record_custom_metric('photos_count', len(photos), {'endpoint': 'photos'})
                        response.success()
                    else:
                        response.failure("Empty photos list")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def test_get_todos(self):
        """Test getting all todos"""
        with self.client.get(API_ENDPOINTS['todos'], name="Get All Todos", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    todos = response.json()
                    if isinstance(todos, list) and len(todos) > 0:
                        record_custom_metric('todos_count', len(todos), {'endpoint': 'todos'})
                        response.success()
                    else:
                        response.failure("Empty todos list")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def test_get_user_todos(self):
        """Test getting todos for a specific user"""
        user_id = random.choice(self.test_data['users'])
        endpoint = f"{API_ENDPOINTS['users']}/{user_id}/todos"
        
        with self.client.get(endpoint, name="Get User Todos", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    todos = response.json()
                    if isinstance(todos, list):
                        record_custom_metric('user_todos_count', len(todos), {'user_id': str(user_id)})
                        response.success()
                    else:
                        response.failure("Invalid todos data")
                except Exception as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def test_response_time_threshold(self):
        """Test response time threshold"""
        start_time = self.client.session.get('start_time', 0)
        
        with self.client.get(API_ENDPOINTS['users'], name="Response Time Check", catch_response=True) as response:
            response_time = response.elapsed.total_seconds() * 1000  # Convert to milliseconds
            threshold = self.env_config.get('thresholds', {}).get('response_time', 1000)
            
            if response_time > threshold:
                response.failure(f"Response time {response_time}ms exceeded threshold {threshold}ms")
                record_custom_metric('response_time_exceeded', 1.0, {'response_time': str(response_time)})
            else:
                response.success()
                record_custom_metric('response_time_ok', 1.0, {'response_time': str(response_time)})
    
    @task(1)
    def test_health_check(self):
        """Test basic health check"""
        endpoints_to_check = [
            API_ENDPOINTS['users'],
            API_ENDPOINTS['posts'],
            API_ENDPOINTS['comments']
        ]
        
        healthy_endpoints = 0
        
        for endpoint in endpoints_to_check:
            with self.client.get(endpoint, name=f"Health Check {endpoint}", catch_response=True) as response:
                if response.status_code == 200:
                    healthy_endpoints += 1
                    response.success()
                else:
                    response.failure(f"Health check failed for {endpoint}")
        
        # Record health metric
        health_ratio = healthy_endpoints / len(endpoints_to_check)
        record_custom_metric('health_ratio', health_ratio, {'healthy_endpoints': str(healthy_endpoints)})
    
    def wait_time_with_jitter(self, min_wait: float = 0.5, max_wait: float = 2.0):
        """Wait with jitter to avoid thundering herd"""
        base_wait = random.uniform(min_wait, max_wait)
        jitter = random.uniform(-0.1, 0.1)
        wait_time = max(0.1, base_wait + jitter)
        return wait_time

# Test configuration
class SmokeTestConfig:
    """Configuration for smoke tests"""
    
    # Test parameters
    USERS = 5
    SPAWN_RATE = 1
    DURATION = 60  # seconds
    
    # Thresholds
    MAX_RESPONSE_TIME = 1000  # milliseconds
    MAX_ERROR_RATE = 0.05  # 5%
    MIN_SUCCESS_RATE = 0.95  # 95%
    
    # Test data
    TEST_ENDPOINTS = [
        API_ENDPOINTS['users'],
        API_ENDPOINTS['posts'],
        API_ENDPOINTS['comments'],
        API_ENDPOINTS['albums'],
        API_ENDPOINTS['photos'],
        API_ENDPOINTS['todos']
    ]

# Alternative user class for minimal smoke testing
class MinimalSmokeTestUser(BaseUser):
    """Minimal smoke test user for quick validation"""
    
    wait_time = between(0.1, 0.5)
    weight = 1
    
    @task(1)
    def test_basic_connectivity(self):
        """Test basic connectivity"""
        with self.client.get(API_ENDPOINTS['users'], name="Basic Connectivity", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Basic connectivity failed: {response.status_code}")
    
    @task(1)
    def test_json_response(self):
        """Test JSON response format"""
        with self.client.get(API_ENDPOINTS['posts'], name="JSON Response", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Response is not a list")
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
            else:
                response.failure(f"JSON response test failed: {response.status_code}")

# Example usage
if __name__ == "__main__":
    # This would typically be run through the locust command
    # locust -f smoke_test.py --host=https://jsonplaceholder.typicode.com --users=5 --spawn-rate=1 --run-time=60s
    pass 