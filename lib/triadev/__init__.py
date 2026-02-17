# TriadDev - Golden Triangle Development Workflow
"""
TriadDev (三元开发) integrates the three essential OpenClaw skills:
- planning-with-files
- task-workflow  
- tdd-sdd-development
"""

__version__ = "1.0.0"
__author__ = "Galatea"
__homepage__ = "https://github.com/Charpup/triadev"

from .orchestrator import TriadDevOrchestrator, ProjectConfig
from .cli import main

__all__ = [
    'TriadDevOrchestrator',
    'ProjectConfig',
    'main',
]