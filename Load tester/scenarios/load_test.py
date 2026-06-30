"""
Load Test Scenario for the Locust Performance Testing Framework
"""

import random
import time
from locust import HttpUser, task, between, events
from utils.base_user import BaseUser
from utils.data_generator import DataGenerator
from utils.monitoring import record_request, record_custom_metric
from config.environments import API_ENDPOINTS, env_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadTestUser(BaseUser):
    """Load test user class for sustained load testing"""
    
    wait_time = between(1, 3)
    weight = 3
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_generator = DataGenerator()
        self.user_session_data = {}
        self.request_history = []
        
    def on_start(self):
        """Called when user starts"""
        super().on_start()
        logger.info(f"Starting load test user: {id(self)}")
        
        # Initialize user session data
        self.user_session_data = {
            'start_time': time.time(),
            'requests_made': 0,
            'errors_encountered': 0,
            'user_id': random.randint(1, 10),
            'session_id': f"session_{random.randint(1000, 9999)}"
        }
        
        # Record user start metric
        record_custom_metric('load_test_user_started', 1.0, {
            'user_id': str(self.user_session_data['user_id']),
            'session_id': self.user_session_data['session_id']
        })
    
    def on_stop(self):
        """Called when user stops"""
        super().on_stop()
        
        # Calculate session statistics
        session_duration = time.time() - self.user_session_data['start_time']
        requests_per_second = self.user_session_data['requests_made'] / session_duration if session_duration > 0 else 0
        error_rate = self.user_session_data['errors_encountered'] / self.user_session_data['requests_made'] if self.user_session_data['requests_made'] > 0 else 0
        
        # Record session metrics
        record_custom_metric('load_test_session_duration', session_duration, {
            'session_id': self.user_session_data['session_id']
        })
        record_custom_metric('load_test_requests_per_second', requests_per_second, {
            'session_id': self.user_session_data['session_id']
        })
        record_custom_metric('load_test_error_rate', error_rate, {
            'session_id': self.user_session_data['session_id']
        })
        
        logger.info(f"Stopping load test user: {id(self)} - Duration: {session_duration:.2f}s, Requests: {self.user_session_data['requests_made']}, RPS: {requests_per_second:.2f}")
    
    def _record_request(self, success: bool, response_time: float = 0):
        """Record request statistics"""
        self.user_session_data['requests_made'] += 1
        if not success:
            self.user_session_data['errors_encountered'] += 1
        
        self.request_history.append({
            'timestamp': time.time(),
            'success': success,
            'response_time': response_time
        })
        
        # Keep only last 100 requests
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]
    
    @task(10)
    def browse_users(self):
        """Browse users with realistic patterns"""
        # Get all users
        start_time = time.time()
        with self.client.get(API_ENDPOINTS['users'], name="Browse Users - Get All", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    users = response.json()
                    if isinstance(users, list) and len(users) > 0:
                        # Simulate user browsing - get details for random users
                        selected_users = random.sample(users, min(3, len(users)))
                        
                        for user in selected_users:
                            self.wait_random(0.5, 1.5)  # Simulate reading time
                            self.get_user_details(user['id'])
                        
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('users_browsed', len(selected_users), {
                            'total_users': str(len(users))
                        })
                    else:
                        response.failure("Empty users list")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def get_user_details(self, user_id: int):
        """Get detailed user information"""
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['users']}/{user_id}", name="Get User Details", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    user = response.json()
                    if 'id' in user and 'name' in user:
                        response.success()
                        self._record_request(True, response_time)
                        
                        # Get user's posts and albums
                        if random.random() < 0.6:  # 60% chance to get posts
                            self.wait_random(0.2, 0.8)
                            self.get_user_posts(user_id)
                        
                        if random.random() < 0.3:  # 30% chance to get albums
                            self.wait_random(0.2, 0.8)
                            self.get_user_albums(user_id)
                    else:
                        response.failure("Missing user data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def get_user_posts(self, user_id: int):
        """Get user's posts"""
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['users']}/{user_id}/posts", name="Get User Posts", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    posts = response.json()
                    if isinstance(posts, list):
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('user_posts_loaded', len(posts), {
                            'user_id': str(user_id)
                        })
                    else:
                        response.failure("Invalid posts data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def get_user_albums(self, user_id: int):
        """Get user's albums"""
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['users']}/{user_id}/albums", name="Get User Albums", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    albums = response.json()
                    if isinstance(albums, list):
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('user_albums_loaded', len(albums), {
                            'user_id': str(user_id)
                        })
                    else:
                        response.failure("Invalid albums data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    @task(15)
    def browse_posts(self):
        """Browse posts with realistic pagination"""
        # Simulate pagination - get posts in chunks
        page_size = 20
        start_index = random.randint(0, 80)  # Random starting point
        
        start_time = time.time()
        params = {
            '_start': start_index,
            '_limit': page_size
        }
        
        with self.client.get(API_ENDPOINTS['posts'], params=params, name="Browse Posts - Paginated", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    posts = response.json()
                    if isinstance(posts, list):
                        # Simulate reading posts
                        for post in posts[:5]:  # Read first 5 posts
                            if random.random() < 0.4:  # 40% chance to read post details
                                self.wait_random(0.3, 1.0)
                                self.get_post_details(post['id'])
                        
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('posts_browsed', len(posts), {
                            'page_start': str(start_index),
                            'page_size': str(page_size)
                        })
                    else:
                        response.failure("Invalid posts data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def get_post_details(self, post_id: int):
        """Get post details and comments"""
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['posts']}/{post_id}", name="Get Post Details", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    post = response.json()
                    if 'id' in post and 'title' in post:
                        response.success()
                        self._record_request(True, response_time)
                        
                        # Get comments for this post
                        if random.random() < 0.7:  # 70% chance to read comments
                            self.wait_random(0.2, 0.6)
                            self.get_post_comments(post_id)
                    else:
                        response.failure("Missing post data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def get_post_comments(self, post_id: int):
        """Get comments for a post"""
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['posts']}/{post_id}/comments", name="Get Post Comments", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    comments = response.json()
                    if isinstance(comments, list):
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('post_comments_loaded', len(comments), {
                            'post_id': str(post_id)
                        })
                    else:
                        response.failure("Invalid comments data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    @task(5)
    def create_and_manage_posts(self):
        """Create and manage posts"""
        # Create a new post
        post_data = self.data_generator.generate_post().to_dict()
        post_data['userId'] = self.user_session_data['user_id']
        
        start_time = time.time()
        with self.client.post(API_ENDPOINTS['posts'], json=post_data, name="Create Post", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 201:
                try:
                    created_post = response.json()
                    if 'id' in created_post:
                        response.success()
                        self._record_request(True, response_time)
                        
                        post_id = created_post['id']
                        record_custom_metric('post_created', 1.0, {
                            'user_id': str(self.user_session_data['user_id']),
                            'post_id': str(post_id)
                        })
                        
                        # Simulate post management operations
                        self.wait_random(1.0, 3.0)
                        
                        # Update post (50% chance)
                        if random.random() < 0.5:
                            self.update_post(post_id, post_data)
                        
                        # Delete post (20% chance)
                        if random.random() < 0.2:
                            self.wait_random(0.5, 1.0)
                            self.delete_post(post_id)
                    else:
                        response.failure("No ID in created post")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def update_post(self, post_id: int, original_data: dict):
        """Update an existing post"""
        updated_data = original_data.copy()
        updated_data['title'] = f"Updated: {updated_data['title']}"
        updated_data['body'] = f"Updated: {updated_data['body']}"
        
        start_time = time.time()
        with self.client.put(f"{API_ENDPOINTS['posts']}/{post_id}", json=updated_data, name="Update Post", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    updated_post = response.json()
                    if 'id' in updated_post:
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('post_updated', 1.0, {
                            'post_id': str(post_id)
                        })
                    else:
                        response.failure("No ID in updated post")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def delete_post(self, post_id: int):
        """Delete a post"""
        start_time = time.time()
        with self.client.delete(f"{API_ENDPOINTS['posts']}/{post_id}", name="Delete Post", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code in [200, 204]:
                response.success()
                self._record_request(True, response_time)
                record_custom_metric('post_deleted', 1.0, {
                    'post_id': str(post_id)
                })
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    @task(8)
    def browse_media(self):
        """Browse albums and photos"""
        # Get random album
        album_id = random.randint(1, 100)
        
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['albums']}/{album_id}", name="Get Album", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    album = response.json()
                    if 'id' in album and 'title' in album:
                        response.success()
                        self._record_request(True, response_time)
                        
                        # Get photos for this album
                        if random.random() < 0.8:  # 80% chance to browse photos
                            self.wait_random(0.3, 1.0)
                            self.browse_album_photos(album_id)
                    else:
                        response.failure("Missing album data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def browse_album_photos(self, album_id: int):
        """Browse photos in an album"""
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['albums']}/{album_id}/photos", name="Get Album Photos", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    photos = response.json()
                    if isinstance(photos, list):
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('album_photos_loaded', len(photos), {
                            'album_id': str(album_id)
                        })
                        
                        # Simulate viewing individual photos
                        for photo in photos[:3]:  # View first 3 photos
                            if random.random() < 0.3:  # 30% chance to view photo details
                                self.wait_random(0.2, 0.5)
                                self.view_photo(photo['id'])
                    else:
                        response.failure("Invalid photos data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def view_photo(self, photo_id: int):
        """View photo details"""
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['photos']}/{photo_id}", name="View Photo", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    photo = response.json()
                    if 'id' in photo and 'url' in photo:
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('photo_viewed', 1.0, {
                            'photo_id': str(photo_id)
                        })
                    else:
                        response.failure("Missing photo data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    @task(3)
    def manage_todos(self):
        """Manage todo items"""
        # Get user's todos
        user_id = self.user_session_data['user_id']
        
        start_time = time.time()
        with self.client.get(f"{API_ENDPOINTS['users']}/{user_id}/todos", name="Get User Todos", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    todos = response.json()
                    if isinstance(todos, list):
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('user_todos_loaded', len(todos), {
                            'user_id': str(user_id)
                        })
                        
                        # Simulate todo management
                        if todos:
                            # Update a random todo
                            todo = random.choice(todos)
                            if random.random() < 0.4:  # 40% chance to update
                                self.wait_random(0.5, 1.0)
                                self.update_todo(todo['id'], not todo['completed'])
                    else:
                        response.failure("Invalid todos data")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    def update_todo(self, todo_id: int, completed: bool):
        """Update todo completion status"""
        todo_data = {
            'completed': completed
        }
        
        start_time = time.time()
        with self.client.patch(f"{API_ENDPOINTS['todos']}/{todo_id}", json=todo_data, name="Update Todo", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    updated_todo = response.json()
                    if 'id' in updated_todo:
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('todo_updated', 1.0, {
                            'todo_id': str(todo_id),
                            'completed': str(completed)
                        })
                    else:
                        response.failure("No ID in updated todo")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)
    
    @task(2)
    def search_and_filter(self):
        """Perform search and filtering operations"""
        # Search posts by title
        search_terms = ['qui', 'sunt', 'et', 'in', 'ut', 'aut', 'est', 'ad']
        search_term = random.choice(search_terms)
        
        start_time = time.time()
        params = {
            'title_like': search_term
        }
        
        with self.client.get(API_ENDPOINTS['posts'], params=params, name="Search Posts", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            if response.status_code == 200:
                try:
                    posts = response.json()
                    if isinstance(posts, list):
                        response.success()
                        self._record_request(True, response_time)
                        record_custom_metric('posts_searched', len(posts), {
                            'search_term': search_term
                        })
                    else:
                        response.failure("Invalid search results")
                        self._record_request(False, response_time)
                except Exception as e:
                    response.failure(f"Invalid JSON: {str(e)}")
                    self._record_request(False, response_time)
            else:
                response.failure(f"Status code: {response.status_code}")
                self._record_request(False, response_time)

class LoadTestConfig:
    """Configuration for load tests"""
    
    # Test parameters
    USERS = 25
    SPAWN_RATE = 2
    DURATION = 300  # 5 minutes
    
    # Performance thresholds
    MAX_RESPONSE_TIME = 2000  # milliseconds
    MAX_ERROR_RATE = 0.02  # 2%
    MIN_THROUGHPUT = 50  # requests per second
    
    # Load patterns
    STEADY_LOAD = {
        'users': 25,
        'spawn_rate': 2,
        'duration': 300
    }
    
    RAMP_UP_LOAD = {
        'users': 50,
        'spawn_rate': 1,
        'duration': 600
    }

# Event handlers for load test monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    logger.info("Load test started")
    record_custom_metric('load_test_started', 1.0, {
        'environment': environment.host
    })

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    logger.info("Load test stopped")
    record_custom_metric('load_test_stopped', 1.0, {
        'environment': environment.host
    })

# Example usage
if __name__ == "__main__":
    # This would typically be run through the locust command
    # locust -f load_test.py --host=https://jsonplaceholder.typicode.com --users=25 --spawn-rate=2 --run-time=300s
    pass 