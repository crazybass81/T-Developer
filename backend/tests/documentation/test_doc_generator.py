"""Test documentation generator - Day 35"""
import pytest

from src.documentation.api_doc_builder import APIDocBuilder
from src.documentation.changelog_generator import ChangelogGenerator
from src.documentation.doc_generator import DocGenerator


class TestDocGenerator:
    """Test suite for documentation generator"""

    @pytest.fixture
    def generator(self):
        """Create doc generator instance"""
        return DocGenerator()

    def test_initialization(self, generator):
        """Test generator initialization"""
        assert generator is not None
        assert hasattr(generator, "templates")

    def test_generate_api_docs(self, generator):
        """Test API documentation generation"""
        code = """
def get_users():
    '''Get all users'''
    return []

def create_user(name: str, email: str):
    '''Create a new user'''
    return {"id": 1, "name": name}
"""

        # Save to temp file and generate docs
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            docs = generator.generate_api_docs(f.name)

        assert "API Documentation" in docs
        # Basic check since parsing may vary
        assert docs is not None

    def test_generate_user_guide(self, generator):
        """Test user guide generation"""
        config = {
            "title": "My Project",
            "overview": "This is a test project",
            "installation": "pip install myproject",
            "features": ["Feature 1", "Feature 2"],
            "usage": [{"title": "Basic Usage", "code": "import myproject\nmyproject.run()"}],
        }

        guide = generator.generate_user_guide(config)

        assert "My Project" in guide
        assert "Overview" in guide
        assert "Installation" in guide
        assert "pip install myproject" in guide
        assert "Feature 1" in guide

    def test_generate_architecture_docs(self, generator):
        """Test architecture documentation"""
        config = {
            "overview": "Microservices architecture",
            "components": [
                {
                    "name": "API Gateway",
                    "purpose": "Route requests",
                    "technology": "FastAPI",
                    "dependencies": ["Auth Service", "User Service"],
                }
            ],
            "data_flow": [
                {"order": 1, "description": "Client sends request"},
                {"order": 2, "description": "Gateway authenticates"},
            ],
        }

        docs = generator.generate_architecture_docs(config)

        assert "System Architecture" in docs
        assert "API Gateway" in docs
        assert "FastAPI" in docs
        assert "Data Flow" in docs

    def test_generate_readme(self, generator):
        """Test README generation"""
        project = {
            "name": "Awesome Project",
            "description": "An awesome project",
            "installation": "pip install awesome",
            "features": ["Fast", "Reliable"],
            "license": "MIT",
        }

        readme = generator.generate_readme(project)

        assert "# Awesome Project" in readme
        assert "Installation" in readme
        assert "Features" in readme
        assert "MIT" in readme

    def test_generate_changelog(self, generator):
        """Test changelog generation"""
        versions = [
            {
                "version": "1.1.0",
                "date": "2024-01-01",
                "added": ["New feature X", "Support for Y"],
                "fixed": ["Bug in Z"],
            },
            {"version": "1.0.0", "date": "2023-12-01", "added": ["Initial release"]},
        ]

        changelog = generator.generate_changelog(versions)

        assert "Changelog" in changelog
        assert "1.1.0" in changelog
        assert "New feature X" in changelog
        assert "Bug in Z" in changelog

    def test_extract_docstrings(self, generator):
        """Test docstring extraction"""
        code = '''
def function_with_doc():
    """This is a docstring"""
    pass

class MyClass:
    """Class docstring"""
    def method(self):
        """Method docstring"""
        pass
'''

        docstrings = generator.extract_docstrings(code)

        assert "function_with_doc" in docstrings
        assert docstrings["function_with_doc"] == "This is a docstring"
        assert "MyClass" in docstrings
        assert docstrings["MyClass"] == "Class docstring"


class TestAPIDocBuilder:
    """Test API documentation builder"""

    @pytest.fixture
    def builder(self):
        """Create API doc builder"""
        return APIDocBuilder()

    def test_document_endpoint(self, builder):
        """Test endpoint documentation"""

        def get_user(user_id: int, include_details: bool = False):
            """Get user by ID"""
            return {}

        doc = builder.document_endpoint(get_user, "/users/{user_id}", "GET")

        assert doc["path"] == "/users/{user_id}"
        assert doc["method"] == "GET"
        assert "Get user by ID" in doc["summary"]
        assert len(doc["parameters"]) == 2

    def test_generate_openapi(self, builder):
        """Test OpenAPI generation"""

        def get_users():
            """Get all users"""
            return []

        builder.document_endpoint(get_users, "/users", "GET")

        spec = builder.generate_openapi({"title": "Test API", "version": "1.0.0"})

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert "/users" in spec["paths"]
        assert "get" in spec["paths"]["/users"]

    def test_generate_markdown(self, builder):
        """Test Markdown documentation"""

        def create_user(name: str, email: str):
            """Create new user"""
            return {}

        builder.document_endpoint(create_user, "/users", "POST")

        markdown = builder.generate_markdown()

        assert "# API Documentation" in markdown
        assert "POST /users" in markdown
        assert "Create new user" in markdown
        assert "Parameters:" in markdown

    def test_generate_postman_collection(self, builder):
        """Test Postman collection generation"""

        def get_products():
            """Get products"""
            return []

        builder.document_endpoint(get_products, "/products", "GET")

        collection = builder.generate_postman_collection("My API")

        assert collection["info"]["name"] == "My API"
        assert len(collection["item"]) == 1
        assert collection["item"][0]["request"]["method"] == "GET"


class TestChangelogGenerator:
    """Test changelog generator"""

    @pytest.fixture
    def generator(self):
        """Create changelog generator"""
        return ChangelogGenerator()

    def test_initialization(self, generator):
        """Test generator initialization"""
        assert generator is not None
        assert "feat" in generator.categories
        assert "fix" in generator.categories

    def test_group_commits(self, generator):
        """Test commit grouping"""
        commits = [
            {
                "hash": "abc123",
                "message": "feat: add new feature",
                "author": "dev",
                "date": "2024-01-01",
            },
            {"hash": "def456", "message": "fix: fix bug", "author": "dev", "date": "2024-01-01"},
            {
                "hash": "ghi789",
                "message": "docs: update readme",
                "author": "dev",
                "date": "2024-01-01",
            },
        ]

        grouped = generator._group_commits(commits)

        assert "feat" in grouped
        assert "fix" in grouped
        assert "docs" in grouped
        assert len(grouped["feat"]) == 1

    def test_format_changelog(self, generator):
        """Test changelog formatting"""
        grouped = {
            "feat": [{"hash": "abc123", "description": "add new feature", "scope": "api"}],
            "fix": [{"hash": "def456", "description": "fix critical bug"}],
        }

        changelog = generator._format_changelog(grouped)

        assert "# Changelog" in changelog
        assert "✨ Features" in changelog
        assert "🐛 Bug Fixes" in changelog
        assert "add new feature" in changelog

    def test_generate_release_notes(self, generator):
        """Test release notes generation"""
        commits = [
            {
                "hash": "abc123",
                "message": "feat(api): add endpoint",
                "author": "dev",
                "date": "2024-01-01",
            },
            {
                "hash": "def456",
                "message": "fix: memory leak",
                "author": "dev",
                "date": "2024-01-01",
            },
        ]

        notes = generator.generate_release_notes("v1.2.0", commits)

        assert "Release v1.2.0" in notes
        assert "Summary" in notes
        assert "1 new features" in notes
        assert "1 bug fixes" in notes
