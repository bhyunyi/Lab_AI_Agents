"""
title: Gemma 4 TF Interaction Agent
author: Bryan
version: 0.1
requirements: pandas, sqlalchemy
"""


### Valves and Pipes are openWEBUI architecture.
### ChatOpenAI() is LangChain's universal way of interfacing with any API that mimics OpenAI's endpoint style
### (including Ollama, vLLM, LiteLLM, LM Studio, and Groq). You can use ChatOpenAI() in standalone scripts,
### discord bots, or command-line apps without Open WebUI.


import json
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Union, Generator, Iterator, Optional

# Import LangChain Core components
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Import database packages
from sqlalchemy import create_engine, text


class Pipeline:
    # Valves are the configuration inputs for custom Pipes, Filters, or Tools
    class Valves(BaseModel):
        # URL destination where your application sends its API requests.
        api_base: str = (
            Field(  ##Field function comes from pydantic package to define metadata
                default="http://100.XX.XX.XX:8084/v1",
                description="The local Ollama server address running on your desktop.",  # Ollama is a free,
                # open-source application that allows you to download and run large language models (LLMs) locally on your own computer
            )
        )
        # password or authorization token to authenticate your account and track billing
        api_key: str = Field(
            default="ollama-local",
            description="Ollama bypass key (can be any string text).",
        )
        # Model name must match what comes up in the desktop when you put the command "ollama list"
        model_name: str = Field(
            default="/Users/Shared/models/mlx/gemma-4-31B-it-qat-OptiQ-4bit",
            description="The model identifier tag. Set to gemma4:31b or gemma4:26b as shown in 'ollama list'.",
        )
        # hidden set of core guidelines given to an AI model before the user ever types a message.
        # It acts as the AI's "job description" or behavioral blueprint, setting rules that persist through the entire chat session.
        SYSTEM_PROMPT: str = Field(
            default="You are a precise local AI assistant driven by Google Gemma 4 tasked with finding crucial Transcription Factor interactions. Use your tools and databases when needed. You need to find other factors that are stimulated when given transcription factor stimulation circuits.",
            description="The core context instruction set for Gemma 4.",
        )

        # initialize the TRRUST database file path
        TRRUST_FILE_PATH: str = Field(
            default="/app/backend/data/trrust_rawdata.human.tsv",
            description="The absolute path to your downloaded TRRUST flat file (.tsv) on your system.",
        )

    def __init__(self):
        self.valves = self.Valves()
        self._trrust_df = None

    def _get_trrust_df(self):
        """Loads and caches the TRRUST TSV so it's only read/parsed once per pipeline instance."""
        if self._trrust_df is None:
            import os
            file_path = self.valves.TRRUST_FILE_PATH
            if not os.path.exists(file_path):
                return None
            self._trrust_df = pd.read_csv(
                file_path,
                sep="\t",
                header=None,
                names=["Transcription_Factor", "Target_Gene", "Mode", "PubMed_ID"],
            )
        return self._trrust_df

    # Adds the dynamic model selection name to the UI dashboard dropdown.
    # Allows the custom pipeline to be selectable in openWEBUI interface.
    def pipes(self) -> List[dict]:
        return [
            {
                "id": "gemma4_TF_interaction_agent_pipe",
                "name": f"Gemma 4 TF Interaction Agent ({self.valves.model_name})",
            }
        ]

    # Execution function called upon submitting messages
    # core execution function of openWEBUI pipeline
    # function runs asynchronously or can pause execution while other things run to not create bottleneck
    # body is a dict with the current chat session from webUI
    # the Union function specifies what the function is allowed to return
    # str = single complete block of text. prints answer all at once
    # Generator/iterator = streams the response word-by-wrod in real time
    async def pipe(self, model_id: str, messages: list, **kwargs) -> Union[str, Generator, Iterator]:
    # 1. Reconstruct the body dictionary using the incoming arguments
        body = {
            "model": model_id,
            "messages": messages,
            **kwargs # Captures any extra fields like temperature, max_tokens, etc.
        }
        # This extracts the full convo history
        messages = body.get("messages", [])
        langchain_messages = []

        # Format the system prompt if provided
        if self.valves.SYSTEM_PROMPT:
            # SystemMessage is a class provided by LangChain
            # SystemMessage defines the rules, identity, constraints for AI
            langchain_messages.append(SystemMessage(content=self.valves.SYSTEM_PROMPT))

        # Parse history arrays into explicit LangChain message formats
        for msg in messages:
            # role can be the user or the AI assistant
            role = msg.get("role")
            content = msg.get("content")

            # Filter out internal thinking blocks from history to save context space
            # The message content will start with "<|channel>thought" if it is from thinking channel
            # HumanMessage and AIMessage will format the message
            # System: role = "system"
            # Human: role = "user"
            # AI: role = "assistant"
            if content and not str(content).startswith("<|channel>thought"):
                if role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))

        # --- STEP A: TRRUST database connection ---
        @tool
        def query_local_trrust_database(gene_symbol: str) -> str:
            """
            Queries your local TRRUST database file to find regulatory relationships for a gene.
            Use this tool whenever the user asks about transcription factors, gene targets,
            or interaction mechanisms (activation/repression) for a specific gene.

            :param gene_symbol: The standard uppercase gene name or symbol (e.g., 'TP53', 'MYC', 'STAT3').
            :return: A formatted text string containing matching interaction records or a warning message.
            """
            df = self._get_trrust_df()

            if df is None:
                return f"Error: TRRUST file not found at {self.valves.TRRUST_FILE_PATH}. Please verify the path in Open WebUI settings."

            try:
                search_term = str(gene_symbol).strip().upper()

                matches = df[
                    (df["Transcription_Factor"] == search_term)
                    | (df["Target_Gene"] == search_term)
                ]

                if matches.empty:
                    return f"No regulatory data found in the local TRRUST file for the gene symbol: '{search_term}'."

                output_lines = [
                    f"Found {len(matches)} TRRUST regulatory records for '{search_term}':"
                ]
                for _, row in matches.iterrows():
                    line = f"- TF: {row['Transcription_Factor']} | Target: {row['Target_Gene']} | Mode: {row['Mode']} (PubMed: {row['PubMed_ID']})"
                    output_lines.append(line)

                return "\n".join(output_lines)

            except Exception as e:
                return f"An error occurred while scanning the local file: {str(e)}"

        # --- STEP B: Package All Tools into a List ---
        tools_list = [query_local_trrust_database]

        # Create a dictionary map for quick execution retrieval later
        tools_map = {tool.name: tool for tool in tools_list}

        try:
            # Instantiate client utilizing Google's recommended Gemma 4 parameters
            llm = ChatOpenAI(
                openai_api_base=self.valves.api_base,
                openai_api_key=self.valves.api_key,
                model_name=self.valves.model_name,
                temperature=1.0,  # Official Gemma 4 baseline standard
                top_p=0.95,  # Recommended token nucleus sampling limit; top and temperature are set to values recommended by Google gemma
                streaming=False,
                timeout=300,       # seconds — tune to your model's real generation time
                max_retries=1,     # avoid silent retry loops on failure 
            )

            # Bind the tools list to the model instance so Gemma 4 knows its capabilities
            llm_with_tools = llm.bind_tools(tools_list)

            # Inject history cleanly using a chat prompt wrapper
            prompt = ChatPromptTemplate.from_messages(
                [MessagesPlaceholder(variable_name="chat_history")]
            )

            chain = prompt | llm_with_tools

            # Invoke the chain with current conversation history
            response_msg = chain.invoke({"chat_history": langchain_messages})

            # If Gemma 4 decides it needs tools to answer the user query:
            if response_msg.tool_calls:
                # Add Gemma 4's tool selection message to the conversation history context
                langchain_messages.append(response_msg)

                # Iterate through every tool request issued by the model
                for tool_call in response_msg.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call["id"]

                    # Fetch and run the corresponding python script
                    target_tool = tools_map.get(tool_name)
                    if target_tool:
                        # Handle either dictionary-unpacked arguments or empty arguments safely
                        tool_output = target_tool.invoke(tool_args)
                    else:
                        tool_output = f"Error: Tool '{tool_name}' was not found in the pipeline map."

                    # Append the tool's raw execution data back into LangChain's message chain
                    langchain_messages.append(
                        ToolMessage(content=str(tool_output), tool_call_id=tool_id)
                    )

                # Re-invoke the chain with the newly added tool result context to stream the final answer
                def stream_final_response():
                    for chunk in chain.stream({"chat_history": langchain_messages}):
                        if chunk.content:
                            yield chunk.content

                return stream_final_response()

            else:
                # If no tool calls were requested, simply output the standalone text response directly
                return response_msg.content

        except Exception as e:
            return f"Error executing local Gemma 4 agent pipeline: {str(e)}"
