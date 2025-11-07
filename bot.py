#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
import re
import time
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

# ==================== CONFIGURATION OPTIMISÉE POUR GROQ ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Soszoe"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition Groq Optimisée"

# 🎨 VOTRE PHOTO PRINCIPALE
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"

# ⚡ MODÈLE OPTIMISÉ
current_model = "llama-3.1-8b-instant"

# Stockage conversations léger
user_sessions = {}

# ==================== SYSTÈME PREMIUM GRATUIT ====================
def init_db():
    """Initialise la base de données pour le système premium"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS groups
                 (group_id INTEGER PRIMARY KEY, 
                  group_name TEXT,
                  member_count INTEGER,
                  added_date TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_access
                 (user_id INTEGER PRIMARY KEY,
                  has_premium BOOLEAN DEFAULT FALSE)''')
    conn.commit()
    conn.close()

def check_group_requirements():
    """Vérifie si les conditions premium sont remplies"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM groups WHERE member_count >= 60')
    qualified_groups = c.fetchone()[0]
    conn.close()
    return qualified_groups >= 5

def check_premium_access(user_id):
    """Vérifie si l'utilisateur a accès au premium"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT has_premium FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0]

def get_group_stats():
    """Récupère les statistiques des groupes"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM groups WHERE member_count >= 60')
    qualified = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM groups')
    total = c.fetchone()[0]
    conn.close()
    return qualified, total

def get_progress_bar():
    """Affiche une barre de progression"""
    qualified, total = get_group_stats()
    filled = '█' * qualified
    empty = '░' * (5 - qualified)
    return f"`[{filled}{empty}]` {qualified}/5"

def activate_premium_for_all():
    """Active le premium pour tous les utilisateurs"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET has_premium = TRUE')
    conn.commit()
    conn.close()

# ==================== FONCTIONS OPTIMISÉES ====================
def get_user_session(user_id):
    """Gestion session minimaliste"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation': [],
            'last_active': datetime.now()
        }
    return user_sessions[user_id]

def create_main_menu():
    """Crée le menu avec bouton Support Créateur"""
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(support_button)
    return keyboard

def create_premium_menu():
    """Crée le menu pour débloquer le premium"""
    keyboard = InlineKeyboardMarkup()
    add_button = InlineKeyboardButton("📥 Ajouter à un groupe", 
                                     url="https://t.me/YourBotUsername?startgroup=true")
    status_button = InlineKeyboardButton("📊 Vérifier le statut", callback_data="check_status")
    keyboard.add(add_button)
    keyboard.add(status_button)
    return keyboard

def detect_quick_intent(text):
    """Détection rapide d'intention"""
    text_lower = text.lower()
    if any(word in text_lower for word in ['salut', 'bonjour', 'hello']): return "greeting"
    if any(word in text_lower for word in ['code', 'programme', 'script']): return "coding"
    if any(word in text_lower for word in ['crée', 'écris', 'invente']): return "creative"
    return "conversation"

def should_send_photo(intent):
    """Décision photo simplifiée"""
    chances = {"greeting": 0.3, "creative": 0.2, "default": 0.1}
    return random.random() < chances.get(intent, chances["default"])

# ==================== COMMANDES OPTIMISÉES ====================
@bot.message_handler(commands=['start', 'aide'])
def optimized_start(message):
    """Menu optimisé avec votre photo"""
    user_id = message.from_user.id
    
    # Enregistrer l'utilisateur dans la base
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO user_access (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()
    
    try:
        # Envoi de votre photo avec légende
        bot.send_photo(
            message.chat.id, 
            MAIN_PHOTO,
            caption=f"📸 **{CREATOR}** - Créateur du bot\n*Votre expert en IA* 👑",
            parse_mode='Markdown'
        )
        time.sleep(0.5)
    except Exception as e:
        print(f"Photo non chargée: {e}")
    
    # Vérifier le statut premium
    if check_premium_access(user_id):
        # ✅ UTILISATEUR PREMIUM
        menu = f"""
🎉 **{BOT_NAME}** - {VERSION} **PREMIUM**

👑 **Créé par {CREATOR}**
⭐ **Version Premium Activée !**

💫 **Fonctionnalités débloquées :**
• 💻 Programmation & Code
• 🎨 Création & Rédaction  
• 📊 Analyse & Conseil
• 🌍 Traduction
• 💬 Conversation naturelle
• 🚀 Réponses illimitées

💡 **Exemples :**
"Code un script Python pour..."
"Écris un article sur..."
"Explique-moi..."
"Traduis ce texte..."

✨ **Profitez de toutes les fonctionnalités !**
"""
        bot.send_message(
            message.chat.id, 
            menu, 
            parse_mode='Markdown',
            reply_markup=create_main_menu()
        )
    else:
        # 🔒 VERSION LIMITÉE
        qualified, total = get_group_stats()
        menu = f"""
🔒 **{BOT_NAME}** - {VERSION} **LIMITÉE**

👑 **Créé par {CREATOR}**

🚀 **Assistant IA optimisé pour Groq**
*Version limitée - Débloquez le premium gratuitement !*

{get_progress_bar()}

🎁 **Conditions pour le Premium GRATUIT :**
• 👥 5 groupes avec 60+ membres
• ➕ Bot dans au moins 5 grands groupes
• ✅ Déblocage immédiat après validation

📊 **Statut actuel :**
• Groupes qualifiés : {qualified}/5
• Total groupes : {total}

💡 **Comment débloquer :**
1. Ajoutez ce bot à des groupes (60+ membres)
2. Partagez avec vos amis
3. Le premium se débloque automatiquement

👑 **La communauté grandit ensemble !**
"""
        bot.send_message(
            message.chat.id, 
            menu, 
            parse_mode='Markdown',
            reply_markup=create_premium_menu()
        )

@bot.message_handler(commands=['status', 'premium'])
def status_command(message):
    """Vérifie le statut premium"""
    user_id = message.from_user.id
    if check_premium_access(user_id):
        bot.reply_to(message, "✅ **Vous avez la version PREMIUM !** Profitez-en ! 🚀")
    else:
        qualified, total = get_group_stats()
        status_msg = f"""
🔒 **STATUT PREMIUM**

{get_progress_bar()}

📊 **Progression :**
• Groupes qualifiés : {qualified}/5
• Total groupes : {total}

🎁 **Il reste {5-qualified} groupes à ajouter pour débloquer le premium !**

👇 **Ajoutez le bot à des groupes pour accélérer le processus :**
"""
        bot.reply_to(message, status_msg, parse_mode='Markdown', reply_markup=create_premium_menu())

@bot.message_handler(commands=['photo'])
def photo_handler(message):
    """Affiche votre photo avec bouton support"""
    try:
        bot.send_photo(
            message.chat.id, 
            MAIN_PHOTO,
            caption=f"📸 **{CREATOR}** - Créateur du bot\n*Merci pour votre support !* 💝",
            parse_mode='Markdown',
            reply_markup=create_main_menu()
        )
    except:
        bot.send_message(message.chat.id, "❌ Erreur lors du chargement de la photo")

@bot.message_handler(commands=['support'])
def support_handler(message):
    """Commande dédiée pour le support"""
    support_text = f"""
💝 **Support {CREATOR}**

Merci de soutenir mon travail ! 
Votre support m'aide à améliorer ce bot et à créer de nouveaux projets.

👇 **Cliquez ci-dessous pour me contacter :**
"""
    bot.send_message(
        message.chat.id,
        support_text,
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

@bot.message_handler(commands=['reset'])
def reset_handler(message):
    """Reset optimisé"""
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions[user_id]['conversation'] = []
    bot.send_message(message.chat.id, "🔄 **Conversation réinitialisée !**")

# ==================== GESTION DES GROUPES ====================
@bot.message_handler(content_types=['new_chat_members'])
def new_group_handler(message):
    """Quand le bot est ajouté à un groupe"""
    if bot.get_me().id in [user.id for user in message.new_chat_members]:
        group_id = message.chat.id
        group_name = message.chat.title
        
        # Obtenir le nombre de membres
        try:
            member_count = bot.get_chat_members_count(group_id)
        except:
            member_count = 0
        
        # Sauvegarder dans la base
        conn = sqlite3.connect('bot_groups.db')
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO groups 
                     (group_id, group_name, member_count, added_date)
                     VALUES (?, ?, ?, ?)''', 
                     (group_id, group_name, member_count, datetime.now()))
        conn.commit()
        conn.close()
        
        # Message de bienvenue dans le groupe
        welcome_msg = f"""
🤖 **{BOT_NAME}** - Merci de m'avoir ajouté !

👑 Créé par {CREATOR}
🚀 Assistant IA optimisé

💫 **Je peux aider avec :**
• Réponses intelligentes
• Génération de code
• Analyse de texte
• Et bien plus !

📊 **Ce groupe contribue au déblocage du premium gratuit !**
        """
        bot.send_message(group_id, welcome_msg, parse_mode='Markdown')
        
        # Vérifier si conditions remplies
        if check_group_requirements():
            activate_premium_for_all()
            # Annonce globale (simplifiée)
            announcement = """
🎉 **FÉLICITATIONS ! PREMIUM DÉBLOQUÉ !**

✅ Les conditions sont remplies !
🚀 **Version Premium maintenant activée pour tous !**

✨ **Toutes les fonctionnalités sont maintenant disponibles :**
• Réponses IA illimitées
• Génération de code
• Analyse avancée
• Et bien plus !

👑 Merci à notre communauté !
            """
            # Envoyer un message système
            bot.send_message(group_id, announcement, parse_mode='Markdown')

# ==================== MOTEUR IA AVEC RESTRICTION PREMIUM ====================
@bot.message_handler(func=lambda message: True)
def optimized_ai_handler(message):
    """Moteur IA avec système premium"""
    user_id = message.from_user.id
    
    # 🔒 VÉRIFICATION PREMIUM
    if not check_premium_access(user_id):
        qualified, total = get_group_stats()
        restriction_msg = f"""
🔒 **FONCTIONNALITÉ BLOQUÉE - VERSION LIMITÉE**

🚫 **Accès restreint** - Le bot ne répond pas aux messages tant que le premium n'est pas débloqué.

{get_progress_bar()}

📊 **Progression actuelle :**
• Groupes qualifiés : {qualified}/5
• Total groupes : {total}

🎁 **Débloquez le premium gratuitement en ajoutant le bot à {5-qualified} groupe(s) supplémentaire(s) de 60+ membres.**

👇 **Ajoutez le bot à des groupes pour activer les réponses :**
        """
        bot.reply_to(message, restriction_msg, parse_mode='Markdown', reply_markup=create_premium_menu())
        return
    
    # ✅ UTILISATEUR PREMIUM - Réponse normale
    user_session = get_user_session(user_id)
    user_session['last_active'] = datetime.now()
    
    intent = detect_quick_intent(message.text)
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # CONSTRUCTION OPTIMISÉE POUR GROQ
        messages = [{"role": "system", "content": create_optimized_prompt()}]
        
        # CONTEXTE LIMITÉ (2 messages max)
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-2:])
        
        # MESSAGE COURANT LIMITÉ
        user_message = message.text[:400]
        messages.append({"role": "user", "content": user_message})

        # PAYLOAD OPTIMISÉ POUR GROQ
        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            # SAUVEGARDE OPTIMISÉE
            user_session['conversation'].extend([
                {"role": "user", "content": user_message[:200]},
                {"role": "assistant", "content": answer[:500]}
            ])
            
            # LIMITE STRICTE HISTORIQUE
            if len(user_session['conversation']) > 6:
                user_session['conversation'] = user_session['conversation'][-6:]
            
            # TRAITEMENT CODE OPTIMISÉ
            code_blocks = re.findall(r'```(?:[\w]*)\n?(.*?)```', answer, re.DOTALL)
            
            if code_blocks:
                response_text = "💻 **CODE**\n\n"
                for i, code in enumerate(code_blocks, 1):
                    lang = "python"
                    code_lower = code.lower()
                    if any(x in code_lower for x in ['<html', '<div']): lang = "html"
                    elif any(x in code_lower for x in ['function', 'const ']): lang = "javascript"
                    elif any(x in code_lower for x in ['public class']): lang = "java"
                    
                    response_text += f"```{lang}\n{code.strip()}\n```\n\n"
                
                response_text += f"👑 **Expert : {CREATOR}**"
                bot.reply_to(message, response_text, parse_mode='Markdown')
            else:
                # RÉPONSE NORMALE
                bot.reply_to(message, answer)
            
            # PHOTO CONTEXTUELLE AVEC BOUTON SUPPORT
            if should_send_photo(intent):
                try:
                    time.sleep(0.5)
                    bot.send_photo(
                        message.chat.id, 
                        MAIN_PHOTO,
                        caption=f"📸 **{CREATOR}** - Merci pour votre confiance ! 💝",
                        parse_mode='Markdown',
                        reply_markup=create_main_menu()
                    )
                except:
                    pass
                
        else:
            if response.status_code == 400:
                bot.reply_to(message, "🔄 **Message trop long** - Réessaie plus court !")
            elif response.status_code == 429:
                bot.reply_to(message, "⏱️ **Trop de requêtes** - Attends 1 minute !")
            else:
                bot.reply_to(message, f"❌ **Erreur {response.status_code}** - Réessaie !")
            
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ **Timeout** - Question plus courte ?")
        
    except Exception as e:
        bot.reply_to(message, "🔧 **Erreur technique** - Réessaie !")

# ==================== CALLBACK QUERY ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Gère les clics sur les boutons"""
    if call.data == "check_status":
        user_id = call.from_user.id
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Vous avez la version PREMIUM !")
        else:
            qualified, total = get_group_stats()
            bot.answer_callback_query(call.id, f"📊 Progression: {qualified}/5 groupes | Total: {total}")

# ==================== NETTOYAGE OPTIMISÉ ====================
def cleanup_sessions():
    """Nettoyage sessions inactives"""
    now = datetime.now()
    inactive_users = []
    
    for user_id, session in user_sessions.items():
        if (now - session['last_active']).total_seconds() > 7200:
            inactive_users.append(user_id)
    
    for user_id in inactive_users:
        del user_sessions[user_id]

# ==================== DÉMARRAGE OPTIMISÉ ====================
if __name__ == "__main__":
    # Initialiser la base de données
    init_db()
    
    print(f"""
🎯 {BOT_NAME} - {VERSION}
👑 Créateur : {CREATOR}
📸 Photo intégrée dans le menu
💝 Bouton Support Créateur activé
🔒 Système Premium Gratuit intégré
⚡ Modèle : {current_model}

🚀 **Fonctionnalités :**
✓ Système premium gratuit via groupes
✓ Bot ne répond pas sans premium
✓ Barre de progression
✓ Gestion automatique des groupes
✓ Interface utilisateur intuitive

💫 **Le bot restreint les réponses jusqu'à ce que 5 groupes de 60+ membres soient atteints !**
    """)
    
    # Nettoyage automatique léger
    import threading
    def schedule_cleanup():
        while True:
            time.sleep(3600)
            cleanup_sessions()
    
    threading.Thread(target=schedule_cleanup, daemon=True).start()
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Arrêt : {e}")
        print(f"👑 Contact : {CREATOR}")
