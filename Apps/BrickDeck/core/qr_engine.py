"""
BrickDeck Pure-Python Barcode & QR Code Engine (core/qr_engine.py)
Generates standard 2D QR Codes (Versions 1 to 6) and 1D Barcodes (Code 128, EAN-13, Code 39).
100% standalone, zero-pip dependencies: runs anywhere on ARM64 Linux without external packages.
"""

from typing import List, Tuple, Optional, Dict

# =====================================================================
# 1. GALOIS FIELD GF(256) & REED-SOLOMON ERROR CORRECTION
# =====================================================================

EXP = [0] * 512
LOG = [0] * 256
_x = 1
for _i in range(255):
    EXP[_i] = _x
    EXP[_i + 255] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D  # Primitive poly x^8 + x^4 + x^3 + x^2 + 1


def gf_mul(x: int, y: int) -> int:
    if x == 0 or y == 0:
        return 0
    return EXP[(LOG[x] + LOG[y]) % 255]


def rs_generator_poly(nsym: int) -> List[int]:
    g = [1]
    for i in range(nsym):
        factor = EXP[i]
        next_g = [0] * (len(g) + 1)
        for j in range(len(g)):
            next_g[j] ^= g[j]
            next_g[j + 1] ^= gf_mul(g[j], factor)
        g = next_g
    return g


def rs_encode(data: List[int], nsym: int) -> List[int]:
    gen = rs_generator_poly(nsym)
    res = list(data) + [0] * nsym
    for i in range(len(data)):
        coef = res[i]
        if coef != 0:
            for j in range(len(gen)):
                res[i + j] ^= gf_mul(gen[j], coef)
    return res[len(data):]


# =====================================================================
# 2. QR CODE SPECIFICATIONS (VERSIONS 1 TO 6)
# =====================================================================

# Capacity tables for Byte mode (Level M and Level L)
# Tuple: (total_codewords, data_codewords, ec_codewords, num_blocks)
QR_SPECS = {
    # Version: { 'M': (total, data, ec, blocks), 'L': (total, data, ec, blocks) }
    1: {'M': (26, 16, 10, 1), 'L': (26, 19, 7, 1)},
    2: {'M': (44, 28, 16, 1), 'L': (44, 34, 10, 1)},
    3: {'M': (70, 44, 26, 1), 'L': (70, 55, 15, 1)},
    4: {'M': (100, 64, 36, 2), 'L': (100, 80, 20, 1)},
    5: {'M': (134, 86, 48, 2), 'L': (134, 108, 26, 1)},
    6: {'M': (172, 108, 64, 4), 'L': (172, 136, 36, 2)},
}

# Alignment pattern centers for versions 1 to 6
ALIGNMENT_COORDS = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
}


def get_format_info(ec_level_bits: int, mask_pattern: int) -> int:
    """Returns 15-bit format info word protected with BCH(15, 5)."""
    data = (ec_level_bits << 3) | mask_pattern
    rem = data << 10
    gen = 0x537
    for i in range(14, 9, -1):
        if (rem >> i) & 1:
            rem ^= (gen << (i - 10))
    return ((data << 10) | rem) ^ 0x5412


def generate_qr_matrix(text: str, ec_level: str = 'M') -> Tuple[List[List[int]], int]:
    """
    Generates standard QR Code 2D matrix (0=white, 1=black).
    Returns (matrix, version).
    """
    raw_bytes = text.encode('utf-8')
    data_len = len(raw_bytes)

    # Determine minimum required version
    version = None
    for v in range(1, 7):
        spec = QR_SPECS[v][ec_level]
        max_bytes = spec[1] - 2  # 2 bytes overhead for mode (4 bits) + length (8 bits)
        if data_len <= max_bytes:
            version = v
            break

    if version is None:
        version = 6  # Truncate or cap at version 6
        max_b = QR_SPECS[6][ec_level][1] - 2
        raw_bytes = raw_bytes[:max_b]
        data_len = len(raw_bytes)

    total_cw, data_cw, ec_cw, num_blocks = QR_SPECS[version][ec_level]
    size = 17 + 4 * version

    # 1. Encode data in Byte mode (0100)
    bits = "0100"
    # Character count (8 bits for versions 1-9 in Byte mode)
    bits += f"{data_len:08b}"
    for b in raw_bytes:
        bits += f"{b:08b}"

    # Terminator 0000 (up to 4 bits)
    bits += "0000"
    # Pad to byte boundary
    if len(bits) % 8 != 0:
        bits += "0" * (8 - (len(bits) % 8))

    # Convert bitstring to data codewords
    codewords = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]

    # Pad with alternate 0xEC and 0x11
    pad_bytes = [0xEC, 0x11]
    p_idx = 0
    while len(codewords) < data_cw:
        codewords.append(pad_bytes[p_idx % 2])
        p_idx += 1

    # 2. Compute Reed-Solomon Error Correction
    ec_per_block = ec_cw // num_blocks
    data_per_block = data_cw // num_blocks

    all_data_blocks = []
    all_ec_blocks = []
    for b in range(num_blocks):
        b_data = codewords[b * data_per_block : (b + 1) * data_per_block]
        b_ec = rs_encode(b_data, ec_per_block)
        all_data_blocks.append(b_data)
        all_ec_blocks.append(b_ec)

    # Interleave data blocks and EC blocks
    final_codewords = []
    for i in range(data_per_block):
        for b in range(num_blocks):
            final_codewords.append(all_data_blocks[b][i])
    for i in range(ec_per_block):
        for b in range(num_blocks):
            final_codewords.append(all_ec_blocks[b][i])

    # Convert final codewords to bitstream
    data_bits = "".join(f"{cw:08b}" for cw in final_codewords)

    # 3. Create Matrix and Function Patterns
    matrix = [[None] * size for _ in range(size)]
    is_reserved = [[False] * size for _ in range(size)]

    def set_module(r, c, val):
        matrix[r][c] = val
        is_reserved[r][c] = True

    # Finder Patterns (7x7) + Separator
    for fr, fc in [(0, 0), (0, size - 7), (size - 7, 0)]:
        for r in range(-1, 8):
            for c in range(-1, 8):
                mr, mc = fr + r, fc + c
                if 0 <= mr < size and 0 <= mc < size:
                    if 0 <= r <= 6 and 0 <= c <= 6:
                        # 7x7 pattern
                        if r in (0, 6) or c in (0, 6) or (2 <= r <= 4 and 2 <= c <= 4):
                            set_module(mr, mc, 1)
                        else:
                            set_module(mr, mc, 0)
                    else:
                        set_module(mr, mc, 0)  # White separator

    # Timing Patterns (Row 6 and Col 6)
    for i in range(8, size - 8):
        if not is_reserved[6][i]:
            set_module(6, i, 1 if i % 2 == 0 else 0)
        if not is_reserved[i][6]:
            set_module(i, 6, 1 if i % 2 == 0 else 0)

    # Dark module
    set_module(size - 8, 8, 1)

    # Alignment Patterns (for v >= 2)
    coords = ALIGNMENT_COORDS.get(version, [])
    for ar in coords:
        for ac in coords:
            # Skip if overlapping with finder patterns
            if (ar < 9 and ac < 9) or (ar < 9 and ac > size - 9) or (ar > size - 9 and ac < 9):
                continue
            for r in range(-2, 3):
                for c in range(-2, 3):
                    mr, mc = ar + r, ac + c
                    if max(abs(r), abs(c)) in (0, 2):
                        set_module(mr, mc, 1)
                    else:
                        set_module(mr, mc, 0)

    # Reserve Format Information areas
    for i in range(9):
        if i != 6:
            is_reserved[8][i] = True
            is_reserved[i][8] = True
    for i in range(size - 8, size):
        is_reserved[8][i] = True
        is_reserved[i][8] = True

    # 4. Place Data Bits in 2-Column Zig-Zag
    bit_idx = 0
    dir_up = True
    col = size - 1
    while col > 0:
        if col == 6:  # Skip vertical timing pattern
            col -= 1

        row_range = range(size - 1, -1, -1) if dir_up else range(size)
        for r in row_range:
            for c_off in (0, -1):
                c = col + c_off
                if not is_reserved[r][c]:
                    b_val = 0
                    if bit_idx < len(data_bits):
                        b_val = int(data_bits[bit_idx])
                        bit_idx += 1
                    # Apply Mask 0: (row + col) % 2 == 0
                    if (r + c) % 2 == 0:
                        matrix[r][c] = 1 - b_val
                    else:
                        matrix[r][c] = b_val
        dir_up = not dir_up
        col -= 2

    # 5. Place Format Information (Level M = 00, Mask 0 = 000 -> 0x5412)
    # ec_bits: 'M'=0, 'L'=1
    ec_bits = 0 if ec_level == 'M' else 1
    fmt_info = get_format_info(ec_bits, 0)

    # Format bits placement (around top-left finder, and bottom/right)
    fmt_bits = [ (fmt_info >> i) & 1 for i in range(15) ]
    # Top-left
    # fmt_bits 0..5 -> (8, 0..5)
    # fmt_bits 6..8 -> (8, 7), (8, 8), (7, 8)
    # fmt_bits 9..14 -> (5..0, 8)
    coords_tl = [
        (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8),
        (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)
    ]
    for i, (r, c) in enumerate(coords_tl):
        matrix[r][c] = fmt_bits[i]

    # Split for bottom-left and top-right
    # fmt_bits 0..6 -> (size-1..size-7, 8)
    # fmt_bits 7..14 -> (8, size-8..size-1)
    coords_split = [
        (size - 1, 8), (size - 2, 8), (size - 3, 8), (size - 4, 8),
        (size - 5, 8), (size - 6, 8), (size - 7, 8),
        (8, size - 8), (8, size - 7), (8, size - 6), (8, size - 5),
        (8, size - 4), (8, size - 3), (8, size - 2), (8, size - 1)
    ]
    for i, (r, c) in enumerate(coords_split):
        matrix[r][c] = fmt_bits[i]

    # Fill any remaining None with 0
    clean_matrix = [[1 if matrix[r][c] == 1 else 0 for c in range(size)] for r in range(size)]
    return clean_matrix, version


# =====================================================================
# 3. 1D BARCODE GENERATORS (CODE 128, EAN-13, CODE 39)
# =====================================================================

# Code 128 Table (Pattern widths: 6 widths totaling 11 modules per symbol)
CODE128_PATTERNS = [
    "212222", "222122", "222221", "121223", "121322", "131222", "122213", "122312", "132212", "221213", # 0-9
    "221312", "231212", "112232", "122132", "122231", "113222", "123122", "123221", "223211", "221132", # 10-19
    "221231", "213212", "223112", "312131", "311222", "321122", "321221", "312212", "322112", "322211", # 20-29
    "212123", "212321", "232121", "111323", "131123", "131321", "112313", "132113", "132311", "211313", # 30-39
    "231113", "231311", "112133", "112331", "132131", "113123", "113321", "133121", "313121", "211331", # 40-49
    "231131", "213113", "213311", "213131", "311123", "311321", "331121", "312113", "312311", "332111", # 50-59
    "314111", "221411", "431111", "111224", "111422", "121124", "121421", "141122", "141221", "112214", # 60-69
    "112412", "122114", "122411", "142112", "142211", "241211", "221114", "413111", "241112", "134111", # 70-79
    "111242", "121142", "121241", "114212", "124112", "124211", "411212", "421112", "421211", "212141", # 80-89
    "214121", "412121", "111143", "111341", "131141", "114113", "114311", "411113", "411311", "113141", # 90-99
    "114131", "311141", "411131", "211412", "211214", "211232", "2331112" # 100-106 (104=StartB, 106=Stop)
]


def generate_code128(text: str) -> List[int]:
    """
    Generates standard Code 128 (Subtype B) 1D barcode bit sequence (1=bar, 0=space).
    """
    # Start Code B is value 104
    data_values = [104]
    for ch in text:
        val = ord(ch) - 32
        if 0 <= val <= 95:
            data_values.append(val)
        else:
            data_values.append(0)  # Space fallback

    # Checksum: (Start + sum(i * value)) % 103
    checksum = data_values[0]
    for i, v in enumerate(data_values[1:], 1):
        checksum += i * v
    data_values.append(checksum % 103)
    # Stop Code is 106
    data_values.append(106)

    # Convert pattern widths to bitstream
    bits = [0] * 10  # Quiet zone
    for idx in data_values:
        pat = CODE128_PATTERNS[idx]
        is_bar = 1
        for width_char in pat:
            w = int(width_char)
            bits.extend([is_bar] * w)
            is_bar = 1 - is_bar
    bits.extend([0] * 10)  # Quiet zone
    return bits


def generate_ean13(digits_str: str) -> Tuple[List[int], str]:
    """
    Generates standard EAN-13 retail barcode bit sequence (1=bar, 0=space).
    Returns (bits, full_13_digits).
    """
    clean_digits = "".join(d for d in digits_str if d.isdigit())
    if len(clean_digits) < 12:
        clean_digits = clean_digits.ljust(12, '0')
    clean_digits = clean_digits[:12]

    # Calculate Modulo-10 Check Digit
    # weights: 1 for odd index (1st, 3rd, 5th), 3 for even index
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(clean_digits))
    check_digit = (10 - (total % 10)) % 10
    full_13 = clean_digits + str(check_digit)

    # EAN-13 Digit Patterns
    L_PATTERNS = ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"]
    G_PATTERNS = ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"]
    R_PATTERNS = ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"]

    # First digit determines L / G parity for left 6 digits
    PARITY_PATTERNS = [
        "LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
        "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"
    ]

    first_digit = int(full_13[0])
    parity_str = PARITY_PATTERNS[first_digit]

    bits = [0] * 10  # Quiet zone
    # Start Guard: 101
    bits.extend([1, 0, 1])

    # Left 6 digits
    for i in range(6):
        d = int(full_13[1 + i])
        pat = L_PATTERNS[d] if parity_str[i] == 'L' else G_PATTERNS[d]
        bits.extend([int(b) for b in pat])

    # Center Guard: 01010
    bits.extend([0, 1, 0, 1, 0])

    # Right 6 digits (always R patterns)
    for i in range(6):
        d = int(full_13[7 + i])
        bits.extend([int(b) for b in R_PATTERNS[d]])

    # End Guard: 101
    bits.extend([1, 0, 1])
    bits.extend([0] * 10)  # Quiet zone
    return bits, full_13
