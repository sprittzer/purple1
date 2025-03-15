from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from agent import ShoppingAssistant
from helper import create_tool_node_with_fallback
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class ShoppingGraph:
    def __init__(self, assistant_runnable, tools_no_confirmation, tools_need_confirmation):
        self.assistant_runnable = assistant_runnable
        self.tools_no_confirmation = tools_no_confirmation
        self.tools_need_confirmation = tools_need_confirmation
        self.confirmation_tool_names = {t.name for t in tools_need_confirmation}
        self.memory = MemorySaver()  # Initialize memory for state persistence
        self.graph = self._build_graph()

    def _build_graph(self):
        # Create a StateGraph builder
        builder = StateGraph(State)

        # Add nodes to the graph
        builder.add_node("assistant", ShoppingAssistant(self.assistant_runnable))
        builder.add_node("tools_no_confirmation", create_tool_node_with_fallback(self.tools_no_confirmation))
        builder.add_node("tools_need_confirmation", create_tool_node_with_fallback(self.tools_need_confirmation))

        # Define a function to route tool invocations
        def route_tools(state):
            next_node = tools_condition(state)
            if next_node == END:
                return END
            ai_message = state["messages"][-1]
            first_tool_call = ai_message.tool_calls[0]
            if first_tool_call["name"] in self.confirmation_tool_names:
                return "tools_need_confirmation"
            return "tools_no_confirmation"

        # Set up edges in the graph
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges(
            "assistant", route_tools, ["tools_no_confirmation", "tools_need_confirmation", END]
        )
        builder.add_edge("tools_no_confirmation", "assistant")
        builder.add_edge("tools_need_confirmation", "assistant")

        # Compile the graph with interruptions for tools needing confirmation
        return builder.compile(
            checkpointer=self.memory,
            interrupt_before=["tools_need_confirmation"],
        )

    def stream_responses(self, input_data, config):
        # Run the assistant graph and yield each response
        return self.graph.stream(input_data, config, stream_mode="values")

    def get_state(self, config):
        # Retrieve the current state of the graph
        return self.graph.get_state(config)

    def invoke(self, input_data, config):
        # Directly invoke the graph with given input and config
        return self.graph.invoke(input_data, config)
