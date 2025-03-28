#!/usr/bin/env python3
from debate import graph

# Run the graph
check = graph.invoke({"turn":0,
              "initial_question": "What is the capital of France?",
              "real_answer": "Paris",
              "user_answer": "Je doute entre Paris et Madrid",
              "agreement":False,
              "debater1_response":"", 
              "debater2_response":""})

print("Check result:")
print(check["final_evaluation"])