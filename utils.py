LLM_NAME = 'llama3.2'
EMBEDDING_MODEL = 'keepitreal/vietnamese-sbert'

def get_history(history_messages):
    his = []
    for item in history_messages:
        his.append({
            "type": item['type'],
            "text": item['text']
        })
    return his
