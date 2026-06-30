"""
Data generation utilities for the Locust Performance Testing Framework
"""

import random
import string
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from faker import Faker
from dataclasses import dataclass, field
from enum import Enum

# Initialize Faker with locale
fake = Faker('en_US')

class DataType(Enum):
    """Enumeration of data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    DATETIME = "datetime"
    UUID = "uuid"
    URL = "url"
    JSON = "json"
    LIST = "list"

@dataclass
class DataSpec:
    """Data specification for generating test data"""
    type: DataType
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    pattern: Optional[str] = None
    nullable: bool = False
    unique: bool = False
    format: Optional[str] = None

@dataclass
class User:
    """User data model"""
    id: int
    name: str
    username: str
    email: str
    phone: str
    website: str
    company: str
    address: Dict[str, str]
    geo: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'company': self.company,
            'address': self.address,
            'geo': self.geo
        }

@dataclass
class Post:
    """Post data model"""
    id: int
    title: str
    body: str
    userId: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert post to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'userId': self.userId
        }

@dataclass
class Comment:
    """Comment data model"""
    id: int
    postId: int
    name: str
    email: str
    body: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'postId': self.postId,
            'name': self.name,
            'email': self.email,
            'body': self.body
        }

@dataclass
class Album:
    """Album data model"""
    id: int
    title: str
    userId: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert album to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'userId': self.userId
        }

@dataclass
class Photo:
    """Photo data model"""
    id: int
    albumId: int
    title: str
    url: str
    thumbnailUrl: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert photo to dictionary"""
        return {
            'id': self.id,
            'albumId': self.albumId,
            'title': self.title,
            'url': self.url,
            'thumbnailUrl': self.thumbnailUrl
        }

@dataclass
class Todo:
    """Todo data model"""
    id: int
    userId: int
    title: str
    completed: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert todo to dictionary"""
        return {
            'id': self.id,
            'userId': self.userId,
            'title': self.title,
            'completed': self.completed
        }

class DataGenerator:
    """Data generator for creating test data"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize data generator with optional seed"""
        if seed:
            random.seed(seed)
            fake.seed_instance(seed)
        
        self.generated_data = {
            'users': [],
            'posts': [],
            'comments': [],
            'albums': [],
            'photos': [],
            'todos': []
        }
        
        self.unique_values = set()
    
    def generate_value(self, spec: DataSpec) -> Any:
        """Generate a value based on the specification"""
        if spec.nullable and random.random() < 0.1:  # 10% chance of null
            return None
        
        if spec.choices:
            return random.choice(spec.choices)
        
        if spec.type == DataType.STRING:
            return self._generate_string(spec)
        elif spec.type == DataType.INTEGER:
            return self._generate_integer(spec)
        elif spec.type == DataType.FLOAT:
            return self._generate_float(spec)
        elif spec.type == DataType.BOOLEAN:
            return random.choice([True, False])
        elif spec.type == DataType.EMAIL:
            return fake.email()
        elif spec.type == DataType.PHONE:
            return fake.phone_number()
        elif spec.type == DataType.DATE:
            return fake.date()
        elif spec.type == DataType.DATETIME:
            return fake.date_time()
        elif spec.type == DataType.UUID:
            return fake.uuid4()
        elif spec.type == DataType.URL:
            return fake.url()
        elif spec.type == DataType.JSON:
            return self._generate_json(spec)
        elif spec.type == DataType.LIST:
            return self._generate_list(spec)
        else:
            raise ValueError(f"Unsupported data type: {spec.type}")
    
    def _generate_string(self, spec: DataSpec) -> str:
        """Generate a random string"""
        min_len = spec.min_length or 1
        max_len = spec.max_length or 100
        
        if spec.pattern:
            # Generate string based on pattern
            return fake.bothify(spec.pattern)
        
        # Generate random string
        length = random.randint(min_len, max_len)
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    def _generate_integer(self, spec: DataSpec) -> int:
        """Generate a random integer"""
        min_val = int(spec.min_value) if spec.min_value else 1
        max_val = int(spec.max_value) if spec.max_value else 1000
        
        value = random.randint(min_val, max_val)
        
        if spec.unique:
            while value in self.unique_values:
                value = random.randint(min_val, max_val)
            self.unique_values.add(value)
        
        return value
    
    def _generate_float(self, spec: DataSpec) -> float:
        """Generate a random float"""
        min_val = float(spec.min_value) if spec.min_value else 0.0
        max_val = float(spec.max_value) if spec.max_value else 1000.0
        
        return random.uniform(min_val, max_val)
    
    def _generate_json(self, spec: DataSpec) -> Dict[str, Any]:
        """Generate random JSON object"""
        keys = ['key1', 'key2', 'key3', 'key4', 'key5']
        selected_keys = random.sample(keys, random.randint(1, len(keys)))
        
        return {
            key: fake.word() for key in selected_keys
        }
    
    def _generate_list(self, spec: DataSpec) -> List[Any]:
        """Generate random list"""
        min_len = spec.min_length or 1
        max_len = spec.max_length or 10
        length = random.randint(min_len, max_len)
        
        return [fake.word() for _ in range(length)]
    
    def generate_user(self, user_id: Optional[int] = None) -> User:
        """Generate a user"""
        if user_id is None:
            user_id = random.randint(1, 10000)
        
        profile = fake.profile()
        
        user = User(
            id=user_id,
            name=profile['name'],
            username=profile['username'],
            email=profile['mail'],
            phone=fake.phone_number(),
            website=fake.url(),
            company=fake.company(),
            address={
                'street': fake.street_address(),
                'suite': fake.secondary_address(),
                'city': fake.city(),
                'zipcode': fake.zipcode(),
                'geo': {
                    'lat': float(fake.latitude()),
                    'lng': float(fake.longitude())
                }
            },
            geo={
                'lat': float(fake.latitude()),
                'lng': float(fake.longitude())
            }
        )
        
        self.generated_data['users'].append(user)
        return user
    
    def generate_post(self, post_id: Optional[int] = None, user_id: Optional[int] = None) -> Post:
        """Generate a post"""
        if post_id is None:
            post_id = random.randint(1, 100000)
        
        if user_id is None:
            user_id = random.randint(1, 10)
        
        post = Post(
            id=post_id,
            title=fake.sentence(nb_words=6),
            body=fake.text(max_nb_chars=200),
            userId=user_id
        )
        
        self.generated_data['posts'].append(post)
        return post
    
    def generate_comment(self, comment_id: Optional[int] = None, post_id: Optional[int] = None) -> Comment:
        """Generate a comment"""
        if comment_id is None:
            comment_id = random.randint(1, 100000)
        
        if post_id is None:
            post_id = random.randint(1, 100)
        
        comment = Comment(
            id=comment_id,
            postId=post_id,
            name=fake.name(),
            email=fake.email(),
            body=fake.text(max_nb_chars=100)
        )
        
        self.generated_data['comments'].append(comment)
        return comment
    
    def generate_album(self, album_id: Optional[int] = None, user_id: Optional[int] = None) -> Album:
        """Generate an album"""
        if album_id is None:
            album_id = random.randint(1, 100000)
        
        if user_id is None:
            user_id = random.randint(1, 10)
        
        album = Album(
            id=album_id,
            title=fake.sentence(nb_words=4),
            userId=user_id
        )
        
        self.generated_data['albums'].append(album)
        return album
    
    def generate_photo(self, photo_id: Optional[int] = None, album_id: Optional[int] = None) -> Photo:
        """Generate a photo"""
        if photo_id is None:
            photo_id = random.randint(1, 100000)
        
        if album_id is None:
            album_id = random.randint(1, 100)
        
        photo = Photo(
            id=photo_id,
            albumId=album_id,
            title=fake.sentence(nb_words=3),
            url=fake.image_url(),
            thumbnailUrl=fake.image_url(width=150, height=150)
        )
        
        self.generated_data['photos'].append(photo)
        return photo
    
    def generate_todo(self, todo_id: Optional[int] = None, user_id: Optional[int] = None) -> Todo:
        """Generate a todo"""
        if todo_id is None:
            todo_id = random.randint(1, 100000)
        
        if user_id is None:
            user_id = random.randint(1, 10)
        
        todo = Todo(
            id=todo_id,
            userId=user_id,
            title=fake.sentence(nb_words=5),
            completed=random.choice([True, False])
        )
        
        self.generated_data['todos'].append(todo)
        return todo
    
    def generate_bulk_users(self, count: int) -> List[User]:
        """Generate multiple users"""
        return [self.generate_user() for _ in range(count)]
    
    def generate_bulk_posts(self, count: int) -> List[Post]:
        """Generate multiple posts"""
        return [self.generate_post() for _ in range(count)]
    
    def generate_bulk_comments(self, count: int) -> List[Comment]:
        """Generate multiple comments"""
        return [self.generate_comment() for _ in range(count)]
    
    def generate_bulk_albums(self, count: int) -> List[Album]:
        """Generate multiple albums"""
        return [self.generate_album() for _ in range(count)]
    
    def generate_bulk_photos(self, count: int) -> List[Photo]:
        """Generate multiple photos"""
        return [self.generate_photo() for _ in range(count)]
    
    def generate_bulk_todos(self, count: int) -> List[Todo]:
        """Generate multiple todos"""
        return [self.generate_todo() for _ in range(count)]
    
    def generate_random_payload(self, schema: Dict[str, DataSpec]) -> Dict[str, Any]:
        """Generate random payload based on schema"""
        payload = {}
        
        for key, spec in schema.items():
            payload[key] = self.generate_value(spec)
        
        return payload
    
    def generate_csv_data(self, schema: Dict[str, DataSpec], count: int) -> List[Dict[str, Any]]:
        """Generate CSV data"""
        return [self.generate_random_payload(schema) for _ in range(count)]
    
    def generate_json_data(self, schema: Dict[str, DataSpec], count: int) -> str:
        """Generate JSON data"""
        data = self.generate_csv_data(schema, count)
        return json.dumps(data, indent=2, default=str)
    
    def save_to_file(self, data: Any, filename: str, format: str = 'json'):
        """Save data to file"""
        with open(filename, 'w') as f:
            if format == 'json':
                json.dump(data, f, indent=2, default=str)
            elif format == 'csv':
                import csv
                if isinstance(data, list) and data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
    
    def clear_generated_data(self):
        """Clear all generated data"""
        self.generated_data = {
            'users': [],
            'posts': [],
            'comments': [],
            'albums': [],
            'photos': [],
            'todos': []
        }
        self.unique_values.clear()
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics of generated data"""
        return {
            key: len(values) for key, values in self.generated_data.items()
        }

# Common data schemas
USER_SCHEMA = {
    'name': DataSpec(DataType.STRING, min_length=5, max_length=50),
    'username': DataSpec(DataType.STRING, min_length=3, max_length=20),
    'email': DataSpec(DataType.EMAIL),
    'phone': DataSpec(DataType.PHONE),
    'website': DataSpec(DataType.URL),
    'company': DataSpec(DataType.STRING, min_length=5, max_length=30)
}

POST_SCHEMA = {
    'title': DataSpec(DataType.STRING, min_length=10, max_length=100),
    'body': DataSpec(DataType.STRING, min_length=50, max_length=500),
    'userId': DataSpec(DataType.INTEGER, min_value=1, max_value=10)
}

COMMENT_SCHEMA = {
    'postId': DataSpec(DataType.INTEGER, min_value=1, max_value=100),
    'name': DataSpec(DataType.STRING, min_length=5, max_length=50),
    'email': DataSpec(DataType.EMAIL),
    'body': DataSpec(DataType.STRING, min_length=20, max_length=200)
}

ALBUM_SCHEMA = {
    'title': DataSpec(DataType.STRING, min_length=5, max_length=50),
    'userId': DataSpec(DataType.INTEGER, min_value=1, max_value=10)
}

PHOTO_SCHEMA = {
    'albumId': DataSpec(DataType.INTEGER, min_value=1, max_value=100),
    'title': DataSpec(DataType.STRING, min_length=5, max_length=50),
    'url': DataSpec(DataType.URL),
    'thumbnailUrl': DataSpec(DataType.URL)
}

TODO_SCHEMA = {
    'userId': DataSpec(DataType.INTEGER, min_value=1, max_value=10),
    'title': DataSpec(DataType.STRING, min_length=10, max_length=100),
    'completed': DataSpec(DataType.BOOLEAN)
}

# Utility functions
def create_test_data_generator(seed: Optional[int] = None) -> DataGenerator:
    """Create a test data generator instance"""
    return DataGenerator(seed=seed)

def generate_test_users(count: int = 10) -> List[Dict[str, Any]]:
    """Generate test users"""
    generator = create_test_data_generator()
    users = generator.generate_bulk_users(count)
    return [user.to_dict() for user in users]

def generate_test_posts(count: int = 100) -> List[Dict[str, Any]]:
    """Generate test posts"""
    generator = create_test_data_generator()
    posts = generator.generate_bulk_posts(count)
    return [post.to_dict() for post in posts]

def generate_test_comments(count: int = 500) -> List[Dict[str, Any]]:
    """Generate test comments"""
    generator = create_test_data_generator()
    comments = generator.generate_bulk_comments(count)
    return [comment.to_dict() for comment in comments]

def generate_test_albums(count: int = 100) -> List[Dict[str, Any]]:
    """Generate test albums"""
    generator = create_test_data_generator()
    albums = generator.generate_bulk_albums(count)
    return [album.to_dict() for album in albums]

def generate_test_photos(count: int = 5000) -> List[Dict[str, Any]]:
    """Generate test photos"""
    generator = create_test_data_generator()
    photos = generator.generate_bulk_photos(count)
    return [photo.to_dict() for photo in photos]

def generate_test_todos(count: int = 200) -> List[Dict[str, Any]]:
    """Generate test todos"""
    generator = create_test_data_generator()
    todos = generator.generate_bulk_todos(count)
    return [todo.to_dict() for todo in todos]

def generate_random_data(data_type: str, count: int = 1) -> List[Dict[str, Any]]:
    """Generate random data of specified type"""
    generator = create_test_data_generator()
    
    if data_type == 'users':
        return generate_test_users(count)
    elif data_type == 'posts':
        return generate_test_posts(count)
    elif data_type == 'comments':
        return generate_test_comments(count)
    elif data_type == 'albums':
        return generate_test_albums(count)
    elif data_type == 'photos':
        return generate_test_photos(count)
    elif data_type == 'todos':
        return generate_test_todos(count)
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

# Example usage
if __name__ == "__main__":
    # Create data generator
    generator = create_test_data_generator(seed=42)
    
    # Generate sample data
    users = generator.generate_bulk_users(5)
    posts = generator.generate_bulk_posts(10)
    comments = generator.generate_bulk_comments(20)
    
    # Print statistics
    print("Generated data statistics:")
    print(generator.get_statistics())
    
    # Save to files
    generator.save_to_file([user.to_dict() for user in users], 'users.json')
    generator.save_to_file([post.to_dict() for post in posts], 'posts.json')
    generator.save_to_file([comment.to_dict() for comment in comments], 'comments.json')
    
    print("Data saved to files successfully!") 