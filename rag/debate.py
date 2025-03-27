#!/usr/bin/env python3
from langchain_ollama.llms import OllamaLLM
from langgraph.graph import START,END, StateGraph
from typing_extensions import TypedDict
import logging
import ast
MAX_TURN = 5

#Define agents
name_orchestrator = "llama3.3"
name_debater1 = "mistral"
name_debater2 = "phi4"
# Initialize the LLMs
orchestrator =  OllamaLLM(model=name_orchestrator)
debater1 = OllamaLLM(model=name_debater1)
debater2 = OllamaLLM(model=name_debater2)
#Intialize the log file
log_file = "debate_log.txt"
logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_file, mode="w")
logger.setLevel(logging.DEBUG)

handler.setLevel(logging.INFO)
handler.addFilter(lambda record: record.levelno == logging.INFO)
logger.addHandler(handler)

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
    if state['turn'] == 0:
        logger.info(f"Tour {state['turn']}:")
        logger.info("Initial question: " + state['intial_question'])
        logger.info("\n")
        prompt = f"""
        Vous êtes un orchestrateur pour un débat entre deux participants.
        La question initiale est : {state['intial_question']}.
        Votre rôle est de guider le débat.
        """
        orchestrator.invoke(prompt)
        return {"agreement": False, "turn": state['turn'] + 1}
    else:  
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
        logger.info(f"Resumé du débat par l'orchestrateur ({name_orchestrator}) : {response['summary']}")
        logger.info("\n")
        logger.info(f"Tour {state['turn']}:")
        logger.info("\n")
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
    logger.info(f"Réponse du Débatteur 1 ({name_debater1}) : {response['response']}")
    logger.info("\n")
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
    logger.info(f"Réponse du Débatteur 2 ({name_debater2}) : {response['response']}")
    logger.info("\n")
    return {"debater2_response": response["response"]}

def end(state: State):
    if state['agreement'] == True or (state['turn'] == MAX_TURN and state['agreement'] == False):
        return "last_action"
    else:
        return ["debater1","debater2"]
    
def last_action(state: State):
    if state['turn'] == MAX_TURN and state['agreement'] == False:
        prompt = f"""
        voici les reponses des débatteurs :
        Débatteur 1 : {state['debater1_response']}.
        Débatteur 2 : {state['debater2_response']}.
        Vous êtes l'orchestrateur.
        Le débat a atteint le nombre maximal de tours ({MAX_TURN}).
        Résumez le débat et évaluez les arguments puis tirez une conclusion.
        """
    if state['agreement'] == True:
        prompt = f"""
        Voici les réponses des débatteurs :
        Débatteur 1 : {state['debater1_response']}.
        Débatteur 2 : {state['debater2_response']}.
        Vous êtes l'orchestrateur.
        Le débat a abouti à un accord.
        Résumez le débat et évaluez les arguments puis tirez une conclusion.
        """
    response = orchestrator.invoke(prompt)
    logger.info(f"Résumé final du débat par l'orchestrateur ({name_orchestrator}) : {response}")
    logger.info("\n")
    return {"agreement": True, "turn": state['turn']}

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


if __name__ == "__main__":
    # Run the graph
    graph.invoke({"turn":0,
                  "intial_question": "La mort est-elle un mal ?", # You can change this question
                  "agreement":False,
                  "debater1_response":"", 
                  "debater2_response":""})
    img = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img)
    print("Image enregistrée sous 'graph.png'")