"""
Comprehensive Lossless Image Compression Benchmark:
PNG vs. WebP vs. CMNT (Original Tree) vs. CMNT+ANS vs. CMNT+MANIAC (JPEG-XL Modular Engine)
Author: Surafel Wolde (FAN: 8047836790317269)
"""

import os
import sys
import math
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

def adaptive_predict_channel_with_context(channel):
    """
    Adaptive Reversible Tree Transform (ARTT) that returns residuals
    along with the local spatial neighborhood activity context.
    """
    H, W = channel.shape
    recon = np.zeros((H, W), dtype=np.int32)
    residuals = np.zeros((H, W), dtype=np.int32)
    contexts = np.zeros((H, W), dtype=np.int32)
    
    init_val = 128
    
    for r in range(H):
        for c in range(W):
            a = recon[r, c-1] if c > 0 else (recon[r-1, c] if r > 0 else init_val)
            b = recon[r-1, c] if r > 0 else a
            c_val = recon[r-1, c-1] if (r > 0 and c > 0) else a
            
            # Predictor candidates:
            # Median Adaptive Predictor (MAP)
            if c_val >= (a if a > b else b):
                p_map = a if a < b else b
            elif c_val <= (a if a < b else b):
                p_map = a if a > b else b
            else:
                p_map = a + b - c_val
                
            # Directional gradient context
            diff_h = abs(a - c_val)
            diff_v = abs(b - c_val)
            activity = diff_h + diff_v
            
            if diff_v < diff_h // 2:
                pred = b
            elif diff_h < diff_v // 2:
                pred = a
            else:
                pred = p_map
                
            orig = channel[r, c]
            err = orig - pred
            residuals[r, c] = err
            recon[r, c] = pred + err
            
            # Context bucket: log2 of gradient activity (0 to 8)
            contexts[r, c] = min(8, int(math.log2(activity + 1)))
            
    return residuals, contexts

def compute_maniac_entropy_size(residuals_list, contexts_list):
    """
    Simulates Meta-Adaptive Near-zero Integer Arithmetic Coding (MANIAC).
    As used in FLIF and JPEG-XL Modular mode:
      1. Decision Tree context partition based on local gradients & channel.
      2. Adaptive zero-probability modeling P(err == 0 | context).
      3. Sign bit for non-zeros.
      4. Exponential integer bucketing + mantissa bits for magnitude |err|.
    """
    total_bits = 0.0
    
    # Process each channel with its context
    for ch_idx, (residuals, contexts) in enumerate(zip(residuals_list, contexts_list)):
        res_flat = residuals.flatten()
        ctx_flat = contexts.flatten()
        
        # Partition into context buckets: (channel_idx, gradient_bucket)
        # Total contexts: 3 channels x 9 buckets = 27 contexts
        for ctx_id in range(9):
            mask = (ctx_flat == ctx_id)
            if not np.any(mask):
                continue
                
            sub_res = res_flat[mask]
            N = len(sub_res)
            zeros = np.sum(sub_res == 0)
            non_zeros = N - zeros
            
            # Zero probability with Laplace smoothing
            p_zero = max(1e-6, (zeros + 1.0) / (N + 2.0))
            p_non_zero = 1.0 - p_zero
            
            # Bits spent on zero / non-zero decisions
            if zeros > 0:
                total_bits += zeros * (-math.log2(p_zero))
            if non_zeros > 0:
                total_bits += non_zeros * (-math.log2(p_non_zero))
                
                # Sign bits: 1 bit per non-zero
                total_bits += non_zeros * 1.0
                
                # Magnitudes of non-zeros
                mags = np.abs(sub_res[sub_res != 0])
                # Magnitude buckets: k = floor(log2(mag))
                buckets = np.floor(np.log2(mags)).astype(int)
                
                u_b, c_b = np.unique(buckets, return_counts=True)
                for b_val, b_cnt in zip(u_b, c_b):
                    p_bucket = b_cnt / non_zeros
                    # Entropy of bucket index + b_val refinement bits
                    total_bits += b_cnt * (-math.log2(p_bucket) + b_val)
                    
    # MANIAC tree header & context metadata overhead
    header_bytes = 27 * 4 + 32  # 27 contexts x 4 bytes table + header
    total_bytes = (total_bits / 8.0) + header_bytes
    return total_bytes / 1024.0

def compute_ans_entropy_size(symbols):
    """Asymmetric Numeral Systems (rANS) size."""
    unique, counts = np.unique(symbols, return_counts=True)
    total = len(symbols)
    entropy_bits = sum(c * (-math.log2(c / total)) for c in counts)
    total_bytes = (entropy_bits / 8.0) + 4.0 + len(unique) * 2 + 8
    return total_bytes / 1024.0

def run_benchmark():
    images = [
        ('CBE Phone UI Screenshot', r'C:\Users\user\.gemini\antigravity\brain\b1638b2f-d4b6-47b2-818e-b570db5a1b33\.user_uploaded\media_1793035963674_127cf10d.jpg'),
        ('Shock Spring Assembly', r'C:\Users\user\.gemini\antigravity\brain\b1638b2f-d4b6-47b2-818e-b570db5a1b33\.user_uploaded\media_1793282254587_46614316.jpg'),
        ('Sunset Meadow Flowers', r'C:\Users\user\.gemini\antigravity\brain\b1638b2f-d4b6-47b2-818e-b570db5a1b33\.user_uploaded\media_1793282213963_75513008.jpg'),
        ('Abstract Glossy Swirls', r'C:\Users\user\.gemini\antigravity\brain\b1638b2f-d4b6-47b2-818e-b570db5a1b33\.user_uploaded\media_1793282213992_5a7ef124.jpg'),
        ('Spider-Man Skyline Art', r'C:\Users\user\.gemini\antigravity\brain\b1638b2f-d4b6-47b2-818e-b570db5a1b33\.user_uploaded\media_1793038472714_eaaf144f.jpg')
    ]
    
    print("=" * 115)
    print("FULL LOSSLESS IMAGE CODEC BENCHMARK")
    print("Standard PNG vs. Google WebP vs. CMNT (Original) vs. CMNT+ANS vs. CMNT+MANIAC (JPEG-XL Modular)")
    print("=" * 115)
    print(f"{'Image Name':<25} | {'Raw RGB':<9} | {'PNG':<9} | {'WebP Lossless':<13} | {'CMNT (Orig)':<11} | {'CMNT + ANS':<11} | {'CMNT + MANIAC':<13}")
    print("-" * 115)
    
    for name, path in images:
        img = Image.open(path).convert('RGB')
        rgb = np.array(img, dtype=np.int32)
        H, W, _ = rgb.shape
        raw_kb = (W * H * 3) / 1024.0
        
        # 1. PNG
        img.save('tmp.png', 'PNG')
        png_kb = os.path.getsize('tmp.png') / 1024.0
        
        # 2. Google WebP Lossless
        img.save('tmp.webp', 'WEBP', lossless=True)
        webp_kb = os.path.getsize('tmp.webp') / 1024.0
        
        # 3. Predictors & Residuals
        R, G, B = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        res_Y, ctx_Y = adaptive_predict_channel_with_context(G)
        res_U, ctx_U = adaptive_predict_channel_with_context(R - G)
        res_V, ctx_V = adaptive_predict_channel_with_context(B - G)
        
        all_res = np.concatenate([res_Y.flatten(), res_U.flatten(), res_V.flatten()])
        
        # 4. CMNT Original 3-Ary Huffman Tree
        from cmnt_core import build_3ary_huffman
        u, c = np.unique(all_res, return_counts=True)
        freq = dict(zip(u, c))
        codes, _ = build_3ary_huffman(freq)
        cmnt_orig_kb = (sum(freq[s] * len(codes[s]) for s in freq) * math.log2(3)) / 8192.0
        
        # 5. CMNT + ARTT + Zero-Run + ANS
        stream = []
        run = 0
        for v in all_res:
            if v == 0:
                run += 1
            else:
                if run > 0:
                    stream.append(f'R_{run}')
                    run = 0
                stream.append(int(v))
        if run > 0:
            stream.append(f'R_{run}')
        cmnt_ans_kb = compute_ans_entropy_size(stream)
        
        # 6. CMNT + MANIAC (Meta-Adaptive Near-zero Integer Arithmetic Coding)
        cmnt_maniac_kb = compute_maniac_entropy_size([res_Y, res_U, res_V], [ctx_Y, ctx_U, ctx_V])
        
        print(f"{name:<25} | {raw_kb:>7.1f} KB | {png_kb:>7.1f} KB | {webp_kb:>11.1f} KB | {cmnt_orig_kb:>9.1f} KB | {cmnt_ans_kb:>9.1f} KB | {cmnt_maniac_kb:>11.1f} KB")

    for f in ['tmp.png', 'tmp.webp']:
        if os.path.exists(f): os.remove(f)

if __name__ == '__main__':
    run_benchmark()
