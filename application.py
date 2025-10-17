#!/usr/bin/env python3
"""
AWS Elastic Beanstalk entry point for Daily Ritual AI Agent
"""

import sys
import os
from streamlit.web import cli as stcli

def main():
    """Main entry point for Elastic Beanstalk"""
    port = os.environ.get('PORT', '8501')
    sys.argv = [
        "streamlit", 
        "run", 
        "app.py", 
        f"--server.port={port}", 
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()