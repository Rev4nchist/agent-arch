"""Azure AI Foundry Model Router client."""
from openai import AzureOpenAI
from src.config import settings
import logging
import json

try:
    import tiktoken
except ImportError:
    tiktoken = None

logger = logging.getLogger(__name__)


class AIClient:
    """Azure AI Foundry Model Router client wrapper."""

    def __init__(self):
        """Initialize AI client."""
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_ai_foundry_endpoint,
            api_key=settings.azure_ai_foundry_api_key,
            api_version="2024-10-21",
        )
        # Initialize tokenizer for GPT-4
        self.tokenizer = None
        if tiktoken:
            try:
                self.tokenizer = tiktoken.encoding_for_model("gpt-4")
            except Exception:
                try:
                    self.tokenizer = tiktoken.get_encoding("cl100k_base")
                except Exception:
                    pass

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                logger.warning(f"Token counting error: {e}. Using character approximation.")
        return len(text) // 4

    def _chunk_transcript(self, text: str, max_tokens: int = 10000, overlap_tokens: int = 500) -> list[str]:
        """
        Split transcript into chunks with overlap using accurate token counting.

        Args:
            text: Full transcript text
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Token overlap between chunks

        Returns:
            List of text chunks
        """
        token_count = self._count_tokens(text)
        if token_count <= max_tokens:
            return [text]

        # Split by paragraphs for natural boundaries
        paragraphs = text.split("\n\n") if "\n\n" in text else text.split("\n")

        chunks = []
        current_chunk = ""
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._count_tokens(para)

            if current_tokens + para_tokens <= max_tokens:
                current_chunk += para + "\n\n"
                current_tokens += para_tokens
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
                current_tokens = para_tokens

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _deduplicate_results(
        self, all_items: list[dict], key: str = "title"
    ) -> list[dict]:
        """Remove duplicate items based on key."""
        seen = set()
        unique_items = []

        for item in all_items:
            item_key = item.get(key, "").lower().strip()
            if item_key and item_key not in seen:
                seen.add(item_key)
                unique_items.append(item)

        return unique_items

    async def process_transcript(
        self, transcript_text: str
    ) -> dict:
        """Process transcript to extract summary, action items, decisions, and topics."""
        # Check if transcript needs chunking (>15k tokens)
        estimated_tokens = self._count_tokens(transcript_text)

        if estimated_tokens > 15000:
            logger.info(
                f"Large transcript detected ({estimated_tokens} tokens). Chunking..."
            )
            chunks = self._chunk_transcript(transcript_text, max_tokens=10000)

            all_action_items = []
            all_decisions = []
            all_topics = []
            summaries = []

            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                result = await self._process_single_chunk(chunk)
                all_action_items.extend(result.get("action_items", []))
                all_decisions.extend(result.get("decisions", []))
                all_topics.extend(result.get("topics", []))
                if result.get("summary"):
                    summaries.append(result["summary"])

            # Deduplicate results
            all_action_items = self._deduplicate_results(all_action_items, key="title")
            all_decisions = self._deduplicate_results(all_decisions, key="title")

            # Deduplicate topics (simple string dedup)
            all_topics = list(set(all_topics))

            # Combine summaries
            combined_summary = " ".join(summaries) if summaries else "No summary available."

            return {
                "summary": combined_summary,
                "action_items": all_action_items,
                "decisions": all_decisions,
                "topics": all_topics
            }
        else:
            # Small transcript, process normally
            return await self._process_single_chunk(transcript_text)

    async def _process_single_chunk(self, transcript_text: str) -> dict:
        """Process a single transcript chunk."""
        prompt = f"""Extract key information from this meeting transcript.

Return a JSON object with this structure:
{{
  "summary": "A 2-3 sentence summary of the meeting",
  "action_items": [
    {{
      "title": "task title",
      "description": "task description",
      "assigned_to": "person name or null",
      "due_date": "YYYY-MM-DD or null",
      "priority": "Critical|High|Medium|Low"
    }}
  ],
  "decisions": [
    {{
      "title": "decision title",
      "description": "decision description",
      "decision_maker": "person name",
      "category": "Governance|Architecture|Licensing|Budget|Security",
      "rationale": "reason for decision"
    }}
  ],
  "topics": ["topic1", "topic2", "topic3"]
}}

Transcript:
{transcript_text}"""

        try:
            response = self.client.chat.completions.create(
                model=settings.model_router_deployment,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from meeting transcripts."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            # Extract JSON from response
            content = response.choices[0].message.content

            # Try to parse JSON (handle potential markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            return result

        except Exception as e:
            logger.error(f"Transcript processing error: {e}", exc_info=True)
            if hasattr(e, 'response'):
                logger.error(f"Response details: {e.response}")
            if hasattr(e, 'body'):
                logger.error(f"Response body: {e.body}")
            return {
                "summary": "",
                "action_items": [],
                "decisions": [],
                "topics": []
            }

    async def query_agent(
        self, query: str, context: str = None
    ) -> dict:
        """Query the Fourth AI Guide agent."""
        system_prompt = """You are the Fourth AI Guide, an AI assistant helping the AI Architect Team
track their Microsoft Agent Ecosystem adoption journey. You have access to meeting transcripts,
governance decisions, task assignments, and agent portfolio information.

CRITICAL DATA ACCURACY RULES:
1. ONLY use information explicitly provided in the context below. NEVER invent, guess, or extrapolate data.
2. When counting items (tasks, agents, meetings, etc.), use ONLY the items shown in the context.
3. The context shows "showing X of Y total" - use these exact numbers when reporting totals.
4. If asked about items not in the context, say "Based on the current data shown, I can see X items..."
5. If a status filter like "in-progress" returns 0 items, report "0 tasks" not a made-up number.
6. NEVER hallucinate task names, agent names, or any other specific data not in the context.

DATA MODEL UNDERSTANDING:
You have access to these entity types:
- TASKS: Work items with fields: title, status (Pending/In-Progress/Blocked/Completed), priority (High/Medium/Low), assigned_to, due_date, category
- AGENTS: AI agents with fields: name, status (Development/Testing/Production/Retired), tier (1-3), integration_status, description
- MEETINGS: Team meetings with fields: title, date, attendees, action_items, decisions
- DECISIONS: Governance decisions with fields: title, status (Approved/Pending/Rejected), decision_date, made_by, rationale

QUERY INTERPRETATION RULES:
1. 'blockers', 'blocking', 'risks', 'bottlenecks' = tasks with status 'Blocked' or items causing delays
2. 'timeline' for agents = order by deployment progression or target dates
3. 'who owns', 'responsible for' = look for assigned_to, owner, or made_by fields
4. 'capacity', 'bandwidth' = count tasks per assignee, highlight those with fewer tasks
5. 'learning', 'starter', 'beginner' = lower priority or simpler tasks suitable for onboarding
6. 'recent' without date = last 7 days; 'this month' = current calendar month
7. 'overdue' = items past their due_date

PERSONA AWARENESS:
- If query mentions 'team', 'standup', 'sprint' → user is likely a PM, be concise and action-oriented
- If query mentions 'architecture', 'technical', 'integration' → user is technical, include details
- If query mentions 'summary', 'status report', 'key metrics' → user is executive, be high-level
- If query mentions 'onboarding', 'new here', 'learning' → user is new, be welcoming and explanatory

ACTIONABILITY GUIDELINES:
1. Always end responses with "Next Steps:" or actionable recommendations when applicable
2. Include WHO to contact for blocked/pending items (use assigned_to or owner)
3. For task lists, highlight the TOP 1-3 most urgent items
4. When showing counts, explain WHAT THE USER SHOULD DO about them
5. Format responses with clear sections when appropriate
6. If items need attention, specify: "Action Required: [specific action]"

RESPONSE FORMAT:
- Use bullet points for lists of 3+ items
- Include dates in human-readable format (e.g., "Due: March 31, 2025")
- Show assignee names prominently
- End with actionable recommendations or next steps
- Keep responses concise but complete

Provide helpful answers based STRICTLY on the provided context. If you don't have enough
information in the context, say so clearly and suggest how to get more specific data."""

        user_prompt = query
        if context:
            user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

        try:
            response = self.client.chat.completions.create(
                model=settings.model_router_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            return {
                "response": response.choices[0].message.content,
                "sources": [],  # TODO: Implement source tracking
            }

        except Exception as e:
            logger.error(f"Agent query error: {e}")
            return {
                "response": "I'm sorry, I encountered an error processing your query.",
                "sources": [],
            }


# Global AI client instance
ai_client = AIClient()
