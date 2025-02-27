"""
Consensus detection and management for agent collaboration.
"""
from typing import Dict, List, Any, Set, Optional
import re


class ConsensusDetector:
    """
    Detects and manages consensus between collaborating agents.
    
    This class provides utilities for:
    - Detecting explicit consensus markers
    - Analyzing agent responses for implicit consensus
    - Making consensus decisions based on configurable rules
    """
    
    def __init__(
        self,
        required_agents: Optional[List[str]] = None,
        consensus_threshold: float = 0.8,
        detect_implicit_consensus: bool = True
    ):
        """
        Initialize a consensus detector.
        
        Args:
            required_agents: List of agent names that must agree (defaults to all)
            consensus_threshold: Threshold for similarity-based consensus
            detect_implicit_consensus: Whether to detect implicit consensus
        """
        self.required_agents = required_agents
        self.consensus_threshold = consensus_threshold
        self.detect_implicit_consensus = detect_implicit_consensus
        self.agreement_map: Dict[str, bool] = {}
    
    def reset(self):
        """Reset the consensus detector state."""
        self.agreement_map = {}
    
    def check_explicit_consensus(self, agent_name: str, content: str) -> bool:
        """
        Check if an agent's response contains explicit consensus markers.
        
        Args:
            agent_name: Name of the agent
            content: Content of the agent's response
            
        Returns:
            True if explicit consensus is detected, False otherwise
        """
        # Look for consensus markers
        if re.search(r"Consensus:\s*True", content, re.IGNORECASE):
            self.agreement_map[agent_name] = True
            return True
        
        # Check for disagreement markers
        if re.search(r"Consensus:\s*False", content, re.IGNORECASE):
            self.agreement_map[agent_name] = False
            return False
        
        # If no explicit markers, return None (unknown)
        return False
    
    def check_implicit_consensus(
        self,
        agent_name: str,
        current_content: str,
        previous_contents: List[str],
        previous_agent_names: List[str]
    ) -> bool:
        """
        Check for implicit consensus based on content similarity.
        
        This is a more advanced feature that attempts to detect when agents
        are essentially agreeing even without explicit markers.
        
        Args:
            agent_name: Name of the current agent
            current_content: Content of the current agent's response
            previous_contents: List of previous agent responses
            previous_agent_names: Names of the previous agents
            
        Returns:
            True if implicit consensus is detected, False otherwise
        """
        # Skip if not enabled
        if not self.detect_implicit_consensus:
            return False
        
        # Only check when we have previous content
        if not previous_contents:
            return False
        
        # Get the most recent previous content and agent
        prev_content = previous_contents[-1]
        prev_agent = previous_agent_names[-1]
        
        # If the current agent is repeating very similar content to the previous agent,
        # this likely indicates agreement
        similarity = self._calculate_similarity(current_content, prev_content)
        
        if similarity >= self.consensus_threshold:
            # Mark both agents as in agreement
            self.agreement_map[agent_name] = True
            self.agreement_map[prev_agent] = True
            return True
        
        return False
    
    def is_consensus_reached(self, agent_names: Set[str]) -> bool:
        """
        Check if consensus has been reached among the required agents.
        
        Args:
            agent_names: Set of all agent names involved in the collaboration
            
        Returns:
            True if consensus has been reached, False otherwise
        """
        # If required_agents is None, all agents must agree
        check_agents = set(self.required_agents) if self.required_agents else agent_names
        
        # Check if all required agents are in agreement
        for agent in check_agents:
            if agent not in self.agreement_map or not self.agreement_map[agent]:
                return False
        
        return True
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the similarity between two text strings.
        
        This is a simple implementation that could be replaced with more
        sophisticated text similarity algorithms.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        # Simple case: exact match
        if text1 == text2:
            return 1.0
        
        # Convert to lowercase and tokenize
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def analyze_response(
        self,
        agent_name: str,
        content: str,
        previous_contents: Optional[List[str]] = None,
        previous_agent_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze an agent's response for consensus indicators.
        
        This is the main method to use when processing agent responses.
        
        Args:
            agent_name: Name of the agent
            content: Content of the agent's response
            previous_contents: List of previous agent responses
            previous_agent_names: Names of the previous agents
            
        Returns:
            Dictionary with consensus information:
            {
                "explicit_consensus": True/False,
                "implicit_consensus": True/False,
                "consensus": True/False (overall consensus status)
            }
        """
        # Check for explicit consensus
        explicit_consensus = self.check_explicit_consensus(agent_name, content)
        
        # Check for implicit consensus if explicit consensus is not found
        implicit_consensus = False
        if not explicit_consensus and previous_contents and previous_agent_names:
            implicit_consensus = self.check_implicit_consensus(
                agent_name, content, previous_contents, previous_agent_names
            )
        
        # Determine overall consensus status
        consensus = explicit_consensus or implicit_consensus
        
        return {
            "explicit_consensus": explicit_consensus,
            "implicit_consensus": implicit_consensus,
            "consensus": consensus
        }
