"""Day 46: Gene Encoder/Decoder System - 6.4KB"""
import base64
import json
import struct
from typing import Any, Dict, List, Union


class GeneEncoder:
    """Efficient encoding and decoding of genetic information"""

    def __init__(self):
        """Initialize gene encoder with encoding schemes"""
        self.encoding_schemes = {
            "binary": self._binary_encode,
            "gray": self._gray_encode,
            "real": self._real_encode,
        }
        self.decoding_schemes = {
            "binary": self._binary_decode,
            "gray": self._gray_decode,
            "real": self._real_decode,
        }

    def encode_numeric(
        self, value: Union[int, float], min_val: float = 0, max_val: float = 1, bits: int = 8
    ) -> str:
        """Encode numeric value to binary string"""
        # Normalize to [0, 1]
        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0.0, min(1.0, normalized))

        # Convert to integer representation
        int_val = int(normalized * (2**bits - 1))

        # Convert to binary string
        binary = format(int_val, f"0{bits}b")
        return binary

    def decode_numeric(self, encoded: str, min_val: float = 0, max_val: float = 1) -> float:
        """Decode binary string to numeric value"""
        # Convert binary to integer
        int_val = int(encoded, 2)
        bits = len(encoded)

        # Normalize to [0, 1]
        normalized = int_val / (2**bits - 1)

        # Scale to original range
        value = min_val + normalized * (max_val - min_val)
        return value

    def encode_categorical(self, selected: List[str], categories: List[str]) -> str:
        """Encode categorical selections as bit string"""
        encoding = []
        for category in categories:
            if category in selected:
                encoding.append("1")
            else:
                encoding.append("0")
        return "".join(encoding)

    def decode_categorical(self, encoded: str, categories: List[str]) -> List[str]:
        """Decode bit string to categorical selections"""
        selected = []
        for i, bit in enumerate(encoded):
            if bit == "1" and i < len(categories):
                selected.append(categories[i])
        return selected

    def compress(self, data: Dict[str, Any]) -> str:
        """Compress complex data structure to string"""
        # Convert to JSON
        json_str = json.dumps(data, separators=(",", ":"))

        # Compress using base64
        compressed = base64.b64encode(json_str.encode()).decode()

        # Further compress if too large
        if len(compressed) > 1024:
            # Use simple RLE compression
            compressed = self._run_length_encode(compressed)

        return compressed

    def decompress(self, compressed: str) -> Dict[str, Any]:
        """Decompress string back to data structure"""
        try:
            # Check if RLE compressed
            if compressed.startswith("RLE:"):
                compressed = self._run_length_decode(compressed[4:])

            # Decode base64
            json_str = base64.b64decode(compressed).decode()

            # Parse JSON
            return json.loads(json_str)
        except Exception:
            return {}

    def _binary_encode(self, value: float, bits: int = 16) -> str:
        """Standard binary encoding"""
        int_val = int(value * (2**bits - 1))
        return format(int_val, f"0{bits}b")

    def _binary_decode(self, encoded: str) -> float:
        """Standard binary decoding"""
        int_val = int(encoded, 2)
        return int_val / (2 ** len(encoded) - 1)

    def _gray_encode(self, value: float, bits: int = 16) -> str:
        """Gray code encoding for better mutation properties"""
        # First get binary
        binary = self._binary_encode(value, bits)
        int_val = int(binary, 2)

        # Convert to Gray code
        gray = int_val ^ (int_val >> 1)
        return format(gray, f"0{bits}b")

    def _gray_decode(self, encoded: str) -> float:
        """Gray code decoding"""
        gray = int(encoded, 2)

        # Convert Gray to binary
        mask = gray
        while mask:
            mask >>= 1
            gray ^= mask

        # Convert to float
        return gray / (2 ** len(encoded) - 1)

    def _real_encode(self, value: float, bits: int = 32) -> str:
        """Real-valued encoding using IEEE 754"""
        # Pack as float
        packed = struct.pack("f", value)

        # Convert to binary string
        binary = "".join(format(byte, "08b") for byte in packed)
        return binary[:bits] if len(binary) > bits else binary

    def _real_decode(self, encoded: str) -> float:
        """Real-valued decoding"""
        # Pad to 32 bits if necessary
        if len(encoded) < 32:
            encoded = encoded + "0" * (32 - len(encoded))
        elif len(encoded) > 32:
            encoded = encoded[:32]

        # Convert to bytes
        bytes_val = int(encoded, 2).to_bytes(4, byteorder="big")

        # Unpack as float
        try:
            return struct.unpack(">f", bytes_val)[0]
        except:
            return 0.0

    def _run_length_encode(self, data: str) -> str:
        """Simple run-length encoding for compression"""
        if not data:
            return "RLE:"

        result = ["RLE:"]
        current = data[0]
        count = 1

        for char in data[1:]:
            if char == current and count < 9:
                count += 1
            else:
                result.append(f"{count}{current}")
                current = char
                count = 1

        result.append(f"{count}{current}")
        return "".join(result)

    def _run_length_decode(self, encoded: str) -> str:
        """Run-length decoding"""
        result = []
        i = 0

        while i < len(encoded):
            if encoded[i].isdigit():
                count = int(encoded[i])
                if i + 1 < len(encoded):
                    char = encoded[i + 1]
                    result.append(char * count)
                    i += 2
                else:
                    break
            else:
                result.append(encoded[i])
                i += 1

        return "".join(result)

    def encode_genome_sequence(self, traits: Dict[str, Any]) -> str:
        """Encode complete genome sequence"""
        encoded_parts = []

        # Encode different trait types
        for key, value in traits.items():
            if isinstance(value, (int, float)):
                # Numeric encoding
                if key == "memory":
                    enc = self.encode_numeric(value, 0, 10000, 14)
                elif key == "speed":
                    enc = self.encode_numeric(value, 0, 10, 10)
                else:
                    enc = self.encode_numeric(value, 0, 1, 8)
                encoded_parts.append(enc)

            elif isinstance(value, list):
                # List encoding (capabilities)
                all_options = [
                    "search",
                    "analysis",
                    "generation",
                    "validation",
                    "optimization",
                    "prediction",
                    "classification",
                    "clustering",
                    "transformation",
                    "aggregation",
                    "monitoring",
                    "debugging",
                    "testing",
                    "deployment",
                ]
                enc = self.encode_categorical(value, all_options)
                encoded_parts.append(enc)

            elif isinstance(value, str):
                # String encoding (architecture type)
                options = ["reactive", "deliberative", "hybrid", "adaptive"]
                if value in options:
                    idx = options.index(value)
                    enc = format(idx, "02b")
                    encoded_parts.append(enc)

        return "".join(encoded_parts)

    def decode_genome_sequence(self, sequence: str) -> Dict[str, Any]:
        """Decode genome sequence back to traits"""
        traits = {}
        pos = 0

        # Decode memory (14 bits)
        if pos + 14 <= len(sequence):
            traits["memory"] = self.decode_numeric(sequence[pos : pos + 14], 0, 10000)
            pos += 14

        # Decode speed (10 bits)
        if pos + 10 <= len(sequence):
            traits["speed"] = self.decode_numeric(sequence[pos : pos + 10], 0, 10)
            pos += 10

        # Decode optimization (8 bits)
        if pos + 8 <= len(sequence):
            traits["optimization"] = self.decode_numeric(sequence[pos : pos + 8], 0, 1)
            pos += 8

        # Decode capabilities (14 bits)
        if pos + 14 <= len(sequence):
            all_options = [
                "search",
                "analysis",
                "generation",
                "validation",
                "optimization",
                "prediction",
                "classification",
                "clustering",
                "transformation",
                "aggregation",
                "monitoring",
                "debugging",
                "testing",
                "deployment",
            ]
            traits["capabilities"] = self.decode_categorical(sequence[pos : pos + 14], all_options)
            pos += 14

        # Decode architecture (2 bits)
        if pos + 2 <= len(sequence):
            options = ["reactive", "deliberative", "hybrid", "adaptive"]
            idx = int(sequence[pos : pos + 2], 2)
            if idx < len(options):
                traits["architecture"] = options[idx]
            pos += 2

        return traits

    def validate_encoding(self, encoded: str) -> bool:
        """Validate that encoding is valid"""
        # Check if only contains valid characters
        valid_chars = set("01AGCT")
        return all(c in valid_chars for c in encoded)

    def encoding_efficiency(self, original: Dict, encoded: str) -> float:
        """Calculate encoding efficiency ratio"""
        original_size = len(json.dumps(original))
        encoded_size = len(encoded)

        if original_size == 0:
            return 1.0

        return 1.0 - (encoded_size / original_size)
