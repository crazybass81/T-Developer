# backend/src/agents/implementations/parser_data_model_parser.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class DataField:
    name: str
    type: str
    required: bool
    description: Optional[str] = None
    constraints: List[str] = None
    default_value: Optional[Any] = None

@dataclass
class DataModel:
    name: str
    description: str
    fields: List[DataField]
    relationships: List[Dict[str, Any]]
    indexes: List[str]
    constraints: List[str]

@dataclass
class DatabaseSchema:
    models: List[DataModel]
    relationships: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]

class DataModelParser:
    """데이터 모델 파서"""

    def __init__(self):
        self.entity_patterns = [
            r'(entity|model|table|collection)\s+["\']?(\w+)["\']?\s+(with|contains|has)\s+(fields?|attributes?|properties?):?\s*([^.]+)',
            r'(\w+)\s+(entity|model|table)\s*:\s*([^.]+)',
            r'(\w+)\s+has\s+(fields?|attributes?):\s*([^.]+)'
        ]
        
        self.field_patterns = [
            r'(\w+)\s*:\s*(\w+)(?:\s*\(([^)]+)\))?(?:\s*-\s*(.+?))?(?:,|$)',
            r'(\w+)\s+(\w+)(?:\s*\(([^)]+)\))?(?:\s*-\s*(.+?))?(?:,|$)',
            r'-\s*(\w+)\s*:\s*(\w+)(?:\s*\(([^)]+)\))?(?:\s*-\s*(.+?))?'
        ]
        
        self.relationship_patterns = [
            r'(\w+)\s+(has\s+many|belongs\s+to|has\s+one)\s+(\w+)',
            r'(\w+)\s+references?\s+(\w+)',
            r'(\w+)\.(\w+)\s+→\s+(\w+)\.(\w+)'
        ]

    async def parse_data_models(
        self,
        requirements: List[Dict[str, Any]]
    ) -> DatabaseSchema:
        """데이터 모델 파싱"""
        
        models = []
        global_relationships = []
        
        for req in requirements:
            description = req.get('description', '')
            
            # 엔티티 추출
            entities = self._extract_entities(description)
            
            for entity_info in entities:
                model = await self._create_data_model(entity_info, description)
                if model:
                    models.append(model)
                    
            # 관계 추출
            relationships = self._extract_relationships(description)
            global_relationships.extend(relationships)
            
        # 중복 제거
        unique_models = self._deduplicate_models(models)
        
        # 인덱스 생성
        indexes = self._generate_indexes(unique_models)
        
        return DatabaseSchema(
            models=unique_models,
            relationships=global_relationships,
            indexes=indexes
        )

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """엔티티 추출"""
        entities = []
        
        for pattern in self.entity_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 3:
                    entity_name = groups[1] if groups[0].lower() in ['entity', 'model', 'table'] else groups[0]
                    fields_text = groups[-1]
                    
                    entities.append({
                        'name': entity_name,
                        'fields_text': fields_text,
                        'context': match.group(0)
                    })
                    
        return entities

    async def _create_data_model(
        self,
        entity_info: Dict[str, Any],
        context: str
    ) -> Optional[DataModel]:
        """데이터 모델 생성"""
        
        name = entity_info['name'].capitalize()
        fields_text = entity_info['fields_text']
        
        # 필드 파싱
        fields = self._parse_fields(fields_text)
        
        # 기본 필드 추가 (id, timestamps)
        if not any(f.name.lower() == 'id' for f in fields):
            fields.insert(0, DataField(
                name='id',
                type='string',
                required=True,
                description='Unique identifier'
            ))
            
        # 타임스탬프 필드 추가
        timestamp_fields = ['created_at', 'updated_at']
        for ts_field in timestamp_fields:
            if not any(f.name.lower() == ts_field for f in fields):
                fields.append(DataField(
                    name=ts_field,
                    type='datetime',
                    required=True,
                    description=f'Record {ts_field.replace("_", " ")}'
                ))
        
        # 관계 추출
        relationships = self._extract_model_relationships(name, context)
        
        # 제약사항 추출
        constraints = self._extract_model_constraints(context)
        
        # 인덱스 추출
        indexes = self._extract_model_indexes(fields, relationships)
        
        return DataModel(
            name=name,
            description=f"{name} entity",
            fields=fields,
            relationships=relationships,
            indexes=indexes,
            constraints=constraints
        )

    def _parse_fields(self, fields_text: str) -> List[DataField]:
        """필드 파싱"""
        fields = []
        
        # 여러 패턴으로 시도
        for pattern in self.field_patterns:
            matches = re.finditer(pattern, fields_text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                field_name = groups[0]
                field_type = groups[1] if len(groups) > 1 else 'string'
                constraints_text = groups[2] if len(groups) > 2 and groups[2] else ''
                description = groups[3] if len(groups) > 3 and groups[3] else None
                
                # 타입 정규화
                normalized_type = self._normalize_field_type(field_type)
                
                # 제약사항 파싱
                constraints = self._parse_field_constraints(constraints_text)
                required = 'required' in constraints_text.lower() or 'not null' in constraints_text.lower()
                
                # 기본값 추출
                default_value = self._extract_default_value(constraints_text)
                
                field = DataField(
                    name=field_name,
                    type=normalized_type,
                    required=required,
                    description=description,
                    constraints=constraints,
                    default_value=default_value
                )
                fields.append(field)
                
        # 패턴 매칭이 실패한 경우 간단한 파싱
        if not fields:
            fields = self._simple_field_parsing(fields_text)
            
        return fields

    def _normalize_field_type(self, field_type: str) -> str:
        """필드 타입 정규화"""
        type_mapping = {
            'str': 'string',
            'text': 'string',
            'varchar': 'string',
            'char': 'string',
            'int': 'integer',
            'integer': 'integer',
            'number': 'integer',
            'float': 'decimal',
            'decimal': 'decimal',
            'bool': 'boolean',
            'boolean': 'boolean',
            'date': 'date',
            'datetime': 'datetime',
            'timestamp': 'datetime',
            'json': 'object',
            'array': 'array'
        }
        
        return type_mapping.get(field_type.lower(), field_type.lower())

    def _parse_field_constraints(self, constraints_text: str) -> List[str]:
        """필드 제약사항 파싱"""
        constraints = []
        
        constraint_patterns = {
            'unique': r'\bunique\b',
            'not_null': r'\bnot\s+null\b',
            'primary_key': r'\bprimary\s+key\b',
            'foreign_key': r'\bforeign\s+key\b',
            'min_length': r'\bmin\s*:\s*(\d+)\b',
            'max_length': r'\bmax\s*:\s*(\d+)\b',
            'range': r'\brange\s*:\s*(\d+)\s*-\s*(\d+)\b'
        }
        
        for constraint_name, pattern in constraint_patterns.items():
            if re.search(pattern, constraints_text, re.IGNORECASE):
                constraints.append(constraint_name)
                
        return constraints

    def _extract_default_value(self, constraints_text: str) -> Optional[Any]:
        """기본값 추출"""
        default_pattern = r'default\s*:\s*([^,\s]+)'
        match = re.search(default_pattern, constraints_text, re.IGNORECASE)
        
        if match:
            value = match.group(1).strip('\'"')
            
            # 타입 추론
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            elif value.isdigit():
                return int(value)
            elif re.match(r'^\d+\.\d+$', value):
                return float(value)
            else:
                return value
                
        return None

    def _simple_field_parsing(self, fields_text: str) -> List[DataField]:
        """간단한 필드 파싱 (폴백)"""
        fields = []
        
        # 쉼표로 분리된 필드명 추출
        field_names = [name.strip() for name in fields_text.split(',')]
        
        for field_name in field_names:
            if field_name and len(field_name) > 0:
                # 기본 타입 추론
                inferred_type = self._infer_field_type(field_name)
                
                fields.append(DataField(
                    name=field_name,
                    type=inferred_type,
                    required=False,
                    description=f"{field_name} field"
                ))
                
        return fields

    def _infer_field_type(self, field_name: str) -> str:
        """필드명으로부터 타입 추론"""
        name_lower = field_name.lower()
        
        if 'id' in name_lower:
            return 'string'
        elif 'name' in name_lower or 'title' in name_lower:
            return 'string'
        elif 'email' in name_lower:
            return 'string'
        elif 'phone' in name_lower:
            return 'string'
        elif 'age' in name_lower or 'count' in name_lower:
            return 'integer'
        elif 'price' in name_lower or 'amount' in name_lower:
            return 'decimal'
        elif 'date' in name_lower or 'time' in name_lower:
            return 'datetime'
        elif 'is_' in name_lower or 'has_' in name_lower:
            return 'boolean'
        else:
            return 'string'

    def _extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """관계 추출"""
        relationships = []
        
        for pattern in self.relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 3:
                    source = groups[0]
                    relation_type = groups[1] if 'has' in groups[1] or 'belongs' in groups[1] else 'references'
                    target = groups[2] if len(groups) == 3 else groups[4]
                    
                    relationships.append({
                        'source': source,
                        'target': target,
                        'type': relation_type,
                        'description': match.group(0)
                    })
                    
        return relationships

    def _extract_model_relationships(
        self,
        model_name: str,
        context: str
    ) -> List[Dict[str, Any]]:
        """모델별 관계 추출"""
        relationships = []
        
        # 외래키 패턴
        fk_patterns = [
            rf'{model_name.lower()}_id',
            rf'{model_name.lower()}Id',
            rf'(\w+)_id.*{model_name.lower()}',
            rf'(\w+)Id.*{model_name.lower()}'
        ]
        
        for pattern in fk_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and match != model_name.lower():
                    relationships.append({
                        'type': 'belongs_to',
                        'target': match.capitalize(),
                        'foreign_key': f'{match}_id'
                    })
                    
        return relationships

    def _extract_model_constraints(self, context: str) -> List[str]:
        """모델 제약사항 추출"""
        constraints = []
        
        constraint_keywords = [
            'unique', 'not null', 'primary key', 'foreign key',
            'check', 'default', 'index'
        ]
        
        for keyword in constraint_keywords:
            if keyword in context.lower():
                constraints.append(keyword)
                
        return constraints

    def _extract_model_indexes(
        self,
        fields: List[DataField],
        relationships: List[Dict[str, Any]]
    ) -> List[str]:
        """모델 인덱스 추출"""
        indexes = []
        
        # 기본 인덱스 (id, foreign keys)
        for field in fields:
            if field.name.lower() == 'id':
                indexes.append(f'PRIMARY KEY ({field.name})')
            elif field.name.endswith('_id'):
                indexes.append(f'INDEX idx_{field.name} ({field.name})')
            elif 'unique' in (field.constraints or []):
                indexes.append(f'UNIQUE INDEX idx_{field.name} ({field.name})')
                
        # 관계 기반 인덱스
        for rel in relationships:
            if 'foreign_key' in rel:
                fk = rel['foreign_key']
                indexes.append(f'INDEX idx_{fk} ({fk})')
                
        return indexes

    def _deduplicate_models(self, models: List[DataModel]) -> List[DataModel]:
        """중복 모델 제거"""
        unique_models = {}
        
        for model in models:
            if model.name not in unique_models:
                unique_models[model.name] = model
            else:
                # 필드 병합
                existing = unique_models[model.name]
                existing_field_names = {f.name for f in existing.fields}
                
                for field in model.fields:
                    if field.name not in existing_field_names:
                        existing.fields.append(field)
                        
                # 관계 병합
                existing.relationships.extend(model.relationships)
                
        return list(unique_models.values())

    def _generate_indexes(self, models: List[DataModel]) -> List[Dict[str, Any]]:
        """인덱스 생성"""
        indexes = []
        
        for model in models:
            for index_def in model.indexes:
                indexes.append({
                    'table': model.name,
                    'definition': index_def,
                    'type': 'btree'
                })
                
        return indexes