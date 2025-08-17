#!/usr/bin/env python3
"""Create a test target project with intentional issues for evolution testing."""

from pathlib import Path


def create_test_project():
    """Create test project with various code issues."""

    # Create project directory
    project_dir = Path("/tmp/test_evolution_target")
    project_dir.mkdir(exist_ok=True, parents=True)

    # Create subdirectories
    (project_dir / "services").mkdir(exist_ok=True)
    (project_dir / "utils").mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)

    print(f"📁 Creating test project at: {project_dir}")

    # 1. main.py - Missing docstrings, type hints, high complexity
    main_py = """
# Main application file
import json
import requests
from datetime import datetime

def process_data(data, config):
    results = []
    errors = []

    for item in data:
        if item.get('type') == 'A':
            if item.get('value') > 100:
                if item.get('priority') == 'high':
                    if item.get('status') == 'active':
                        result = item['value'] * 2.5
                        if result > 500:
                            results.append({'item': item['id'], 'result': result, 'flag': 'high'})
                        else:
                            results.append({'item': item['id'], 'result': result, 'flag': 'medium'})
                    else:
                        result = item['value'] * 1.5
                        results.append({'item': item['id'], 'result': result, 'flag': 'low'})
                else:
                    result = item['value'] * 1.2
                    results.append({'item': item['id'], 'result': result, 'flag': 'low'})
            else:
                errors.append(f"Value too low for item {item['id']}")
        elif item.get('type') == 'B':
            if item.get('value') > 50:
                result = item['value'] ** 2
                results.append({'item': item['id'], 'result': result, 'flag': 'special'})
            else:
                errors.append(f"Type B item {item['id']} below threshold")
        else:
            errors.append(f"Unknown type for item {item['id']}")

    return results, errors

class DataProcessor:
    def __init__(self):
        self.data = []
        self.config = {}
        self.results = []
        self.timestamp = None

    def load_data(self, source):
        if isinstance(source, str):
            with open(source, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = source

    def process(self):
        self.timestamp = datetime.now()
        self.results = []

        for item in self.data:
            processed = self.process_item(item)
            if processed:
                self.results.append(processed)

    def process_item(self, item):
        value = item.get('value', 0)
        multiplier = self.config.get('multiplier', 1.0)

        if value > 0:
            return value * multiplier
        else:
            return None

    def save_results(self, output_file):
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': str(self.timestamp),
                'results': self.results
            }, f)

def fetch_data(url, timeout=30):
    response = requests.get(url, timeout=timeout)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def validate_config(config):
    required_keys = ['api_key', 'endpoint', 'timeout']
    for key in required_keys:
        if key not in config:
            return False
    return True

def main():
    config = {
        'api_key': 'test123',
        'endpoint': 'https://api.example.com',
        'timeout': 30
    }

    if validate_config(config):
        processor = DataProcessor()
        processor.config = config
        processor.load_data('data.json')
        processor.process()
        processor.save_results('output.json')
        print("Processing complete")
    else:
        print("Invalid configuration")

if __name__ == "__main__":
    main()
"""
    (project_dir / "main.py").write_text(main_py)
    print("  ✅ Created main.py with complexity issues")

    # 2. services/calculator.py - Missing type hints and docstrings
    calculator_py = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return None
    return a / b

def power(base, exponent):
    return base ** exponent

def factorial(n):
    if n < 0:
        return None
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

class Calculator:
    def __init__(self):
        self.memory = 0
        self.history = []

    def add_to_memory(self, value):
        self.memory += value
        self.history.append(('add', value, self.memory))

    def subtract_from_memory(self, value):
        self.memory -= value
        self.history.append(('subtract', value, self.memory))

    def clear_memory(self):
        self.memory = 0
        self.history.append(('clear', 0, 0))

    def get_history(self):
        return self.history
"""
    (project_dir / "services" / "calculator.py").write_text(calculator_py)
    print("  ✅ Created services/calculator.py without type hints")

    # 3. services/validator.py - PEP8 violations and duplicated code
    validator_py = r"""
import re

def validate_email( email ):
    pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match( pattern,email ):
        return True
    else:
        return False

def validate_phone( phone ):
    pattern=r'^\+?1?\d{9,15}$'
    if re.match( pattern,phone ):
        return True
    else:
        return False

def validate_url( url ):
    pattern=r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if re.match( pattern,url ):
        return True
    else:
        return False

def validate_username(username):
    if len(username)<3:
        return False
    if len(username)>20:
        return False
    if not username[0].isalpha():
        return False
    for char in username:
        if not char.isalnum() and char!='_':
            return False
    return True

def validate_password(password):
    if len(password)<8:
        return False
    if len(password)>50:
        return False
    has_upper=False
    has_lower=False
    has_digit=False
    has_special=False

    for char in password:
        if char.isupper():
            has_upper=True
        elif char.islower():
            has_lower=True
        elif char.isdigit():
            has_digit=True
        elif char in '!@#$%^&*()_+-=[]{}|;:,.<>?':
            has_special=True

    if not has_upper:
        return False
    if not has_lower:
        return False
    if not has_digit:
        return False
    if not has_special:
        return False

    return True
"""
    (project_dir / "services" / "validator.py").write_text(validator_py)
    print("  ✅ Created services/validator.py with PEP8 violations")

    # 4. utils/helpers.py - Duplicated code and no error handling
    helpers_py = """
import os
import json

def read_json_file(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def write_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)

def read_text_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    return content

def write_text_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def get_file_size(filepath):
    return os.path.getsize(filepath)

def file_exists(filepath):
    return os.path.exists(filepath)

def create_directory(dirpath):
    os.makedirs(dirpath, exist_ok=True)

def list_files(dirpath):
    files = []
    for item in os.listdir(dirpath):
        if os.path.isfile(os.path.join(dirpath, item)):
            files.append(item)
    return files

def merge_dicts(dict1, dict2):
    result = dict1.copy()
    result.update(dict2)
    return result

def filter_list(items, condition):
    filtered = []
    for item in items:
        if condition(item):
            filtered.append(item)
    return filtered
"""
    (project_dir / "utils" / "helpers.py").write_text(helpers_py)
    print("  ✅ Created utils/helpers.py with no error handling")

    # 5. utils/formatter.py - Magic numbers and no constants
    formatter_py = """
def format_currency(amount):
    if amount >= 1000000:
        return f"${amount/1000000:.2f}M"
    elif amount >= 1000:
        return f"${amount/1000:.2f}K"
    else:
        return f"${amount:.2f}"

def format_percentage(value):
    return f"{value * 100:.2f}%"

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")

def format_time(time_obj):
    return time_obj.strftime("%H:%M:%S")

def truncate_string(text, length):
    if len(text) > length:
        return text[:length-3] + "..."
    return text

def pad_string(text, length, char=' '):
    if len(text) < length:
        padding = char * (length - len(text))
        return text + padding
    return text

def wrap_text(text, width):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\\n'.join(lines)
"""
    (project_dir / "utils" / "formatter.py").write_text(formatter_py)
    print("  ✅ Created utils/formatter.py with magic numbers")

    # 6. tests/test_main.py - Minimal test coverage
    test_main_py = """
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import validate_config

class TestMain(unittest.TestCase):
    def test_validate_config_valid(self):
        config = {
            'api_key': 'test',
            'endpoint': 'http://test.com',
            'timeout': 30
        }
        self.assertTrue(validate_config(config))

    def test_validate_config_invalid(self):
        config = {'api_key': 'test'}
        self.assertFalse(validate_config(config))

if __name__ == '__main__':
    unittest.main()
"""
    (project_dir / "tests" / "test_main.py").write_text(test_main_py)
    print("  ✅ Created tests/test_main.py with minimal coverage")

    # Create __init__.py files
    (project_dir / "services" / "__init__.py").touch()
    (project_dir / "utils" / "__init__.py").touch()
    (project_dir / "tests" / "__init__.py").touch()

    # Create a requirements.txt
    requirements = """requests>=2.28.0
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
"""
    (project_dir / "requirements.txt").write_text(requirements)

    print("\n📊 Project Statistics:")
    print("  - Total Python files: 6")
    print("  - Total lines of code: ~400")
    print("  - Issues to fix:")
    print("    • Missing docstrings: ~30")
    print("    • Missing type hints: ~25")
    print("    • High complexity functions: 3")
    print("    • PEP8 violations: ~15")
    print("    • No error handling: 10+")
    print("    • Magic numbers: 5+")
    print("    • Low test coverage: <10%")

    return project_dir


if __name__ == "__main__":
    project_path = create_test_project()
    print(f"\n✅ Test project created at: {project_path}")
    print("🎯 Ready for evolution testing!")
