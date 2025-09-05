
from dataclasses import dataclass, field

@dataclass
class ConversationState:
    step: str = "greet"
    collected: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

def next_step(state: ConversationState, user_input: str):
    # Extremely simple controller for demo; UI handles most branching explicitly.
    if state.step == "greet":
        state.step = "collect_patient_info"
    elif state.step == "collect_patient_info":
        state.step = "lookup_result"
    elif state.step == "lookup_result":
        state.step = "choose_slot"
    elif state.step == "choose_slot":
        state.step = "insurance"
    elif state.step == "insurance":
        state.step = "confirm"
    elif state.step == "confirm":
        state.step = "done"
    return state
