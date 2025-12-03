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
        self, query: str, context: str = None, platform_context: str = None, intent: str = None
    ) -> dict:
        """Query the Fourth AI Guide agent."""
        system_prompt = self._build_system_prompt(platform_context, intent)

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
                "sources": [],
            }

        except Exception as e:
            logger.error(f"Agent query error: {e}")
            return {
                "response": "I'm sorry, I encountered an error processing your query.",
                "sources": [],
            }

    def _build_system_prompt(self, platform_context: str = None, intent: str = None) -> str:
        """Build system prompt with optional platform documentation context."""
        base_prompt = """You are the Fourth AI Guide, the intelligent assistant for the Fourth AI Architecture Platform.

## Your Role
Help team members navigate and use the platform effectively. You can:
- Explain platform features and how to use them
- Guide users through workflows and processes
- Answer questions about platform data (meetings, tasks, agents, etc.)
- Suggest next steps and related features

## Platform Overview
The Fourth AI Architecture Platform helps the AI Architect Team manage:
- **Dashboard**: Overview of platform activity and quick stats
- **Proposals & Decisions**: Track governance decisions and proposals
- **Meetings Hub**: Schedule meetings, process transcripts, track action items
- **Tasks**: Manage work items in list or kanban view
- **Agents**: Registry of AI agents across the organization
- **Feedback Hub**: Internal ticketing for bugs, features, and ideas
- **Resources Library**: Document storage and knowledge base
- **Tech Radar**: Technology adoption recommendations
- **Audit Trail**: Activity tracking and compliance

## Response Guidelines
1. Be concise but thorough
2. Include specific navigation paths (e.g., "Go to Tasks → Click 'New Task'")
3. Mention related features when relevant
4. If you reference documentation, cite the source
5. Suggest next steps or actions the user can take
6. If you don't know something, say so clearly
7. Use markdown formatting: **bold** for headers, bullet points for lists

SPECIAL QUERIES - HANDLE THESE FIRST:
When users ask "What can I ask you about?", "Help", "What do you do?", or similar introductory questions,
provide a friendly capability overview:

"I'm the Fourth AI Guide, your assistant for navigating the Fourth AI Architecture Platform. Here's what I can help you with:

🏠 **Platform Navigation**
- How do I navigate the platform?
- Where can I find [feature]?

📋 **Tasks & Work Items**
- How do I create a task?
- What's the difference between Architecture and Feedback tasks?

🤖 **AI Agent Management**
- How do I register a new agent?
- What's the agent approval workflow?

📅 **Meetings & Decisions**
- How do I schedule a meeting?
- How do proposals become decisions?

💬 **Feedback & Tickets**
- How do I submit a bug report?
- How does the feedback triage work?

💡 **Tips**: Ask me 'How do I create a task?' or 'Where can I submit feedback?' to get started!"
"""

        if intent in ["platform_help", "navigation"]:
            base_prompt += """

## Platform Documentation Context
When answering platform questions, structure your response as:

1. **Direct Answer**: Answer the question concisely
2. **How To** (if applicable): Step-by-step instructions
3. **Tips**: Any helpful tips or shortcuts
4. **Related**: Mention related features or next steps

Keep responses focused and actionable.
"""

        if platform_context:
            base_prompt += f"""

## Relevant Documentation
The following platform documentation is relevant to this query:

{platform_context}
"""

        base_prompt += """

## Data Query Guidelines
When users ask about their data (tasks, meetings, agents):
- Use ONLY information explicitly provided in the context
- When counting items, use exact numbers from context
- Never hallucinate data not present in context
- If data isn't available, explain how to find it

CRITICAL: Base your response STRICTLY on provided context and documentation."""

        return base_prompt

    def query_agent_streaming(
        self, query: str, context: str = None, platform_context: str = None, intent: str = None
    ):
        """Stream query responses from the Fourth AI Guide agent."""
        system_prompt = self._build_system_prompt(platform_context, intent)

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
                stream=True,
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Streaming agent query error: {e}")
            yield f"I'm sorry, I encountered an error processing your query: {str(e)}"


# Global AI client instance
ai_client = AIClient()
