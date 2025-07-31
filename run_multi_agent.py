#!/usr/bin/env python3
"""
Wrapper script to run the Multi-Agent Orchestrator with a single query.
This script allows non-interactive execution of the orchestrator.
"""

import argparse
import sys
import contextlib
import io
from make_it_heavy import OrchestratorCLI


def main():
    parser = argparse.ArgumentParser(description='Run Multi-Agent Orchestrator with a single query')
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Configuration file path (default: config.yaml)')
    parser.add_argument('--query', '-q', required=True,
                       help='Query to send to the orchestrator')
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator (suppress all output during initialization)
        import contextlib
        import io
        
        # Capture all output during initialization
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cli = OrchestratorCLI(config_path=args.config)

        # Capture orchestrator output during run
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            # Run the task
            result = cli.run_task(args.query)
        
        # Print only the clean result
        if result:
            print(result)
        else:
            print("Task failed - no result returned")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
