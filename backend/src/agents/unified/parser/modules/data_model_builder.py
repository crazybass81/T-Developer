"""
Data Model Builder Module
Builds comprehensive data models from requirements and entities
"""

import re
from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class DataType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    UUID = "uuid"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    JSON = "json"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"
    FILE = "file"
    IMAGE = "image"
    BINARY = "binary"


class RelationType(Enum):
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_ONE = "N:1"
    MANY_TO_MANY = "N:N"


class DataModelBuilder:
    """Builds data models from analyzed requirements"""

    def __init__(self):
        # Field patterns for automatic detection
        self.field_patterns = {
            "id": {"type": DataType.UUID, "required": True, "unique": True},
            "uuid": {"type": DataType.UUID, "required": True, "unique": True},
            "email": {"type": DataType.EMAIL, "required": True, "unique": True},
            "password": {"type": DataType.STRING, "required": True, "encrypted": True},
            "username": {"type": DataType.STRING, "required": True, "unique": True},
            "name": {"type": DataType.STRING, "required": True},
            "title": {"type": DataType.STRING, "required": True},
            "description": {"type": DataType.STRING, "required": False},
            "status": {"type": DataType.ENUM, "required": True},
            "created_at": {"type": DataType.DATETIME, "required": True, "auto": True},
            "updated_at": {"type": DataType.DATETIME, "required": True, "auto": True},
            "deleted_at": {"type": DataType.DATETIME, "required": False},
            "price": {"type": DataType.FLOAT, "required": True, "min": 0},
            "quantity": {"type": DataType.INTEGER, "required": True, "min": 0},
            "date": {"type": DataType.DATE, "required": True},
            "time": {"type": DataType.TIME, "required": True},
            "url": {"type": DataType.URL, "required": False},
            "phone": {"type": DataType.PHONE, "required": False},
            "address": {"type": DataType.STRING, "required": False},
            "is_active": {"type": DataType.BOOLEAN, "required": True, "default": True},
            "is_deleted": {
                "type": DataType.BOOLEAN,
                "required": True,
                "default": False,
            },
        }

        # Common model templates
        self.model_templates = {
            "user": {
                "fields": [
                    "id",
                    "email",
                    "password",
                    "username",
                    "name",
                    "created_at",
                    "updated_at",
                ],
                "indexes": ["email", "username"],
                "soft_delete": True,
            },
            "product": {
                "fields": [
                    "id",
                    "name",
                    "description",
                    "price",
                    "quantity",
                    "created_at",
                    "updated_at",
                ],
                "indexes": ["name"],
                "soft_delete": False,
            },
            "order": {
                "fields": [
                    "id",
                    "user_id",
                    "status",
                    "total",
                    "created_at",
                    "updated_at",
                ],
                "indexes": ["user_id", "status"],
                "soft_delete": False,
            },
            "category": {
                "fields": [
                    "id",
                    "name",
                    "description",
                    "parent_id",
                    "created_at",
                    "updated_at",
                ],
                "indexes": ["name", "parent_id"],
                "soft_delete": True,
            },
        }

        # Validation rules
        self.validation_rules = {
            "string": ["minLength", "maxLength", "pattern", "enum"],
            "integer": ["min", "max", "multipleOf"],
            "float": ["min", "max", "precision"],
            "date": ["min", "max", "format"],
            "email": ["format", "domain"],
            "url": ["format", "protocol"],
            "array": ["minItems", "maxItems", "uniqueItems"],
        }

    async def build(
        self, entities: Dict[str, Any], requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build data models from entities and requirements

        Args:
            entities: Extracted entities
            requirements: Analyzed requirements

        Returns:
            Complete data model specification
        """
        # Extract models from entities
        models = self._extract_models(entities)

        # Enhance models with requirements
        models = self._enhance_with_requirements(models, requirements)

        # Add fields to models
        models = self._add_fields_to_models(models, entities)

        # Identify relationships
        relationships = self._identify_relationships(models, entities)

        # Add relationship fields
        models = self._add_relationship_fields(models, relationships)

        # Add validations
        models = self._add_validations(models, requirements)

        # Add indexes
        models = self._add_indexes(models)

        # Generate schemas
        schemas = self._generate_schemas(models)

        # Generate migrations
        migrations = self._generate_migrations(models)

        # Generate API specifications
        api_specs = self._generate_api_specs(models)

        # Validate models
        validation = self._validate_models(models)

        # Generate documentation
        documentation = self._generate_documentation(models)

        return {
            "models": models,
            "relationships": relationships,
            "schemas": schemas,
            "migrations": migrations,
            "api_specs": api_specs,
            "validation": validation,
            "documentation": documentation,
            "statistics": self._calculate_statistics(models),
        }

    def _extract_models(self, entities: Dict[str, Any]) -> Dict[str, Dict]:
        """Extract data models from entities"""
        models = {}

        # Process entity categories
        for category, entity_list in entities.get("entities", {}).items():
            if category in ["objects", "business"]:
                for entity in entity_list:
                    model_name = self._normalize_model_name(entity["text"])

                    # Check for template
                    if model_name.lower() in self.model_templates:
                        models[model_name] = self._create_from_template(model_name.lower())
                    else:
                        models[model_name] = self._create_basic_model(model_name)

        return models

    def _normalize_model_name(self, text: str) -> str:
        """Normalize entity text to model name"""
        # Convert to PascalCase
        words = re.findall(r"\w+", text)
        return "".join(word.capitalize() for word in words)

    def _create_from_template(self, template_name: str) -> Dict:
        """Create model from template"""
        template = self.model_templates[template_name]

        model = {
            "name": template_name.capitalize(),
            "table": f"{template_name}s",
            "fields": {},
            "indexes": template.get("indexes", []),
            "relations": [],
            "validations": {},
            "soft_delete": template.get("soft_delete", False),
            "timestamps": True,
        }

        # Add fields from template
        for field_name in template["fields"]:
            if field_name in self.field_patterns:
                model["fields"][field_name] = self.field_patterns[field_name].copy()

        return model

    def _create_basic_model(self, name: str) -> Dict:
        """Create basic model structure"""
        return {
            "name": name,
            "table": f"{name.lower()}s",
            "fields": {
                "id": {"type": DataType.UUID, "required": True, "unique": True},
                "created_at": {
                    "type": DataType.DATETIME,
                    "required": True,
                    "auto": True,
                },
                "updated_at": {
                    "type": DataType.DATETIME,
                    "required": True,
                    "auto": True,
                },
            },
            "indexes": ["id"],
            "relations": [],
            "validations": {},
            "soft_delete": False,
            "timestamps": True,
        }

    def _enhance_with_requirements(
        self, models: Dict[str, Dict], requirements: List[Dict]
    ) -> Dict[str, Dict]:
        """Enhance models based on requirements"""
        for req in requirements:
            # Extract model information from requirement
            entities = req.get("entities", [])

            for entity in entities:
                model_name = self._normalize_model_name(entity)

                if model_name not in models:
                    models[model_name] = self._create_basic_model(model_name)

                # Add fields based on requirement text
                fields = self._extract_fields_from_requirement(req)
                for field in fields:
                    if field not in models[model_name]["fields"]:
                        models[model_name]["fields"][field] = self._infer_field_type(field)

        return models

    def _extract_fields_from_requirement(self, requirement: Dict) -> List[str]:
        """Extract field names from requirement text"""
        fields = []
        text = requirement.get("text", "").lower()

        # Look for common field indicators
        field_patterns = [
            r"(?:with|has|contains?)\s+([a-z_]+(?:\s+and\s+[a-z_]+)*)",
            r"(?:field|attribute|property):\s*([a-z_]+)",
            r"([a-z_]+)\s+(?:field|attribute|property)",
        ]

        for pattern in field_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                field_text = match.group(1)
                # Split on 'and' if present
                if " and " in field_text:
                    fields.extend(field_text.split(" and "))
                else:
                    fields.append(field_text.strip())

        return [self._normalize_field_name(f) for f in fields]

    def _normalize_field_name(self, text: str) -> str:
        """Normalize text to field name"""
        # Convert to snake_case
        words = re.findall(r"\w+", text.lower())
        return "_".join(words)

    def _infer_field_type(self, field_name: str) -> Dict:
        """Infer field type from name"""
        field_lower = field_name.lower()

        # Check known patterns
        if field_lower in self.field_patterns:
            return self.field_patterns[field_lower].copy()

        # Infer from name patterns
        if field_lower.endswith("_id"):
            return {"type": DataType.UUID, "required": True, "foreign_key": True}
        elif field_lower.endswith("_at"):
            return {"type": DataType.DATETIME, "required": True}
        elif field_lower.startswith("is_") or field_lower.startswith("has_"):
            return {"type": DataType.BOOLEAN, "required": True, "default": False}
        elif "email" in field_lower:
            return {"type": DataType.EMAIL, "required": True}
        elif "url" in field_lower or "link" in field_lower:
            return {"type": DataType.URL, "required": False}
        elif "phone" in field_lower or "mobile" in field_lower:
            return {"type": DataType.PHONE, "required": False}
        elif "price" in field_lower or "cost" in field_lower or "amount" in field_lower:
            return {"type": DataType.FLOAT, "required": True, "min": 0}
        elif "count" in field_lower or "quantity" in field_lower:
            return {"type": DataType.INTEGER, "required": True, "min": 0}
        elif "date" in field_lower:
            return {"type": DataType.DATE, "required": True}
        elif "time" in field_lower:
            return {"type": DataType.TIME, "required": True}
        else:
            return {"type": DataType.STRING, "required": False}

    def _add_fields_to_models(
        self, models: Dict[str, Dict], entities: Dict[str, Any]
    ) -> Dict[str, Dict]:
        """Add fields to models based on entity attributes"""
        attributes = entities.get("attributes", {})

        for entity_name, attr_list in attributes.items():
            model_name = self._normalize_model_name(entity_name)

            if model_name in models:
                for attr in attr_list:
                    field_name = self._normalize_field_name(attr["name"])

                    if field_name not in models[model_name]["fields"]:
                        models[model_name]["fields"][field_name] = self._infer_field_type(
                            field_name
                        )

        return models

    def _identify_relationships(
        self, models: Dict[str, Dict], entities: Dict[str, Any]
    ) -> List[Dict]:
        """Identify relationships between models"""
        relationships = []
        entity_relationships = entities.get("relationships", [])

        for rel in entity_relationships:
            source = self._normalize_model_name(rel["source"])
            target = self._normalize_model_name(rel["target"])

            if source in models and target in models:
                relationship = {
                    "source": source,
                    "target": target,
                    "type": self._determine_relationship_type(rel["type"]),
                    "name": rel.get("type", "related"),
                    "foreign_key": f"{target.lower()}_id",
                    "inverse": self._get_inverse_name(source, target, rel["type"]),
                }
                relationships.append(relationship)

        # Infer relationships from foreign keys
        for model_name, model in models.items():
            for field_name, field_spec in model["fields"].items():
                if field_spec.get("foreign_key"):
                    # Extract target model from field name
                    target_model = self._extract_model_from_fk(field_name)
                    if target_model in models:
                        relationships.append(
                            {
                                "source": model_name,
                                "target": target_model,
                                "type": RelationType.MANY_TO_ONE,
                                "name": "belongs_to",
                                "foreign_key": field_name,
                            }
                        )

        return relationships

    def _determine_relationship_type(self, rel_type: str) -> RelationType:
        """Determine relationship cardinality"""
        if rel_type in ["has_one", "owns"]:
            return RelationType.ONE_TO_ONE
        elif rel_type in ["has_many", "has", "contains"]:
            return RelationType.ONE_TO_MANY
        elif rel_type in ["belongs_to", "is_part_of"]:
            return RelationType.MANY_TO_ONE
        elif rel_type in ["many_to_many", "associated"]:
            return RelationType.MANY_TO_MANY
        else:
            return RelationType.ONE_TO_MANY

    def _get_inverse_name(self, source: str, target: str, rel_type: str) -> str:
        """Get inverse relationship name"""
        if rel_type == "has_many":
            return source.lower()
        elif rel_type == "belongs_to":
            return f"{target.lower()}s"
        else:
            return f"{source.lower()}_rel"

    def _extract_model_from_fk(self, field_name: str) -> str:
        """Extract model name from foreign key field"""
        if field_name.endswith("_id"):
            model_name = field_name[:-3]  # Remove _id
            return model_name.capitalize()
        return ""

    def _add_relationship_fields(
        self, models: Dict[str, Dict], relationships: List[Dict]
    ) -> Dict[str, Dict]:
        """Add relationship fields to models"""
        for rel in relationships:
            source = rel["source"]
            target = rel["target"]

            if source in models:
                # Add foreign key field
                if rel["type"] in [RelationType.MANY_TO_ONE, RelationType.ONE_TO_ONE]:
                    fk_field = rel["foreign_key"]
                    if fk_field not in models[source]["fields"]:
                        models[source]["fields"][fk_field] = {
                            "type": DataType.UUID,
                            "required": True,
                            "foreign_key": True,
                            "references": target,
                        }

                # Add relation to model
                models[source]["relations"].append(
                    {"name": rel["name"], "target": target, "type": rel["type"].value}
                )

            # Add many-to-many junction table
            if rel["type"] == RelationType.MANY_TO_MANY:
                junction_name = f"{source}_{target}"
                if junction_name not in models:
                    models[junction_name] = {
                        "name": junction_name,
                        "table": f"{source.lower()}_{target.lower()}",
                        "fields": {
                            "id": {
                                "type": DataType.UUID,
                                "required": True,
                                "unique": True,
                            },
                            f"{source.lower()}_id": {
                                "type": DataType.UUID,
                                "required": True,
                                "foreign_key": True,
                                "references": source,
                            },
                            f"{target.lower()}_id": {
                                "type": DataType.UUID,
                                "required": True,
                                "foreign_key": True,
                                "references": target,
                            },
                            "created_at": {
                                "type": DataType.DATETIME,
                                "required": True,
                                "auto": True,
                            },
                        },
                        "indexes": [f"{source.lower()}_id", f"{target.lower()}_id"],
                        "relations": [],
                        "validations": {},
                        "soft_delete": False,
                        "timestamps": False,
                    }

        return models

    def _add_validations(
        self, models: Dict[str, Dict], requirements: List[Dict]
    ) -> Dict[str, Dict]:
        """Add validations based on requirements"""
        for req in requirements:
            constraints = req.get("constraints", [])

            for constraint in constraints:
                # Apply constraint to relevant models
                for entity in req.get("entities", []):
                    model_name = self._normalize_model_name(entity)

                    if model_name in models:
                        # Add validation rule
                        if "validations" not in models[model_name]:
                            models[model_name]["validations"] = {}

                        # Parse constraint and add validation
                        validation = self._parse_constraint_to_validation(constraint)
                        if validation:
                            field = validation.get("field", "general")
                            if field not in models[model_name]["validations"]:
                                models[model_name]["validations"][field] = []
                            models[model_name]["validations"][field].append(validation)

        return models

    def _parse_constraint_to_validation(self, constraint: Dict) -> Optional[Dict]:
        """Parse constraint into validation rule"""
        if constraint["type"] == "numeric":
            return {
                "type": "range",
                "value": constraint["value"],
                "unit": constraint.get("unit"),
            }
        elif constraint["type"] == "range":
            return {
                "type": "between",
                "min": constraint["min"],
                "max": constraint["max"],
            }

        return None

    def _add_indexes(self, models: Dict[str, Dict]) -> Dict[str, Dict]:
        """Add database indexes to models"""
        for model_name, model in models.items():
            indexes = model.get("indexes", [])

            # Add indexes for foreign keys
            for field_name, field_spec in model["fields"].items():
                if field_spec.get("foreign_key") and field_name not in indexes:
                    indexes.append(field_name)

                # Add indexes for unique fields
                if field_spec.get("unique") and field_name not in indexes:
                    indexes.append(field_name)

            # Add composite indexes for common queries
            if "user_id" in model["fields"] and "created_at" in model["fields"]:
                indexes.append(["user_id", "created_at"])

            model["indexes"] = indexes

        return models

    def _generate_schemas(self, models: Dict[str, Dict]) -> Dict[str, Dict]:
        """Generate database schemas"""
        schemas = {}

        for model_name, model in models.items():
            schema = {
                "table": model["table"],
                "columns": [],
                "indexes": [],
                "foreign_keys": [],
            }

            # Generate columns
            for field_name, field_spec in model["fields"].items():
                column = {
                    "name": field_name,
                    "type": self._map_to_sql_type(field_spec["type"]),
                    "nullable": not field_spec.get("required", False),
                    "unique": field_spec.get("unique", False),
                    "default": field_spec.get("default"),
                    "auto_increment": field_spec.get("auto", False),
                }
                schema["columns"].append(column)

                # Add foreign key constraint
                if field_spec.get("foreign_key"):
                    schema["foreign_keys"].append(
                        {
                            "column": field_name,
                            "references": field_spec.get("references", ""),
                            "on_delete": "CASCADE",
                            "on_update": "CASCADE",
                        }
                    )

            # Add indexes
            for index in model.get("indexes", []):
                if isinstance(index, list):
                    schema["indexes"].append(
                        {
                            "name": f"idx_{model['table']}_{'_'.join(index)}",
                            "columns": index,
                            "unique": False,
                        }
                    )
                else:
                    schema["indexes"].append(
                        {
                            "name": f"idx_{model['table']}_{index}",
                            "columns": [index],
                            "unique": False,
                        }
                    )

            schemas[model_name] = schema

        return schemas

    def _map_to_sql_type(self, data_type: DataType) -> str:
        """Map DataType to SQL type"""
        mapping = {
            DataType.STRING: "VARCHAR(255)",
            DataType.INTEGER: "INTEGER",
            DataType.FLOAT: "DECIMAL(10,2)",
            DataType.BOOLEAN: "BOOLEAN",
            DataType.DATE: "DATE",
            DataType.DATETIME: "TIMESTAMP",
            DataType.TIME: "TIME",
            DataType.UUID: "UUID",
            DataType.EMAIL: "VARCHAR(255)",
            DataType.URL: "TEXT",
            DataType.PHONE: "VARCHAR(20)",
            DataType.JSON: "JSON",
            DataType.ARRAY: "JSON",
            DataType.OBJECT: "JSON",
            DataType.ENUM: "VARCHAR(50)",
            DataType.FILE: "VARCHAR(500)",
            DataType.IMAGE: "VARCHAR(500)",
            DataType.BINARY: "BLOB",
        }

        if isinstance(data_type, DataType):
            return mapping.get(data_type, "VARCHAR(255)")
        else:
            return mapping.get(DataType[data_type.upper()], "VARCHAR(255)")

    def _generate_migrations(self, models: Dict[str, Dict]) -> List[Dict]:
        """Generate database migrations"""
        migrations = []

        for model_name, model in models.items():
            migration = {
                "name": f"create_{model['table']}_table",
                "up": self._generate_create_table_sql(model),
                "down": f"DROP TABLE IF EXISTS {model['table']};",
            }
            migrations.append(migration)

        return migrations

    def _generate_create_table_sql(self, model: Dict) -> str:
        """Generate CREATE TABLE SQL"""
        sql = f"CREATE TABLE {model['table']} (\n"

        columns = []
        for field_name, field_spec in model["fields"].items():
            col_def = f"  {field_name} {self._map_to_sql_type(field_spec['type'])}"

            if field_spec.get("required"):
                col_def += " NOT NULL"

            if field_spec.get("unique"):
                col_def += " UNIQUE"

            if field_spec.get("default") is not None:
                col_def += f" DEFAULT {field_spec['default']}"

            columns.append(col_def)

        sql += ",\n".join(columns)

        # Add primary key
        sql += ",\n  PRIMARY KEY (id)"

        sql += "\n);"

        return sql

    def _generate_api_specs(self, models: Dict[str, Dict]) -> Dict[str, List]:
        """Generate API specifications for models"""
        api_specs = {}

        for model_name, model in models.items():
            endpoints = []
            base_path = f"/{model['table']}"

            # CRUD endpoints
            endpoints.extend(
                [
                    {
                        "method": "GET",
                        "path": base_path,
                        "description": f"List all {model['name']}",
                        "parameters": ["page", "limit", "sort", "filter"],
                    },
                    {
                        "method": "GET",
                        "path": f"{base_path}/{{id}}",
                        "description": f"Get {model['name']} by ID",
                        "parameters": ["id"],
                    },
                    {
                        "method": "POST",
                        "path": base_path,
                        "description": f"Create new {model['name']}",
                        "body": self._generate_request_body(model),
                    },
                    {
                        "method": "PUT",
                        "path": f"{base_path}/{{id}}",
                        "description": f"Update {model['name']}",
                        "parameters": ["id"],
                        "body": self._generate_request_body(model),
                    },
                    {
                        "method": "DELETE",
                        "path": f"{base_path}/{{id}}",
                        "description": f"Delete {model['name']}",
                        "parameters": ["id"],
                    },
                ]
            )

            api_specs[model_name] = endpoints

        return api_specs

    def _generate_request_body(self, model: Dict) -> Dict:
        """Generate request body schema"""
        properties = {}
        required = []

        for field_name, field_spec in model["fields"].items():
            # Skip auto fields
            if field_spec.get("auto"):
                continue

            properties[field_name] = {
                "type": field_spec["type"].value
                if isinstance(field_spec["type"], DataType)
                else field_spec["type"]
            }

            if field_spec.get("required"):
                required.append(field_name)

        return {"type": "object", "properties": properties, "required": required}

    def _validate_models(self, models: Dict[str, Dict]) -> Dict[str, Any]:
        """Validate data models"""
        validation = {"valid": True, "errors": [], "warnings": []}

        for model_name, model in models.items():
            # Check for primary key
            has_primary = any(
                field.get("unique") and field.get("required") for field in model["fields"].values()
            )

            if not has_primary:
                validation["warnings"].append(f"Model '{model_name}' lacks primary key")

            # Check for timestamps
            if model.get("timestamps") and "created_at" not in model["fields"]:
                validation["warnings"].append(f"Model '{model_name}' missing timestamps")

            # Check foreign key references
            for field_name, field_spec in model["fields"].items():
                if field_spec.get("foreign_key"):
                    ref = field_spec.get("references")
                    if ref and ref not in models:
                        validation["errors"].append(
                            f"Model '{model_name}' references unknown model '{ref}'"
                        )

        validation["valid"] = len(validation["errors"]) == 0

        return validation

    def _generate_documentation(self, models: Dict[str, Dict]) -> Dict[str, str]:
        """Generate model documentation"""
        docs = {}

        for model_name, model in models.items():
            doc = f"# {model['name']} Model\n\n"
            doc += f"Table: `{model['table']}`\n\n"

            doc += "## Fields\n\n"
            doc += "| Field | Type | Required | Description |\n"
            doc += "|-------|------|----------|-------------|\n"

            for field_name, field_spec in model["fields"].items():
                field_type = (
                    field_spec["type"].value
                    if isinstance(field_spec["type"], DataType)
                    else field_spec["type"]
                )
                required = "Yes" if field_spec.get("required") else "No"
                doc += f"| {field_name} | {field_type} | {required} | |\n"

            if model.get("relations"):
                doc += "\n## Relationships\n\n"
                for rel in model["relations"]:
                    doc += f"- {rel['name']}: {rel['target']} ({rel['type']})\n"

            docs[model_name] = doc

        return docs

    def _calculate_statistics(self, models: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate model statistics"""
        total_fields = sum(len(model["fields"]) for model in models.values())
        total_relations = sum(len(model.get("relations", [])) for model in models.values())

        return {
            "total_models": len(models),
            "total_fields": total_fields,
            "average_fields_per_model": total_fields / len(models) if models else 0,
            "total_relationships": total_relations,
            "models_with_soft_delete": sum(1 for m in models.values() if m.get("soft_delete")),
            "models_with_timestamps": sum(1 for m in models.values() if m.get("timestamps")),
        }
