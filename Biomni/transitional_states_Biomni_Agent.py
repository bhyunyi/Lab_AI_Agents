#!/usr/bin/env python3
"""
transitional_states_Biomni_Agent.py

Usage:
    python3 transitional_states_Biomni_Agent.py <PROMPT> <UNIQUE_IDENTIFIER>
"""

import sys
import os
from biomni.agent import A1

tools_dir = os.path.abspath("path/to/Database_Query_Scripts")
if tools_dir not in sys.path:
    sys.path.append(tools_dir)


from query_cellmarker import query_local_cellmarker_database
from query_TFMarker import query_local_TFMarker_database
from query_trrust import query_local_trrust_database

agent = A1(
    path = "path/to/biomni/data", 
    llm = "llm_name", 
    source = "Custom",
    base_url = "", 
    api_key = "")

agent.add_tool(query_local_cellmarker_database)
agent.add_tool(query_local_TFMarker_database)
agent.add_tool(query_local_trrust_database)

if len(sys.argv) != 3:
    sys.exit(
        "Usage: python transitional_states_Biomni_Agent.py "
        "'PROMPT' UNIQUE_IDENTIFIER"
    )

prompt = sys.argv[1]
identifier = sys.argv[2]

agent.go(prompt)

agent.save_conversation_history(f"path/to/history/directory/{identifier}_Biomni_results.pdf")