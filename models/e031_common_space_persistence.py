#!/usr/bin/env python3
"""E-031 common-space persistence diagnostic.

E-030 found a second coarse-grid component in the matched ``pair < 0.02``
tail, but its fine and coarse component counts lived on different node
complexes.  This module recomputes only the unaccepted ``49/96`` and
``25/48`` endpoints and puts both matched pair-margin fields on exactly the
same coarse physical nodes and four-neighbour graph.

For two scalar fields on one finite graph, bottleneck stability gives
``d_B <= epsilon``, where ``epsilon`` is their common-node sup difference.
A finite zero-dimensional feature with lifetime ``p`` costs ``p/2`` to match
to the persistence diagonal.  E-031 therefore requires the strict inequality
``p > 2*epsilon`` before the observed cross-grid discrepancy can force an
off-diagonal counterpart.  Failure of that screen does not prove that a
feature is noise or absent; it leaves the feature unresolved.

The existing full matched common window is the theorem-level primary graph.
The positive-source induced graph is retained as the requested source-layer
sensitivity.  Persistence and epsilon are unweighted.  Cylindrical volume
and literal source-charge weights are reported separately and never alter
the filtration.

No endpoint from this module is accepted, checkpointed, or promoted as
evidence for a continuum solution, a physical field, artificial gravity,
inertial control, spacetime engineering, faster-than-light travel, or
propulsion.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any, Iterable

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e026_nonsymmetric_amg as e026
import models.e028_fine_grid_campaign as e028
import models.e029_cone_safe_campaign as e029
import models.e030_margin_spectrum as e030
from models.e026_nonsymmetric_amg import AmgConfiguration


BASELINE_AMPLITUDE = e030.BASELINE_AMPLITUDE
VERIFICATION_AMPLITUDES = e030.VERIFICATION_AMPLITUDES
LOW_PAIR_THRESHOLD = 0.02
COARSE_TO_FINE_INDEX_RATIO = 2
POSITIVE_LIFETIME_TOLERANCE = 0.0


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint E-031 and every reused numerical implementation."""

    paths = {
        "e031_campaign": Path(__file__).resolve(),
        "e030_campaign": Path(e030.__file__).resolve(),
        "e029_campaign": Path(e029.__file__).resolve(),
        "e028_campaign": Path(e028.__file__).resolve(),
        "e025_operator": Path(e025.__file__).resolve(),
        "e026_amg": Path(e026.__file__).resolve(),
        "research_requirements": (
            Path(__file__).resolve().parents[1]
            / "requirements-research.txt"
        ),
    }
    repository_root = Path(__file__).resolve().parents[1]
    return {
        "campaign": "E-031",
        "campaign_schema": 1,
        "modules": {
            name: {
                "path": str(path.relative_to(repository_root)),
                "sha256": _sha256_file(path),
            }
            for name, path in paths.items()
        },
        "strategy": {
            "accepted_baseline_amplitude": BASELINE_AMPLITUDE,
            "verification_amplitudes": list(VERIFICATION_AMPLITUDES),
            "matched_difference_step": e029.MATCHED_DIFFERENCE_STEP,
            "common_window_radius": e029.COMMON_WINDOW_RADIUS,
            "low_pair_threshold": LOW_PAIR_THRESHOLD,
            "adjacency": "four_neighbour_no_diagonals",
            "filtration": (
                "lower-star graph filtration: vertex value f(v), edge value "
                "max(f(u),f(v)), ordinary H0 intervals [birth, death)"
            ),
            "stability_screen": (
                "A finite feature is forced away from the diagonal only "
                "when lifetime p is strictly greater than 2*epsilon."
            ),
            "domains": {
                "full_common_window": (
                    "primary theorem-level graph containing every exactly "
                    "coincident matched-window coarse node"
                ),
                "positive_source_support": (
                    "conditional source-layer induced-graph sensitivity; "
                    "mask boundaries can change deaths or essential classes"
                ),
            },
            "lineage_policy": (
                "All E-031 roots are transient diagnostics. Accepted lineage "
                "remains the immutable E-028 6/12 checkpoint."
            ),
        },
    }


def _coarse_to_fine_nodes(
    fine_system: Any,
    coarse_system: Any,
    coarse_nodes: np.ndarray,
) -> np.ndarray:
    """Map coarse nodes to exact fine-grid lattice nodes."""

    ratio = coarse_system.grid.spacing / fine_system.grid.spacing
    if not math.isclose(
        ratio,
        COARSE_TO_FINE_INDEX_RATIO,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise ValueError("E-031 requires an exact 2:1 coarse/fine spacing")
    coarse_nodes = np.asarray(coarse_nodes, dtype=int)
    coarse_i = np.rint(
        coarse_system.rho[coarse_nodes] / coarse_system.grid.spacing
    ).astype(int)
    coarse_j = np.rint(
        coarse_system.z[coarse_nodes] / coarse_system.grid.spacing
    ).astype(int)
    fine_i = COARSE_TO_FINE_INDEX_RATIO * coarse_i
    fine_j = COARSE_TO_FINE_INDEX_RATIO * coarse_j
    fine_nodes = fine_system.index_map[fine_i, fine_j]
    if np.any(fine_nodes < 0):
        raise ValueError("a coarse node has no interior fine-grid counterpart")
    if not np.array_equal(
        fine_system.rho[fine_nodes],
        coarse_system.rho[coarse_nodes],
    ) or not np.array_equal(
        fine_system.z[fine_nodes],
        coarse_system.z[coarse_nodes],
    ):
        raise ValueError("coarse/fine mapped coordinates are not identical")
    return np.asarray(fine_nodes, dtype=int)


def _matched_values_on_nodes(
    system: Any,
    field: np.ndarray,
    requested_nodes: np.ndarray,
) -> np.ndarray:
    values, evaluated_nodes = e030._matched_pair_values(system, field)
    dense = np.full(system.size, np.nan, dtype=float)
    dense[evaluated_nodes] = values
    selected = dense[np.asarray(requested_nodes, dtype=int)]
    if not np.all(np.isfinite(selected)):
        raise ValueError("requested node lies outside matched reconstruction")
    return selected


def _common_node_bundle(
    fine_system: Any,
    coarse_system: Any,
    fine_source: np.ndarray,
    coarse_source: np.ndarray,
    fine_fields: dict[str, np.ndarray],
    coarse_fields: dict[str, np.ndarray],
) -> dict[str, Any]:
    """Evaluate every field on one ordered set of coarse physical nodes."""

    _coarse_baseline_values, coarse_nodes = e030._matched_pair_values(
        coarse_system,
        coarse_fields["stage6"],
    )
    fine_nodes = _coarse_to_fine_nodes(
        fine_system,
        coarse_system,
        coarse_nodes,
    )
    fine_source_values = np.asarray(fine_source)[fine_nodes]
    coarse_source_values = np.asarray(coarse_source)[coarse_nodes]
    if not np.array_equal(fine_source_values, coarse_source_values):
        raise ValueError("fine/coarse source values differ on common nodes")

    labels = ("stage6",) + tuple(
        f"{amplitude:.17g}" for amplitude in VERIFICATION_AMPLITUDES
    )
    values: dict[str, dict[str, np.ndarray]] = {}
    for label in labels:
        values[label] = {
            "fine": _matched_values_on_nodes(
                fine_system,
                fine_fields[label],
                fine_nodes,
            ),
            "coarse": _matched_values_on_nodes(
                coarse_system,
                coarse_fields[label],
                coarse_nodes,
            ),
        }

    return {
        "coarse_nodes": np.asarray(coarse_nodes, dtype=int),
        "fine_nodes": fine_nodes,
        "rho": coarse_system.rho[coarse_nodes],
        "z": coarse_system.z[coarse_nodes],
        "source": coarse_source_values,
        "weights": e025.nodal_volume_weights(coarse_system)[coarse_nodes],
        "values": values,
    }


def _build_induced_graph(
    system: Any,
    common_global_nodes: np.ndarray,
    selected_common_indices: np.ndarray,
) -> dict[str, Any]:
    """Build an induced four-neighbour graph and explicit crop boundary."""

    common_global_nodes = np.asarray(common_global_nodes, dtype=int)
    selected_common_indices = np.asarray(selected_common_indices, dtype=int)
    selected_global_nodes = common_global_nodes[selected_common_indices]
    local_from_global = np.full(system.size, -1, dtype=int)
    local_from_global[selected_global_nodes] = np.arange(
        selected_global_nodes.size,
        dtype=int,
    )
    spacing = float(system.grid.spacing)
    edges: list[tuple[int, int]] = []
    crop_boundary = np.zeros(selected_global_nodes.size, dtype=bool)
    for local_node, global_node in enumerate(selected_global_nodes):
        grid_i = int(round(float(system.rho[global_node]) / spacing))
        grid_j = int(round(float(system.z[global_node]) / spacing))
        for delta_i, delta_j in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            next_i = grid_i + delta_i
            next_j = grid_j + delta_j
            if (
                next_i < 0
                or next_j < 0
                or next_i >= system.index_map.shape[0]
                or next_j >= system.index_map.shape[1]
            ):
                continue
            neighbor_global = int(system.index_map[next_i, next_j])
            if neighbor_global < 0:
                continue
            neighbor_local = int(local_from_global[neighbor_global])
            if neighbor_local < 0:
                crop_boundary[local_node] = True
            elif local_node < neighbor_local:
                edges.append((local_node, neighbor_local))
    edge_array = np.asarray(edges, dtype=np.int64).reshape((-1, 2))
    return {
        "selected_common_indices": selected_common_indices,
        "global_nodes": selected_global_nodes,
        "edges": edge_array,
        "crop_boundary": crop_boundary,
    }


def _graph_component_count(vertex_count: int, edges: np.ndarray) -> int:
    parent = np.arange(vertex_count, dtype=int)

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = int(parent[node])
        return node

    for first, second in np.asarray(edges, dtype=int):
        root_first = find(int(first))
        root_second = find(int(second))
        if root_first != root_second:
            parent[root_second] = root_first
    return len({find(node) for node in range(vertex_count)})


def _bbox(
    rho: np.ndarray,
    z: np.ndarray,
    members: np.ndarray,
) -> dict[str, float]:
    return {
        "rho_min": float(np.min(rho[members])),
        "rho_max": float(np.max(rho[members])),
        "z_min": float(np.min(z[members])),
        "z_max": float(np.max(z[members])),
    }


def lower_star_h0_persistence(
    values: np.ndarray,
    rho: np.ndarray,
    z: np.ndarray,
    edges: np.ndarray,
    crop_boundary: np.ndarray,
) -> dict[str, Any]:
    """Compute deterministic ordinary-H0 lower-star persistence on a graph."""

    values = np.asarray(values, dtype=float)
    rho = np.asarray(rho, dtype=float)
    z = np.asarray(z, dtype=float)
    edges = np.asarray(edges, dtype=int).reshape((-1, 2))
    crop_boundary = np.asarray(crop_boundary, dtype=bool)
    vertex_count = int(values.size)
    if (
        rho.size != vertex_count
        or z.size != vertex_count
        or crop_boundary.size != vertex_count
    ):
        raise ValueError("persistence graph arrays have inconsistent sizes")
    if not np.all(np.isfinite(values)):
        raise ValueError("persistence values must be finite")
    if edges.size and (
        np.min(edges) < 0 or np.max(edges) >= vertex_count
    ):
        raise ValueError("persistence edge endpoint is out of range")

    parent = np.arange(vertex_count, dtype=int)
    active = np.zeros(vertex_count, dtype=bool)
    birth = values.copy()
    birth_vertex = np.arange(vertex_count, dtype=int)
    rho_min = rho.copy()
    rho_max = rho.copy()
    z_min = z.copy()
    z_max = z.copy()
    member_count = np.ones(vertex_count, dtype=int)
    touches_boundary = crop_boundary.copy()
    finite_bars: list[dict[str, Any]] = []

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = int(parent[node])
        return node

    def union(first: int, second: int, level: float) -> None:
        root_first = find(first)
        root_second = find(second)
        if root_first == root_second:
            return
        key_first = (float(birth[root_first]), int(birth_vertex[root_first]))
        key_second = (
            float(birth[root_second]),
            int(birth_vertex[root_second]),
        )
        survivor, dying = (
            (root_first, root_second)
            if key_first <= key_second
            else (root_second, root_first)
        )
        lifetime = float(level - birth[dying])
        if lifetime < -1.0e-14:
            raise RuntimeError("negative persistence lifetime")
        lifetime = max(lifetime, 0.0)
        finite_bars.append(
            {
                "feature_id": int(birth_vertex[dying]),
                "birth": float(birth[dying]),
                "death": float(level),
                "lifetime": lifetime,
                "birth_vertex": int(birth_vertex[dying]),
                "birth_coordinate": {
                    "rho": float(rho[birth_vertex[dying]]),
                    "z": float(z[birth_vertex[dying]]),
                },
            }
        )
        parent[dying] = survivor
        rho_min[survivor] = min(rho_min[survivor], rho_min[dying])
        rho_max[survivor] = max(rho_max[survivor], rho_max[dying])
        z_min[survivor] = min(z_min[survivor], z_min[dying])
        z_max[survivor] = max(z_max[survivor], z_max[dying])
        member_count[survivor] += member_count[dying]
        touches_boundary[survivor] = bool(
            touches_boundary[survivor] or touches_boundary[dying]
        )

    vertex_order = np.argsort(values, kind="stable")
    edge_levels = (
        np.maximum(values[edges[:, 0]], values[edges[:, 1]])
        if edges.size
        else np.empty(0, dtype=float)
    )
    edge_order = np.argsort(edge_levels, kind="stable")
    vertex_cursor = 0
    edge_cursor = 0
    while vertex_cursor < vertex_count:
        level = float(values[vertex_order[vertex_cursor]])
        vertex_end = vertex_cursor
        while (
            vertex_end < vertex_count
            and float(values[vertex_order[vertex_end]]) == level
        ):
            active[vertex_order[vertex_end]] = True
            vertex_end += 1
        while (
            edge_cursor < edge_order.size
            and float(edge_levels[edge_order[edge_cursor]]) < level
        ):
            raise RuntimeError("an edge event preceded an endpoint")
        edge_end = edge_cursor
        while (
            edge_end < edge_order.size
            and float(edge_levels[edge_order[edge_end]]) == level
        ):
            edge_index = int(edge_order[edge_end])
            first = int(edges[edge_index, 0])
            second = int(edges[edge_index, 1])
            if not active[first] or not active[second]:
                raise RuntimeError("lower-star edge has an inactive endpoint")
            union(first, second, level)
            edge_end += 1
        vertex_cursor = vertex_end
        edge_cursor = edge_end
    if edge_cursor != edge_order.size:
        raise RuntimeError("unprocessed persistence edges remain")

    roots = sorted({find(node) for node in range(vertex_count)})
    essential_bars = [
        {
            "feature_id": int(birth_vertex[root]),
            "birth": float(birth[root]),
            "death": None,
            "lifetime": None,
            "birth_vertex": int(birth_vertex[root]),
            "birth_coordinate": {
                "rho": float(rho[birth_vertex[root]]),
                "z": float(z[birth_vertex[root]]),
            },
            "terminal_node_count": int(member_count[root]),
            "terminal_bbox": {
                "rho_min": float(rho_min[root]),
                "rho_max": float(rho_max[root]),
                "z_min": float(z_min[root]),
                "z_max": float(z_max[root]),
            },
            "terminal_touches_crop_boundary": bool(touches_boundary[root]),
        }
        for root in roots
    ]

    adjacency: list[list[int]] = [[] for _ in range(vertex_count)]
    for first, second in edges:
        adjacency[int(first)].append(int(second))
        adjacency[int(second)].append(int(first))
    for row in finite_bars:
        if float(row["lifetime"]) <= POSITIVE_LIFETIME_TOLERANCE:
            row["dying_branch_open_sublevel_node_count"] = 0
            row["dying_branch_open_sublevel_bbox"] = None
            row["dying_branch_open_sublevel_touches_crop_boundary"] = False
            continue
        death = float(row["death"])
        birth_node = int(row["birth_vertex"])
        open_sublevel = values < death
        if not open_sublevel[birth_node]:
            raise RuntimeError("positive bar birth is absent below its death")
        visited = np.zeros(vertex_count, dtype=bool)
        queue: deque[int] = deque([birth_node])
        visited[birth_node] = True
        members: list[int] = []
        while queue:
            node = queue.popleft()
            members.append(node)
            for neighbor in adjacency[node]:
                if open_sublevel[neighbor] and not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        member_array = np.asarray(members, dtype=int)
        row["dying_branch_open_sublevel_node_count"] = int(
            member_array.size
        )
        row["dying_branch_open_sublevel_bbox"] = _bbox(
            rho,
            z,
            member_array,
        )
        row["dying_branch_open_sublevel_touches_crop_boundary"] = bool(
            np.any(crop_boundary[member_array])
        )
    finite_bars.sort(
        key=lambda row: (
            float(row["birth"]),
            float(row["death"]),
            int(row["feature_id"]),
        )
    )
    return {
        "dying_branch_support_definition": (
            "connected component containing the birth vertex in the strict "
            "open sublevel f < death; invariant to equal-level edge order"
        ),
        "finite_bars": finite_bars,
        "essential_bars": essential_bars,
    }


def _threshold_components(
    values: np.ndarray,
    rho: np.ndarray,
    z: np.ndarray,
    edges: np.ndarray,
    crop_boundary: np.ndarray,
    source: np.ndarray,
    weights: np.ndarray,
    persistence: dict[str, Any],
    *,
    threshold: float,
) -> list[dict[str, Any]]:
    """Describe strict sublevel components and their persistence intervals."""

    values = np.asarray(values, dtype=float)
    edges = np.asarray(edges, dtype=int).reshape((-1, 2))
    selected = values < threshold
    adjacency: list[list[int]] = [[] for _ in range(values.size)]
    for first, second in edges:
        adjacency[int(first)].append(int(second))
        adjacency[int(second)].append(int(first))
    finite_by_birth = {
        int(row["birth_vertex"]): row
        for row in persistence["finite_bars"]
    }
    essential_by_birth = {
        int(row["birth_vertex"]): row
        for row in persistence["essential_bars"]
    }
    support = np.asarray(source) > 0.0
    weights = np.asarray(weights, dtype=float)
    volume_total = float(np.sum(weights[support]))
    charge_weights = weights * np.asarray(source, dtype=float)
    charge_total = float(np.sum(charge_weights[support]))
    visited = np.zeros(values.size, dtype=bool)
    rows: list[dict[str, Any]] = []
    for start in np.flatnonzero(selected):
        if visited[start]:
            continue
        queue: deque[int] = deque([int(start)])
        visited[start] = True
        members: list[int] = []
        while queue:
            node = queue.popleft()
            members.append(node)
            for neighbor in adjacency[node]:
                if selected[neighbor] and not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        member_array = np.asarray(members, dtype=int)
        birth_vertex = min(
            members,
            key=lambda node: (float(values[node]), int(node)),
        )
        interval = finite_by_birth.get(
            birth_vertex,
            essential_by_birth.get(birth_vertex),
        )
        if interval is None:
            raise RuntimeError("threshold component has no persistence class")
        support_members = member_array[support[member_array]]
        volume_weight = float(np.sum(weights[support_members]))
        charge_weight = float(np.sum(charge_weights[support_members]))
        rows.append(
            {
                "node_count": int(member_array.size),
                "source_support_node_count": int(support_members.size),
                "bbox_at_threshold": _bbox(rho, z, member_array),
                "touches_crop_boundary_at_threshold": bool(
                    np.any(crop_boundary[member_array])
                ),
                "minimum_value": float(np.min(values[member_array])),
                "maximum_value": float(np.max(values[member_array])),
                "source_support_volume_weight_fraction": (
                    volume_weight / volume_total
                    if volume_total > 0.0
                    else 0.0
                ),
                "source_charge_weight_fraction": (
                    charge_weight / charge_total
                    if charge_total > 0.0
                    else 0.0
                ),
                "persistence_interval": interval,
            }
        )
    rows.sort(
        key=lambda row: (
            row["source_support_volume_weight_fraction"],
            row["node_count"],
        ),
        reverse=True,
    )
    source_rank = 0
    for row in rows:
        if row["source_support_node_count"] <= 0:
            row["role"] = "background_component"
            continue
        row["role"] = (
            "dominant_source_component"
            if source_rank == 0
            else "detached_source_component"
        )
        source_rank += 1
    return rows


def _persistence_summary(
    values: np.ndarray,
    rho: np.ndarray,
    z: np.ndarray,
    edges: np.ndarray,
    crop_boundary: np.ndarray,
    source: np.ndarray,
    weights: np.ndarray,
) -> dict[str, Any]:
    persistence = lower_star_h0_persistence(
        values,
        rho,
        z,
        edges,
        crop_boundary,
    )
    finite_bars = persistence["finite_bars"]
    positive_bars = [
        row
        for row in finite_bars
        if float(row["lifetime"]) > POSITIVE_LIFETIME_TOLERANCE
    ]
    zero_bars = [
        row
        for row in finite_bars
        if float(row["lifetime"]) <= POSITIVE_LIFETIME_TOLERANCE
    ]
    positive_bars_by_lifetime = sorted(
        positive_bars,
        key=lambda row: (
            float(row["lifetime"]),
            -int(row["feature_id"]),
        ),
        reverse=True,
    )
    threshold_components = _threshold_components(
        values,
        rho,
        z,
        edges,
        crop_boundary,
        source,
        weights,
        persistence,
        threshold=LOW_PAIR_THRESHOLD,
    )
    return {
        "ordinary_h0_interval_convention": "[birth, death)",
        "strict_threshold_component_rule": (
            f"pair margin < {LOW_PAIR_THRESHOLD:.2f}"
        ),
        "finite_bar_count": len(finite_bars),
        "positive_finite_bar_count": len(positive_bars),
        "zero_lifetime_bar_count": len(zero_bars),
        "essential_bar_count": len(persistence["essential_bars"]),
        "positive_finite_bars": positive_bars_by_lifetime,
        "zero_lifetime_bars_sha256": _sha256_json(zero_bars),
        "essential_bars": persistence["essential_bars"],
        "components_below_threshold": threshold_components,
    }


def _weighted_deficit_summary(
    baseline: np.ndarray,
    current: np.ndarray,
    weights: np.ndarray,
) -> dict[str, Any]:
    baseline = np.asarray(baseline, dtype=float)
    current = np.asarray(current, dtype=float)
    weights = np.asarray(weights, dtype=float)
    use = weights > 0.0
    if not np.any(use):
        raise ValueError("deficit spectrum has no positive weight")
    baseline = baseline[use]
    current = current[use]
    weights = weights[use]
    deficit = np.maximum(baseline - current, 0.0)
    total = float(np.sum(weights))
    return {
        "total_weight": total,
        "weighted_mean_positive_deficit": float(
            np.sum(weights * deficit) / total
        ),
        "weighted_rms_positive_deficit": float(
            np.sqrt(np.sum(weights * deficit**2) / total)
        ),
        "weight_fraction_with_decreased_margin": float(
            np.sum(weights[current < baseline]) / total
        ),
        "positive_deficit_quantiles": e030._weighted_quantiles(
            deficit,
            weights,
        ),
    }


def common_deficit_spectra(
    baseline_fine: np.ndarray,
    current_fine: np.ndarray,
    baseline_coarse: np.ndarray,
    current_coarse: np.ndarray,
    source: np.ndarray,
    volume_weights: np.ndarray,
) -> dict[str, Any]:
    """Compare both grids with identical nodes and identical two weightings."""

    source = np.asarray(source, dtype=float)
    volume_weights = np.asarray(volume_weights, dtype=float)
    support = (source > 0.0) & (volume_weights > 0.0)
    if not np.any(support):
        raise ValueError("common deficit spectrum has no source support")
    measures = {
        "source_support_volume": volume_weights[support],
        "source_charge": volume_weights[support] * source[support],
    }
    result: dict[str, Any] = {
        "definition": (
            "Common-node positive margin deficit max(stage6-current,0), "
            "using one coarse cylindrical quadrature for both fields. "
            "Topology and epsilon remain unweighted."
        ),
        "source_support_node_count": int(np.count_nonzero(support)),
        "spectra": {},
    }
    for name, measure_weights in measures.items():
        fine = _weighted_deficit_summary(
            np.asarray(baseline_fine)[support],
            np.asarray(current_fine)[support],
            measure_weights,
        )
        coarse = _weighted_deficit_summary(
            np.asarray(baseline_coarse)[support],
            np.asarray(current_coarse)[support],
            measure_weights,
        )
        fine_mean = float(fine["weighted_mean_positive_deficit"])
        coarse_mean = float(coarse["weighted_mean_positive_deficit"])
        result["spectra"][name] = {
            "fine": fine,
            "coarse": coarse,
            "coarse_to_fine_mean_deficit_ratio": (
                coarse_mean / fine_mean if fine_mean > 0.0 else None
            ),
        }
    return result


def _diagram_candidate_matches(
    coarse_interval: dict[str, Any],
    fine_positive_bars: Iterable[dict[str, Any]],
    epsilon: float,
) -> dict[str, Any]:
    if coarse_interval["death"] is None:
        return {
            "applicable": False,
            "reason": "essential intervals are not tested against the diagonal",
        }
    candidates: list[dict[str, Any]] = []
    nearest: dict[str, Any] | None = None
    nearest_distance = math.inf
    for row in fine_positive_bars:
        if row["death"] is None:
            continue
        distance = max(
            abs(float(coarse_interval["birth"]) - float(row["birth"])),
            abs(float(coarse_interval["death"]) - float(row["death"])),
        )
        candidate = {
            "fine_feature_id": int(row["feature_id"]),
            "birth": float(row["birth"]),
            "death": float(row["death"]),
            "lifetime": float(row["lifetime"]),
            "diagram_linf_distance": float(distance),
        }
        if distance < nearest_distance:
            nearest = candidate
            nearest_distance = distance
        if distance <= epsilon:
            candidates.append(candidate)
    return {
        "applicable": True,
        "candidate_count_within_epsilon": len(candidates),
        "candidates_within_epsilon": candidates,
        "nearest_fine_interval": nearest,
    }


def _finite_feature_stability_screen(
    lifetime: float,
    epsilon: float,
) -> dict[str, Any]:
    """Apply the strict bottleneck-to-diagonal screen."""

    if lifetime < 0.0 or epsilon < 0.0:
        raise ValueError("lifetime and epsilon must be non-negative")
    margin = float(lifetime - 2.0 * epsilon)
    return {
        "epsilon": float(epsilon),
        "twice_epsilon": float(2.0 * epsilon),
        "lifetime": float(lifetime),
        "lifetime_minus_twice_epsilon": margin,
        "strictly_exceeds_twice_epsilon": bool(margin > 0.0),
        "interpretation": (
            "forced_off_diagonal_counterpart_on_this_graph"
            if margin > 0.0
            else "diagonal_match_permitted_feature_unresolved"
        ),
    }


def _domain_comparison(
    name: str,
    graph: dict[str, Any],
    bundle: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    indices = graph["selected_common_indices"]
    rho = np.asarray(bundle["rho"])[indices]
    z = np.asarray(bundle["z"])[indices]
    source = np.asarray(bundle["source"])[indices]
    weights = np.asarray(bundle["weights"])[indices]
    fine_values = np.asarray(bundle["values"][label]["fine"])[indices]
    coarse_values = np.asarray(bundle["values"][label]["coarse"])[indices]
    epsilon_values = np.abs(fine_values - coarse_values)
    epsilon = float(np.max(epsilon_values))
    epsilon_node = int(np.argmax(epsilon_values))
    fine_persistence = _persistence_summary(
        fine_values,
        rho,
        z,
        graph["edges"],
        graph["crop_boundary"],
        source,
        weights,
    )
    coarse_persistence = _persistence_summary(
        coarse_values,
        rho,
        z,
        graph["edges"],
        graph["crop_boundary"],
        source,
        weights,
    )
    detached: list[dict[str, Any]] = []
    for component in coarse_persistence["components_below_threshold"]:
        if component["role"] != "detached_source_component":
            continue
        interval = component["persistence_interval"]
        if interval["death"] is None:
            detached.append(
                {
                    "component": component,
                    "stability_screen": {
                        "applicable": False,
                        "reason": (
                            "essential intervals cannot be matched to the "
                            "persistence diagonal"
                        ),
                    },
                }
            )
            continue
        lifetime = float(interval["lifetime"])
        screen = _finite_feature_stability_screen(lifetime, epsilon)
        screen["applicable"] = True
        screen["fine_diagram_candidates"] = _diagram_candidate_matches(
            interval,
            fine_persistence["positive_finite_bars"],
            epsilon,
        )
        detached.append(
            {
                "component": component,
                "stability_screen": screen,
            }
        )
    applicable = [
        row["stability_screen"]
        for row in detached
        if row["stability_screen"]["applicable"]
    ]
    return {
        "domain": name,
        "graph": {
            "vertex_count": int(indices.size),
            "edge_count": int(graph["edges"].shape[0]),
            "terminal_component_count": _graph_component_count(
                int(indices.size),
                graph["edges"],
            ),
            "crop_boundary_vertex_count": int(
                np.count_nonzero(graph["crop_boundary"])
            ),
            "vertex_coordinate_sha256": _sha256_json(
                np.column_stack((rho, z)).tolist()
            ),
            "edge_sha256": _sha256_json(graph["edges"].tolist()),
        },
        "common_sup_norm": {
            "epsilon": epsilon,
            "twice_epsilon": 2.0 * epsilon,
            "maximum_discrepancy_coordinate": {
                "rho": float(rho[epsilon_node]),
                "z": float(z[epsilon_node]),
            },
            "fine_value": float(fine_values[epsilon_node]),
            "coarse_value": float(coarse_values[epsilon_node]),
            "definition": (
                "unweighted max absolute fine/coarse matched pair-margin "
                "difference over every vertex in this exact common graph"
            ),
        },
        "fine_persistence": fine_persistence,
        "coarse_persistence": coarse_persistence,
        "detached_source_components": detached,
        "decision": {
            "finite_detached_component_count": len(applicable),
            "all_finite_detached_source_features_exceed_twice_epsilon": bool(
                applicable
                and all(
                    row["strictly_exceeds_twice_epsilon"]
                    for row in applicable
                )
            ),
            "all_finite_detached_source_features_unresolved": bool(
                applicable
                and all(
                    not row["strictly_exceeds_twice_epsilon"]
                    for row in applicable
                )
            ),
        },
    }


def _solve_transient_endpoints(
    system: Any,
    full_source: np.ndarray,
    stage6_field: np.ndarray,
    baseline_caps: dict[str, Any],
    configuration: AmgConfiguration,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]]]:
    fields = {"stage6": np.asarray(stage6_field, dtype=float).copy()}
    field = fields["stage6"].copy()
    rows: list[dict[str, Any]] = []
    for amplitude in VERIFICATION_AMPLITUDES:
        field, stage = e029.solve_cone_safe_stage(
            system,
            full_source,
            field,
            amplitude,
            configuration,
        )
        tail = e029.matched_tail_diagnostics(system, field, full_source)
        stage["diagnostic_role"] = "verified_unaccepted_e031_endpoint"
        stage["endpoint_tail"] = tail
        stage["frozen_tail_gate"] = e029.evaluate_tail_gate(
            tail,
            baseline_caps,
        )
        stage["native_grid_deficit_spectrum"] = (
            e030.margin_deficit_spectrum(
                system,
                stage6_field,
                field,
                full_source,
            )
        )
        stage["output_field_sha256"] = e029._sha256_array(field)
        label = f"{amplitude:.17g}"
        fields[label] = np.asarray(field, dtype=float).copy()
        rows.append(stage)
    return fields, rows


def run_campaign(
    *,
    accepted_stage6_checkpoint: str | Path = (
        e029.ACCEPTED_STAGE6_CHECKPOINT
    ),
    configuration: AmgConfiguration = AmgConfiguration(),
) -> dict[str, Any]:
    """Run the bounded, no-checkpoint E-031 diagnostic campaign."""

    configuration.validate()
    started = time.perf_counter()
    fine_system = e025.build_system(e028._canonical_grid())
    fine_source, fine_source_metadata = e025.smooth_annulus_source(
        fine_system
    )
    fine_stage6, _fine_linear, e028_report = (
        e029._validate_accepted_stage6(
            Path(accepted_stage6_checkpoint),
            fine_system,
            fine_source,
            configuration,
        )
    )
    fine_baseline_tail = e029.matched_tail_diagnostics(
        fine_system,
        fine_stage6,
        fine_source,
    )
    e029._verify_fine_reference_caps(fine_baseline_tail)
    fine_fields, fine_stages = _solve_transient_endpoints(
        fine_system,
        fine_source,
        fine_stage6,
        e029.FINE_STAGE6_REFERENCE_CAPS,
        configuration,
    )

    coarse_system, coarse_source, coarse_stage6, coarse_preparation = (
        e029._fresh_coarse_stage6(configuration)
    )
    coarse_baseline_tail = e029.matched_tail_diagnostics(
        coarse_system,
        coarse_stage6,
        coarse_source,
    )
    coarse_caps = e029.tail_caps_from_baseline(coarse_baseline_tail)
    coarse_fields, coarse_stages = _solve_transient_endpoints(
        coarse_system,
        coarse_source,
        coarse_stage6,
        coarse_caps,
        configuration,
    )

    bundle = _common_node_bundle(
        fine_system,
        coarse_system,
        fine_source,
        coarse_source,
        fine_fields,
        coarse_fields,
    )
    common_indices = np.arange(bundle["coarse_nodes"].size, dtype=int)
    support_indices = np.flatnonzero(
        (np.asarray(bundle["source"]) > 0.0)
        & (np.asarray(bundle["weights"]) > 0.0)
    )
    graphs = {
        "full_common_window": _build_induced_graph(
            coarse_system,
            bundle["coarse_nodes"],
            common_indices,
        ),
        "positive_source_support": _build_induced_graph(
            coarse_system,
            bundle["coarse_nodes"],
            support_indices,
        ),
    }

    comparisons: list[dict[str, Any]] = []
    common_spectra: list[dict[str, Any]] = []
    for amplitude in VERIFICATION_AMPLITUDES:
        label = f"{amplitude:.17g}"
        domains = {
            name: _domain_comparison(name, graph, bundle, label)
            for name, graph in graphs.items()
        }
        comparisons.append(
            {
                "amplitude": amplitude,
                "domains": domains,
            }
        )
        common_spectra.append(
            {
                "amplitude": amplitude,
                "common_deficit_spectra": common_deficit_spectra(
                    bundle["values"]["stage6"]["fine"],
                    bundle["values"][label]["fine"],
                    bundle["values"]["stage6"]["coarse"],
                    bundle["values"][label]["coarse"],
                    bundle["source"],
                    bundle["weights"],
                ),
            }
        )

    primary_decisions = [
        row["domains"]["full_common_window"]["decision"]
        for row in comparisons
    ]
    source_decisions = [
        row["domains"]["positive_source_support"]["decision"]
        for row in comparisons
    ]
    all_primary_unresolved = all(
        decision["all_finite_detached_source_features_unresolved"]
        for decision in primary_decisions
    )
    all_source_unresolved = all(
        decision["all_finite_detached_source_features_unresolved"]
        for decision in source_decisions
    )
    report = {
        "epistemic_status": (
            "common-graph numerical topology for a Hessian-derived diagnostic "
            "of a hypothetical PDE; not native-fine or continuum topology, "
            "a detected physical field, useful artificial gravity, inertial "
            "control, spacetime engineering, FTL, or propulsion"
        ),
        "focus_question": (
            "Does the detached E-030 coarse low-pair component have finite "
            "H0 lifetime greater than twice the exact common-graph fine/coarse "
            "sup discrepancy at 49/96 or 25/48?"
        ),
        "runtime_provenance": e026.runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "configuration": {
            "amg": e026.configuration_provenance(configuration),
            "accepted_baseline_amplitude": BASELINE_AMPLITUDE,
            "verification_amplitudes": list(VERIFICATION_AMPLITUDES),
        },
        "provenance": {
            "accepted_stage6_checkpoint": str(
                Path("models")
                / "checkpoints"
                / Path(accepted_stage6_checkpoint).name
            ),
            "accepted_stage6_checkpoint_sha256": (
                e029.ACCEPTED_STAGE6_CHECKPOINT_SHA256
            ),
            "accepted_stage6_field_sha256": (
                e029.ACCEPTED_STAGE6_FIELD_SHA256
            ),
            "e028_input_implementation_provenance": e028_report[
                "implementation_provenance"
            ],
        },
        "fine": {
            "grid": {
                "radial_max": fine_system.grid.radial_max,
                "spacing": fine_system.grid.spacing,
                "directional_radius": fine_system.grid.directional_radius,
                "unknowns": fine_system.size,
            },
            "source_metadata": fine_source_metadata,
            "stage6_field_sha256": e029._sha256_array(fine_stage6),
            "stage6_baseline_tail": fine_baseline_tail,
            "stages": fine_stages,
        },
        "coarse": {
            "grid": {
                "radial_max": coarse_system.grid.radial_max,
                "spacing": coarse_system.grid.spacing,
                "directional_radius": coarse_system.grid.directional_radius,
                "unknowns": coarse_system.size,
            },
            "preparation": coarse_preparation,
            "stage6_field_sha256": e029._sha256_array(coarse_stage6),
            "stage6_baseline_tail": coarse_baseline_tail,
            "stages": coarse_stages,
        },
        "common_mapping": {
            "common_node_count": int(bundle["coarse_nodes"].size),
            "positive_source_node_count": int(support_indices.size),
            "coarse_global_nodes_sha256": e029._sha256_array(
                bundle["coarse_nodes"]
            ),
            "fine_global_nodes_sha256": e029._sha256_array(
                bundle["fine_nodes"]
            ),
            "source_values_sha256": e029._sha256_array(bundle["source"]),
            "source_values_bitwise_identical": True,
        },
        "comparisons": comparisons,
        "common_deficit_spectra": common_spectra,
        "decision": {
            "diagnostic_completed": True,
            "accepted_amplitude": BASELINE_AMPLITUDE,
            "accepted_lineage_changed": False,
            "checkpoint_or_field_artifacts_written_by_campaign": False,
            "report_output_policy": (
                "run_campaign returns an in-memory report; the CLI writes "
                "JSON only when the caller supplies --report-json"
            ),
            "primary_full_window_all_detached_source_features_unresolved": (
                all_primary_unresolved
            ),
            "source_layer_sensitivity_all_detached_source_features_unresolved": (
                all_source_unresolved
            ),
            "status": (
                "detached_feature_unresolved_under_common_graph_discrepancy"
                if all_primary_unresolved and all_source_unresolved
                else "domain_or_feature_result_requires_manual_interpretation"
            ),
            "rule": (
                "p <= 2*epsilon permits a diagonal match and is unresolved; "
                "p > 2*epsilon forces some off-diagonal counterpart on the "
                "same restricted graph but does not prove spatial identity, "
                "native-fine topology, Hessian convergence, or continuum "
                "realization."
            ),
        },
        "limitations": [
            "The primary theorem applies only to piecewise-linear fields on the fixed common four-neighbour graph.",
            "Restricting the fine field to coarse nodes discards native-fine features between those nodes.",
            "Persistence stability guarantees an off-diagonal counterpart, not spatial identity of a lobe or stability of its bounding box.",
            "The positive-source mask is a conditional sensitivity whose artificial boundary can alter death levels or create essential classes.",
            "The common-node epsilon excludes separately unquantified floating-point and nonlinear-solver error; a near-zero positive p-2epsilon would not be rigorous.",
            "Potential convergence does not imply convergence of this Hessian-derived pair-margin field.",
            "No diagnostic endpoint is retained as an accepted or work checkpoint.",
            "No 13/24, 7/12, 8/12, outer-box, density, asymmetry, target, EFT, or engineering extension is authorized.",
        ],
        "resource_accounting": {
            "elapsed_seconds": time.perf_counter() - started,
            "peak_rss_bytes": e028.peak_rss_bytes(),
            "peak_rss_gib": e028.peak_rss_bytes() / 1024.0**3,
        },
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--accepted-stage6-checkpoint",
        type=Path,
        default=e029.ACCEPTED_STAGE6_CHECKPOINT,
    )
    parser.add_argument("--report-json", type=Path)
    parser.add_argument(
        "--preconditioner",
        choices=("pgsa",),
        default="pgsa",
    )
    args = parser.parse_args()
    report = run_campaign(
        accepted_stage6_checkpoint=args.accepted_stage6_checkpoint,
        configuration=AmgConfiguration(kind=args.preconditioner),
    )
    if args.report_json is not None:
        args.report_json.write_text(
            json.dumps(
                report,
                allow_nan=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    print(
        "E-031 "
        f"decision={report['decision']['status']} "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.2f}s"
    )


if __name__ == "__main__":
    main()
