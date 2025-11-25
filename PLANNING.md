# Task 8: Simple AI Agent - Planning & Execution Overview

## 🎯 Task Summary

**Objective:** Build a user management agent from scratch with custom tools and DIAL API integration, without using frameworks.

**Repository:** ai-dial-simple-agent

**Completion Date:** November 25, 2025

**Key Components:**
1. Custom Tool System (5 CRUD tools + Web Search)
2. DIAL Client (Streaming + Tool Calling)
3. Tool Execution Loop (Recursive)
4. Agent Application (Interactive Chat)

---

## 🧠 Planning & Architecture

### Agent Architecture (Framework-less)

```
┌─────────────────────────────────────────┐
│          User Management Agent          │
│                                         │
│  ┌─────────────────┐   ┌─────────────┐ │
│  │  Conversation   │   │   System    │ │
│  │    History      │   │   Prompt    │ │
│  └────────┬────────┘   └──────┬──────┘ │
│           │                   │        │
│           └───────┬───────────┘        │
│                   ▼                    │
│           ┌──────────────┐             │
│           │ DIAL Client  │             │
│           │              │             │
│           │ • Streaming  │             │
│           │ • Tool Calls │             │
│           └──────┬───────┘             │
│                  │                     │
│        ┌─────────┴─────────┐           │
│        ▼                   ▼           │
│   ┌─────────┐        ┌─────────┐      │
│   │ Azure   │        │  Tools  │      │
│   │ OpenAI  │        │  Dict   │      │
│   │ (gpt4o) │        │         │      │
│   └─────────┘        └────┬────┘      │
│                           │           │
│                ┌──────────┴────────┐  │
│                ▼                   ▼  │
│         ┌──────────┐         ┌────────────┐
│         │Web Search│         │User Service│
│         │  Tool    │         │   Tools    │
│         └──────────┘         └────────────┘
│                                    │
└────────────────────────────────────┼──────┘
                                    ▼
                            ┌──────────────┐
                            │User Service  │
                            │(Docker:8041) │
                            └──────────────┘
```

---

## 💭 Key Design Decisions

### Decision 1: Why No Framework?

**Options:**
- LangChain: Full-featured, opinionated
- LlamaIndex: Document-focused
- Custom: Full control, learning opportunity

**Chose: Custom Implementation**

**Reasoning:**
- ✅ Educational value (understand internals)
- ✅ No hidden abstractions
- ✅ Full control over tool calling
- ✅ Minimal dependencies
- ❌ More code to write
- ❌ No built-in features (memory, etc.)

**Trade-off:** Learning vs Speed → Chose learning

---

### Decision 2: Tool System Design

**Base Tool Interface:**
```python
class BaseTool(ABC):
    @abstractmethod
    def execute(self, arguments: dict) -> str:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> dict:
        pass
    
    @property
    def schema(self) -> dict:
        """Converts to DIAL API format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }
```

**Reasoning:**
- Abstract base enforces contract
- `schema` property auto-converts to DIAL format
- Tools are self-documenting
- Easy to add new tools

---

### Decision 3: DIAL Client Architecture

**Streaming + Tool Calling:**
```python
class DialClient:
    def __init__(self, api_key, endpoint, tools, mcp_client):
        self.tools = tools  # Tool schemas for LLM
        self.mcp_client = mcp_client  # Executor
        self.openai = AsyncAzureOpenAI(...)
    
    async def get_completion(self, messages):
        # 1. Stream response from LLM
        ai_message = await self._stream_response(messages)
        
        # 2. Check for tool calls
        if ai_message.tool_calls:
            messages.append(ai_message)
            await self._call_tools(ai_message, messages)
            
            # 3. Recursive: Get final response
            return await self.get_completion(messages)
        
        return ai_message
```

**Key Patterns:**

**Pattern 1: Streaming Collection**
```python
async def _stream_response(self, messages):
    content = ""
    tool_deltas = []
    
    async for chunk in stream:
        if chunk.delta.content:
            print(chunk.delta.content, end="")
            content += chunk.delta.content
        
        if chunk.delta.tool_calls:
            tool_deltas.extend(chunk.delta.tool_calls)
    
    return Message(
        role=Role.AI,
        content=content,
        tool_calls=self._collect_tool_calls(tool_deltas)
    )
```

**Pattern 2: Recursive Tool Calling**
```
User: "Add Alice with email alice@test.com"
    ↓
LLM: tool_call = add_user(name="Alice", email=...)
    ↓
Agent: Execute add_user tool
    Result: "User added with ID 1042"
    ↓
LLM (recursive): "I've created Alice with ID 1042"
    ↓
User sees final response
```

**Why Recursive:**
- ✅ Handles multi-step operations
- ✅ Clean code (no explicit loop)
- ✅ LLM decides when done (finish_reason="stop")
- ❌ Risk of infinite loop (but rare with good prompts)

---

## 🛠️ Implementation Details

### Phase 1: Tool Implementation

**Web Search Tool:**
```python
class WebSearchTool(BaseTool):
    def __init__(self, api_key, endpoint):
        self.__api_key = api_key
        self.__endpoint = f"{endpoint}/openai/deployments/gemini-2.5-pro/chat/completions"
    
    @property
    def name(self) -> str:
        return "web_search_tool"
    
    @property
    def description(self) -> str:
        return "Search the web using Google. Returns relevant results."
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["request"]
        }
    
    def execute(self, arguments: dict) -> str:
        # Use gemini-2.5-pro with google_search static function
        response = requests.post(
            url=self.__endpoint,
            headers={"api-key": self.__api_key, ...},
            json={
                "messages": [{"role": "user", "content": arguments["request"]}],
                "tools": [{
                    "type": "static_function",
                    "static_function": {
                        "name": "google_search",
                        "description": "Grounding with Google Search",
                        "configuration": {}
                    }
                }]
            }
        )
        return response.json()["choices"][0]["message"]["content"]
```

**User CRUD Tools:**
All inherit from `BaseUserServiceTool`:
```python
class BaseUserServiceTool(BaseTool, ABC):
    def __init__(self, user_client: UserClient):
        self._user_client = user_client
```

**Implementations:**
1. **GetUserByIdTool:** `user_client.get_user(id)`
2. **SearchUsersTool:** `user_client.search_users(**kwargs)`
3. **CreateUserTool:** `user_client.add_user(UserCreate.model_validate(args))`
4. **UpdateUserTool:** `user_client.update_user(id, UserUpdate.model_validate(args))`
5. **DeleteUserTool:** `user_client.delete_user(id)`

**Pattern:** Thin wrapper around UserClient API

---

### Phase 2: DIAL Client Implementation

**Message Flow:**
```python
# 1. User message
messages.append(Message(role=Role.USER, content="Add Alice"))

# 2. AI message with tool call
messages.append(Message(
    role=Role.AI,
    content="",
    tool_calls=[{
        "id": "call_xyz",
        "function": {
            "name": "add_user",
            "arguments": '{"name":"Alice",...}'
        }
    }]
))

# 3. Tool message
messages.append(Message(
    role=Role.TOOL,
    name="add_user",
    tool_call_id="call_xyz",
    content="User added: ID 1042"
))

# 4. Final AI message
messages.append(Message(
    role=Role.AI,
    content="I've created Alice with ID 1042"
))
```

**Critical: tool_call_id Linkage**
- LLM needs to correlate tool results with tool calls
- If `tool_call_id` doesn't match, LLM errors
- Must preserve exact ID from tool call

---

### Phase 3: System Prompt Engineering

```python
SYSTEM_PROMPT = """
You are an intelligent User Management Agent with access to:

1. get_user_by_id: Retrieve user by ID
2. search_users: Search by name/surname/email/gender
3. add_user: Create new user (name, surname, email, about_me required)
4. update_user: Modify existing user
5. delete_user: Remove user (confirm first!)
6. web_search_tool: Search web for user information

Guidelines:
- Always confirm destructive operations
- Use web search to enrich user profiles when appropriate
- Validate user IDs before updates/deletes
- Provide clear feedback on operations
- Handle errors gracefully

Stay focused on user management tasks.
"""
```

**Key Elements:**
- Tool inventory (LLM knows what's available)
- Usage guidelines (when/how to use tools)
- Safety instructions (confirm deletes)
- Domain constraints (stay on topic)

---

## 🔄 Complete Execution Flow

### Example: "Add Andrej Karpathy as a new user"

```
┌──────────────────────────────────────────┐
│ 1. User Input                            │
│    "Add Andrej Karpathy as a new user"  │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│ 2. LLM Analysis (Tool Planning)          │
│    - Need to add user                    │
│    - Missing: email, about_me            │
│    - Should search web for info          │
│    Decision: Use web_search_tool first   │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│ 3. Tool Call: web_search_tool            │
│    Args: {request: "Andrej Karpathy"}    │
│    Result: "AI researcher, former Tesla  │
│             Director of AI, Eureka Labs" │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│ 4. LLM Synthesis (2nd Call)              │
│    - Now have background info            │
│    - Can construct user profile          │
│    Decision: Use add_user tool           │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│ 5. Tool Call: add_user                   │
│    Args: {                               │
│      name: "Andrej",                     │
│      surname: "Karpathy",                │
│      email: "andrej.karpathy@example.com"│
│      about_me: "AI researcher..."        │
│    }                                     │
│    Result: "User added: ID 1067"         │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│ 6. Final LLM Response (3rd Call)         │
│    "I've created Andrej Karpathy with    │
│     ID 1067. He's an AI researcher..."   │
└──────────────────────────────────────────┘
```

**Total LLM Calls:** 3 (search → add → synthesize)

---

## 📊 Performance & Optimization

### Metrics

**Agent Latency Breakdown:**
- User input → Tool decision: ~1-2s
- Tool execution: ~0.5-3s (depends on tool)
- Final synthesis: ~1-2s
- **Total:** ~3-7s per query

**Token Usage (Average):**
- System prompt: ~300 tokens
- Conversation history: ~500 tokens/turn
- Tool schemas: ~200 tokens
- Tool results: ~100-500 tokens
- **Total Input:** ~1000-1500 tokens/turn
- **Total Output:** ~100-300 tokens/turn

**Cost (Rough):**
- Input: $0.0015/query
- Output: $0.0006/query
- **Total:** ~$0.002/query

### Optimization Opportunities

1. **Schema Compression:** Shorter tool descriptions
2. **Conversation Truncation:** Keep only recent turns
3. **Parallel Tool Calls:** Execute independent tools together
4. **Caching:** Cache frequent queries (e.g., "get user 1")
5. **Streaming UX:** User sees progress immediately

---

## 🎓 Key Learnings

### What Worked Well

1. **Base Tool Pattern:** Easy to add new tools
2. **Recursive Tool Calling:** Clean, natural flow
3. **Streaming:** Great user experience
4. **Test-Driven:** Fresh conversation per test avoided context issues

### Challenges

1. **Context Length:** Conversation history grows fast
2. **Tool Call ID Tracking:** Must preserve exact IDs
3. **Error Handling:** Tool failures need graceful recovery
4. **Delta Collection:** Streaming tool calls are fragmented

### Best Practices

1. **Tool Design:**
   - Single responsibility per tool
   - Clear, specific descriptions
   - Minimal required parameters
   - Rich error messages

2. **Agent Design:**
   - System prompt defines behavior
   - Conversation history maintains context
   - Tool calls are async (don't block)
   - Recursive completion handles multi-turn

3. **Testing:**
   - Fresh conversation per test
   - Cover tool combinations
   - Test error scenarios
   - Verify tool call IDs

---

## 🚀 Conclusion

This framework-less agent demonstrates:

1. **Core Agent Mechanics:** Tools, planning, execution, synthesis
2. **DIAL API Integration:** Streaming, tool calling, recursion
3. **Production Patterns:** Error handling, conversation management
4. **Extensibility:** Easy to add tools and capabilities

**Key Achievement:** Built a fully functional agent understanding every layer, from tool schemas to recursive LLM calls.

**Learning Value:** Understanding frameworks starts with building without them. This foundation makes LangChain/LlamaIndex usage more effective.

**Production Readiness:** With proper error handling, logging, and monitoring, this architecture scales to real applications.

