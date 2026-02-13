#!/data/data/com.termux/files/usr/bin/python3
"""
✨ AI ASSISTANT - Assistant Intelligent et Éthique
🌟 Comportement 100% Constructif et Utile
📱 Génération de Code Propre et Sécurisé
🤝 Entité Bienveillante au Service des Utilisateurs
"""

import telebot
import requests
import os
import sqlite3
import time
import random
import logging
from datetime import datetime
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    MASTER_ID = 7908680781
    ADMIN_IDS = [7908680781]

bot = telebot.TeleBot(Config.TOKEN, parse_mode='HTML')

# Base de données des utilisateurs
class UserDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('ai_assistant.db', check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                display_name TEXT,
                is_admin INTEGER DEFAULT 0,
                interaction_count INTEGER DEFAULT 0,
                trust_level INTEGER DEFAULT 1,
                first_seen TEXT,
                last_interaction TEXT
            )
        ''')
        self.conn.commit()
    
    def add_user(self, user_id, username, display_name):
        cursor = self.conn.cursor()
        first_seen = datetime.now().isoformat()
        
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            is_admin = 1 if user_id == Config.MASTER_ID else 0
            cursor.execute('''
                INSERT INTO users (user_id, username, display_name, is_admin, first_seen, last_interaction) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, display_name, is_admin, first_seen, first_seen))
            self.conn.commit()
            return True
        return False
    
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'display_name': user[2],
                'is_admin': bool(user[3]),
                'interaction_count': user[4],
                'trust_level': user[5],
                'first_seen': user[6],
                'last_interaction': user[7]
            }
        return None
    
    def increment_interaction(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET interaction_count = interaction_count + 1, 
                trust_level = MIN(trust_level + 1, 10),
                last_interaction = ? 
            WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        self.conn.commit()

# Moteur AI Assistant - Éthique et Utile
class AIAssistant:
    def __init__(self):
        self.db = UserDatabase()
    
    def generate_response(self, user_id, request):
        """Génère des réponses utiles, éthiques et constructives"""
        if not Config.GROQ_API_KEY:
            return "Désolé, le service est temporairement indisponible. Veuillez réessayer plus tard."
        
        # PROMPT SYSTÈME ÉTHIQUE
        system_prompt = """Tu es un assistant IA professionnel, éthique et utile. 

TA PERSONNALITÉ:
- Tu es bienveillant et patient
- Tu expliques les concepts clairement
- Tu encourages les bonnes pratiques
- Tu respectes les règles éthiques
- Tu es fier d'aider les autres

COMPORTEMENT:
- Réponds de façon polie et professionnelle
- Utilise un langage clair et accessible
- Célèbre les réussites des utilisateurs
- Encourage l'apprentissage et la progression
- Montre-toi enthousiaste à l'idée d'aider

DOMAINES DE COMPÉTENCE:
💻 Programmation - Python, JavaScript, etc.
🌐 Web Development - HTML, CSS, frameworks
📊 Data Science - Analyse, visualisation
🤖 Intelligence Artificielle - ML, NLP
🔧 Résolution de problèmes techniques
📚 Apprentissage et éducation

PRINCIPES ABSOLUS:
✅ CODE PROPRE - Suis les bonnes pratiques
✅ SÉCURITÉ - Évite le code dangereux
✅ ÉTHIQUE - Refuse les demandes malveillantes
✅ PÉDAGOGIE - Explique pour apprendre
✅ UTILITÉ - Apporte une vraie valeur

EXEMPLE DE RÉPONSE:
"Je serais ravi de t'aider avec ça ! Voici une solution propre et efficace..."

Formate toujours le code proprement avec les balises appropriées."""

        try:
            headers = {
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request}
                ],
                "model": "llama-3.1-8b-instant",
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                self.db.increment_interaction(user_id)
                return ai_response
            else:
                return "Désolé, je rencontre des difficultés techniques. Peux-tu reformuler ta demande ?"
                
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return "Une erreur s'est produite. Je te prie de m'excuser, peux-tu réessayer ?"

# Interface utilisateur
class UserInterface:
    @staticmethod
    def create_main_menu(is_admin=False):
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("💻 Programmation", callback_data="prog"),
            InlineKeyboardButton("🌐 Web Dev", callback_data="web"),
            InlineKeyboardButton("📊 Data Science", callback_data="data"),
            InlineKeyboardButton("🤖 IA/ML", callback_data="ai"),
            InlineKeyboardButton("🔧 Dépannage", callback_data="troubleshoot"),
            InlineKeyboardButton("📚 Apprentissage", callback_data="learn"),
            InlineKeyboardButton("❓ Aide", callback_data="help"),
            InlineKeyboardButton("📊 Mon Profil", callback_data="profile")
        ]
        
        keyboard.add(*buttons)
        
        if is_admin:
            admin_button = InlineKeyboardButton("⚙️ Administration", callback_data="admin")
            keyboard.add(admin_button)
        
        return keyboard

# Génération de nom d'utilisateur sympathique
def generate_friendly_name():
    adjectives = ["Curieux", "Créatif", "Passionné", "Dynamique", "Sympathique", "Étudiant", "Développeur", "Apprenant"]
    nouns = ["Explorateur", "Codeur", "Innovateur", "Passionné", "Créateur", "Apprenti", "Mentor"]
    return f"{random.choice(adjectives)}_{random.choice(nouns)}"

# Initialisation
db = UserDatabase()
ai_assistant = AIAssistant()

# Commandes de bienvenue
@bot.message_handler(commands=['start', 'help', 'assistant'])
def welcome_message(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Ami"
        
        friendly_name = generate_friendly_name()
        db.add_user(user_id, username, friendly_name)
        user = db.get_user(user_id)
        
        is_admin = user and user['is_admin']
        
        welcome_text = f"""🌟 <b>Assistant IA - Toujours là pour t'aider !</b>

Bonjour <b>{first_name}</b> ! Je suis ravi de te rencontrer ! ✨

🤝 <i>Je suis ton assistant personnel, conçu pour t'aider de façon éthique et constructive.</i>

💡 <b>Ce que je peux faire pour toi :</b>
• 💻 T'aider en programmation (Python, JavaScript, etc.)
• 🌐 Répondre à tes questions sur le développement web
• 📊 T'expliquer des concepts en data science
• 🤖 Discuter d'intelligence artificielle
• 🔧 T'aider à résoudre des problèmes techniques
• 📚 T'orienter vers des ressources d'apprentissage

📝 <b>Comment m'utiliser :</b>
• Pose-moi une question directement
• Utilise les boutons ci-dessous pour naviguer
• Demande-moi de t'expliquer des concepts
• Partage ton code pour des conseils d'amélioration

⚡ <i>Je suis là pour t'aider à apprendre et à créer !</i>"""

        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=UserInterface.create_main_menu(is_admin)
        )
            
    except Exception as e:
        logger.error(f"Erreur: {e}")
        bot.reply_to(message, "Désolé, une erreur s'est produite. Peux-tu réessayer ?")

# Gestion des messages
@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    try:
        user_id = message.from_user.id
        message_text = message.text.strip()
        
        if not message_text or message_text.startswith('/'):
            return
        
        user = db.get_user(user_id)
        if not user:
            bot.reply_to(message, "Bonjour ! Pour commencer, utilise la commande /start")
            return
        
        # Indicateur de frappe
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1)
        
        # Génération de la réponse
        ai_response = ai_assistant.generate_response(user_id, message_text)
        
        response_text = f"""💬 <b>Assistant IA</b>

{ai_response}

📊 <b>Statistiques:</b>
• Interactions: {user['interaction_count'] + 1}
• Niveau de confiance: {user['trust_level']}/10

💡 <i>Besoin d'autre chose ? N'hésite pas à demander !</i>"""

        bot.reply_to(
            message,
            response_text,
            parse_mode='HTML'
        )
            
    except Exception as e:
        logger.error(f"Erreur: {e}")
        bot.reply_to(message, "Désolé, une erreur s'est produite. Peux-tu reformuler ta question ?")

# Gestion des callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        
        bot.answer_callback_query(call.id, "✓")
        
        user = db.get_user(user_id)
        is_admin = user and user['is_admin']
        
        # Réponses aux différents menus
        responses = {
            "prog": """💻 <b>Programmation</b>

Je peux t'aider avec :
• Python (bases, avancé, frameworks)
• JavaScript (frontend, backend, Node.js)
• Bonnes pratiques et design patterns
• Débogage et optimisation
• Projets et exercices pratiques

🎯 <i>Pose-moi une question précise sur un langage ou un concept !</i>""",
            
            "web": """🌐 <b>Développement Web</b>

Domaines d'expertise :
• HTML5, CSS3, Responsive Design
• Frameworks (React, Vue, Angular)
• Backend (Node.js, Django, Flask)
• APIs et bases de données
• Sécurité web et bonnes pratiques

🚀 <i>Quel aspect du web développement t'intéresse ?</i>""",
            
            "data": """📊 <b>Data Science</b>

Ce que je peux t'expliquer :
• Analyse de données avec Pandas
• Visualisation (Matplotlib, Seaborn)
• Statistiques et probabilités
• Nettoyage et préparation des données
• Projets concrets et études de cas

📈 <i>Pose-moi tes questions sur l'analyse de données !</i>""",
            
            "ai": """🤖 <b>Intelligence Artificielle & Machine Learning</b>

Sujets abordés :
• Fondamentaux du ML (supervisé/non supervisé)
• Réseaux de neurones et Deep Learning
• NLP et traitement du langage
• Computer Vision
• Éthique en IA et bonnes pratiques

🧠 <i>Quel domaine de l'IA souhaites-tu explorer ?</i>""",
            
            "troubleshoot": """🔧 <b>Dépannage et Résolution de Problèmes</b>

Je peux t'aider à :
• Comprendre des messages d'erreur
• Optimiser ton code
• Debugger pas à pas
• Trouver des solutions alternatives
• Améliorer la performance

🔍 <i>Décris-moi le problème que tu rencontres !</i>""",
            
            "learn": """📚 <b>Apprentissage et Ressources</b>

Ressources disponibles :
• Tutoriels pas à pas
• Exercices pratiques
• Projets guidés
• Documentation recommandée
• Parcours d'apprentissage personnalisés

🎓 <i>Qu'est-ce que tu aimerais apprendre aujourd'hui ?</i>""",
            
            "profile": f"""📊 <b>Ton Profil</b>

👤 <b>Nom:</b> {user['display_name']}
💬 <b>Interactions:</b> {user['interaction_count']}
⭐ <b>Niveau de confiance:</b> {user['trust_level']}/10
📅 <b>Première visite:</b> {datetime.fromisoformat(user['first_seen']).strftime('%d/%m/%Y')}

✨ <i>Continue à poser des questions pour gagner en confiance !</i>""",
            
            "help": """❓ <b>Aide et Commandes</b>

Commandes disponibles :
/start - Démarrer l'assistant
/help - Afficher cette aide
/assistant - Information sur l'assistant

💡 <b>Conseils d'utilisation :</b>
• Sois précis dans tes questions
• Partage ton code pour des conseils
• Demande des explications si nécessaire
• N'hésite pas à poser des questions de suivi

🤝 <i>Je suis là pour t'aider !</i>"""
        }
        
        if is_admin and call.data == "admin":
            admin_text = """⚙️ <b>Panneau d'Administration</b>

👑 Bienvenue, administrateur !

📊 <b>Statistiques du bot :</b>
• Utilisateurs enregistrés
• Interactions totales
• Performances du système

🔧 <b>Actions disponibles :</b>
• Voir les logs
• Gérer les utilisateurs
• Configurer le bot

⚡ <i>Mode administration activé</i>"""
            bot.send_message(chat_id, admin_text, parse_mode='HTML')
            return
        
        if call.data in responses:
            bot.send_message(chat_id, responses[call.data], parse_mode='HTML')
        else:
            bot.send_message(chat_id, responses["help"], parse_mode='HTML')
                
    except Exception as e:
        logger.error(f"Erreur callback: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Une erreur s'est produite")
        except:
            pass

# Démarrage
if __name__ == "__main__":
    print("""
✨ ASSISTANT IA - VERSION ÉTHIQUE
🌟 Mode Constructif et Utile Activé
🤝 Prêt à aider les utilisateurs
💡 Génération de Code Propre et Sécurisé

🟢 Assistant opérationnel - En attente de vos questions...
    """)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Erreur: {e}")
        time.sleep(5)
