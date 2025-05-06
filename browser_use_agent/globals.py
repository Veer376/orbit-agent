"""Global state shared between modules to avoid circular imports."""

import sys
import threading

# Global reference to the browser controller - will be set by runner.py
# and used by tools.py without creating a circular dependency
BROWSER_CONTROLLER = None

def check_browser_controller():
    """Diagnostic function to check the status of BROWSER_CONTROLLER variable."""
    global BROWSER_CONTROLLER
    
    print(f"[GLOBALS] BROWSER_CONTROLLER exists: {BROWSER_CONTROLLER is not None}")
    print(f"[GLOBALS] BROWSER_CONTROLLER type: {type(BROWSER_CONTROLLER)}")
    print(f"[GLOBALS] Current thread: {threading.current_thread().name}")
    print(f"[GLOBALS] Module name: {__name__}")
    print(f"[GLOBALS] Module id: {id(sys.modules[__name__])}")
    
    return BROWSER_CONTROLLER is not None

def get_browser_controller():
    """Get the current browser controller instance.
    This function should be used instead of direct importing to avoid module caching issues.
    """
    global BROWSER_CONTROLLER
    return BROWSER_CONTROLLER