from indexer.search_index import search_index

# Perform a sample search
query = "apple"  # You can change this to anything
results = search_index(query)

# Print results
i = 0
for r in results:
    # print(f"{r['word']} ({r['pos']}): {r['definition'][:100]}...")
    print(f"RESULT {i}")
    print(r)
    i += 1
