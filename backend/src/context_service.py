"""Context service for AI Guide platform awareness."""
import re
import logging
from typing import List, Optional, Tuple
from src.database import db
from src.models import PlatformDoc, QueryIntent, ContextResult

logger = logging.getLogger(__name__)

PLATFORM_KEYWORDS = {
    "dashboard": ["dashboard", "home", "overview", "stats", "main page"],
    "proposals": ["proposal", "proposals", "decision", "decisions", "governance", "approve", "agreed"],
    "meetings": ["meeting", "meetings", "schedule", "transcript", "agenda", "calendar", "action item"],
    "tasks": ["task", "tasks", "kanban", "todo", "assign", "work item", "pending", "in progress"],
    "agents": ["agent", "agents", "copilot", "bot", "ai agent", "tier", "register"],
    "feedback": ["feedback", "bug", "feature request", "submit", "ticket", "idea", "improvement"],
    "resources": ["resource", "resources", "document", "upload", "library", "pdf", "file"],
    "tech-radar": ["tech radar", "technology", "adopt", "trial", "assess", "hold", "tool"],
    "audit": ["audit", "log", "track", "activity", "history", "compliance"],
    "guide": ["guide", "help", "how to", "how do", "where", "what is", "explain"],
}

NAVIGATION_PATTERNS = [
    r"where (?:can i|do i|is|are)",
    r"how (?:do i|can i|to)",
    r"go to",
    r"navigate",
    r"find (?:the|my|a)",
    r"show me",
    r"take me to",
    r"open",
]

PLATFORM_HELP_PATTERNS = [
    r"what (?:is|are|does)",
    r"how (?:do i|can i|to) (?:create|add|submit|upload|delete|edit|update)",
    r"explain",
    r"help (?:me|with)",
    r"what's the (?:process|workflow|way)",
    r"steps to",
    r"guide me",
]

DATA_QUERY_PATTERNS = [
    r"show (?:me )?(?:my|all|the)",
    r"list (?:all|my|the)",
    r"what (?:tasks|meetings|agents|decisions) (?:are|do i have)",
    r"how many",
    r"count",
    r"assigned to me",
    r"due (?:today|this week|soon)",
]


class ContextService:
    """Service for gathering context based on user queries."""

    def __init__(self):
        self.container = None

    def _get_container(self):
        if not self.container:
            self.container = db.get_container("platform_docs")
        return self.container

    def classify_intent(self, query: str) -> QueryIntent:
        """Classify the intent of a user query."""
        query_lower = query.lower().strip()

        for pattern in DATA_QUERY_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.DATA_QUERY

        for pattern in NAVIGATION_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.NAVIGATION

        for pattern in PLATFORM_HELP_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.PLATFORM_HELP

        for feature, keywords in PLATFORM_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return QueryIntent.PLATFORM_HELP

        return QueryIntent.GENERAL

    def extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from a query."""
        query_lower = query.lower()
        keywords = []

        for feature, feature_keywords in PLATFORM_KEYWORDS.items():
            for keyword in feature_keywords:
                if keyword in query_lower:
                    keywords.append(keyword)

        words = re.findall(r'\b\w+\b', query_lower)
        stop_words = {"the", "a", "an", "is", "are", "how", "do", "i", "can", "to", "what", "where", "when", "my", "me", "in", "on", "for"}
        keywords.extend([w for w in words if w not in stop_words and len(w) > 2])

        return list(set(keywords))

    async def search_platform_docs(self, query: str, limit: int = 5) -> List[PlatformDoc]:
        """Search platform docs by keyword matching."""
        container = self._get_container()
        if not container:
            logger.warning("Platform docs container not available")
            return []

        keywords = self.extract_keywords(query)
        query_lower = query.lower()

        all_docs = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))

        scored_docs = []
        for doc in all_docs:
            score = 0
            doc_keywords = [k.lower() for k in doc.get("keywords", [])]
            doc_title = doc.get("title", "").lower()
            doc_content = doc.get("content", "").lower()

            for keyword in keywords:
                if keyword in doc_keywords:
                    score += 10
                if keyword in doc_title:
                    score += 5
                if keyword in doc_content:
                    score += 2

            if query_lower in doc_title:
                score += 15
            if query_lower in doc_content:
                score += 3

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        return [PlatformDoc(**doc) for _, doc in scored_docs[:limit]]

    def format_docs_as_context(self, docs: List[PlatformDoc]) -> str:
        """Format platform docs as context string for the AI."""
        if not docs:
            return ""

        context_parts = []
        for doc in docs:
            context_parts.append(f"## {doc.title}\n{doc.content}")

        return "\n\n---\n\n".join(context_parts)

    async def get_navigation_context(self) -> str:
        """Get navigation-specific context."""
        container = self._get_container()
        if not container:
            return ""

        query = "SELECT * FROM c WHERE c.category = 'navigation' OR c.id = 'getting-started'"
        docs = list(container.query_items(query=query, enable_cross_partition_query=True))

        if docs:
            return self.format_docs_as_context([PlatformDoc(**d) for d in docs])
        return ""

    async def get_context_for_query(self, query: str, page_context: Optional[dict] = None) -> ContextResult:
        """Gather relevant context based on query intent."""
        intent = self.classify_intent(query)

        context_parts = []
        sources = []

        if intent in [QueryIntent.PLATFORM_HELP, QueryIntent.NAVIGATION]:
            docs = await self.search_platform_docs(query)
            if docs:
                context_parts.append(self.format_docs_as_context(docs))
                sources.extend([d.title for d in docs])

        if intent == QueryIntent.NAVIGATION and not context_parts:
            nav_context = await self.get_navigation_context()
            if nav_context:
                context_parts.append(nav_context)
                sources.append("Platform Navigation")

        if page_context and page_context.get("current_page"):
            page_keywords = self._extract_page_keywords(page_context["current_page"])
            if page_keywords:
                page_docs = await self.search_platform_docs(" ".join(page_keywords), limit=2)
                for doc in page_docs:
                    if doc.title not in sources:
                        context_parts.append(f"## {doc.title} (Current Page Context)\n{doc.content}")
                        sources.append(doc.title)

        return ContextResult(
            context="\n\n---\n\n".join(context_parts) if context_parts else "",
            sources=sources,
            intent=intent
        )

    def _extract_page_keywords(self, page_path: str) -> List[str]:
        """Extract keywords from current page path."""
        page_map = {
            "/": ["dashboard"],
            "/dashboard": ["dashboard"],
            "/decisions": ["proposals", "decisions"],
            "/meetings": ["meetings"],
            "/tasks": ["tasks"],
            "/agents": ["agents"],
            "/feedback": ["feedback"],
            "/resources": ["resources"],
            "/tech-radar": ["tech radar"],
            "/audit": ["audit"],
            "/guide": ["guide"],
        }

        for path, keywords in page_map.items():
            if page_path == path or page_path.startswith(path + "/"):
                return keywords
        return []


context_service = ContextService()
