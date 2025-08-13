"""
NLP Processor Module
Advanced natural language processing for requirement analysis
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from collections import Counter


class NLPProcessor:
    """Processes natural language text with advanced NLP techniques"""

    def __init__(self):
        self.sentence_delimiters = [".", "!", "?", "\n\n"]
        self.clause_delimiters = [",", ";", ":", " - "]

        # POS tag mappings
        self.pos_tags = {
            "noun": ["NN", "NNS", "NNP", "NNPS"],
            "verb": ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"],
            "adjective": ["JJ", "JJR", "JJS"],
            "adverb": ["RB", "RBR", "RBS"],
            "pronoun": ["PRP", "PRP$", "WP", "WP$"],
            "determiner": ["DT", "PDT", "WDT"],
            "preposition": ["IN", "TO"],
            "conjunction": ["CC", "IN"],
            "modal": ["MD"],
        }

        # Dependency patterns
        self.dependency_patterns = {
            "subject": ["nsubj", "nsubjpass", "csubj", "csubjpass"],
            "object": ["dobj", "iobj", "pobj"],
            "modifier": ["amod", "advmod", "neg", "nummod"],
            "compound": ["compound", "name", "mwe"],
            "auxiliary": ["aux", "auxpass", "cop"],
            "conjunction": ["conj", "cc", "preconj"],
            "relation": ["acl", "advcl", "relcl"],
        }

        # Semantic patterns
        self.semantic_patterns = {
            "action": r"\b(create|make|build|develop|implement|design|add|remove|delete|update|modify|change|process|handle|manage|configure|setup|deploy|test|validate|verify|check|ensure|provide|enable|disable|allow|prevent|require|support)\b",
            "entity": r"\b(user|admin|customer|client|account|profile|product|item|order|payment|invoice|report|dashboard|page|screen|form|field|button|link|menu|table|list|grid|chart|graph|notification|message|email|file|document|image|video|data|record|entry|transaction|session|token|key|password|role|permission|group|team|organization|company|project|task|issue|ticket|comment|note|tag|category|type|status|state|level|priority|setting|configuration|option|preference|feature|function|service|api|endpoint|resource|database|server|system|application|module|component|package|library|framework|platform|environment|version|release|build|test|log|error|warning|info|debug|metric|statistic|analytics|event|action|operation|process|workflow|pipeline|queue|cache|storage|backup|archive|export|import|sync|integration|connection|network|security|authentication|authorization|encryption|validation|verification|audit|compliance|policy|rule|condition|constraint|limit|threshold|timeout|interval|duration|frequency|schedule|calendar|date|time|timezone|location|address|contact|phone|email|website|url|link|path|route|navigation|search|filter|sort|pagination|scroll|zoom|drag|drop|upload|download|share|print|copy|paste|cut|undo|redo|save|cancel|submit|confirm|approve|reject|publish|draft|archive|delete|restore|refresh|reload|restart|shutdown|start|stop|pause|resume|continue|skip|next|previous|first|last|home|back|forward|up|down|left|right|top|bottom|center|align|resize|rotate|flip|crop|trim|merge|split|combine|separate|group|ungroup|lock|unlock|show|hide|expand|collapse|open|close|minimize|maximize|restore)\b",
            "attribute": r"\b(name|title|description|label|value|text|content|body|header|footer|id|uuid|key|code|number|count|amount|quantity|price|cost|total|subtotal|discount|tax|fee|rate|percentage|ratio|score|rating|rank|weight|size|length|width|height|depth|dimension|area|volume|capacity|speed|velocity|acceleration|time|date|datetime|timestamp|duration|interval|frequency|period|cycle|age|year|month|week|day|hour|minute|second|millisecond|timezone|location|latitude|longitude|altitude|address|street|city|state|country|zipcode|postal|phone|mobile|fax|email|website|url|domain|protocol|port|path|query|parameter|header|cookie|session|token|username|password|pin|secret|public|private|enabled|disabled|active|inactive|visible|hidden|required|optional|valid|invalid|success|failure|error|warning|info|debug|trace|fatal|critical|high|medium|low|primary|secondary|tertiary|default|custom|standard|premium|basic|advanced|pro|enterprise|free|paid|trial|demo|beta|alpha|stable|latest|current|previous|next|new|old|temp|temporary|permanent|draft|published|archived|deleted|pending|processing|completed|failed|cancelled|approved|rejected|blocked|locked|unlocked|open|closed|started|stopped|paused|resumed|online|offline|connected|disconnected|available|unavailable|busy|idle|ready|waiting|loading|saving|syncing|uploading|downloading|importing|exporting|backing|restoring)\b",
            "condition": r"\b(if|when|where|unless|until|while|before|after|during|since|once|whenever|wherever|as soon as|as long as|provided that|given that|assuming that|in case|in the event that)\b",
            "requirement": r"\b(must|shall|should|could|would|will|can|may|might|need|needs|require|requires|required|necessary|essential|critical|important|mandatory|optional|recommended|preferred|desired|expected|intended|supposed|allowed|permitted|prohibited|forbidden|restricted)\b",
            "constraint": r"\b(maximum|minimum|max|min|limit|threshold|boundary|range|between|within|outside|above|below|greater than|less than|equal to|not equal to|at least|at most|no more than|no less than|exactly|approximately|about|around|nearly|roughly|precisely)\b",
        }

        # Linguistic features
        self.linguistic_features = {
            "tense": {
                "past": ["was", "were", "had", "did", "ed"],
                "present": ["is", "are", "am", "has", "have", "do", "does"],
                "future": ["will", "shall", "going to", "would"],
            },
            "voice": {
                "active": ["subject performs action"],
                "passive": ["action performed on subject"],
            },
            "mood": {
                "indicative": ["statement of fact"],
                "imperative": ["command or request"],
                "subjunctive": ["hypothetical or wishful"],
            },
        }

    async def process(self, text: str) -> Dict[str, Any]:
        """
        Process text with comprehensive NLP analysis

        Args:
            text: Input text to process

        Returns:
            Comprehensive NLP analysis results
        """
        # Clean and normalize text
        cleaned_text = self._clean_text(text)

        # Sentence segmentation
        sentences = self._segment_sentences(cleaned_text)

        # Tokenization
        tokens = self._tokenize(cleaned_text)

        # POS tagging
        pos_tags = self._pos_tag(tokens)

        # Named entity recognition
        entities = self._extract_named_entities(tokens, pos_tags)

        # Dependency parsing
        dependencies = self._parse_dependencies(sentences)

        # Semantic analysis
        semantics = self._analyze_semantics(cleaned_text)

        # Syntactic analysis
        syntax = self._analyze_syntax(sentences)

        # Extract key phrases
        key_phrases = self._extract_key_phrases(tokens, pos_tags)

        # Sentiment analysis
        sentiment = self._analyze_sentiment(cleaned_text)

        # Coreference resolution
        coreferences = self._resolve_coreferences(sentences)

        # Extract relationships
        relationships = self._extract_relationships(entities, dependencies)

        # Identify patterns
        patterns = self._identify_patterns(cleaned_text)

        # Language features
        features = self._extract_language_features(sentences)

        return {
            "original": text,
            "cleaned": cleaned_text,
            "sentences": sentences,
            "tokens": tokens,
            "pos_tags": pos_tags,
            "entities": entities,
            "dependencies": dependencies,
            "semantics": semantics,
            "syntax": syntax,
            "key_phrases": key_phrases,
            "sentiment": sentiment,
            "coreferences": coreferences,
            "relationships": relationships,
            "patterns": patterns,
            "features": features,
            "statistics": self._calculate_statistics(text, sentences, tokens),
        }

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = " ".join(text.split())

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(""", "'").replace(""", "'")

        # Fix common typos
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)

        # Normalize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        return text.strip()

    def _segment_sentences(self, text: str) -> List[str]:
        """Segment text into sentences"""
        sentences = []
        current = []

        # Use regex for sentence boundaries
        pattern = r"([.!?])\s*(?=[A-Z]|$)"
        parts = re.split(pattern, text)

        for i in range(0, len(parts) - 1, 2):
            if i + 1 < len(parts):
                sentence = parts[i] + parts[i + 1]
                sentences.append(sentence.strip())

        # Handle last part if exists
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1].strip())

        return sentences if sentences else [text]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Basic word tokenization
        tokens = re.findall(r"\b\w+\b|[^\w\s]", text.lower())

        # Handle contractions
        expanded = []
        contractions = {
            "don't": ["do", "not"],
            "won't": ["will", "not"],
            "can't": ["cannot"],
            "n't": ["not"],
            "'s": ["is"],
            "'re": ["are"],
            "'ve": ["have"],
            "'ll": ["will"],
            "'d": ["would"],
        }

        for token in tokens:
            if token in contractions:
                expanded.extend(contractions[token])
            else:
                expanded.append(token)

        return expanded

    def _pos_tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Part-of-speech tagging"""
        pos_tags = []

        # Simple rule-based POS tagging
        for token in tokens:
            tag = self._guess_pos(token)
            pos_tags.append((token, tag))

        return pos_tags

    def _guess_pos(self, token: str) -> str:
        """Guess POS tag for a token"""
        # Common patterns
        if token in ["the", "a", "an", "this", "that", "these", "those"]:
            return "DT"
        elif token in ["is", "are", "was", "were", "be", "been", "being"]:
            return "VB"
        elif token in ["i", "you", "he", "she", "it", "we", "they"]:
            return "PRP"
        elif token in ["and", "or", "but", "nor", "for", "yet", "so"]:
            return "CC"
        elif token in ["in", "on", "at", "to", "from", "with", "by", "about"]:
            return "IN"
        elif token.endswith("ing"):
            return "VBG"
        elif token.endswith("ed"):
            return "VBD"
        elif token.endswith("ly"):
            return "RB"
        elif token.endswith("er") or token.endswith("est"):
            return "JJR"
        elif token.endswith("s") and len(token) > 2:
            return "NNS"
        elif token[0].isupper():
            return "NNP"
        elif token.isdigit():
            return "CD"
        else:
            return "NN"

    def _extract_named_entities(
        self, tokens: List[str], pos_tags: List[Tuple[str, str]]
    ) -> Dict[str, List[str]]:
        """Extract named entities"""
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "products": [],
            "technologies": [],
            "concepts": [],
        }

        # Extract based on POS patterns
        for i, (token, tag) in enumerate(pos_tags):
            if tag == "NNP":  # Proper noun
                # Check context for entity type
                context = " ".join(
                    [t for t, _ in pos_tags[max(0, i - 2) : min(len(pos_tags), i + 3)]]
                )

                if any(
                    word in context for word in ["user", "person", "people", "customer"]
                ):
                    entities["persons"].append(token)
                elif any(
                    word in context for word in ["company", "organization", "team"]
                ):
                    entities["organizations"].append(token)
                elif any(
                    word in context for word in ["place", "location", "address", "city"]
                ):
                    entities["locations"].append(token)
                elif any(
                    word in context for word in ["product", "service", "application"]
                ):
                    entities["products"].append(token)
                elif any(
                    word in context
                    for word in ["technology", "framework", "language", "tool"]
                ):
                    entities["technologies"].append(token)
                else:
                    entities["concepts"].append(token)

        # Extract technology entities
        tech_keywords = [
            "react",
            "vue",
            "angular",
            "python",
            "javascript",
            "java",
            "aws",
            "docker",
            "kubernetes",
        ]
        for token in tokens:
            if token.lower() in tech_keywords:
                if token not in entities["technologies"]:
                    entities["technologies"].append(token)

        return entities

    def _parse_dependencies(self, sentences: List[str]) -> List[Dict]:
        """Parse syntactic dependencies"""
        dependencies = []

        for sentence in sentences:
            deps = self._extract_sentence_dependencies(sentence)
            dependencies.append({"sentence": sentence, "dependencies": deps})

        return dependencies

    def _extract_sentence_dependencies(self, sentence: str) -> List[Dict]:
        """Extract dependencies from a sentence"""
        deps = []
        tokens = self._tokenize(sentence)

        # Simple dependency extraction
        for i, token in enumerate(tokens):
            if token in ["is", "are", "was", "were"]:
                # Subject-verb-object pattern
                if i > 0:
                    deps.append(
                        {
                            "governor": token,
                            "dependent": tokens[i - 1],
                            "relation": "nsubj",
                        }
                    )
                if i < len(tokens) - 1:
                    deps.append(
                        {
                            "governor": token,
                            "dependent": tokens[i + 1],
                            "relation": "attr",
                        }
                    )

        return deps

    def _analyze_semantics(self, text: str) -> Dict[str, List[str]]:
        """Analyze semantic content"""
        semantics = {}

        for category, pattern in self.semantic_patterns.items():
            matches = re.findall(pattern, text.lower())
            semantics[category] = list(set(matches))

        return semantics

    def _analyze_syntax(self, sentences: List[str]) -> List[Dict]:
        """Analyze syntactic structure"""
        syntax = []

        for sentence in sentences:
            structure = self._analyze_sentence_structure(sentence)
            syntax.append({"sentence": sentence, "structure": structure})

        return syntax

    def _analyze_sentence_structure(self, sentence: str) -> Dict:
        """Analyze structure of a single sentence"""
        tokens = self._tokenize(sentence)

        structure = {
            "type": "simple",  # simple, compound, complex
            "clauses": 1,
            "phrases": [],
        }

        # Check for compound sentences
        if any(conj in tokens for conj in ["and", "but", "or"]):
            structure["type"] = "compound"
            structure["clauses"] = 2

        # Check for complex sentences
        if any(sub in tokens for sub in ["because", "although", "when", "if"]):
            structure["type"] = "complex"
            structure["clauses"] += 1

        return structure

    def _extract_key_phrases(
        self, tokens: List[str], pos_tags: List[Tuple[str, str]]
    ) -> List[str]:
        """Extract key phrases from text"""
        key_phrases = []
        current_phrase = []

        for token, tag in pos_tags:
            # Build noun phrases
            if tag in ["NN", "NNS", "NNP", "NNPS", "JJ"]:
                current_phrase.append(token)
            else:
                if len(current_phrase) > 1:
                    key_phrases.append(" ".join(current_phrase))
                current_phrase = []

        # Add last phrase
        if len(current_phrase) > 1:
            key_phrases.append(" ".join(current_phrase))

        return key_phrases

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "love",
            "like",
            "best",
            "perfect",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "dislike",
            "worst",
            "poor",
            "disappointing",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = "positive"
            score = (
                positive_count / (positive_count + negative_count)
                if negative_count > 0
                else 1.0
            )
        elif negative_count > positive_count:
            sentiment = "negative"
            score = (
                -negative_count / (positive_count + negative_count)
                if positive_count > 0
                else -1.0
            )
        else:
            sentiment = "neutral"
            score = 0.0

        return {
            "label": sentiment,
            "score": score,
            "positive_count": positive_count,
            "negative_count": negative_count,
        }

    def _resolve_coreferences(self, sentences: List[str]) -> List[Dict]:
        """Resolve coreferences in text"""
        coreferences = []

        pronouns = ["it", "they", "them", "this", "that", "these", "those"]

        for i, sentence in enumerate(sentences):
            tokens = self._tokenize(sentence)

            for token in tokens:
                if token in pronouns:
                    # Look for antecedent in previous sentences
                    antecedent = self._find_antecedent(token, sentences[: i + 1])
                    if antecedent:
                        coreferences.append(
                            {
                                "pronoun": token,
                                "antecedent": antecedent,
                                "sentence_index": i,
                            }
                        )

        return coreferences

    def _find_antecedent(
        self, pronoun: str, previous_sentences: List[str]
    ) -> Optional[str]:
        """Find antecedent for a pronoun"""
        # Simple heuristic: look for nearest noun
        for sentence in reversed(previous_sentences):
            tokens = self._tokenize(sentence)
            pos_tags = self._pos_tag(tokens)

            for token, tag in reversed(pos_tags):
                if tag in ["NN", "NNS", "NNP", "NNPS"]:
                    # Check agreement
                    if self._check_agreement(pronoun, token):
                        return token

        return None

    def _check_agreement(self, pronoun: str, noun: str) -> bool:
        """Check pronoun-noun agreement"""
        singular_pronouns = ["it", "this", "that"]
        plural_pronouns = ["they", "them", "these", "those"]

        if pronoun in singular_pronouns:
            return not noun.endswith("s")
        elif pronoun in plural_pronouns:
            return noun.endswith("s")

        return True

    def _extract_relationships(
        self, entities: Dict, dependencies: List[Dict]
    ) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []

        # Extract from dependencies
        for dep_group in dependencies:
            for dep in dep_group.get("dependencies", []):
                if dep["relation"] in ["nsubj", "dobj"]:
                    relationships.append(
                        {
                            "subject": dep.get("dependent"),
                            "predicate": dep.get("governor"),
                            "object": None,
                            "type": "action",
                        }
                    )

        return relationships

    def _identify_patterns(self, text: str) -> Dict[str, List[str]]:
        """Identify linguistic patterns"""
        patterns = {}

        # Identify each pattern type
        for pattern_name, pattern_regex in self.semantic_patterns.items():
            matches = re.findall(pattern_regex, text.lower())
            if matches:
                patterns[pattern_name] = matches

        return patterns

    def _extract_language_features(self, sentences: List[str]) -> Dict[str, Any]:
        """Extract language features"""
        features = {"tense": [], "voice": [], "mood": [], "complexity": "simple"}

        for sentence in sentences:
            tokens = self._tokenize(sentence)

            # Detect tense
            if any(word in tokens for word in ["was", "were", "had", "did"]):
                features["tense"].append("past")
            elif any(word in tokens for word in ["will", "shall", "going"]):
                features["tense"].append("future")
            else:
                features["tense"].append("present")

            # Detect voice
            if "by" in tokens and any(
                word in tokens for word in ["was", "were", "is", "are"]
            ):
                features["voice"].append("passive")
            else:
                features["voice"].append("active")

            # Detect mood
            if sentence.endswith("!") or any(
                word in tokens for word in ["please", "must"]
            ):
                features["mood"].append("imperative")
            elif sentence.endswith("?"):
                features["mood"].append("interrogative")
            else:
                features["mood"].append("indicative")

        # Determine complexity
        avg_sentence_length = (
            sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        )
        if avg_sentence_length > 20:
            features["complexity"] = "complex"
        elif avg_sentence_length > 10:
            features["complexity"] = "moderate"

        return features

    def _calculate_statistics(
        self, text: str, sentences: List[str], tokens: List[str]
    ) -> Dict[str, Any]:
        """Calculate text statistics"""
        words = [t for t in tokens if t.isalnum()]

        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "token_count": len(tokens),
            "average_word_length": sum(len(w) for w in words) / len(words)
            if words
            else 0,
            "average_sentence_length": len(words) / len(sentences) if sentences else 0,
            "vocabulary_size": len(set(words)),
            "lexical_diversity": len(set(words)) / len(words) if words else 0,
            "readability_score": self._calculate_readability(sentences, words),
        }

    def _calculate_readability(self, sentences: List[str], words: List[str]) -> float:
        """Calculate readability score (Flesch Reading Ease)"""
        if not sentences or not words:
            return 0.0

        syllable_count = sum(self._count_syllables(word) for word in words)

        # Flesch Reading Ease formula
        score = (
            206.835
            - 1.015 * (len(words) / len(sentences))
            - 84.6 * (syllable_count / len(words))
        )

        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        vowels = "aeiouAEIOU"
        count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith("e"):
            count -= 1

        # Ensure at least one syllable
        return max(1, count)
