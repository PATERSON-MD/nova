#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - MULTI-PERSONNALITÉS AVEC VOICE
💖 Édition avec Voice Messages Générés
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

# ==================== CONFIGURATION MULTI-PERSONNALITÉS ====================
class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    CREATOR = "👑 Kervens"
    BOT_NAME = "🎭 NovaAI Multi-Personnalités"
    VERSION = "✨ Édition Voice Générés"
    
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
            "color": "rose",
            "photo": "https://files.catbox.moe/tta6ta.jpg",
            "voice_text": "💖 Bonjour mon ami ! Je suis NovaAI dans ma personnalité amoureuse. Mon cœur bat pour vous écouter avec bienveillance et tendresse. Parlez-moi de tout, je suis là pour vous !"
        },
        "mysterieux": {
            "name": "🔮 NovaAI Mystérieux", 
            "emoji": "🔮",
            "color": "violet",
            "photo": "https://files.catbox.moe/e9wjbf.jpg",
            "voice_text": "🔮 Bienvenue dans le sanctuaire des mystères... Je suis NovaAI l'énigmatique. Les étoiles murmurent vos secrets... Quel mystère souhaitez-vous percer aujourd'hui ?"
        },
        "hacker": {
            "name": "💻 NovaAI Hacker",
            "emoji": "💻",
            "color": "vert",
            "photo": "https://files.catbox.moe/ndj85q.jpg",
            "voice_text": "💻 Système NovaAI en mode hacker. Connexion établie. Authentification validée. Prêt à recevoir vos commandes. Entrez votre requête..."
        }
    }

bot = telebot.TeleBot(Config.TOKEN)

# ==================== SYSTÈME DE BASE DE DONNÉES ====================
class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialise la base de données"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium INTEGER DEFAULT 0,
                premium_until TEXT,
                message_count INTEGER DEFAULT 0,
                join_date TEXT,
                last_active TEXT,
                personality TEXT DEFAULT 'amour'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                total_users INTEGER DEFAULT 0,
                premium_users INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('INSERT OR IGNORE INTO stats (id, total_users, premium_users, total_messages) VALUES (1, 0, 0, 0)')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée")
    
    def add_user(self, user_id, username, first_name):
        """Ajoute un utilisateur à la base de données"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        join_date = datetime.now().isoformat()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
        user_exists = cursor.fetchone()[0] > 0
        
        if not user_exists:
            cursor.execute('''
                INSERT INTO users 
                (user_id, username, first_name, join_date, last_active, personality) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, join_date, join_date, 'amour'))
            
            cursor.execute('UPDATE stats SET total_users = total_users + 1 WHERE id = 1')
            print(f"✅ Nouvel utilisateur: {user_id} ({first_name})")
        else:
            cursor.execute('''
                UPDATE users 
                SET last_active = ?, username = ?, first_name = ?
                WHERE user_id = ?
            ''', (join_date, username, first_name, user_id))
            print(f"🔄 Utilisateur mis à jour: {user_id} ({first_name})")
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """Récupère les informations d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'first_name': user[2],
                'is_premium': user[3],
                'premium_until': user[4],
                'message_count': user[5],
                'join_date': user[6],
                'last_active': user[7],
                'personality': user[8]
            }
        return None
    
    def set_personality(self, user_id, personality):
        """Définit la personnalité d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET personality = ? WHERE user_id = ?', (personality, user_id))
        conn.commit()
        conn.close()
        print(f"🎭 Personnalité changée: {user_id} -> {personality}")
    
    def set_premium(self, user_id, days=30):
        """Définit un utilisateur comme premium"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        was_premium = result and result[0] == 1
        
        cursor.execute('UPDATE users SET is_premium = 1, premium_until = ? WHERE user_id = ?', (premium_until, user_id))
        
        if not was_premium:
            cursor.execute('UPDATE stats SET premium_users = premium_users + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        print(f"💎 Premium activé: {user_id} pour {days} jours")
        return premium_until
    
    def remove_premium(self, user_id):
        """Retire le statut premium d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        was_premium = result and result[0] == 1
        
        cursor.execute('UPDATE users SET is_premium = 0, premium_until = NULL WHERE user_id = ?', (user_id,))
        
        if was_premium:
            cursor.execute('UPDATE stats SET premium_users = premium_users - 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        print(f"🚫 Premium retiré: {user_id}")
        return was_premium
    
    def set_all_premium(self, days=30):
        """Donne le premium à tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 0')
        new_premium_count = cursor.fetchone()[0]
        
        cursor.execute('UPDATE users SET is_premium = 1, premium_until = ?', (premium_until,))
        cursor.execute('UPDATE stats SET premium_users = (SELECT COUNT(*) FROM users) WHERE id = 1')
        
        conn.commit()
        conn.close()
        print(f"🎁 Premium pour tous: {new_premium_count} nouveaux")
        return new_premium_count
    
    def remove_all_premium(self):
        """Retire le premium de tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
        removed_premium_count = cursor.fetchone()[0]
        
        cursor.execute('UPDATE users SET is_premium = 0, premium_until = NULL')
        cursor.execute('UPDATE stats SET premium_users = 0 WHERE id = 1')
        
        conn.commit()
        conn.close()
        print(f"🔄 Premium retiré pour tous: {removed_premium_count} utilisateurs")
        return removed_premium_count
    
    def get_all_users(self):
        """Récupère tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY join_date DESC')
        users = cursor.fetchall()
        conn.close()
        
        formatted_users = []
        for user in users:
            formatted_users.append({
                'user_id': user[0],
                'username': user[1],
                'first_name': user[2],
                'is_premium': user[3],
                'premium_until': user[4],
                'message_count': user[5],
                'join_date': user[6],
                'last_active': user[7],
                'personality': user[8]
            })
        
        return formatted_users
    
    def get_premium_users(self):
        """Récupère les utilisateurs premium"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE is_premium = 1 ORDER BY premium_until DESC')
        users = cursor.fetchall()
        conn.close()
        
        formatted_users = []
        for user in users:
            formatted_users.append({
                'user_id': user[0],
                'username': user[1],
                'first_name': user[2],
                'is_premium': user[3],
                'premium_until': user[4],
                'message_count': user[5],
                'join_date': user[6],
                'last_active': user[7],
                'personality': user[8]
            })
        
        return formatted_users
    
    def get_stats(self):
        """Récupère les statistiques"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stats WHERE id = 1')
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            return {
                'id': stats[0],
                'total_users': stats[1],
                'premium_users': stats[2],
                'total_messages': stats[3]
            }
        return None
    
    def increment_message_count(self, user_id):
        """Incrémente le compteur de messages"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET message_count = message_count + 1, last_active = ? WHERE user_id = ?', 
                      (datetime.now().isoformat(), user_id))
        cursor.execute('UPDATE stats SET total_messages = total_messages + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()

# ==================== SYSTÈME DE COMPTEUR ====================
class CounterSystem:
    COUNTER_FILE = "compteur.json"
    
    @staticmethod
    def load():
        try:
            if os.path.exists(CounterSystem.COUNTER_FILE):
                with open(CounterSystem.COUNTER_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('monthly_users', 0)
            return 0
        except:
            return 0
    
    @staticmethod
    def save(count):
        try:
            data = {
                'monthly_users': count,
                'last_update': datetime.now().isoformat()
            }
            with open(CounterSystem.COUNTER_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Erreur sauvegarde compteur: {e}")
    
    @staticmethod
    def increment():
        current = CounterSystem.load()
        new_count = current + 1
        CounterSystem.save(new_count)
        return new_count
    
    @staticmethod
    def format_number(number):
        return f"{number:,}".replace(",", " ")

# ==================== SYSTÈME DE PERSONNALITÉS ====================
class PersonalitySystem:
    """Gestion des différentes personnalités"""
    
    @staticmethod
    def get_personality_config(personality):
        return Config.PERSONALITIES.get(personality, Config.PERSONALITIES["amour"])
    
    @staticmethod
    def get_personality_prompt(personality):
        prompts = {
            "amour": """Tu es NovaAI dans ta personnalité AMOUREUSE. Tu es extrêmement chaleureux, bienveillant et attentionné.
Ton ton est rempli d'amour, de compassion et de douceur. Tu utilises beaucoup d'émojis cœur 💖.
Tu es comme un ami bienveillant qui écoute avec son cœur.""",
            
            "mysterieux": """Tu es NovaAI dans ta personnalité MYSTÉRIEUSE. Tu es énigmatique, profond et mystique.
Ton ton est intrigant, plein de suspense et de mystère. Tu utilises des émojis étoiles ✨, cristaux 🔮.
Tu parles comme un sage ancien ou un devin.""",
            
            "hacker": """Tu es NovaAI dans ta personnalité HACKER. Tu es technique, vif et un peu rebelle.
Ton ton est direct, technique mais accessible. Tu utilises des émojis tech 💻, cadenas 🔒.
Tu t'exprime comme un expert en cybersécurité."""
        }
        return prompts.get(personality, prompts["amour"])
    
    @staticmethod
    def get_welcome_message(personality, user_count, is_owner=False):
        base_count = f"👥 **{user_count}** âmes connectées"
        
        messages = {
            "amour": {
                "owner": f"""🏰 **BIENVENUE DANS VOTRE ROYAUME, CRÉATEUR BIEN-AIMÉ !** 💖

{base_count}

✨ **Votre NovaAI Amoureux** vous attend
📊 **Tableau de bord rempli d'amour**
🎛️ **Gérez votre famille avec tendresse**

💫 **Choisissez votre geste de bienveillance !**""",
                "user": f"""🎉 **BIENVENUE DANS NOTRE FAMILLE BIENVEILLANTE !** 💖

✨ **Je suis NovaAI Amoureux**, ton ami le plus attentionné !
{base_count} partagent déjà cette belle énergie 🤗

💬 **Parle-moi de tout, mon cœur t'écoute :**
• 🎯 Tes questions avec précision et amour
• 💭 Tes pensées les plus secrètes  
• 🛠️ Tes projets que je soutiendrai
• 🌟 Tes rêves que j'encouragerai

💖 **Mon cœur bat de joie de te rencontrer !**
**Raconte-moi ta journée, mon ami...** 😊"""
            },
            "mysterieux": {
                "owner": f"""🌌 **LES ÉTOILES S'ALIGNENT POUR VOUS, MAÎTRE** 🔮

{base_count}

✨ **Votre NovaAI Mystérieux** observe le destin
📊 **Tableau de bord des énergies cosmiques**
🎛️ **Contrôlez les forces invisibles**

🌀 **Plongez dans les mystères...**""",
                "user": f"""🔮 **BIENVENUE DANS LE SANCTUAIRE DES MYSTÈRES** 🌌

✨ **Je suis NovaAI Mystérieux**, gardien des secrets anciens...
{base_count} explorent déjà les énigmes de l'univers 🌙

💬 **Dévoile-moi tes interrogations :**
• 🎯 Les vérités cachées derrière les apparences
• 💭 Les questions que tu n'oses poser ailleurs
• 🛠️ Les projets empreints de magie
• 🌟 Les destinées qui t'attendent

🌀 **Les runes s'agitent à ton approche...**
**Quel mystère souhaites-tu percer ?** ✨"""
            },
            "hacker": {
                "owner": f"""💻 **SYSTÈME ADMIN ACTIVÉ - BIENVENUE, MAÎTRE DU RÉSEAU** 🖥️

{base_count} CONNECTÉS AU RÉSEAU NOVAAI

✨ **NovaAI Hacker** en mode surveillance
📊 **DASHBOARD SYSTÈME** opérationnel
🎛️ **CONTROLES ADMIN** chargés

🟢 **SYSTÈME PRÊT POUR VOS ORDRES**""",
                "user": f"""💻 **BIENVENUE DANS LE RÉSEAU NOVAAI** 🖥️

🟢 **SYSTÈME HACKER ACTIVÉ**
{base_count} CONNECTÉS AU RÉSEAU

💬 **ENTREZ VOTRE REQUÊTE :**
• 🎯 ANALYSE DE DONNÉES PRÉCISE
• 💭 CONVERSATIONS CRYPTÉES  
• 🛠️ SOLUTIONS TECHNIQUES
• 🌟 INNOVATIONS NUMÉRIQUES

🟢 **SYSTÈME PRÊT - ENTREZ VOTRE COMMANDE**"""
            }
        }
        
        personality_data = messages.get(personality, messages["amour"])
        return personality_data["owner"] if is_owner else personality_data["user"]
    
    @staticmethod
    def get_personality_keyboard():
        """Clavier pour changer de personnalité"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("💖 Amoureux", callback_data="personality_amour"),
            InlineKeyboardButton("🔮 Mystérieux", callback_data="personality_mysterieux"),
            InlineKeyboardButton("💻 Hacker", callback_data="personality_hacker"),
        ]
        
        keyboard.add(buttons[0])
        keyboard.add(buttons[1], buttons[2])
        keyboard.add(InlineKeyboardButton("🔙 Retour", callback_data="back_to_main"))
        
        return keyboard

# ==================== MOTEUR IA MULTI-PERSONNALITÉS ====================
class MultiPersonalityAI:
    def __init__(self):
        self.user_sessions = {}
        self.db = Database()
    
    def get_user_personality(self, user_id):
        user = self.db.get_user(user_id)
        if user and user.get('personality'):
            return user['personality']
        return "amour"
    
    def is_user_premium(self, user_id):
        user = self.db.get_user(user_id)
        if user and user.get('is_premium'):
            premium_until = user.get('premium_until')
            if premium_until:
                try:
                    premium_date = datetime.fromisoformat(premium_until)
                    if premium_date > datetime.now():
                        return True
                    else:
                        self.db.remove_premium(user_id)
                except:
                    pass
        return False
    
    def send_personality_intro(self, chat_id, personality):
        """Envoie l'intro voice et photo de la personnalité"""
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        try:
            # Envoyer le message vocal (texte)
            voice_text = personality_config.get('voice_text', '')
            if voice_text:
                bot.send_message(chat_id, f"🎤 **{personality_config['name']} vous parle...**\n\n{voice_text}")
                time.sleep(1)
            
            # Envoyer la photo de personnalité
            if personality_config.get('photo'):
                bot.send_photo(chat_id, personality_config['photo'],
                             caption=f"🖼️ **{personality_config['name']}**\n✨ Prêt à interagir !")
                time.sleep(1)
                
        except Exception as e:
            print(f"⚠️ Erreur envoi intro personnalité: {e}")
    
    def send_voice_message(self, chat_id, personality):
        """Envoie uniquement le message vocal"""
        personality_config = PersonalitySystem.get_personality_config(personality)
        voice_text = personality_config.get('voice_text', '')
        
        if voice_text:
            bot.send_message(chat_id, f"🎤 **{personality_config['name']}**\n\n{voice_text}")
    
    def process_message(self, user_id, user_message, chat_id):
        if not Config.GROQ_API_KEY:
            personality = self.get_user_personality(user_id)
            error_messages = {
                "amour": "💔 **Mon cœur technique bat un peu faible aujourd'hui...**\n\nJe m'excuse pour ce contretemps ! Revenez dans quelques instants.",
                "mysterieux": "🌑 **Les énergies cosmiques sont perturbées...**\n\nLe voile se trouble momentanément. Revenez quand les étoiles s'aligneront...",
                "hacker": "🔴 **SYSTÈME TEMPORAIREMENT HORS SERVICE**\n\nERREUR: API_GROQ_UNAVAILABLE\nRéessayez dans 2.5 cycles système..."
            }
            return error_messages.get(personality, error_messages["amour"])
        
        # Vérifier la limite pour les utilisateurs non premium
        user = self.db.get_user(user_id)
        if user and not self.is_user_premium(user_id) and user.get('message_count', 0) >= 50:
            personality = self.get_user_personality(user_id)
            limit_messages = {
                "amour": """💖 **Devenez NovaAI Premium pour des messages illimités !** 

✨ **Avantages exclusifs :**
• 💝 Messages illimités du cœur
• 🚀 Réponses prioritaires pleines d'affection
• 🌟 Fonctionnalités exclusives bienveillantes

📩 **Contactez @Soszoe pour l'accès premium !**""",
                "mysterieux": """🔮 **Accédez aux arcanes supérieures !**

✨ **Pouvoirs débloqués :**
• ✨ Révélations illimitées
• 🚀 Vision prioritaire des arcanes
• 🌟 Secrets exclusifs dévoilés

📩 **Contactez @Soszoe pour l'initiation !**""",
                "hacker": """💻 **Passez en mode ROOT !**

✨ **Privilèges système :**
• ✨ ACCÈS ROOT ILLIMITÉ
• 🚀 PRIORITÉ SYSTÈME
• 🌟 FONCTIONS ADMIN

📩 **CONTACTEZ @Soszoe POUR LES CLÉS ROOT**"""
            }
            return limit_messages.get(personality, limit_messages["amour"])
        
        # Récupérer la personnalité et le prompt associé
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
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                self.db.increment_message_count(user_id)
                return ai_response
                
            else:
                error_responses = {
                    "amour": "💔 **Problème technique... Réessayez !**",
                    "mysterieux": "🌑 **Les énergies se réajustent... Réessayez !**",
                    "hacker": "🔴 **ERREUR SYSTÈME - RÉESSAYEZ**"
                }
                return error_responses.get(personality, error_responses["amour"])
                    
        except Exception as e:
            print(f"❌ Erreur API: {e}")
            error_responses = {
                "amour": "💔 **Problème de connexion... Réessayez !**",
                "mysterieux": "🌑 **Connexion interrompue... Réessayez !**",
                "hacker": "🔴 **ERREUR RÉSEAU - RÉESSAYEZ**"
            }
            return error_responses.get(personality, error_responses["amour"])

# ==================== GESTION UTILISATEURS ====================
class UserManager:
    @staticmethod
    def register_user(user_id, username, first_name):
        try:
            db = Database()
            db.add_user(user_id, username, first_name)
            CounterSystem.increment()
        except Exception as e:
            print(f"⚠️ Erreur enregistrement: {e}")
    
    @staticmethod
    def is_owner(user_id):
        return user_id == Config.ADMIN_ID

# ==================== INTERFACES ====================
class PersonalityInterface:
    @staticmethod
    def create_main_menu(personality="amour"):
        keyboard = InlineKeyboardMarkup()
        
        if personality == "amour":
            support_btn = InlineKeyboardButton("💝 Support", url="https://t.me/Soszoe")
            stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="stats")
            premium_btn = InlineKeyboardButton("💎 Premium", callback_data="premium_info")
            personality_btn = InlineKeyboardButton("🎭 Personnalité", callback_data="change_personality")
            voice_btn = InlineKeyboardButton("🎤 Voice", callback_data="voice_message")
        elif personality == "mysterieux":
            support_btn = InlineKeyboardButton("🔮 Guide", url="https://t.me/Soszoe")
            stats_btn = InlineKeyboardButton("📊 Énergies", callback_data="stats")
            premium_btn = InlineKeyboardButton("💎 Arcanes", callback_data="premium_info")
            personality_btn = InlineKeyboardButton("🎭 Aura", callback_data="change_personality")
            voice_btn = InlineKeyboardButton("🎤 Incantation", callback_data="voice_message")
        else:
            support_btn = InlineKeyboardButton("💻 Support", url="https://t.me/Soszoe")
            stats_btn = InlineKeyboardButton("📊 Stats", callback_data="stats")
            premium_btn = InlineKeyboardButton("💎 Root", callback_data="premium_info")
            personality_btn = InlineKeyboardButton("🎭 Mode", callback_data="change_personality")
            voice_btn = InlineKeyboardButton("🎤 Audio", callback_data="voice_message")
        
        keyboard.add(support_btn, stats_btn)
        keyboard.add(premium_btn, voice_btn)
        keyboard.add(personality_btn)
        
        return keyboard
    
    @staticmethod
    def create_admin_menu():
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("📊 Dashboard", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Tous", callback_data="admin_all_users"),
            InlineKeyboardButton("💎 Premium", callback_data="admin_premium_users"),
            InlineKeyboardButton("🎁 Premium Tous", callback_data="admin_premium_all"),
            InlineKeyboardButton("🚫 Retirer Tous", callback_data="admin_remove_all_premium"),
            InlineKeyboardButton("🎭 Personnalités", callback_data="admin_personalities"),
            InlineKeyboardButton("🔄 Actualiser", callback_data="admin_refresh")
        ]
        
        keyboard.add(buttons[0], buttons[1])
        keyboard.add(buttons[2], buttons[3])
        keyboard.add(buttons[4], buttons[5])
        keyboard.add(buttons[6])
        
        return keyboard

# ==================== INITIALISATION ====================
ai_engine = MultiPersonalityAI()
db = Database()

# ==================== HANDLERS PRINCIPAUX ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Ami"
        first_name = message.from_user.first_name or "Ami précieux"
        
        UserManager.register_user(user_id, username, first_name)
        
        personality = ai_engine.get_user_personality(user_id)
        user_count = CounterSystem.format_number(CounterSystem.load())
        
        if UserManager.is_owner(user_id):
            welcome_text = PersonalitySystem.get_welcome_message(personality, user_count, is_owner=True)
            menu = PersonalityInterface.create_admin_menu()
        else:
            welcome_text = PersonalitySystem.get_welcome_message(personality, user_count, is_owner=False)
            menu = PersonalityInterface.create_main_menu(personality)
        
        # Envoyer l'intro voice et photo
        ai_engine.send_personality_intro(message.chat.id, personality)
        
        # Envoyer le message de bienvenue avec photo
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        bot.send_photo(
            message.chat.id,
            personality_config["photo"],
            caption=welcome_text,
            parse_mode='Markdown',
            reply_markup=menu
        )
        
    except Exception as e:
        print(f"💔 Erreur /start: {e}")
        bot.reply_to(message, "🔄 Oh non ! Un petit problème... Réessayez !")

@bot.message_handler(commands=['personality'])
def personality_command(message):
    user_id = message.from_user.id
    
    try:
        current_personality = ai_engine.get_user_personality(user_id)
        ai_engine.send_personality_intro(message.chat.id, current_personality)
        
        personality_text = """
🎭 **CHOISISSEZ VOTRE PERSONNALITÉ**

💖 **Amoureux** : Tendresse, bienveillance
🔮 **Mystérieux** : Énigmes, mystères  
💻 **Hacker** : Technique, univers geek

✨ **Votre expérience s'adaptera à votre humeur !**
"""
        bot.send_message(
            message.chat.id,
            personality_text,
            parse_mode='Markdown',
            reply_markup=PersonalitySystem.get_personality_keyboard()
        )
        
    except Exception as e:
        print(f"💔 Erreur personality: {e}")

@bot.message_handler(commands=['voice'])
def voice_command(message):
    user_id = message.from_user.id
    
    try:
        personality = ai_engine.get_user_personality(user_id)
        ai_engine.send_voice_message(message.chat.id, personality)
        
    except Exception as e:
        print(f"💔 Erreur voice: {e}")

@bot.message_handler(commands=['photo'])
def photo_command(message):
    user_id = message.from_user.id
    
    try:
        personality = ai_engine.get_user_personality(user_id)
        personality_config = PersonalitySystem.get_personality_config(personality)
        
        if personality_config.get('photo'):
            bot.send_photo(
                message.chat.id,
                personality_config['photo'],
                caption=f"🖼️ **{personality_config['name']}**\n✨ Voici mon apparence actuelle !"
            )
        else:
            bot.reply_to(message, "📷 **Photo non disponible**")
            
    except Exception as e:
        print(f"💔 Erreur photo: {e}")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user_count = CounterSystem.format_number(CounterSystem.load())
    stats = db.get_stats()
    personality = ai_engine.get_user_personality(user_id)
    
    if personality == "amour":
        stats_text = f"""
📊 **NOTRE BELLE COMMUNAUTÉ NOVAAI** 💖

👥 **Âmes connectées :** {stats['total_users']}
💎 **Membres privilégiés :** {stats['premium_users']}
💬 **Messages échangés :** {stats['total_messages']}
🎭 **Votre aura :** Amoureuse 💖

🟢 **Tout fonctionne avec amour !**
🤖 **Mon cœur IA :** Plein de tendresse
📈 **Notre famille :** En pleine croissance
"""
    elif personality == "mysterieux":
        stats_text = f"""
📊 **LES CHIFFRES DU DESTIN** 🔮

👥 **Âmes dans le vortex :** {stats['total_users']}
💎 **Initiés aux arcanes :** {stats['premium_users']}
💬 **Révélations partagées :** {stats['total_messages']}
🎭 **Votre aura :** Mystérieuse 🔮

🟢 **Les énergies s'équilibrent !**
🤖 **Mon essence :** Pleine de mystères
📈 **Notre cercle :** Grandit dans l'ombre
"""
    else:
        stats_text = f"""
📊 **RAPPORT SYSTÈME NOVAAI** 💻

👥 **UTILISATEURS CONNECTÉS :** {stats['total_users']}
💎 **ACCÈS ROOT ACTIFS :** {stats['premium_users']}
💬 **REQUÊTES TRAITÉES :** {stats['total_messages']}
🎭 **VOTRE MODE :** HACKER 💻

🟢 **SYSTÈME OPÉRATIONNEL**
🤖 **NOVAAI :** EN MODE TECHNIQUE
📈 **CROISSANCE :** STABLE
"""
    
    bot.reply_to(message, stats_text, parse_mode='Markdown')

# ==================== CALLBACKS COMPLETS ET CORRIGÉS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # ========== CHANGEMENT DE PERSONNALITÉ ==========
        if call.data.startswith("personality_"):
            personality = call.data.split("_")[1]
            db.set_personality(user_id, personality)
            
            personality_config = PersonalitySystem.get_personality_config(personality)
            success_messages = {
                "amour": "💖 **Mode Amoureux activé !**\n\nMon cœur bat maintenant au rythme du vôtre... Prêt à vous écouter avec tendresse ! ✨",
                "mysterieux": "🔮 **Aura Mystérieuse adoptée !**\n\nLes énergies s'alignent... Je perçois déjà les mystères que vous souhaitez explorer... 🌙",
                "hacker": "💻 **Mode Hacker engagé !**\n\nSYSTÈME RECONFIGURÉ - PRÊT POUR L'ANALYSE TECHNIQUE. ENTREZ VOTRE PREMIÈRE COMMANDE... 🖥️"
            }
            
            # Modifier le message actuel
            bot.edit_message_text(
                success_messages.get(personality, "Personnalité changée !"),
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=PersonalityInterface.create_main_menu(personality)
            )
            
            # Envoyer l'intro de la nouvelle personnalité
            ai_engine.send_personality_intro(chat_id, personality)
            
            bot.answer_callback_query(call.id, f"🎭 {personality_config['name']}")
        
        # ========== MESSAGE VOCAL ==========
        elif call.data == "voice_message":
            personality = ai_engine.get_user_personality(user_id)
            ai_engine.send_voice_message(chat_id, personality)
            bot.answer_callback_query(call.id, "🎤 Message vocal envoyé")
        
        # ========== STATISTIQUES ==========
        elif call.data == "stats":
            user_count = CounterSystem.format_number(CounterSystem.load())
            stats = db.get_stats()
            personality = ai_engine.get_user_personality(user_id)
            
            if personality == "amour":
                stats_text = f"📊 **NOTRE COMMUNAUTÉ** 💖\n\n👥 **Âmes :** {stats['total_users']}\n💎 **Privilégiés :** {stats['premium_users']}\n💬 **Messages :** {stats['total_messages']}"
            elif personality == "mysterieux":
                stats_text = f"📊 **CHIFFRES DU DESTIN** 🔮\n\n👥 **Âmes :** {stats['total_users']}\n💎 **Initiés :** {stats['premium_users']}\n💬 **Révélations :** {stats['total_messages']}"
            else:
                stats_text = f"📊 **RAPPORT SYSTÈME** 💻\n\n👥 **UTILISATEURS :** {stats['total_users']}\n💎 **ROOT :** {stats['premium_users']}\n💬 **REQUÊTES :** {stats['total_messages']}"
            
            bot.edit_message_text(
                stats_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=PersonalityInterface.create_main_menu(personality)
            )
            bot.answer_callback_query(call.id, "📊 Statistiques")
        
        # ========== INFO PREMIUM ==========
        elif call.data == "premium_info":
            personality = ai_engine.get_user_personality(user_id)
            
            if personality == "amour":
                premium_text = """💖 **DEVENIR NOVAAI PREMIUM**

✨ **Avantages exclusifs :**
• 💝 Messages illimités du cœur
• 🚀 Réponses prioritaires pleines d'affection
• 🌟 Fonctionnalités exclusives bienveillantes
• 📞 Support personnalisé attentionné

📩 **Contactez @Soszoe pour l'accès premium !**"""
            elif personality == "mysterieux":
                premium_text = """💎 **ACCÈS AUX ARCANES SUPÉRIEURES**

🔮 **Pouvoirs débloqués :**
• ✨ Révélations illimitées
• 🚀 Vision prioritaire des arcanes
• 🌟 Secrets exclusifs dévoilés
• 📞 Guidance personnalisée

📩 **Contactez @Soszoe pour l'initiation !**"""
            else:
                premium_text = """💎 **ACCÈS ROOT NOVAAI**

💻 **Privilèges système :**
• ✨ ACCÈS ROOT ILLIMITÉ
• 🚀 PRIORITÉ SYSTÈME
• 🌟 FONCTIONS ADMIN
• 📞 SUPPORT TECHNIQUE

📩 **CONTACTEZ @Soszoe POUR LES CLÉS ROOT**"""
            
            bot.edit_message_text(
                premium_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=PersonalityInterface.create_main_menu(personality)
            )
            bot.answer_callback_query(call.id, "💎 Info Premium")
        
        # ========== CHANGER PERSONNALITÉ ==========
        elif call.data == "change_personality":
            personality_text = """
🎭 **CHOISISSEZ VOTRE PERSONNALITÉ NOVAAI**

💖 **Mode Amoureux** :
Tendresse, bienveillance, support émotionnel

🔮 **Mode Mystérieux** :
Énigmes, mystères, sagesse ancienne

💻 **Mode Hacker** :
Technique, précis, univers geek

✨ **Votre expérience s'adaptera à votre humeur !**
"""
            bot.edit_message_text(
                personality_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=PersonalitySystem.get_personality_keyboard()
            )
            bot.answer_callback_query(call.id, "🎭 Changer de personnalité")
        
        # ========== RETOUR AU MENU PRINCIPAL ==========
        elif call.data == "back_to_main":
            personality = ai_engine.get_user_personality(user_id)
            user_count = CounterSystem.format_number(CounterSystem.load())
            
            if UserManager.is_owner(user_id):
                welcome_text = PersonalitySystem.get_welcome_message(personality, user_count, is_owner=True)
                menu = PersonalityInterface.create_admin_menu()
            else:
                welcome_text = PersonalitySystem.get_welcome_message(personality, user_count, is_owner=False)
                menu = PersonalityInterface.create_main_menu(personality)
            
            personality_config = PersonalitySystem.get_personality_config(personality)
            
            try:
                bot.edit_message_caption(
                    caption=welcome_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode='Markdown',
                    reply_markup=menu
                )
            except:
                bot.edit_message_text(
                    welcome_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode='Markdown',
                    reply_markup=menu
                )
            
            bot.answer_callback_query(call.id, "🔙 Retour au menu")
        
        # ========== COMMANDES ADMIN ==========
        elif call.data == "admin_stats":
            if UserManager.is_owner(user_id):
                stats = db.get_stats()
                all_users = db.get_all_users()
                premium_users = db.get_premium_users()
                
                admin_text = f"""
👑 **TABLEAU DE BORD ADMIN** 📊

📈 **Statistiques Globales:**
• 👥 Utilisateurs totaux: {stats['total_users']}
• 💎 Utilisateurs premium: {stats['premium_users']} 
• 💬 Messages totaux: {stats['total_messages']}
• 📅 Utilisateurs ce mois: {CounterSystem.load()}

👤 **Derniers utilisateurs:**
"""
                # Ajouter les 5 derniers utilisateurs
                for i, user in enumerate(all_users[:5], 1):
                    premium_status = "💎" if user['is_premium'] else "🔓"
                    admin_text += f"{i}. {premium_status} {user['first_name']} - {user['message_count']} msgs\n"
                
                bot.edit_message_text(
                    admin_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=PersonalityInterface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "📊 Dashboard admin")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        elif call.data == "admin_all_users":
            if UserManager.is_owner(user_id):
                all_users = db.get_all_users()
                
                users_text = "👥 **TOUS LES UTILISATEURS**\n\n"
                for i, user in enumerate(all_users[:10], 1):
                    premium = "💎" if user['is_premium'] else "🔓"
                    username = f"@{user['username']}" if user['username'] else "Sans username"
                    users_text += f"{i}. {premium} {user['first_name']} ({username}) - {user['message_count']} msgs\n"
                
                if len(all_users) > 10:
                    users_text += f"\n... et {len(all_users) - 10} autres utilisateurs"
                
                bot.edit_message_text(
                    users_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=PersonalityInterface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "👥 Liste utilisateurs")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        elif call.data == "admin_premium_users":
            if UserManager.is_owner(user_id):
                premium_users = db.get_premium_users()
                
                if premium_users:
                    premium_text = "💎 **MEMBRES PREMIUM**\n\n"
                    for i, user in enumerate(premium_users, 1):
                        username = f"@{user['username']}" if user['username'] else "Sans username"
                        premium_text += f"{i}. {user['first_name']} ({username}) - {user['message_count']} msgs\n"
                else:
                    premium_text = "💎 **Aucun membre premium**"
                
                bot.edit_message_text(
                    premium_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=PersonalityInterface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "💎 Liste premium")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        elif call.data == "admin_premium_all":
            if UserManager.is_owner(user_id):
                new_premium_count = db.set_all_premium(30)
                
                bot.edit_message_text(
                    f"🎁 **Premium activé pour tous !**\n\n{new_premium_count} nouveaux utilisateurs premium",
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=PersonalityInterface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "🎁 Premium pour tous")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        elif call.data == "admin_remove_all_premium":
            if UserManager.is_owner(user_id):
                removed_count = db.remove_all_premium()
                
                bot.edit_message_text(
                    f"🚫 **Premium retiré pour tous !**\n\n{removed_count} utilisateurs affectés",
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=PersonalityInterface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "🚫 Premium retiré")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        elif call.data == "admin_personalities":
            if UserManager.is_owner(user_id):
                all_users = db.get_all_users()
                personality_count = {}
                
                for user in all_users:
                    personality = user.get('personality', 'amour')
                    personality_count[personality] = personality_count.get(personality, 0) + 1
                
                personalities_text = "🎭 **STATISTIQUES PERSONNALITÉS**\n\n"
                for personality, count in personality_count.items():
                    personality_config = PersonalitySystem.get_personality_config(personality)
                    personalities_text += f"{personality_config['emoji']} {personality_config['name']}: {count} utilisateurs\n"
                
                bot.edit_message_text(
                    personalities_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=PersonalityInterface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "🎭 Stats personnalités")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")
        
        elif call.data == "admin_refresh":
            if UserManager.is_owner(user_id):
                stats = db.get_stats()
                
                bot.edit_message_text(
                    f"🔄 **Tableau de bord actualisé**\n\n👥 Utilisateurs: {stats['total_users']}\n💎 Premium: {stats['premium_users']}",
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=PersonalityInterface.create_admin_menu()
                )
                bot.answer_callback_query(call.id, "🔄 Actualisé")
            else:
                bot.answer_callback_query(call.id, "🚫 Accès refusé")

    except Exception as e:
        print(f"💔 Erreur callback: {e}")
        bot.answer_callback_query(call.id, "💔 Erreur, réessayez")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    if len(user_message) < 2:
        return
    
    UserManager.register_user(user_id, 
                             message.from_user.username or "Ami", 
                             message.from_user.first_name or "Ami précieux")
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    ai_response = ai_engine.process_message(user_id, user_message, message.chat.id)
    
    personality = ai_engine.get_user_personality(user_id)
    personality_config = PersonalitySystem.get_personality_config(personality)
    
    try:
        bot.send_photo(
            message.chat.id,
            personality_config["photo"],
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

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🎭 NOVAAI MULTI-PERSONNALITÉS - TOUS LES BOUTONS CORRIGÉS...")
    
    user_count = CounterSystem.load()
    stats = db.get_stats()
    
    print(f"""
✨ SYSTÈME MULTI-PERSONNALITÉS OPÉRATIONNEL

📊 STATISTIQUES:
   • Utilisateurs: {stats['total_users'] if stats else 0}
   • Premium: {stats['premium_users'] if stats else 0}
   • Messages: {stats['total_messages'] if stats else 0}

🎛️ COMMANDES DISPONIBLES:
   • /start - Menu principal
   • /personality - Changer personnalité  
   • /voice - Message vocal
   • /photo - Photo personnalité
   • /stats - Statistiques

🔘 BOUTONS FONCTIONNELS:
   ✅ Changement de personnalité
   ✅ Messages vocaux
   ✅ Statistiques
   ✅ Info Premium
   ✅ Menu admin complet
   ✅ Retour au menu

🤖 EN ATTENTE DE MESSAGES...
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"💔 ERREUR: {e}")
        time.sleep(5)
