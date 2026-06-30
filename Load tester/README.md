# API Load and Stress Testing

A Python-based API Load and Stress Testing project built using **Locust**. It helps evaluate the performance of REST APIs by simulating multiple concurrent users and measuring response time, throughput, and failure rate.

---

## Features

- Load testing for REST APIs
- Stress testing with configurable concurrent users
- Performance metrics collection
- Response time monitoring
- Throughput analysis
- Failure rate tracking
- Reusable test scenarios
- Easy configuration using Python

---

## Tech Stack

- Python 3
- Locust
- Requests
- CSV
- Git

---

## Project Structure

```
API-Load-and-Stress-Testing/
│
├── config/
├── scenarios/
├── tasks/
├── utils/
├── reports/
├── requirements.txt
├── run-tests.py
└── README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/Avtansh88/API-Load-and-Stress-Testing.git
```

Move into the project directory

```bash
cd API-Load-and-Stress-Testing
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Project

Start Locust

```bash
locust
```

or

```bash
python run-tests.py
```

Open your browser

```
http://localhost:8089
```

Configure

- Host URL
- Number of Users
- Spawn Rate

Click **Start Swarming** to begin testing.

---

## Metrics

- Average Response Time
- Minimum Response Time
- Maximum Response Time
- Requests per Second
- Failure Rate
- Total Requests

---

## Use Cases

- REST API Testing
- Load Testing
- Stress Testing
- Performance Validation

---

## Future Improvements

- CSV Report Export
- HTML Report Generation
- Authentication Support
- Docker Support

---

## Author

**Avtansh Tripathi**

GitHub: https://github.com/Avtansh88