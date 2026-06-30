# Locust Performance Testing Framework

A comprehensive Python-based performance testing framework built with Locust for load testing, stress testing, and performance validation of web applications and APIs.

## Features

- 🐍 **Python-based**: Easy to read and write test scenarios using Python
- 🔧 **Modular Architecture**: Reusable components for different testing scenarios
- 📊 **Real-time Monitoring**: Built-in web UI and metrics collection
- 🏗️ **Multi-scenario Support**: Load, stress, spike, and endurance testing
- 🌐 **Web & API Testing**: Support for both web applications and REST APIs
- 📝 **Comprehensive Reporting**: Detailed reports with metrics and visualizations
- 🐳 **Docker Support**: Containerized execution for consistency
- 🔄 **CI/CD Integration**: Easy integration with CI/CD pipelines
- 🎯 **Data-driven Testing**: Support for CSV feeders and dynamic data generation
- 🛠️ **Extensible**: Easy to extend with custom tasks and behaviors

## Project Structure

```
locust-performance-testing-framework/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── docker-compose.yml            # Docker Compose setup
├── run-tests.py                   # Main test runner
├── config/                        # Configuration files
│   ├── __init__.py
│   ├── settings.py               # Application settings
│   └── environments.py           # Environment configurations
├── tasks/                         # Task definitions
│   ├── __init__.py
│   ├── api_tasks.py              # API testing tasks
│   ├── web_tasks.py              # Web application tasks
│   └── mixed_tasks.py            # Mixed testing scenarios
├── scenarios/                     # Test scenarios
│   ├── __init__.py
│   ├── load_test.py              # Load testing scenarios
│   ├── stress_test.py            # Stress testing scenarios
│   ├── spike_test.py             # Spike testing scenarios
│   └── endurance_test.py         # Endurance testing scenarios
├── utils/                         # Utility functions
│   ├── __init__.py
│   ├── data_generator.py         # Test data generation
│   ├── helpers.py                # Helper functions
│   └── custom_clients.py         # Custom client implementations
├── data/                          # Test data files
│   ├── users.csv                 # User test data
│   ├── posts.csv                 # Post test data
│   └── comments.csv              # Comment test data
├── reports/                       # Test reports directory
├── logs/                          # Log files directory
└── tests/                         # Unit tests for the framework
    ├── __init__.py
    ├── test_tasks.py             # Task unit tests
    └── test_utils.py             # Utility unit tests
```

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Docker and Docker Compose (for containerized execution)
- Git (for version control)

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd locust-performance-testing-framework
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Docker Installation

1. Build the Docker image:
```bash
docker-compose build
```

2. Run with Docker Compose:
```bash
docker-compose up
```

## Quick Start

### Running Tests Locally

1. **Basic Load Test**:
```bash
python run-tests.py --scenario load --users 10 --spawn-rate 2 --duration 60
```

2. **Stress Test**:
```bash
python run-tests.py --scenario stress --users 100 --spawn-rate 10 --duration 300
```

3. **Web UI Mode**:
```bash
python run-tests.py --scenario load --web-ui
```

### Running Tests with Docker

1. **Load Test**:
```bash
docker-compose run --rm locust-tests python run-tests.py --scenario load --users 10 --spawn-rate 2 --duration 60
```

2. **Stress Test**:
```bash
docker-compose run --rm locust-tests python run-tests.py --scenario stress --users 100 --spawn-rate 10 --duration 300
```

### Using Environment Variables

```bash
# Set target environment
export ENVIRONMENT=staging
export TARGET_HOST=https://api.staging.example.com

# Run tests
python run-tests.py --scenario load --users 50 --spawn-rate 5 --duration 120
```

## Configuration

### Environment Configuration

Configure different environments in `config/environments.py`:

```python
ENVIRONMENTS = {
    'dev': {
        'host': 'https://jsonplaceholder.typicode.com',
        'users': 10,
        'spawn_rate': 2,
        'duration': 60
    },
    'staging': {
        'host': 'https://staging-api.example.com',
        'users': 50,
        'spawn_rate': 5,
        'duration': 300
    },
    'production': {
        'host': 'https://api.example.com',
        'users': 100,
        'spawn_rate': 10,
        'duration': 600
    }
}
```

### Test Settings

Modify `config/settings.py` to adjust:
- Default test parameters
- Request timeouts
- Custom headers
- Authentication settings
- Logging configuration

## Test Scenarios

### Load Testing
Tests normal expected load to validate system performance:
- Simulates realistic user behavior
- Validates response times under normal conditions
- Checks system stability with expected traffic

### Stress Testing
Tests system limits and breaking points:
- Gradually increases load beyond normal capacity
- Identifies performance bottlenecks
- Tests error handling under high load

### Spike Testing
Tests system behavior under sudden traffic spikes:
- Simulates sudden increases in user activity
- Validates auto-scaling capabilities
- Tests system recovery after spikes

### Endurance Testing
Tests system stability over extended periods:
- Runs moderate load for long durations
- Identifies memory leaks and performance degradation
- Validates system reliability over time

## Task Types

### API Tasks
- **GET Requests**: Retrieve data from endpoints
- **POST Requests**: Create new resources
- **PUT Requests**: Update existing resources
- **DELETE Requests**: Remove resources
- **Authentication**: Login/logout flows

### Web Tasks
- **Page Navigation**: Browse through web pages
- **Form Submission**: Submit forms with data
- **File Upload**: Upload files to the server
- **Session Management**: Handle user sessions

### Mixed Tasks
- **Combined Workflows**: Mix of API and web interactions
- **Realistic User Journeys**: Simulate real user behavior
- **Complex Scenarios**: Multi-step business processes

## Data Management

### CSV Feeders
Use CSV files for test data:
```python
from utils.data_generator import CSVDataFeeder

user_data = CSVDataFeeder('data/users.csv')
user = user_data.get_random_data()
```

### Dynamic Data Generation
Generate test data on-the-fly:
```python
from utils.data_generator import DataGenerator

user_data = DataGenerator.generate_user_data()
post_data = DataGenerator.generate_post_data()
```

## Reporting and Analysis

### Built-in Reports
- **HTML Reports**: Detailed performance metrics
- **Statistics**: Response times, throughput, error rates
- **Charts**: Visual representation of performance data
- **Logs**: Detailed execution logs

### Custom Reporting
Extend reporting with custom metrics:
```python
from locust import events

@events.request.add_listener
def custom_request_handler(request_type, name, response_time, response_length, exception, context, **kwargs):
    # Custom metrics collection
    pass
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Performance Tests
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  performance-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run Performance Tests
      run: |
        python run-tests.py --scenario load --users 50 --spawn-rate 5 --duration 300 --headless
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'python -m venv venv'
                sh 'source venv/bin/activate && pip install -r requirements.txt'
            }
        }
        
        stage('Load Tests') {
            steps {
                sh 'source venv/bin/activate && python run-tests.py --scenario load --users 50 --spawn-rate 5 --duration 300 --headless'
            }
        }
        
        stage('Stress Tests') {
            steps {
                sh 'source venv/bin/activate && python run-tests.py --scenario stress --users 100 --spawn-rate 10 --duration 300 --headless'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: false,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'index.html',
                reportName: 'Performance Test Report'
            ])
        }
    }
}
```

## Advanced Features

### Custom Task Classes
Create custom task behaviors:
```python
from locust import User, task, between
from utils.custom_clients import CustomHttpClient

class CustomUser(User):
    def __init__(self, environment):
        super().__init__(environment)
        self.client = CustomHttpClient()
    
    @task
    def custom_task(self):
        # Custom task implementation
        pass
```

### Real-time Monitoring
Integrate with monitoring systems:
```python
from locust import events
import influxdb

@events.request.add_listener
def send_to_influxdb(request_type, name, response_time, response_length, exception, context, **kwargs):
    # Send metrics to InfluxDB
    pass
```

### Custom Metrics
Track custom business metrics:
```python
from locust import events
from locust.stats import stats_history

@events.request.add_listener
def track_custom_metrics(request_type, name, response_time, response_length, exception, context, **kwargs):
    # Track custom metrics
    pass
```

## Best Practices

### Test Design
- Start with smoke tests before running full load tests
- Use realistic data and user behavior patterns
- Implement proper error handling and retries
- Monitor system resources during tests

### Performance Monitoring
- Set up proper monitoring for target systems
- Monitor both application and infrastructure metrics
- Use distributed testing for high-load scenarios
- Implement alerting for performance degradation

### Data Management
- Use realistic test data that matches production patterns
- Implement proper data cleanup after tests
- Avoid using production data in tests
- Use data feeders for scalable test data management

### Reporting
- Generate comprehensive reports with actionable insights
- Include both technical and business metrics
- Set up automated report distribution
- Archive results for trend analysis

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Check network connectivity
   - Verify target host accessibility
   - Review firewall settings

2. **High Response Times**:
   - Check target system capacity
   - Review test scenario complexity
   - Monitor system resources

3. **Test Failures**:
   - Review test logs for error details
   - Check test data validity
   - Verify test environment setup

### Performance Optimization
- Use connection pooling for better performance
- Implement proper request batching
- Monitor client-side resource usage
- Use distributed testing for high loads

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Check the documentation
- Review existing issues
- Create a new issue with detailed information
- Contact the development team

## Changelog

### Version 1.0.0
- Initial release
- Basic load testing scenarios
- API and web task support
- Docker integration
- Comprehensive reporting

### Version 1.1.0
- Added stress testing scenarios
- Improved data generation
- Enhanced reporting features
- CI/CD integration examples 