#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - VERSION STABLE
💖 Tous les boutons fonctionnels + Musique + Admin
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
    
    # Musique pour chaque personnalité
    MUSIC_URLS = {
        "amour": "https://files.catbox.moe/h68fij.m4a",
        "mysterieux": "https://files.catbox.moe/h68fij.m4a", 
        "hacker": "https://files.catbox.moe/h68fij.m4a"
    }
    
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
            "music": "https://files.catbox.moe/h68fij.m4a"
        },
        "mysterieux": {
            "name": "🔮 NovaAI Mystérieux", 
            "emoji": "🔮",
            "photo": "https://files.catbox.moe/e9wjbf.jpg",
            "music": "https://files.catbox.moe/h68fij.m4a"
        },
        "hacker": {
            "name": "💻 NovaAI Hacker",
            "emoji": "💻",
            "photo": "https://files.catbox.moe/ndj85q.jpg",
            "music": "https://files.catbox.moe/h68fij.m4a"
        }
    }

bot = telebot.TeleBot(Config.TOKEN)

# ==================== BASE DE DONNÉES ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('nova_users.db', check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        cursor = self.conn.cursor()
        
        # Table utilisateurs
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
        join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, join_date) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, join_date))
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
                'is_premium': bool(user[3]),
                'message_count': user[4],
                'join_date': user[5],
                'personality': user[6] or 'amour'
            }
        return None
    
    def set_personality(self, user_id, personality):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET personality = ? WHERE user_id = ?', (personality, user_id))
        self.conn.commit()
        return True
    
    def increment_message_count(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET message_count = message_count + 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY join_date DESC')
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
    
    def set_premium(self, user_id, days=30):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_premium = 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        return True
    
    def set_all_premium(self):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_premium = 1')
        self.conn.commit()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]
    
    def remove_all_premium(self):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_premium = 0')
        self.conn.commit()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
        return cursor.fetchone()[0]

# ==================== SYSTÈME DE PERSONNALITÉS ====================
class PersonalitySystem:
    @staticmethod
    def get_personality_config(personality):
        return Config.PERSONALITIES.get(personality, Config.PERSONALITIES["amour"])
    
    @staticmethod
    def get_personality_prompt(personality):
        prompts = {
            "amour": "Tu es NovaAI Amoureux. Tu es chaleureux, bienveillant et attentionné. Utilise des émojis cœur 💖 et sois très affectueux.",
            "mysterieux": "Tu es NovaAI Mystérieux. Tu es énigmatique et profond. Utilise des émojis étoiles ✨ et sois mystérieux.",
            "hacker": "Tu es NovaAI Hacker. Tu es technique et direct. Utilise un langage geek et sois précis."
        }
        return prompts.get(personality, prompts["amour"])
    
    @staticmethod
    def get_personality_keyboard():
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("💖 Amoureux", callback_data="personality_amour"),
            InlineKeyboardButton("🔮 Mystérieux", callback_data="personality_mysterieux")
        )
        keyboard.row(InlineKeyboardButton("💻 Hacker", callback_data="personality_hacker"))
        keyboard.row(InlineKeyboardButton("🔙 Retour", callback_data="back_to_main"))
        return keyboard

# ==================== MOTEUR IA ====================
class MultiPersonalityAI:
    def __init__(self):
        self.db = Database()
    
    def get_user_personality(self, user_id):
        user = self.db.get_user(user_id)
        return user['personality'] if user else 'amour'
    
    def send_music(self, chat_id, personality):
        try:
            music_url = Config.MUSIC_URLS.get(personality)
            if music_url:
                bot.send_audio(chat_id, music_url, caption="🎵 Votre musique NovaAI !")
                return True
        except Exception as e:
            print(f"Erreur musique: {e}")
        return False
    
    def process_message(self, user_id, user_message):
        if not Config.GROQ_API_KEY:
            return "🤖 Le système IA est temporairement indisponible. Réessayez plus tard."
        
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
                return "❌ Erreur de connexion avec l'IA. Réessayez dans quelques instants."
                
        except Exception as e:
            return f"❌ Erreur temporaire: {str(e)}"

# ==================== INTERFACES ====================
class Interface:
    @staticmethod
    def create_main_menu(personality="amour"):
        keyboard = InlineKeyboardMarkup()
        
        if personality == "amour":
            keyboard.row(
                InlineKeyboardButton("📊 Statistiques", callback_data="stats"),
                InlineKeyboardButton("🎵 Musique", callback_data="music")
            )
            keyboard.row(
                InlineKeyboardButton("🎭 Personnalité", callback_data="change_personality"),
                InlineKeyboardButton("💎 Premium", callback_data="premium_info")
            )
            keyboard.row(InlineKeyboardButton("🆘 Support", url="https://t.me/Soszoe"))
            
        elif personality == "mysterieux":
            keyboard.row(
                InlineKeyboardButton("📊 Énergies", callback_data="stats"),
                InlineKeyboardButton("🎵 Musique", callback_data="music")
            )
            keyboard.row(
                InlineKeyboardButton("🎭 Aura", callback_data="change_personality"),
                InlineKeyboardButton("💎 Arcanes", callback_data="premium_info")
            )
            keyboard.row(InlineKeyboardButton("🆘 Guide", url="https://t.me/Soszoe"))
            
        else:  # hacker
            keyboard.row(
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
                InlineKeyboardButton("🎵 Audio", callback_data="music")
            )
            keyboard.row(
                InlineKeyboardButton("🎭 Mode", callback_data="change_personality"),
                InlineKeyboardButton("💎 Root", callback_data="premium_info")
            )
            keyboard.row(InlineKeyboardButton("🆘 Support", url="https://t.me/Soszoe"))
        
        return keyboard
    
    @staticmethod
    def create_admin_menu():
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("📊 Dashboard", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_all_users")
        )
        keyboard.row(
            InlineKeyboardButton("💎 Premium Tous", callback_data="admin_premium_all"),
            InlineKeyboardButton("🚫 Retirer Premium", callback_data="admin_remove_premium")
        )
        keyboard.row(
            InlineKeyboardButton("🎭 Personnalités", callback_data="admin_personalities"),
            InlineKeyboardButton("🔄 Actualiser", callback_data="admin_refresh")
        )
        keyboard.row(InlineKeyboardButton("🔙 Menu Principal", callback_data="back_to_main"))
        return keyboard

# ==================== INITIALISATION ====================
db = Database()
ai_engine = MultiPersonalityAI()

# ==================== COMMANDES BOT ====================
@bot.message_handler(commands=['start', 'aide', 'help'])
def start_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Ami"
        
        # Enregistrer l'utilisateur
        db.add_user(user_id, username, first_name)
        
        # Récupérer la personnalité
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        # Obtenir les stats réelles
        stats = db.get_stats()
        user_count = stats['total_users']
        
        # Message de bienvenue selon le rôle
        if user_id == Config.ADMIN_ID:
            welcome_text = f"""👑 BIENVENUE DANS VOTRE ROYAUME, MAÎTRE !

{user_count} âmes connectées à votre empire NovaAI

✨ Votre NovaAI {personality_config['name']} vous attend
📊 Tableau de bord administrateur activé
🎛️ Contrôlez votre empire avec sagesse

Choisissez votre action, créateur bien-aimé !"""
            menu = Interface.create_admin_menu()
        else:
            welcome_text = f"""🎉 BIENVENUE DANS LA FAMILLE NOVAAI, {first_name.upper()} !

{personality_config['emoji']} **{personality_config['name']}**
✨ Prêt à vous accompagner avec bienveillance

👥 **{user_count} personnes** partagent déjà cette belle énergie
💬 Parlez-moi de tout, je suis là pour vous écouter
🎭 Changez de personnalité selon votre humeur

*L'aventure NovaAI commence maintenant !*"""
            menu = Interface.create_main_menu(personality)
        
        # Envoyer la photo avec menu
        bot.send_photo(
            message.chat.id,
            personality_config['photo'],
            caption=welcome_text,
            parse_mode='Markdown',
            reply_markup=menu
        )
        
    except Exception as e:
        print(f"Erreur start: {e}")
        bot.reply_to(message, "🎯 Bienvenue ! Utilisez les boutons ci-dessous pour naviguer.")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    try:
        user_id = message.from_user.id
        personality = ai_engine.get_user_personality(user_id)
        stats = db.get_stats()
        
        if personality == "amour":
            stats_text = f"""📊 **STATISTIQUES NOTRE FAMILLE** 💖

👥 **Âmes connectées :** {stats['total_users']}
💎 **Cœurs premium :** {stats['premium_users']}
💬 **Messages d'amour :** {stats['total_messages']}
🎭 **Votre aura :** Amoureuse 💖

*Notre famille grandit chaque jour !*"""
        
        elif personality == "mysterieux":
            stats_text = f"""📊 **LES CHIFFRES DU DESTIN** 🔮

👥 **Âmes dans le vortex :** {stats['total_users']}
💎 **Initiés aux arcanes :** {stats['premium_users']}
💬 **Révélations partagées :** {stats['total_messages']}
🎭 **Votre aura :** Mystérieuse 🔮

*Les énergies s'équilibrent...*"""
        
        else:
            stats_text = f"""📊 **RAPPORT SYSTÈME NOVAAI** 💻

👥 **UTILISATEURS CONNECTÉS :** {stats['total_users']}
💎 **ACCÈS ROOT ACTIFS :** {stats['premium_users']}
💬 **REQUÊTES TRAITÉES :** {stats['total_messages']}
🎭 **VOTRE MODE :** HACKER 💻

*SYSTÈME OPÉRATIONNEL*"""
        
        bot.reply_to(message, stats_text, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, "❌ Erreur lors du chargement des statistiques.")

@bot.message_handler(commands=['personality', 'personnalite'])
def personality_command(message):
    try:
        user_id = message.from_user.id
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        # Envoyer la musique actuelle
        ai_engine.send_music(message.chat.id, personality)
        
        time.sleep(1)
        
        text = f"""🎭 **CHOISISSEZ VOTRE PERSONNALITÉ NOVAAI**

Personnalité actuelle: {personality_config['name']}

💖 **Mode Amoureux** 
Tendresse, bienveillance, support émotionnel

🔮 **Mode Mystérieux**
Énigmes, mystères, sagesse ancienne

💻 **Mode Hacker**
Technique, précis, univers geek

*Votre expérience s'adaptera à votre humeur !*"""
        
        bot.send_message(
            message.chat.id,
            text,
            parse_mode='Markdown',
            reply_markup=PersonalitySystem.get_personality_keyboard()
        )
    except Exception as e:
        bot.reply_to(message, "❌ Erreur changement de personnalité.")

@bot.message_handler(commands=['music', 'musique', 'audio'])
def music_command(message):
    try:
        user_id = message.from_user.id
        personality = ai_engine.get_user_personality(user_id)
        
        if ai_engine.send_music(message.chat.id, personality):
            bot.reply_to(message, "🎵 Voici votre musique NovaAI !")
        else:
            bot.reply_to(message, "❌ Musique temporairement indisponible.")
    except Exception as e:
        bot.reply_to(message, "❌ Erreur lecture musique.")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    try:
        user_id = message.from_user.id
        if user_id == Config.ADMIN_ID:
            stats = db.get_stats()
            
            admin_text = f"""👑 **PANEL ADMINISTRATEUR**

📊 **Statistiques:**
• Utilisateurs: {stats['total_users']}
• Premium: {stats['premium_users']}
• Messages: {stats['total_messages']}

⚡ **Commandes disponibles:**
• /stats - Voir les statistiques
• /personality - Changer personnalité
• /music - Écouter la musique
• /admin - Panel administrateur

*Utilisez les boutons pour gérer votre empire.*"""
            
            bot.send_message(
                message.chat.id,
                admin_text,
                parse_mode='Markdown',
                reply_markup=Interface.create_admin_menu()
            )
        else:
            bot.reply_to(message, "🚫 Accès réservé à l'administrateur.")
    except Exception as e:
        bot.reply_to(message, "❌ Erreur commande admin.")

# ==================== CALLBACKS - TOUS FONCTIONNELS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # ========== CHANGEMENT PERSONNALITÉ ==========
        if call.data.startswith("personality_"):
            personality = call.data.replace("personality_", "")
            success = db.set_personality(user_id, personality)
            
            if success:
                personality_config = PersonalitySystem.get_personality_config(personality)
                
                # Envoyer la musique de la nouvelle personnalité
                ai_engine.send_music(chat_id, personality)
                
                time.sleep(1)
                
                # Modifier le message
                bot.edit_message_text(
                    f"✅ **Personnalité changée !**\n\n{personality_config['emoji']} **{personality_config['name']}**\n\n*Nouvelle personnalité activée avec succès !*",
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=Interface.create_main_menu(personality)
                )
                
                bot.answer_callback_query(call.id, f"🎭 {personality_config['name']}")
            else:
                bot.answer_callback_query(call.id, "❌ Erreur changement")
        
        # ========== MUSIQUE ==========
        elif call.data == "music":
            personality = ai_engine.get_user_personality(user_id)
            if ai_engine.send_music(chat_id, personality):
                bot.answer_callback_query(call.id, "🎵 Musique envoyée !")
            else:
                bot.answer_callback_query(call.id, "❌ Musique indisponible")
        
        # ========== STATISTIQUES ==========
        elif call.data == "stats":
            personality = ai_engine.get_user_personality(user_id)
            stats = db.get_stats()
            
            if personality == "amour":
                stats_text = f"📊 **NOTRE FAMILLE**\n\n👥 Âmes: {stats['total_users']}\n💎 Cœurs: {stats['premium_users']}\n💬 Messages: {stats['total_messages']}"
            elif personality == "mysterieux":
                stats_text = f"📊 **ÉNERGIES**\n\n👥 Âmes: {stats['total_users']}\n💎 Initiés: {stats['premium_users']}\n💬 Révélations: {stats['total_messages']}"
            else:
                stats_text = f"📊 **SYSTÈME**\n\n👥 UTILISATEURS: {stats['total_users']}\n💎 ROOT: {stats['premium_users']}\n💬 REQUÊTES: {stats['total_messages']}"
            
            bot.edit_message_text(
                stats_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=Interface.create_main_menu(personality)
            )
            bot.answer_callback_query(call.id, "📊 Statistiques")
        
        # ========== INFO PREMIUM ==========
        elif call.data == "premium_info":
            personality = ai_engine.get_user_personality(user_id)
            
            if personality == "amour":
                premium_text = "💖 **NOVAAI PREMIUM**\n\n• Messages illimités du cœur\n• Réponses prioritaires\n• Fonctions exclusives\n• Support personnalisé\n\n📩 Contact: @Soszoe"
            elif personality == "mysterieux":
                premium_text = "💎 **ACCÈS ARCANES**\n\n• Révélations illimitées\n• Vision prioritaire\n• Secrets exclusifs\n• Guidance personnalisée\n\n📩 Contact: @Soszoe"
            else:
                premium_text = "💻 **ACCÈS ROOT**\n\n• Accès root illimité\n• Priorité système\n• Fonctions admin\n• Support technique\n\n📩 Contact: @Soszoe"
            
            bot.edit_message_text(
                premium_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=Interface.create_main_menu(personality)
            )
            bot.answer_callback_query(call.id, "💎 Info Premium")
        
        # ========== CHANGER PERSONNALITÉ ==========
        elif call.data == "change_personality":
            text = "🎭 **CHOISISSEZ VOTRE PERSONNALITÉ:**"
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=PersonalitySystem.get_personality_keyboard()
            )
            bot.answer_callback_query(call.id, "🎭 Personnalités")
        
        # ========== RETOUR MENU ==========
        elif call.data == "back_to_main":
            personality = ai_engine.get_user_personality(user_id)
            stats = db.get_stats()
            
            if user_id == Config.ADMIN_ID:
                welcome_text = f"👑 **TABLEAU DE BORD ADMIN**\n\n📊 {stats['total_users']} utilisateurs\n💎 {stats['premium_users']} premium\n💬 {stats['total_messages']} messages"
                menu = Interface.create_admin_menu()
            else:
                personality_config = PersonalitySystem.get_personality_config(personality)
                welcome_text = f"{personality_config['emoji']} **{personality_config['name']}**\n\n👥 {stats['total_users']} utilisaires\n💬 {stats['total_messages']} messages"
                menu = Interface.create_main_menu(personality)
            
            bot.edit_message_text(
                welcome_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=menu
            )
            bot.answer_callback_query(call.id, "🔙 Menu principal")
        
        # ========== ADMIN - STATISTIQUES ==========
        elif call.data == "admin_stats":
            if user_id == Config.ADMIN_ID:
                stats = db.get_stats()
                all_users = db.get_all_users()
                
                admin_text = f"""👑 **DASHBOARD ADMINISTRATEUR**

📈 **Statistiques Globales:**
• 👥 Utilisateurs totaux: {stats['total_users']}
• 💎 Utilisateurs premium: {stats['premium_users']}
• 💬 Messages totaux: {stats['total_messages']}

👤 **Derniers utilisateurs:**"""
                
                for i, user in enumerate(all_users[:5], 1):
                    admin_text += f"\n{i}. {user[2]} (@{user[1]}) - {user[4]} msgs"
                
                bot.edit_message_text(
                    admin_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=Interface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "📊 Dashboard")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        # ========== ADMIN - TOUS LES UTILISATEURS ==========
        elif call.data == "admin_all_users":
            if user_id == Config.ADMIN_ID:
                all_users = db.get_all_users()
                
                users_text = "👥 **LISTE DES UTILISATEURS**\n\n"
                for i, user in enumerate(all_users[:10], 1):
                    premium = "💎" if user[3] else "🔓"
                    users_text += f"{i}. {premium} {user[2]} - {user[4]} msgs\n"
                
                if len(all_users) > 10:
                    users_text += f"\n... et {len(all_users) - 10} autres"
                
                bot.edit_message_text(
                    users_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=Interface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "👥 Utilisateurs")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        # ========== ADMIN - PREMIUM TOUS ==========
        elif call.data == "admin_premium_all":
            if user_id == Config.ADMIN_ID:
                count = db.set_all_premium()
                bot.edit_message_text(
                    f"💎 **PREMIUM ACTIVÉ POUR TOUS !**\n\n{count} utilisateurs sont maintenant premium.",
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=Interface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "💎 Premium activé")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        # ========== ADMIN - RETIRER PREMIUM ==========
        elif call.data == "admin_remove_premium":
            if user_id == Config.ADMIN_ID:
                count = db.remove_all_premium()
                bot.edit_message_text(
                    f"🚫 **PREMIUM RETIRÉ POUR TOUS !**\n\n{count} utilisateurs affectés.",
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=Interface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "🚫 Premium retiré")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        # ========== ADMIN - PERSONNALITÉS ==========
        elif call.data == "admin_personalities":
            if user_id == Config.ADMIN_ID:
                all_users = db.get_all_users()
                personality_count = {"amour": 0, "mysterieux": 0, "hacker": 0}
                
                for user in all_users:
                    personality = user[6] or 'amour'
                    personality_count[personality] = personality_count.get(personality, 0) + 1
                
                personalities_text = "🎭 **STATISTIQUES PERSONNALITÉS**\n\n"
                for personality, count in personality_count.items():
                    config = PersonalitySystem.get_personality_config(personality)
                    personalities_text += f"{config['emoji']} {config['name']}: {count} utilisateurs\n"
                
                bot.edit_message_text(
                    personalities_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=Interface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "🎭 Personnalités")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        # ========== ADMIN - ACTUALISER ==========
        elif call.data == "admin_refresh":
            if user_id == Config.ADMIN_ID:
                stats = db.get_stats()
                bot.answer_callback_query(call.id, "🔄 Actualisé !")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
                
    except Exception as e:
        print(f"Erreur callback: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Erreur, réessayez")
        except:
            pass

# ==================== GESTION DES MESSAGES ====================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        if message.chat.type in ['group', 'supergroup']:
            return
            
        user_id = message.from_user.id
        user_message = message.text.strip()
        
        if len(user_message) < 1:
            return
        
        # Enregistrer l'utilisateur
        db.add_user(user_id, message.from_user.username or "User", message.from_user.first_name or "User")
        
        # Typing indicator
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Traiter le message IA
        ai_response = ai_engine.process_message(user_id, user_message)
        
        # Récupérer la personnalité
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        # Envoyer la réponse
        try:
            bot.send_photo(
                message.chat.id,
                personality_config['photo'],
                caption=f"{personality_config['emoji']} **{personality_config['name']}**\n\n{ai_response}",
                parse_mode='Markdown',
                reply_to_message_id=message.message_id
            )
        except:
            bot.reply_to(
                message,
                f"{personality_config['emoji']} **{personality_config['name']}**\n\n{ai_response}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        print(f"Erreur message: {e}")
        try:
            bot.reply_to(message, "❌ Erreur de traitement. Réessayez.")
        except:
            pass

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🎮 NOVA-AI - SYSTÈME COMPLET ACTIVÉ")
    print("✅ Base de données: OK")
    print("✅ Personnalités: OK") 
    print("✅ Musique: OK")
    print("✅ Commandes admin: OK")
    print("✅ Boutons: TOUS FONCTIONNELS")
    print("🟢 En attente de messages...")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
