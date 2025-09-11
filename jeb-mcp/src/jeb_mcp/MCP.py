# -*- coding: utf-8 -*-
import sys
import time
import json
import struct
import threading
import traceback
import os

# A module that helps with writing thread safe ida code.
# Based on:
# https://web.archive.org/web/20160305190440/http://www.williballenthin.com/blog/2015/09/04/idapython-synchronization-decorator/
import logging
import traceback
import functools

# Python 2.7 changes - use urlparse from urlparse module instead of urllib.parse
from urlparse import urlparse
# Python 2.7 doesn't have typing, so we'll define our own minimal substitutes
# and ignore most type annotations
import Queue as queue  # Python 2.7 uses Queue instead of queue
# Use BaseHTTPServer instead of http.server
import BaseHTTPServer


from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.util import DecompilerHelper

from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import JebCoreService, ICoreContext, Artifact, RuntimeProjectUtil

from com.pnfsoftware.jeb.core.input import FileInput
from com.pnfsoftware.jeb.core.units import INativeCodeUnit
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit
from com.pnfsoftware.jeb.core.output.text import TextDocumentUtil
from com.pnfsoftware.jeb.core.units.code.asm.decompiler import INativeSourceUnit
from com.pnfsoftware.jeb.core.actions import ActionXrefsData, Actions, ActionContext, ActionOverridesData
from java.io import File

# Mock typing classes/functions for type annotation compatibility
class Any(object): pass
class Callable(object): pass
def get_type_hints(func):
    """Mock for get_type_hints that works with Python 2.7 functions"""
    hints = {}
    
    # Try to get annotations (modern Python way)
    if hasattr(func, '__annotations__'):
        hints.update(getattr(func, '__annotations__', {}))
    
    # For Python 2.7, inspect the function signature
    import inspect
    args, varargs, keywords, defaults = inspect.getargspec(func)
    
    # Add all positional parameters with Any type
    for arg in args:
        if arg not in hints:
            hints[arg] = Any
            
    return hints
class TypedDict(dict): pass
class Optional(object): pass
class Annotated(object): pass
class TypeVar(object): pass
class Generic(object): pass


class JSONRPCError(Exception):
    def __init__(self, code, message, data=None):
        Exception.__init__(self, message)
        self.code = code
        self.message = message
        self.data = data

class RPCRegistry(object):
    def __init__(self):
        self.methods = {}

    def register(self, func):
        self.methods[func.__name__] = func
        return func

    def dispatch(self, method, params):
        if method not in self.methods:
            raise JSONRPCError(-32601, "Method '{0}' not found".format(method))

        func = self.methods[method]
        hints = get_type_hints(func)

        # Remove return annotation if present
        if 'return' in hints:
            hints.pop("return", None)

        if isinstance(params, list):
            if len(params) != len(hints):
                raise JSONRPCError(-32602, "Invalid params: expected {0} arguments, got {1}".format(len(hints), len(params)))

            # Python 2.7 doesn't support zip with items() directly
            # Convert to simpler validation approach
            converted_params = []
            param_items = hints.items()
            for i, value in enumerate(params):
                if i < len(param_items):
                    param_name, expected_type = param_items[i]
                    # In Python 2.7, we'll do minimal type checking
                    converted_params.append(value)
                else:
                    converted_params.append(value)

            return func(*converted_params)
        elif isinstance(params, dict):
            # Simplify type validation for Python 2.7
            if set(params.keys()) != set(hints.keys()):
                raise JSONRPCError(-32602, "Invalid params: expected {0}".format(list(hints.keys())))

            # Validate and convert parameters
            converted_params = {}
            for param_name, expected_type in hints.items():
                value = params.get(param_name)
                # Skip detailed type validation in Python 2.7 version
                converted_params[param_name] = value

            return func(**converted_params)
        else:
            raise JSONRPCError(-32600, "Invalid Request: params must be array or object")

rpc_registry = RPCRegistry()

def jsonrpc(func):
    """Decorator to register a function as a JSON-RPC method"""
    global rpc_registry
    return rpc_registry.register(func)

class JSONRPCRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def send_jsonrpc_error(self, code, message, id=None):
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        if id is not None:
            response["id"] = id
        response_body = json.dumps(response)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

    def do_POST(self):
        global rpc_registry

        parsed_path = urlparse(self.path)
        if parsed_path.path != "/mcp":
            self.send_jsonrpc_error(-32098, "Invalid endpoint", None)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_jsonrpc_error(-32700, "Parse error: missing request body", None)
            return

        request_body = self.rfile.read(content_length)
        try:
            request = json.loads(request_body)
        except ValueError:  # Python 2.7 uses ValueError instead of JSONDecodeError
            self.send_jsonrpc_error(-32700, "Parse error: invalid JSON", None)
            return

        # Prepare the response
        response = {
            "jsonrpc": "2.0"
        }
        if request.get("id") is not None:
            response["id"] = request.get("id")

        try:
            # Basic JSON-RPC validation
            if not isinstance(request, dict):
                raise JSONRPCError(-32600, "Invalid Request")
            if request.get("jsonrpc") != "2.0":
                raise JSONRPCError(-32600, "Invalid JSON-RPC version")
            if "method" not in request:
                raise JSONRPCError(-32600, "Method not specified")

            # Dispatch the method
            result = rpc_registry.dispatch(request["method"], request.get("params", []))
            response["result"] = result

        except JSONRPCError as e:
            response["error"] = {
                "code": e.code,
                "message": e.message
            }
            if e.data is not None:
                response["error"]["data"] = e.data
        except Exception as e:
            traceback.print_exc()
            response["error"] = {
                "code": -32603,
                "message": "Internal error (please report a bug)",
                "data": traceback.format_exc(),
            }

        try:
            response_body = json.dumps(response)
        except Exception as e:
            traceback.print_exc()
            response_body = json.dumps({
                "error": {
                    "code": -32603,
                    "message": "Internal error (please report a bug)",
                    "data": traceback.format_exc(),
                }
            })

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        # Suppress logging
        pass

class MCPHTTPServer(BaseHTTPServer.HTTPServer):
    allow_reuse_address = False

class Server(object):  # Use explicit inheritance from object for py2
    HOST = "127.0.0.1"
    PORT = 16161

    def __init__(self):
        self.server = None
        self.server_thread = None
        self.running = False

    def start(self):
        if self.running:
            print("[MCP] Server is already running")
            return

        # Python 2.7 doesn't support daemon parameter in Thread constructor
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True  # Set daemon attribute after creation
        self.running = True
        self.server_thread.start()

    def stop(self):
        if not self.running:
            return

        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join()
            self.server = None
        print("[MCP] Server stopped")

    def _run_server(self):
        try:
            # Create server in the thread to handle binding
            self.server = MCPHTTPServer((Server.HOST, Server.PORT), JSONRPCRequestHandler)
            print("[MCP] Server started at http://{0}:{1}".format(Server.HOST, Server.PORT))
            self.server.serve_forever()
        except OSError as e:
            if e.errno == 98 or e.errno == 10048:  # Port already in use (Linux/Windows)
                print("[MCP] Error: Port 13337 is already in use")
            else:
                print("[MCP] Server error: {0}".format(e))
            self.running = False
        except Exception as e:
            print("[MCP] Server error: {0}".format(e))
        finally:
            self.running = False


@jsonrpc
def ping():
    """Do a simple ping to check server is alive and running"""
    return "pong"

# implement a FIFO queue to store the artifacts
artifactQueue = list()

def addArtifactToQueue(artifact):
    """Add an artifact to the queue"""
    artifactQueue.append(artifact)

def getArtifactFromQueue():
    """Get an artifact from the queue"""
    if len(artifactQueue) > 0:
        return artifactQueue.pop(0)
    return None

def clearArtifactQueue():
    """Clear the artifact queue"""
    global artifactQueue
    artifactQueue = list()

MAX_OPENED_ARTIFACTS = 10

# 全局缓存，目前只缓存了exported_activities，加载新的apk文件时将被清除。
apk_cached_data = {}

def getOrLoadApk(filepath):
    engctx = CTX.getEnginesContext()

    if not engctx:
        print('Back-end engines not initialized')
        return

    if not os.path.exists(filepath):
        raise Exception("File not found: %s" % filepath)
    # Create a project
    project = engctx.loadProject('MCPPluginProject')
    correspondingArtifact = None
    for artifact in project.getLiveArtifacts():
        if artifact.getArtifact().getName() == filepath:
            # If the artifact is already loaded, return it
            correspondingArtifact = artifact
            break
    if not correspondingArtifact:
        # try to load the artifact, but first check if the queue size has been exceeded
        if len(artifactQueue) >= MAX_OPENED_ARTIFACTS:
            # unload the oldest artifact
            oldestArtifact = getArtifactFromQueue()
            if oldestArtifact:
                # unload the artifact
                oldestArtifactName = oldestArtifact.getArtifact().getName()
                print('Unloading artifact: %s because queue size limit exeeded' % oldestArtifactName)
                RuntimeProjectUtil.destroyLiveArtifact(oldestArtifact)

        # Fix: 直接用filepath而不是basename作为Artifact的名称，否则如果加载了多个同名不同路径的apk，会出现问题。
        correspondingArtifact = project.processArtifact(Artifact(filepath, FileInput(File(filepath))))
        addArtifactToQueue(correspondingArtifact)
        apk_cached_data.clear()
    
    unit = correspondingArtifact.getMainUnit()
    if isinstance(unit, IApkUnit):
        # If the unit is already loaded, return it
        return unit    
    return None


@jsonrpc
def get_manifest(filepath):
    """Get the manifest of the given APK file in path, note filepath needs to be an absolute path"""
    if not filepath:
        return None

    apk = getOrLoadApk(filepath)  # Fixed: use getOrLoadApk function to load the APK
    #get base name
    
    if apk is None:
        # if the input is not apk (e.g. a jar or single dex)
        # assume it runs in system context
        return None
    
    if 'manifest' in apk_cached_data:
        return apk_cached_data['manifest']
    
    man = apk.getManifest()
    if man is None:
        return None
    doc = man.getFormatter().getPresentation(0).getDocument()
    text = TextDocumentUtil.getText(doc)
    #engctx.unloadProjects(True)
    apk_cached_data['manifest'] = text
    return text


@jsonrpc
def get_all_exported_activities(filepath):
    """
    Get all exported Activity components from the APK and normalize their class names.

    An Activity is considered "exported" if:
    - It explicitly sets android:exported="true", or
    - It omits android:exported but includes an <intent-filter> (implicitly exported)

    Note:
    - If android:exported="false" is explicitly set, the Activity is NOT exported, even if it has intent-filters.

    Class name normalization rules:
    - If it starts with '.', prepend the package name (e.g., .MainActivity -> com.example.app.MainActivity)
    - If it has no '.', include both the original and package-prefixed versions
    - If it's a full class name, keep as-is

    Returns a list of fully qualified exported Activity class names (for use in decompilation, etc.)
    """
    if not filepath:
        return []
    

    
    from xml.etree import ElementTree as ET

    manifest_text = get_manifest(filepath).replace("&", "&amp;")

    if not manifest_text:
        return []
    
    # 首先尝试在缓存中取
    if 'exported_activities' in apk_cached_data:
        return apk_cached_data['exported_activities']
    
    try:
        root = ET.fromstring(manifest_text.encode('utf-8'))
    except Exception as e:
        print("[MCP] Error parsing manifest:", e)
        return []

    ANDROID_NS = 'http://schemas.android.com/apk/res/android'
    exported_activities = []

    # 获取包名
    package_name = root.attrib.get('package', '').strip()

    # 查找 <application> 节点
    app_node = root.find('application')
    if app_node is None:
        return []

    for activity in app_node.findall('activity'):
        name = activity.attrib.get('{' + ANDROID_NS + '}name')
        exported = activity.attrib.get('{' + ANDROID_NS + '}exported')
        has_intent_filter = len(activity.findall('intent-filter')) > 0

        if not name:
            continue

        if exported == "true" or (exported is None and has_intent_filter):
            normalized = set()

            if name.startswith('.'):
                normalized.add(package_name + name)
            elif '.' not in name:
                normalized.add(name)
                normalized.add(package_name + '.' + name)
            else:
                normalized.add(name)

            exported_activities.extend(normalized)
    # 缓存导出Activity数据
    apk_cached_data['exported_activities'] = exported_activities
    return exported_activities


@jsonrpc
def get_exported_activities_count(filepath):
    exported_activities = get_all_exported_activities(filepath)
    return len(exported_activities)


@jsonrpc
def get_an_exported_activity_by_index(filepath, index):
    exported_activities = get_all_exported_activities(filepath)
    if index >= 0 and index < len(exported_activities):
        return exported_activities[index]
    else:
        return None


@jsonrpc
def get_method_decompiled_code(filepath, method_signature):
    """Get the decompiled code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)
    decomp = DecompilerHelper.getDecompiler(codeUnit)
    if not decomp:
        print('Cannot acquire decompiler for unit: %s' % decomp)
        return None
    
    if method is None:
        print('[MCP] Class not found: %s' % method_signature)
        return None

    if not decomp.decompileMethod(method.getSignature()):
        print('Failed decompiling method')
        return None

    text = decomp.getDecompiledMethodText(method.getSignature())
    return text


@jsonrpc
def get_method_smali_code(filepath, method_signature):
    """Get the smali code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)
    
    if method is None:
        print('[MCP] Method not found: %s' % method_signature)
        return None

    instrustions = method.getInstructions()
    smali_code = ""
    for instrustion in instrustions:
        smali_code = smali_code + instrustion.format(None) + "\n"

    return smali_code


@jsonrpc
def get_class_decompiled_code(filepath, class_signature):
    """Get the decompiled code of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z
    note filepath needs to be an absolute path
    """
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        print('[MCP] Class not found: %s' % class_signature)
        return None

    decomp = DecompilerHelper.getDecompiler(codeUnit)
    if not decomp:
        print('Cannot acquire decompiler for unit: %s' % codeUnit)
        return None

    if not decomp.decompileClass(clazz.getSignature()):
        print('Failed decompiling class: %s' % class_signature)
        return None

    text = decomp.getDecompiledClassText(clazz.getSignature())
    return text


@jsonrpc
def get_method_callers(filepath, method_signature):
    """
    Get the callers of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    ret = []
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)
    if method is None:
        raise Exception("Method not found: %s" % method_signature)
    actionXrefsData = ActionXrefsData()
    actionContext = ActionContext(codeUnit, Actions.QUERY_XREFS, method.getItemId(), None)
    if codeUnit.prepareExecution(actionContext,actionXrefsData):
        for i in range(actionXrefsData.getAddresses().size()):
            ret.append({
                "address": actionXrefsData.getAddresses()[i],
                "details": actionXrefsData.getDetails()[i]
            })
    return ret


@jsonrpc
def get_field_callers(filepath, field_signature):
    """
    Get the callers of the given field in the APK file, the passed in field_signature needs to be a fully-qualified signature
    note filepath needs to be an absolute path
    """
    if not filepath or not field_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    ret = []
    codeUnit = apk.getDex()
    field = codeUnit.getField(field_signature)
    if field is None:
        raise Exception("Field not found: %s" % field_signature)
    actionXrefsData = ActionXrefsData()
    actionContext = ActionContext(codeUnit, Actions.QUERY_XREFS, field.getItemId(), None)
    if codeUnit.prepareExecution(actionContext,actionXrefsData):
        for i in range(actionXrefsData.getAddresses().size()):
            ret.append({
                "address": actionXrefsData.getAddresses()[i],
                "details": actionXrefsData.getDetails()[i]
            })
    return ret


@jsonrpc
def get_method_overrides(filepath, method_signature):
    """
    Get the overrides of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    ret = []
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)
    if method is None:
        raise Exception("Method not found: %s" % method_signature)
    data = ActionOverridesData()
    actionContext = ActionContext(codeUnit, Actions.QUERY_OVERRIDES, method.getItemId(), None)
    if codeUnit.prepareExecution(actionContext,data):
        for i in range(data.getAddresses().size()):
            ret.append(data.getAddresses()[i])
    return ret


@jsonrpc
def get_superclass(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None

    return clazz.getSupertypeSignature(True)


@jsonrpc
def get_interfaces(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None
    
    interfaces = []
    interfaces_array = clazz.getInterfaceSignatures(True)
    for interface in interfaces_array:
        interfaces.append(interface)

    return interfaces


@jsonrpc
def get_class_methods(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None
    
    method_signatures = []
    dex_methods = clazz.getMethods()
    for method in dex_methods:
        if method:
            method_signatures.append(method.getSignature(True))

    return method_signatures


@jsonrpc
def get_class_fields(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None
    
    field_signatures = []
    dex_field = clazz.getFields()
    for field in dex_field:
        if field:
            field_signatures.append(field.getSignature(True))

    return field_signatures


CTX = None
class MCP(IScript):

    def __init__(self):
        self.server = Server()
        print("[MCP] Plugin loaded")

    def run(self, ctx):
        global CTX  # Fixed: use global keyword to modify global variable
        CTX = ctx
        self.server.start()
        print("[MCP] Plugin running")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("Exiting...")

    def term(self):
        self.server.stop()
