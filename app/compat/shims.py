# app/compat/langchain_shims.py
import sys, types

# BaseCallbackHandler → langchain_core.callbacks.base
from langchain_core.callbacks.base import BaseCallbackHandler
m = types.ModuleType("langchain.callbacks.base")
m.BaseCallbackHandler = BaseCallbackHandler
sys.modules["langchain.callbacks.base"] = m

# Document → langchain_core.documents
from langchain_core.documents import Document
m = types.ModuleType("langchain.schema.document")
m.Document = Document
sys.modules["langchain.schema.document"] = m

# AgentAction / AgentFinish → langchain_core.agents
from langchain_core.agents import AgentAction, AgentFinish
m = types.ModuleType("langchain.schema.agent")
m.AgentAction = AgentAction
m.AgentFinish = AgentFinish
sys.modules["langchain.schema.agent"] = m