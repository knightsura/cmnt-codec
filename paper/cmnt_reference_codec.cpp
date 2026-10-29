/**
 * Reference C++ Implementation:
 * Combinatorial Multi-Node Tree (CMNT) for Joint CTU Partition Signaling
 * 
 * Author: Surafel Wolde (FAN: 8047836790317269)
 * Target: IEEE Data Compression Conference (DCC) / VCIP
 */

#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <cstdint>

enum PartitionMode {
    NO_SPLIT = 0,
    QT       = 1,
    BTH      = 2,
    BTV      = 3,
    TTH      = 4,
    TTV      = 5,
    BTH_BTH  = 6,
    BTH_BTV  = 7,
    BTV_BTV  = 8,
    TTH_BTH  = 9,
    TTV_BTV  = 10,
    QT_QT    = 11
};

struct CMNTSymbol {
    uint8_t level;              // 1: single node, 2: joint pair
    uint8_t nodes[2];           // Node indices {0, 1, 2}
    double theoretical_bits;    // Information cost (trits converted to bits)
};

// CMNT 3-Node Mapping Table with Self-Repeating Diagonal States
const CMNTSymbol CMNT_TABLE[12] = {
    {1, {0, 0}, 1.58496}, // NO_SPLIT -> (N1)
    {1, {1, 0}, 1.58496}, // QT       -> (N2)
    {1, {2, 0}, 1.58496}, // BTH      -> (N3)
    {2, {0, 0}, 3.16993}, // BTV      -> (N1, N1) [Self-Repeat]
    {2, {1, 1}, 3.16993}, // TTH      -> (N2, N2) [Self-Repeat]
    {2, {2, 2}, 3.16993}, // TTV      -> (N3, N3) [Self-Repeat]
    {2, {0, 1}, 3.16993}, // BTH_BTH  -> (N1, N2) [Cross-Pair]
    {2, {0, 2}, 3.16993}, // BTH_BTV  -> (N1, N3) [Cross-Pair]
    {2, {1, 0}, 3.16993}, // BTV_BTV  -> (N2, N1) [Cross-Pair]
    {2, {1, 2}, 3.16993}, // TTH_BTH  -> (N2, N3) [Cross-Pair]
    {2, {2, 0}, 3.16993}, // TTV_BTV  -> (N3, N1) [Cross-Pair]
    {2, {2, 1}, 3.16993}  // QT_QT    -> (N3, N2) [Cross-Pair]
};

// Fast Hardware Single/Double-Cycle Decoder
inline PartitionMode decode_cmnt(uint8_t level, uint8_t n0, uint8_t n1) {
    if (level == 1) {
        if (n0 == 0) return NO_SPLIT;
        if (n0 == 1) return QT;
        return BTH;
    } else {
        if (n0 == 0 && n1 == 0) return BTV;
        if (n0 == 1 && n1 == 1) return TTH;
        if (n0 == 2 && n1 == 2) return TTV;
        if (n0 == 0 && n1 == 1) return BTH_BTH;
        if (n0 == 0 && n1 == 2) return BTH_BTV;
        if (n0 == 1 && n1 == 0) return BTV_BTV;
        if (n0 == 1 && n1 == 2) return TTH_BTH;
        if (n0 == 2 && n1 == 0) return TTV_BTV;
        return QT_QT;
    }
}

int main() {
    std::cout << "========================================================\n";
    std::cout << "  CMNT Reference C++ Codec Engine\n";
    std::cout << "  Author: Surafel Wolde (FAN: 8047836790317269)\n";
    std::cout << "========================================================\n\n";

    std::cout << "Verifying Encode/Decode Identity across all 12 states:\n";
    bool all_pass = true;
    for (int m = 0; m < 12; ++m) {
        CMNTSymbol sym = CMNT_TABLE[m];
        PartitionMode decoded = decode_cmnt(sym.level, sym.nodes[0], sym.nodes[1]);
        std::cout << "  Mode " << m << ": Encoded Level=" << (int)sym.level 
                  << " (N" << (int)sym.nodes[0] + 1;
        if (sym.level == 2) std::cout << ", N" << (int)sym.nodes[1] + 1;
        std::cout << ") -> Decoded Mode: " << decoded;
        if (decoded == m) {
            std::cout << " [PASS]\n";
        } else {
            std::cout << " [FAIL]\n";
            all_pass = false;
        }
    }

    std::cout << "\nAll 12 States Passed: " << (all_pass ? "YES" : "NO") << "\n";
    return 0;
}
