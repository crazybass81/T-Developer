"""
OpenAPI Documentation Configuration
API 문서화 및 Swagger UI 설정
"""

from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

# API Metadata
API_TITLE = "T-Developer API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
# T-Developer Enterprise API

## 🚀 Overview

T-Developer is an enterprise-grade AI-powered development platform that generates complete software projects from natural language descriptions.

## 🔑 Authentication

This API uses **JWT Bearer tokens** for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

For server-to-server communication, you can also use **API Keys**:

```
X-API-Key: <your-api-key>
```

## 📊 Rate Limiting

Rate limits vary by subscription tier:

| Tier | Requests/Hour | Concurrent Projects |
|------|--------------|-------------------|
| Free | 100 | 1 |
| Basic | 1,000 | 5 |
| Premium | 10,000 | 20 |
| Enterprise | 100,000 | Unlimited |

## 🔗 Base URLs

- **Production**: `https://api.t-developer.com`
- **Staging**: `https://staging-api.t-developer.com`
- **Development**: `http://localhost:8000`

## 📝 Response Format

All responses follow this format:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {...}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🌐 WebSocket Support

Real-time updates are available via WebSocket at:

```
wss://api.t-developer.com/ws
```

## 📚 SDK Libraries

Official SDKs available for:
- Python: `pip install tdeveloper`
- JavaScript/TypeScript: `npm install @tdeveloper/sdk`
- Go: `go get github.com/tdeveloper/sdk-go`
- Java: Maven/Gradle support

## 🆘 Support

- Documentation: https://docs.t-developer.com
- Status Page: https://status.t-developer.com
- Support Email: support@t-developer.com
"""

# Tags for grouping endpoints
TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization endpoints",
    },
    {"name": "Projects", "description": "Project generation and management"},
    {"name": "Agents", "description": "AI agent operations and status"},
    {"name": "Users", "description": "User profile and settings management"},
    {"name": "Organizations", "description": "Organization and team management"},
    {"name": "API Keys", "description": "API key management for programmatic access"},
    {"name": "Billing", "description": "Subscription and billing management"},
    {"name": "Admin", "description": "Administrative endpoints (requires admin role)"},
    {"name": "Health", "description": "System health and status checks"},
    {"name": "WebSocket", "description": "WebSocket connection and real-time events"},
]

# Security schemes
SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT Bearer token authentication",
    },
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API Key authentication for server-to-server communication",
    },
}

# Response examples
RESPONSE_EXAMPLES = {
    "200": {
        "description": "Successful response",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "status": "completed",
                    },
                    "message": "Operation successful",
                }
            }
        },
    },
    "400": {
        "description": "Bad request",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": "Invalid request parameters",
                        "details": {"field": "email", "issue": "Invalid email format"},
                    },
                }
            }
        },
    },
    "401": {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Authentication required",
                    },
                }
            }
        },
    },
    "403": {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Insufficient permissions",
                    },
                }
            }
        },
    },
    "404": {
        "description": "Not found",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {"code": "NOT_FOUND", "message": "Resource not found"},
                }
            }
        },
    },
    "429": {
        "description": "Too many requests",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Rate limit exceeded. Please try again later.",
                    },
                }
            }
        },
    },
    "500": {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                    },
                }
            }
        },
    },
}


def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema"""

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        routes=app.routes,
        tags=TAGS_METADATA,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = SECURITY_SCHEMES

    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]

    # Add servers
    openapi_schema["servers"] = [
        {"url": "https://api.t-developer.com", "description": "Production server"},
        {"url": "https://staging-api.t-developer.com", "description": "Staging server"},
        {"url": "http://localhost:8000", "description": "Development server"},
    ]

    # Add external documentation
    openapi_schema["externalDocs"] = {
        "description": "Full API Documentation",
        "url": "https://docs.t-developer.com/api",
    }

    # Add license
    openapi_schema["info"]["license"] = {
        "name": "Enterprise License",
        "url": "https://t-developer.com/license",
    }

    # Add contact
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "url": "https://support.t-developer.com",
        "email": "api@t-developer.com",
    }

    # Add terms of service
    openapi_schema["info"]["termsOfService"] = "https://t-developer.com/terms"

    # Add x-logo for ReDoc
    openapi_schema["info"]["x-logo"] = {
        "url": "https://t-developer.com/logo.png",
        "altText": "T-Developer Logo",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_documentation(app: FastAPI):
    """Setup API documentation endpoints"""

    # Custom OpenAPI schema
    app.openapi = lambda: custom_openapi(app)

    # Custom Swagger UI
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{API_TITLE} - Swagger UI",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
            swagger_favicon_url="https://t-developer.com/favicon.ico",
        )

    # Custom ReDoc
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{API_TITLE} - ReDoc",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
            redoc_favicon_url="https://t-developer.com/favicon.ico",
        )

    # API specification download
    @app.get("/api-spec", include_in_schema=False)
    async def download_api_spec():
        """Download OpenAPI specification as JSON"""
        return custom_openapi(app)

    # Postman collection export
    @app.get("/postman-collection", include_in_schema=False)
    async def export_postman_collection():
        """Export API as Postman collection"""
        # Convert OpenAPI to Postman format
        openapi = custom_openapi(app)

        # Simplified Postman collection structure
        postman_collection = {
            "info": {
                "name": API_TITLE,
                "description": API_DESCRIPTION,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {"key": "token", "value": "{{access_token}}", "type": "string"}
                ],
            },
            "item": [],
            "variable": [
                {
                    "key": "base_url",
                    "value": "https://api.t-developer.com",
                    "type": "string",
                },
                {"key": "access_token", "value": "", "type": "string"},
            ],
        }

        return postman_collection


# API Examples for documentation
API_EXAMPLES = {
    "project_create": {
        "summary": "Create a todo app",
        "value": {
            "query": "Create a modern todo application with React",
            "requirements": {
                "features": ["authentication", "real-time updates", "drag-and-drop"],
                "framework": "react",
                "styling": "tailwind",
            },
        },
    },
    "project_response": {
        "summary": "Successful project creation",
        "value": {
            "success": True,
            "data": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "processing",
                "estimated_time": 30,
                "download_url": "/api/v1/download/123e4567-e89b-12d3-a456-426614174000",
            },
        },
    },
}
