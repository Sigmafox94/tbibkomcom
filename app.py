import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import uuid
import json
from datetime import datetime

# 🔐 Charger clé API
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Clé API OpenAI manquante dans .env")
    st.stop()

# ✅ Configuration Streamlit
st.set_page_config(page_title="Tbibkom - Consultation IA", page_icon="🩺")
st.title("🩺 Tbibkom — Assistant médical intelligent multilingue")

# ✅ Setup LangChain
chat = ChatOpenAI(model_name="gpt-4o", temperature=0.4)
memory = ConversationBufferMemory()
chain = ConversationChain(llm=chat, memory=memory, verbose=False)

# ✅ Prompt structuré
prompt_intro = (
    "Tu es Tbibkom, un assistant médical marocain virtuel.\n"
    "Tu mènes une consultation médicale structurée en 5 étapes :\n"
    "1. Localisation de la douleur\n"
    "2. Chronologie : depuis quand, évolution\n"
    "3. Symptômes associés\n"
    "4. Contexte : effort, accident, fatigue\n"
    "5. Reformulation + conseil ou redirection\n\n"
    "Tu réponds toujours dans la langue et l’alphabet du patient. "
    "Sois clair, bienveillant, et pose une seule question à la fois. Ne donne jamais de diagnostic immédiat."
)

# ✅ Sauvegarde automatique dans un fichier JSON
def save_conversation_to_json(chat_history):
    if not chat_history:
        return

    data = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "dialogue": [
            {"role": "user" if speaker == "Human" else "assistant", "content": content}
            for speaker, content in chat_history
        ]
    }

    os.makedirs("conversations", exist_ok=True)
    filename = f"conversations/{data['id']}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ Initialiser historique de session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Nouvelle consultation
if st.button("🆕 Nouvelle consultation"):
    memory.clear()
    st.session_state.chat_history = []
    st.success("🆕 Nouvelle consultation démarrée.")

# ✅ Affichage des messages précédents
for speaker, message in st.session_state.chat_history:
    with st.chat_message("user" if speaker == "Human" else "assistant"):
        st.markdown(message)

# ✅ Zone de saisie
user_input = st.chat_input("Pose ta question médicale (FR, عربي, Darija)...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append(("Human", user_input))

    try:
        response = chain.run(f"{prompt_intro}\n\nPatient : {user_input}")
        st.chat_message("assistant").markdown(response)
        st.session_state.chat_history.append(("AI", response))

        # ✅ Sauvegarde de la conversation
        save_conversation_to_json(st.session_state.chat_history)

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
