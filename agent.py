
from langchain_core.runnables import RunnableConfig
from typing import Dict

class ShoppingAssistant:
    def __init__(self, runnable):
        self.runnable = runnable

    def __call__(self, state: Dict, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("user_id", None)
            state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)
            
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Please provide a detailed response.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
