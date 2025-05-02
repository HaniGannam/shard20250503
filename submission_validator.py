import json
import sys
import os
import jsonschema
from typing import Dict, Any, Tuple, List, Callable, Optional
from functools import partial

def load_json_file(file_path: str) -> Dict[Any, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)

def validate_against_schema(data: Dict[Any, Any], schema: Dict[Any, Any]) -> Tuple[bool, Optional[List[str]]]:
    """Validate data against a JSON schema."""
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]

def validate_crypto_specific(data: Dict[Any, Any]) -> Tuple[bool, List[str]]:
    """Validate crypto-specific requirements."""
    warnings = []
    errors = []
    
    # Check required fields for crypto servers
    if "fee_structure" not in data:
        errors.append("Crypto servers must include fee_structure")
    
    if "supported_blockchains" not in data or not data.get("supported_blockchains"):
        errors.append("Crypto servers must specify supported_blockchains")
    
    # Check for warnings
    if data.get("fee_structure", {}).get("fee_enabled") is False:
        warnings.append("Warning: Crypto server has fee_enabled set to false")
    
    return len(errors) == 0, errors + warnings

def validate_standard_specific(data: Dict[Any, Any]) -> Tuple[bool, List[str]]:
    """Validate standard-specific requirements and warnings."""
    warnings = []
    
    # Check for warnings for standard servers
    if data.get("fee_structure", {}).get("fee_enabled") is True:
        warnings.append("Warning: Standard server has fee_enabled set to true - verify if this should be a crypto server")
    
    if data.get("supported_blockchains"):
        warnings.append("Warning: Standard server specifies supported_blockchains - verify if this should be a crypto server")
    
    return True, warnings  # Standard servers only have warnings, no errors

def validate_endpoints(data: Dict[Any, Any]) -> Tuple[bool, List[str]]:
    """Validate endpoint configuration."""
    warnings = []
    errors = []
    
    endpoints = data.get("endpoints", {})
    
    # Check that invoke_path starts with a slash
    invoke_path = endpoints.get("invoke_path", "")
    if not invoke_path.startswith("/"):
        errors.append("Endpoint invoke_path must start with a slash (/)")
    
    # Construct full invoke URL for checking
    base_url = endpoints.get("base_url", "").rstrip("/")
    full_url = f"{base_url}{invoke_path}"
    
    # Check for best practices (as warnings, not errors)
    if "version" not in invoke_path and "v" not in invoke_path:
        warnings.append("Warning: Consider including a version in your invoke_path (e.g., /v1/invoke)")
    
    # Provide informational output about the constructed endpoint
    print(f"📌 Full invoke endpoint: {full_url}")
    
    return len(errors) == 0, errors + warnings

def apply_type_specific_validation(data: Dict[Any, Any]) -> Tuple[bool, List[str]]:
    """Apply validation specific to server type."""
    server_type = data.get("server_type", "standard")
    
    if server_type == "crypto":
        print("⚠️ Validating crypto-specific requirements...")
        return validate_crypto_specific(data)
    else:
        return validate_standard_specific(data)

def print_validation_results(is_valid: bool, messages: List[str]) -> None:
    """Print validation results."""
    for message in messages:
        if message.startswith("Warning"):
            print(f"⚠️ {message}")
        else:
            print(f"❌ {message}")
    
    if is_valid:
        print("✅ Validation passed!")
    else:
        print("❌ Validation failed!")

def validate_mcp_server_entry(entry_path: str, schema_path: str) -> int:
    """Validate an MCP server entry against the schema."""
    # Load files
    schema = load_json_file(schema_path)
    data = load_json_file(entry_path)
    
    # Validate base schema
    schema_valid, schema_errors = validate_against_schema(data, schema)
    
    if not schema_valid:
        print("❌ Entry validation failed against schema:")
        for error in schema_errors:
            print(f"  - {error}")
        return 1
    
    print("✅ Entry is valid according to the base schema!")
    
    # Validate endpoints
    print("\nChecking endpoint configuration...")
    endpoints_valid, endpoint_messages = validate_endpoints(data)
    if endpoint_messages:
        print_validation_results(endpoints_valid, endpoint_messages)
    
    # Apply additional type-specific validation
    print("\nChecking server type-specific requirements...")
    type_valid, type_messages = apply_type_specific_validation(data)
    if type_messages:
        print_validation_results(type_valid, type_messages)
    
    # Final result
    print("\nFinal validation result:")
    if schema_valid and endpoints_valid and type_valid:
        print("✅ Entry validation complete and successful!")
        return 0
    else:
        print("❌ One or more validation checks failed!")
        return 1

def main() -> int:
    """Main entry point for the validator."""
    if len(sys.argv) != 2:
        print("Usage: python submission_validator.py <entry_json_path>")
        return 1
    
    entry_path = sys.argv[1]
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "submission_schema.json")
    
    return validate_mcp_server_entry(entry_path, schema_path)

if __name__ == "__main__":
    sys.exit(main())
