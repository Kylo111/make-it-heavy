#!/usr/bin/env python3
"""
Wrapper script to run the Universal Agent with a single query.
This script is designed to be called from external applications.
"""

import argparse
import sys
from agent import UniversalAgent

def main():
    """Main entry point for running agent with a single query"""
    parser = argparse.ArgumentParser(description='Run Universal Agent with a single query')
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Configuration file path (default: config.yaml)')
    parser.add_argument('--query', '-q', required=True,
                       help='Query to send to the agent')
    args = parser.parse_args()
    
    try:
        # Initialize agent (suppress all output during initialization)
        import contextlib
        import io

        # Capture all output during initialization
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            agent = UniversalAgent(config_path=args.config)

        # Capture agent output during run
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            response = agent.run(args.query)

        # Print only the clean response
        print(response)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
