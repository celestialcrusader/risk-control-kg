"""
Unit Tests for Graph Wavefront Spreading Activation Engine (STORY-MAINT-101).
"""

import pytest
from app.services.graph_wavefront import GraphWavefrontEngine, ActivationSeed


def test_wavefront_spreading_activation_neighbors():
    """Verify spreading activation discovers 1-hop and 2-hop neighbors with decaying energy."""
    engine = GraphWavefrontEngine(energy_decay=0.8, min_energy=0.5)

    # Mock Graph Topology:
    # Seed Node: MAS-7.5
    # Neighbors of MAS-7.5: NIST-CP-9, RISK-DATA-LOSS
    # Neighbors of NIST-CP-9: CIS-10.1
    mock_topology = {
        "MAS-7.5": ["NIST-CP-9", "RISK-DATA-LOSS"],
        "NIST-CP-9": ["CIS-10.1", "MAS-7.5"],
        "RISK-DATA-LOSS": ["MAS-7.5"],
        "CIS-10.1": ["NIST-CP-9"],
    }

    def mock_neighbor_fetcher(node_id: str):
        return mock_topology.get(node_id, [])

    seed = ActivationSeed(
        new_node_id="CUSTOM-BACKUP-CTRL",
        seed_node_id="MAS-7.5",
        initial_energy=1.0,
    )

    infected_nodes = engine.propagate(seed, neighbor_fetcher=mock_neighbor_fetcher)

    # Verify 1-Hop neighbors are infected with E = 1.0 * 0.8 = 0.8
    assert "NIST-CP-9" in infected_nodes
    assert infected_nodes["NIST-CP-9"] == pytest.approx(0.8, 0.01)

    assert "RISK-DATA-LOSS" in infected_nodes
    assert infected_nodes["RISK-DATA-LOSS"] == pytest.approx(0.8, 0.01)

    # Verify 2-Hop neighbor is infected with E = 0.8 * 0.8 = 0.64
    assert "CIS-10.1" in infected_nodes
    assert infected_nodes["CIS-10.1"] == pytest.approx(0.64, 0.01)


def test_wavefront_propagation_halts_below_threshold():
    """Verify propagation terminates when energy decays below min_energy threshold."""
    engine = GraphWavefrontEngine(energy_decay=0.5, min_energy=0.3)

    mock_topology = {
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
        "D": ["E"],
    }

    def mock_neighbor_fetcher(node_id: str):
        return mock_topology.get(node_id, [])

    seed = ActivationSeed(new_node_id="NODE-X", seed_node_id="A", initial_energy=1.0)
    infected = engine.propagate(seed, neighbor_fetcher=mock_neighbor_fetcher)

    # A -> B (0.5)
    assert "B" in infected
    # B -> C (0.25 < min_energy 0.3) -> should not propagate to D
    assert "C" not in infected
    assert "D" not in infected
