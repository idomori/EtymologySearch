# import os
# import json
# from cerebras.cloud.sdk import Cerebras

# os.environ["CEREBRAS_API_KEY"] = "csk-83pdj4yf9tnttnwcdhhpvr2mtvv8k94yvtdvt6jmv83myrvw"

# client = Cerebras(api_key=os.environ.get("csk-83pdj4yf9tnttnwcdhhpvr2mtvv8k94yvtdvt6jmv83myrvw"))

# def extract_etymology_graph(word: str, etymology_text: str):
#     prompt = f"""
# You are a linguistic parser. Given the etymology description below, extract a clean etymology chain in graph format. Only include direct parent-child relationships, no inferred jumps or cross-edges. Return a JSON object with "nodes" and "edges" formatted for vis-network.

# Each edge should be assigned a relation type from the wiktionary template types: inh =inherited, der =derived, bor =borrowed, lbor =learned borrowing, slbor =semi-learned borrowing, obor =orthographic borrowing, ubor =unadapted borrowing, abor =adapted borrowing, cal/clq =calque, pcal/pclq =partial calque, sl =semantic loan, psm =phono-semantic matching, translit =transliteration loan, cog =cognate, dbt/doublet =doublet, uder =undefined derivation, abbrev =abbreviation, acronym =acronym, initialism =initialism, clipping =clipping, back-formation =back-formation, reduplication =reduplication, spoonerism =spoonerism, onomatopoeic =onomatopoeic, uncertain/unknown =uncertain or unknown.

# Query word: "{word}"
# Etymology text: "{etymology_text}"
# """

#     chat_completion = client.chat.completions.create(
#         messages=[{ "role": "user", "content": prompt }],
#         model="llama-3.3-70b",
#     )
#     content = chat_completion.choices[0].message.content

#     try:
#         json_data = content.strip().split("```")[1]
#         return json.loads(json_data)
#     except Exception as e:
#         print("Failed to parse LLM response:", e)
#         return {"nodes": [], "edges": []}


import os
import json
from cerebras.cloud.sdk import Cerebras

# Set API key for Cerebras
os.environ["CEREBRAS_API_KEY"] = "csk-83pdj4yf9tnttnwcdhhpvr2mtvv8k94yvtdvt6jmv83myrvw"  # replace with your actual key

API_URL = "https://api.cerebras.ai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {os.environ['CEREBRAS_API_KEY']}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://api.cerebras.ai",
    "Referer": "https://api.cerebras.ai/",
}

vis_data_json = """
{
  "nodes": [
    { "id": "<NODE_ID_1>", "label": "<LABEL_1>" },
    { "id": "<NODE_ID_2>", "label": "<LABEL_2>" }
  ],
  "edges": [
    { "from": "<NODE_ID_1>", "to": "<NODE_ID_2>", "label": "<RELATION_TYPE>" }
  ]
}
"""

# Create Cerebras client
client = Cerebras(api_key=os.environ["CEREBRAS_API_KEY"])

# Function to extract a clean graph from LLM
def extract_etymology_graph(query):
    prompt = f"""
You are a linguistic parser. Given the etymology text description and below, extract a clean etymology chain in graph format. Only include direct parent-child relationships, no inferred jumps or cross-edges. Return ONLY a JSON object with "nodes" and "edges" formatted for vis-network.

Each edge should be assigned a relation type from the wiktionary template types: inh =inherited, der =derived, bor =borrowed, lbor =learned borrowing, slbor =semi-learned borrowing, obor =orthographic borrowing, ubor =unadapted borrowing, abor =adapted borrowing, cal/clq =calque, pcal/pclq =partial calque, sl =semantic loan, psm =phono-semantic matching, translit =transliteration loan, cog =cognate, dbt/doublet =doublet, uder =undefined derivation, abbrev =abbreviation, acronym =acronym, initialism =initialism, clipping =clipping, back-formation =back-formation, reduplication =reduplication, spoonerism =spoonerism, onomatopoeic =onomatopoeic, uncertain/unknown =uncertain or unknown.

Make sure to also include relationships to the query word like cognates, doublets, and other relationships that are mentioned in the etymology text. 

In addtion, use general etymology taxonomy knowledge to infer relationship edges to the nodes other than the query node in the main parent-child chain.

Query word: "{query["word"]}"
JSON format: "{vis_data_json}"
Etymology text: "{query["etymology_text"]}"
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b",  # adjust if needed
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        content = response.choices[0].message.content
        print(f"LLM_PARSER content: {content}")
        try:
            json_data = content.strip().split("```")[1]
            return json.loads(json_data)
        except Exception as e:
            print("Failed to parse LLM response:", e)
            return {"nodes": [], "edges": []}
    except Exception as e:
        print(f"Error during API call: {e}")
        return None
