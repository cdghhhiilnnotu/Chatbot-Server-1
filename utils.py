LLM_NAME = 'llama3.1'
EMBEDDING_MODEL = 'keepitreal/vietnamese-sbert'

def get_history(history_messages):
    his = []
    for item in history_messages:
        history_messages.append({
            "type": item['type'],
            "text": item['text']
        })
    return his
