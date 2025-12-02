from typing import List, TypedDict, Annotated
import operator

class AgentState(TypedDict):
    alert_data: dict
    messages: Annotated[list, operator.add]  # 自动追加
    turn_count: int
    max_turns: int
    final_conclusion: str