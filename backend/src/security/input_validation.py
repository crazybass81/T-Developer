"""
Input Validation & Sanitization
SQL Injection 및 XSS 방어
"""

import hashlib
import html
import json
import re
from typing import Any, Dict, List, Optional, Union

import bleach
import sqlalchemy
from pydantic import BaseModel, Field, validator
from sqlalchemy.sql import text


class InputSanitizer:
    """입력 데이터 정제"""

    # Dangerous SQL keywords
    SQL_KEYWORDS = [
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "EXEC",
        "EXECUTE",
        "UNION",
        "FROM",
        "WHERE",
        "JOIN",
        "SCRIPT",
        "JAVASCRIPT",
        "ONLOAD",
        "ONERROR",
    ]

    # Dangerous characters for SQL
    SQL_CHARS = ["'", '"', ";", "--", "/*", "*/", "\\", "\x00", "\n", "\r", "\x1a"]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<embed",
        r"<object",
        r"eval\(",
        r"expression\(",
        r"vbscript:",
        r"onmouseover",
        r"onclick",
        r"onerror",
    ]

    # File upload restrictions
    ALLOWED_EXTENSIONS = {
        "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
        "document": ["pdf", "doc", "docx", "txt", "md"],
        "code": ["py", "js", "ts", "jsx", "tsx", "css", "html", "json", "yaml", "yml"],
        "archive": ["zip", "tar", "gz", "rar"],
    }

    BLOCKED_EXTENSIONS = ["exe", "dll", "so", "bat", "sh", "cmd", "com", "scr"]

    @classmethod
    def sanitize_sql_input(cls, value: str) -> str:
        """SQL Injection 방지를 위한 입력 정제"""
        if not value:
            return value

        # Remove SQL keywords (case-insensitive)
        sanitized = value
        for keyword in cls.SQL_KEYWORDS:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            sanitized = pattern.sub("", sanitized)

        # Escape dangerous characters
        for char in cls.SQL_CHARS:
            sanitized = sanitized.replace(char, "")

        # Remove multiple spaces
        sanitized = re.sub(r"\s+", " ", sanitized)

        return sanitized.strip()

    @classmethod
    def sanitize_html_input(cls, value: str, allowed_tags: List[str] = None) -> str:
        """XSS 방지를 위한 HTML 정제"""
        if not value:
            return value

        # Default allowed tags
        if allowed_tags is None:
            allowed_tags = [
                "p",
                "br",
                "span",
                "div",
                "strong",
                "em",
                "u",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "ul",
                "ol",
                "li",
                "a",
                "img",
                "blockquote",
                "code",
                "pre",
            ]

        # Allowed attributes
        allowed_attributes = {
            "a": ["href", "title", "target"],
            "img": ["src", "alt", "width", "height"],
            "div": ["class", "id"],
            "span": ["class", "id"],
            "p": ["class", "id"],
        }

        # Clean with bleach
        cleaned = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)

        # Additional XSS pattern removal
        for pattern in cls.XSS_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        return cleaned

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """파일명 정제"""
        if not filename:
            return "unnamed"

        # Remove path traversal attempts
        filename = filename.replace("..", "")
        filename = filename.replace("/", "")
        filename = filename.replace("\\", "")

        # Remove special characters
        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        # Limit length
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        if len(name) > 100:
            name = name[:100]

        # Check extension
        if ext.lower() in cls.BLOCKED_EXTENSIONS:
            ext = "txt"  # Force safe extension

        return f"{name}.{ext}" if ext else name

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """이메일 형식 검증"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """URL 형식 검증"""
        pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*$"
        return bool(re.match(pattern, url))

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """전화번호 형식 검증"""
        # Remove non-digits
        digits = re.sub(r"\D", "", phone)
        # Check if valid length (10-15 digits)
        return 10 <= len(digits) <= 15

    @classmethod
    def escape_json(cls, data: Any) -> str:
        """JSON 데이터 이스케이프"""
        if isinstance(data, str):
            # Escape special characters
            data = data.replace("\\", "\\\\")
            data = data.replace('"', '\\"')
            data = data.replace("\n", "\\n")
            data = data.replace("\r", "\\r")
            data = data.replace("\t", "\\t")

        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def hash_sensitive_data(cls, data: str, salt: str = "") -> str:
        """민감한 데이터 해싱"""
        return hashlib.sha256(f"{data}{salt}".encode()).hexdigest()


class SQLQueryBuilder:
    """안전한 SQL 쿼리 빌더"""

    @staticmethod
    def build_safe_query(
        table: str,
        columns: List[str] = None,
        where: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
    ) -> tuple:
        """파라미터화된 쿼리 생성"""

        # Validate table name (alphanumeric and underscore only)
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
            raise ValueError(f"Invalid table name: {table}")

        # Build SELECT clause
        if columns:
            # Validate column names
            for col in columns:
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", col):
                    raise ValueError(f"Invalid column name: {col}")
            columns_str = ", ".join(columns)
        else:
            columns_str = "*"

        query = f"SELECT {columns_str} FROM {table}"
        params = {}

        # Build WHERE clause
        if where:
            conditions = []
            for key, value in where.items():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    raise ValueError(f"Invalid column name: {key}")
                conditions.append(f"{key} = :{key}")
                params[key] = value

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        # Build ORDER BY clause
        if order_by:
            # Validate order by (column name and optional DESC/ASC)
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(\s+(ASC|DESC))?$", order_by, re.IGNORECASE):
                raise ValueError(f"Invalid ORDER BY clause: {order_by}")
            query += f" ORDER BY {order_by}"

        # Build LIMIT clause
        if limit:
            if not isinstance(limit, int) or limit < 1:
                raise ValueError(f"Invalid LIMIT value: {limit}")
            query += f" LIMIT :limit"
            params["limit"] = limit

        return query, params


class RequestValidator(BaseModel):
    """요청 데이터 검증 기본 클래스"""

    class Config:
        # Automatically validate on assignment
        validate_assignment = True
        # Use Enum values
        use_enum_values = True
        # Custom JSON encoder
        json_encoders = {datetime: lambda v: v.isoformat()}

    @validator("*", pre=True)
    def sanitize_string_fields(cls, v):
        """모든 문자열 필드 자동 정제"""
        if isinstance(v, str):
            # Remove leading/trailing whitespace
            v = v.strip()
            # Remove null bytes
            v = v.replace("\x00", "")
            # Limit length
            if len(v) > 10000:
                v = v[:10000]
        return v


class FileUploadValidator:
    """파일 업로드 검증"""

    @staticmethod
    def validate_file(
        filename: str,
        content: bytes,
        max_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_types: List[str] = None,
    ) -> Dict[str, Any]:
        """파일 검증"""

        # Sanitize filename
        safe_filename = InputSanitizer.sanitize_filename(filename)

        # Check file size
        if len(content) > max_size:
            raise ValueError(f"File too large: {len(content)} bytes (max: {max_size})")

        # Check file extension
        ext = safe_filename.split(".")[-1].lower() if "." in safe_filename else ""

        if allowed_types:
            if ext not in allowed_types:
                raise ValueError(f"File type not allowed: {ext}")
        elif ext in InputSanitizer.BLOCKED_EXTENSIONS:
            raise ValueError(f"File type blocked: {ext}")

        # Check file content (magic numbers)
        file_signatures = {
            b"\xFF\xD8\xFF": "jpg",
            b"\x89\x50\x4E\x47": "png",
            b"\x47\x49\x46\x38": "gif",
            b"\x50\x4B\x03\x04": "zip",
            b"\x25\x50\x44\x46": "pdf",
        }

        file_type = None
        for signature, ftype in file_signatures.items():
            if content.startswith(signature):
                file_type = ftype
                break

        # Verify extension matches content
        if file_type and ext != file_type:
            raise ValueError(f"File extension ({ext}) doesn't match content ({file_type})")

        return {
            "filename": safe_filename,
            "size": len(content),
            "extension": ext,
            "content_type": file_type or "unknown",
        }


from datetime import datetime
