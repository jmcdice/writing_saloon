"""
Coordinator for managing agent collaboration.
"""
from typing import Dict, List, Any, Optional, Tuple
import time

from ..agents.base import BaseAgent
from ..providers.openai_provider import OpenAIProvider
from ..providers.anthropic_provider import AnthropicProvider
from ..utils.logger import Logger


class CollaborationCoordinator:
    """
    Manages collaboration between agents.
    
    The coordinator is responsible for:
    - Starting and managing the collaboration process
    - Handling agent handoffs
    - Maintaining the conversation context
    - Detecting consensus
    - Managing turn limits and fallbacks
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        max_turns: int = 10,
        force_consensus_after_max_turns: bool = True,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        logger: Optional[Logger] = None
    ):
        """
        Initialize a collaboration coordinator.
        
        Args:
            agents: List of agents to coordinate
            max_turns: Maximum number of turns allowed
            force_consensus_after_max_turns: Whether to force consensus after max turns
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            logger: Logger instance for IRC-style logging
        """
        self.agents = agents
        self.max_turns = max_turns
        self.force_consensus_after_max_turns = force_consensus_after_max_turns
        self.messages = []
        self.turn_count = 0
        self.consecutive_failures = 0
        self.logger = logger
        
        # Initialize providers
        self.providers = {
            "openai": OpenAIProvider(api_key=openai_api_key),
            "anthropic": AnthropicProvider(api_key=anthropic_api_key)
        }
        
        # Validate agents
        if len(agents) < 2:
            raise ValueError("At least two agents are required for collaboration")
    
    def start_collaboration(
        self,
        initial_message: str,
        context_variables: Optional[Dict[str, Any]] = None,
        starting_agent_index: int = 0
    ) -> Dict[str, Any]:
        """
        Start the collaboration process between agents.
        
        Args:
            initial_message: The initial message to start the conversation
            context_variables: Optional context variables to pass to agents
            starting_agent_index: Index of the agent to start with
            
        Returns:
            Dictionary containing the collaboration results:
            {
                "consensus": Whether consensus was reached
                "forced_consensus": Whether consensus was forced
                "content": The final content
                "turns": Number of turns taken
                "messages": Full message history
            }
        """
        if starting_agent_index >= len(self.agents):
            raise ValueError(f"Invalid starting agent index: {starting_agent_index}")
        
        # Initialize conversation with the user message
        self.messages = [{"role": "user", "content": initial_message}]
        self.turn_count = 0
        self.consecutive_failures = 0
        
        current_agent_index = starting_agent_index
        forced_consensus = False
        context_variables = context_variables or {}
        
        # Log the initial message
        if self.logger:
            self.logger.user_message(initial_message)
        
        # Start the collaboration loop
        while self.turn_count < self.max_turns:
            try:
                # Get the current agent
                current_agent = self.agents[current_agent_index]
                
                # Log the current turn
                if self.logger:
                    self.logger.system_message(f"Turn {self.turn_count + 1}: {current_agent.name}'s turn")
                
                # Get the appropriate provider for this agent
                provider = self.providers.get(current_agent.provider)
                if not provider:
                    raise ValueError(f"Unknown provider: {current_agent.provider}")
                
                # Get the agent's response
                response = provider.generate_response(
                    instructions=current_agent.instructions,
                    messages=self.messages,
                    functions=current_agent.functions,
                    temperature=0.7,  # Explicitly pass default temp if needed
                    context_variables=context_variables,
                    model=current_agent.model  # Pass the agent's model
                )
                
                # Extract the content
                content = response["content"]
                
                # Process the response
                processed = current_agent.process_response(content)
                
                # Add the response to the conversation
                self.messages.append({"role": "assistant", "content": content})
                
                # Log the agent's response
                if self.logger:
                    self.logger.agent_message(current_agent.name, processed["content"])
                
                # Check for consensus
                if processed.get("consensus", False):
                    if self.logger:
                        self.logger.success(f"Consensus reached after {self.turn_count + 1} turns!")
                    return {
                        "consensus": True,
                        "forced_consensus": False,
                        "content": processed["content"],
                        "turns": self.turn_count + 1,
                        "messages": self.messages,
                        "metadata": {k: v for k, v in processed.items() if k not in ["content", "consensus", "raw_response"]}
                    }
                
                # Update context variables with any extracted metadata
                for key, value in processed.items():
                    if key not in ["content", "consensus", "raw_response", "agent"]:
                        context_variables[key] = value
                
                # Move to the next agent
                current_agent_index = (current_agent_index + 1) % len(self.agents)
                self.turn_count += 1
                self.consecutive_failures = 0
                
            except Exception as e:
                self.consecutive_failures += 1
                if self.logger:
                    self.logger.error(f"Error during agent collaboration: {str(e)}")
                
                # If we've had too many consecutive failures, break the loop
                if self.consecutive_failures >= 3:
                    if self.logger:
                        self.logger.error("Too many consecutive failures, forcing consensus")
                    break
                
                # Wait a moment before retrying
                time.sleep(1)
        
        # If we've reached the maximum number of turns without consensus
        if self.force_consensus_after_max_turns:
            if self.logger:
                self.logger.warning(f"Forcing consensus after {self.max_turns} turns")
            
            # Use the last agent's response as the final content
            final_content = self._force_consensus()
            forced_consensus = True
            
            return {
                "consensus": True,
                "forced_consensus": True,
                "content": final_content,
                "turns": self.turn_count,
                "messages": self.messages,
                "metadata": {}
            }
        else:
            if self.logger:
                self.logger.error(f"Failed to reach consensus after {self.max_turns} turns")
            
            return {
                "consensus": False,
                "forced_consensus": False,
                "content": None,
                "turns": self.turn_count,
                "messages": self.messages,
                "metadata": {}
            }
    
    def _force_consensus(self) -> str:
        """
        Force consensus by using the last agent's response.
        
        Returns:
            The extracted content from the last response
        """
        # Find the last assistant message
        for message in reversed(self.messages):
            if message["role"] == "assistant":
                # Process the content to extract the actual content
                for agent in self.agents:
                    processed = agent.process_response(message["content"])
                    if "content" in processed and processed["content"]:
                        return processed["content"]
                
                # If we couldn't process it, just return the raw content
                return message["content"]
        
        # If there are no assistant messages, return a placeholder
        return "No content available due to consensus failure."
