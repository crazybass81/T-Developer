"""
Entity Extractor Module
Extracts and classifies entities from parsed text
"""

import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple


class EntityExtractor:
    """Extracts entities and their relationships from text"""

    def __init__(self):
        # Entity patterns
        self.entity_patterns = {
            "user_types": {
                "patterns": [
                    r"\b(user|users|customer|customers|client|clients|admin|administrator|manager|employee|staff|member|guest|visitor|subscriber|buyer|seller|vendor|supplier|partner|developer|designer|analyst|operator|moderator|editor|viewer|owner|tenant)\b",
                ],
                "category": "actor",
            },
            "data_entities": {
                "patterns": [
                    r"\b(product|products|item|items|order|orders|invoice|invoices|payment|payments|transaction|transactions|account|accounts|profile|profiles|document|documents|file|files|report|reports|record|records|entry|entries|post|posts|article|articles|comment|comments|review|reviews|rating|ratings|category|categories|tag|tags|label|labels)\b",
                ],
                "category": "object",
            },
            "ui_components": {
                "patterns": [
                    r"\b(page|pages|screen|screens|view|views|form|forms|button|buttons|link|links|menu|menus|modal|modals|dialog|dialogs|popup|popups|dropdown|dropdowns|table|tables|list|lists|grid|grids|card|cards|panel|panels|tab|tabs|accordion|accordions|sidebar|sidebars|navbar|navbars|header|headers|footer|footers|widget|widgets|component|components)\b",
                ],
                "category": "interface",
            },
            "system_components": {
                "patterns": [
                    r"\b(api|apis|endpoint|endpoints|service|services|database|databases|server|servers|cache|caches|queue|queues|storage|repository|repositories|module|modules|package|packages|library|libraries|framework|frameworks|platform|platforms|system|systems|application|applications|software|tool|tools|plugin|plugins|extension|extensions)\b",
                ],
                "category": "system",
            },
            "business_entities": {
                "patterns": [
                    r"\b(company|companies|organization|organizations|department|departments|team|teams|project|projects|task|tasks|workflow|workflows|process|processes|policy|policies|rule|rules|requirement|requirements|feature|features|function|functions|capability|capabilities|permission|permissions|role|roles|privilege|privileges)\b",
                ],
                "category": "business",
            },
            "attributes": {
                "patterns": [
                    r"\b(name|title|description|status|state|type|category|price|cost|amount|quantity|date|time|email|phone|address|url|id|code|number|value|size|color|weight|height|width|length|duration|priority|level|score|rating|version|language|currency|location|position)\b",
                ],
                "category": "property",
            },
        }

        # Relationship indicators
        self.relationship_indicators = {
            "has": ["has", "have", "contains", "includes", "comprises", "consists of"],
            "belongs_to": [
                "belongs to",
                "is part of",
                "is in",
                "is member of",
                "is owned by",
            ],
            "uses": ["uses", "utilizes", "employs", "leverages", "depends on"],
            "creates": ["creates", "generates", "produces", "makes", "builds"],
            "manages": ["manages", "controls", "handles", "administers", "oversees"],
            "interacts": [
                "interacts with",
                "communicates with",
                "connects to",
                "interfaces with",
            ],
            "inherits": ["inherits from", "extends", "derives from", "is based on"],
            "implements": ["implements", "realizes", "fulfills", "provides"],
        }

        # Entity modifiers
        self.modifiers = {
            "quantity": [
                "single",
                "multiple",
                "many",
                "few",
                "several",
                "all",
                "some",
                "any",
            ],
            "importance": [
                "primary",
                "secondary",
                "main",
                "auxiliary",
                "critical",
                "optional",
            ],
            "state": ["active", "inactive", "enabled", "disabled", "visible", "hidden"],
            "access": ["public", "private", "protected", "internal", "external"],
            "lifecycle": [
                "new",
                "existing",
                "updated",
                "deleted",
                "archived",
                "draft",
                "published",
            ],
        }

        # Domain-specific entities
        self.domain_entities = {
            "ecommerce": [
                "cart",
                "checkout",
                "shipping",
                "inventory",
                "discount",
                "coupon",
                "wishlist",
            ],
            "social": [
                "feed",
                "timeline",
                "friend",
                "follower",
                "like",
                "share",
                "message",
                "notification",
            ],
            "healthcare": [
                "patient",
                "doctor",
                "appointment",
                "prescription",
                "diagnosis",
                "treatment",
            ],
            "education": [
                "course",
                "lesson",
                "student",
                "teacher",
                "grade",
                "assignment",
                "exam",
            ],
            "finance": [
                "account",
                "balance",
                "transfer",
                "deposit",
                "withdrawal",
                "statement",
                "budget",
            ],
        }

    async def extract(self, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities from NLP processed text

        Args:
            nlp_result: NLP processing results

        Returns:
            Extracted entities with classifications
        """
        text = nlp_result.get("original", "")
        cleaned_text = nlp_result.get("cleaned", text)
        sentences = nlp_result.get("sentences", [])
        tokens = nlp_result.get("tokens", [])
        pos_tags = nlp_result.get("pos_tags", [])

        # Extract entities by pattern
        pattern_entities = self._extract_by_patterns(cleaned_text)

        # Extract entities by POS tags
        pos_entities = self._extract_by_pos(pos_tags)

        # Extract named entities
        named_entities = self._extract_named_entities(nlp_result.get("entities", {}))

        # Extract compound entities
        compound_entities = self._extract_compound_entities(tokens, pos_tags)

        # Merge and deduplicate entities
        all_entities = self._merge_entities(
            pattern_entities, pos_entities, named_entities, compound_entities
        )

        # Classify entities
        classified = self._classify_entities(all_entities, cleaned_text)

        # Extract relationships
        relationships = self._extract_relationships(classified, sentences)

        # Extract entity attributes
        attributes = self._extract_attributes(classified, sentences)

        # Build entity hierarchy
        hierarchy = self._build_hierarchy(classified, relationships)

        # Identify entity roles
        roles = self._identify_roles(classified, sentences)

        # Extract constraints
        constraints = self._extract_constraints(classified, sentences)

        # Detect domain
        domain = self._detect_domain(classified)

        # Generate entity model
        model = self._generate_entity_model(classified, relationships, attributes)

        return {
            "entities": classified,
            "relationships": relationships,
            "attributes": attributes,
            "hierarchy": hierarchy,
            "roles": roles,
            "constraints": constraints,
            "domain": domain,
            "model": model,
            "statistics": self._calculate_statistics(classified),
        }

    def _extract_by_patterns(self, text: str) -> Dict[str, List[Dict]]:
        """Extract entities using regex patterns"""
        entities = defaultdict(list)
        text_lower = text.lower()

        for category, config in self.entity_patterns.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    entity = {
                        "text": match.group(),
                        "category": config["category"],
                        "type": category,
                        "position": match.span(),
                        "confidence": 0.9,
                    }
                    entities[config["category"]].append(entity)

        return dict(entities)

    def _extract_by_pos(self, pos_tags: List[Tuple[str, str]]) -> Dict[str, List[Dict]]:
        """Extract entities based on POS tags"""
        entities = defaultdict(list)

        for i, (token, tag) in enumerate(pos_tags):
            entity = None

            if tag in ["NN", "NNS"]:  # Common nouns
                entity = {
                    "text": token,
                    "category": "object",
                    "type": "noun",
                    "confidence": 0.7,
                }
            elif tag in ["NNP", "NNPS"]:  # Proper nouns
                entity = {
                    "text": token,
                    "category": "named",
                    "type": "proper_noun",
                    "confidence": 0.8,
                }
            elif tag in ["VB", "VBZ", "VBP", "VBD", "VBN", "VBG"]:  # Verbs
                entity = {
                    "text": token,
                    "category": "action",
                    "type": "verb",
                    "confidence": 0.6,
                }

            if entity:
                entities[entity["category"]].append(entity)

        return dict(entities)

    def _extract_named_entities(self, nlp_entities: Dict) -> Dict[str, List[Dict]]:
        """Extract named entities from NLP results"""
        entities = defaultdict(list)

        for category, entity_list in nlp_entities.items():
            for entity_name in entity_list:
                if isinstance(entity_name, dict):
                    entities[category].append(entity_name)
                else:
                    entities[category].append(
                        {
                            "text": entity_name,
                            "category": category,
                            "type": "named",
                            "confidence": 0.85,
                        }
                    )

        return dict(entities)

    def _extract_compound_entities(
        self, tokens: List[str], pos_tags: List[Tuple[str, str]]
    ) -> Dict[str, List[Dict]]:
        """Extract compound entities (multi-word entities)"""
        entities = defaultdict(list)
        current_compound = []
        current_tags = []

        for i, (token, tag) in enumerate(pos_tags):
            # Build compound nouns
            if tag in ["NN", "NNS", "NNP", "NNPS", "JJ"]:
                current_compound.append(token)
                current_tags.append(tag)
            else:
                if len(current_compound) > 1:
                    compound_text = " ".join(current_compound)
                    entities["compound"].append(
                        {
                            "text": compound_text,
                            "category": "object",
                            "type": "compound",
                            "components": current_compound.copy(),
                            "tags": current_tags.copy(),
                            "confidence": 0.75,
                        }
                    )
                current_compound = []
                current_tags = []

        # Handle last compound
        if len(current_compound) > 1:
            compound_text = " ".join(current_compound)
            entities["compound"].append(
                {
                    "text": compound_text,
                    "category": "object",
                    "type": "compound",
                    "components": current_compound,
                    "tags": current_tags,
                    "confidence": 0.75,
                }
            )

        return dict(entities)

    def _merge_entities(self, *entity_dicts) -> List[Dict]:
        """Merge and deduplicate entities from multiple sources"""
        merged = []
        seen = set()

        for entity_dict in entity_dicts:
            for category, entities in entity_dict.items():
                for entity in entities:
                    # Create unique key
                    key = (entity["text"].lower(), entity.get("category"))

                    if key not in seen:
                        seen.add(key)
                        merged.append(entity)
                    else:
                        # Update confidence if higher
                        for existing in merged:
                            if (
                                existing["text"].lower(),
                                existing.get("category"),
                            ) == key:
                                existing["confidence"] = max(
                                    existing.get("confidence", 0),
                                    entity.get("confidence", 0),
                                )

        return merged

    def _classify_entities(self, entities: List[Dict], text: str) -> Dict[str, List[Dict]]:
        """Classify entities into semantic categories"""
        classified = defaultdict(list)

        for entity in entities:
            # Enhance classification with context
            context = self._get_context(entity["text"], text)

            # Determine final category
            category = self._determine_category(entity, context)
            entity["final_category"] = category
            entity["context"] = context

            classified[category].append(entity)

        return dict(classified)

    def _get_context(self, entity_text: str, full_text: str, window: int = 50) -> str:
        """Get context around an entity"""
        index = full_text.lower().find(entity_text.lower())
        if index == -1:
            return ""

        start = max(0, index - window)
        end = min(len(full_text), index + len(entity_text) + window)

        return full_text[start:end]

    def _determine_category(self, entity: Dict, context: str) -> str:
        """Determine the semantic category of an entity"""
        text = entity["text"].lower()

        # Check for specific patterns
        if any(pattern in text for pattern in ["user", "customer", "admin", "client"]):
            return "actors"
        elif any(pattern in text for pattern in ["page", "screen", "form", "button"]):
            return "ui_elements"
        elif any(pattern in text for pattern in ["api", "database", "service", "server"]):
            return "system_components"
        elif any(pattern in text for pattern in ["create", "update", "delete", "read"]):
            return "operations"
        elif any(pattern in text for pattern in ["name", "email", "date", "status"]):
            return "attributes"
        else:
            return entity.get("category", "objects")

    def _extract_relationships(
        self, entities: Dict[str, List[Dict]], sentences: List[str]
    ) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Find entities in sentence
            entities_in_sentence = []
            for category, entity_list in entities.items():
                for entity in entity_list:
                    if entity["text"].lower() in sentence_lower:
                        entities_in_sentence.append(entity)

            # Extract relationships between found entities
            for i, entity1 in enumerate(entities_in_sentence):
                for entity2 in entities_in_sentence[i + 1 :]:
                    rel_type = self._identify_relationship_type(
                        entity1["text"], entity2["text"], sentence
                    )

                    if rel_type:
                        relationships.append(
                            {
                                "source": entity1["text"],
                                "target": entity2["text"],
                                "type": rel_type,
                                "sentence": sentence,
                                "confidence": 0.8,
                            }
                        )

        return relationships

    def _identify_relationship_type(
        self, entity1: str, entity2: str, sentence: str
    ) -> Optional[str]:
        """Identify the type of relationship between two entities"""
        sentence_lower = sentence.lower()

        for rel_type, indicators in self.relationship_indicators.items():
            for indicator in indicators:
                pattern = f"{entity1.lower()}.*{indicator}.*{entity2.lower()}"
                if re.search(pattern, sentence_lower):
                    return rel_type

        # Check for implicit relationships
        if "and" in sentence_lower:
            return "associated"
        elif "or" in sentence_lower:
            return "alternative"

        return None

    def _extract_attributes(
        self, entities: Dict[str, List[Dict]], sentences: List[str]
    ) -> Dict[str, List[Dict]]:
        """Extract attributes for entities"""
        attributes = defaultdict(list)

        for sentence in sentences:
            for category, entity_list in entities.items():
                for entity in entity_list:
                    if entity["text"] in sentence.lower():
                        # Look for attributes near the entity
                        attrs = self._find_attributes_in_sentence(entity["text"], sentence)

                        if attrs:
                            attributes[entity["text"]].extend(attrs)

        return dict(attributes)

    def _find_attributes_in_sentence(self, entity: str, sentence: str) -> List[Dict]:
        """Find attributes related to an entity in a sentence"""
        attributes = []

        # Common attribute patterns
        patterns = [
            rf"{entity}\s+(?:has|have|with)\s+(\w+)",
            rf"(\w+)\s+(?:of|for)\s+{entity}",
            rf"{entity}'s\s+(\w+)",
            rf"{entity}\s+(\w+)\s+(?:is|are|was|were)",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                attr_text = match.group(1)
                attributes.append(
                    {
                        "name": attr_text,
                        "entity": entity,
                        "type": self._classify_attribute(attr_text),
                        "sentence": sentence,
                    }
                )

        return attributes

    def _classify_attribute(self, attr_text: str) -> str:
        """Classify an attribute"""
        attr_lower = attr_text.lower()

        if attr_lower in ["name", "title", "label"]:
            return "identifier"
        elif attr_lower in ["date", "time", "datetime", "timestamp"]:
            return "temporal"
        elif attr_lower in ["price", "cost", "amount", "total"]:
            return "numeric"
        elif attr_lower in ["status", "state", "type", "category"]:
            return "categorical"
        elif attr_lower in ["description", "note", "comment"]:
            return "textual"
        else:
            return "general"

    def _build_hierarchy(
        self, entities: Dict[str, List[Dict]], relationships: List[Dict]
    ) -> Dict[str, Any]:
        """Build entity hierarchy"""
        hierarchy = {"root": "system", "levels": {}, "tree": {}}

        # Determine hierarchy levels
        level_0 = []  # System level
        level_1 = []  # Actor level
        level_2 = []  # Object level
        level_3 = []  # Attribute level

        for category, entity_list in entities.items():
            for entity in entity_list:
                if category == "system_components":
                    level_0.append(entity["text"])
                elif category == "actors":
                    level_1.append(entity["text"])
                elif category in ["objects", "ui_elements"]:
                    level_2.append(entity["text"])
                elif category == "attributes":
                    level_3.append(entity["text"])

        hierarchy["levels"] = {0: level_0, 1: level_1, 2: level_2, 3: level_3}

        # Build tree structure
        hierarchy["tree"] = self._build_tree_structure(entities, relationships)

        return hierarchy

    def _build_tree_structure(
        self, entities: Dict[str, List[Dict]], relationships: List[Dict]
    ) -> Dict:
        """Build tree structure from relationships"""
        tree = {}

        # Create nodes
        for category, entity_list in entities.items():
            for entity in entity_list:
                tree[entity["text"]] = {
                    "category": category,
                    "children": [],
                    "parents": [],
                }

        # Add relationships
        for rel in relationships:
            if rel["type"] in ["has", "contains", "comprises"]:
                if rel["source"] in tree and rel["target"] in tree:
                    tree[rel["source"]]["children"].append(rel["target"])
                    tree[rel["target"]]["parents"].append(rel["source"])

        return tree

    def _identify_roles(
        self, entities: Dict[str, List[Dict]], sentences: List[str]
    ) -> Dict[str, List[str]]:
        """Identify roles of entities"""
        roles = defaultdict(list)

        for category, entity_list in entities.items():
            for entity in entity_list:
                entity_roles = []

                # Check in sentences
                for sentence in sentences:
                    if entity["text"] in sentence.lower():
                        # Identify role based on context
                        if "create" in sentence or "add" in sentence:
                            entity_roles.append("creator")
                        if "manage" in sentence or "control" in sentence:
                            entity_roles.append("manager")
                        if "view" in sentence or "read" in sentence:
                            entity_roles.append("viewer")
                        if "approve" in sentence or "authorize" in sentence:
                            entity_roles.append("approver")

                if entity_roles:
                    roles[entity["text"]] = list(set(entity_roles))

        return dict(roles)

    def _extract_constraints(
        self, entities: Dict[str, List[Dict]], sentences: List[str]
    ) -> List[Dict]:
        """Extract constraints on entities"""
        constraints = []

        constraint_patterns = [
            r"(\w+)\s+must\s+(?:be|have)\s+(.+)",
            r"(\w+)\s+should\s+(?:be|have)\s+(.+)",
            r"(\w+)\s+(?:cannot|can\'t|must not)\s+(.+)",
            r"maximum\s+(\d+)\s+(\w+)",
            r"minimum\s+(\d+)\s+(\w+)",
            r"(\w+)\s+limit(?:ed)?\s+to\s+(\d+)",
        ]

        for sentence in sentences:
            for pattern in constraint_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    constraints.append(
                        {
                            "entity": match.group(1),
                            "constraint": match.group(2) if match.lastindex > 1 else match.group(0),
                            "type": self._classify_constraint(sentence),
                            "sentence": sentence,
                        }
                    )

        return constraints

    def _classify_constraint(self, text: str) -> str:
        """Classify constraint type"""
        text_lower = text.lower()

        if "must" in text_lower or "required" in text_lower:
            return "mandatory"
        elif "should" in text_lower or "recommended" in text_lower:
            return "recommended"
        elif "cannot" in text_lower or "must not" in text_lower:
            return "prohibited"
        elif "maximum" in text_lower or "minimum" in text_lower:
            return "boundary"
        else:
            return "general"

    def _detect_domain(self, entities: Dict[str, List[Dict]]) -> str:
        """Detect the domain based on entities"""
        domain_scores = defaultdict(int)

        # Count domain-specific entities
        for domain, keywords in self.domain_entities.items():
            for category, entity_list in entities.items():
                for entity in entity_list:
                    if entity["text"].lower() in keywords:
                        domain_scores[domain] += 1

        # Return domain with highest score
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)

        return "general"

    def _generate_entity_model(
        self,
        entities: Dict[str, List[Dict]],
        relationships: List[Dict],
        attributes: Dict[str, List[Dict]],
    ) -> Dict[str, Any]:
        """Generate entity relationship model"""
        model = {"entities": {}, "relationships": [], "cardinalities": {}}

        # Build entity definitions
        for category, entity_list in entities.items():
            for entity in entity_list:
                entity_name = entity["text"]

                model["entities"][entity_name] = {
                    "type": category,
                    "attributes": [attr["name"] for attr in attributes.get(entity_name, [])],
                    "relationships": [],
                }

        # Add relationships
        for rel in relationships:
            model["relationships"].append(
                {"from": rel["source"], "to": rel["target"], "type": rel["type"]}
            )

            # Update entity relationships
            if rel["source"] in model["entities"]:
                model["entities"][rel["source"]]["relationships"].append(
                    {"target": rel["target"], "type": rel["type"]}
                )

        # Infer cardinalities
        model["cardinalities"] = self._infer_cardinalities(relationships)

        return model

    def _infer_cardinalities(self, relationships: List[Dict]) -> Dict[str, str]:
        """Infer relationship cardinalities"""
        cardinalities = {}

        for rel in relationships:
            key = f"{rel['source']}-{rel['target']}"

            # Simple heuristics
            if rel["type"] == "has":
                cardinalities[key] = "1:N"
            elif rel["type"] == "belongs_to":
                cardinalities[key] = "N:1"
            elif rel["type"] == "associated":
                cardinalities[key] = "N:N"
            else:
                cardinalities[key] = "1:1"

        return cardinalities

    def _calculate_statistics(self, entities: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate entity extraction statistics"""
        total_entities = sum(len(entity_list) for entity_list in entities.values())

        category_counts = {category: len(entity_list) for category, entity_list in entities.items()}

        unique_entities = set()
        for entity_list in entities.values():
            for entity in entity_list:
                unique_entities.add(entity["text"].lower())

        return {
            "total_entities": total_entities,
            "unique_entities": len(unique_entities),
            "category_counts": category_counts,
            "categories": list(entities.keys()),
            "average_confidence": self._calculate_average_confidence(entities),
        }

    def _calculate_average_confidence(self, entities: Dict[str, List[Dict]]) -> float:
        """Calculate average confidence score"""
        confidences = []

        for entity_list in entities.values():
            for entity in entity_list:
                if "confidence" in entity:
                    confidences.append(entity["confidence"])

        return sum(confidences) / len(confidences) if confidences else 0.0
