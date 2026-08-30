# OpenCode AI Agents

AI agents to be used in tandem with the OpenCode UI and locally downloaded LLM models
---

**Agent List**

- Transcription Factor Interaction Agent
- Whisper Voice to Text Transcription Agent

## Usage Guide

### 1. OpenCode Configurations

Make sure that the URLs within the opencode.json file matches with the IP address of the remote connection that houses the local LLM models. Once the json file is up to date, copy the file to your local OpenCode config folder (ie ~/.config/opencode). 

### 2. Setup for the Agents

Within your OpenCode config directory (ie ~/.config/opencode), create a new folder named "tools". 

For the TF interaction Agent, ensure that the directory to the local download of the TRRUST database in "query-local-trrust-database.ts" matches to the location of the database within your personal computer. Once the directory is correct in the typescript script, copy "query_trrust.py" and "query-local-trrust-database.ts" to the "tools" folder within the OpenCode config directory (ie ~/.config/opencode/tools). 

For the Whisper Voice to Text Agent, copy the "whispr.py" and "whispr.ts" files to the "tools" folder within the OpenCode config directory (ie ~/.config/opencode/tools). The "whisper_server_base.py" and "whisper_server_turbo.py" files should already be in the home directory of the TruongLab Mac Studio. 

### 3. Implementation of TF Interaction Agent

First, ensure that the Gemma 4 4bit model is running on the TruongLab Mac Studio. Once confirmed, start up OpenCode on your personal computer and click tab on your keyboard until the TF interaction Agent is chosen. Enter your query about a gene or transcription factor that was expressed and wait for a response. 

For instructions on how to start up the Gemma 4 4bit model on the TruongLab Mac Studio, refer to the TruongLab AI Master Doc.

### 4. Implementation of the Whisper Agent

Start up the Whisper model by executing the following command within the TruongLab Mac Studio via remote connection:
- uvicorn whisper_server_base:app --host 100.X.X.X --port 8085
Replace the IP address with the IP address of the TruongLab Mac Studio, and the "whisper_server_base" can be switched to "whisper_server_turbo" depending on which Whisper model you want to use.

Once the Whisper model has been started up, start up OpenCode on your personal computer. Since this agent is a subagent, you have to invoke this agent by typing an "@" symbol in a prompt. This means that this Whisper subagent can be invoked within any primary agent that is configured for your OpenCode. After invoking the subagent within the prompt, the query should include the path to an audio file that you want transcribed. 
- Example Query: "@whisper_voice_to_text_agent transcribe the following audio file for me: /path/to/audio/file/recording"
