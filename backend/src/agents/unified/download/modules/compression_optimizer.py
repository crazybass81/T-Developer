"""
Compression Optimizer Module
Optimizes file compression for faster downloads
"""

import asyncio
import bz2
import gzip
import lzma
import os
import shutil
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CompressionResult:
    success: bool
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_method: str
    output_path: str
    processing_time: float
    savings_percentage: float
    error: str = ""


@dataclass
class CompressionStats:
    files_processed: int
    total_original_size: int
    total_compressed_size: int
    average_compression_ratio: float
    best_method: str
    processing_time: float


class CompressionOptimizer:
    """Advanced file compression optimization"""

    def __init__(self):
        self.version = "1.0.0"

        self.compression_config = {
            "available_methods": {
                "zip": {
                    "extension": ".zip",
                    "compression_level": 6,  # 0-9
                    "good_for": ["mixed", "text", "code"],
                    "speed": "fast",
                },
                "gzip": {
                    "extension": ".tar.gz",
                    "compression_level": 6,
                    "good_for": ["text", "code", "logs"],
                    "speed": "fast",
                },
                "bz2": {
                    "extension": ".tar.bz2",
                    "compression_level": 9,
                    "good_for": ["large_files", "archives"],
                    "speed": "slow",
                },
                "lzma": {
                    "extension": ".tar.xz",
                    "compression_level": 6,
                    "good_for": ["maximum_compression"],
                    "speed": "very_slow",
                },
            },
            "auto_select_method": True,
            "max_processing_time": 300,  # 5 minutes
            "min_compression_ratio": 0.9,  # Only compress if 10%+ savings
            "parallel_processing": True,
        }

        self.optimization_history = []

    async def optimize_compression(
        self, source_path: str, target_directory: str, context: Dict[str, Any]
    ) -> CompressionResult:
        """Optimize compression for a file or directory"""

        start_time = datetime.now()

        try:
            # Analyze source to determine best compression method
            if self.compression_config["auto_select_method"]:
                best_method = await self._analyze_and_select_method(source_path)
            else:
                best_method = context.get("compression_method", "zip")

            # Get original size
            original_size = self._get_size(source_path)

            # Perform compression
            compressed_path = await self._compress_with_method(
                source_path, target_directory, best_method
            )

            # Get compressed size
            compressed_size = os.path.getsize(compressed_path)

            # Calculate metrics
            compression_ratio = compressed_size / original_size
            savings_percentage = (1 - compression_ratio) * 100
            processing_time = (datetime.now() - start_time).total_seconds()

            # Check if compression was worthwhile
            if compression_ratio > self.compression_config["min_compression_ratio"]:
                # Compression didn't save enough space, return original
                if os.path.exists(compressed_path):
                    os.remove(compressed_path)

                # Just copy original file
                output_path = os.path.join(target_directory, os.path.basename(source_path))
                shutil.copy2(source_path, output_path)

                return CompressionResult(
                    success=True,
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=1.0,
                    compression_method="none",
                    output_path=output_path,
                    processing_time=processing_time,
                    savings_percentage=0.0,
                )

            # Record optimization
            await self._record_optimization(
                source_path, best_method, compression_ratio, processing_time
            )

            return CompressionResult(
                success=True,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_method=best_method,
                output_path=compressed_path,
                processing_time=processing_time,
                savings_percentage=savings_percentage,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                compression_method="",
                output_path="",
                processing_time=processing_time,
                savings_percentage=0.0,
                error=str(e),
            )

    async def batch_optimize(
        self, source_paths: List[str], target_directory: str, context: Dict[str, Any]
    ) -> List[CompressionResult]:
        """Optimize compression for multiple files"""

        if self.compression_config["parallel_processing"]:
            # Process files in parallel
            tasks = [
                self.optimize_compression(path, target_directory, context) for path in source_paths
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            final_results = []
            for result in results:
                if isinstance(result, Exception):
                    final_results.append(
                        CompressionResult(
                            success=False,
                            original_size=0,
                            compressed_size=0,
                            compression_ratio=0.0,
                            compression_method="",
                            output_path="",
                            processing_time=0.0,
                            savings_percentage=0.0,
                            error=str(result),
                        )
                    )
                else:
                    final_results.append(result)

            return final_results
        else:
            # Process files sequentially
            results = []
            for source_path in source_paths:
                result = await self.optimize_compression(source_path, target_directory, context)
                results.append(result)
            return results

    async def _analyze_and_select_method(self, source_path: str) -> str:
        """Analyze source and select best compression method"""

        # Get file characteristics
        size = self._get_size(source_path)
        file_types = self._analyze_file_types(source_path)

        # Decision logic based on content and size
        if size < 1024 * 1024:  # < 1MB
            return "zip"  # Fast compression for small files

        elif size > 100 * 1024 * 1024:  # > 100MB
            if "binary" in file_types:
                return "zip"  # Don't over-compress binaries
            else:
                return "bz2"  # Better compression for large text files

        else:  # Medium size files
            if "text" in file_types or "code" in file_types:
                return "gzip"  # Good balance for text/code
            else:
                return "zip"  # Default for mixed content

    async def _compress_with_method(
        self, source_path: str, target_directory: str, method: str
    ) -> str:
        """Compress using specified method"""

        method_config = self.compression_config["available_methods"][method]
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        output_path = os.path.join(target_directory, base_name + method_config["extension"])

        if method == "zip":
            return await self._compress_zip(source_path, output_path, method_config)
        elif method == "gzip":
            return await self._compress_gzip(source_path, output_path, method_config)
        elif method == "bz2":
            return await self._compress_bz2(source_path, output_path, method_config)
        elif method == "lzma":
            return await self._compress_lzma(source_path, output_path, method_config)
        else:
            raise ValueError(f"Unknown compression method: {method}")

    async def _compress_zip(
        self, source_path: str, output_path: str, config: Dict[str, Any]
    ) -> str:
        """Compress using ZIP"""

        compression_level = config["compression_level"]

        with zipfile.ZipFile(
            output_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=compression_level,
        ) as zipf:
            if os.path.isfile(source_path):
                zipf.write(source_path, os.path.basename(source_path))
            else:
                # Compress directory
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, source_path)
                        zipf.write(file_path, arc_name)

        return output_path

    async def _compress_gzip(
        self, source_path: str, output_path: str, config: Dict[str, Any]
    ) -> str:
        """Compress using GZIP (TAR.GZ)"""

        compression_level = config["compression_level"]

        with tarfile.open(output_path, "w:gz", compresslevel=compression_level) as tar:
            if os.path.isfile(source_path):
                tar.add(source_path, arcname=os.path.basename(source_path))
            else:
                tar.add(source_path, arcname=os.path.basename(source_path))

        return output_path

    async def _compress_bz2(
        self, source_path: str, output_path: str, config: Dict[str, Any]
    ) -> str:
        """Compress using BZ2 (TAR.BZ2)"""

        compression_level = config["compression_level"]

        with tarfile.open(output_path, "w:bz2", compresslevel=compression_level) as tar:
            if os.path.isfile(source_path):
                tar.add(source_path, arcname=os.path.basename(source_path))
            else:
                tar.add(source_path, arcname=os.path.basename(source_path))

        return output_path

    async def _compress_lzma(
        self, source_path: str, output_path: str, config: Dict[str, Any]
    ) -> str:
        """Compress using LZMA (TAR.XZ)"""

        preset = config["compression_level"]

        with tarfile.open(output_path, "w:xz", preset=preset) as tar:
            if os.path.isfile(source_path):
                tar.add(source_path, arcname=os.path.basename(source_path))
            else:
                tar.add(source_path, arcname=os.path.basename(source_path))

        return output_path

    def _get_size(self, path: str) -> int:
        """Get total size of file or directory"""

        if os.path.isfile(path):
            return os.path.getsize(path)

        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass  # Skip files that can't be accessed

        return total_size

    def _analyze_file_types(self, path: str) -> List[str]:
        """Analyze file types in source"""

        file_types = set()

        if os.path.isfile(path):
            file_type = self._classify_file_type(path)
            file_types.add(file_type)
        else:
            # Analyze directory contents
            for root, dirs, files in os.walk(path):
                for file in files[:100]:  # Limit analysis to first 100 files
                    file_path = os.path.join(root, file)
                    file_type = self._classify_file_type(file_path)
                    file_types.add(file_type)

        return list(file_types)

    def _classify_file_type(self, file_path: str) -> str:
        """Classify file type for compression optimization"""

        _, ext = os.path.splitext(file_path.lower())

        text_extensions = {
            ".txt",
            ".md",
            ".json",
            ".xml",
            ".csv",
            ".log",
            ".yaml",
            ".yml",
        }
        code_extensions = {
            ".js",
            ".ts",
            ".py",
            ".java",
            ".cpp",
            ".h",
            ".css",
            ".html",
            ".php",
            ".rb",
            ".go",
            ".rs",
        }
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
        binary_extensions = {".exe", ".dll", ".so", ".dylib", ".bin"}
        archive_extensions = {".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z"}

        if ext in text_extensions:
            return "text"
        elif ext in code_extensions:
            return "code"
        elif ext in image_extensions:
            return "image"
        elif ext in binary_extensions:
            return "binary"
        elif ext in archive_extensions:
            return "archive"
        else:
            # Try to determine by content (simplified)
            try:
                with open(file_path, "rb") as f:
                    sample = f.read(1024)

                # Check if it's text (most bytes are printable)
                try:
                    sample.decode("utf-8")
                    printable_ratio = sum(32 <= b <= 126 for b in sample) / len(sample)
                    if printable_ratio > 0.7:
                        return "text"
                except UnicodeDecodeError:
                    pass

                return "binary"

            except (OSError, IOError):
                return "unknown"

    async def _record_optimization(
        self,
        source_path: str,
        method: str,
        compression_ratio: float,
        processing_time: float,
    ) -> None:
        """Record optimization for analysis"""

        record = {
            "timestamp": datetime.now(),
            "source_path": source_path,
            "method": method,
            "compression_ratio": compression_ratio,
            "processing_time": processing_time,
            "file_size": self._get_size(source_path),
            "file_types": self._analyze_file_types(source_path),
        }

        self.optimization_history.append(record)

        # Keep only recent history
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]

    async def benchmark_methods(self, test_file_path: str) -> Dict[str, CompressionResult]:
        """Benchmark all compression methods on a test file"""

        results = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            for method in self.compression_config["available_methods"].keys():
                try:
                    result = await self.optimize_compression(
                        test_file_path, temp_dir, {"compression_method": method}
                    )
                    results[method] = result
                except Exception as e:
                    results[method] = CompressionResult(
                        success=False,
                        original_size=0,
                        compressed_size=0,
                        compression_ratio=0.0,
                        compression_method=method,
                        output_path="",
                        processing_time=0.0,
                        savings_percentage=0.0,
                        error=str(e),
                    )

        return results

    def get_compression_stats(self) -> CompressionStats:
        """Get compression statistics"""

        if not self.optimization_history:
            return CompressionStats(
                files_processed=0,
                total_original_size=0,
                total_compressed_size=0,
                average_compression_ratio=0.0,
                best_method="",
                processing_time=0.0,
            )

        files_processed = len(self.optimization_history)
        total_original_size = sum(record["file_size"] for record in self.optimization_history)
        total_compressed_size = sum(
            int(record["file_size"] * record["compression_ratio"])
            for record in self.optimization_history
        )

        average_compression_ratio = (
            sum(record["compression_ratio"] for record in self.optimization_history)
            / files_processed
        )

        # Find best method by average compression ratio
        method_performance = {}
        for record in self.optimization_history:
            method = record["method"]
            if method not in method_performance:
                method_performance[method] = []
            method_performance[method].append(record["compression_ratio"])

        best_method = ""
        best_ratio = 1.0
        for method, ratios in method_performance.items():
            avg_ratio = sum(ratios) / len(ratios)
            if avg_ratio < best_ratio:
                best_ratio = avg_ratio
                best_method = method

        total_processing_time = sum(
            record["processing_time"] for record in self.optimization_history
        )

        return CompressionStats(
            files_processed=files_processed,
            total_original_size=total_original_size,
            total_compressed_size=total_compressed_size,
            average_compression_ratio=average_compression_ratio,
            best_method=best_method,
            processing_time=total_processing_time,
        )

    async def suggest_optimal_method(self, file_characteristics: Dict[str, Any]) -> str:
        """Suggest optimal compression method based on file characteristics"""

        size = file_characteristics.get("size", 0)
        file_types = file_characteristics.get("types", [])
        priority = file_characteristics.get("priority", "balanced")  # speed, size, balanced

        # Priority-based suggestions
        if priority == "speed":
            return "zip"
        elif priority == "size":
            if size > 50 * 1024 * 1024:  # > 50MB
                return "lzma"
            else:
                return "bz2"
        else:  # balanced
            if "text" in file_types or "code" in file_types:
                return "gzip"
            elif "binary" in file_types or "image" in file_types:
                return "zip"
            else:
                return "zip"  # Default

    def get_method_recommendations(self) -> Dict[str, str]:
        """Get method recommendations based on usage patterns"""

        if not self.optimization_history:
            return {
                "small_files": "zip",
                "large_files": "bz2",
                "text_files": "gzip",
                "mixed_content": "zip",
            }

        # Analyze history to provide data-driven recommendations
        size_performance = {"small": {}, "large": {}}
        type_performance = {}

        for record in self.optimization_history:
            method = record["method"]
            file_size = record["file_size"]
            ratio = record["compression_ratio"]

            # Size-based analysis
            size_category = "small" if file_size < 10 * 1024 * 1024 else "large"
            if method not in size_performance[size_category]:
                size_performance[size_category][method] = []
            size_performance[size_category][method].append(ratio)

            # Type-based analysis
            for file_type in record["file_types"]:
                if file_type not in type_performance:
                    type_performance[file_type] = {}
                if method not in type_performance[file_type]:
                    type_performance[file_type][method] = []
                type_performance[file_type][method].append(ratio)

        recommendations = {}

        # Find best methods for each category
        for size_cat, methods in size_performance.items():
            best_method = min(
                methods.items(),
                key=lambda x: sum(x[1]) / len(x[1]),
                default=("zip", [1.0]),
            )[0]
            recommendations[f"{size_cat}_files"] = best_method

        for file_type, methods in type_performance.items():
            best_method = min(
                methods.items(),
                key=lambda x: sum(x[1]) / len(x[1]),
                default=("zip", [1.0]),
            )[0]
            recommendations[f"{file_type}_files"] = best_method

        return recommendations
