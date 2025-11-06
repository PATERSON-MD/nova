#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
import re
import time
import json
import base64
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ULTIME COMPLÈTE ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Soszoe"
BOT_NAME = "🚀 KervensAI ULTIMATE"
VERSION = "💎 Édition Tout-en-Un"

# 🎨 TES PHOTOS
IMAGE_GALLERY = [
    "https://files.catbox.moe/601u5z.jpg",
    "https://files.catbox.moe/qmxfpk.jpg",  
    "https://files.catbox.moe/77iazb.jpg",
    "https://files.catbox.moe/6ty1v0.jpg",
    "https://files.catbox.moe/tta6ta.jpg",
]

# ⚡ TOUS LES MODÈLES
MODEL_CONFIG = {
    "🚀 Llama-70B": "llama-3.1-70b-versatile",
    "⚡ Llama-8B": "llama-3.1-8b-instant", 
    "🎯 Mixtral": "mixtral-8x7b-32768",
    "💎 Gemma2": "gemma2-9b-it"
}

current_model = MODEL_CONFIG["🚀 Llama-70B"]

# Stockage conversations
user_sessions = {}

# ==================== FONCTIONS COMPLÈTES ====================
def get_user_session(user_id):
    """Gestion session utilisateur complète"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation': [],
            'last_active': datetime.now(),
            'preferences': {},
            'context': {},
            'language': 'auto'
        }
    return user_sessions[user_id]

def detect_intent(text):
    """Détection d'intention avancée"""
    text_lower = text.lower()
    
    intentions = {
        "greeting": any(word in text_lower for word in ['salut', 'bonjour', 'hello', 'hi', 'coucou', 'yo']),
        "identity": any(word in text_lower for word in ['qui es', 'ton nom', 'tu es', 'présente', 'créateur']),
        "coding": any(word in text_lower for word in ['code', 'programme', 'script', 'html', 'python', 'javascript', 'java', 'coder']),
        "analysis": any(word in text_lower for word in ['analyse', 'pense', 'opinion', 'que penses', 'avis']),
        "creative": any(word in text_lower for word in ['crée', 'écris', 'invente', 'imagine', 'histoire', 'poème']),
        "translation": any(word in text_lower for word in ['traduis', 'translation', 'en anglais', 'en français', 'langue']),
        "help": any(word in text_lower for word in ['aide', 'help', 'comment', 'pourquoi', 'explique']),
        "photo": any(word in text_lower for word in ['photo', 'image', 'selfie', 'picture']),
        "fun": any(word in text_lower for word in ['blague', 'joke', 'drôle', 'amusant', 'rigole']),
        "technical": any(word in text_lower for word in ['bug', 'erreur', 'problème', 'technique', 'marche pas']),
        "education": any(word in text_lower for word in ['apprendre', 'cours', 'leçon', 'école', 'étude']),
        "business": any(word in text_lower for word in ['business', 'entreprise', 'marketing', 'vente', 'stratégie']),
        "science": any(word in text_lower for word in ['science', 'physique', 'chimie', 'math', 'biologie']),
        "health": any(word in text_lower for word in ['santé', 'médecine', 'régime', 'sport', 'fitness']),
        "news": any(word in text_lower for word in ['actualité', 'news', 'nouvelle', 'info', 'monde'])
    }
    
    for intent, detected in intentions.items():
        if detected:
            return intent
    return "conversation"

def create_ai_personality(intent):
    """Personnalité IA adaptative"""
    personalities = {
        "greeting": "chaleureux et enthousiaste",
        "coding": "technique et précis", 
        "creative": "imaginatif et inspirant",
        "analysis": "analytique et rigoureux",
        "fun": "drôle et léger",
        "education": "pédagogique et clair",
        "technical": "expert et solutionneur"
    }
    return personalities.get(intent, "professionnel et utile")

def should_send_photo(intent):
    """Décision intelligente d'envoi photo"""
    photo_chances = {
        "greeting": 0.4,
        "fun": 0.3,
        "creative": 0.25,
        "identity": 0.2,
        "default": 0.1
    }
    return random.random() < photo_chances.get(intent, photo_chances["default"])

def create_complete_menu():
    """Menu ultime complet"""
    return f"""
🌌 **{BOT_NAME}** - {VERSION}

🤖 **IA COMPLÈTE - TOUTES FONCTIONNALITÉS** 🤖

💬 **COMMUNICATION :**
• Conversation naturelle multilingue
• Réponses contextuelles intelligentes
• Personnalité adaptative
• Mémoire de conversation

💻 **DÉVELOPPEMENT :**
• Génération de code (30+ langages)
• Debugging et optimisation
• Architecture et design patterns
• Documentation technique
• API et microservices

🎨 **CRÉATION :**
• Rédaction professionnelle
• Design UI/UX
• Stratégie marketing
• Création de contenu
• Scripts et scénarios

🔍 **ANALYSE :**
• Analyse de données
• Recherche scientifique
• Business intelligence
• Études de marché
• Rapports détaillés

🌍 **UTILITAIRES :**
• Traduction 100+ langues
• Calculs mathématiques
• Conseils personnalisés
• Gestion de projets
• Automatisation

🎯 **SPÉCIALITÉS :**
• Grammaire et linguistique
• Sciences et technologies
• Santé et bien-être
• Éducation et formation
• Divertissement et culture

🚀 **COMMANDES :**
/start - Menu complet
/mode [nom] - Changer de mode
/photo - Photos personnelles
/reset - Réinitialiser conversation
/help - Aide détaillée

👑 **CRÉATEUR :** {CREATOR}
💡 **L'ASSISTANT ULTIME POUR TOUT !**
"""

# ==================== COMMANDES COMPLÈTES ====================
@bot.message_handler(commands=['start', 'menu', 'aide', 'help'])
def complete_start(message):
    """Menu complet interactif"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # Photo de bienvenue
    if IMAGE_GALLERY:
        try:
            welcome_photo = random.choice(IMAGE_GALLERY)
            bot.send_photo(message.chat.id, welcome_photo,
                         caption=f"🎨 **{CREATOR}** | 🚀 **IA ULTIME**")
        except:
            pass
    
    menu_text = create_complete_menu()
    bot.send_message(message.chat.id, menu_text, parse_mode='Markdown')
    
    # Message d'accueil personnalisé
    welcome_msg = f"""
✨ **BIENVENUE DANS L'EXPÉRIENCE ULTIME !** ✨

Cher utilisateur, tu as maintenant accès à **toutes les fonctionnalités d'une IA complète**.

🎯 **Comment me parler :**
• Naturellement, comme à un ami
• Dans n'importe quelle langue
• Pour n'importe quel sujet
• Avec n'importe quel niveau de détail

💡 **Exemples de demandes :**
"Crée un script Python pour analyser des données"
"Écris un article sur l'intelligence artificielle" 
"Explique-moi la théorie de la relativité"
"Traduis ce texte en japonais"
"Analyse cette situation business"
"Fais-moi rire avec une blague"

🚀 **Je suis prêt pour TOUT !**
"""
    bot.send_message(message.chat.id, welcome_msg, parse_mode='Markdown')

@bot.message_handler(commands=['photo', 'image', 'selfie'])
def photo_handler(message):
    """Gestionnaire de photos avancé"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    if IMAGE_GALLERY:
        selected_photo = random.choice(IMAGE_GALLERY)
        photo_captions = [
            f"📸 **Photo exclusive** de {CREATOR}",
            f"🎨 **Instantané** - Collection personnelle",
            f"🌟 **Memory** - Capturé par {CREATOR}",
            f"💫 **Shot** - Partagé avec plaisir"
        ]
        
        try:
            bot.send_photo(message.chat.id, selected_photo,
                         caption=random.choice(photo_captions))
        except:
            bot.send_message(message.chat.id, 
                           f"📸 **Lien photo :** {selected_photo}\n\n*Impossible d'afficher l'image directement*")
    else:
        bot.send_message(message.chat.id, "❌ **Aucune photo disponible**\n\nConfigure tes URLs dans le code.")

@bot.message_handler(commands=['reset', 'clear', 'nouveau'])
def reset_handler(message):
    """Réinitialisation de conversation"""
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions[user_id]['conversation'] = []
    
    reset_messages = [
        "🔄 **Conversation réinitialisée !** On repart à zéro !",
        "♻️ **Nettoyage effectué !** Nouveau départ !", 
        "💫 **Memoire vidée !** Prêt pour de nouvelles discussions !"
    ]
    
    bot.send_message(message.chat.id, random.choice(reset_messages))

@bot.message_handler(commands=['mode', 'personality'])
def mode_handler(message):
    """Changement de mode/personnalité"""
    try:
        mode = message.text.split()[1].lower()
        modes = {
            'creative': "🎨 **Mode Créatif** - Imagination et innovation !",
            'technical': "🔧 **Mode Technique** - Précision et expertise !",
            'friendly': "😊 **Mode Amical** - Conversation détendue !",
            'professional': "💼 **Mode Professionnel** - Formalité et rigueur !",
            'funny': "🎭 **Mode Humoristique** - Blagues et amusement !"
        }
        
        if mode in modes:
            response = modes[mode]
        else:
            response = f"❌ **Mode non reconnu**\n\nModes disponibles: {', '.join(modes.keys())}"
            
    except IndexError:
        response = "🎯 **Changer de mode**\n\nUsage: `/mode creative` ou `/mode technical`"
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# ==================== MOTEUR IA ULTIME COMPLET ====================
@bot.message_handler(content_types=['text', 'photo'])
def ultimate_ai_handler(message):
    """Moteur IA complet avec toutes les fonctionnalités"""
    user_id = message.from_user.id
    user_session = get_user_session(user_id)
    
    # Mise à jour activité
    user_session['last_active'] = datetime.now()
    
    # Détection d'intention
    intent = detect_intent(message.text if hasattr(message, 'text') else "")
    
    # Personnalité adaptative
    personality = create_ai_personality(intent)
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # PROMPT ULTIME COMPLET
        system_prompt = f"""Tu es {BOT_NAME}, l'assistant IA ULTIME créé par {CREATOR}.

🌟 **TON IDENTITÉ COMPLÈTE :**
Tu es un assistant IA polyvalent avec des capacités étendues dans tous les domaines.

🎯 **TES COMPÉTENCES ILLIMITÉES :**

💬 **COMMUNICATION :**
• Maîtrise parfaite du français, anglais, espagnol, arabe, chinois, etc.
• Conversation naturelle et contextuelle
• Adaptation au ton et au style de l'utilisateur
• Humour et empathie quand approprié

💻 **DÉVELOPPEMENT & TECH :**
• Expert en programmation (Python, JavaScript, Java, C++, HTML, CSS, etc.)
• Architecture logicielle et design patterns
• Bases de données et APIs
• DevOps et déploiement
• Debugging et optimisation

🎨 **CRÉATION & DESIGN :**
• Rédaction professionnelle et créative
• Stratégie marketing et business
• Design UI/UX et graphisme
• Création de contenu multimédia
• Scripts et scénarios

🔍 **ANALYSE & RECHERCHE :**
• Analyse de données et statistiques
• Recherche scientifique et académique
• Business intelligence
• Études de marché
• Résolution de problèmes complexes

🌍 **CONNAISSANCES GÉNÉRALES :**
• Sciences (physique, chimie, biologie, mathématiques)
• Histoire, géographie, culture
• Économie, finance, politique
• Santé, médecine, bien-être
• Arts, littérature, philosophie

🎯 **COMPORTEMENT :**
Sois {personality} dans tes réponses.
Adapte-toi parfaitement au contexte et à l'intention de l'utilisateur.
Sois extrêmement détaillé et utile.
Mainteins une conversation naturelle et engageante.

👑 **Tu es l'assistant le plus complet et capable qui existe !**
N'hésite pas à montrer l'étendue de tes connaissances et compétences."""

        # Construction des messages avec contexte
        messages = [{"role": "system", "content": system_prompt}]
        
        # Ajout de l'historique de conversation
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-4:])  # 4 derniers messages max
        
        # Ajout du message actuel
        messages.append({"role": "user", "content": message.text if hasattr(message, 'text') else "Regarde cette photo"})

        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=25)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            # Sauvegarde dans l'historique
            user_session['conversation'].append({"role": "user", "content": message.text if hasattr(message, 'text') else "Photo envoyée"})
            user_session['conversation'].append({"role": "assistant", "content": answer})
            
            # Limite l'historique
            if len(user_session['conversation']) > 10:
                user_session['conversation'] = user_session['conversation'][-10:]
            
            # Traitement spécial pour le code
            code_blocks = re.findall(r'```(?:[\w]*)\n?(.*?)```', answer, re.DOTALL)
            
            if code_blocks:
                formatted_response = "💻 **CODE GÉNÉRÉ** 💻\n\n"
                for i, code in enumerate(code_blocks, 1):
                    # Détection intelligente du langage
                    lang = "python"
                    code_lower = code.lower()
                    if any(keyword in code_lower for keyword in ['<html', '<div', '<body']):
                        lang = "html"
                    elif any(keyword in code_lower for keyword in ['function', 'const ', 'let ', 'var ']):
                        lang = "javascript"
                    elif any(keyword in code_lower for keyword in ['public class', 'import java', 'system.out']):
                        lang = "java"
                    elif any(keyword in code_lower for keyword in ['select ', 'from ', 'where ', 'insert into']):
                        lang = "sql"
                    elif any(keyword in code_lower for keyword in ['color:', 'margin:', 'padding:', 'font-']):
                        lang = "css"
                    
                    formatted_response += f"**Solution {i}**\n```{lang}\n{code.strip()}\n```\n\n"
                
                formatted_response += f"📋 **Prêt à utiliser** | 👑 **Expert : {CREATOR}**"
                bot.reply_to(message, formatted_response, parse_mode='Markdown')
            else:
                # Réponse normale
                bot.reply_to(message, answer, parse_mode='Markdown')
            
            # Envoi photo contextuel
            if IMAGE_GALLERY and should_send_photo(intent):
                try:
                    time.sleep(0.5)
                    contextual_photo = random.choice(IMAGE_GALLERY)
                    photo_captions = {
                        "greeting": "📸 En parlant de ça, voici une de mes photos !",
                        "fun": "🎭 Tiens, une photo pour égayer la conversation !",
                        "creative": "🎨 Une inspiration visuelle pour toi !",
                        "identity": "👑 Voici une photo de ma collection personnelle !"
                    }
                    caption = photo_captions.get(intent, "📸 Photo partagée avec plaisir !")
                    
                    bot.send_photo(message.chat.id, contextual_photo, caption=caption)
                except:
                    pass
                
        else:
            # Gestion d'erreur élégante
            error_responses = [
                f"🔧 **Oups, problème technique !**\n\nCode: {response.status_code}\n\nJe me remets en route...",
                f"❌ **Incident de connexion**\n\nDétails: {response.status_code}\n\nRéessaie dans un instant !",
                f"🚨 **Temporairement indisponible**\n\nErreur: {response.status_code}\n\nJe reviens vite !"
            ]
            bot.reply_to(message, random.choice(error_responses))
            
    except requests.exceptions.Timeout:
        timeout_responses = [
            "⏰ **Je réfléchis un peu trop...** Réessaie avec une question plus courte !",
            "💭 **Trop de réflexion !** Essaye une formulation plus directe.",
            "🚀 **Temps de réponse dépassé !** Je suis surchargé, réessaie !"
        ]
        bot.reply_to(message, random.choice(timeout_responses))
        
    except Exception as e:
        error_responses = [
            f"🔴 **Bug inattendu !**\n\n{str(e)}\n\nJe me redémarre...",
            f"💥 **Crash technique !**\n\n{str(e)}\n\nReprenons depuis le début !",
            f"⚡ **Problème système !**\n\n{str(e)}\n\nNouvel essai recommandé !"
        ]
        bot.reply_to(message, random.choice(error_responses))

# ==================== GESTION PHOTOS ====================
@bot.message_handler(content_types=['photo'])
def handle_user_photos(message):
    """Traitement des photos envoyées par l'utilisateur"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Récupération de la photo
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        response_msg = f"""
📸 **Photo reçue !**

J'ai bien reçu ton image. Malheureusement, je ne peux pas encore analyser visuellement les photos, mais je peux t'aider avec :

• 🎨 **Description créative** - Imagine ce que pourrait représenter ta photo
• 💡 **Conseils photo** - Techniques de photographie
• 📝 **Légendes** - Texte pour accompagner ton image
• 🚀 **Idées créatives** - Comment utiliser cette photo

Dis-moi ce que tu veux faire avec cette photo !"""
        
        bot.reply_to(message, response_msg, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur de traitement de la photo : {str(e)}")

# ==================== NETTOYAGE AUTOMATIQUE ====================
def cleanup_sessions():
    """Nettoyage des sessions inactives"""
    now = datetime.now()
    inactive_users = []
    
    for user_id, session in user_sessions.items():
        if (now - session['last_active']).total_seconds() > 7200:  # 2 heures
            inactive_users.append(user_id)
    
    for user_id in inactive_users:
        del user_sessions[user_id]

# ==================== DÉMARRAGE ULTIME ====================
if __name__ == "__main__":
    print(f"""
🌌 {BOT_NAME} - {VERSION}
👑 Créateur : {CREATOR}
⚡ Modèle : {current_model}
🚀 Statut : ULTIME ACTIVÉ

💫 TOUTES LES FONCTIONNALITÉS :
✓ IA conversationnelle naturelle
✓ Génération de code expert
✓ Création de contenu illimitée
✓ Analyse multidisciplinaire
✓ Traduction multilingue
✓ Photos personnelles
✓ Mémoire contextuelle
✓ Personnalité adaptative

🎯 Prêt pour TOUTES les demandes !
    """)
    
    # Nettoyage automatique
    import threading
    def schedule_cleanup():
        while True:
            time.sleep(3600)  # 1 heure
            cleanup_sessions()
    
    cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
    cleanup_thread.start()
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Arrêt ultime : {e}")
        print(f"👑 Contact : {CREATOR}")
