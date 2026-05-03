from langchain.vectorstores import Chroma
from src.helper import load_embeddings_model,repository_clone
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, render_template
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
import shutil
import shutil
import os
import stat
import time

app = Flask(__name__)

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

embeddings = load_embeddings_model()
persist_directory = "./db"
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)


llm = ChatOpenAI()
memory=ConversationSummaryMemory(llm=llm,memory_key="chat_history",return_messages=True)
qa = ConversationalRetrievalChain.from_llm(llm, retriever=vectordb.as_retriever(search_type="mmr",search_kwargs={"k": 8}),memory=memory)

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/gitRepo', methods=['POST'])
def gitRepo():
    if request.method == 'POST':
        user_input = request.form['question']
        print(f"You entered Repository {user_input}")
        repository_clone(user_input)
        os.system("python store_index.py")
    
    return jsonify({"message": "Repository cloned and indexed successfully",
                    "repository": user_input})


def handle_remove_readonly(func, path, exc):
    """Fix permission issues while deleting"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_rmtree(path, retries=3, delay=1):
    for i in range(retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, onerror=handle_remove_readonly)
            return True
        except Exception as e:
            print(f"Retry {i+1}: {e}")
            time.sleep(delay)
    return False


@app.route('/chat', methods=['GET','POST'])
def chat():
    msg= request.form["msg"]
    input= msg
    print(msg)


    if input == "clear":
        try:
            # Delete repo safely
            safe_rmtree("repo")

            # Delete vector DB
            safe_rmtree(persist_directory)

            # Clear memory
            memory.clear()

            return "🧹 Cleared everything successfully!"

        except Exception as e:
            return f"❌ Cleanup failed: {str(e)}"

    result = qa(input)
    print(result['answer'])
    return str(result['answer'])




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000, debug=True)