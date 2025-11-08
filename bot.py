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

# ==================== CONFIGURATION ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Soszoe"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition Groq Optimisée"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
current_model = "llama-3.1-8b-instant"

# 🔐 ADMIN
ADMIN_ID = 7908680781
ADMIN_USERNAME = "soszoe"
ADMIN_PASSWORD = "KING1998"

# Stockage
user_sessions = {}
admin_sessions = {}
user_messages = {}  # Stocke les messages des utilisateurs

# ==================== BASE DE DONNÉES ====================
def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Table des groupes
    c.execute('''CREATE TABLE IF NOT EXISTS groups
                 (group_id INTEGER PRIMARY KEY, 
                  group_name TEXT,
                  member_count INTEGER,
                  added_date TIMESTAMP)''')
    
    # Table des utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS user_access
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  has_premium BOOLEAN DEFAULT FALSE,
                  premium_since TIMESTAMP,
                  added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table des messages (pour l'historique)
    c.execute('''CREATE TABLE IF NOT EXISTS user_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  username TEXT,
                  first_name TEXT,
                  message_text TEXT,
                  message_date TIMESTAMP,
                  replied BOOLEAN DEFAULT FALSE)''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

def repair_database():
    """Répare la structure de la base de données"""
    try:
        conn = sqlite3.connect('bot_groups.db')
        c = conn.cursor()
        
        # Vérifier et ajouter les colonnes manquantes
        columns_to_add = [
            ('user_access', 'username', 'TEXT'),
            ('user_access', 'first_name', 'TEXT'),
            ('user_access', 'premium_since', 'TIMESTAMP')
        ]
        
        for table, column, col_type in columns_to_add:
            try:
                c.execute(f'SELECT {column} FROM {table} LIMIT 1')
            except sqlite3.OperationalError:
                print(f"🔄 Ajout de la colonne {column}...")
                c.execute(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')
                conn.commit()
                print(f"✅ Colonne {column} ajoutée")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur réparation DB: {e}")
        return False

def check_group_requirements():
    """Vérifie si 5 groupes sont atteints"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM groups')
    total_groups = c.fetchone()[0]
    conn.close()
    return total_groups >= 5

def check_premium_access(user_id):
    """Vérifie si un utilisateur a le premium"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT has_premium FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0]

def activate_user_premium(user_id):
    """Active le premium pour un utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, has_premium, premium_since) VALUES (?, ?, ?)''', 
                 (user_id, True, datetime.now()))
    conn.commit()
    conn.close()

def deactivate_user_premium(user_id):
    """Désactive le premium pour un utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET has_premium = FALSE, premium_since = NULL WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    """Récupère tous les utilisateurs"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium FROM user_access')
    users = c.fetchall()
    conn.close()
    return users

def get_premium_users():
    """Récupère les utilisateurs premium"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name FROM user_access WHERE has_premium = TRUE')
    users = c.fetchall()
    conn.close()
    return users

def get_user_info(user_id):
    """Récupère les infos d'un utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium, premium_since FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_group_stats():
    """Récupère le nombre de groupes"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM groups')
    total = c.fetchone()[0]
    conn.close()
    return total

def add_group_to_db(group_id, group_name, member_count):
    """Ajoute un groupe à la base"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO groups 
                 (group_id, group_name, member_count, added_date)
                 VALUES (?, ?, ?, ?)''', 
                 (group_id, group_name, member_count, datetime.now()))
    conn.commit()
    conn.close()

def register_user(user_id, username, first_name):
    """Enregistre un utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, username, first_name, added_date) 
                 VALUES (?, ?, ?, ?)''', 
                 (user_id, username, first_name, datetime.now()))
    conn.commit()
    conn.close()

def save_user_message(user_id, username, first_name, message_text):
    """Sauvegarde un message d'un utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT INTO user_messages 
                 (user_id, username, first_name, message_text, message_date)
                 VALUES (?, ?, ?, ?, ?)''', 
                 (user_id, username, first_name, message_text, datetime.now()))
    conn.commit()
    conn.close()

def get_user_messages(user_id=None):
    """Récupère les messages des utilisateurs"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    if user_id:
        c.execute('''SELECT * FROM user_messages 
                     WHERE user_id = ? ORDER BY message_date DESC LIMIT 50''', (user_id,))
    else:
        c.execute('''SELECT * FROM user_messages 
                     ORDER BY message_date DESC LIMIT 100''')
    
    messages = c.fetchall()
    conn.close()
    return messages

def get_recent_messages(limit=20):
    """Récupère les messages récents"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM user_messages 
                 ORDER BY message_date DESC LIMIT ?''', (limit,))
    messages = c.fetchall()
    conn.close()
    return messages

# ==================== FONCTIONS ADMIN ====================
def is_admin(user_id):
    """Vérifie si l'utilisateur est admin"""
    return user_id == ADMIN_ID

def verify_admin_password(password):
    """Vérifie le mot de passe admin"""
    return password == ADMIN_PASSWORD

def is_admin_authenticated(user_id):
    """Vérifie si l'admin est authentifié"""
    if user_id not in admin_sessions:
        return False
    session = admin_sessions[user_id]
    if (datetime.now() - session['auth_time']).total_seconds() > 1800:  # 30 minutes
        del admin_sessions[user_id]
        return False
    return session['authenticated']

# ==================== FONCTIONS UTILISATEURS ====================
def get_user_session(user_id):
    """Gère les sessions utilisateur"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation': [],
            'last_active': datetime.now()
        }
    return user_sessions[user_id]

def get_progress_bar():
    """Affiche une barre de progression"""
    total = get_group_stats()
    filled = '█' * min(total, 5)
    empty = '░' * (5 - min(total, 5))
    return f"`[{filled}{empty}]` {total}/5"

def create_main_menu():
    """Menu principal"""
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    comment_button = InlineKeyboardButton("📝 Commentaire", callback_data="send_comment")
    keyboard.add(support_button)
    keyboard.add(comment_button)
    return keyboard

def create_premium_menu():
    """Menu pour débloquer le premium"""
    keyboard = InlineKeyboardMarkup()
    
    try:
        bot_user = bot.get_me()
        bot_username = bot_user.username
        add_button = InlineKeyboardButton(
            "📥 Ajouter à un groupe", 
            url=f"https://t.me/{bot_username}?startgroup=true"
        )
    except:
        add_button = InlineKeyboardButton("📥 Ajouter à un groupe", url="https://t.me/")
    
    status_button = InlineKeyboardButton("📊 Vérifier le statut", callback_data="check_status")
    premium_button = InlineKeyboardButton("🎁 Activer Premium", callback_data="activate_premium")
    comment_button = InlineKeyboardButton("📝 Commentaire", callback_data="send_comment")
    
    keyboard.add(add_button)
    keyboard.add(status_button)
    keyboard.add(premium_button)
    keyboard.add(comment_button)
    
    return keyboard

def create_admin_menu(user_id=None):
    """Menu administrateur - Affiche Auth si pas authentifié"""
    keyboard = InlineKeyboardMarkup()
    
    if user_id and is_admin_authenticated(user_id):
        # ✅ ADMIN AUTHENTIFIÉ - Menu complet débloqué
        stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="admin_stats")
        users_btn = InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_users")
        premium_btn = InlineKeyboardButton("⭐ Gérer Premium", callback_data="admin_premium")
        broadcast_btn = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
        mail_btn = InlineKeyboardButton("📨 Mail Historique", callback_data="admin_mail")
        commands_btn = InlineKeyboardButton("🛠️ Commandes", callback_data="admin_commands")
        help_btn = InlineKeyboardButton("❓ Aide Admin", callback_data="admin_help")
        
        keyboard.add(stats_btn, users_btn)
        keyboard.add(premium_btn, broadcast_btn)
        keyboard.add(mail_btn, commands_btn)
        keyboard.add(help_btn)
    else:
        # 🔐 ADMIN NON AUTHENTIFIÉ - Bouton Auth seulement
        auth_btn = InlineKeyboardButton("🔐 Authentification Admin", callback_data="admin_auth")
        keyboard.add(auth_btn)
    
    return keyboard

def create_optimized_prompt():
    """Prompt pour l'IA"""
    return f"""Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Expert en programmation, création, analyse et aide générale. Sois naturel, précis et utile. Réponds dans la langue de l'utilisateur."""

# ==================== HANDLERS UTILISATEURS ====================
@bot.message_handler(commands=['start', 'aide', 'help'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        # Enregistrer l'utilisateur
        register_user(user_id, username, first_name)
        
        # ✅ PROPRIÉTAIRE - Premium immédiat
        if is_admin(user_id):
            activate_user_premium(user_id)
            
            # Vérifier si admin est déjà authentifié
            if is_admin_authenticated(user_id):
                menu_text = "👑 **Mode Propriétaire Activé**\n\n⭐ **Premium activé pour vous !**\n🔓 **Session admin active** - Accès complet débloqué !"
            else:
                menu_text = "👑 **Mode Propriétaire Activé**\n\n⭐ **Premium activé pour vous !**\n🔐 **Authentification requise** - Cliquez sur 'Auth' pour débloquer le panel admin."
            
            bot.send_message(
                message.chat.id,
                menu_text,
                reply_markup=create_admin_menu(user_id),
                parse_mode='Markdown'
            )
            return
        
        # Photo du créateur
        try:
            bot.send_photo(
                message.chat.id, 
                MAIN_PHOTO,
                caption=f"📸 **{CREATOR}** - Créateur du bot\n*Votre expert en IA* 👑",
                parse_mode='Markdown'
            )
            time.sleep(0.5)
        except:
            pass
        
        if check_premium_access(user_id):
            menu = f"""
🎉 **{BOT_NAME}** - {VERSION} **PREMIUM**

⭐ **Version Premium Activée !**

💫 **Fonctionnalités débloquées :**
• 💻 Programmation & Code
• 🎨 Création & Rédaction  
• 📊 Analyse & Conseil
• 🌍 Traduction
• 💬 Conversation naturelle

✨ **Envoyez-moi un message pour commencer !**
"""
            bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=create_main_menu())
        else:
            total = get_group_stats()
            
            if total >= 5:
                menu = f"""
🎊 **{BOT_NAME}** - PRÊT POUR LE PREMIUM !

{get_progress_bar()}

✅ **Conditions remplies !** 
5/5 groupes atteints !

🎁 **Cliquez sur "Activer Premium" ci-dessous**
pour débloquer toutes les fonctionnalités !

🚀 **L'IA vous attend !**
"""
            else:
                menu = f"""
🔒 **{BOT_NAME}** - {VERSION} **LIMITÉE**

🚀 **Assistant IA optimisé pour Groq**
*Version limitée - Débloquez le premium gratuitement !*

{get_progress_bar()}

🎁 **Conditions pour le Premium GRATUIT :**
• ➕ Bot dans 5 groupes
• ✅ Déblocage immédiat après validation

📊 **Statut actuel :**
• Groupes : {total}/5

💡 **Comment débloquer :**
1. Cliquez sur "Ajouter à un groupe" ci-dessous
2. Choisissez n'importe quel groupe
3. Le premium se débloque à 5 groupes
"""
            
            bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=create_premium_menu())
            
    except Exception as e:
        print(f"❌ Erreur start: {e}")
        bot.reply_to(message, "❌ Erreur temporaire. Réessayez.")

@bot.message_handler(commands=['test'])
def test_command(message):
    """Commande test"""
    bot.reply_to(message, "✅ **Bot actif !**\n🚀 Fonctionne parfaitement !")

@bot.message_handler(commands=['reset'])
def reset_handler(message):
    """Réinitialise la conversation"""
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions[user_id]['conversation'] = []
    bot.reply_to(message, "🔄 **Conversation réinitialisée !**\nNouveau départ !")

@bot.message_handler(commands=['status'])
def status_handler(message):
    """Vérifie le statut"""
    user_id = message.from_user.id
    total = get_group_stats()
    
    if check_premium_access(user_id):
        bot.reply_to(message, "⭐ **Statut : PREMIUM ACTIVÉ**\n✨ Profitez de l'IA complète !")
    else:
        bot.reply_to(message, 
                   f"🔒 **Statut : VERSION LIMITÉE**\n\n{get_progress_bar()}\n\nAjoutez le bot à {5-total} groupe(s) pour débloquer le premium.",
                   reply_markup=create_premium_menu())

@bot.message_handler(commands=['commentaire', 'comment'])
def comment_command(message):
    """Commande pour envoyer un commentaire au créateur"""
    msg = bot.reply_to(message, "📝 **ENVOYER UN COMMENTAIRE**\n\nÉcrivez votre message pour le créateur :")
    bot.register_next_step_handler(msg, process_comment)

def process_comment(message):
    """Traite l'envoi d'un commentaire"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    first_name = message.from_user.first_name or "Utilisateur"
    comment_text = message.text
    
    # Sauvegarder le message dans la base de données
    save_user_message(user_id, username, first_name, comment_text)
    
    # Notifier l'admin
    try:
        admin_message = f"📨 **NOUVEAU COMMENTAIRE**\n\n👤 De: {first_name} (@{username})\n🆔 ID: `{user_id}`\n💬 Message:\n{comment_text}"
        bot.send_message(ADMIN_ID, admin_message, parse_mode='Markdown')
    except Exception as e:
        print(f"❌ Erreur envoi admin: {e}")
    
    bot.reply_to(message, "✅ **Commentaire envoyé !**\n\nMerci pour votre feedback ! Le créateur le recevra rapidement.")

# ==================== GESTION GROUPES ====================
@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Quand le bot est ajouté à un groupe"""
    try:
        if bot.get_me().id in [user.id for user in message.new_chat_members]:
            group_id = message.chat.id
            group_name = message.chat.title or "Groupe sans nom"
            
            try:
                member_count = bot.get_chat_members_count(group_id)
            except:
                member_count = 0
            
            add_group_to_db(group_id, group_name, member_count)
            
            welcome_msg = f"""
🤖 **{BOT_NAME}** - Merci de m'avoir ajouté !

👑 Créé par {CREATOR}
🚀 Assistant IA optimisé

📊 **Ce groupe compte pour le déblocage du premium gratuit !**

💡 Utilisez /start en privé pour voir votre progression.
"""
            bot.send_message(group_id, welcome_msg, parse_mode='Markdown')
            
    except Exception as e:
        print(f"❌ Erreur nouveau groupe: {e}")

# ==================== MOTEUR IA ====================
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gère tous les messages"""
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    
    if not check_premium_access(user_id):
        total = get_group_stats()
        if total >= 5:
            bot.reply_to(message, 
                       "🎊 **PRÊT POUR LE PREMIUM !**\n\n✅ 5/5 groupes atteints !\n\n🎁 Cliquez sur 'Activer Premium' pour débloquer l'IA !",
                       reply_markup=create_premium_menu())
        else:
            bot.reply_to(message, 
                       f"🔒 **Version limitée**\n\n{get_progress_bar()}\n\nAjoutez le bot à {5-total} groupe(s) pour débloquer l'IA.",
                       reply_markup=create_premium_menu())
        return
    
    # ✅ UTILISATEUR PREMIUM - Traitement IA
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        if not GROQ_API_KEY:
            bot.reply_to(message, "❌ Service IA temporairement indisponible.")
            return
            
        user_session = get_user_session(user_id)
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": create_optimized_prompt()}]
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-4:])  # Garde les 4 derniers messages
        
        user_message = message.text[:500]  # Limite la longueur
        messages.append({"role": "user", "content": user_message})

        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            
            # Mise à jour de la conversation
            user_session['conversation'].extend([
                {"role": "user", "content": user_message[:300]},
                {"role": "assistant", "content": answer[:600]}
            ])
            
            # Limite la taille de la conversation
            if len(user_session['conversation']) > 8:
                user_session['conversation'] = user_session['conversation'][-8:]
            
            user_session['last_active'] = datetime.now()
            
            bot.reply_to(message, answer)
        else:
            error_msg = "❌ Erreur de service. Réessayez dans quelques instants."
            if response.status_code == 429:
                error_msg = "⏰ Trop de requêtes. Veuillez patienter quelques secondes."
            elif response.status_code == 401:
                error_msg = "🔑 Erreur d'authentification API."
            
            bot.reply_to(message, error_msg)
            
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Délai d'attente dépassé. Réessayez.")
    except Exception as e:
        print(f"❌ Erreur IA: {e}")
        bot.reply_to(message, "🔧 Service temporairement indisponible. Réessayez plus tard.")

# ==================== COMMANDES ADMIN ====================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Panel admin principal"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Accès réservé au propriétaire.")
        return
    
    bot.send_message(
        message.chat.id,
        "👑 **Panel Administrateur**\n\nSélectionnez une option :",
        reply_markup=create_admin_menu(user_id),
        parse_mode='Markdown'
    )

def require_admin_auth(func):
    """Décorateur pour exiger l'authentification admin"""
    def wrapper(message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.reply_to(message, "❌ Accès réservé au propriétaire.")
            return
        
        if not is_admin_authenticated(user_id):
            msg = bot.reply_to(message, "🔐 **Authentification requise**\n\nVeuillez entrer le mot de passe admin :")
            bot.register_next_step_handler(msg, process_admin_auth_for_command, func, message)
            return
        
        # Si authentifié, exécuter la commande
        func(message)
    
    return wrapper

def process_admin_auth_for_command(message, original_func, original_message):
    """Traite l'authentification pour une commande spécifique"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if verify_admin_password(message.text.strip()):
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        bot.send_message(message.chat.id, "✅ **Authentification réussie !**")
        # Exécuter la commande originale après authentification
        original_func(original_message)
    else:
        bot.reply_to(message, "❌ **Mot de passe incorrect.**\n\nUtilisez à nouveau la commande admin.")

@bot.message_handler(commands=['mail'])
@require_admin_auth
def mail_command(message):
    """Commande pour voir l'historique des messages (Admin seulement)"""
    show_mail_history(message)

def show_mail_history(message, page=1):
    """Affiche l'historique des messages"""
    messages = get_recent_messages(limit=50)
    
    if not messages:
        bot.reply_to(message, "📭 **Aucun message reçu**\n\nAucun utilisateur n'a encore envoyé de commentaire.")
        return
    
    items_per_page = 10
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_messages = messages[start_idx:end_idx]
    
    response = f"📨 **HISTORIQUE DES MESSAGES**\n\n"
    response += f"📊 Total messages: {len(messages)}\n"
    response += f"📄 Page {page}/{(len(messages) + items_per_page - 1) // items_per_page}\n\n"
    
    for i, msg in enumerate(page_messages, start_idx + 1):
        msg_id, user_id, username, first_name, message_text, message_date, replied = msg
        username_display = f"@{username}" if username else "Sans username"
        date_str = message_date.split('.')[0] if isinstance(message_date, str) else message_date.strftime("%d/%m/%Y %H:%M")
        
        response += f"**{i}. {first_name}** ({username_display})\n"
        response += f"🆔 `{user_id}` | 📅 {date_str}\n"
        response += f"💬 {message_text[:100]}{'...' if len(message_text) > 100 else ''}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Ajouter la pagination
    keyboard = InlineKeyboardMarkup()
    if page > 1:
        keyboard.add(InlineKeyboardButton("⬅️ Page précédente", callback_data=f"mail_page_{page-1}"))
    if end_idx < len(messages):
        keyboard.add(InlineKeyboardButton("Page suivante ➡️", callback_data=f"mail_page_{page+1}"))
    
    keyboard.add(InlineKeyboardButton("🔄 Actualiser", callback_data="admin_mail"))
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(commands=['stats'])
@require_admin_auth
def stats_command(message):
    """Statistiques du bot"""
    total_users = len(get_all_users())
    premium_users = len(get_premium_users())
    groups_count = get_group_stats()
    total_messages = len(get_user_messages())
    
    stats_text = f"""
📊 **STATISTIQUES DU BOT**

👥 **Utilisateurs :**
• Total : {total_users}
• Premium : {premium_users}
• Standard : {total_users - premium_users}
• Taux premium : {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%

📁 **Groupes :** {groups_count}/5
📨 **Messages reçus :** {total_messages}
🕐 **Dernière MAJ :** {datetime.now().strftime('%H:%M %d/%m/%Y')}

👑 **Admin :** {CREATOR}
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['users'])
@require_admin_auth
def users_command(message):
    """Lister tous les utilisateurs"""
    users = get_all_users()
    if not users:
        bot.reply_to(message, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **LISTE DES UTILISATEURS**\n\n"
    for i, user in enumerate(users[:20], 1):
        user_id, username, first_name, has_premium = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "Sans username"
        response += f"{i}. {premium_status} {first_name} ({username_display}) - ID: `{user_id}`\n"
    
    if len(users) > 20:
        response += f"\n... et {len(users) - 20} autres utilisateurs"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['premium_users'])
@require_admin_auth
def premium_users_command(message):
    """Lister les utilisateurs premium"""
    premium_users = get_premium_users()
    if not premium_users:
        bot.reply_to(message, "⭐ Aucun utilisateur premium.")
        return
    
    response = "⭐ **UTILISATEURS PREMIUM**\n\n"
    for i, user in enumerate(premium_users, 1):
        user_id, username, first_name = user
        username_display = f"@{username}" if username else "Sans username"
        response += f"{i}. {first_name} ({username_display}) - ID: `{user_id}`\n"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['give_premium'])
@require_admin_auth
def give_premium_command(message):
    """Donner le premium à un utilisateur"""
    msg = bot.reply_to(message, "⭐ **DONNER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_give_premium)

def process_give_premium(message):
    """Traite l'ajout de premium"""
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        activate_user_premium(target_user_id)
        
        try:
            bot.send_message(target_user_id, 
                           "🎉 **FÉLICITATIONS !**\n\n⭐ **Premium activé !**\n\n✨ Profitez de toutes les fonctionnalités IA !\n💬 Envoyez-moi un message pour commencer !")
        except:
            pass
        
        bot.reply_to(message, f"✅ **Premium accordé à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['remove_premium'])
@require_admin_auth
def remove_premium_command(message):
    """Retirer le premium à un utilisateur"""
    msg = bot.reply_to(message, "🔒 **RETIRER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_remove_premium)

def process_remove_premium(message):
    """Traite le retrait de premium"""
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        deactivate_user_premium(target_user_id)
        bot.reply_to(message, f"✅ **Premium retiré à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['user_info'])
@require_admin_auth
def user_info_command(message):
    """Informations sur un utilisateur"""
    msg = bot.reply_to(message, "🔍 **INFORMATIONS UTILISATEUR**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_user_info)

def process_user_info(message):
    """Traite la recherche d'utilisateur"""
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        user_info = get_user_info(target_user_id)
        
        if user_info:
            user_id, username, first_name, has_premium, premium_since = user_info
            premium_status = "⭐ PREMIUM" if has_premium else "🔒 STANDARD"
            since = premium_since.strftime("%d/%m/%Y %H:%M") if premium_since else "Non premium"
            username_display = f"@{username}" if username else "Aucun"
            
            # Récupérer les messages de l'utilisateur
            user_messages = get_user_messages(target_user_id)
            
            response = f"""
👤 **INFORMATIONS UTILISATEUR**

🆔 ID: `{user_id}`
📛 Nom: {first_name}
👤 Username: {username_display}
🎯 Statut: {premium_status}
📅 Premium depuis: {since}
📨 Messages envoyés: {len(user_messages)}
"""
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Utilisateur non trouvé.")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['broadcast'])
@require_admin_auth
def broadcast_command(message):
    """Envoyer un message à tous les utilisateurs"""
    msg = bot.reply_to(message, "📢 **BROADCAST**\n\nEnvoyez le message à diffuser :")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    """Traite le broadcast"""
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    broadcast_text = message.text
    users = get_all_users()
    total_users = len(users)
    
    progress_msg = bot.send_message(message.chat.id, f"📤 **Diffusion en cours...**\n0/{total_users} utilisateurs")
    
    success_count = 0
    fail_count = 0
    
    for i, user in enumerate(users):
        try:
            bot.send_message(user[0], f"📢 **Message de {CREATOR}**\n\n{broadcast_text}")
            success_count += 1
        except:
            fail_count += 1
        
        if i % 10 == 0:
            try:
                bot.edit_message_text(
                    f"📤 **Diffusion en cours...**\n{i+1}/{total_users} utilisateurs",
                    message.chat.id,
                    progress_msg.message_id
                )
            except:
                pass
        
        time.sleep(0.1)
    
    result_text = f"""
✅ **BROADCAST TERMINÉ**

📊 **Résultats :**
• ✅ Envoyés : {success_count}
• ❌ Échecs : {fail_count}
• 📝 Total : {total_users}
"""
    bot.send_message(message.chat.id, result_text, parse_mode='Markdown')

@bot.message_handler(commands=['premium_all'])
@require_admin_auth
def premium_all_command(message):
    """Activer le premium pour tous"""
    users = get_all_users()
    for user in users:
        activate_user_premium(user[0])
    
    bot.reply_to(message, f"⭐ **Premium activé pour tous les {len(users)} utilisateurs !**")

@bot.message_handler(commands=['remove_all_premium'])
@require_admin_auth
def remove_all_premium_command(message):
    """Retirer le premium à tous (sauf admin)"""
    users = get_all_users()
    count = 0
    for user in users:
        if user[0] != ADMIN_ID:
            deactivate_user_premium(user[0])
            count += 1
    
    bot.reply_to(message, f"🔒 **Premium retiré à {count} utilisateurs !**")

@bot.message_handler(commands=['commands', 'cmd'])
@require_admin_auth
def admin_commands_command(message):
    """Affiche toutes les commandes admin"""
    commands_text = """
🛠️ **TOUTES LES COMMANDES ADMIN**

📊 **STATISTIQUES :**
`/stats` - Statistiques complètes du bot
`/users` - Liste tous les utilisateurs
`/premium_users` - Liste les utilisateurs premium

👤 **GESTION UTILISATEURS :**
`/user_info` - Infos détaillées sur un utilisateur
`/mail` - Historique des messages reçus

⭐ **GESTION PREMIUM :**
`/give_premium` - Donner premium à un utilisateur
`/remove_premium` - Retirer premium à un utilisateur
`/premium_all` - Premium pour TOUS les utilisateurs
`/remove_all_premium` - Retirer premium à tous (sauf vous)

📢 **COMMUNICATION :**
`/broadcast` - Envoyer un message à tous

🔧 **UTILITAIRES :**
`/admin` - Panel d'authentification
`/commands` - Ce menu des commandes

💡 **ASTUCE :** Utilisez le panel `/admin` pour une navigation facile !
"""
    
    bot.reply_to(message, commands_text, parse_mode='Markdown')

# ==================== CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Gère tous les callbacks"""
    user_id = call.from_user.id
    
    if call.data == "check_status":
        total = get_group_stats()
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Premium activé !")
        else:
            bot.answer_callback_query(call.id, f"📊 {total}/5 groupes - {5-total} manquant(s)")
    
    elif call.data == "activate_premium":
        total = get_group_stats()
        if total >= 5:
            activate_user_premium(user_id)
            bot.answer_callback_query(call.id, "🎉 Premium activé !")
            
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="🎉 **Premium activé avec succès !**\n\n✨ **Profitez de toutes les fonctionnalités IA !**\n💬 Envoyez-moi un message pour commencer !",
                    parse_mode='Markdown',
                    reply_markup=create_main_menu()
                )
            except:
                bot.send_message(call.message.chat.id, "🎉 **Premium activé avec succès !**\n\n✨ Profitez de l'IA !")
        else:
            bot.answer_callback_query(call.id, f"❌ {5-total} groupe(s) manquant(s)")
    
    elif call.data == "send_comment":
        msg = bot.send_message(call.message.chat.id, "📝 **ENVOYER UN COMMENTAIRE**\n\nÉcrivez votre message pour le créateur :")
        bot.register_next_step_handler(msg, process_comment)
        bot.answer_callback_query(call.id, "📝 Commentaire")
    
    elif call.data == "admin_auth":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Accès réservé")
            return
        
        msg = bot.send_message(call.message.chat.id, "🔐 **AUTHENTIFICATION ADMIN**\n\nVeuillez entrer le mot de passe :")
        bot.register_next_step_handler(msg, process_admin_auth_callback, call.message)
        bot.answer_callback_query(call.id, "🔐 Authentification")
    
    elif call.data == "admin_stats":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        total_users = len(get_all_users())
        premium_users = len(get_premium_users())
        groups_count = get_group_stats()
        total_messages = len(get_user_messages())
        
        stats_text = f"""
📊 **STATISTIQUES ADMIN**

👥 Utilisateurs: {total_users}
⭐ Premium: {premium_users}
📁 Groupes: {groups_count}/5
📨 Messages: {total_messages}
🕐 MAJ: {datetime.now().strftime('%H:%M %d/%m/%Y')}
"""
        bot.answer_callback_query(call.id, "📊 Statistiques")
        bot.send_message(call.message.chat.id, stats_text, parse_mode='Markdown')
    
    elif call.data == "admin_users":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        users = get_all_users()
        response = "👥 **UTILISATEURS**\n\n"
        for i, user in enumerate(users[:15], 1):
            user_id, username, first_name, has_premium = user
            status = "⭐" if has_premium else "🔒"
            username_display = f"@{username}" if username else "Sans username"
            response += f"{i}. {status} {first_name} ({username_display}) - ID: `{user_id}`\n"
        
        if len(users) > 15:
            response += f"\n... et {len(users) - 15} autres"
        
        bot.answer_callback_query(call.id, "👥 Utilisateurs")
        bot.send_message(call.message.chat.id, response, parse_mode='Markdown')
    
    elif call.data == "admin_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        keyboard = InlineKeyboardMarkup()
        give_btn = InlineKeyboardButton("➕ Donner Premium", callback_data="admin_give_premium")
        remove_btn = InlineKeyboardButton("➖ Retirer Premium", callback_data="admin_remove_premium")
        all_btn = InlineKeyboardButton("⭐ À Tous", callback_data="admin_premium_all")
        remove_all_btn = InlineKeyboardButton("🔒 Retirer à Tous", callback_data="admin_remove_all_premium")
        
        keyboard.add(give_btn, remove_btn)
        keyboard.add(all_btn, remove_all_btn)
        
        bot.answer_callback_query(call.id, "⭐ Gestion Premium")
        bot.send_message(call.message.chat.id, "⭐ **GESTION PREMIUM**", reply_markup=keyboard)
    
    elif call.data == "admin_broadcast":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        msg = bot.send_message(call.message.chat.id, "📢 **BROADCAST**\n\nEnvoyez le message à diffuser :")
        bot.register_next_step_handler(msg, process_broadcast)
        bot.answer_callback_query(call.id, "📢 Broadcast")
    
    elif call.data == "admin_mail":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        show_mail_history(call.message)
        bot.answer_callback_query(call.id, "📨 Mail Historique")
    
    elif call.data == "admin_commands":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        admin_commands_command(call.message)
        bot.answer_callback_query(call.id, "🛠️ Commandes")
    
    elif call.data == "admin_help":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        help_text = """
❓ **AIDE ADMINISTRATEUR**

💡 **Conseils d'utilisation :**

🔐 **Authentification :**
- Cliquez sur "Auth" pour vous authentifier
- Session valide 30 minutes
- Une fois authentifié, tous les boutons sont débloqués

📊 **Pour les statistiques :**
- Utilisez "Statistiques" pour un aperçu général
- "Utilisateurs" pour voir tous les utilisateurs

⭐ **Gestion du premium :**
- "Gérer Premium" pour le menu complet
- Donner/retirer premium individuellement ou en masse

📨 **Système de messages :**
- Les utilisateurs utilisent `/commentaire`
- Vous consultez avec "Mail Historique"
- Notifications en temps réel

📢 **Communication :**
- "Broadcast" pour messages massifs
- Utilisez avec modération

🆘 **Support :** Contactez @Soszoe pour assistance
"""
        bot.send_message(call.message.chat.id, help_text, parse_mode='Markdown')
        bot.answer_callback_query(call.id, "❓ Aide Admin")
    
    elif call.data.startswith("mail_page_"):
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        page = int(call.data.split("_")[2])
        show_mail_history(call.message, page)
        bot.answer_callback_query(call.id, f"📄 Page {page}")
    
    elif call.data == "admin_give_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        msg = bot.send_message(call.message.chat.id, "⭐ **DONNER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
        bot.register_next_step_handler(msg, process_give_premium)
        bot.answer_callback_query(call.id, "➕ Donner Premium")
    
    elif call.data == "admin_remove_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        msg = bot.send_message(call.message.chat.id, "🔒 **RETIRER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
        bot.register_next_step_handler(msg, process_remove_premium)
        bot.answer_callback_query(call.id, "➖ Retirer Premium")
    
    elif call.data == "admin_premium_all":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        users = get_all_users()
        for user in users:
            activate_user_premium(user[0])
        
        bot.answer_callback_query(call.id, "✅ Premium à tous")
        bot.send_message(call.message.chat.id, f"⭐ **Premium activé pour tous les {len(users)} utilisateurs !**")
    
    elif call.data == "admin_remove_all_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        users = get_all_users()
        count = 0
        for user in users:
            if user[0] != ADMIN_ID:
                deactivate_user_premium(user[0])
                count += 1
        
        bot.answer_callback_query(call.id, "🔒 Premium retiré")
        bot.send_message(call.message.chat.id, f"🔒 **Premium retiré à {count} utilisateurs !**")

def process_admin_auth_callback(message, original_message):
    """Traite l'authentification depuis le callback"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if verify_admin_password(message.text.strip()):
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        
        # Mettre à jour le message original avec le menu débloqué
        try:
            bot.edit_message_text(
                chat_id=original_message.chat.id,
                message_id=original_message.message_id,
                text="👑 **Panel Administrateur**\n\n✅ **Authentification réussie !**\n🔓 **Tous les boutons sont maintenant débloqués !**",
                parse_mode='Markdown',
                reply_markup=create_admin_menu(user_id)
            )
        except:
            bot.send_message(
                original_message.chat.id,
                "✅ **Authentification réussie !**\n🔓 **Tous les boutons sont maintenant débloqués !**",
                reply_markup=create_admin_menu(user_id),
                parse_mode='Markdown'
            )
    else:
        bot.reply_to(message, "❌ **Mot de passe incorrect.**\n\nUtilisez à nouveau le bouton Auth.")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🗃️ Initialisation de la base de données...")
    init_db()
    repair_database()
    print("✅ Base de données prête")
    print(f"🚀 {BOT_NAME} - {VERSION}")
    print(f"👑 Créateur: {CREATOR}")
    print("🔐 Système d'authentification avec bouton Auth activé")
    print("📊 Menu admin dynamique (boutons débloqués après auth)")
    print("📨 Système de commentaires activé")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("🔄 Redémarrage dans 5 secondes...")
        time.sleep(5)
