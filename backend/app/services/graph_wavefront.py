"""
Graph Wavefront Spreading Activation Engine ("Zombie Infection") (STORY-MAINT-101).

Propagates localized neighbor activation from newly linked seed nodes, triggering
targeted micro-NLI evaluations across 1-hop and 2-hop graph clusters with decaying energy.
"""

import logging
from collections import deque
from typing import Dict, List, Callable, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ActivationSeed(BaseModel):
    new_node_id: str
    seed_node_id: str
    initial_energy: float = Field(default=1.0, ge=0.0, le=1.0)


class GraphWavefrontEngine:
    """Spreading activation engine for local neighborhood graph discovery."""

    def __init__(self, energy_decay: float = 0.80, min_energy: float = 0.50):
        self.energy_decay = energy_decay
        self.min_energy = min_energy

    def propagate(
        self,
        seed: ActivationSeed,
        neighbor_fetcher: Callable[[str], List[str]],
    ) -> Dict[str, float]:
        """
        Executes wavefront propagation starting at seed_node_id.
        Returns dictionary of {infected_node_id: energy_level}.
        """
        infected: Dict[str, float] = {}
        visited = {seed.new_node_id, seed.seed_node_id}
        
        # Queue: (current_node_id, current_energy)
        queue = deque([(seed.seed_node_id, seed.initial_energy)])

        while queue:
            curr_node, curr_energy = queue.popleft()
            decayed_energy = round(curr_energy * self.energy_decay, 4)

            if decayed_energy < self.min_energy:
                continue

            neighbors = neighbor_fetcher(curr_node)
            for nbr in neighbors:
                if nbr not in visited and decayed_energy >= self.min_energy:
                    visited.add(nbr)
                    infected[nbr] = decayed_energy
                    queue.append((nbr, decayed_energy))

        logger.info(
            "Wavefront propagation from seed %s infected %d neighbor nodes",
            seed.seed_node_id, len(infected)
        )
        return infected
