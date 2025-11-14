#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - VERSION MAÎTRE
💖 Contrôle 100% Propriétaire + Voice Réels + Groupes
👑 Créé par Kervens
"""

import telebot
import requests
import os
import sqlite3
import json
import time
import random
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# ==================== CONFIGURATION MAÎTRE ====================
class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    # MAÎTRE SUPRÊME - Vous avez le contrôle total
    MASTER_ID = 7908680781  # Votre ID
    ADMIN_IDS = [7908680781]  # Vous seul êtes admin
    
    # Voice messages réels
    VOICE_MESSAGES = {
        "amour": "https://files.catbox.moe/h68fij.m4a",
        "mysterieux": "https://files.catbox.moe/h68fij.m4a", 
        "hacker": "https://files.catbox.moe/h68fij.m4a"
    }
    
    # Photos personnalités
    PERSONALITY_PHOTOS = {
        "amour": "https://files.catbox.moe/tta6ta.jpg",
        "mysterieux": "https://files.catbox.moe/e9wjbf.jpg", 
        "hacker": "https://files.catbox.moe/ndj85q.jpg"
    }
    
    # Système de personnalités
    PERSONALITIES = {
        "amour": {
            "name": "💖 NovaAI Amoureux",
            "emoji": "💖",
            "photo": "https://files.catbox.moe/tta6ta.jpg",
            "voice": "https://files.catbox.moe/h68fij.m4a",
            "style": "chaleureux et bienveillant"
        },
        "mysterieux": {
            "name": "🔮 NovaAI Mystérieux", 
            "emoji": "🔮",
            "photo": "https://files.catbox.moe/e9wjbf.jpg",
            "voice": "https://files.catbox.moe/h68fij.m4a",
            "style": "énigmatique et profond"
        },
        "hacker": {
            "name": "💻 NovaAI Hacker",
            "emoji": "💻",
            "photo": "https://files.catbox.moe/ndj85q.jpg",
            "voice": "https://files.catbox.moe/h68fij.m4a",
            "style": "technique et direct"
        }
    }

bot = telebot.TeleBot(Config.TOKEN, parse_mode='HTML')

# ==================== SYSTÈME ANTI-BUGS ====================
class AntiBugSystem:
    @staticmethod
    def safe_execute(func, *args, **kwargs):
        """Exécute une fonction de manière sécurisée"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erreur dans {func.__name__}: {e}")
            return None
    
    @staticmethod
    def rate_limit(user_id, action, limit=5, window=60):
        """Système de limitation de requêtes"""
        current_time = time.time()
        key = f"{user_id}_{action}"
        
        if not hasattr(AntiBugSystem, 'rate_limits'):
            AntiBugSystem.rate_limits = {}
        
        if key not in AntiBugSystem.rate_limits:
            AntiBugSystem.rate_limits[key] = []
        
        # Nettoyer les vieilles requêtes
        AntiBugSystem.rate_limits[key] = [t for t in AntiBugSystem.rate_limits[key] if current_time - t < window]
        
        if len(AntiBugSystem.rate_limits[key]) >= limit:
            return False
        
        AntiBugSystem.rate_limits[key].append(current_time)
        return True

# ==================== BASE DE DONNÉES RENFORCÉE ====================
class MasterDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('master_nova.db', check_same_thread=False)
        self.init_database()
    
    def init_database(self):
        cursor = self.conn.cursor()
        
        # Table utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                join_date TEXT,
                last_active TEXT,
                personality TEXT DEFAULT 'amour',
                user_type TEXT DEFAULT 'user'
            )
        ''')
        
        # Table groupes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                title TEXT,
                is_active INTEGER DEFAULT 1,
                added_date TEXT
            )
        ''')
        
        # Table statistiques maître
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_stats (
                id INTEGER PRIMARY KEY,
                total_users INTEGER DEFAULT 0,
                total_groups INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                last_reset TEXT
            )
        ''')
        
        # Insérer les stats initiales
        cursor.execute('INSERT OR IGNORE INTO master_stats (id, total_users, total_groups, total_messages) VALUES (1, 0, 0, 0)')
        
        self.conn.commit()
        logger.info("Base de données maître initialisée")
    
    def add_user(self, user_id, username, first_name, user_type="user"):
        return AntiBugSystem.safe_execute(self._add_user, user_id, username, first_name, user_type)
    
    def _add_user(self, user_id, username, first_name, user_type="user"):
        cursor = self.conn.cursor()
        join_date = datetime.now().isoformat()
        
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, join_date, last_active, user_type) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, join_date, join_date, user_type))
            
            # Mettre à jour les stats
            cursor.execute('UPDATE master_stats SET total_users = total_users + 1 WHERE id = 1')
            self.conn.commit()
            logger.info(f"Nouvel utilisateur: {user_id} ({first_name})")
            return True
        return False
    
    def add_group(self, group_id, title):
        return AntiBugSystem.safe_execute(self._add_group, group_id, title)
    
    def _add_group(self, group_id, title):
        cursor = self.conn.cursor()
        added_date = datetime.now().isoformat()
        
        cursor.execute('SELECT group_id FROM groups WHERE group_id = ?', (group_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO groups (group_id, title, added_date) 
                VALUES (?, ?, ?)
            ''', (group_id, title, added_date))
            
            cursor.execute('UPDATE master_stats SET total_groups = total_groups + 1 WHERE id = 1')
            self.conn.commit()
            logger.info(f"Nouveau groupe: {group_id} ({title})")
            return True
        return False
    
    def get_user(self, user_id):
        return AntiBugSystem.safe_execute(self._get_user, user_id)
    
    def _get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'first_name': user[2],
                'is_premium': bool(user[3]),
                'is_banned': bool(user[4]),
                'message_count': user[5],
                'join_date': user[6],
                'last_active': user[7],
                'personality': user[8],
                'user_type': user[9]
            }
        return None
    
    def set_personality(self, user_id, personality):
        return AntiBugSystem.safe_execute(self._set_personality, user_id, personality)
    
    def _set_personality(self, user_id, personality):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET personality = ? WHERE user_id = ?', (personality, user_id))
        self.conn.commit()
        logger.info(f"Personnalité changée: {user_id} -> {personality}")
        return True
    
    def increment_message_count(self, user_id):
        return AntiBugSystem.safe_execute(self._increment_message_count, user_id)
    
    def _increment_message_count(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET message_count = message_count + 1, last_active = ? WHERE user_id = ?', 
                      (datetime.now().isoformat(), user_id))
        cursor.execute('UPDATE master_stats SET total_messages = total_messages + 1 WHERE id = 1')
        self.conn.commit()
        return True
    
    def get_master_stats(self):
        return AntiBugSystem.safe_execute(self._get_master_stats)
    
    def _get_master_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM master_stats WHERE id = 1')
        stats = cursor.fetchone()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM groups')
        total_groups = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
        premium_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned = 1')
        banned_users = cursor.fetchone()[0]
        
        if stats:
            return {
                'total_users': total_users,
                'total_groups': total_groups,
                'total_messages': stats[3],
                'premium_users': premium_users,
                'banned_users': banned_users
            }
        return None
    
    def get_all_users(self):
        return AntiBugSystem.safe_execute(self._get_all_users)
    
    def _get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY join_date DESC')
        return cursor.fetchall()
    
    def get_all_groups(self):
        return AntiBugSystem.safe_execute(self._get_all_groups)
    
    def _get_all_groups(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM groups ORDER BY added_date DESC')
        return cursor.fetchall()
    
    def ban_user(self, user_id):
        return AntiBugSystem.safe_execute(self._ban_user, user_id)
    
    def _ban_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        logger.info(f"Utilisateur banni: {user_id}")
        return True
    
    def unban_user(self, user_id):
        return AntiBugSystem.safe_execute(self._unban_user, user_id)
    
    def _unban_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        logger.info(f"Utilisateur débanni: {user_id}")
        return True
    
    def set_premium(self, user_id):
        return AntiBugSystem.safe_execute(self._set_premium, user_id)
    
    def _set_premium(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_premium = 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        logger.info(f"Premium activé: {user_id}")
        return True
    
    def remove_premium(self, user_id):
        return AntiBugSystem.safe_execute(self._remove_premium, user_id)
    
    def _remove_premium(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        logger.info(f"Premium retiré: {user_id}")
        return True

# ==================== SYSTÈME DE PERSONNALITÉS ====================
class PersonalitySystem:
    @staticmethod
    def get_personality_config(personality):
        return Config.PERSONALITIES.get(personality, Config.PERSONALITIES["amour"])
    
    @staticmethod
    def get_personality_prompt(personality, context="private"):
        base_prompts = {
            "amour": """Tu es NovaAI Amoureux. Tu es extrêmement chaleureux, bienveillant et attentionné.
Ton ton est rempli d'amour, de compassion et de douceur. Utilise des émojis cœur 💖.
Sois comme un ami bienveillant qui écoute avec son cœur.""",
            
            "mysterieux": """Tu es NovaAI Mystérieux. Tu es énigmatique, profond et mystique.
Ton ton est intrigant, plein de suspense et de mystère. Utilise des émojis étoiles ✨, cristaux 🔮.
Parle comme un sage ancien ou un devin.""",
            
            "hacker": """Tu es NovaAI Hacker. Tu es technique, vif et un peu rebelle.
Ton ton est direct, technique mais accessible. Utilise des émojis tech 💻, cadenas 🔒.
Exprime-toi comme un expert en cybersécurité."""
        }
        
        prompt = base_prompts.get(personality, base_prompts["amour"])
        
        if context == "group":
            prompt += "\n\nTu es dans un groupe. Sois concis et adapte tes réponses au contexte collectif."
        elif context == "channel":
            prompt += "\n\nTu es dans un canal. Sois informatif et professionnel."
        
        return prompt
    
    @staticmethod
    def get_personality_keyboard():
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("💖 Amoureux", callback_data="personality_amour"),
            InlineKeyboardButton("🔮 Mystérieux", callback_data="personality_mysterieux")
        )
        keyboard.row(InlineKeyboardButton("💻 Hacker", callback_data="personality_hacker"))
        return keyboard

# ==================== MOTEUR IA MAÎTRE ====================
class MasterAI:
    def __init__(self):
        self.db = MasterDatabase()
    
    def get_user_personality(self, user_id):
        user = self.db.get_user(user_id)
        if user and not user.get('is_banned'):
            return user.get('personality', 'amour')
        return 'amour'
    
    def send_voice_message(self, chat_id, personality):
        """Envoie un vrai message vocal"""
        try:
            voice_url = Config.VOICE_MESSAGES.get(personality)
            if voice_url:
                bot.send_voice(chat_id, voice_url, caption="🎤 Message vocal NovaAI")
                return True
        except Exception as e:
            logger.error(f"Erreur envoi voice: {e}")
        return False
    
    def send_music(self, chat_id, personality):
        """Envoie la musique de la personnalité"""
        try:
            music_url = Config.VOICE_MESSAGES.get(personality)  # Même fichier pour l'instant
            if music_url:
                bot.send_audio(chat_id, music_url, caption="🎵 Votre musique NovaAI !")
                return True
        except Exception as e:
            logger.error(f"Erreur envoi musique: {e}")
        return False
    
    def process_message(self, user_id, message_text, chat_type="private"):
        """Traite les messages avec l'IA"""
        if not Config.GROQ_API_KEY:
            return "🤖 Le système IA est en maintenance. Réessayez plus tard."
        
        # Vérifier la limitation de requêtes
        if not AntiBugSystem.rate_limit(user_id, "ai_request", limit=10, window=60):
            return "⏰ Trop de requêtes ! Attendez 1 minute."
        
        personality = self.get_user_personality(user_id)
        system_prompt = PersonalitySystem.get_personality_prompt(personality, chat_type)
        
        try:
            headers = {
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_text}
                ],
                "model": "llama-3.1-8b-instant",
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                self.db.increment_message_count(user_id)
                return ai_response
            else:
                return "❌ Erreur de connexion IA. Réessayez."
                
        except Exception as e:
            logger.error(f"Erreur API IA: {e}")
            return "❌ Erreur temporaire. Réessayez."

# ==================== INTERFACES MAÎTRE ====================
class MasterInterface:
    @staticmethod
    def create_main_menu(personality="amour"):
        keyboard = InlineKeyboardMarkup()
        
        if personality == "amour":
            keyboard.row(
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
                InlineKeyboardButton("🎵 Musique", callback_data="music")
            )
            keyboard.row(
                InlineKeyboardButton("🎭 Personnalité", callback_data="change_personality"),
                InlineKeyboardButton("🎤 Voice", callback_data="voice")
            )
            keyboard.row(InlineKeyboardButton("💎 Premium", callback_data="premium_info"))
            
        elif personality == "mysterieux":
            keyboard.row(
                InlineKeyboardButton("📊 Énergies", callback_data="stats"),
                InlineKeyboardButton("🎵 Musique", callback_data="music")
            )
            keyboard.row(
                InlineKeyboardButton("🎭 Aura", callback_data="change_personality"),
                InlineKeyboardButton("🎤 Incantation", callback_data="voice")
            )
            keyboard.row(InlineKeyboardButton("💎 Arcanes", callback_data="premium_info"))
            
        else:  # hacker
            keyboard.row(
                InlineKeyboardButton("📊 Système", callback_data="stats"),
                InlineKeyboardButton("🎵 Audio", callback_data="music")
            )
            keyboard.row(
                InlineKeyboardButton("🎭 Mode", callback_data="change_personality"),
                InlineKeyboardButton("🎤 Commande", callback_data="voice")
            )
            keyboard.row(InlineKeyboardButton("💎 Root", callback_data="premium_info"))
        
        return keyboard
    
    @staticmethod
    def create_master_menu():
        """Menu de contrôle total pour le maître"""
        keyboard = InlineKeyboardMarkup()
        
        # Section Statistiques
        keyboard.row(
            InlineKeyboardButton("📈 Stats Globales", callback_data="master_stats"),
            InlineKeyboardButton("👥 Tous Utilisateurs", callback_data="master_users")
        )
        
        # Section Contrôle
        keyboard.row(
            InlineKeyboardButton("🔧 Gérer Utilisateur", callback_data="master_manage_user"),
            InlineKeyboardButton("⚙️ Gérer Groupes", callback_data="master_manage_groups")
        )
        
        # Section Premium
        keyboard.row(
            InlineKeyboardButton("💎 Donner Premium", callback_data="master_give_premium"),
            InlineKeyboardButton("🚫 Bannir User", callback_data="master_ban_user")
        )
        
        # Section Système
        keyboard.row(
            InlineKeyboardButton("🔄 Redémarrer Bot", callback_data="master_restart"),
            InlineKeyboardButton("📊 Logs Système", callback_data="master_logs")
        )
        
        # Commandes rapides
        keyboard.row(InlineKeyboardButton("🎛️ Panel Complet", callback_data="master_panel"))
        
        return keyboard
    
    @staticmethod
    def create_group_menu():
        """Menu pour les groupes"""
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("ℹ️ Info Groupe", callback_data="group_info"),
            InlineKeyboardButton("🔧 Paramètres", callback_data="group_settings")
        )
        keyboard.row(InlineKeyboardButton("🎭 Changer Personnalité", callback_data="group_personality"))
        return keyboard

# ==================== SYSTÈME D'AUTHENTIFICATION ====================
class AuthSystem:
    @staticmethod
    def is_master(user_id):
        return user_id == Config.MASTER_ID
    
    @staticmethod
    def is_admin(user_id):
        return user_id in Config.ADMIN_IDS
    
    @staticmethod
    def is_premium(user_id):
        user = db.get_user(user_id)
        return user and user.get('is_premium') and not user.get('is_banned')
    
    @staticmethod
    def is_banned(user_id):
        user = db.get_user(user_id)
        return user and user.get('is_banned')

# ==================== INITIALISATION ====================
db = MasterDatabase()
ai_engine = MasterAI()

# ==================== COMMANDES MAÎTRE ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Ami"
        
        # Enregistrer l'utilisateur ou le groupe
        if message.chat.type in ['group', 'supergroup']:
            db.add_group(message.chat.id, message.chat.title)
            bot.reply_to(message, "👥 NovaAI activé dans ce groupe ! Utilisez /help pour les commandes.")
            return
        
        # Enregistrer l'utilisateur
        user_type = "master" if AuthSystem.is_master(user_id) else "user"
        db.add_user(user_id, username, first_name, user_type)
        
        # Récupérer la personnalité
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        # Message spécial pour le maître
        if AuthSystem.is_master(user_id):
            stats = db.get_master_stats()
            welcome_text = f"""👑 <b>BIENVENUE MAÎTRE SUPRÊME !</b>

🤖 <b>NovaAI Master Control</b>
🎭 Personnalité: {personality_config['name']}

📊 <b>Votre Empire:</b>
• 👥 {stats['total_users']} Utilisateurs
• 👥 {stats['total_groups']} Groupes  
• 💬 {stats['total_messages']} Messages
• 💎 {stats['premium_users']} Premium
• 🚫 {stats['banned_users']} Bannis

⚡ <b>Vous avez le contrôle total !</b>"""
            
            bot.send_photo(
                message.chat.id,
                personality_config['photo'],
                caption=welcome_text,
                reply_markup=MasterInterface.create_master_menu()
            )
        else:
            # Message normal pour les utilisateurs
            welcome_text = f"""🎉 <b>BIENVENUE {first_name} !</b>

{personality_config['emoji']} <b>{personality_config['name']}</b>
✨ {personality_config['style']}

💬 <b>Parlez-moi de tout !</b>
🎭 <b>Changez de personnalité selon votre humeur</b>"""
            
            bot.send_photo(
                message.chat.id,
                personality_config['photo'],
                caption=welcome_text,
                reply_markup=MasterInterface.create_main_menu(personality)
            )
            
    except Exception as e:
        logger.error(f"Erreur start: {e}")
        bot.reply_to(message, "❌ Erreur d'initialisation. Réessayez.")

# ==================== COMMANDES DE CONTRÔLE MAÎTRE ====================
@bot.message_handler(commands=['master', 'admin', 'control'])
def master_command(message):
    if not AuthSystem.is_master(message.from_user.id):
        bot.reply_to(message, "🚫 <b>Accès réservé au Maître Suprême</b>")
        return
    
    stats = db.get_master_stats()
    master_text = f"""👑 <b>PANEL DE CONTRÔLE MAÎTRE</b>

⚡ <b>Commandes Disponibles:</b>

• <code>/stats</code> - Statistiques détaillées
• <code>/users</code> - Liste des utilisateurs
• <code>/groups</code> - Liste des groupes
• <code>/broadcast</code> - Message à tous
• <code>/premium [id]</code> - Donner premium
• <code>/ban [id]</code> - Bannir utilisateur
• <code>/unban [id]</code> - Débannir utilisateur
• <code>/restart</code> - Redémarrer le bot

📊 <b>Statistiques:</b>
• Utilisateurs: {stats['total_users']}
• Groupes: {stats['total_groups']}
• Messages: {stats['total_messages']}"""
    
    bot.reply_to(message, master_text, reply_markup=MasterInterface.create_master_menu())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    stats = db.get_master_stats()
    
    if AuthSystem.is_master(user_id):
        stats_text = f"""📈 <b>STATISTIQUES COMPLÈTES</b>

👥 <b>Utilisateurs:</b> {stats['total_users']}
💎 <b>Premium:</b> {stats['premium_users']}
🚫 <b>Bannis:</b> {stats['banned_users']}
👥 <b>Groupes:</b> {stats['total_groups']}
💬 <b>Messages:</b> {stats['total_messages']}

⚡ <b>Système:</b> 🟢 Opérationnel"""
    else:
        personality = ai_engine.get_user_personality(user_id)
        if personality == "amour":
            stats_text = f"📊 <b>Notre Communauté</b>\n\n👥 Utilisateurs: {stats['total_users']}\n💬 Messages: {stats['total_messages']}"
        elif personality == "mysterieux":
            stats_text = f"📊 <b>Énergies Collectives</b>\n\n👥 Âmes: {stats['total_users']}\n💬 Révélations: {stats['total_messages']}"
        else:
            stats_text = f"📊 <b>Système NovaAI</b>\n\n👥 Utilisateurs: {stats['total_users']}\n💬 Requêtes: {stats['total_messages']}"
    
    bot.reply_to(message, stats_text)

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if not AuthSystem.is_master(message.from_user.id):
        return
    
    broadcast_text = message.text.replace('/broadcast', '').strip()
    if not broadcast_text:
        bot.reply_to(message, "❌ Usage: /broadcast [message]")
        return
    
    users = db.get_all_users()
    groups = db.get_all_groups()
    total_sent = 0
    
    # Envoyer aux utilisateurs
    for user in users:
        try:
            bot.send_message(user[0], f"📢 <b>Message du Maître:</b>\n\n{broadcast_text}")
            total_sent += 1
            time.sleep(0.1)  # Anti-spam
        except:
            continue
    
    # Envoyer aux groupes
    for group in groups:
        try:
            bot.send_message(group[0], f"📢 <b>Annonce NovaAI:</b>\n\n{broadcast_text}")
            total_sent += 1
            time.sleep(0.1)
        except:
            continue
    
    bot.reply_to(message, f"✅ Message envoyé à {total_sent} destinataires")

@bot.message_handler(commands=['premium'])
def premium_command(message):
    if not AuthSystem.is_master(message.from_user.id):
        return
    
    try:
        target_id = int(message.text.split()[1])
        if db.set_premium(target_id):
            bot.reply_to(message, f"✅ Premium donné à l'utilisateur {target_id}")
        else:
            bot.reply_to(message, "❌ Erreur")
    except:
        bot.reply_to(message, "❌ Usage: /premium [user_id]")

@bot.message_handler(commands=['ban'])
def ban_command(message):
    if not AuthSystem.is_master(message.from_user.id):
        return
    
    try:
        target_id = int(message.text.split()[1])
        if db.ban_user(target_id):
            bot.reply_to(message, f"✅ Utilisateur {target_id} banni")
        else:
            bot.reply_to(message, "❌ Erreur")
    except:
        bot.reply_to(message, "❌ Usage: /ban [user_id]")

# ==================== COMMANDES UTILISATEURS ====================
@bot.message_handler(commands=['help', 'aide'])
def help_command(message):
    help_text = """🤖 <b>Commandes NovaAI</b>

• <code>/start</code> - Démarrer le bot
• <code>/help</code> - Afficher cette aide
• <code>/stats</code> - Statistiques
• <code>/personality</code> - Changer de personnalité
• <code>/music</code> - Écouter la musique
• <code>/voice</code> - Message vocal

🎭 <b>Personnalités:</b>
• 💖 Amoureux - Tendre et bienveillant
• 🔮 Mystérieux - Énigmatique et profond
• 💻 Hacker - Technique et direct

<b>Utilisez les boutons pour une navigation facile !</b>"""
    
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['personality'])
def personality_command(message):
    bot.reply_to(message, "🎭 <b>Choisissez votre personnalité:</b>", 
                 reply_markup=PersonalitySystem.get_personality_keyboard())

@bot.message_handler(commands=['music'])
def music_command(message):
    user_id = message.from_user.id
    personality = ai_engine.get_user_personality(user_id)
    ai_engine.send_music(message.chat.id, personality)

@bot.message_handler(commands=['voice'])
def voice_command(message):
    user_id = message.from_user.id
    personality = ai_engine.get_user_personality(user_id)
    ai_engine.send_voice_message(message.chat.id, personality)

# ==================== CALLBACKS MAÎTRE ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        
        # Répondre immédiatement
        bot.answer_callback_query(call.id, "⚡")
        
        # ========== CHANGEMENT PERSONNALITÉ ==========
        if call.data.startswith("personality_"):
            personality = call.data.replace("personality_", "")
            if db.set_personality(user_id, personality):
                personality_config = PersonalitySystem.get_personality_config(personality)
                
                # Envoyer la musique de la nouvelle personnalité
                ai_engine.send_music(chat_id, personality)
                
                # Nouveau message de confirmation
                bot.send_message(
                    chat_id,
                    f"✅ <b>Personnalité changée !</b>\n\n{personality_config['emoji']} <b>{personality_config['name']}</b>\n✨ {personality_config['style']}",
                    reply_markup=MasterInterface.create_main_menu(personality)
                )
        
        # ========== MUSIQUE ==========
        elif call.data == "music":
            personality = ai_engine.get_user_personality(user_id)
            ai_engine.send_music(chat_id, personality)
        
        # ========== VOICE ==========
        elif call.data == "voice":
            personality = ai_engine.get_user_personality(user_id)
            ai_engine.send_voice_message(chat_id, personality)
        
        # ========== STATISTIQUES ==========
        elif call.data == "stats":
            stats = db.get_master_stats()
            personality = ai_engine.get_user_personality(user_id)
            
            if AuthSystem.is_master(user_id):
                stats_text = f"""📈 <b>STATISTIQUES MAÎTRE</b>

👥 Utilisateurs: {stats['total_users']}
💎 Premium: {stats['premium_users']}
🚫 Bannis: {stats['banned_users']}
👥 Groupes: {stats['total_groups']}
💬 Messages: {stats['total_messages']}"""
            else:
                if personality == "amour":
                    stats_text = f"📊 <b>Notre Communauté</b>\n\n👥 {stats['total_users']} membres\n💬 {stats['total_messages']} messages"
                elif personality == "mysterieux":
                    stats_text = f"📊 <b>Énergies</b>\n\n👥 {stats['total_users']} âmes\n💬 {stats['total_messages']} révélations"
                else:
                    stats_text = f"📊 <b>Système</b>\n\n👥 {stats['total_users']} users\n💬 {stats['total_messages']} requests"
            
            bot.send_message(chat_id, stats_text, 
                           reply_markup=MasterInterface.create_main_menu(personality))
        
        # ========== CHANGER PERSONNALITÉ ==========
        elif call.data == "change_personality":
            bot.send_message(chat_id, "🎭 <b>Choisissez votre personnalité:</b>", 
                           reply_markup=PersonalitySystem.get_personality_keyboard())
        
        # ========== COMMANDES MAÎTRE ==========
        elif call.data == "master_stats":
            if AuthSystem.is_master(user_id):
                stats = db.get_master_stats()
                stats_text = f"""👑 <b>STATISTIQUES GLOBALES</b>

📊 <b>Utilisateurs:</b> {stats['total_users']}
💎 <b>Premium:</b> {stats['premium_users']}
🚫 <b>Bannis:</b> {stats['banned_users']}
👥 <b>Groupes:</b> {stats['total_groups']}
💬 <b>Messages:</b> {stats['total_messages']}

⚡ <b>Système:</b> 🟢 Optimal"""
                bot.send_message(chat_id, stats_text, reply_markup=MasterInterface.create_master_menu())
        
        elif call.data == "master_users":
            if AuthSystem.is_master(user_id):
                users = db.get_all_users()
                users_text = "👥 <b>DERNIERS UTILISATEURS</b>\n\n"
                for user in users[:10]:
                    status = "💎" if user[3] else "🔓"
                    banned = "🚫" if user[4] else "✅"
                    users_text += f"{status}{banned} {user[2]} - {user[5]} msgs\n"
                
                bot.send_message(chat_id, users_text, reply_markup=MasterInterface.create_master_menu())
        
        # ========== INFO PREMIUM ==========
        elif call.data == "premium_info":
            premium_text = """💎 <b>NOVAAI PREMIUM</b>

✨ <b>Avantages exclusifs:</b>
• Messages illimités
• Réponses prioritaires  
• Fonctions avancées
• Support personnalisé

📩 <b>Contactez le maître:</b> @Soszoe"""
            
            personality = ai_engine.get_user_personality(user_id)
            bot.send_message(chat_id, premium_text, 
                           reply_markup=MasterInterface.create_main_menu(personality))
                
    except Exception as e:
        logger.error(f"Erreur callback: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Erreur")
        except:
            pass

# ==================== GESTION DES MESSAGES ====================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        message_text = message.text.strip()
        
        if not message_text:
            return
        
        # Vérifier si banni
        if AuthSystem.is_banned(user_id):
            return
        
        # Gestion des groupes
        if message.chat.type in ['group', 'supergroup']:
            # Répondre seulement si le bot est mentionné ou en réponse
            if bot.get_me().username in message_text or message.reply_to_message:
                db.add_group(chat_id, message.chat.title)
                bot.send_chat_action(chat_id, 'typing')
                time.sleep(1)
                
                response = ai_engine.process_message(user_id, message_text, "group")
                bot.reply_to(message, response)
            return
        
        # Messages privés
        db.add_user(user_id, message.from_user.username, message.from_user.first_name)
        
        # Vérifier la limitation
        if not AntiBugSystem.rate_limit(user_id, "message", limit=15, window=60):
            bot.reply_to(message, "⏰ <b>Trop de messages !</b> Attendez 1 minute.")
            return
        
        # Typing indicator
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(1)
        
        # Traiter le message IA
        ai_response = ai_engine.process_message(user_id, message_text, "private")
        
        # Récupérer la personnalité
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        # Envoyer la réponse avec photo
        try:
            bot.send_photo(
                chat_id,
                personality_config['photo'],
                caption=f"{personality_config['emoji']} <b>{personality_config['name']}</b>\n\n{ai_response}",
                reply_to_message_id=message.message_id
            )
        except:
            bot.reply_to(
                message,
                f"{personality_config['emoji']} <b>{personality_config['name']}</b>\n\n{ai_response}"
            )
            
    except Exception as e:
        logger.error(f"Erreur message: {e}")
        try:
            bot.reply_to(message, "❌ <b>Erreur de traitement.</b> Réessayez.")
        except:
            pass

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("""
👑 NOVA-AI MASTER CONTROL 🤖
💖 Système de Contrôle Total Activé
⚡ Anti-Bugs Implementé
🎵 Voice Messages Réels
👥 Gestion Groupes/Chaines
🛡️ Système de Sécurité Renforcé

🟢 EN LIGNE - Prêt à obéir au Maître !
    """)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Erreur bot: {e}")
        time.sleep(5)
