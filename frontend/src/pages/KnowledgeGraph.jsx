import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  AlertCircle,
  CircleDot,
  GitBranch,
  Minus,
  Network,
  Plus,
  RefreshCw,
  RotateCcw,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  getKnowledgeGraph,
  getKnowledgeGraphConcept,
} from "@/services/knowledgeGraphApi";

const VIEWBOX_WIDTH = 1200;
const VIEWBOX_HEIGHT = 720;

const NODE_RADIUS = 30;

const MIN_ZOOM = 0.45;
const MAX_ZOOM = 2.5;
const ZOOM_STEP = 0.15;

/* -------------------------------------------------------------------------- */
/* Helpers                                                                    */
/* -------------------------------------------------------------------------- */

function getNodeName(node) {
  return (
    node?.name ||
    node?.label ||
    node?.id ||
    "Unknown concept"
  );
}

function getNodeType(node) {
  return node?.type || "concept";
}

function getRelationshipLabel(edge) {
  return (
    edge?.relationship ||
    edge?.label ||
    "related_to"
  );
}

function truncate(text, maxLength = 24) {
  const value = String(text || "");

  if (value.length <= maxLength) {
    return value;
  }

  return `${value.slice(0, maxLength - 1)}…`;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function hashString(value) {
  let hash = 0;

  for (let index = 0; index < value.length; index += 1) {
    hash =
      (hash << 5) -
      hash +
      value.charCodeAt(index);

    hash |= 0;
  }

  return Math.abs(hash);
}

/* -------------------------------------------------------------------------- */
/* Force-directed graph layout                                                */
/* -------------------------------------------------------------------------- */

function buildForceLayout(nodes, edges) {
  if (!nodes.length) {
    return {};
  }

  const centerX = VIEWBOX_WIDTH / 2;
  const centerY = VIEWBOX_HEIGHT / 2;

  const positions = {};
  const velocities = {};

  /*
   * Start nodes in a deterministic spiral instead of random positions.
   * This keeps the graph visually stable between refreshes.
   */
  nodes.forEach((node, index) => {
    const hash = hashString(String(node.id));

    const angle =
      (index / Math.max(nodes.length, 1)) *
        Math.PI *
        2 +
      (hash % 360) * (Math.PI / 180);

    const radius =
      120 +
      (index % 4) * 65;

    positions[node.id] = {
      x:
        centerX +
        Math.cos(angle) * radius,
      y:
        centerY +
        Math.sin(angle) * radius,
    };

    velocities[node.id] = {
      x: 0,
      y: 0,
    };
  });

  const nodeIds = nodes.map((node) =>
    String(node.id)
  );

  const nodeSet = new Set(nodeIds);

  const cleanEdges = edges.filter(
    (edge) =>
      nodeSet.has(String(edge.source_id)) &&
      nodeSet.has(String(edge.target_id))
  );

  /*
   * Build an undirected adjacency set for the layout.
   * The actual displayed arrows remain directional.
   */
  const adjacency = new Map();

  nodeIds.forEach((id) => {
    adjacency.set(id, new Set());
  });

  cleanEdges.forEach((edge) => {
    const source = String(edge.source_id);
    const target = String(edge.target_id);

    if (source === target) {
      return;
    }

    adjacency.get(source)?.add(target);
    adjacency.get(target)?.add(source);
  });

  const iterations = Math.min(
    180,
    90 + nodes.length * 3
  );

  const idealDistance =
    nodes.length > 35 ? 125 : 145;

  for (
    let iteration = 0;
    iteration < iterations;
    iteration += 1
  ) {
    const temperature =
      1 -
      iteration / iterations;

    /*
     * Repulsion.
     */
    for (
      let i = 0;
      i < nodeIds.length;
      i += 1
    ) {
      for (
        let j = i + 1;
        j < nodeIds.length;
        j += 1
      ) {
        const sourceId = nodeIds[i];
        const targetId = nodeIds[j];

        const source = positions[sourceId];
        const target = positions[targetId];

        let dx = target.x - source.x;
        let dy = target.y - source.y;

        let distance = Math.sqrt(
          dx * dx + dy * dy
        );

        if (distance < 0.01) {
          dx = 1;
          dy = 0;
          distance = 1;
        }

        const minimumDistance = 65;

        const strength =
          distance < minimumDistance
            ? 10000 / (distance * distance)
            : 3500 / (distance * distance);

        const forceX =
          (dx / distance) * strength;
        const forceY =
          (dy / distance) * strength;

        velocities[sourceId].x -= forceX;
        velocities[sourceId].y -= forceY;

        velocities[targetId].x += forceX;
        velocities[targetId].y += forceY;
      }
    }

    /*
     * Attraction along relationships.
     */
    cleanEdges.forEach((edge) => {
      const sourceId = String(
        edge.source_id
      );

      const targetId = String(
        edge.target_id
      );

      if (sourceId === targetId) {
        return;
      }

      const source = positions[sourceId];
      const target = positions[targetId];

      let dx = target.x - source.x;
      let dy = target.y - source.y;

      let distance = Math.sqrt(
        dx * dx + dy * dy
      );

      if (distance < 0.01) {
        dx = 1;
        dy = 0;
        distance = 1;
      }

      const displacement =
        distance - idealDistance;

      const strength =
        displacement * 0.003;

      const forceX =
        (dx / distance) * strength;

      const forceY =
        (dy / distance) * strength;

      velocities[sourceId].x += forceX;
      velocities[sourceId].y += forceY;

      velocities[targetId].x -= forceX;
      velocities[targetId].y -= forceY;
    });

    /*
     * Gentle center gravity prevents disconnected nodes
     * from escaping the graph.
     */
    nodeIds.forEach((id) => {
      const position = positions[id];

      const dx =
        centerX - position.x;

      const dy =
        centerY - position.y;

      velocities[id].x += dx * 0.0007;
      velocities[id].y += dy * 0.0007;
    });

    /*
     * Apply velocity with damping.
     */
    nodeIds.forEach((id) => {
      const position = positions[id];
      const velocity = velocities[id];

      const damping =
        0.78 +
        temperature * 0.08;

      velocity.x *= damping;
      velocity.y *= damping;

      const maxMovement =
        10 * (0.35 + temperature);

      const movement =
        Math.sqrt(
          velocity.x * velocity.x +
            velocity.y * velocity.y
        );

      if (movement > maxMovement) {
        velocity.x =
          (velocity.x / movement) *
          maxMovement;

        velocity.y =
          (velocity.y / movement) *
          maxMovement;
      }

      position.x += velocity.x;
      position.y += velocity.y;

      /*
       * Keep nodes inside the visible graph.
       */
      const padding = 65;

      position.x = clamp(
        position.x,
        padding,
        VIEWBOX_WIDTH - padding
      );

      position.y = clamp(
        position.y,
        padding,
        VIEWBOX_HEIGHT - padding
      );
    });
  }

  /*
   * Small final collision pass.
   */
  for (
    let pass = 0;
    pass < 8;
    pass += 1
  ) {
    for (
      let i = 0;
      i < nodeIds.length;
      i += 1
    ) {
      for (
        let j = i + 1;
        j < nodeIds.length;
        j += 1
      ) {
        const sourceId = nodeIds[i];
        const targetId = nodeIds[j];

        const source = positions[sourceId];
        const target = positions[targetId];

        let dx = target.x - source.x;
        let dy = target.y - source.y;

        let distance = Math.sqrt(
          dx * dx + dy * dy
        );

        if (distance < 0.01) {
          dx = 1;
          dy = 0;
          distance = 1;
        }

        const minimumDistance = 72;

        if (distance < minimumDistance) {
          const correction =
            (minimumDistance -
              distance) /
            2;

          const nx = dx / distance;
          const ny = dy / distance;

          source.x -= nx * correction;
          source.y -= ny * correction;

          target.x += nx * correction;
          target.y += ny * correction;
        }
      }
    }
  }

  return positions;
}

/* -------------------------------------------------------------------------- */
/* SVG edge geometry                                                          */
/* -------------------------------------------------------------------------- */

function getEdgeGeometry(source, target) {
  const dx = target.x - source.x;
  const dy = target.y - source.y;

  const distance = Math.sqrt(
    dx * dx + dy * dy
  );

  if (distance < 0.01) {
    return {
      x1: source.x,
      y1: source.y,
      x2: target.x,
      y2: target.y,
      labelX: source.x,
      labelY: source.y,
    };
  }

  const unitX = dx / distance;
  const unitY = dy / distance;

  const x1 =
    source.x + unitX * NODE_RADIUS;

  const y1 =
    source.y + unitY * NODE_RADIUS;

  const x2 =
    target.x - unitX * NODE_RADIUS;

  const y2 =
    target.y - unitY * NODE_RADIUS;

  return {
    x1,
    y1,
    x2,
    y2,
    labelX: (x1 + x2) / 2,
    labelY: (y1 + y2) / 2,
  };
}

/* -------------------------------------------------------------------------- */
/* Stat card                                                                  */
/* -------------------------------------------------------------------------- */

function StatCard({
  icon: Icon,
  label,
  value,
}) {
  return (
    <Card className="border-border bg-card/40 shadow-none">
      <CardContent className="flex items-center gap-3 p-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-border bg-muted/40">
          <Icon className="h-4 w-4 text-primary" />
        </div>

        <div className="min-w-0">
          <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
            {label}
          </p>

          <p className="mt-0.5 text-lg font-semibold tracking-tight text-foreground">
            {value}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

/* -------------------------------------------------------------------------- */
/* Empty graph                                                                */
/* -------------------------------------------------------------------------- */

function EmptyGraph() {
  return (
    <div className="flex h-full min-h-[420px] flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-card/20 px-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-border bg-muted/40">
        <Network className="h-6 w-6 text-primary" />
      </div>

      <h2 className="mt-5 text-lg font-semibold tracking-tight text-foreground">
        No knowledge graph data yet
      </h2>

      <p className="mt-2 max-w-md text-[13.5px] leading-relaxed text-muted-foreground">
        Upload and process documents to populate
        MemoryOS with concepts and relationships.
      </p>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Main page                                                                  */
/* -------------------------------------------------------------------------- */

export default function KnowledgeGraph() {
  const [graph, setGraph] = useState({
    nodes: [],
    edges: [],
    nodeCount: 0,
    edgeCount: 0,
  });

  const [selectedConcept, setSelectedConcept] =
    useState(null);

  const [status, setStatus] =
    useState("loading");

  const [error, setError] =
    useState(null);

  const [zoom, setZoom] =
    useState(1);

  const [pan, setPan] = useState({
    x: 0,
    y: 0,
  });

  const [isDragging, setIsDragging] =
    useState(false);

  const dragRef = useRef(null);

  /* ---------------------------------------------------------------------- */
  /* Load graph                                                             */
  /* ---------------------------------------------------------------------- */

  const loadGraph = useCallback(async () => {
    setStatus("loading");
    setError(null);

    try {
      const data =
        await getKnowledgeGraph();

      setGraph(data);
      setSelectedConcept(null);
      setZoom(1);
      setPan({
        x: 0,
        y: 0,
      });

      setStatus(
        data.nodes.length > 0
          ? "ready"
          : "empty"
      );
    } catch (err) {
      setError(
        err?.message ||
          "Failed to load the knowledge graph."
      );

      setStatus("error");
    }
  }, []);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  /* ---------------------------------------------------------------------- */
  /* Calculate graph positions                                              */
  /* ---------------------------------------------------------------------- */

  const positions = useMemo(
    () =>
      buildForceLayout(
        graph.nodes,
        graph.edges
      ),
    [graph.nodes, graph.edges]
  );

  /* ---------------------------------------------------------------------- */
  /* Node map                                                               */
  /* ---------------------------------------------------------------------- */

  const nodeMap = useMemo(() => {
    const map = new Map();

    graph.nodes.forEach((node) => {
      map.set(String(node.id), node);
    });

    return map;
  }, [graph.nodes]);

  /* ---------------------------------------------------------------------- */
  /* Selected concept                                                        */
  /* ---------------------------------------------------------------------- */

  const selectedNodeId =
    selectedConcept?.id;

  const selectedRelationships =
    Array.isArray(
      selectedConcept?.relationships
    )
      ? selectedConcept.relationships
      : [];

  /* ---------------------------------------------------------------------- */
  /* Connected node detection                                               */
  /* ---------------------------------------------------------------------- */

  const connectedNodeIds = useMemo(() => {
    const connected = new Set();

    if (!selectedNodeId) {
      return connected;
    }

    graph.edges.forEach((edge) => {
      const source = String(
        edge.source_id
      );

      const target = String(
        edge.target_id
      );

      if (
        source === String(selectedNodeId)
      ) {
        connected.add(target);
      }

      if (
        target === String(selectedNodeId)
      ) {
        connected.add(source);
      }
    });

    return connected;
  }, [
    graph.edges,
    selectedNodeId,
  ]);

  /* ---------------------------------------------------------------------- */
  /* Select concept                                                         */
  /* ---------------------------------------------------------------------- */

  const handleNodeClick = async (
    node
  ) => {
    setSelectedConcept({
      ...node,
      loading: true,
    });

    try {
      const concept =
        await getKnowledgeGraphConcept(
          node.id
        );

      setSelectedConcept(
        concept
          ? {
              ...concept,
              loading: false,
            }
          : {
              ...node,
              loading: false,
            }
      );
    } catch {
      setSelectedConcept({
        ...node,
        loading: false,
      });
    }
  };

  /* ---------------------------------------------------------------------- */
  /* Zoom                                                                   */
  /* ---------------------------------------------------------------------- */

  const changeZoom = (amount) => {
    setZoom((current) =>
      clamp(
        Number(
          (current + amount).toFixed(2)
        ),
        MIN_ZOOM,
        MAX_ZOOM
      )
    );
  };

  const resetView = () => {
    setZoom(1);
    setPan({
      x: 0,
      y: 0,
    });
  };

  /* ---------------------------------------------------------------------- */
  /* Mouse panning                                                          */
  /* ---------------------------------------------------------------------- */

  const handlePointerDown = (event) => {
    /*
     * Only pan when clicking the empty SVG background.
     * Node clicks are handled separately.
     */
    if (
      event.target.tagName !== "svg" &&
      event.target.dataset?.graphBackground !==
        "true"
    ) {
      return;
    }

    setIsDragging(true);

    dragRef.current = {
      startX: event.clientX,
      startY: event.clientY,
      originalX: pan.x,
      originalY: pan.y,
    };
  };

  const handlePointerMove = (event) => {
    if (
      !isDragging ||
      !dragRef.current
    ) {
      return;
    }

    const deltaX =
      event.clientX -
      dragRef.current.startX;

    const deltaY =
      event.clientY -
      dragRef.current.startY;

    setPan({
      x:
        dragRef.current.originalX +
        deltaX / zoom,
      y:
        dragRef.current.originalY +
        deltaY / zoom,
    });
  };

  const handlePointerUp = () => {
    setIsDragging(false);
    dragRef.current = null;
  };

  /* ---------------------------------------------------------------------- */
  /* Mouse wheel zoom                                                       */
  /* ---------------------------------------------------------------------- */

  const handleWheel = (event) => {
    event.preventDefault();

    const direction =
      event.deltaY > 0 ? -1 : 1;

    changeZoom(
      direction * ZOOM_STEP
    );
  };

  /* ---------------------------------------------------------------------- */
  /* Render                                                                 */
  /* ---------------------------------------------------------------------- */

  return (
    <div className="mx-auto w-full max-w-7xl px-5 py-8 sm:px-8 sm:py-10">
      {/* Page header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-muted/40">
              <Network className="h-4.5 w-4.5 text-primary" />
            </div>

            <div>
              <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
                Knowledge Graph
              </h1>

              <p className="mt-1 text-[14px] text-muted-foreground">
                Explore concepts and relationships
                extracted from your knowledge base.
              </p>
            </div>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={loadGraph}
          disabled={status === "loading"}
          className="gap-1.5 border-border"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${
              status === "loading"
                ? "animate-spin"
                : ""
            }`}
          />

          Refresh
        </Button>
      </div>

      {/* Statistics */}
      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <StatCard
          icon={CircleDot}
          label="Concepts"
          value={graph.nodeCount}
        />

        <StatCard
          icon={GitBranch}
          label="Relationships"
          value={graph.edgeCount}
        />

        <StatCard
          icon={Sparkles}
          label="Graph status"
          value={
            status === "loading"
              ? "Loading"
              : status === "error"
                ? "Unavailable"
                : status === "empty"
                  ? "Empty"
                  : "Ready"
          }
        />
      </div>

      {/* Error */}
      {status === "error" && (
        <div className="mt-6 flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/5 px-6 py-14 text-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/10">
            <AlertCircle className="h-5 w-5 text-destructive" />
          </div>

          <p className="mt-4 text-[14px] font-medium text-foreground">
            {error}
          </p>

          <Button
            variant="outline"
            size="sm"
            className="mt-4 gap-1.5 border-border"
            onClick={loadGraph}
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Try again
          </Button>
        </div>
      )}

      {/* Empty */}
      {status === "empty" && (
        <div className="mt-6">
          <EmptyGraph />
        </div>
      )}

      {/* Graph */}
      {status === "ready" && (
        <div className="mt-6 grid min-w-0 gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
          {/* Graph card */}
          <Card className="min-w-0 overflow-hidden border-border bg-card/30 shadow-none">
            <CardHeader className="border-b border-border px-5 py-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle className="text-[14px] font-semibold">
                    Concept relationships
                  </CardTitle>

                  <p className="mt-1 text-[12px] text-muted-foreground">
                    Select a concept to inspect its
                    details.
                  </p>
                </div>

                <div className="flex items-center gap-1.5">
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 border-border"
                    onClick={() =>
                      changeZoom(
                        -ZOOM_STEP
                      )
                    }
                    title="Zoom out"
                  >
                    <Minus className="h-3.5 w-3.5" />
                  </Button>

                  <div className="min-w-[52px] text-center text-[11px] font-medium text-muted-foreground">
                    {Math.round(
                      zoom * 100
                    )}
                    %
                  </div>

                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 border-border"
                    onClick={() =>
                      changeZoom(
                        ZOOM_STEP
                      )
                    }
                    title="Zoom in"
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </Button>

                  <Button
                    variant="outline"
                    size="icon"
                    className="ml-1 h-8 w-8 border-border"
                    onClick={resetView}
                    title="Reset graph view"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <div
                className={`h-[560px] w-full overflow-hidden bg-background/20 ${
                  isDragging
                    ? "cursor-grabbing"
                    : "cursor-grab"
                }`}
              >
                <svg
                  viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
                  className="h-full w-full select-none"
                  role="img"
                  aria-label="MemoryOS knowledge graph"
                  onPointerDown={
                    handlePointerDown
                  }
                  onPointerMove={
                    handlePointerMove
                  }
                  onPointerUp={
                    handlePointerUp
                  }
                  onPointerCancel={
                    handlePointerUp
                  }
                  onWheel={
                    handleWheel
                  }
                >
                  <defs>
                    {/* Arrow */}
                    <marker
                      id="knowledgeGraphArrow"
                      markerWidth="8"
                      markerHeight="8"
                      refX="7"
                      refY="3"
                      orient="auto"
                      markerUnits="strokeWidth"
                    >
                      <path
                        d="M0,0 L0,6 L7,3 z"
                        className="fill-primary/60"
                      />
                    </marker>

                    {/* Selected glow */}
                    <filter
                      id="knowledgeGraphGlow"
                      x="-100%"
                      y="-100%"
                      width="300%"
                      height="300%"
                    >
                      <feGaussianBlur
                        stdDeviation="6"
                        result="blur"
                      />

                      <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>

                  {/* Background */}
                  <rect
                    x="0"
                    y="0"
                    width={VIEWBOX_WIDTH}
                    height={VIEWBOX_HEIGHT}
                    fill="transparent"
                    data-graph-background="true"
                  />

                  {/* Graph viewport */}
                  <g
                    transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}
                  >
                    {/* Relationship edges */}
                    <g>
                      {graph.edges.map(
                        (edge, index) => {
                          const source =
                            positions[
                              edge.source_id
                            ];

                          const target =
                            positions[
                              edge.target_id
                            ];

                          if (
                            !source ||
                            !target
                          ) {
                            return null;
                          }

                          const isConnected =
                            selectedNodeId &&
                            (
                              String(
                                edge.source_id
                              ) ===
                                String(
                                  selectedNodeId
                                ) ||
                              String(
                                edge.target_id
                              ) ===
                                String(
                                  selectedNodeId
                                )
                            );

                          const hasSelection =
                            Boolean(
                              selectedNodeId
                            );

                          const opacity =
                            hasSelection
                              ? isConnected
                                ? 0.9
                                : 0.08
                              : 0.42;

                          const geometry =
                            getEdgeGeometry(
                              source,
                              target
                            );

                          return (
                            <g
                              key={`${edge.source_id}-${edge.target_id}-${edge.edge_key ?? index}`}
                            >
                              <line
                                x1={
                                  geometry.x1
                                }
                                y1={
                                  geometry.y1
                                }
                                x2={
                                  geometry.x2
                                }
                                y2={
                                  geometry.y2
                                }
                                className="stroke-primary/60"
                                strokeWidth={
                                  isConnected
                                    ? 2.4
                                    : 1.4
                                }
                                strokeOpacity={
                                  opacity
                                }
                                markerEnd="url(#knowledgeGraphArrow)"
                              />

                              {(!hasSelection ||
                                isConnected) && (
                                <text
                                  x={
                                    geometry.labelX
                                  }
                                  y={
                                    geometry.labelY -
                                    7
                                  }
                                  textAnchor="middle"
                                  className="pointer-events-none fill-muted-foreground text-[10px]"
                                  opacity={
                                    opacity
                                  }
                                >
                                  {truncate(
                                    getRelationshipLabel(
                                      edge
                                    ),
                                    22
                                  )}
                                </text>
                              )}
                            </g>
                          );
                        }
                      )}
                    </g>

                    {/* Nodes */}
                    <g>
                      {graph.nodes.map(
                        (node) => {
                          const position =
                            positions[
                              node.id
                            ];

                          if (
                            !position
                          ) {
                            return null;
                          }

                          const isSelected =
                            String(
                              node.id
                            ) ===
                            String(
                              selectedNodeId
                            );

                          const isConnected =
                            connectedNodeIds.has(
                              String(
                                node.id
                              )
                            );

                          const dimmed =
                            Boolean(
                              selectedNodeId
                            ) &&
                            !isSelected &&
                            !isConnected;

                          return (
                            <g
                              key={node.id}
                              transform={`translate(${position.x}, ${position.y})`}
                              className="cursor-pointer"
                              onClick={(event) => {
                                event.stopPropagation();

                                handleNodeClick(
                                  node
                                );
                              }}
                              role="button"
                              tabIndex={0}
                              onKeyDown={(
                                event
                              ) => {
                                if (
                                  event.key ===
                                    "Enter" ||
                                  event.key ===
                                    " "
                                ) {
                                  event.preventDefault();

                                  handleNodeClick(
                                    node
                                  );
                                }
                              }}
                              opacity={
                                dimmed
                                  ? 0.2
                                  : 1
                              }
                            >
                              {/* Selection ring */}
                              {isSelected && (
                                <circle
                                  r="40"
                                  className="fill-primary/10 stroke-primary/40"
                                  strokeWidth="2"
                                  filter="url(#knowledgeGraphGlow)"
                                />
                              )}

                              {/* Connection ring */}
                              {isConnected &&
                                !isSelected && (
                                  <circle
                                    r="36"
                                    className="fill-primary/5 stroke-primary/20"
                                    strokeWidth="1.5"
                                  />
                                )}

                              {/* Main node */}
                              <circle
                                r={
                                  isSelected
                                    ? 32
                                    : 29
                                }
                                className={
                                  isSelected
                                    ? "fill-primary stroke-primary"
                                    : "fill-card stroke-border"
                                }
                                strokeWidth={
                                  isSelected
                                    ? 2.5
                                    : 1.5
                                }
                              />

                              {/* Inner node */}
                              <circle
                                r={
                                  isSelected
                                    ? 24
                                    : 21
                                }
                                className={
                                  isSelected
                                    ? "fill-primary/80"
                                    : "fill-muted/40"
                                }
                              />

                              {/* Small center icon */}
                              <circle
                                r="4"
                                className={
                                  isSelected
                                    ? "fill-primary-foreground/90"
                                    : "fill-primary/80"
                                }
                              />

                              {/* Node label */}
                              <rect
                                x="-72"
                                y="40"
                                width="144"
                                height="23"
                                rx="7"
                                className="fill-background/80"
                              />

                              <text
                                x="0"
                                y="55"
                                textAnchor="middle"
                                className={
                                  isSelected
                                    ? "fill-foreground text-[11px] font-semibold"
                                    : "fill-foreground text-[10.5px] font-medium"
                                }
                              >
                                {truncate(
                                  getNodeName(
                                    node
                                  ),
                                  24
                                )}
                              </text>

                              {/* Type */}
                              <text
                                x="0"
                                y="72"
                                textAnchor="middle"
                                className="fill-muted-foreground text-[9px]"
                              >
                                {truncate(
                                  getNodeType(
                                    node
                                  ),
                                  18
                                )}
                              </text>
                            </g>
                          );
                        }
                      )}
                    </g>
                  </g>
                </svg>
              </div>

              {/* Graph footer */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border px-5 py-3">
                <div className="flex items-center gap-4 text-[11px] text-muted-foreground">
                  <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-primary" />
                    Concept
                  </span>

                  <span className="flex items-center gap-1.5">
                    <span className="h-px w-5 bg-primary/50" />
                    Relationship
                  </span>
                </div>

                <p className="text-[11px] text-muted-foreground">
                  Scroll to zoom · Drag to move
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Concept details */}
          <Card className="border-border bg-card/30 shadow-none">
            <CardHeader className="border-b border-border px-5 py-4">
              <CardTitle className="text-[14px] font-semibold">
                Concept details
              </CardTitle>
            </CardHeader>

            <CardContent className="p-5">
              {!selectedConcept && (
                <div className="flex min-h-[360px] flex-col items-center justify-center text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-muted/40">
                    <CircleDot className="h-5 w-5 text-primary" />
                  </div>

                  <p className="mt-4 text-[13.5px] font-medium text-foreground">
                    Select a concept
                  </p>

                  <p className="mt-1 max-w-[230px] text-[12.5px] leading-relaxed text-muted-foreground">
                    Click any node in the graph to
                    view its backend details and
                    relationships.
                  </p>
                </div>
              )}

              {selectedConcept && (
                <div className="space-y-5">
                  {/* Concept title */}
                  <div>
                    <div className="flex items-start gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-primary/20 bg-primary/10">
                        <CircleDot className="h-4 w-4 text-primary" />
                      </div>

                      <div className="min-w-0">
                        <h3 className="break-words text-[15px] font-semibold text-foreground">
                          {getNodeName(
                            selectedConcept
                          )}
                        </h3>

                        <p className="mt-1 break-all text-[11px] text-muted-foreground">
                          {selectedConcept.id}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Type */}
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                      Type
                    </p>

                    <div className="mt-2 inline-flex rounded-lg border border-border bg-muted/40 px-2.5 py-1.5 text-[12px] font-medium text-foreground">
                      {getNodeType(
                        selectedConcept
                      )}
                    </div>
                  </div>

                  {/* Description */}
                  {selectedConcept.description && (
                    <div>
                      <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                        Description
                      </p>

                      <p className="mt-2 text-[13px] leading-relaxed text-muted-foreground">
                        {
                          selectedConcept.description
                        }
                      </p>
                    </div>
                  )}

                  {/* Relationships */}
                  <div>
                    <div className="flex items-center justify-between">
                      <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                        Relationships
                      </p>

                      <span className="rounded-md bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                        {
                          selectedRelationships.length
                        }
                      </span>
                    </div>

                    {selectedConcept.loading ? (
                      <div className="mt-3 flex items-center gap-2 text-[12px] text-muted-foreground">
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        Loading concept details...
                      </div>
                    ) : selectedRelationships.length ===
                      0 ? (
                      <p className="mt-3 text-[12.5px] text-muted-foreground">
                        No outgoing relationships
                        found.
                      </p>
                    ) : (
                      <div className="mt-3 space-y-2">
                        {selectedRelationships.map(
                          (
                            relationship,
                            index
                          ) => {
                            const target =
                              nodeMap.get(
                                String(
                                  relationship.target_id
                                )
                              );

                            return (
                              <div
                                key={`${relationship.target_id}-${index}`}
                                className="rounded-xl border border-border bg-card/40 p-3"
                              >
                                <div className="flex items-center justify-between gap-3">
                                  <span className="min-w-0 truncate text-[12.5px] font-medium text-foreground">
                                    {target
                                      ? getNodeName(
                                          target
                                        )
                                      : relationship.target_id}
                                  </span>

                                  <GitBranch className="h-3.5 w-3.5 shrink-0 text-primary" />
                                </div>

                                <p className="mt-1 text-[11px] text-muted-foreground">
                                  {getRelationshipLabel(
                                    relationship
                                  )}
                                </p>

                                {typeof relationship.confidence ===
                                  "number" && (
                                  <p className="mt-1 text-[10.5px] text-muted-foreground/70">
                                    Confidence:{" "}
                                    {Math.round(
                                      relationship.confidence *
                                        100
                                    )}
                                    %
                                  </p>
                                )}
                              </div>
                            );
                          }
                        )}
                      </div>
                    )}
                  </div>

                  {/* Provenance */}
                  {Array.isArray(
                    selectedConcept.provenance
                  ) &&
                    selectedConcept.provenance
                      .length > 0 && (
                      <div>
                        <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                          Sources
                        </p>

                        <div className="mt-2 space-y-2">
                          {selectedConcept.provenance
                            .slice(0, 5)
                            .map(
                              (
                                source,
                                index
                              ) => (
                                <div
                                  key={index}
                                  className="rounded-lg border border-border bg-muted/20 px-3 py-2 text-[11px] text-muted-foreground"
                                >
                                  <div>
                                    Document:{" "}
                                    {source?.document_id ||
                                      "Unknown"}
                                  </div>

                                  {source?.page_number && (
                                    <div className="mt-0.5">
                                      Page:{" "}
                                      {
                                        source.page_number
                                      }
                                    </div>
                                  )}
                                </div>
                              )
                            )}
                        </div>
                      </div>
                    )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}