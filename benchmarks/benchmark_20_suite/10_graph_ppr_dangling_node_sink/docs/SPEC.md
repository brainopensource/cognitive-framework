# Specification: Personalized PageRank Probability Conservation (GRA-10)

The `PersonalizedPageRank` computation MUST:
1. Conserve total probability mass: \sum_{v} p(v) = 1.0 \pm 10^{-4}.
2. When encountering dangling nodes (nodes with out-degree 0), redistribute their retained mass \alpha \cdot p(u) to the teleport distribution.
