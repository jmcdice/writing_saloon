"""
Handoff mechanism for agent collaboration.
"""
from typing import Dict, Any, Callable, Optional, List
import functools


def create_handoff_function(
    target_agent_name: str,
    context_variables: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Create a handoff function for transferring control between agents.
    
    Args:
        target_agent_name: Name of the agent to hand off to
        context_variables: Optional context variables to include in the handoff
        
    Returns:
        A function that can be called to initiate a handoff
    """
    context_variables = context_variables or {}
    
    @functools.wraps(create_handoff_function)
    def handoff_function(message: str = "") -> Dict[str, Any]:
        """
        Initiate a handoff to another agent.
        
        Args:
            message: Optional message to include with the handoff
            
        Returns:
            Dictionary containing handoff information
        """
        return {
            "handoff_to": target_agent_name,
            "message": message,
            "context_variables": context_variables
        }
    
    # Set a name for the function based on the target agent
    handoff_function.__name__ = f"handoff_to_{target_agent_name.lower()}"
    
    return handoff_function


class HandoffManager:
    """
    Manages handoffs between agents during collaboration.
    
    This class handles:
    - Creating handoff functions for agents
    - Processing handoff requests
    - Maintaining context during handoffs
    """
    
    def __init__(self, agent_names: List[str]):
        """
        Initialize a handoff manager.
        
        Args:
            agent_names: List of agent names in the system
        """
        self.agent_names = agent_names
        self.current_context: Dict[str, Any] = {}
    
    def create_handoff_functions(self) -> Dict[str, Dict[str, Callable]]:
        """
        Create handoff functions for all agent pairs.
        
        Returns:
            Dictionary mapping agent names to their handoff functions
        """
        handoff_functions = {}
        
        for source_agent in self.agent_names:
            agent_handoffs = {}
            
            for target_agent in self.agent_names:
                if source_agent != target_agent:
                    handoff_func = create_handoff_function(
                        target_agent,
                        self.current_context
                    )
                    agent_handoffs[target_agent] = handoff_func
            
            handoff_functions[source_agent] = agent_handoffs
        
        return handoff_functions
    
    def update_context(self, new_context: Dict[str, Any]):
        """
        Update the current context with new variables.
        
        Args:
            new_context: New context variables to add/update
        """
        self.current_context.update(new_context)
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context variables.
        
        Returns:
            Dictionary of current context variables
        """
        return self.current_context.copy()
    
    def reset_context(self):
        """Reset the context to an empty state."""
        self.current_context = {}
    
    def process_handoff(
        self,
        response: Dict[str, Any],
        current_agent_index: int
    ) -> int:
        """
        Process a handoff request and determine the next agent.
        
        Args:
            response: Response dictionary from an agent
            current_agent_index: Index of the current agent
            
        Returns:
            Index of the next agent to take a turn
        """
        # If there's no handoff, just go to the next agent
        if "handoff_to" not in response:
            return (current_agent_index + 1) % len(self.agent_names)
        
        # Get the target agent name
        target_agent = response["handoff_to"]
        
        # Update context if provided
        if "context_variables" in response and response["context_variables"]:
            self.update_context(response["context_variables"])
        
        # Find the index of the target agent
        try:
            target_index = self.agent_names.index(target_agent)
            return target_index
        except ValueError:
            # If the target agent doesn't exist, just go to the next agent
            return (current_agent_index + 1) % len(self.agent_names)
