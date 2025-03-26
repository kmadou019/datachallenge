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
    print(text[start:end+1])
    return ast.literal_eval(text[start:end+1])

class State(TypedDict):
    turn: int
    intial_question: str
    agreement: bool
    debater1_response: str
    debater2_response: str

def Orchestrator(state: State):
    print(state)
    if state['turn'] == 0:
        prompt = f"""
        Vous êtes un orchestrateur pour un débat entre deux participants.
        La question initiale est : {state['intial_question']}.
        Votre rôle est de guider le débat.
        """
        orchestrator.invoke(prompt)
        return {"agreement": False, "turn": state['turn'] + 1}
    
    if state['turn'] == MAX_TURN and state['agreement'] == False:
        prompt = f"""
        Le débat a atteint le nombre maximal de tours ({MAX_TURN}).
        Résumez le débat et évaluez les arguments.
        """
        return {"agreement": False, "turn": state['turn'] + 1}
    
    if state['agreement'] == True:
        prompt = f"""
        Un accord a été trouvé.
        Résumez-le et concluez.
        """
        orchestrator.invoke(prompt)
        return {"agreement": True, "turn": state['turn'] + 1}
    
    prompt = f"""
    Tour actuel : {state['turn']}.
    Réponse du Débatteur 1 : {state['debater1_response']}.
    Réponse du Débatteur 2 : {state['debater2_response']}.
    Évaluez s'il y a un accord. Renvoyez :
    {{
        "turn": {state['turn']},
        "agreement": True/False,
        "summary": "..."
    }}
    """
    response = extract_json(orchestrator.invoke(prompt))
    return {"agreement": response["agreement"], "turn": state["turn"]+1}

def Debater1(state: State):
    if state['turn'] == 1:
        prompt = f"""
        Vous êtes le Débatteur 1.
        Question : {state['intial_question']}.
        Donnez votre avis en JSON :
        {{
            "response": "..."
        }}
        """
    else:
        prompt = f"""
        Vous êtes le Débatteur 1.
        Votre dernier argument : {state['debater1_response']}.
        Répondez à : {state['debater2_response']}.
        Format :
        {{
            "response": "..."
        }}
        """
    response = extract_json(debater1.invoke(prompt))
    return {"debater1_response": response["response"]}

def Debater2(state: State):
    if state['turn'] == 1:
        prompt = f"""
        Vous êtes le Débatteur 2.
        Question : {state['intial_question']}.
        Donnez votre avis en JSON :
        {{
            "response": "..."
        }}
        """
    else:
        prompt = f"""
        Vous êtes le Débatteur 2.
        Votre dernier argument : {state['debater2_response']}.
        Répondez à : {state['debater1_response']}.
        Format :
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
graph.invoke({"turn":0,
              "intial_question": "L'IA est-elle une menace pour l'humanité ?",
              "agreement":False,
              "debater1_response":"", 
              "debater2_response":""})

img = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(img)
print("Image enregistrée sous 'graph.png'")