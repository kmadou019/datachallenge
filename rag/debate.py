#!/usr/bin/env python3
from langchain_ollama.llms import OllamaLLM
from langgraph.graph import START,END, StateGraph
from typing_extensions import TypedDict
import ast
MAX_TURN = 5

#Define agents
orchestrator =  OllamaLLM(model="mistral")
debater1 = OllamaLLM(model="mistral")
#debater1 = OllamaLLM(model="mistral")
debater2 = OllamaLLM(model="mistral")
#debater2 = OllamaLLM(model="phi4")


def extract_json(text):
    start = text.find("{")
    end = text.find("}")
    return ast.literal_eval(text[start:end+1])

class State(TypedDict):
    turn: int
    intial_question: str
    agreement: bool
    debater1_response: str
    debater2_response: str

def Orchestrator(state: State):
    print(state)
    if state['turn'] == 1:
        prompt = f"""
        You are an orchestrator for a debate between two debaters. 
        The initial question is: {state['intial_question']}. 
        Your task is to lead the debate with two debaters.
        """
        orchestrator.invoke(prompt)
        return {"agreement": False}
    
    if state['turn'] == MAX_TURN and state['agreement'] == False:
        prompt = f"""
        The debate has reached its maximum turn limit of {MAX_TURN}. 
        Please summarize the debate and provide a final evaluation of the arguments presented by both debaters.
        """
        return {"agreement": False}
    
    if state['agreement'] == True:
        prompt = f"""
        The debate has reached an agreement. 
        Please summarize the agreement and provide any final thoughts or conclusions.
        """
        orchestrator.invoke(prompt)
        return {"agreement": True}
    
    prompt = f"""
    You are an orchestrator for a debate between two debaters. 
    The current round is {state['turn']}. 
    Debater 1 has responded with: {state['debater1_response']}. 
    Debater 2 has responded with: {state['debater2_response']}. 
    Your task is to evaluate the responses and determine if there is any agreement between the two debaters. 
    If there is agreement, please summarize it by providing me this json format:
    {{
        "turn": {state['turn']},
        "agreement": true,
        "summary": "..."
    }}
    If there is no agreement, please provide me this json format:
    {{
        "turn": {state['turn']},
        "agreement": false,
        "summary": "..."
    }}
    """
    response = extract_json(orchestrator.invoke(prompt))
    return {"agreement": response["agreement"], "turn": state["turn"]+1}

def Debater1(state: State):
    if state['turn'] == 1:
        prompt = f"""
        You are Debater 1 in a debate. 
        The initial question is: {state['intial_question']}. 
        Give your opinion about the question in the following format:
        {{
            "response": "..."
        }}
        """
    else:
        prompt = f"""
        You are Debater 1 in a debate. 
        You said this in the previous turn: {state['debater1_response']}. 
        Your task is to provide a response to Debater 2's argument: {state['debater2_response']}. 
        Please provide your response in the following format:
        {{
            "response": "..."
        }}
        """

    response = extract_json(debater1.invoke(prompt))
    return {"debater1_response": response["response"]}

def Debater2(state: State):
    if state['turn'] == 1:
        prompt = f"""
        You are Debater 2 in a debate. 
        The initial question is: {state['intial_question']}. 
        Give your opinion about the question in the following format:
        {{
            "response": "..."
        }}
        """
    else:
        prompt = f"""
        You are Debater 2 in a debate. 
        You said this in the previous turn: {state['debater2_response']}. 
        Your task is to provide a response to Debater 1's argument: {state['debater1_response']}. 
        Please provide your response in the following format:
        {{
            "response": "..."
        }}
        """

    response = extract_json(debater2.invoke(prompt))
    return {"debater2_response": response["response"]}

def end(state: State):
    if state['agreement'] == True:
        return "last_action"
    else:
        return ["debater1","debater2"]
    
def last_action(state: State):
    print("last action")
    print(state)

graph_builder = StateGraph(State)
graph_builder.add_node("Orchestrator", Orchestrator)
graph_builder.add_node("debater1", Debater1)
graph_builder.add_node("debater2", Debater2)
graph_builder.add_node("last_action", last_action)

graph_builder.add_edge(START, "Orchestrator")
graph_builder.add_edge("debater1", "Orchestrator")
graph_builder.add_edge("debater2", "Orchestrator")
graph_builder.add_edge("last_action", END)
graph_builder.add_conditional_edges("Orchestrator", end,["debater1","debater2","last_action"])
graph = graph_builder.compile()


# Run the graph
graph.invoke({"turn":1,
              "intial_question": "Is AI a threat to humanity?",
              "agreement":False,
              "debater1_response":"", 
              "debater2_response":""})

img = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(img)
print("Image enregistrée sous 'graph.png'")