# Combinatorial Multi-Node Tree (CMNT) for Joint CTU Partition Signaling
**Author:** Surafel Wolde  
**National ID / FAN:** 8047836790317269  
**Date:** October 26, 2026  
**Document Version:** 1.0 (Phase 1: Mathematical Formulation)  
**Target Submission:** IEEE Data Compression Conference (DCC) / Visual Communications and Image Processing (VCIP)

---

## 1. Introduction and Problem Statement

In next-generation video coding standards, including **Versatile Video Coding (VVC / H.266)** and the experimental **Enhanced Compression Model (ECM)**, the **Coding Tree Unit (CTU)** serves as the fundamental spatial container for intra- and inter-prediction. 

### 1.1 The VVC Quad-Tree plus Multi-Type Tree (QT-MTT) Bottleneck
VVC supports six distinct partition states for any coding unit $U$ of dimensions $W \times H$:
$$\mathcal{S} = \{ \text{NO\_SPLIT}, \text{QT}, \text{BTH}, \text{BTV}, \text{TTH}, \text{TTV} \}$$
where $\text{QT}$ is quad-tree, $\text{BTH}/\text{BTV}$ are binary tree horizontal/vertical, and $\text{TTH}/\text{TTV}$ are ternary tree horizontal/vertical ($1:2:1$ ratio).

In current VVC reference software (VTM), signaling $s \in \mathcal{S}$ requires evaluating a sequential chain of binary syntax bins:
1. $b_0 = \text{split\_cu\_flag} \in \{0, 1\}$
2. If $b_0 = 1$: $b_1 = \text{split\_qt\_flag} \in \{0, 1\}$
3. If $b_1 = 0$: $b_2 = \text{mtt\_split\_cu\_vertical\_flag} \in \{0, 1\}$
4. $b_3 = \text{mtt\_split\_cu\_binary\_flag} \in \{0, 1\}$

**The Technical Flaw:**
- **Serial Parsing Dependency:** In hardware decoders, $b_k$ cannot be parsed until $b_{k-1}$ is fully decoded via CABAC engine context updates. This introduces a $4$ to $5$ cycle pipeline stall per block.
- **Syntax Overhead:** In lossless or high-fidelity regimes, partition syntax accounts for $12\%$ to $22\%$ of total bitstream volume.

---

## 2. Mathematical Model of the Combinatorial Multi-Node Tree (CMNT)

Let the partition signaling engine be defined over an $M$-node alphabet:
$$\mathcal{N} = \{ n_1, n_2, \dots, n_M \}$$
where each node $n_i$ represents an elementary structural basis vector.

### 2.1 State Space Expansion with Self-Repeating Permutations
We define the code alphabet depth levels $L \in \{1, 2, \dots\}$.

#### Level 1 ($L = 1$, Single Node Activation):
$$\Omega_1 = \{ (n_i) \mid n_i \in \mathcal{N} \}, \quad |\Omega_1| = M$$
Each single activation $(n_i)$ carries the highest probability mass and is mapped to dominant partition modes.

#### Level 2 ($L = 2$, Joint Pair Activation with Self-Repeating):
$$\Omega_2 = \underbrace{\{ (n_i, n_i) \mid n_i \in \mathcal{N} \}}_{\text{Self-Repeating Transitions (Diagonal)}} \;\cup\; \underbrace{\{ (n_i, n_j) \mid n_i, n_j \in \mathcal{N}, i \ne j \}}_{\text{Cross-Node Combinations}}$$
The cardinality of Level 2 states is:
$$|\Omega_2| = M + \left( M(M - 1) \right) = M^2$$

#### Level $L$ (General $L$-Step Sequence):
For an arbitrary depth $L$, the total number of reachable distinct states is:
$$|\Omega_L| = M^L$$
The cumulative addressable state space up to depth $K$ is:
$$\Phi(M, K) = \sum_{L=1}^{K} M^L = \frac{M(M^K - 1)}{M - 1}$$

---

## 3. Probability-Ordered Partition Mapping

Let the empirical distribution of partition modes across training sequences be $P(s)$, ordered such that:
$$P(s_1) \ge P(s_2) \ge \dots \ge P(s_{|\mathcal{S}|})$$

### 3.1 Mapping Formulation for $M = 3$ Nodes
For $M = 3$ nodes ($\mathcal{N} = \{n_1, n_2, n_3\}$):
- **Level 1 ($L=1$, 1 symbol / 1 step):** $3$ states
- **Level 2 ($L=2$, 2 symbols / 2 steps):** $3^2 = 9$ states
- **Total accessible states at $K=2$:** $3 + 9 = 12$ states.

Since $|\mathcal{S}| = 6$ standard VVC modes plus $6$ common nested 2-level combinations:
$$\begin{aligned}
s_1 = \text{NO\_SPLIT} &\longrightarrow (n_1) \\
s_2 = \text{QT} &\longrightarrow (n_2) \\
s_3 = \text{BTH} &\longrightarrow (n_3) \\
s_4 = \text{BTV} &\longrightarrow (n_1, n_1) \quad \text{[Self-Repeat]} \\
s_5 = \text{TTH} &\longrightarrow (n_2, n_2) \quad \text{[Self-Repeat]} \\
s_6 = \text{TTV} &\longrightarrow (n_3, n_3) \quad \text{[Self-Repeat]} \\
s_7 = (\text{BTH} \to \text{BTH}) &\longrightarrow (n_1, n_2) \quad \text{[Cross-Pair]} \\
s_8 = (\text{BTH} \to \text{BTV}) &\longrightarrow (n_1, n_3) \quad \text{[Cross-Pair]} \\
s_9 = (\text{BTV} \to \text{BTV}) &\longrightarrow (n_2, n_1) \quad \text{[Cross-Pair]} \\
s_{10} = (\text{TTH} \to \text{BTH}) &\longrightarrow (n_2, n_3) \quad \text{[Cross-Pair]} \\
s_{11} = (\text{TTV} \to \text{BTV}) &\longrightarrow (n_3, n_1) \quad \text{[Cross-Pair]} \\
s_{12} = (\text{QT} \to \text{QT}) &\longrightarrow (n_3, n_2) \quad \text{[Cross-Pair]}
\end{aligned}$$

---

## 4. Theoretical Advantages

1. **Deterministic Single/Double Cycle Hardware Parsing:**
   - Dominant modes ($s_1, s_2, s_3$) are parsed in **$1$ lookup step**.
   - Compound 2-level nested modes are resolved in **$2$ lookup steps**, eliminating up to $10$ sequential binary CABAC flags across nested depths.

2. **Entropy Squeezing via Joint Modeling:**
   Let $H(\mathcal{S})$ be the marginal entropy of individual partition flags. By jointly coding the compound partition transitions through the node matrix $\Omega_2$, we exploit cross-level partition correlation:
   $$H(s_{\text{parent}}, s_{\text{child}}) \le H(s_{\text{parent}}) + H(s_{\text{child}})$$
   The mutual information $I(s_{\text{parent}}; s_{\text{child}}) > 0$ yields a net bitstream reduction.

---

## 5. Next Steps for Phase 2: Experimental Framework
1. Implement the C++ reference encoder/decoder for CMNT.
2. Benchmark against VVC VTM reference syntax on standard test blocks.
3. Quantify bit savings and parsing cycle reduction.
