"""
Document Assistant - Chatbot interface for document generator
Interprets natural language commands and executes app functions
"""

import re
from typing import Any, Dict, List, Optional, Tuple
import json
import asyncio
import gradio as gr

try:
    from pydantic_ai import Agent
    from pydantic import BaseModel
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    # Create a simple BaseModel replacement
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


class CommandIntent(BaseModel):
    """Parsed user intent from chatbot"""
    action: str
    parameters: Dict[str, Any]
    confidence: float
    response: str


class DocumentAssistant:
    """Chatbot assistant for document operations"""
    
    def __init__(self):
        # Initialize the AI agent for parsing intents if available
        if PYDANTIC_AI_AVAILABLE:
            try:
                self.agent = Agent(
                    'openai:gpt-4o-mini',
                    system_prompt="""You are a document assistant that helps users create and manage documents.
                    Parse user requests into specific actions with parameters.
                    
                    Available actions:
                    - create_outline: Create a new document outline from a prompt
                    - add_ai_block: Add an AI-generated section
                    - add_text_block: Add a manual text section
                    - delete_block: Remove a section
                    - update_block: Update section content
                    - generate_document: Generate the full document
                    - export_markdown: Export as Markdown
                    - export_docx: Export as Word document
                    - upload_resource: Handle file upload
                    - assign_resource: Assign resource to a section
                    - reset_document: Clear and start over
                    - help: Show available commands
                    
                    Return a JSON with: action, parameters, confidence (0-1), and a friendly response message.
                    """
                )
            except Exception:
                self.agent = None
        else:
            self.agent = None
        
        # Simple pattern matching for common commands (fallback)
        self.patterns = {
            r"create.*(document|outline).*about (.+)": ("create_outline", self._extract_topic),
            r"add.*(section|block).*(?:about|on|for) (.+)": ("add_ai_block", self._extract_topic),
            r"generate.*document": ("generate_document", lambda m: {}),
            r"export.*(?:as )?(word|docx)": ("export_docx", lambda m: {}),
            r"export.*(?:as )?(markdown|md)": ("export_markdown", lambda m: {}),
            r"delete.*(?:section|block)": ("delete_block", lambda m: {}),
            r"reset|clear|start over": ("reset_document", lambda m: {}),
            r"help|commands|what can you do": ("help", lambda m: {}),
        }
    
    def _extract_topic(self, match) -> Dict[str, str]:
        """Extract topic from regex match"""
        topic = match.group(2) if match.lastindex >= 2 else match.group(1)
        return {"topic": topic}
    
    async def parse_intent(self, message: str, context: Dict[str, Any]) -> CommandIntent:
        """Parse user message into structured intent using AI or patterns"""
        
        if self.agent:
            try:
                # Try AI parsing first
                result = await self.agent.run(
                    f"Parse this command: {message}\nCurrent context: Has {len(context.get('blocks', []))} blocks"
                )
                
                # Parse AI response
                if isinstance(result.data, str):
                    intent_data = json.loads(result.data)
                    return CommandIntent(**intent_data)
            except Exception as e:
                print(f"AI parsing failed: {e}, falling back to patterns")
        
        # Fallback to pattern matching
        message_lower = message.lower().strip()
        
        for pattern, (action, param_extractor) in self.patterns.items():
            match = re.search(pattern, message_lower)
            if match:
                params = param_extractor(match)
                return CommandIntent(
                    action=action,
                    parameters=params,
                    confidence=0.8,
                    response=self._get_response_for_action(action, params)
                )
        
        # Unknown command
        return CommandIntent(
            action="unknown",
            parameters={},
            confidence=0.0,
            response="I didn't understand that command. Type 'help' to see what I can do."
        )
    
    def _get_response_for_action(self, action: str, params: Dict) -> str:
        """Generate friendly response for action"""
        responses = {
            "create_outline": f"Creating document outline about {params.get('topic', 'your topic')}...",
            "add_ai_block": f"Adding section about {params.get('topic', 'that topic')}...",
            "add_text_block": "Adding a text section for you to edit...",
            "generate_document": "Generating the full document content...",
            "export_docx": "Exporting document as Word file...",
            "export_markdown": "Exporting document as Markdown...",
            "delete_block": "Removing the selected section...",
            "reset_document": "Clearing the document to start fresh...",
            "help": "Here's what I can help you with:\n• Create document outlines\n• Add/edit sections\n• Generate content\n• Export documents\n• Manage resources"
        }
        return responses.get(action, "Processing your request...")
    
    async def execute_command(
        self,
        intent: CommandIntent,
        app_functions: Dict[str, callable],
        current_state: Dict[str, Any]
    ) -> Tuple[Any, str]:
        """Execute the parsed command using app functions"""
        
        if intent.action == "unknown":
            return None, intent.response
        
        if intent.action == "help":
            return None, intent.response
        
        # Map intent actions to actual function calls
        action_mapping = {
            "create_outline": lambda: app_functions["handle_start_draft_click"](
                intent.parameters.get("topic", ""),
                current_state.get("resources", []),
                current_state.get("session_id")
            ),
            "add_ai_block": lambda: app_functions["add_ai_block"](
                current_state.get("blocks", []),
                current_state.get("focused_block_id"),
                initial_content=f"Write about {intent.parameters.get('topic', '')}"
            ),
            "add_text_block": lambda: app_functions["add_text_block"](
                current_state.get("blocks", []),
                current_state.get("focused_block_id")
            ),
            "generate_document": lambda: app_functions["handle_document_generation"](
                current_state.get("blocks", []),
                current_state.get("resources", []),
                current_state.get("session_id")
            ),
            "export_docx": lambda: app_functions["handle_download_click"](
                current_state.get("blocks", []),
                "docx"
            ),
            "export_markdown": lambda: app_functions["handle_download_click"](
                current_state.get("blocks", []),
                "md"
            ),
            "delete_block": lambda: app_functions["delete_block"](
                current_state.get("blocks", []),
                current_state.get("focused_block_id")
            ),
            "reset_document": lambda: app_functions["reset_document"](),
        }
        
        if intent.action in action_mapping:
            try:
                # Don't await since these are sync functions
                result = action_mapping[intent.action]()
                return result, intent.response
            except Exception as e:
                return None, f"Error executing command: {str(e)}"
        
        return None, "Command recognized but not yet implemented."


def create_chatbot_interface():
    """Create the Gradio chatbot interface components"""
    
    with gr.Column():
        gr.Markdown("### 🤖 Document Assistant")
        gr.Markdown("Ask me to help create, edit, or manage your document!")
        
        chatbot = gr.Chatbot(
            height=400,
            placeholder="Type a command to get started...",
            bubble_full_width=False,
            elem_classes="assistant-chatbot"
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Try: 'Create a document about machine learning' or 'Add a section on neural networks'",
                show_label=False,
                scale=4,
                lines=1
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)
            clear_btn = gr.Button("Clear", scale=1)
        
        with gr.Accordion("📚 Available Commands", open=False):
            gr.Markdown("""
            **Document Creation:**
            - "Create a document about [topic]"
            - "Start an outline for [topic]"
            
            **Section Management:**
            - "Add a section about [topic]"
            - "Add a text block"
            - "Delete this section"
            - "Update the section content"
            
            **Generation & Export:**
            - "Generate the document"
            - "Export as Word"
            - "Export as Markdown"
            
            **Other:**
            - "Reset/Clear document"
            - "Help" - Show commands
            """)
    
    return chatbot, msg_input, send_btn, clear_btn


def handle_chat_message(
    message: str,
    history: List[List[str]],
    blocks_state: List[Dict],
    resources_state: List[Dict],
    session_id: str,
    focused_block_id: Optional[str],
    app_functions: Dict[str, callable]
) -> Tuple[List[List[str]], List[Dict], List[Dict], Optional[str]]:
    """Process chat message and execute commands (synchronous version)"""
    
    if not message:
        return history, blocks_state, resources_state, None
    
    # Initialize assistant (could cache this)
    assistant = DocumentAssistant()
    
    # Prepare context
    context = {
        "blocks": blocks_state,
        "resources": resources_state,
        "session_id": session_id,
        "focused_block_id": focused_block_id
    }
    
    # Parse intent using asyncio.run for sync context
    intent = asyncio.run(assistant.parse_intent(message, context))
    
    # Execute command
    result, response = asyncio.run(assistant.execute_command(
        intent, app_functions, context
    ))
    
    # Update history
    history.append([message, response])
    
    # Return updated states based on action
    if intent.action == "create_outline" and result:
        # Result should be new blocks
        return history, result, resources_state, response
    elif intent.action in ["add_ai_block", "add_text_block", "delete_block"] and result:
        # Result should be updated blocks
        return history, result, resources_state, response
    elif intent.action == "generate_document" and result:
        # Result should be updated blocks with generated content
        return history, result, resources_state, response
    elif intent.action in ["export_docx", "export_markdown"] and result:
        # Result is a file path, response includes download info
        return history, blocks_state, resources_state, f"{response}\n\nFile ready: {result}"
    elif intent.action == "reset_document" and result:
        # reset_document returns multiple values, extract blocks and resources
        if isinstance(result, tuple) and len(result) >= 4:
            # Result is (title, desc, resources, blocks, outline, json, session, ...)
            new_resources = result[2]  # resources_state
            new_blocks = result[3]     # blocks_state
            return history, new_blocks, new_resources, response
        else:
            return history, [], [], response
    else:
        # No state change
        return history, blocks_state, resources_state, response