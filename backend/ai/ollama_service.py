import ollama
from backend.ai.prompts import build_graph_analysis_prompt
from backend.ai.prompts import build_analyze_analytics_prompt
from backend.ai.prompts import build_network_analysis_prompt

MODEL = "llama3.2:3b"

def ask_ollama(prompt):

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_predict": 400
        }
    )

    return response["message"]["content"]

def analyze_graph(graph_context):

    prompt = build_graph_analysis_prompt(
        graph_context
    )

    return ask_ollama(prompt)



def analyze_analytics(analytics_context):

    prompt = build_analyze_analytics_prompt(
        analytics_context
    )

    return ask_ollama(prompt)


def analyze_network_pattern(network_context):

    prompt = build_network_analysis_prompt(
        network_context
    )

    return ask_ollama(prompt)

