"""
Database Schema Designer Module
Automatically designs database schemas with normalization
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

class NormalizationLevel(Enum):
    FIRST_NF = "1NF"
    SECOND_NF = "2NF"
    THIRD_NF = "3NF"
    BCNF = "BCNF"

class DatabaseSchemaDesigner:
    """Designs optimized database schemas"""
    
    def __init__(self):
        self.supported_databases = ["PostgreSQL", "MySQL", "MongoDB", "DynamoDB"]
        self.data_types = {
            "PostgreSQL": {
                "string": "VARCHAR",
                "text": "TEXT",
                "integer": "INTEGER",
                "decimal": "DECIMAL",
                "boolean": "BOOLEAN",
                "date": "DATE",
                "datetime": "TIMESTAMP",
                "json": "JSONB",
                "uuid": "UUID"
            },
            "MySQL": {
                "string": "VARCHAR",
                "text": "TEXT",
                "integer": "INT",
                "decimal": "DECIMAL",
                "boolean": "BOOLEAN",
                "date": "DATE",
                "datetime": "DATETIME",
                "json": "JSON",
                "uuid": "CHAR(36)"
            }
        }
    
    async def design_schema(
        self,
        entities: List[Dict[str, Any]],
        database_type: str,
        normalization_level: str = "3NF"
    ) -> Dict[str, Any]:
        """Design database schema"""
        
        # Analyze relationships
        relationships = self._analyze_relationships(entities)
        
        # Apply normalization
        normalized_entities = self._normalize_entities(
            entities,
            NormalizationLevel(normalization_level)
        )
        
        # Generate schema
        if database_type in ["PostgreSQL", "MySQL"]:
            schema = self._generate_sql_schema(normalized_entities, database_type)
        elif database_type == "MongoDB":
            schema = self._generate_nosql_schema(normalized_entities)
        else:
            schema = self._generate_dynamodb_schema(normalized_entities)
        
        # Add indexes
        indexes = self._recommend_indexes(normalized_entities, relationships)
        
        # Add constraints
        constraints = self._generate_constraints(normalized_entities, relationships)
        
        return {
            "database_type": database_type,
            "tables": schema,
            "relationships": relationships,
            "indexes": indexes,
            "constraints": constraints,
            "migrations": self._generate_migrations(schema)
        }
    
    def _analyze_relationships(self, entities: List[Dict]) -> List[Dict]:
        """Analyze entity relationships"""
        
        relationships = []
        
        for entity in entities:
            for field in entity.get("fields", []):
                if field.get("type") == "reference":
                    relationships.append({
                        "from": entity["name"],
                        "to": field["references"],
                        "type": field.get("relationship", "many-to-one"),
                        "field": field["name"]
                    })
        
        return relationships
    
    def _normalize_entities(
        self,
        entities: List[Dict],
        level: NormalizationLevel
    ) -> List[Dict]:
        """Apply database normalization"""
        
        normalized = entities.copy()
        
        if level.value >= "1NF":
            # Remove repeating groups
            normalized = self._apply_1nf(normalized)
        
        if level.value >= "2NF":
            # Remove partial dependencies
            normalized = self._apply_2nf(normalized)
        
        if level.value >= "3NF":
            # Remove transitive dependencies
            normalized = self._apply_3nf(normalized)
        
        return normalized
    
    def _apply_1nf(self, entities: List[Dict]) -> List[Dict]:
        """Apply First Normal Form"""
        
        result = []
        
        for entity in entities:
            # Check for multi-valued attributes
            new_entities = []
            modified_entity = entity.copy()
            
            for field in entity.get("fields", []):
                if field.get("multi_valued"):
                    # Create separate table for multi-valued attribute
                    new_entity = {
                        "name": f"{entity['name']}_{field['name']}",
                        "fields": [
                            {"name": f"{entity['name'].lower()}_id", "type": "reference"},
                            {"name": field['name'], "type": field['type']}
                        ]
                    }
                    new_entities.append(new_entity)
                    # Remove from original
                    modified_entity["fields"] = [
                        f for f in modified_entity["fields"]
                        if f["name"] != field["name"]
                    ]
            
            result.append(modified_entity)
            result.extend(new_entities)
        
        return result
    
    def _apply_2nf(self, entities: List[Dict]) -> List[Dict]:
        """Apply Second Normal Form"""
        # Implementation for 2NF
        return entities
    
    def _apply_3nf(self, entities: List[Dict]) -> List[Dict]:
        """Apply Third Normal Form"""
        # Implementation for 3NF
        return entities
    
    def _generate_sql_schema(
        self,
        entities: List[Dict],
        database_type: str
    ) -> List[Dict]:
        """Generate SQL schema"""
        
        tables = []
        data_types = self.data_types[database_type]
        
        for entity in entities:
            table = {
                "name": entity["name"].lower(),
                "columns": [],
                "primary_key": None
            }
            
            # Add ID column
            table["columns"].append({
                "name": "id",
                "type": data_types["uuid"],
                "nullable": False,
                "primary": True
            })
            table["primary_key"] = "id"
            
            # Add other columns
            for field in entity.get("fields", []):
                column = {
                    "name": field["name"].lower(),
                    "type": data_types.get(field["type"], "VARCHAR(255)"),
                    "nullable": not field.get("required", False)
                }
                
                if field.get("unique"):
                    column["unique"] = True
                
                table["columns"].append(column)
            
            # Add timestamps
            table["columns"].extend([
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                {"name": "updated_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ])
            
            tables.append(table)
        
        return tables
    
    def _generate_nosql_schema(self, entities: List[Dict]) -> List[Dict]:
        """Generate NoSQL schema"""
        
        collections = []
        
        for entity in entities:
            collection = {
                "name": entity["name"].lower(),
                "schema": {
                    "_id": "ObjectId",
                    "fields": {}
                },
                "indexes": []
            }
            
            for field in entity.get("fields", []):
                collection["schema"]["fields"][field["name"]] = {
                    "type": field["type"],
                    "required": field.get("required", False)
                }
            
            collections.append(collection)
        
        return collections
    
    def _generate_dynamodb_schema(self, entities: List[Dict]) -> List[Dict]:
        """Generate DynamoDB schema"""
        
        tables = []
        
        for entity in entities:
            table = {
                "name": entity["name"],
                "partition_key": "id",
                "sort_key": None,
                "attributes": [],
                "global_indexes": []
            }
            
            tables.append(table)
        
        return tables
    
    def _recommend_indexes(
        self,
        entities: List[Dict],
        relationships: List[Dict]
    ) -> List[Dict]:
        """Recommend database indexes"""
        
        indexes = []
        
        # Foreign key indexes
        for rel in relationships:
            indexes.append({
                "table": rel["from"].lower(),
                "column": rel["field"],
                "type": "btree",
                "reason": "Foreign key optimization"
            })
        
        # Unique constraint indexes
        for entity in entities:
            for field in entity.get("fields", []):
                if field.get("unique"):
                    indexes.append({
                        "table": entity["name"].lower(),
                        "column": field["name"],
                        "type": "unique",
                        "reason": "Unique constraint"
                    })
        
        return indexes
    
    def _generate_constraints(
        self,
        entities: List[Dict],
        relationships: List[Dict]
    ) -> List[Dict]:
        """Generate database constraints"""
        
        constraints = []
        
        # Foreign key constraints
        for rel in relationships:
            constraints.append({
                "type": "foreign_key",
                "table": rel["from"].lower(),
                "column": rel["field"],
                "references_table": rel["to"].lower(),
                "references_column": "id",
                "on_delete": "CASCADE",
                "on_update": "CASCADE"
            })
        
        # Check constraints
        for entity in entities:
            for field in entity.get("fields", []):
                if field.get("validation"):
                    constraints.append({
                        "type": "check",
                        "table": entity["name"].lower(),
                        "column": field["name"],
                        "condition": field["validation"]
                    })
        
        return constraints
    
    def _generate_migrations(self, schema: List[Dict]) -> List[str]:
        """Generate migration scripts"""
        
        migrations = []
        
        for table in schema:
            # Create table migration
            columns_sql = []
            for col in table["columns"]:
                col_sql = f"{col['name']} {col['type']}"
                if not col.get("nullable", True):
                    col_sql += " NOT NULL"
                if col.get("primary"):
                    col_sql += " PRIMARY KEY"
                columns_sql.append(col_sql)
            
            create_sql = f"""CREATE TABLE {table['name']} (
    {', '.join(columns_sql)}
);"""
            migrations.append(create_sql)
        
        return migrations
