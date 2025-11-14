#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - MULTI-PERSONNALITÉS
💖 Version Complètement Fonctionnelle
👑 Créé par Kervens
"""

import telebot
import requests
import os
import sqlite3
import json
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

# ==================== CONFIGURATION ====================
class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    ADMIN_ID = 7908680781
    
    # Photos pour chaque personnalité
    PERSONALITY_PHOTOS = {
        "amour": "https://files.catbox.moe/tta6ta.jpg",
        "mysterieux": "https://files.catbox.moe/e9wjbf.jpg", 
        "hacker": "https://files.catbox.moe/ndj85q.jpg"
    }
    
    # Personnalités disponibles
    PERSONALITIES = {
        "amour": {
            "name": "💖 NovaAI Amoureux",
            "emoji": "💖",
            "photo": "https://files.catbox.moe/tta6ta.jpg",
            "voice_text": "💖 Bonjour mon ami ! Je suis NovaAI dans ma personnalité amoureuse. Mon cœur bat pour vous écouter avec bienveillance et tendresse."
        },
        "mysterieux": {
            "name": "🔮 NovaAI Mystérieux", 
            "emoji": "🔮",
            "photo": "https://files.catbox.moe/e9wjbf.jpg",
            "voice_text": "🔮 Bienvenue dans le sanctuaire des mystères... Je suis NovaAI l'énigmatique. Les étoiles murmurent vos secrets..."
        },
        "hacker": {
            "name": "💻 NovaAI Hacker",
            "emoji": "💻",
            "photo": "https://files.catbox.moe/ndj85q.jpg",
            "voice_text": "💻 Système NovaAI en mode hacker. Connexion établie. Authentification validée. Prêt à recevoir vos commandes."
        }
    }

bot = telebot.TeleBot(Config.TOKEN)

# ==================== BASE DE DONNÉES SIMPLIFIÉE ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('nova_users.db', check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                join_date TEXT,
                personality TEXT DEFAULT 'amour'
            )
        ''')
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name):
        cursor = self.conn.cursor()
        join_date = datetime.now().isoformat()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, join_date, personality) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, join_date, 'amour'))
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
                'first_name': user[2],
                'is_premium': user[3],
                'message_count': user[4],
                'join_date': user[5],
                'personality': user[6]
            }
        return None
    
    def set_personality(self, user_id, personality):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET personality = ? WHERE user_id = ?', (personality, user_id))
        self.conn.commit()
    
    def increment_message_count(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET message_count = message_count + 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users')
        return cursor.fetchall()
    
    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
        premium_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(message_count) FROM users')
        total_messages = cursor.fetchone()[0] or 0
        
        return {
            'total_users': total_users,
            'premium_users': premium_users,
            'total_messages': total_messages
        }

# ==================== COMPTEUR RÉEL ====================
class CounterSystem:
    @staticmethod
    def get_user_count():
        try:
            db = Database()
            stats = db.get_stats()
            return stats['total_users']
        except:
            return 0

# ==================== SYSTÈME DE PERSONNALITÉS ====================
class PersonalitySystem:
    @staticmethod
    def get_personality_config(personality):
        return Config.PERSONALITIES.get(personality, Config.PERSONALITIES["amour"])
    
    @staticmethod
    def get_personality_prompt(personality):
        prompts = {
            "amour": "Tu es NovaAI Amoureux. Tu es chaleureux, bienveillant et attentionné. Ton ton est rempli d'amour et de douceur.",
            "mysterieux": "Tu es NovaAI Mystérieux. Tu es énigmatique et profond. Ton ton est intrigant et mystique.",
            "hacker": "Tu es NovaAI Hacker. Tu es technique et direct. Ton ton est précis et geek."
        }
        return prompts.get(personality, prompts["amour"])
    
    @staticmethod
    def get_personality_keyboard():
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("💖 Amoureux", callback_data="personality_amour"))
        keyboard.add(InlineKeyboardButton("🔮 Mystérieux", callback_data="personality_mysterieux"))
        keyboard.add(InlineKeyboardButton("💻 Hacker", callback_data="personality_hacker"))
        keyboard.add(InlineKeyboardButton("🔙 Retour", callback_data="back_to_main"))
        return keyboard

# ==================== MOTEUR IA ====================
class MultiPersonalityAI:
    def __init__(self):
        self.db = Database()
    
    def get_user_personality(self, user_id):
        user = self.db.get_user(user_id)
        return user['personality'] if user else 'amour'
    
    def send_voice_message(self, chat_id, personality):
        personality_config = PersonalitySystem.get_personality_config(personality)
        bot.send_message(chat_id, f"🎤 {personality_config['voice_text']}")
    
    def process_message(self, user_id, user_message):
        if not Config.GROQ_API_KEY:
            return "🤖 Le système est en maintenance. Réessayez plus tard."
        
        personality = self.get_user_personality(user_id)
        system_prompt = PersonalitySystem.get_personality_prompt(personality)
        
        try:
            headers = {
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "model": "llama-3.1-8b-instant",
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                self.db.increment_message_count(user_id)
                return ai_response
            else:
                return "❌ Erreur de connexion. Réessayez."
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"

# ==================== INTERFACES ====================
class Interface:
    @staticmethod
    def create_main_menu(personality="amour"):
        keyboard = InlineKeyboardMarkup()
        
        if personality == "amour":
            keyboard.add(InlineKeyboardButton("📊 Statistiques", callback_data="stats"))
            keyboard.add(InlineKeyboardButton("🎭 Changer Personnalité", callback_data="change_personality"))
            keyboard.add(InlineKeyboardButton("🎤 Message Vocal", callback_data="voice_message"))
            keyboard.add(InlineKeyboardButton("💎 Premium", callback_data="premium_info"))
            
        elif personality == "mysterieux":
            keyboard.add(InlineKeyboardButton("📊 Énergies", callback_data="stats"))
            keyboard.add(InlineKeyboardButton("🎭 Changer d'Aura", callback_data="change_personality"))
            keyboard.add(InlineKeyboardButton("🎤 Incantation", callback_data="voice_message"))
            keyboard.add(InlineKeyboardButton("💎 Arcanes", callback_data="premium_info"))
            
        else:  # hacker
            keyboard.add(InlineKeyboardButton("📊 Stats Système", callback_data="stats"))
            keyboard.add(InlineKeyboardButton("🎭 Changer Mode", callback_data="change_personality"))
            keyboard.add(InlineKeyboardButton("🎤 Audio", callback_data="voice_message"))
            keyboard.add(InlineKeyboardButton("💎 Root", callback_data="premium_info"))
        
        return keyboard
    
    @staticmethod
    def create_admin_menu():
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📊 Dashboard", callback_data="admin_stats"))
        keyboard.add(InlineKeyboardButton("👥 Tous les Utilisateurs", callback_data="admin_all_users"))
        keyboard.add(InlineKeyboardButton("🔄 Actualiser", callback_data="admin_refresh"))
        return keyboard

# ==================== INITIALISATION ====================
db = Database()
ai_engine = MultiPersonalityAI()

# ==================== HANDLERS PRINCIPAUX ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Ami"
        
        # Enregistrer l'utilisateur
        is_new_user = db.add_user(user_id, username, first_name)
        
        # Récupérer la personnalité
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        # Compter les utilisateurs RÉELS
        user_count = CounterSystem.get_user_count()
        
        # Message de bienvenue
        if user_id == Config.ADMIN_ID:
            welcome_text = f"""👑 BIENVENUE MAÎTRE !

🎭 Votre NovaAI {personality_config['name']} vous attend
👥 {user_count} âmes connectées
📊 Tableau de bord administrateur activé"""
            menu = Interface.create_admin_menu()
        else:
            welcome_text = f"""🎉 BIENVENUE {first_name} !

{personality_config['emoji']} Je suis {personality_config['name']}
👥 {user_count} personnes utilisent déjà NovaAI

💬 Parle-moi de tout, je suis là pour toi !"""
            menu = Interface.create_main_menu(personality)
        
        # Envoyer la photo avec le menu
        bot.send_photo(
            message.chat.id,
            personality_config['photo'],
            caption=welcome_text,
            reply_markup=menu
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    try:
        user_id = message.from_user.id
        personality = ai_engine.get_user_personality(user_id)
        stats = db.get_stats()
        user_count = CounterSystem.get_user_count()
        
        if personality == "amour":
            stats_text = f"""📊 STATISTIQUES RÉELLES

👥 Utilisateurs: {stats['total_users']}
💎 Premium: {stats['premium_users']}
💬 Messages: {stats['total_messages']}
🎭 Votre mode: Amoureux 💖"""
        
        elif personality == "mysterieux":
            stats_text = f"""📊 ÉNERGIES COSMIQUES

👥 Âmes connectées: {stats['total_users']}
💎 Initiés: {stats['premium_users']}
💬 Révélations: {stats['total_messages']}
🎭 Votre aura: Mystérieuse 🔮"""
        
        else:
            stats_text = f"""📊 RAPPORT SYSTÈME

👥 UTILISATEURS: {stats['total_users']}
💎 ROOT: {stats['premium_users']}
💬 REQUÊTES: {stats['total_messages']}
🎭 VOTRE MODE: HACKER 💻"""
        
        bot.reply_to(message, stats_text)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

@bot.message_handler(commands=['personality'])
def personality_command(message):
    try:
        text = """🎭 CHOISISSEZ VOTRE PERSONNALITÉ

💖 Amoureux - Tendre et bienveillant
🔮 Mystérieux - Énigmatique et profond  
💻 Hacker - Technique et direct

Chaque personnalité a son propre style !"""
        
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=PersonalitySystem.get_personality_keyboard()
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

@bot.message_handler(commands=['voice'])
def voice_command(message):
    try:
        user_id = message.from_user.id
        personality = ai_engine.get_user_personality(user_id)
        ai_engine.send_voice_message(message.chat.id, personality)
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

# ==================== CALLBACKS CORRIGÉS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # Changement de personnalité
        if call.data.startswith("personality_"):
            personality = call.data.replace("personality_", "")
            db.set_personality(user_id, personality)
            
            personality_config = PersonalitySystem.get_personality_config(personality)
            
            # Modifier le message
            bot.edit_message_text(
                f"✅ Personnalité changée: {personality_config['name']}",
                chat_id,
                message_id
            )
            
            # Envoyer la nouvelle présentation
            time.sleep(1)
            bot.send_message(
                chat_id,
                f"🎤 {personality_config['voice_text']}",
                reply_markup=Interface.create_main_menu(personality)
            )
            
            bot.answer_callback_query(call.id, "Personnalité changée !")
        
        # Message vocal
        elif call.data == "voice_message":
            personality = ai_engine.get_user_personality(user_id)
            ai_engine.send_voice_message(chat_id, personality)
            bot.answer_callback_query(call.id, "Message vocal envoyé !")
        
        # Statistiques
        elif call.data == "stats":
            personality = ai_engine.get_user_personality(user_id)
            stats = db.get_stats()
            
            if personality == "amour":
                stats_text = f"📊 STATISTIQUES\n\n👥 Utilisateurs: {stats['total_users']}\n💬 Messages: {stats['total_messages']}"
            elif personality == "mysterieux":
                stats_text = f"📊 ÉNERGIES\n\n👥 Âmes: {stats['total_users']}\n💬 Révélations: {stats['total_messages']}"
            else:
                stats_text = f"📊 SYSTÈME\n\n👥 UTILISATEURS: {stats['total_users']}\n💬 REQUÊTES: {stats['total_messages']}"
            
            bot.edit_message_text(
                stats_text,
                chat_id,
                message_id,
                reply_markup=Interface.create_main_menu(personality)
            )
            bot.answer_callback_query(call.id, "Statistiques")
        
        # Info Premium
        elif call.data == "premium_info":
            personality = ai_engine.get_user_personality(user_id)
            
            if personality == "amour":
                premium_text = "💖 NOVAAI PREMIUM\n\nMessages illimités\nSupport prioritaire\nFonctions exclusives\n\nContact: @Soszoe"
            elif personality == "mysterieux":
                premium_text = "💎 ACCÈS ARCANES\n\nRévélations illimitées\nVision prioritaire\nSecrets exclusifs\n\nContact: @Soszoe"
            else:
                premium_text = "💻 ACCÈS ROOT\n\nAccès illimité\nPriorité système\nFonctions admin\n\nContact: @Soszoe"
            
            bot.edit_message_text(
                premium_text,
                chat_id,
                message_id,
                reply_markup=Interface.create_main_menu(personality)
            )
            bot.answer_callback_query(call.id, "Info Premium")
        
        # Changer personnalité
        elif call.data == "change_personality":
            text = "🎭 CHOISISSEZ VOTRE PERSONNALITÉ:"
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=PersonalitySystem.get_personality_keyboard()
            )
            bot.answer_callback_query(call.id, "Changer personnalité")
        
        # Retour au menu
        elif call.data == "back_to_main":
            personality = ai_engine.get_user_personality(user_id)
            user_count = CounterSystem.get_user_count()
            
            if user_id == Config.ADMIN_ID:
                welcome_text = f"👑 TABLEAU DE BORD ADMIN\n\n👥 {user_count} utilisateurs"
                menu = Interface.create_admin_menu()
            else:
                personality_config = PersonalitySystem.get_personality_config(personality)
                welcome_text = f"{personality_config['emoji']} {personality_config['name']}\n\n👥 {user_count} utilisateurs"
                menu = Interface.create_main_menu(personality)
            
            bot.edit_message_text(
                welcome_text,
                chat_id,
                message_id,
                reply_markup=menu
            )
            bot.answer_callback_query(call.id, "Menu principal")
        
        # Admin - Statistiques
        elif call.data == "admin_stats":
            if user_id == Config.ADMIN_ID:
                stats = db.get_stats()
                all_users = db.get_all_users()
                
                admin_text = f"""👑 DASHBOARD ADMIN

📊 STATISTIQUES:
• Utilisateurs: {stats['total_users']}
• Premium: {stats['premium_users']}
• Messages: {stats['total_messages']}

👤 DERNIERS UTILISATEURS:"""
                
                for user in all_users[:5]:
                    admin_text += f"\n• {user[2]} (@{user[1]}) - {user[4]} msgs"
                
                bot.edit_message_text(
                    admin_text,
                    chat_id,
                    message_id,
                    reply_markup=Interface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "Dashboard admin")
            else:
                bot.answer_callback_query(call.id, "❌ Accès refusé")
        
        # Admin - Tous les utilisateurs
        elif call.data == "admin_all_users":
            if user_id == Config.ADMIN_ID:
                all_users = db.get_all_users()
                
                users_text = "👥 TOUS LES UTILISATEURS:\n\n"
                for user in all_users[:15]:
                    users_text += f"• {user[2]} - {user[4]} msgs\n"
                
                if len(all_users) > 15:
                    users_text += f"\n... et {len(all_users) - 15} autres"
                
                bot.edit_message_text(
                    users_text,
                    chat_id,
                    message_id,
                    reply_markup=Interface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "Liste utilisateurs")
            else:
                bot.answer_callback_query(call.id, "❌ Accès refusé")
        
        # Admin - Actualiser
        elif call.data == "admin_refresh":
            if user_id == Config.ADMIN_ID:
                stats = db.get_stats()
                bot.answer_callback_query(call.id, "✅ Actualisé")
            else:
                bot.answer_callback_query(call.id, "❌ Accès refusé")
                
    except Exception as e:
        print(f"Erreur callback: {e}")
        bot.answer_callback_query(call.id, "❌ Erreur, réessayez")

# ==================== GESTION DES MESSAGES ====================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        if message.chat.type in ['group', 'supergroup']:
            return
            
        user_id = message.from_user.id
        user_message = message.text.strip()
        
        if len(user_message) < 2:
            return
        
        # Enregistrer l'utilisateur s'il n'existe pas
        db.add_user(user_id, message.from_user.username or "User", message.from_user.first_name or "User")
        
        # Afficher "typing"
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Traiter le message avec l'IA
        ai_response = ai_engine.process_message(user_id, user_message)
        
        # Récupérer la personnalité pour la réponse
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        # Envoyer la réponse avec la photo de personnalité
        try:
            bot.send_photo(
                message.chat.id,
                personality_config['photo'],
                caption=f"{personality_config['emoji']} {personality_config['name']}\n\n{ai_response}",
                reply_to_message_id=message.message_id
            )
        except:
            # Fallback si l'image ne charge pas
            bot.reply_to(
                message,
                f"{personality_config['emoji']} {personality_config['name']}\n\n{ai_response}"
            )
            
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🤖 NOVA-AI DÉMARRAGE...")
    print("✅ Base de données initialisée")
    print("✅ Système de personnalités chargé")
    print("✅ Handlers configurés")
    print("🟢 Bot en attente de messages...")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
