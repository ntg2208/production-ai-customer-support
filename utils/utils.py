# Enhanced logging utilities for agent interactions
import sys
from datetime import datetime
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import centralized time configuration
try:
    from ..config.time_config import get_system_time_iso
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
    from time_config import get_system_time_iso


class Colors:
    """ANSI color codes for terminal output"""
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Reset
    RESET = '\033[0m'
    
    @classmethod
    def colorize(cls, text, color):
        """Apply color to text"""
        return f"{color}{text}{cls.RESET}"


class LogColors:
    """Default color mappings for different log types"""
    USER_MESSAGE = Colors.BRIGHT_CYAN
    AGENT_RESPONSE = Colors.BRIGHT_WHITE
    AGENT_HEADER = Colors.BRIGHT_MAGENTA
    TOOL_CALL = Colors.BRIGHT_YELLOW
    TOOL_RESULT = Colors.BRIGHT_GREEN
    SESSION_INFO = Colors.BRIGHT_BLACK
    ERROR = Colors.BRIGHT_RED
    SUCCESS = Colors.BRIGHT_GREEN


def enhanced_log(level, emoji, message, color=Colors.BRIGHT_WHITE, indent=0):
    """Enhanced logging function with colors and formatting
    
    Args:
        level: Log level (for future use, currently not used but kept for API consistency)
        emoji: Emoji to display with the message
        message: The message to log
        color: ANSI color code for the message
        indent: Number of indentation levels
    """
    # Use centralized time for consistent timestamps
    system_time = get_system_time_iso()
    timestamp = datetime.fromisoformat(system_time).strftime("%H:%M:%S.%f")[:-3]
    indent_str = "  " * indent
    
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        # Terminal supports colors
        colored_message = Colors.colorize(message, color)
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {indent_str}{emoji} {colored_message}")
    else:
        # Fallback for environments that don't support colors
        print(f"[{timestamp}] {indent_str}{emoji} {message}")


async def run_agent_with_enhanced_logging(runner, query, user_id, session_id, show_args=True, max_arg_length=150):
    """
    Enhanced agent running function with improved logging, colors, and better formatting.
    
    Args:
        runner: The agent runner instance
        query: The user query string
        user_id: User identifier
        session_id: Session identifier
        show_args: Whether to display function arguments (default: True)
        max_arg_length: Maximum length for displaying arguments (default: 150)
    """
    
    # Create the content message
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # Log the initial query with bright colors
    enhanced_log("INFO", "👤", f"User Query: {query}", LogColors.USER_MESSAGE)
    enhanced_log("INFO", "📋", f"Session: {session_id} | User: {user_id}", LogColors.SESSION_INFO, indent=1)
    
    print()  # Add spacing
    
    try:
        # Start the agent interaction
        events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)
        
        async for event in events:
            # Handle function calls
            calls = event.get_function_calls()
            if calls:
                enhanced_log("DEBUG", "🔧", "Function Calls Detected", Colors.YELLOW, indent=1)
                for i, call in enumerate(calls, 1):
                    tool_name = call.name
                    arguments = call.args
                    
                    # Log tool name with color
                    enhanced_log("DEBUG", "⚙️", f"Tool #{i}: {tool_name}", LogColors.TOOL_CALL, indent=2)
                    
                    # Log arguments if requested and they're not too long
                    if show_args and arguments:
                        arg_str = str(arguments)
                        if len(arg_str) <= max_arg_length:
                            enhanced_log("DEBUG", "📝", f"Args: {arg_str}", Colors.DIM, indent=3)
                        else:
                            truncated = arg_str[:max_arg_length-3] + "..."
                            enhanced_log("DEBUG", "📝", f"Args: {truncated}", Colors.DIM, indent=3)
            
            # Handle function responses
            responses = event.get_function_responses()
            if responses:
                enhanced_log("DEBUG", "✅", "Function Responses Received", Colors.GREEN, indent=1)
                for i, response in enumerate(responses, 1):
                    tool_name = response.name
                    result = str(response.response)
                    
                    # Log tool result with truncation for readability
                    if len(result) <= 200:
                        result_display = result
                        truncation_indicator = ""
                    else:
                        result_display = result[:200]
                        truncation_indicator = f" ({len(result)} chars total)"
                    
                    enhanced_log("DEBUG", "🎯", f"Result #{i} from {tool_name}: {result_display}{truncation_indicator}", LogColors.TOOL_RESULT, indent=2)
            
            # Handle final response
            if event.is_final_response():
                final_response = event.content.parts[0].text
                enhanced_log("SUCCESS", "🤖", "Agent Final Response:", LogColors.AGENT_HEADER)
                
                # Format the response with proper indentation and brighter colors
                response_lines = final_response.split('\n')
                for line in response_lines:
                    if line.strip():  # Only print non-empty lines
                        enhanced_log("RESPONSE", "💬", line.strip(), LogColors.AGENT_RESPONSE, indent=1)
                
                print()  # Add spacing after response
                
    except Exception as e:
        enhanced_log("ERROR", "❌", f"Error during agent execution: {str(e)}", LogColors.ERROR)
        raise


def create_agent_runner_session(agent, app_name="default_app", user_id="default_user"):
    """
    Convenience function to create a complete session setup for any agent.
    
    Args:
        agent: The agent instance to use
        app_name: Name of the application (default: "default_app")  
        user_id: User identifier (default: "default_user")
    
    Returns:
        tuple: (runner, session_id) ready for use with run_agent_with_enhanced_logging
    """
    session_service = InMemorySessionService()
    
    async def setup():
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id
        )
        runner = Runner(
            agent=agent,
            app_name=app_name, 
            session_service=session_service
        )
        return runner, session.id
    
    return setup()


async def quick_agent_test(agent, query, app_name="test", user_id="test_user"):
    """Quick test function for any agent with enhanced logging"""
    runner, session_id = await create_agent_runner_session(agent, app_name, user_id)
    await run_agent_with_enhanced_logging(runner, query, user_id, session_id)


class LogLevel:
    """Predefined logging level configurations"""
    MINIMAL = {"show_args": False, "max_arg_length": 50}
    STANDARD = {"show_args": True, "max_arg_length": 100}  
    VERBOSE = {"show_args": True, "max_arg_length": 300}
    FULL = {"show_args": True, "max_arg_length": 1000}