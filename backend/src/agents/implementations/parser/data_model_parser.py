from typing import Dict, List, Any
import re

class DataModelParser:
    """데이터 모델 파서"""

    def __init__(self):
        self.entity_patterns = self._load_entity_patterns()
        self.field_patterns = self._load_field_patterns()
        self.relationship_patterns = self._load_relationship_patterns()

    def _load_entity_patterns(self) -> List[str]:
        """엔티티 패턴 로드"""
        return [
            r'(user|customer|client|person)\s+(?:entity|model|table)',
            r'(product|item|article)\s+(?:entity|model|table)',
            r'(order|purchase|transaction)\s+(?:entity|model|table)',
            r'(?:entity|model|table)\s+(?:called|named)\s+(\w+)',
            r'(\w+)\s+(?:has|contains|includes)\s+(?:fields?|attributes?|properties?)'
        ]

    def _load_field_patterns(self) -> List[str]:
        """필드 패턴 로드"""
        return [
            r'(?:field|attribute|property|column)\s+(\w+)\s+(?:of type|as)\s+(\w+)',
            r'(\w+)\s+(?:field|attribute|property)\s+\((\w+)\)',
            r'(\w+):\s*(\w+)',
            r'(\w+)\s+(\w+)\s+(?:field|attribute|property)'
        ]

    def _load_relationship_patterns(self) -> List[str]:
        """관계 패턴 로드"""
        return [
            r'(\w+)\s+(?:has many|contains many)\s+(\w+)',
            r'(\w+)\s+(?:belongs to|is owned by)\s+(\w+)',
            r'(\w+)\s+(?:has one|contains one)\s+(\w+)',
            r'(\w+)\s+(?:references|links to)\s+(\w+)'
        ]

    async def parse(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """데이터 모델 파싱"""
        data_models = []
        text = str(base_structure)

        # 엔티티 추출
        entities = self._extract_entities(text)
        
        for entity in entities:
            model = {
                'name': entity['name'],
                'type': 'entity',
                'fields': self._extract_fields_for_entity(text, entity['name']),
                'relationships': self._extract_relationships_for_entity(text, entity['name']),
                'constraints': self._extract_constraints_for_entity(text, entity['name']),
                'indexes': self._suggest_indexes(entity['name']),
                'metadata': {
                    'table_name': self._generate_table_name(entity['name']),
                    'primary_key': 'id',
                    'timestamps': True
                }
            }
            data_models.append(model)

        # 기본 모델이 없으면 추론
        if not data_models:
            data_models = self._infer_basic_models(base_structure)

        return data_models

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """엔티티 추출"""
        entities = []
        
        for pattern in self.entity_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_name = self._extract_entity_name(match)
                if entity_name and entity_name not in [e['name'] for e in entities]:
                    entities.append({
                        'name': entity_name,
                        'description': match.group().strip()
                    })

        return entities

    def _extract_entity_name(self, match) -> str:
        """매치에서 엔티티 이름 추출"""
        groups = match.groups()
        for group in groups:
            if group and group.isalpha():
                return group.lower().capitalize()
        return ""

    def _extract_fields_for_entity(self, text: str, entity_name: str) -> List[Dict[str, Any]]:
        """엔티티별 필드 추출"""
        fields = []
        
        # 기본 필드 추가
        fields.extend([
            {'name': 'id', 'type': 'integer', 'primary_key': True, 'auto_increment': True},
            {'name': 'created_at', 'type': 'timestamp', 'nullable': False},
            {'name': 'updated_at', 'type': 'timestamp', 'nullable': False}
        ])

        # 패턴 기반 필드 추출
        for pattern in self.field_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                field = self._parse_field_match(match)
                if field and field not in fields:
                    fields.append(field)

        # 엔티티별 기본 필드 추가
        entity_specific_fields = self._get_entity_specific_fields(entity_name)
        fields.extend(entity_specific_fields)

        return fields

    def _parse_field_match(self, match) -> Dict[str, Any]:
        """필드 매치 파싱"""
        groups = match.groups()
        if len(groups) >= 2:
            field_name = groups[0].lower()
            field_type = self._normalize_field_type(groups[1])
            
            return {
                'name': field_name,
                'type': field_type,
                'nullable': True,
                'description': match.group().strip()
            }
        return {}

    def _normalize_field_type(self, type_str: str) -> str:
        """필드 타입 정규화"""
        type_mapping = {
            'string': 'varchar',
            'text': 'text',
            'number': 'integer',
            'int': 'integer',
            'float': 'decimal',
            'bool': 'boolean',
            'date': 'date',
            'datetime': 'timestamp',
            'email': 'varchar',
            'url': 'varchar',
            'phone': 'varchar'
        }
        
        return type_mapping.get(type_str.lower(), 'varchar')

    def _get_entity_specific_fields(self, entity_name: str) -> List[Dict[str, Any]]:
        """엔티티별 특화 필드"""
        entity_fields = {
            'user': [
                {'name': 'email', 'type': 'varchar', 'unique': True, 'nullable': False},
                {'name': 'password_hash', 'type': 'varchar', 'nullable': False},
                {'name': 'first_name', 'type': 'varchar', 'nullable': True},
                {'name': 'last_name', 'type': 'varchar', 'nullable': True},
                {'name': 'is_active', 'type': 'boolean', 'default': True}
            ],
            'product': [
                {'name': 'name', 'type': 'varchar', 'nullable': False},
                {'name': 'description', 'type': 'text', 'nullable': True},
                {'name': 'price', 'type': 'decimal', 'precision': 10, 'scale': 2},
                {'name': 'sku', 'type': 'varchar', 'unique': True},
                {'name': 'stock_quantity', 'type': 'integer', 'default': 0}
            ],
            'order': [
                {'name': 'order_number', 'type': 'varchar', 'unique': True},
                {'name': 'total_amount', 'type': 'decimal', 'precision': 10, 'scale': 2},
                {'name': 'status', 'type': 'varchar', 'default': 'pending'},
                {'name': 'order_date', 'type': 'timestamp', 'nullable': False}
            ]
        }
        
        return entity_fields.get(entity_name.lower(), [])

    def _extract_relationships_for_entity(self, text: str, entity_name: str) -> List[Dict[str, Any]]:
        """엔티티별 관계 추출"""
        relationships = []
        
        for pattern in self.relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                relationship = self._parse_relationship_match(match, entity_name)
                if relationship:
                    relationships.append(relationship)

        return relationships

    def _parse_relationship_match(self, match, entity_name: str) -> Dict[str, Any]:
        """관계 매치 파싱"""
        groups = match.groups()
        if len(groups) >= 2:
            source = groups[0].lower()
            target = groups[1].lower()
            
            # 관계 타입 결정
            match_text = match.group().lower()
            if 'has many' in match_text or 'contains many' in match_text:
                relationship_type = 'one_to_many'
            elif 'belongs to' in match_text or 'is owned by' in match_text:
                relationship_type = 'many_to_one'
            elif 'has one' in match_text or 'contains one' in match_text:
                relationship_type = 'one_to_one'
            else:
                relationship_type = 'many_to_many'

            return {
                'type': relationship_type,
                'source': source,
                'target': target,
                'foreign_key': f"{target}_id",
                'description': match.group().strip()
            }
        
        return {}

    def _extract_constraints_for_entity(self, text: str, entity_name: str) -> List[Dict[str, Any]]:
        """엔티티별 제약조건 추출"""
        constraints = []
        
        # 기본 제약조건
        constraints.append({
            'type': 'primary_key',
            'columns': ['id'],
            'name': f"pk_{entity_name.lower()}"
        })
        
        # 유니크 제약조건 패턴 찾기
        unique_patterns = [
            r'(\w+)\s+(?:must be|should be)\s+unique',
            r'unique\s+(\w+)',
            r'(\w+)\s+(?:field|column)\s+unique'
        ]
        
        for pattern in unique_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                field_name = match.group(1).lower()
                constraints.append({
                    'type': 'unique',
                    'columns': [field_name],
                    'name': f"uk_{entity_name.lower()}_{field_name}"
                })

        return constraints

    def _suggest_indexes(self, entity_name: str) -> List[Dict[str, Any]]:
        """인덱스 제안"""
        indexes = []
        
        # 기본 인덱스
        common_index_fields = {
            'user': ['email', 'created_at'],
            'product': ['sku', 'name', 'created_at'],
            'order': ['order_number', 'status', 'order_date']
        }
        
        fields = common_index_fields.get(entity_name.lower(), ['created_at'])
        
        for field in fields:
            indexes.append({
                'name': f"idx_{entity_name.lower()}_{field}",
                'columns': [field],
                'type': 'btree'
            })

        return indexes

    def _generate_table_name(self, entity_name: str) -> str:
        """테이블 이름 생성"""
        # 복수형으로 변환
        if entity_name.endswith('y'):
            return entity_name[:-1] + 'ies'
        elif entity_name.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return entity_name + 'es'
        else:
            return entity_name + 's'

    def _infer_basic_models(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기본 모델 추론"""
        project_type = base_structure.get('project_info', {}).get('type', 'web')
        
        if 'ecommerce' in str(base_structure).lower():
            return self._create_ecommerce_models()
        elif 'blog' in str(base_structure).lower():
            return self._create_blog_models()
        else:
            return self._create_generic_models()

    def _create_ecommerce_models(self) -> List[Dict[str, Any]]:
        """이커머스 모델 생성"""
        return [
            {
                'name': 'User',
                'type': 'entity',
                'fields': self._get_entity_specific_fields('user'),
                'relationships': [],
                'constraints': [],
                'indexes': self._suggest_indexes('user'),
                'metadata': {'table_name': 'users', 'primary_key': 'id'}
            },
            {
                'name': 'Product',
                'type': 'entity',
                'fields': self._get_entity_specific_fields('product'),
                'relationships': [],
                'constraints': [],
                'indexes': self._suggest_indexes('product'),
                'metadata': {'table_name': 'products', 'primary_key': 'id'}
            }
        ]

    def _create_blog_models(self) -> List[Dict[str, Any]]:
        """블로그 모델 생성"""
        return [
            {
                'name': 'User',
                'type': 'entity',
                'fields': self._get_entity_specific_fields('user'),
                'relationships': [],
                'constraints': [],
                'indexes': self._suggest_indexes('user'),
                'metadata': {'table_name': 'users', 'primary_key': 'id'}
            }
        ]

    def _create_generic_models(self) -> List[Dict[str, Any]]:
        """일반 모델 생성"""
        return [
            {
                'name': 'User',
                'type': 'entity',
                'fields': self._get_entity_specific_fields('user'),
                'relationships': [],
                'constraints': [],
                'indexes': self._suggest_indexes('user'),
                'metadata': {'table_name': 'users', 'primary_key': 'id'}
            }
        ]