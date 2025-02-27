"""
Base generator class for content generation.
"""
from typing import Dict, List, Any, Optional
import time

from ..agents.base import BaseAgent
from ..collaboration.coordinator import CollaborationCoordinator
from ..utils.logger import Logger


class BaseGenerator:
    """
    Base class for all content generators.
    
    This class provides common functionality for the different types
    of generators (title, TOC, section) and handles the core
    collaboration logic.
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        max_attempts: int = 10,
        force_consensus: bool = True,
        logger: Optional[Logger] = None
    ):
        """
        Initialize a base generator.
        
        Args:
            agents: List of agents to use for generation
            max_attempts: Maximum number of collaboration attempts
            force_consensus: Whether to force consensus after max attempts
            logger: Logger instance for IRC-style logging
        """
        self.agents = agents
        self.max_attempts = max_attempts
        self.force_consensus = force_consensus
        self.logger = logger
        self.coordinator = CollaborationCoordinator(
            agents=agents,
            max_turns=max_attempts,
            force_consensus_after_max_turns=force_consensus,
            logger=logger
        )
    
    def generate(
        self,
        prompt: str,
        context_variables: Optional[Dict[str, Any]] = None,
        starting_agent_index: int = 0
    ) -> Dict[str, Any]:
        """
        Generate content through agent collaboration.
        
        Args:
            prompt: The prompt to initiate the generation
            context_variables: Optional context variables
            starting_agent_index: Index of the agent to start with
            
        Returns:
            Dictionary containing the generation results:
            {
                "success": Whether generation was successful
                "content": The generated content
                "consensus": Whether consensus was reached
                "forced_consensus": Whether consensus was forced
                "attempts": Number of attempts made
                "metadata": Additional metadata from the generation
            }
        """
        start_time = time.time()
        
        if self.logger:
            self.logger.system_message(f"Starting content generation with prompt: {prompt}")
        
        result = self.coordinator.start_collaboration(
            initial_message=prompt,
            context_variables=context_variables,
            starting_agent_index=starting_agent_index
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if self.logger:
            if result["consensus"]:
                if result["forced_consensus"]:
                    self.logger.warning(f"Forced consensus after {result['turns']} turns")
                else:
                    self.logger.success(f"Consensus reached after {result['turns']} turns")
            else:
                self.logger.error(f"Failed to reach consensus after {result['turns']} turns")
            
            self.logger.system_message(f"Generation completed in {duration:.2f} seconds")
        
        return {
            "success": result["consensus"],
            "content": result["content"],
            "consensus": result["consensus"],
            "forced_consensus": result["forced_consensus"],
            "attempts": result["turns"],
            "metadata": result.get("metadata", {}),
            "messages": result["messages"],
            "duration": duration
        }
    
    def _process_generation_result(self, result: Dict[str, Any]) -> Any:
        """
        Process the raw generation result into the expected output format.
        
        This method should be overridden by subclasses to extract the
        specific content type from the generation result.
        
        Args:
            result: Raw generation result from generate()
            
        Returns:
            Processed content in the appropriate format
        """
        raise NotImplementedError("Subclasses must implement _process_generation_result")
    
    def execute(
        self,
        prompt: str,
        context_variables: Optional[Dict[str, Any]] = None,
        starting_agent_index: int = 0
    ) -> Any:
        """
        Execute the full generation process and return the processed result.
        
        Args:
            prompt: The prompt to initiate the generation
            context_variables: Optional context variables
            starting_agent_index: Index of the agent to start with
            
        Returns:
            Processed content in the format specific to the generator type
        """
        result = self.generate(prompt, context_variables, starting_agent_index)
        return self._process_generation_result(result)
