"""
CMNT Codec Package
Combinatorial Multi-Node Tree Image Compression Architecture
Author: Surafel Wolde (FAN: 8047836790317269), Aziza Jemal
"""

from .core import compress_image_to_cmnt, decompress_cmnt_to_image, MAGIC, VERSION

__version__ = "1.0.0"
__author__ = "Surafel Wolde, Aziza Jemal"
__all__ = ["compress_image_to_cmnt", "decompress_cmnt_to_image", "MAGIC", "VERSION"]
