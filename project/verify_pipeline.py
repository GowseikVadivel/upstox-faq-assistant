import sys

sys.path.insert(0, '.')

from modules.vector_store import get_collection
from modules.retriever import retrieve_context
from modules.llm_client import generate_answer

print('starting')
collection = get_collection()
print('collection_count=', collection.count())
results = retrieve_context('How can I add money to my account?', top_k=2)
print('result_count=', len(results))
if results:
    print('top_result_url=', results[0]['url'])
    print('top_result_title=', results[0]['title'])

answer = generate_answer('How can I add money to my account?')
print('answer_preview=', answer[:200])
