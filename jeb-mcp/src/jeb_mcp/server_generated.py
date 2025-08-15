# NOTE: This file has been automatically generated, do not modify!
# Architecture based on https://github.com/mrexodia/ida-pro-mcp (MIT License)
from typing import Annotated, Optional, TypedDict, Generic, TypeVar
from pydantic import Field

T = TypeVar("T")

@mcp.tool()
def ping() -> str:
    """Do a simple ping to check server is alive and running"""
    return make_jsonrpc_request('ping')

@mcp.tool()
def get_manifest(filepath: str) -> str:
    """Get the manifest of the given APK file in path, the passed in filepath needs to be a fully-qualified absolute path"""
    return make_jsonrpc_request('get_manifest', filepath)

@mcp.tool()
def get_all_exported_activities(filepath: str) -> list[str]:
    """
    Get all exported activity names from the APK manifest.

    This includes activities with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request('get_all_exported_activities', filepath)

@mcp.tool()
def get_exported_activities_count(filepath: str) -> int:
    """
    Get exported activities count from the APK manifest.

    This includes activities with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request('get_exported_activities_count', filepath)

@mcp.tool()
def get_an_exported_activity_by_index(filepath: str, index: int) -> str:
    """
    Get an exported activity name by index from the APK manifest.

    This includes activities with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request('get_an_exported_activity_by_index', filepath, index)

@mcp.tool()
def get_method_decompiled_code(filepath: str, method_signature: str) -> str:
    """Get the decompiled code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
        
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z

    @param filepath: the path to the APK file
    @param method_signature: the fully-qualified method signature to decompile, e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_method_decompiled_code', filepath, method_signature)

@mcp.tool()
def get_class_decompiled_code(filepath: str, class_signature: str) -> str:
    """Get the decompiled code of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:

    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z

    @param: filepath: The path to the APK file
    @param: class_signature: The fully-qualified signature of the class to decompile, e.g. Lcom/abc/Foo;
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_class_decompiled_code', filepath, class_signature)

@mcp.tool()
def get_method_callers(filepath: str, method_signature: str) -> list[(str,str)]:
    """
    Get the callers of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_method_callers', filepath, method_signature)

@mcp.tool()
def get_method_overrides(filepath: str, method_signature: str) -> list[(str,str)]:
    """
    Get the overrides of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_method_overrides', filepath, method_signature)
    
@mcp.tool()
def get_superclass(filepath: str, class_signature: str) -> str:
    """
    Get the superclass of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_superclass', filepath, class_signature)

@mcp.tool()
def get_interfaces(filepath: str, class_signature: str) -> list[str]:
    """
    Get the interfaces of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_interfaces', filepath, class_signature)

@mcp.tool()
def get_class_methods(filepath: str, class_signature: str) -> list[str]:
    """
    Get the methods of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_class_methods', filepath, class_signature)

@mcp.tool()
def get_class_fields(filepath: str, class_signature: str) -> list[str]:
    """
    Get the fields of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_class_fields', filepath, class_signature)
