import os
import sys

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from ui.audit_app import main


if __name__ == "__main__":
    main()
    
    
    