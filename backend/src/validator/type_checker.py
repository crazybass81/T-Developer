"""
TypeChecker - Day 31
Type validation system for services
Size: ~6.5KB (optimized)
"""

from typing import Any, Callable, Dict, List, Type


class TypeChecker:
    """Validates types in service specifications"""

    def __init__(self):
        self.type_definitions = {}
        self.strict_mode = False
        self.validation_cache = {}
        self._init_builtin_types()

    def check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main type checking method"""
        # result = {"valid": True, "type_errors": [], "checked_fields": []}

        # Define expected schema for services
        schema = {
            "name": str,
            "version?": str,
            "agents?": list,
            "workflow?": dict,
            "constraints?": dict,
            "config?": dict,
        }

        return self.check_schema(data, schema)

    def check_field(self, value: Any, expected_type: Type) -> Dict[str, Any]:
        """Check single field type"""
        result = {
            "valid": True,
            "expected_type": expected_type.__name__,
            "actual_type": type(value).__name__,
        }

        if self.strict_mode:
            # Strict type checking
            if type(value) is not expected_type:
                result["valid"] = False
                result["error"] = f"Expected {expected_type.__name__}, got {type(value).__name__}"
        else:
            # Lenient type checking
            if not isinstance(value, expected_type):
                result["valid"] = False
                result["error"] = f"Expected {expected_type.__name__}, got {type(value).__name__}"

        return result

    def check_schema(self, data: Dict[str, Any], schema: Dict[str, Type]) -> Dict[str, Any]:
        """Check data against schema"""
        result = {"valid": True, "type_errors": [], "checked_fields": []}

        for field_name, expected_type in schema.items():
            # Handle optional fields
            is_optional = field_name.endswith("?")
            actual_field = field_name.rstrip("?")

            if is_optional and actual_field not in data:
                continue

            if not is_optional and actual_field not in data:
                result["valid"] = False
                result["type_errors"].append(f"Missing required field: {actual_field}")
                continue

            if actual_field in data:
                field_result = self.check_field(data[actual_field], expected_type)
                result["checked_fields"].append(actual_field)

                if not field_result["valid"]:
                    result["valid"] = False
                    result["type_errors"].append(f"Field '{actual_field}': {field_result['error']}")

        return result

    def check_union_type(self, value: Any, types: List[Type]) -> Dict[str, Any]:
        """Check if value matches any of the union types"""
        result = {"valid": False, "matched_type": None}

        for typ in types:
            check = self.check_field(value, typ)
            if check["valid"]:
                result["valid"] = True
                result["matched_type"] = typ.__name__
                break

        if not result["valid"]:
            result[
                "error"
            ] = f"Value doesn't match any type in union: {[t.__name__ for t in types]}"

        return result

    def check_array_elements(self, array: List[Any], element_type: Type) -> Dict[str, Any]:
        """Check all elements in array have same type"""
        result = {"valid": True, "invalid_indices": []}

        for i, element in enumerate(array):
            check = self.check_field(element, element_type)
            if not check["valid"]:
                result["valid"] = False
                result["invalid_indices"].append(i)

        return result

    def check_recursive(
        self, data: Any, max_depth: int = 10, current_depth: int = 0
    ) -> Dict[str, Any]:
        """Recursively validate nested structures"""
        result = {"valid": True, "max_depth_reached": current_depth + 1}

        if current_depth >= max_depth:
            result["error"] = "Maximum recursion depth reached"
            return result

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    nested_result = self.check_recursive(value, max_depth, current_depth + 1)
                    if nested_result["max_depth_reached"] > result["max_depth_reached"]:
                        result["max_depth_reached"] = nested_result["max_depth_reached"]
                    if not nested_result.get("valid", True):
                        result["valid"] = False

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    nested_result = self.check_recursive(item, max_depth, current_depth + 1)
                    if nested_result["max_depth_reached"] > result["max_depth_reached"]:
                        result["max_depth_reached"] = nested_result["max_depth_reached"]
                    if not nested_result.get("valid", True):
                        result["valid"] = False

        return result

    def define_type(self, name: str, validator: Callable[[Any], bool]) -> None:
        """Define custom type with validator function"""
        self.type_definitions[name] = validator

    def check_custom_type(self, value: Any, type_name: str) -> Dict[str, Any]:
        """Check value against custom type"""
        result = {"valid": False, "type": type_name}

        if type_name in self.type_definitions:
            validator = self.type_definitions[type_name]
            try:
                result["valid"] = validator(value)
                if not result["valid"]:
                    result["error"] = f"Value doesn't match custom type: {type_name}"
            except Exception as e:
                result["error"] = f"Validation error: {str(e)}"
        else:
            result["error"] = f"Unknown custom type: {type_name}"

        return result

    def coerce(self, value: Any, target_type: Type) -> Dict[str, Any]:
        """Try to coerce value to target type"""
        result = {"success": False, "value": None}

        try:
            if target_type == int:
                result["value"] = int(value)
                result["success"] = True
            elif target_type == float:
                result["value"] = float(value)
                result["success"] = True
            elif target_type == str:
                result["value"] = str(value)
                result["success"] = True
            elif target_type == bool:
                result["value"] = bool(value)
                result["success"] = True
        except (ValueError, TypeError) as e:
            result["error"] = str(e)

        return result

    def infer_schema(self, data: Dict[str, Any]) -> Dict[str, Type]:
        """Infer type schema from data"""
        schema = {}

        for key, value in data.items():
            schema[key] = type(value)

        return schema

    def set_strict_mode(self, strict: bool) -> None:
        """Set strict type checking mode"""
        self.strict_mode = strict

    def generate_report(self, result: Dict[str, Any]) -> str:
        """Generate type checking report"""
        report = f"""
Type Check Report
=================
Valid: {result.get('valid', False)}
Checked Fields: {len(result.get('checked_fields', []))}
Type Errors: {len(result.get('type_errors', []))}
"""

        if result.get("type_errors"):
            report += "\nErrors:\n"
            for error in result["type_errors"]:
                report += f"  - {error}\n"

        return report

    def _init_builtin_types(self) -> None:
        """Initialize built-in custom types"""
        # Size constraint for agents
        self.define_type("AgentSize", lambda x: isinstance(x, (int, float)) and 0 < x <= 6.5)

        # Instantiation time constraint
        self.define_type(
            "InstantiationTime", lambda x: isinstance(x, (int, float)) and 0 < x <= 3.0
        )

        # Percentage type
        self.define_type("Percentage", lambda x: isinstance(x, (int, float)) and 0 <= x <= 100)
