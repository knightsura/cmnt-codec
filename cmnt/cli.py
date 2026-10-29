#!/usr/bin/env python3
"""
CMNT Codec Command Line Interface
Author: Surafel Wolde (FAN: 8047836790317269)

Usage:
  python cmnt_cli.py compress input.png output.cmnt [--lossless | --lossy]
  python cmnt_cli.py decompress input.cmnt output.png
  python cmnt_cli.py view input.cmnt
  python cmnt_cli.py info input.cmnt
"""

import os
import sys
import argparse
import tempfile
import struct
from cmnt_core import compress_image_to_cmnt, decompress_cmnt_to_image, MAGIC

def cmd_compress(args):
    input_path = args.input
    output_path = args.output
    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".cmnt"

    if args.lossy:
        delta_y = 3
        delta_c = 5
        mode_label = "Near-Lossless / High-Efficiency Lossy (Delta Y=3, C=5)"
    else:
        delta_y = 1
        delta_c = 1
        mode_label = "Lossless (100% Bit-Perfect Reversible)"

    print(f"\n[CMNT ENCODER] Mode: {mode_label}")
    print(f"Reading:  {input_path}")
    stats = compress_image_to_cmnt(input_path, output_path, delta_y=delta_y, delta_c=delta_c)
    
    print(f"Success! Saved to: {output_path}")
    print(f"Dimensions:        {stats['width']} x {stats['height']} (24-bit RGB)")
    print(f"Raw RGB Size:      {stats['raw_bytes'] / 1024:.2f} KB")
    print(f"CMNT File Size:    {stats['cmnt_bytes'] / 1024:.2f} KB")
    print(f"Compression Ratio: {stats['ratio']:.2f}x\n")

def cmd_decompress(args):
    input_path = args.input
    output_path = args.output
    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = base + "_restored.png"

    print(f"\n[CMNT DECODER] Opening: {input_path}")
    img, (W, H, dy, dc) = decompress_cmnt_to_image(input_path, output_path)
    mode = "Lossless" if (dy == 1 and dc == 1) else f"Lossy (dy={dy}, dc={dc})"
    print(f"Decoded:   {W} x {H} pixels ({mode})")
    print(f"Exported:  {output_path}\n")

def cmd_view(args):
    input_path = args.input
    print(f"\n[CMNT VIEWER] Opening {input_path} in Windows Image Viewer...")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        temp_png = tf.name
    
    decompress_cmnt_to_image(input_path, temp_png)
    if sys.platform == 'win32':
        os.startfile(temp_png)
    else:
        print(f"Rendered temporary file at {temp_png}")
    print("Image opened successfully.\n")

def cmd_info(args):
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return
        
    with open(input_path, 'rb') as f:
        header_data = f.read(25)
        if len(header_data) < 25:
            print("Error: Invalid CMNT file (too short).")
            return
            
        (magic, ver, W, H, delta_y, delta_c, num_symbols,
         codebook_size, total_trits, payload_size) = struct.unpack('>4sBHHBBHIII', header_data)
        
    if magic != MAGIC:
        print(f"Error: Magic bytes mismatch (got {magic}, expected {MAGIC})")
        return
        
    file_size = os.path.getsize(input_path)
    raw_size = W * H * 3
    mode = "Lossless (Bit-Perfect)" if (delta_y == 1 and delta_c == 1) else f"Lossy (ΔY={delta_y}, ΔC={delta_c})"
    
    print("\n" + "=" * 55)
    print("           CMNT FILE METADATA HEADER")
    print("=" * 55)
    print(f"File Path:         {input_path}")
    print(f"Format Version:    v{ver}")
    print(f"Resolution:        {W} x {H} pixels")
    print(f"Channels:          3 (RGB with Reversible Color Transform)")
    print(f"Quantization:      {mode}")
    print(f"Symbol Vocabulary: {num_symbols} active residual symbols")
    print(f"Total Trits:       {total_trits:,} ternary pulses")
    print(f"Dense Packing:     5 trits / byte (99.06% density)")
    print(f"Header + Codebook: {25 + codebook_size} bytes")
    print(f"Payload Size:      {payload_size} bytes")
    print(f"Total Disk Size:   {file_size / 1024:.2f} KB ({file_size:,} bytes)")
    print(f"Compression Ratio: {raw_size / file_size:.2f}x vs raw RGB")
    print("=" * 55 + "\n")

def main():
    parser = argparse.ArgumentParser(description="CMNT (Combinatorial Multi-Node Tree) Image Codec CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Compress
    p_comp = subparsers.add_parser("compress", help="Compress image to .cmnt")
    p_comp.add_argument("input", help="Path to input image (.png, .jpg, etc.)")
    p_comp.add_argument("output", nargs="?", default=None, help="Path to output .cmnt file")
    p_comp.add_argument("--lossy", action="store_true", help="Enable near-lossless high efficiency lossy mode")
    p_comp.set_defaults(func=cmd_compress)

    # Decompress
    p_decomp = subparsers.add_parser("decompress", help="Decompress .cmnt to image")
    p_decomp.add_argument("input", help="Path to input .cmnt file")
    p_decomp.add_argument("output", nargs="?", default=None, help="Path to output image (.png)")
    p_decomp.set_defaults(func=cmd_decompress)

    # View
    p_view = subparsers.add_parser("view", help="Decompress and display .cmnt immediately")
    p_view.add_argument("input", help="Path to input .cmnt file")
    p_view.set_defaults(func=cmd_view)

    # Info
    p_info = subparsers.add_parser("info", help="Display metadata of .cmnt file")
    p_info.add_argument("input", help="Path to input .cmnt file")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
