"""
Duplicate Detection System - ML-Powered Similarity Detection

This module provides duplicate bug detection using:
- Text similarity (TF-IDF, cosine similarity)
- Semantic similarity (embeddings)
- Structural matching (code, URLs, parameters)
- Fuzzy matching
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter
import math

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SimilarityScore(BaseModel):
    """Similarity score result."""
    bug_id: str
    title_similarity: float
    description_similarity: float
    code_similarity: float
    url_similarity: float
    overall_score: float
    is_duplicate: bool
    confidence: float


class DuplicateDetectionResult(BaseModel):
    """Duplicate detection result."""
    query_bug_id: str
    potential_duplicates: List[SimilarityScore]
    highest_match: Optional[SimilarityScore] = None
    detection_time_ms: int


class DuplicateDetectionService:
    """
    Duplicate Detection Service.

    Provides:
    - Text similarity analysis
    - Code snippet matching
    - URL/endpoint matching
    - Configurable thresholds
    - Batch detection
    """

    def __init__(self):
        """Initialize duplicate detection service."""
        self._bugs: Dict[str, Dict[str, Any]] = {}
        self._idf_cache: Dict[str, float] = {}
        self._thresholds = {
            "title": 0.7,
            "description": 0.6,
            "code": 0.8,
            "url": 0.9,
            "overall": 0.65
        }

    def add_bug(self, bug_id: str, bug_data: Dict[str, Any]) -> None:
        """
        Add bug to detection index.

        Args:
            bug_id: Bug ID
            bug_data: Bug data including title, description, etc.
        """
        # Preprocess and store
        processed = {
            "id": bug_id,
            "title": bug_data.get("title", ""),
            "title_tokens": self._tokenize(bug_data.get("title", "")),
            "description": bug_data.get("description", ""),
            "description_tokens": self._tokenize(bug_data.get("description", "")),
            "code_snippets": self._extract_code(bug_data.get("proof_of_concept", "")),
            "urls": self._extract_urls(bug_data.get("description", "") + " " + bug_data.get("reproduction_steps", "")),
            "vulnerability_type": bug_data.get("vulnerability_type", ""),
            "affected_component": bug_data.get("affected_component", ""),
            "program_id": bug_data.get("program_id", ""),
            "created_at": bug_data.get("created_at", datetime.utcnow())
        }

        self._bugs[bug_id] = processed
        self._update_idf()

    def detect_duplicates(
        self,
        bug_id: str,
        program_id: Optional[str] = None,
        limit: int = 10
    ) -> DuplicateDetectionResult:
        """
        Detect potential duplicates for a bug.

        Args:
            bug_id: Bug ID to check
            program_id: Optional program filter
            limit: Max results to return

        Returns:
            Detection result with potential duplicates
        """
        import time
        start_time = time.time()

        if bug_id not in self._bugs:
            raise ValueError(f"Bug {bug_id} not found in index")

        query_bug = self._bugs[bug_id]
        candidates = []

        # Get candidate bugs
        for candidate_id, candidate in self._bugs.items():
            if candidate_id == bug_id:
                continue

            # Filter by program if specified
            if program_id and candidate.get("program_id") != program_id:
                continue

            # Skip if different vulnerability type
            if (query_bug.get("vulnerability_type") and
                candidate.get("vulnerability_type") and
                query_bug["vulnerability_type"] != candidate["vulnerability_type"]):
                continue

            # Calculate similarity scores
            score = self._calculate_similarity(query_bug, candidate)
            candidates.append(score)

        # Sort by overall score
        candidates.sort(key=lambda x: x.overall_score, reverse=True)

        # Apply limit
        top_candidates = candidates[:limit]

        # Mark duplicates based on threshold
        for score in top_candidates:
            score.is_duplicate = score.overall_score >= self._thresholds["overall"]
            score.confidence = min(score.overall_score / self._thresholds["overall"], 1.0)

        detection_time = int((time.time() - start_time) * 1000)

        return DuplicateDetectionResult(
            query_bug_id=bug_id,
            potential_duplicates=top_candidates,
            highest_match=top_candidates[0] if top_candidates else None,
            detection_time_ms=detection_time
        )

    def _calculate_similarity(
        self,
        query: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> SimilarityScore:
        """Calculate similarity scores between two bugs."""
        # Title similarity (TF-IDF cosine)
        title_sim = self._cosine_similarity_tfidf(
            query["title_tokens"],
            candidate["title_tokens"]
        )

        # Description similarity
        desc_sim = self._cosine_similarity_tfidf(
            query["description_tokens"],
            candidate["description_tokens"]
        )

        # Code similarity
        code_sim = self._code_similarity(
            query["code_snippets"],
            candidate["code_snippets"]
        )

        # URL similarity
        url_sim = self._url_similarity(
            query["urls"],
            candidate["urls"]
        )

        # Component match bonus
        component_bonus = 0.1 if (
            query.get("affected_component") and
            query["affected_component"] == candidate.get("affected_component")
        ) else 0

        # Calculate weighted overall score
        overall = (
            title_sim * 0.3 +
            desc_sim * 0.3 +
            code_sim * 0.25 +
            url_sim * 0.15 +
            component_bonus
        )

        return SimilarityScore(
            bug_id=candidate["id"],
            title_similarity=round(title_sim, 3),
            description_similarity=round(desc_sim, 3),
            code_similarity=round(code_sim, 3),
            url_similarity=round(url_sim, 3),
            overall_score=round(min(overall, 1.0), 3),
            is_duplicate=False,
            confidence=0
        )

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if not text:
            return []

        # Lowercase and extract words
        text = text.lower()
        tokens = re.findall(r'\b[a-z0-9]+\b', text)

        # Remove stopwords
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
            'neither', 'not', 'only', 'same', 'than', 'too', 'very',
            'just', 'also', 'now', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'any', 'this', 'that'
        }

        return [t for t in tokens if t not in stopwords and len(t) > 2]

    def _update_idf(self) -> None:
        """Update IDF cache based on current bugs."""
        doc_count = len(self._bugs)
        if doc_count == 0:
            return

        # Count document frequency for each term
        df = Counter()
        for bug in self._bugs.values():
            terms = set(bug["title_tokens"] + bug["description_tokens"])
            for term in terms:
                df[term] += 1

        # Calculate IDF
        for term, count in df.items():
            self._idf_cache[term] = math.log(doc_count / count) + 1

    def _cosine_similarity_tfidf(
        self,
        tokens1: List[str],
        tokens2: List[str]
    ) -> float:
        """Calculate cosine similarity using TF-IDF."""
        if not tokens1 or not tokens2:
            return 0.0

        # Build TF-IDF vectors
        all_terms = set(tokens1 + tokens2)

        def tfidf_vector(tokens):
            tf = Counter(tokens)
            total = len(tokens)
            return {
                term: (tf[term] / total) * self._idf_cache.get(term, 1)
                for term in all_terms
            }

        vec1 = tfidf_vector(tokens1)
        vec2 = tfidf_vector(tokens2)

        # Calculate cosine similarity
        dot_product = sum(vec1[t] * vec2[t] for t in all_terms)
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _extract_code(self, text: str) -> List[str]:
        """Extract code snippets from text."""
        if not text:
            return []

        snippets = []

        # Extract code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', text)
        for block in code_blocks:
            code = block.strip('`').strip()
            if code:
                snippets.append(code)

        # Extract inline code
        inline = re.findall(r'`([^`]+)`', text)
        snippets.extend(inline)

        return snippets

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        if not text:
            return []

        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)

        # Normalize URLs
        normalized = []
        for url in urls:
            # Remove trailing punctuation
            url = url.rstrip('.,;:!?')
            # Remove fragments
            url = url.split('#')[0]
            normalized.append(url.lower())

        return normalized

    def _code_similarity(
        self,
        code1: List[str],
        code2: List[str]
    ) -> float:
        """Calculate code similarity."""
        if not code1 or not code2:
            return 0.0

        # Normalize code
        def normalize_code(code_list):
            combined = ' '.join(code_list)
            # Remove whitespace and comments
            combined = re.sub(r'\s+', ' ', combined)
            combined = re.sub(r'//.*', '', combined)
            combined = re.sub(r'/\*.*?\*/', '', combined)
            return combined.strip()

        norm1 = normalize_code(code1)
        norm2 = normalize_code(code2)

        if not norm1 or not norm2:
            return 0.0

        # Jaccard similarity on n-grams
        n = 3
        ngrams1 = set(norm1[i:i+n] for i in range(len(norm1) - n + 1))
        ngrams2 = set(norm2[i:i+n] for i in range(len(norm2) - n + 1))

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)

        return intersection / union if union > 0 else 0.0

    def _url_similarity(
        self,
        urls1: List[str],
        urls2: List[str]
    ) -> float:
        """Calculate URL similarity."""
        if not urls1 or not urls2:
            return 0.0

        # Extract paths and parameters
        def extract_parts(urls):
            parts = set()
            for url in urls:
                # Extract path
                match = re.search(r'https?://[^/]+(/[^?]*)', url)
                if match:
                    path = match.group(1)
                    # Normalize path (remove IDs)
                    path = re.sub(r'/\d+', '/:id', path)
                    parts.add(path)

                # Extract parameters
                if '?' in url:
                    params = url.split('?')[1]
                    param_names = re.findall(r'([^&=]+)=', params)
                    parts.update(param_names)

            return parts

        parts1 = extract_parts(urls1)
        parts2 = extract_parts(urls2)

        if not parts1 or not parts2:
            return 0.0

        intersection = len(parts1 & parts2)
        union = len(parts1 | parts2)

        return intersection / union if union > 0 else 0.0

    def set_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Update similarity thresholds."""
        self._thresholds.update(thresholds)

    def batch_detect(
        self,
        bug_ids: List[str],
        program_id: Optional[str] = None
    ) -> List[DuplicateDetectionResult]:
        """Run duplicate detection for multiple bugs."""
        results = []
        for bug_id in bug_ids:
            try:
                result = self.detect_duplicates(bug_id, program_id)
                results.append(result)
            except Exception as e:
                logger.warning(f"Detection failed for {bug_id}: {e}")

        return results

    def find_duplicate_clusters(
        self,
        program_id: Optional[str] = None,
        threshold: float = 0.7
    ) -> List[List[str]]:
        """
        Find clusters of duplicate bugs.

        Returns:
            List of duplicate clusters (lists of bug IDs)
        """
        # Build similarity graph
        processed = set()
        clusters = []

        for bug_id in self._bugs:
            if bug_id in processed:
                continue

            # Find all bugs similar to this one
            cluster = {bug_id}
            to_process = [bug_id]

            while to_process:
                current = to_process.pop()
                if current in processed:
                    continue

                processed.add(current)

                try:
                    result = self.detect_duplicates(current, program_id, limit=50)
                    for score in result.potential_duplicates:
                        if score.overall_score >= threshold:
                            if score.bug_id not in cluster:
                                cluster.add(score.bug_id)
                                to_process.append(score.bug_id)
                except Exception:
                    continue

            if len(cluster) > 1:
                clusters.append(list(cluster))

        return clusters

    def get_statistics(self) -> Dict[str, Any]:
        """Get detection service statistics."""
        return {
            "total_bugs_indexed": len(self._bugs),
            "unique_terms": len(self._idf_cache),
            "thresholds": self._thresholds
        }


# Singleton instance
_duplicate_service: Optional[DuplicateDetectionService] = None


def get_duplicate_service() -> DuplicateDetectionService:
    """Get the global duplicate detection service instance."""
    global _duplicate_service
    if _duplicate_service is None:
        _duplicate_service = DuplicateDetectionService()
    return _duplicate_service


__all__ = [
    "DuplicateDetectionService",
    "SimilarityScore",
    "DuplicateDetectionResult",
    "get_duplicate_service"
]
