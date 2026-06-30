#!/usr/bin/env python3
"""
Test runner for the Locust Performance Testing Framework
"""

import os
import sys
import argparse
import subprocess
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add the framework to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.environments import EnvironmentConfig
from utils.helpers import DateTimeHelper, StringHelper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestRunner:
    """Test runner for Locust performance tests"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.scenarios_dir = self.base_dir / "scenarios"
        self.reports_dir = self.base_dir / "reports"
        self.logs_dir = self.base_dir / "logs"
        
        # Ensure directories exist
        self.reports_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.env_config = EnvironmentConfig()
    
    def get_available_scenarios(self) -> List[str]:
        """Get list of available test scenarios"""
        scenarios = []
        if self.scenarios_dir.exists():
            for file in self.scenarios_dir.glob("*.py"):
                if file.name != "__init__.py":
                    scenarios.append(file.stem)
        return scenarios
    
    def get_available_environments(self) -> List[str]:
        """Get list of available environments"""
        return self.env_config.get_available_environments()
    
    def build_locust_command(self, scenario: str, environment: str, 
                           test_type: str = 'load', **kwargs) -> Tuple[List[str], Dict[str, str]]:
        """Build locust command based on parameters"""
        scenario_file = self.scenarios_dir / f"{scenario}.py"
        
        if not scenario_file.exists():
            raise ValueError(f"Scenario file not found: {scenario_file}")
        
        # Get test configuration
        config = self.env_config.get_test_config(environment, test_type)
        host = self.env_config.get_host(environment)
        
        # Build base command
        cmd = [
            "locust",
            "-f", str(scenario_file),
            "--host", host,
            "--users", str(kwargs.get('users', config.get('users', 10))),
            "--spawn-rate", str(kwargs.get('spawn_rate', config.get('spawn_rate', 1))),
            "--headless"  # Run without web UI by default
        ]
        
        # Add duration if specified
        duration = kwargs.get('duration', config.get('duration'))
        if duration:
            if isinstance(duration, int):
                cmd.extend(["--run-time", f"{duration}s"])
            else:
                cmd.extend(["--run-time", str(duration)])
        
        # Add report generation
        timestamp = DateTimeHelper.get_current_timestamp().replace(" ", "_").replace(":", "-")
        report_name = f"{scenario}_{environment}_{test_type}_{timestamp}"
        
        html_report = self.reports_dir / f"{report_name}.html"
        csv_report = self.reports_dir / f"{report_name}"
        log_file = self.logs_dir / f"{report_name}.log"
        
        cmd.extend([
            "--html", str(html_report),
            "--csv", str(csv_report),
            "--logfile", str(log_file),
            "--loglevel", kwargs.get('log_level', 'INFO')
        ])
        
        # Add custom tags
        tags = kwargs.get('tags', [])
        if tags:
            cmd.extend(["--tags"] + tags)
        
        # Add environment variables
        return cmd, {
            "LOCUST_ENVIRONMENT": environment,
            "LOCUST_TEST_TYPE": test_type,
            "LOCUST_REPORT_NAME": report_name
        }
    
    def run_test(self, scenario: str, environment: str = 'dev', 
                test_type: str = 'load', **kwargs) -> int:
        """Run a specific test scenario"""
        logger.info(f"Starting {test_type} test: {scenario} on {environment}")
        
        try:
            # Validate inputs
            if scenario not in self.get_available_scenarios():
                raise ValueError(f"Invalid scenario: {scenario}")
            
            if environment not in self.get_available_environments():
                raise ValueError(f"Invalid environment: {environment}")
            
            # Build command
            cmd, env_vars = self.build_locust_command(scenario, environment, test_type, **kwargs)
            
            # Set environment variables
            env = os.environ.copy()
            env.update(env_vars)
            
            # Log command
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Run the test
            result = subprocess.run(cmd, env=env, capture_output=False)
            
            if result.returncode == 0:
                logger.info(f"Test completed successfully: {scenario}")
            else:
                logger.error(f"Test failed with return code: {result.returncode}")
            
            return result.returncode
            
        except Exception as e:
            logger.error(f"Error running test: {str(e)}")
            return 1
    
    def run_smoke_tests(self, environment: str = 'dev') -> int:
        """Run smoke tests"""
        logger.info(f"Running smoke tests on {environment}")
        
        return self.run_test(
            scenario='smoke_test',
            environment=environment,
            test_type='smoke',
            users=5,
            spawn_rate=1,
            duration=60
        )
    
    def run_load_tests(self, environment: str = 'test') -> int:
        """Run load tests"""
        logger.info(f"Running load tests on {environment}")
        
        return self.run_test(
            scenario='load_test',
            environment=environment,
            test_type='load',
            users=25,
            spawn_rate=2,
            duration=300
        )
    
    def run_stress_tests(self, environment: str = 'staging') -> int:
        """Run stress tests"""
        logger.info(f"Running stress tests on {environment}")
        
        # Get stress test configuration
        config = self.env_config.get_test_config(environment, 'stress')
        
        return self.run_test(
            scenario='load_test',  # Use load test scenario with higher load
            environment=environment,
            test_type='stress',
            users=config.get('users', 100),
            spawn_rate=config.get('spawn_rate', 10),
            duration=config.get('duration', 600)
        )
    
    def run_spike_tests(self, environment: str = 'staging') -> int:
        """Run spike tests"""
        logger.info(f"Running spike tests on {environment}")
        
        # Get spike test configuration
        config = self.env_config.get_test_config(environment, 'spike')
        
        return self.run_test(
            scenario='load_test',  # Use load test scenario with spike load
            environment=environment,
            test_type='spike',
            users=config.get('users', 200),
            spawn_rate=config.get('spawn_rate', 50),
            duration=config.get('duration', 180)
        )
    
    def run_endurance_tests(self, environment: str = 'staging') -> int:
        """Run endurance tests"""
        logger.info(f"Running endurance tests on {environment}")
        
        # Get endurance test configuration
        config = self.env_config.get_test_config(environment, 'endurance')
        
        return self.run_test(
            scenario='load_test',  # Use load test scenario with long duration
            environment=environment,
            test_type='endurance',
            users=config.get('users', 50),
            spawn_rate=config.get('spawn_rate', 5),
            duration=config.get('duration', 3600)  # 1 hour
        )
    
    def run_all_tests(self, environment: str = 'test') -> int:
        """Run all test types in sequence"""
        logger.info(f"Running all tests on {environment}")
        
        tests = [
            ('smoke', self.run_smoke_tests),
            ('load', self.run_load_tests),
            ('stress', self.run_stress_tests)
        ]
        
        failed_tests = []
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running {test_name} tests")
            logger.info(f"{'='*50}")
            
            try:
                result = test_func(environment)
                if result != 0:
                    failed_tests.append(test_name)
            except Exception as e:
                logger.error(f"Failed to run {test_name} tests: {str(e)}")
                failed_tests.append(test_name)
        
        if failed_tests:
            logger.error(f"Failed tests: {', '.join(failed_tests)}")
            return 1
        else:
            logger.info("All tests completed successfully")
            return 0
    
    def list_scenarios(self):
        """List available test scenarios"""
        scenarios = self.get_available_scenarios()
        print("Available test scenarios:")
        for scenario in scenarios:
            print(f"  - {scenario}")
    
    def list_environments(self):
        """List available environments"""
        environments = self.get_available_environments()
        print("Available environments:")
        for env in environments:
            description = self.env_config.get_environment_description(env)
            print(f"  - {env}: {description}")
    
    def show_environment_config(self, environment: str):
        """Show configuration for a specific environment"""
        if environment not in self.get_available_environments():
            print(f"Invalid environment: {environment}")
            return
        
        self.env_config.print_environment_info(environment)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Locust Performance Testing Framework Runner")
    parser.add_argument("--scenario", help="Test scenario to run")
    parser.add_argument("--environment", "-e", default="dev", help="Target environment")
    parser.add_argument("--test-type", "-t", default="load", 
                       choices=['smoke', 'load', 'stress', 'spike', 'endurance'],
                       help="Type of test to run")
    parser.add_argument("--users", "-u", type=int, help="Number of users")
    parser.add_argument("--spawn-rate", "-r", type=int, help="Spawn rate")
    parser.add_argument("--duration", "-d", help="Test duration (e.g., 60s, 5m, 1h)")
    parser.add_argument("--tags", nargs="+", help="Tags to include")
    parser.add_argument("--log-level", default="INFO", 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help="Log level")
    
    # Action commands
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--stress", action="store_true", help="Run stress tests")
    parser.add_argument("--spike", action="store_true", help="Run spike tests")
    parser.add_argument("--endurance", action="store_true", help="Run endurance tests")
    parser.add_argument("--all", action="store_true", help="Run all test types")
    
    # Information commands
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
    parser.add_argument("--list-environments", action="store_true", help="List available environments")
    parser.add_argument("--show-config", help="Show configuration for environment")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        # Information commands
        if args.list_scenarios:
            runner.list_scenarios()
            return 0
        
        if args.list_environments:
            runner.list_environments()
            return 0
        
        if args.show_config:
            runner.show_environment_config(args.show_config)
            return 0
        
        # Test execution commands
        if args.all:
            return runner.run_all_tests(args.environment)
        
        if args.smoke:
            return runner.run_smoke_tests(args.environment)
        
        if args.load:
            return runner.run_load_tests(args.environment)
        
        if args.stress:
            return runner.run_stress_tests(args.environment)
        
        if args.spike:
            return runner.run_spike_tests(args.environment)
        
        if args.endurance:
            return runner.run_endurance_tests(args.environment)
        
        # Custom test execution
        if args.scenario:
            kwargs = {}
            if args.users:
                kwargs['users'] = args.users
            if args.spawn_rate:
                kwargs['spawn_rate'] = args.spawn_rate
            if args.duration:
                kwargs['duration'] = args.duration
            if args.tags:
                kwargs['tags'] = args.tags
            kwargs['log_level'] = args.log_level
            
            return runner.run_test(args.scenario, args.environment, args.test_type, **kwargs)
        
        # Default: show help
        parser.print_help()
        return 0
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 