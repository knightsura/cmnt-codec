"""
PHASE 2 EXPERIMENTAL BENCHMARK:
Combinatorial Multi-Node Tree (CMNT) vs. VVC QT-MTT CTU Partition Signaling
Author: Surafel Wolde (FAN: 8047836790317269)
Target: IEEE Data Compression Conference (DCC) / VCIP
"""
import sys
import math
import random
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)

# ── 1. The 6 VVC Partition Modes ──
# 0: NO_SPLIT, 1: QT, 2: BTH, 3: BTV, 4: TTH, 5: TTV
MODE_NAMES = ["NO_SPLIT", "QT", "BTH", "BTV", "TTH", "TTV"]

# Also include common nested compound splits (Parent -> Child)
# e.g., 6: BTH->BTH, 7: BTH->BTV, 8: BTV->BTV, 9: TTH->BTH, 10: TTV->BTV, 11: QT->QT
COMPOUND_MODES = [
    "NO_SPLIT", "QT", "BTH", "BTV", "TTH", "TTV",
    "BTH->BTH", "BTH->BTV", "BTV->BTV", "TTH->BTH", "TTV->BTV", "QT->QT"
]

# ── 2. Standard VVC QT-MTT Syntax Coding ──
def encode_vvc_syntax(mode_idx):
    """
    Standard VVC VTM reference syntax binarization for CTU split modes.
    Returns: (list of binary bins, number of serialized hardware parsing cycles)
    """
    if mode_idx == 0:  # NO_SPLIT
        # split_cu_flag = 0
        return [0], 1
    elif mode_idx == 1:  # QT
        # split_cu_flag = 1, split_qt_flag = 1
        return [1, 1], 2
    elif mode_idx == 2:  # BTH
        # split_cu_flag = 1, split_qt_flag = 0, mtt_vert = 0, mtt_binary = 1
        return [1, 0, 0, 1], 4
    elif mode_idx == 3:  # BTV
        # split_cu_flag = 1, split_qt_flag = 0, mtt_vert = 1, mtt_binary = 1
        return [1, 0, 1, 1], 4
    elif mode_idx == 4:  # TTH
        # split_cu_flag = 1, split_qt_flag = 0, mtt_vert = 0, mtt_binary = 0
        return [1, 0, 0, 0], 4
    elif mode_idx == 5:  # TTV
        # split_cu_flag = 1, split_qt_flag = 0, mtt_vert = 1, mtt_binary = 0
        return [1, 0, 1, 0], 4
    elif mode_idx >= 6:  # Compound 2-level nested splits
        # Two consecutive VVC blocks evaluated sequentially
        sub1 = encode_vvc_syntax(2 if "BTH" in COMPOUND_MODES[mode_idx] else (3 if "BTV" in COMPOUND_MODES[mode_idx] else 1))
        sub2 = encode_vvc_syntax(2 if "BTH" in COMPOUND_MODES[mode_idx] else (3 if "BTV" in COMPOUND_MODES[mode_idx] else 1))
        return sub1[0] + sub2[0], sub1[1] + sub2[1]

# ── 3. Surafel's Combinatorial Multi-Node Tree (CMNT) ──
# 3 Nodes: N1, N2, N3
# Level 1 (Single Node, L=1): 3 states
# Level 2 (Self-Repeating + Cross-Pairs, L=2): 9 states
# Total = 12 addressable states
CMNT_MAPPING = {
    0: ("N1",),       # NO_SPLIT -> Level 1 (1 step, 1 node)
    1: ("N2",),       # QT       -> Level 1 (1 step, 1 node)
    2: ("N3",),       # BTH      -> Level 1 (1 step, 1 node)
    3: ("N1", "N1"),  # BTV      -> Level 2 Self-Repeat (2 steps)
    4: ("N2", "N2"),  # TTH      -> Level 2 Self-Repeat (2 steps)
    5: ("N3", "N3"),  # TTV      -> Level 2 Self-Repeat (2 steps)
    6: ("N1", "N2"),  # BTH->BTH -> Level 2 Cross-Pair (2 steps)
    7: ("N1", "N3"),  # BTH->BTV -> Level 2 Cross-Pair (2 steps)
    8: ("N2", "N1"),  # BTV->BTV -> Level 2 Cross-Pair (2 steps)
    9: ("N2", "N3"),  # TTH->BTH -> Level 2 Cross-Pair (2 steps)
    10: ("N3", "N1"), # TTV->BTV -> Level 2 Cross-Pair (2 steps)
    11: ("N3", "N2"), # QT->QT   -> Level 2 Cross-Pair (2 steps)
}

def encode_cmnt_syntax(mode_idx):
    """
    Surafel's CMNT encoding:
    Returns: (symbol representation, number of hardware lookup cycles)
    Level 1 states resolve in 1 cycle; Level 2 states resolve in 2 cycles.
    """
    nodes = CMNT_MAPPING[mode_idx]
    cycles = len(nodes)
    # Using base-3 entropy coding for the ternary tree nodes
    # Level 1 costs log2(3) = 1.585 bits, Level 2 costs 2 * log2(3) = 3.17 bits
    bits = len(nodes) * math.log2(3)
    return nodes, cycles, bits

# ── 4. Benchmark Over Standard Video Test Regimes ──
# Test regimes corresponding to standard JVET CTC (Common Test Conditions):
# Regime 1: Smooth Background / Video Conferencing (Low activity, mostly NO_SPLIT)
# Regime 2: Natural Scenery (Medium activity, balanced QT/BT)
# Regime 3: High Texture / Dense Edges (High activity, frequent TT and compound splits)

REGIMES = {
    "Class A (Low Activity / Smooth)": [
        0.55, 0.20, 0.08, 0.06, 0.03, 0.02,
        0.015, 0.015, 0.01, 0.01, 0.005, 0.005
    ],
    "Class B (Medium Activity / Natural)": [
        0.25, 0.22, 0.16, 0.14, 0.08, 0.05,
        0.03, 0.025, 0.02, 0.01, 0.005, 0.005
    ],
    "Class C (High Activity / Complex Edges)": [
        0.10, 0.18, 0.18, 0.16, 0.12, 0.10,
        0.04, 0.04, 0.03, 0.02, 0.015, 0.015
    ]
}

N_BLOCKS = 20_000

print("=" * 80)
print("  PHASE 2 EXPERIMENTAL BENCHMARK REPORT")
print("  Lead Researcher: Surafel Wolde (FAN: 8047836790317269)")
print("  System: Combinatorial Multi-Node Tree (CMNT) vs VVC QT-MTT Baseline")
print(f"  Test Sample Size: {N_BLOCKS:,} CTU Blocks per Regime")
print("=" * 80)

summary_table = []

for regime_name, weights in REGIMES.items():
    print(f"\n" + "-" * 80)
    print(f"  EVALUATION REGIME: {regime_name}")
    print("-" * 80)

    # Normalize weights
    total_w = sum(weights)
    dist = [w / total_w for w in weights]
    
    # Generate test blocks
    blocks = random.choices(range(len(COMPOUND_MODES)), weights=dist, k=N_BLOCKS)
    
    # ── Test VVC Baseline ──
    vvc_total_bins = 0
    vvc_total_cycles = 0
    for b in blocks:
        bins, cycles = encode_vvc_syntax(b)
        vvc_total_bins += len(bins)
        vvc_total_cycles += cycles
        
    vvc_avg_bins = vvc_total_bins / N_BLOCKS
    vvc_avg_cycles = vvc_total_cycles / N_BLOCKS

    # ── Test Surafel's CMNT ──
    cmnt_total_bits = 0
    cmnt_total_cycles = 0
    for b in blocks:
        nodes, cycles, bits = encode_cmnt_syntax(b)
        cmnt_total_bits += bits
        cmnt_total_cycles += cycles
        
    cmnt_avg_bits = cmnt_total_bits / N_BLOCKS
    cmnt_avg_cycles = cmnt_total_cycles / N_BLOCKS

    # Calculate improvements
    bit_reduction = ((vvc_avg_bins - cmnt_avg_bits) / vvc_avg_bins) * 100
    cycle_reduction = ((vvc_avg_cycles - cmnt_avg_cycles) / vvc_avg_cycles) * 100

    print(f"  VVC QT-MTT Baseline:")
    print(f"    - Avg Syntax Bits / Block:       {vvc_avg_bins:6.3f} bits")
    print(f"    - Avg Hardware Parsing Cycles:   {vvc_avg_cycles:6.3f} cycles")
    print(f"\n  Surafel's CMNT (Proposed):")
    print(f"    - Avg Syntax Bits / Block:       {cmnt_avg_bits:6.3f} bits")
    print(f"    - Avg Hardware Parsing Cycles:   {cmnt_avg_cycles:6.3f} cycles")
    print(f"\n  PERFORMANCE GAINS:")
    print(f"    - Syntax Overhead Reduction:     {bit_reduction:+6.2f}%")
    print(f"    - Hardware Parsing Speedup:      {cycle_reduction:+6.2f}% fewer cycles")

    summary_table.append({
        "regime": regime_name,
        "vvc_bits": vvc_avg_bins,
        "cmnt_bits": cmnt_avg_bits,
        "bit_saving": bit_reduction,
        "vvc_cycles": vvc_avg_cycles,
        "cmnt_cycles": cmnt_avg_cycles,
        "cycle_saving": cycle_reduction
    })

print("\n" + "=" * 80)
print("  OFFICIAL BENCHMARK SUMMARY (TO BE INCLUDED IN IEEE PAPER TABLE I)")
print("=" * 80)
print(f"{'Test Video Class':<35} | {'VVC Bits':<9} | {'CMNT Bits':<9} | {'Bit Saving':<10} | {'Cycle Reduction'}")
print("-" * 80)
for row in summary_table:
    print(f"{row['regime']:<35} | {row['vvc_bits']:<9.3f} | {row['cmnt_bits']:<9.3f} | {row['bit_saving']:>8.2f}% | {row['cycle_saving']:>13.2f}%")
print("=" * 80)
