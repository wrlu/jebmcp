# NOTE: This file has been automatically generated, do not modify!
# Architecture based on https://github.com/mrexodia/ida-pro-mcp (MIT License)
from typing import Annotated, TypeVar

T = TypeVar("T")


@mcp.tool()
def ping() -> str:
    """Do a simple ping to check server is alive and running"""
    return make_jsonrpc_request("ping")

@mcp.tool()
def get_manifest(filepath: Annotated[str, "full apk file path."]) -> str:
    """Get the manifest of the given APK file in path, the passed in filepath needs to be a fully-qualified absolute path"""
    return make_jsonrpc_request("get_manifest", filepath)

@mcp.tool()
def get_all_exported_activities(
    filepath: Annotated[str, "full apk file path."],
) -> list[str]:
    """
    Get all exported activity names from the APK manifest.

    This includes activities with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request("get_all_exported_activities", filepath)


@mcp.tool()
def get_all_exported_services(
    filepath: Annotated[str, "full apk file path."]) -> list[str]:
    """
    Get all exported service names from the APK manifest.

    This includes services with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request("get_all_exported_services", filepath)


@mcp.tool()
def get_method_decompiled_code(
    filepath: Annotated[str, "full apk file path."],
    method_signature: Annotated[
        str,
        "the method_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V",
    ],
) -> str:
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
    return make_jsonrpc_request(
        "get_method_decompiled_code", filepath, method_signature
    )


@mcp.tool()
def get_method_smali_code(
    filepath: Annotated[str, "full apk file path."], method_signature: Annotated[
        str,
        "the method_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V",
    ]
) -> str:
    """Get the smali code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
        
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z

    @param filepath: the path to the APK file
    @param method_signature: the fully-qualified method signature to decompile, e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request(
        "get_method_smali_code", filepath, method_signature
    )


@mcp.tool()
def get_method_callers(
    filepath: Annotated[str, "full apk file path."],
    method_signature: Annotated[
        str,
        "the method_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V",
    ],
) -> list[dict]:
    """
    Get the callers of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request(
        "get_method_callers", filepath, method_signature
    )


@mcp.tool()
def get_field_callers(
    filepath: Annotated[str, "full apk file path."],
    field_signature: Annotated[
        str,
        "the field_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->a",
    ],) -> list[dict]:
    """
    Get the callers of the given field in the APK file, the passed in field_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request(
        "get_field_callers", filepath, field_signature
    )


@mcp.tool()
def get_method_overrides(
    filepath: Annotated[str, "full apk file path."],
    method_signature: Annotated[
        str,
        "the method_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V",
    ],
) -> list[str]:
    """
    Get the overrides of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request(
        "get_method_overrides", filepath, method_signature
    )


@mcp.tool()
def get_superclass(
    filepath: Annotated[str, "full apk file path."],
    class_signature: Annotated[
        str, "fully-qualified signature of the class, e.g. Lcom/abc/Foo;"
    ],
) -> str:
    """
    Get the superclass of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request("get_superclass", filepath, class_signature)


@mcp.tool()
def get_interfaces(
    filepath: Annotated[str, "full apk file path."],
    class_signature: Annotated[
        str, "fully-qualified signature of the class, e.g. Lcom/abc/Foo;"
    ],
) -> list[str]:
    """
    Get the interfaces of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request("get_interfaces", filepath, class_signature)


@mcp.tool()
def get_class_methods(
    filepath: Annotated[str, "full apk file path."],
    class_signature: Annotated[
        str, "fully-qualified signature of the class, e.g. Lcom/abc/Foo;"
    ],
) -> list[str]:
    """
    Get the methods of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request("get_class_methods", filepath, class_signature)


@mcp.tool()
def get_class_fields(
    filepath: Annotated[str, "full apk file path."],
    class_signature: Annotated[
        str, "fully-qualified signature of the class, e.g. Lcom/abc/Foo;"
    ],
) -> list[str]:
    """
    Get the fields of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request("get_class_fields", filepath, class_signature)


@mcp.tool()
def rename_class_name(
    filepath: Annotated[str, "full apk file path"],
    class_signature: Annotated[
        str, "fully-qualified signature of the class, e.g. Lcom/abc/Foo;"
    ],
    new_class_name: Annotated[
        str,
        "the new name for java class name without package and type, e.g. 'MyNewClass'",
    ],
):
    """rename the given class in the APK file

    Args:
        filepath (str): full apk file path.
        class_signature (str): fully-qualified signature of the class, e.g. Lcom/abc/Foo;
        new_class_name (str): the new name for java class name without package and type, e.g. "MyNewClass"

    Returns:
        None
    """
    return make_jsonrpc_request(
        "rename_class_name", filepath, class_signature, new_class_name
    )


@mcp.tool()
def rename_method_name(
    filepath: Annotated[str, "full apk file path"],
    class_signature: Annotated[
        str, "fully-qualified signature of the class, e.g. Lcom/abc/Foo;"
    ],
    method_signature: Annotated[
        str,
        "the method_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V",
    ],
    new_method_name: Annotated[
        str,
        "the new name for java method name without parameters, e.g. 'myNewMethod'",
    ],
):
    """rename the given class method in the APK file

    Args:
        filepath (str): full apk file path.
        class_signature (str): fully-qualified signature of the class, e.g. Lcom/abc/Foo;
        method_signature (str): the method_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
        new_method_name (str): the new name for java method name without parameters, e.g. "myNewMethod"

    Returns:
        None
    """
    return make_jsonrpc_request(
        "rename_method_name",
        filepath,
        class_signature,
        method_signature,
        new_method_name,
    )


@mcp.tool()
def rename_class_field(
    filepath: Annotated[str, "full apk file path"],
    class_signature: Annotated[
        str, "fully-qualified signature of the class, e.g. Lcom/abc/Foo;"
    ],
    field_signature: Annotated[
        str,
        "the field_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->flag1:Z",
    ],
    new_field_name: Annotated[
        str, "the new name for java field name without type, e.g. 'myNewField'"
    ],
):
    """rename the given class field in the APK file

    Args:
        filepath (str): _description_
        class_signature (str): class_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;
        field_signature (str): the field_signature needs to be a fully-qualified signature e.g. Lcom/abc/Foo;->flag1:Z
        new_field_name (str): the new name for java field name without type, e.g. "myNewField"

    Returns:
        None
    """
    return make_jsonrpc_request(
        "rename_class_field",
        filepath,
        class_signature,
        field_signature,
        new_field_name,
    )

@mcp.tool()
def check_java_identifier(
    filepath: Annotated[str, "full apk file path"],
    identifier: Annotated[
        str,
        "the passed in identifier needs to be a fully-qualified name (like `com.abc.def.Foo`) or a signature;",
    ],) -> list[dict]:
    """
    Check an identifier in the APK file and recognize if this is a class, type, method or field.
    the passed in identifier needs to be a fully-qualified name (like `com.abc.def.Foo`) or a signature;
    the passed in filepath needs to be a fully-qualified absolute path;
    the return value will be a list to tell you the possible type of the passed identifier.
    """
    return make_jsonrpc_request("check_java_identifier", filepath, identifier)