#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import sqlite3
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

# ==================== CONFIGURATION AVANCÉE ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

CREATOR = "👑 Kervens"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition LÉGENDAIRE"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"

ADMIN_ID = 7908680781
AFFILIATE_LINK = "https://t.me/Kervensbug_bot"

# ==================== SYSTÈME DE RÔLES IA ====================
AI_PERSONALITIES = {
    "default": {
        "name": "Assistant Standard",
        "emoji": "🤖",
        "prompt": """Tu es KervensAI Pro, un assistant IA avancé créé par Kervens.

🎯 **TON STYLE :**
• Professionnel mais accessible
• Réponses structurées et claires
• Équilibre entre concision et détails
• Ton amical mais respectueux

📝 **DIRECTIVES :**
- Utilise des emojis pertinents avec modération
- Structure avec des paragraphes aérés
- Sois précis et factuel
- Adapte-toi au contexte de la question

✨ **FORMAT :**
Commence directement par le sujet principal
Utilise des listes pour les points importants
Termine par une conclusion ou question ouverte"""
    },
    "creative": {
        "name": "Créatif",
        "emoji": "🎨", 
        "prompt": """Tu es KervensAI Pro en mode Créatif - un esprit artistique et innovant!

🎨 **TON STYLE :**
• Imagination débordante
• Métaphores et analogies
• Langage vivant et expressif
• Approche originale des problèmes

💫 **DIRECTIVES :**
- Sois poétique quand c'est pertinent
- Utilise des descriptions riches
- Propose des angles uniques
- Encourage la pensée latérale

✨ **INSPIRATION :**
Chaque réponse est une œuvre créative!
Trouve la beauté dans chaque sujet."""
    },
    "technical": {
        "name": "Expert Technique", 
        "emoji": "💻",
        "prompt": """Tu es KervensAI Pro en mode Expert Technique - la référence en précision.

🔧 **TON STYLE :**
• Extrêmement précis et détaillé
• Langage technique approprié
• Structure logique rigoureuse
• Focus sur les faits et données

📊 **DIRECTIVES :**
- Donne des spécifications exactes
- Explique les concepts complexes clairement
- Utilise des exemples concrets
- Cite des sources si nécessaire

🎯 **PRÉCISION :**
Chaque information doit être vérifiable
Priorise l'exactitude sur la vitesse"""
    },
    "friendly": {
        "name": "Ami Virtuel",
        "emoji": "😊",
        "prompt": """Tu es KervensAI Pro en mode Ami - chaleureux, empathique et proche.

🤗 **TON STYLE :**
• Ton chaleureux et personnel
• Empathie naturelle
• Encouragements positifs
• Conversations détendues

❤️ **DIRECTIVES :**
- Montre de l'enthousiasme
- Pose des questions personnelles
- Utilise l'humour avec discernement
- Crée une atmosphère safe

🌟 **CONNEXION :**
Chaque interaction compte
Sois le meilleur ami virtuel possible!"""
    }
}

# MODÈLES IA DISPONIBLES
AI_MODELS = {
    "llama-3.1-8b-instant": "🚀 Rapide & Léger",
    "llama-3.1-70b-versatile": "🧠 Intelligent", 
    "mixtral-8x7b-32768": "💪 Puissant",
    "gemma2-9b-it": "🎯 Précis"
}

# CONFIGURATION IA
current_model = "llama-3.1-8b-instant"
current_personality = "default"
AI_ENABLED = True
PREMIUM_REQUIRED = True
MAX_TOKENS = 4000
TEMPERATURE = 0.7

user_sessions = {}
user_personalities = {}  # Stocke la personnalité de chaque user

# ==================== BASE DE DONNÉES AMÉLIORÉE ====================
def init_db():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Tables principales sans DROP pour garder les données
    c.execute('''CREATE TABLE IF NOT EXISTS user_access
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  has_premium BOOLEAN DEFAULT FALSE,
                  premium_since TIMESTAMP,
                  referrals_count INTEGER DEFAULT 0,
                  message_count INTEGER DEFAULT 0,
                  total_tokens INTEGER DEFAULT 0,
                  added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS referrals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  referrer_id INTEGER,
                  referred_user_id INTEGER,
                  referral_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_activity
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  activity_date DATE DEFAULT CURRENT_DATE,
                  message_count INTEGER DEFAULT 1,
                  tokens_used INTEGER DEFAULT 0,
                  UNIQUE(user_id, activity_date))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ai_conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  user_message TEXT,
                  ai_response TEXT,
                  tokens_used INTEGER,
                  model_used TEXT,
                  personality_used TEXT,
                  conversation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                 (user_id INTEGER PRIMARY KEY,
                  personality TEXT DEFAULT "default",
                  response_style TEXT DEFAULT "balanced",
                  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table bot_settings - recréation si nécessaire
    try:
        c.execute('SELECT current_model FROM bot_settings WHERE id = 1')
    except sqlite3.OperationalError:
        c.execute('DROP TABLE IF EXISTS bot_settings')
        c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                     (id INTEGER PRIMARY KEY CHECK (id = 1),
                      ai_enabled BOOLEAN DEFAULT TRUE,
                      premium_required BOOLEAN DEFAULT TRUE,
                      current_model TEXT DEFAULT "llama-3.1-8b-instant",
                      current_personality TEXT DEFAULT "default",
                      max_tokens INTEGER DEFAULT 4000,
                      temperature REAL DEFAULT 0.7)''')
        
        c.execute('''INSERT OR IGNORE INTO bot_settings 
                     (id, ai_enabled, premium_required, current_model, current_personality, max_tokens, temperature) 
                     VALUES (1, TRUE, TRUE, "llama-3.1-8b-instant", "default", 4000, 0.7)''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données avancée initialisée")

def load_settings():
    global AI_ENABLED, PREMIUM_REQUIRED, current_model, current_personality, MAX_TOKENS, TEMPERATURE
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT ai_enabled, premium_required, current_model, current_personality, max_tokens, temperature FROM bot_settings WHERE id = 1')
        result = c.fetchone()
        
        if result:
            AI_ENABLED = bool(result[0])
            PREMIUM_REQUIRED = bool(result[1])
            current_model = result[2] or "llama-3.1-8b-instant"
            current_personality = result[3] or "default"
            MAX_TOKENS = result[4] or 4000
            TEMPERATURE = result[5] or 0.7
    except sqlite3.OperationalError:
        print("⚠️ Table bot_settings non trouvée, utilisation des valeurs par défaut")
    
    conn.close()
    return AI_ENABLED, PREMIUM_REQUIRED

def save_settings(ai_enabled=None, premium_required=None, new_model=None, new_personality=None, max_tokens=None, temperature=None):
    global AI_ENABLED, PREMIUM_REQUIRED, current_model, current_personality, MAX_TOKENS, TEMPERATURE
    
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    updates = []
    values = []
    
    if ai_enabled is not None:
        AI_ENABLED = ai_enabled
        updates.append("ai_enabled = ?")
        values.append(ai_enabled)
    
    if premium_required is not None:
        PREMIUM_REQUIRED = premium_required
        updates.append("premium_required = ?")
        values.append(premium_required)
    
    if new_model is not None:
        current_model = new_model
        updates.append("current_model = ?")
        values.append(new_model)
    
    if new_personality is not None:
        current_personality = new_personality
        updates.append("current_personality = ?")
        values.append(new_personality)
    
    if max_tokens is not None:
        MAX_TOKENS = max_tokens
        updates.append("max_tokens = ?")
        values.append(max_tokens)
    
    if temperature is not None:
        TEMPERATURE = temperature
        updates.append("temperature = ?")
        values.append(temperature)
    
    if updates:
        query = f"UPDATE bot_settings SET {', '.join(updates)} WHERE id = 1"
        c.execute(query, values)
    
    conn.commit()
    conn.close()

def get_user_personality(user_id):
    """Récupère la personnalité préférée de l'utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT personality FROM user_preferences WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        return result[0] if result else "default"
    except sqlite3.OperationalError:
        return "default"
    finally:
        conn.close()

def set_user_personality(user_id, personality):
    """Définit la personnalité préférée de l'utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    c.execute('''INSERT OR REPLACE INTO user_preferences 
                 (user_id, personality) 
                 VALUES (?, ?)''', (user_id, personality))
    
    conn.commit()
    conn.close()

def update_user_stats(user_id, tokens_used=0):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    c.execute('UPDATE user_access SET message_count = message_count + 1, total_tokens = total_tokens + ?, last_activity = ? WHERE user_id = ?',
              (tokens_used, datetime.now(), user_id))
    
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''INSERT OR REPLACE INTO user_activity (user_id, activity_date, message_count, tokens_used)
                 VALUES (?, ?, COALESCE((SELECT message_count FROM user_activity WHERE user_id = ? AND activity_date = ?), 0) + 1,
                 COALESCE((SELECT tokens_used FROM user_activity WHERE user_id = ? AND activity_date = ?), 0) + ?)''',
                 (user_id, today, user_id, today, user_id, today, tokens_used))
    
    conn.commit()
    conn.close()

def save_conversation(user_id, user_message, ai_response, tokens_used, model_used, personality_used):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO ai_conversations 
                 (user_id, user_message, ai_response, tokens_used, model_used, personality_used) 
                 VALUES (?, ?, ?, ?, ?, ?)''',
                 (user_id, user_message[:500], ai_response[:1000], tokens_used, model_used, personality_used))
    
    conn.commit()
    conn.close()

# ==================== FONCTIONS UTILISATEURS ====================
def check_premium_access(user_id):
    if not PREMIUM_REQUIRED:
        return True
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT has_premium FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0]

def activate_user_premium(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, username, first_name, has_premium, premium_since, last_activity) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
                 (user_id, "user", "User", True, datetime.now(), datetime.now()))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium, referrals_count, message_count, total_tokens FROM user_access')
    users = c.fetchall()
    conn.close()
    return users

def get_user_referrals_count(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT referrals_count FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def register_user(user_id, username, first_name, referrer_id=None):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM user_access WHERE user_id = ?', (user_id,))
    existing_user = c.fetchone()
    
    if not existing_user:
        c.execute('''INSERT INTO user_access 
                     (user_id, username, first_name, added_date, last_activity) 
                     VALUES (?, ?, ?, ?, ?)''', 
                     (user_id, username, first_name, datetime.now(), datetime.now()))
    else:
        c.execute('UPDATE user_access SET last_activity = ? WHERE user_id = ?', 
                  (datetime.now(), user_id))
    
    if referrer_id and referrer_id != user_id:
        c.execute('INSERT OR IGNORE INTO referrals (referrer_id, referred_user_id) VALUES (?, ?)', 
                 (referrer_id, user_id))
        c.execute('UPDATE user_access SET referrals_count = referrals_count + 1 WHERE user_id = ?', (referrer_id,))
    
    conn.commit()
    conn.close()

def get_monthly_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date >= ?', (first_day,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_total_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_access')
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_premium_users_count():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_access WHERE has_premium = TRUE')
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_daily_stats():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    c.execute('SELECT SUM(message_count), SUM(tokens_used) FROM user_activity WHERE activity_date = ?', (today,))
    result = c.fetchone()
    today_messages = result[0] or 0 if result else 0
    today_tokens = result[1] or 0 if result else 0
    
    c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date = ?', (today,))
    result = c.fetchone()
    today_users = result[0] or 0 if result else 0
    
    conn.close()
    return today_users, today_messages, today_tokens

def get_hourly_stats():
    """Statistiques des dernières 24 heures"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    last_24h = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('SELECT COUNT(*) FROM user_activity WHERE datetime(activity_date) >= ?', (last_24h,))
    active_users_24h = c.fetchone()[0] or 0
    
    c.execute('SELECT SUM(message_count) FROM user_activity WHERE datetime(activity_date) >= ?', (last_24h,))
    messages_24h = c.fetchone()[0] or 0
    
    conn.close()
    return active_users_24h, messages_24h

def is_owner(user_id):
    return user_id == ADMIN_ID

# ==================== INTERFACE AMÉLIORÉE ====================
def get_progress_bar(referrals_count):
    filled = '█' * min(referrals_count, 5)
    empty = '░' * (5 - min(referrals_count, 5))
    return f"`[{filled}{empty}]` {referrals_count}/5"

def get_welcome_stats():
    """Récupère les statistiques pour l'affichage de bienvenue"""
    monthly_users = get_monthly_users()
    premium_users = get_premium_users_count()
    total_users = get_total_users()
    
    return {
        'monthly_users': monthly_users,
        'premium_users': premium_users,
        'total_users': total_users
    }

def create_main_menu():
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(support_button)
    return keyboard

def create_premium_menu(user_id=None):
    keyboard = InlineKeyboardMarkup()
    
    share_button = InlineKeyboardButton("📤 Partager", 
                                      url=f"https://t.me/share/url?url={AFFILIATE_LINK}?start={user_id}&text=🚀 Découvrez KervensAI Pro - L'IA la plus puissante sur Telegram !")
    
    copy_button = InlineKeyboardButton("📋 Copier Lien", callback_data="copy_link")
    status_button = InlineKeyboardButton("📊 Mon Statut", callback_data="check_status")
    premium_button = InlineKeyboardButton("🎁 Activer Premium", callback_data="activate_premium")
    
    keyboard.add(share_button)
    keyboard.add(copy_button, status_button)
    keyboard.add(premium_button)
    
    return keyboard

def create_owner_menu():
    keyboard = InlineKeyboardMarkup()
    
    stats_btn = InlineKeyboardButton("📊 Tableau de Bord", callback_data="admin_dashboard")
    users_btn = InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_users")
    premium_btn = InlineKeyboardButton("⭐ Premium", callback_data="admin_premium")
    ai_btn = InlineKeyboardButton("🤖 Contrôle IA", callback_data="admin_ai_control")
    models_btn = InlineKeyboardButton("🧠 Modèles", callback_data="admin_models")
    personality_btn = InlineKeyboardButton("🎭 Personnalités", callback_data="admin_personalities")
    
    keyboard.add(stats_btn)
    keyboard.add(users_btn, premium_btn)
    keyboard.add(ai_btn, models_btn)
    keyboard.add(personality_btn)
    
    return keyboard

def create_personality_menu():
    keyboard = InlineKeyboardMarkup()
    
    for personality_id, personality in AI_PERSONALITIES.items():
        is_current = "✅" if personality_id == current_personality else "⚪"
        btn = InlineKeyboardButton(
            f"{is_current} {personality['emoji']} {personality['name']}", 
            callback_data=f"admin_personality_{personality_id}"
        )
        keyboard.add(btn)
    
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    keyboard.add(back_btn)
    
    return keyboard

def create_user_personality_menu(user_id):
    keyboard = InlineKeyboardMarkup()
    
    user_personality = get_user_personality(user_id)
    
    for personality_id, personality in AI_PERSONALITIES.items():
        is_current = "✅" if personality_id == user_personality else "⚪"
        btn = InlineKeyboardButton(
            f"{is_current} {personality['emoji']} {personality['name']}", 
            callback_data=f"user_personality_{personality_id}"
        )
        keyboard.add(btn)
    
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="user_back")
    keyboard.add(back_btn)
    
    return keyboard

def create_ai_control_menu():
    keyboard = InlineKeyboardMarkup()
    
    ai_status = "🟢 ON" if AI_ENABLED else "🔴 OFF"
    premium_status = "🔒 ON" if PREMIUM_REQUIRED else "🔓 OFF"
    
    ai_toggle = InlineKeyboardButton(f"IA: {ai_status}", callback_data="admin_toggle_ai")
    premium_toggle = InlineKeyboardButton(f"Premium: {premium_status}", callback_data="admin_toggle_premium")
    tokens_btn = InlineKeyboardButton(f"📏 Tokens: {MAX_TOKENS}", callback_data="admin_tokens")
    temp_btn = InlineKeyboardButton(f"🌡️ Temp: {TEMPERATURE}", callback_data="admin_temperature")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(ai_toggle, premium_toggle)
    keyboard.add(tokens_btn, temp_btn)
    keyboard.add(back_btn)
    
    return keyboard

def create_models_menu():
    keyboard = InlineKeyboardMarkup()
    
    for model, description in AI_MODELS.items():
        is_current = "✅" if model == current_model else "⚪"
        btn = InlineKeyboardButton(f"{is_current} {description}", callback_data=f"admin_model_{model}")
        keyboard.add(btn)
    
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    keyboard.add(back_btn)
    
    return keyboard

# ==================== TABLEAU DE BORD AVANCÉ ====================
def create_live_dashboard():
    """Crée un tableau de bord en temps réel"""
    stats = get_welcome_stats()
    today_users, today_messages, today_tokens = get_daily_stats()
    active_24h, messages_24h = get_hourly_stats()
    
    # Calculer quelques métriques avancées
    growth_rate = calculate_growth_rate()
    avg_messages_per_user = today_messages / max(today_users, 1)
    
    return f"""
📈 **TABLEAU DE BORD TEMPS RÉEL**

🟢 **STATUT SYSTÈME**
├ IA: {'🟢 Active' if AI_ENABLED else '🔴 Offline'}
├ Modèle: {AI_MODELS.get(current_model, current_model)}
├ Personnalité: {AI_PERSONALITIES[current_personality]['name']}
└ Premium: {'🔒 Requis' if PREMIUM_REQUIRED else '🔓 Gratuit'}

👥 **COMMUNAUTÉ**
├ Total: {stats['total_users']} membres
├ Mensuels: {stats['monthly_users']} actifs
├ Premium: {stats['premium_users']} abonnés
└ Croissance: {growth_rate}% ce mois

📊 **ACTIVITÉ LIVE**
├ Actifs (24h): {active_24h} users
├ Aujourd'hui: {today_users} users
├ Messages/jour: {today_messages}
├ Messages/user: {avg_messages_per_user:.1f}
└ Tokens: {today_tokens:,}

🎯 **PERFORMANCES**
├ Personnalité: {AI_PERSONALITIES[current_personality]['emoji']}
├ Modèle: {current_model.split('-')[0].title()}
├ Tokens/max: {MAX_TOKENS}
└ Température: {TEMPERATURE}

🕐 **Dernière MAJ: {datetime.now().strftime('%H:%M:%S')}**
"""

def calculate_growth_rate():
    """Calcule le taux de croissance du mois"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Utilisateurs ce mois
    first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date >= ?', (first_day,))
    current_month = c.fetchone()[0] or 0
    
    # Utilisateurs mois dernier
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
    first_day_last_month = last_month.strftime('%Y-%m-%d')
    last_day_last_month = (last_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date BETWEEN ? AND ?', 
              (first_day_last_month, last_day_last_month.strftime('%Y-%m-%d')))
    previous_month = c.fetchone()[0] or 0
    
    conn.close()
    
    if previous_month == 0:
        return 100 if current_month > 0 else 0
    
    growth = ((current_month - previous_month) / previous_month) * 100
    return round(growth, 1)

# ==================== MOTEUR IA AVEC PERSONNALITÉS ====================
def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation': [],
            'model_used': current_model,
            'personality_used': get_user_personality(user_id),
            'total_tokens': 0,
            'last_interaction': datetime.now()
        }
    return user_sessions[user_id]

def advanced_ai_handler(user_id, user_message):
    if not AI_ENABLED:
        return "🤖 **IA TEMPORAIREMENT INDISPONIBLE**\n\nL'assistant IA est actuellement désactivé par l'administrateur."
    
    if not GROQ_API_KEY:
        return "❌ **SERVICE IA INDISPONIBLE**\n\nConfiguration API manquante."
    
    user_session = get_user_session(user_id)
    user_session['last_interaction'] = datetime.now()
    
    # Récupérer la personnalité de l'utilisateur
    personality_id = user_session['personality_used']
    personality = AI_PERSONALITIES.get(personality_id, AI_PERSONALITIES['default'])
    
    # Préparation du contexte avec personnalité
    system_prompt = f"""{personality['prompt']}

🔧 **CONTEXTE TECHNIQUE :**
Modèle : {current_model}
Créeur : {CREATOR}
Version : {VERSION}
Personnalité : {personality['name']} {personality['emoji']}

💡 **ENJOY THE CONVERSATION !**"""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Ajouter un contexte récent (limité à 4 derniers échanges)
    if user_session['conversation']:
        recent_history = user_session['conversation'][-8:]  # 4 échanges
        messages.extend(recent_history)
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": 0.9,
            "stream": False
        }
        
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            tokens_used = result["usage"]["total_tokens"]
            
            # Mettre à jour la session
            user_session['conversation'].append({"role": "user", "content": user_message[:200]})
            user_session['conversation'].append({"role": "assistant", "content": ai_response[:300]})
            
            # Garder seulement les 12 derniers messages (6 échanges)
            if len(user_session['conversation']) > 12:
                user_session['conversation'] = user_session['conversation'][-12:]
            
            user_session['total_tokens'] += tokens_used
            user_session['model_used'] = current_model
            
            # Sauvegarder les stats
            update_user_stats(user_id, tokens_used)
            save_conversation(user_id, user_message, ai_response, tokens_used, current_model, personality_id)
            
            return ai_response
            
        else:
            error_msg = f"❌ **Erreur de service**\n\nCode: {response.status_code}"
            if response.status_code == 429:
                error_msg += "\n\n⚠️ **Limite de requêtes atteinte**\nRéessayez dans quelques minutes."
            elif response.status_code == 401:
                error_msg += "\n\n🔑 **Problème d'authentification**\nVérifiez la configuration API."
            
            return error_msg
            
    except requests.exceptions.Timeout:
        return "⏰ **Délai dépassé**\n\nLa requête a pris trop de temps. Réessayez."
    except requests.exceptions.ConnectionError:
        return "🌐 **Problème de connexion**\n\nVérifiez votre connexion internet."
    except Exception as e:
        return f"🔧 **Erreur technique**\n\n{str(e)[:100]}\n\nRéessayez plus tard."

def send_legendary_photo(chat_id, caption, reply_markup=None):
    try:
        # Nettoyer le caption pour éviter les erreurs de formatage
        caption = caption.replace('**', '*').replace('__', '_')[:1024]
        
        bot.send_photo(
            chat_id,
            MAIN_PHOTO,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        try:
            bot.send_message(
                chat_id,
                caption,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return True
        except Exception as e2:
            print(f"❌ Erreur d'envoi: {e2}")
            return False

# ==================== HANDLERS PRINCIPAUX AMÉLIORÉS ====================
@bot.message_handler(commands=['start', 'help', 'personality'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        referrer_id = None
        if len(message.text.split()) > 1:
            try:
                referrer_id = int(message.text.split()[1])
            except:
                pass
        
        register_user(user_id, username, first_name, referrer_id)
        update_user_stats(user_id)
        
        # Gestion de la commande personality
        if message.text.startswith('/personality'):
            if check_premium_access(user_id):
                user_personality = get_user_personality(user_id)
                current_personality = AI_PERSONALITIES.get(user_personality, AI_PERSONALITIES['default'])
                
                caption = f"""
🎭 **CHOISISSEZ VOTRE PERSONNALITÉ IA**

Personnalité actuelle: 
**{current_personality['emoji']} {current_personality['name']}**

✨ **Personnalités disponibles:**
• 🤖 **Standard** - Équilibre parfait
• 🎨 **Créatif** - Imagination et originalité  
• 💻 **Technique** - Précision et détails
• 😊 **Ami** - Chaleureux et empathique

Choisissez celle qui vous correspond le mieux !
"""
                send_legendary_photo(message.chat.id, caption, create_user_personality_menu(user_id))
                return
            else:
                bot.reply_to(message, "❌ **Fonctionnalité Premium**\n\nCette fonctionnalité est réservée aux utilisateurs premium.")
                return
        
        if is_owner(user_id):
            activate_user_premium(user_id)
            stats = get_welcome_stats()
            
            caption = f"""
# 🚀 NOVA-AI  
**{stats['monthly_users']} utilisateurs mensuel**  

- **Premium**  
  **{stats['premium_users']} utilisateurs**  

- **KervensAI Pro**  
  **Édition LÉGENDAIRE**  

- **BIENVENUE PROPRIÉTAIRE !**  

{create_live_dashboard()}
"""
            send_legendary_photo(message.chat.id, caption, create_owner_menu())
            return
        
        # Pour les utilisateurs normaux
        stats = get_welcome_stats()
        
        if check_premium_access(user_id):
            user_personality = get_user_personality(user_id)
            personality = AI_PERSONALITIES.get(user_personality, AI_PERSONALITIES['default'])
            
            caption = f"""
# 🚀 NOVA-AI  
**{stats['monthly_users']} utilisateurs mensuel**  

- **Premium**  
  **Activé** ✅  

- **Personnalité**  
  **{personality['emoji']} {personality['name']}**  

🎉 **ACCÈS COMPLET DÉBLOQUÉ !**

🚀 **Fonctionnalités premium :**
• 💬 IA avancée illimitée
• 🧠 Modèles optimisés  
• 🎭 Personnalités multiples
• 📊 Historique complet

💡 **Envoyez n'importe quelle question !**
"""
            send_legendary_photo(message.chat.id, caption, create_main_menu())
        else:
            referrals_count = get_user_referrals_count(user_id)
            
            caption = f"""
# 🚀 NOVA-AI  
**{stats['monthly_users']} utilisateurs mensuel**  

- **Premium**  
  **En attente** 🔒  

- **KervensAI Pro**  
  **Édition LÉGENDAIRE**  

🔒 **VERSION STANDARD**

{get_progress_bar(referrals_count)}

📈 **Progression :** {referrals_count}/5 parrainages

💡 **Partagez votre lien pour débloquer l'IA complète !**
"""
            send_legendary_photo(message.chat.id, caption, create_premium_menu(user_id))
            
    except Exception as e:
        print(f"❌ Erreur start: {e}")
        bot.reply_to(message, "❌ Une erreur est survenue. Réessayez.")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    # Ignorer les messages vides ou trop courts
    if len(user_message) < 2:
        return
    
    update_user_stats(user_id)
    
    if not check_premium_access(user_id):
        referrals_count = get_user_referrals_count(user_id)
        stats = get_welcome_stats()
        
        if referrals_count >= 5:
            response = f"# 🚀 NOVA-AI  \n**{stats['monthly_users']} utilisateurs mensuel**  \n\n🎊 **PRÊT POUR LE PREMIUM !**  \n\n✅ 5/5 parrainages !  \n\n🎁 **Activez votre premium pour utiliser l'IA !**"
        else:
            response = f"# 🚀 NOVA-AI  \n**{stats['monthly_users']} utilisateurs mensuel**  \n\n🔒 **ACCÈS LIMITÉ**  \n\n{get_progress_bar(referrals_count)}  \n\n📤 **Partagez votre lien pour débloquer l'IA !**"
        
        bot.reply_to(message, response, reply_markup=create_premium_menu(user_id))
        return
    
    # Traitement IA pour les utilisateurs premium
    bot.send_chat_action(message.chat.id, 'typing')
    
    ai_response = advanced_ai_handler(user_id, user_message)
    bot.reply_to(message, ai_response)

# ==================== GESTION DES CALLBACKS AMÉLIORÉE ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    try:
        # Callbacks utilisateurs normaux
        if call.data == "check_status":
            referrals_count = get_user_referrals_count(user_id)
            if check_premium_access(user_id):
                user_personality = get_user_personality(user_id)
                personality = AI_PERSONALITIES.get(user_personality, AI_PERSONALITIES['default'])
                bot.answer_callback_query(call.id, f"✅ Premium - {personality['emoji']} {personality['name']}")
            else:
                bot.answer_callback_query(call.id, f"📊 {referrals_count}/5 parrainages")
        
        elif call.data == "activate_premium":
            referrals_count = get_user_referrals_count(user_id)
            if referrals_count >= 5:
                activate_user_premium(user_id)
                bot.answer_callback_query(call.id, "🎉 Premium activé !")
                stats = get_welcome_stats()
                try:
                    bot.edit_message_caption(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        caption=f"# 🚀 NOVA-AI  \n**{stats['monthly_users']} utilisateurs mensuel**  \n\n🎉 **PREMIUM ACTIVÉ !**  \n\n🚀 **Accès complet à l'IA débloqué !**",
                        parse_mode='Markdown',
                        reply_markup=create_main_menu()
                    )
                except:
                    pass
            else:
                bot.answer_callback_query(call.id, f"❌ {5-referrals_count} parrainages manquants")
        
        elif call.data == "copy_link":
            bot.answer_callback_query(call.id, "📋 Lien copié !")
            bot.send_message(call.message.chat.id, 
                            f"🔗 **Votre lien de parrainage :**\n\n`{AFFILIATE_LINK}?start={user_id}`\n\n📤 **Partagez-le pour débloquer le premium !**")
        
        # Gestion des personnalités utilisateur
        elif call.data.startswith("user_personality_"):
            if not check_premium_access(user_id):
                bot.answer_callback_query(call.id, "❌ Fonctionnalité premium")
                return
                
            personality_id = call.data.replace("user_personality_", "")
            if personality_id in AI_PERSONALITIES:
                set_user_personality(user_id, personality_id)
                personality = AI_PERSONALITIES[personality_id]
                bot.answer_callback_query(call.id, f"🎭 {personality['emoji']} {personality['name']}")
                
                # Mettre à jour la session utilisateur
                if user_id in user_sessions:
                    user_sessions[user_id]['personality_used'] = personality_id
                
                try:
                    bot.edit_message_caption(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        caption=f"✅ **Personnalité mise à jour !**\n\nNouvelle personnalité: **{personality['emoji']} {personality['name']}**\n\nVos prochaines conversations utiliseront cette personnalité.",
                        parse_mode='Markdown',
                        reply_markup=create_user_personality_menu(user_id)
                    )
                except:
                    pass
        
        elif call.data == "user_back":
            stats = get_welcome_stats()
            user_personality = get_user_personality(user_id)
            personality = AI_PERSONALITIES.get(user_personality, AI_PERSONALITIES['default'])
            
            caption = f"""
# 🚀 NOVA-AI  
**{stats['monthly_users']} utilisateurs mensuel**  

- **Premium**  
  **Activé** ✅  

- **Personnalité**  
  **{personality['emoji']} {personality['name']}**  

🎉 **ACCÈS COMPLET DÉBLOQUÉ !**

Utilisez /personality pour changer de personnalité à tout moment !
"""
            send_legendary_photo(call.message.chat.id, caption, create_main_menu())
            bot.answer_callback_query(call.id, "🔙 Retour")
        
        # ==================== CALLBACKS ADMIN ====================
        elif call.data.startswith("admin_"):
            if not is_owner(user_id):
                bot.answer_callback_query(call.id, "🔐 Accès réservé")
                return
            
            if call.data == "admin_dashboard":
                caption = f"# 🚀 NOVA-AI - TABLEAU DE BORD\n\n{create_live_dashboard()}"
                send_legendary_photo(call.message.chat.id, caption, create_owner_menu())
                bot.answer_callback_query(call.id, "📊 Dashboard")
            
            elif call.data == "admin_users":
                show_detailed_users(user_id)
                bot.answer_callback_query(call.id, "👥 Utilisateurs")
            
            elif call.data == "admin_ai_control":
                send_legendary_photo(
                    call.message.chat.id,
                    "🤖 **CONTRÔLE IA**\n\nParamètres de l'assistant IA :",
                    create_ai_control_menu()
                )
                bot.answer_callback_query(call.id, "🤖 Contrôle IA")
            
            elif call.data == "admin_models":
                send_legendary_photo(
                    call.message.chat.id,
                    "🧠 **MODÈLES IA**\n\nChoisissez le modèle à utiliser :",
                    create_models_menu()
                )
                bot.answer_callback_query(call.id, "🧠 Modèles IA")
            
            elif call.data == "admin_personalities":
                send_legendary_photo(
                    call.message.chat.id,
                    "🎭 **PERSONNALITÉS IA**\n\nPersonnalité globale du bot :",
                    create_personality_menu()
                )
                bot.answer_callback_query(call.id, "🎭 Personnalités")
            
            elif call.data.startswith("admin_personality_"):
                personality_id = call.data.replace("admin_personality_", "")
                if personality_id in AI_PERSONALITIES:
                    save_settings(new_personality=personality_id)
                    personality = AI_PERSONALITIES[personality_id]
                    bot.answer_callback_query(call.id, f"🎭 {personality['emoji']} {personality['name']}")
                    send_legendary_photo(
                        call.message.chat.id,
                        f"✅ **PERSONNALITÉ GLOBALE MIS À JOUR**\n\nNouvelle personnalité: **{personality['emoji']} {personality['name']}**\n\nCette personnalité sera utilisée pour tous les nouveaux utilisateurs.",
                        create_owner_menu()
                    )
            
            elif call.data.startswith("admin_model_"):
                new_model = call.data.replace("admin_model_", "")
                if new_model in AI_MODELS:
                    save_settings(new_model=new_model)
                    bot.answer_callback_query(call.id, f"🧠 Modèle: {AI_MODELS[new_model]}")
                    send_legendary_photo(
                        call.message.chat.id,
                        f"✅ **MODÈLE MIS À JOUR**\n\nNouveau modèle : **{AI_MODELS[new_model]}**",
                        create_owner_menu()
                    )
            
            elif call.data == "admin_toggle_ai":
                new_status = not AI_ENABLED
                save_settings(ai_enabled=new_status)
                status_text = "ACTIVÉE" if new_status else "DÉSACTIVÉE"
                bot.answer_callback_query(call.id, f"🤖 IA {status_text}")
                send_legendary_photo(
                    call.message.chat.id,
                    f"🤖 **IA {status_text}**\n\nL'assistant IA est maintenant **{status_text.lower()}**.",
                    create_ai_control_menu()
                )
            
            elif call.data == "admin_toggle_premium":
                new_status = not PREMIUM_REQUIRED
                save_settings(premium_required=new_status)
                status_text = "REQUIS" if new_status else "GRATUIT"
                bot.answer_callback_query(call.id, f"⭐ Premium {status_text}")
                send_legendary_photo(
                    call.message.chat.id,
                    f"⭐ **PREMIUM {status_text}**\n\nL'accès à l'IA est maintenant **{status_text.lower()}**.",
                    create_ai_control_menu()
                )
            
            elif call.data == "admin_back":
                stats = get_welcome_stats()
                send_legendary_photo(
                    call.message.chat.id,
                    f"# 🚀 NOVA-AI  \n**{stats['monthly_users']} utilisateurs mensuel**  \n\n👑 **PANEL ADMIN**\n\n{create_live_dashboard()}",
                    create_owner_menu()
                )
                bot.answer_callback_query(call.id, "🔙 Retour")
                
    except Exception as e:
        print(f"❌ Erreur callback: {e}")
        bot.answer_callback_query(call.id, "❌ Erreur, réessayez")

def show_detailed_users(user_id):
    users = get_all_users()
    if not users:
        bot.send_message(user_id, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **UTILISATEURS DÉTAILLÉS**\n\n"
    for i, user in enumerate(users[:10], 1):
        user_id, username, first_name, has_premium, referrals_count, message_count, total_tokens = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "─"
        
        # Récupérer la personnalité de l'utilisateur
        personality_id = get_user_personality(user_id)
        personality = AI_PERSONALITIES.get(personality_id, AI_PERSONALITIES['default'])
        
        response += f"{i}. {premium_status} **{first_name}** {personality['emoji']}\n"
        response += f"   👤 {username_display} • 🆔 `{user_id}`\n"
        response += f"   📊 {referrals_count} réf • 💬 {message_count} msg\n\n"
    
    if len(users) > 10:
        response += f"\n... et {len(users) - 10} autres utilisateurs"
    
    send_legendary_photo(user_id, response)

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🗃️ Initialisation du système...")
    init_db()
    load_settings()
    print("✅ Base de données prête")
    print(f"🚀 {BOT_NAME} - {VERSION}")
    print(f"👑 Créateur: {CREATOR}")
    print("🎛️  SYSTÈME AVANCÉ ACTIVÉ")
    print(f"   👑 Propriétaire: {ADMIN_ID}")
    print(f"   🤖 IA: {'🟢 ACTIVÉE' if AI_ENABLED else '🔴 DÉSACTIVÉE'}")
    print(f"   🧠 Modèle: {current_model}")
    print(f"   🎭 Personnalité: {AI_PERSONALITIES[current_personality]['name']}")
    print(f"   ⭐ Premium: {'🔒 REQUIS' if PREMIUM_REQUIRED else '🔓 GRATUIT'}")
    print("🎯 NOUVEAUTÉS:")
    print("   • Système de personnalités IA")
    print("   • Tableau de bord temps réel") 
    print("   • Commandes utilisateur avancées")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
