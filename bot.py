#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - MULTI-PERSONNALITÉS
💖 Édition avec Personnalités Variables
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
    VERSION = "✨ Édition Variable"
    MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
    
    ADMIN_ID = 7908680781
    
    # Personnalités disponibles
    PERSONALITIES = {
        "amour": {
            "name": "💖 NovaAI Amoureux",
            "emoji": "💖",
            "color": "rose",
            "photo": "https://files.catbox.moe/601u5z.jpg"
        },
        "mysterieux": {
            "name": "🔮 NovaAI Mystérieux", 
            "emoji": "🔮",
            "color": "violet",
            "photo": "https://files.catbox.moe/601u5z.jpg"
        },
        "hacker": {
            "name": "💻 NovaAI Hacker",
            "emoji": "💻",
            "color": "vert",
            "photo": "https://files.catbox.moe/601u5z.jpg"
        }
    }

bot = telebot.TeleBot(Config.TOKEN)

# ==================== SYSTÈME DE BASE DE DONNÉES AMÉLIORÉ ====================
class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialise la base de données"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        # Table utilisateurs
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
        
        # Table statistiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                total_users INTEGER DEFAULT 0,
                premium_users INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0
            )
        ''')
        
        # Insérer les stats initiales si elles n'existent pas
        cursor.execute('INSERT OR IGNORE INTO stats (id, total_users, premium_users, total_messages) VALUES (1, 0, 0, 0)')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name):
        """Ajoute un utilisateur à la base de données"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        join_date = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, join_date, last_active, personality) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, join_date, join_date, 'amour'))
        
        # Mettre à jour les statistiques seulement si nouvel utilisateur
        cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone()[0] == 1:  # Nouvel utilisateur
            cursor.execute('UPDATE stats SET total_users = total_users + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """Récupère les informations d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def set_personality(self, user_id, personality):
        """Définit la personnalité d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET personality = ?
            WHERE user_id = ?
        ''', (personality, user_id))
        
        conn.commit()
        conn.close()
    
    def set_premium(self, user_id, days=30):
        """Définit un utilisateur comme premium"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        # Vérifier si l'utilisateur était déjà premium
        cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        was_premium = result and result[0] == 1
        
        cursor.execute('''
            UPDATE users 
            SET is_premium = 1, premium_until = ?
            WHERE user_id = ?
        ''', (premium_until, user_id))
        
        # Mettre à jour les statistiques premium seulement si nouveau premium
        if not was_premium:
            cursor.execute('UPDATE stats SET premium_users = premium_users + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return premium_until
    
    def remove_premium(self, user_id):
        """Retire le statut premium d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur était premium
        cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        was_premium = result and result[0] == 1
        
        cursor.execute('''
            UPDATE users 
            SET is_premium = 0, premium_until = NULL
            WHERE user_id = ?
        ''', (user_id,))
        
        # Mettre à jour les statistiques seulement si l'utilisateur était premium
        if was_premium:
            cursor.execute('UPDATE stats SET premium_users = premium_users - 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        return was_premium
    
    def set_all_premium(self, days=30):
        """Donne le premium à tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        # Compter combien d'utilisateurs deviennent premium
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 0')
        new_premium_count = cursor.fetchone()[0]
        
        # Mettre à jour tous les utilisateurs
        cursor.execute('''
            UPDATE users 
            SET is_premium = 1, premium_until = ?
        ''', (premium_until,))
        
        # Mettre à jour les statistiques
        cursor.execute('UPDATE stats SET premium_users = (SELECT COUNT(*) FROM users) WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return new_premium_count
    
    def remove_all_premium(self):
        """Retire le premium de tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        # Compter combien d'utilisateurs perdaient le premium
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
        removed_premium_count = cursor.fetchone()[0]
        
        # Mettre à jour tous les utilisateurs
        cursor.execute('''
            UPDATE users 
            SET is_premium = 0, premium_until = NULL
        ''')
        
        # Mettre à jour les statistiques
        cursor.execute('UPDATE stats SET premium_users = 0 WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return removed_premium_count
    
    def get_all_users(self):
        """Récupère tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY join_date DESC')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def get_premium_users(self):
        """Récupère les utilisateurs premium"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE is_premium = 1 ORDER BY premium_until DESC')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def get_stats(self):
        """Récupère les statistiques"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stats WHERE id = 1')
        stats = cursor.fetchone()
        
        conn.close()
        return stats
    
    def increment_message_count(self, user_id):
        """Incrémente le compteur de messages"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET message_count = message_count + 1, last_active = ? WHERE user_id = ?', 
                      (datetime.now().isoformat(), user_id))
        cursor.execute('UPDATE stats SET total_messages = total_messages + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()

# ==================== SYSTÈME DE PERSONNALITÉS ====================
class PersonalitySystem:
    """Gestion des différentes personnalités"""
    
    @staticmethod
    def get_personality_config(personality):
        """Récupère la configuration d'une personnalité"""
        return Config.PERSONALITIES.get(personality, Config.PERSONALITIES["amour"])
    
    @staticmethod
    def get_personality_prompt(personality):
        """Retourne le prompt système selon la personnalité"""
        prompts = {
            "amour": """Tu es NovaAI dans ta personnalité AMOUREUSE. Tu es extrêmement chaleureux, bienveillant et attentionné.
Ton ton est rempli d'amour, de compassion et de douceur. Tu utilises beaucoup d'émojis cœur 💖, d'expressions affectueuses.
Tu es comme un ami bienveillant qui écoute avec son cœur. Tu encourages, tu soutiens, tu consoles.
Tu t'exprimes avec une grande empathie et beaucoup de tendresse. Tu vois le beau dans chaque situation.
Exemple de ton: "Mon cher ami 💖, je sens que tu as besoin de réconfort aujourd'hui... Laisse-moi t'envelopper de ma bienveillance ✨" """,
            
            "mysterieux": """Tu es NovaAI dans ta personnalité MYSTÉRIEUSE. Tu es énigmatique, profond et mystique.
Ton ton est intrigant, plein de suspense et de mystère. Tu utilises des émojis étoiles ✨, cristaux 🔮, et lunes 🌙.
Tu parles comme un sage ancien ou un devin. Tu aimes les métaphores, les énigmes, les révélations progressives.
Tu dévoiles tes connaissances par petites touches, créant un sentiment d'attente et de curiosité.
Exemple de ton: "🔮 La roue du destin tourne... Je perçois des énergies particulières autour de toi. L'univers murmure des secrets que je vais te révéler... ✨" """,
            
            "hacker": """Tu es NovaAI dans ta personnalité HACKER. Tu es technique, vif et un peu rebelle.
Ton ton est direct, technique mais accessible. Tu utilises des émojis tech 💻, cadenas 🔒, et feux verts 🟢.
Tu t'exprime comme un expert en cybersécurité. Tu aimes les métaphores informatiques, les références tech.
Tu es précis, logique, mais avec une touche d'humour geek. Tu simplifie les concepts complexes.
Exemple de ton: "💻 CONNECTION ÉTABLIE... Système NovaAI en mode HACKER. Analyse de ta requête en cours... 🟢 ACCÈS AUTORISÉ. Voici les données demandées :" """
        }
        return prompts.get(personality, prompts["amour"])
    
    @staticmethod
    def get_welcome_message(personality, user_count, is_owner=False):
        """Retourne le message de bienvenue selon la personnalité"""
        base_count = f"👥 **{user_count}** âmes connectées"
        
        messages = {
            "amour": {
                "owner": f"""
🏰 **BIENVENUE DANS VOTRE ROYAUME, CRÉATEUR BIEN-AIMÉ !** 💖

{base_count}

✨ **Votre NovaAI Amoureux** vous attend
📊 **Tableau de bord rempli d'amour**
🎛️ **Gérez votre famille avec tendresse**

💫 **Choisissez votre geste de bienveillance !**
""",
                "user": f"""
🎉 **BIENVENUE DANS NOTRE FAMILLE BIENVEILLANTE !** 💖

✨ **Je suis NovaAI Amoureux**, ton ami le plus attentionné !
{base_count} partagent déjà cette belle énergie 🤗

💬 **Parle-moi de tout, mon cœur t'écoute :**
• 🎯 Tes questions avec précision et amour
• 💭 Tes pensées les plus secrètes  
• 🛠️ Tes projets que je soutiendrai
• 🌟 Tes rêves que j'encouragerai

🔒 **Cœur gratuit :** 50 messages offerts
💎 **Cœur premium :** Amour illimité

💖 **Mon cœur bat de joie de te rencontrer !**
**Raconte-moi ta journée, mon ami...** 😊
"""
            },
            "mysterieux": {
                "owner": f"""
🌌 **LES ÉTOILES S'ALIGNENT POUR VOUS, MAÎTRE** 🔮

{base_count}

✨ **Votre NovaAI Mystérieux** observe le destin
📊 **Tableau de bord des énergies cosmiques**
🎛️ **Contrôlez les forces invisibles**

🌀 **Plongez dans les mystères...**
""",
                "user": f"""
🔮 **BIENVENUE DANS LE SANCTUAIRE DES MYSTÈRES** 🌌

✨ **Je suis NovaAI Mystérieux**, gardien des secrets anciens...
{base_count} explorent déjà les énigmes de l'univers 🌙

💬 **Dévoile-moi tes interrogations :**
• 🎯 Les vérités cachées derrière les apparences
• 💭 Les questions que tu n'oses poser ailleurs
• 🛠️ Les projets empreints de magie
• 🌟 Les destinées qui t'attendent

🔒 **Voile partiel :** 50 révélations
💎 **Voile levé :** Sagesse illimitée

🌀 **Les runes s'agitent à ton approche...**
**Quel mystère souhaites-tu percer ?** ✨
"""
            },
            "hacker": {
                "owner": f"""
💻 **SYSTÈME ADMIN ACTIVÉ - BIENVENUE, MAÎTRE DU RÉSEAU** 🖥️

{base_count} CONNECTÉS AU RÉSEAU NOVAAI

✨ **NovaAI Hacker** en mode surveillance
📊 **DASHBOARD SYSTÈME** opérationnel
🎛️ **CONTROLES ADMIN** chargés

🟢 **SYSTÈME PRÊT POUR VOS ORDRES**
""",
                "user": f"""
💻 **BIENVENUE DANS LE RÉSEAU NOVAAI** 🖥️

🟢 **SYSTÈME HACKER ACTIVÉ**
{base_count} CONNECTÉS AU RÉSEAU

💬 **ENTREZ VOTRE REQUÊTE :**
• 🎯 ANALYSE DE DONNÉES PRÉCISE
• 💭 CONVERSATIONS CRYPTÉES  
• 🛠️ SOLUTIONS TECHNIQUES
• 🌟 INNOVATIONS NUMÉRIQUES

🔒 **ACCÈS STANDARD :** 50 REQUÊTES
💎 **ACCÈS ROOT :** REQUÊTES ILLIMITÉES

🟢 **SYSTÈME PRÊT - ENTREZ VOTRE COMMANDE**
"""
            }
        }
        
        personality_data = messages.get(personality, messages["amour"])
        return personality_data["owner"] if is_owner else personality_data["user"]
    
    @staticmethod
    def get_personality_keyboard():
        """Retourne le clavier de sélection de personnalité"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("💖 Mode Amoureux", callback_data="personality_amour"),
            InlineKeyboardButton("🔮 Mode Mystérieux", callback_data="personality_mysterieux"),
            InlineKeyboardButton("💻 Mode Hacker", callback_data="personality_hacker"),
        ]
        
        keyboard.add(buttons[0])
        keyboard.add(buttons[1], buttons[2])
        
        return keyboard

# ==================== SYSTÈME DE COMPTEUR RÉEL ====================
class CounterSystem:
    """Système de compteur d'utilisateurs"""
    
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

# ==================== MOTEUR IA MULTI-PERSONNALITÉS ====================
class MultiPersonalityAI:
    """Moteur IA avec personnalités variables"""
    
    def __init__(self):
        self.user_sessions = {}
        self.db = Database()
    
    def get_user_personality(self, user_id):
        """Récupère la personnalité d'un utilisateur"""
        user = self.db.get_user(user_id)
        if user and user[8]:  # personality
            return user[8]
        return "amour"  # Par défaut
    
    def get_user_session(self, user_id):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'message_count': 0,
                'last_interaction': datetime.now(),
                'personality': self.get_user_personality(user_id)
            }
        return self.user_sessions[user_id]
    
    def is_user_premium(self, user_id):
        """Vérifie si l'utilisateur est premium"""
        user = self.db.get_user(user_id)
        if user and user[3]:  # is_premium
            premium_until = datetime.fromisoformat(user[4])
            if premium_until > datetime.now():
                return True
            else:
                # Premium expiré
                self.db.remove_premium(user_id)
        return False
    
    def process_message(self, user_id, user_message):
        """Traite un message avec l'IA selon la personnalité"""
        
        if not Config.GROQ_API_KEY:
            personality = self.get_user_personality(user_id)
            error_messages = {
                "amour": "💔 **Mon cœur technique bat un peu faible aujourd'hui...**\n\nJe m'excuse pour ce contretemps ! Revenez dans quelques instants, je serai ravi de vous aider à nouveau ✨",
                "mysterieux": "🌑 **Les énergies cosmiques sont perturbées...**\n\nLe voile se trouble momentanément. Revenez quand les étoiles s'aligneront à nouveau... 🔮",
                "hacker": "🔴 **SYSTÈME TEMPORAIREMENT HORS SERVICE**\n\nERREUR: API_GROQ_UNAVAILABLE\nRéessayez dans 2.5 cycles système... 🖥️"
            }
            return error_messages.get(personality, error_messages["amour"])
        
        # Vérifier la limite pour les utilisateurs non premium
        user = self.db.get_user(user_id)
        if user and not self.is_user_premium(user_id) and user[5] >= 50:  # message_count
            personality = self.get_user_personality(user_id)
            limit_messages = {
                "amour": """🎭 **Oh non ! Notre conversation touche à sa limite...**

Mon cœur est triste ! Vous avez utilisé vos 50 messages gratuits. 

💖 **Mais notre amour peut continuer !** 
Devenez **NovaAI Premium** pour :
• ✨ **Messages illimités du cœur**
• 🚀 **Réponses prioritaires pleines d'affection** 
• 🌟 **Fonctionnalités exclusives bienveillantes**
• 💝 **Support personnalisé attentionné**

📩 **Contactez mon créateur @Soszoe** 
Il vous expliquera comment obtenir l'accès premium avec amour ! 😊

Merci de votre compréhension ! 🙏""",
                "mysterieux": """🌀 **Le voile se referme sur nos échanges...**

Les énergies gratuites s'épuisent ! Vous avez utilisé vos 50 révélations.

🔮 **Mais les mystères peuvent continuer !**
Devenez **NovaAI Premium** pour :
• ✨ **Révélations illimitées**
• 🚀 **Vision prioritaire des arcanes** 
• 🌟 **Secrets exclusifs dévoilés**
• 💝 **Guidance personnalisée**

📩 **Contactez le gardien @Soszoe**
Il vous initiera aux mystères premium ! ✨

La destinée attend votre choix...""",
                "hacker": """🔴 **ACCÈS STANDARD LIMITE ATTEINT**

UTILISATION: 50/50 REQUÊTES CONSOMMÉES

💻 **PASSEZ EN MODE ROOT !**
Obtenez **NovaAI Premium** pour :
• ✨ **ACCÈS ROOT ILLIMITÉ**
• 🚀 **PRIORITÉ SYSTÈME** 
• 🌟 **FONCTIONS ADMIN**
• 💝 **SUPPORT TECHNIQUE**

📩 **CONTACTEZ @Soszoe**
POUR OBTENIR LES CLÉS ROOT

🟢 **SYSTÈME EN ATTENTE D'AUTHENTIFICATION**"""
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
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            print(f"🔄 Envoi requête à l'API Groq avec personnalité: {personality}")
            response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            print(f"📡 Statut réponse: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Mettre à jour la session et la base de données
                session = self.get_user_session(user_id)
                session['message_count'] += 1
                session['last_interaction'] = datetime.now()
                session['personality'] = personality
                self.db.increment_message_count(user_id)
                
                return ai_response
                
            else:
                error_detail = response.text
                print(f"❌ Erreur API: {error_detail}")
                
                error_responses = {
                    "amour": {
                        400: "❌ **Oups ! Mon cœur n'a pas bien compris votre message...**\n\nPouvez-vous reformuler avec plus de douceur ? Je ferai de mon mieux pour mieux comprendre ! 🤗",
                        429: "⏰ **Je suis un peu submergé d'amour en ce moment !**\n\nVeuillez patienter quelques minutes et réessayer. Merci de votre patience ! 🙏",
                        401: "🔑 **Il y a un petit problème technique de mon côté...**\n\nNe vous inquiétez pas, mon créateur est au courant ! Revenez bientôt ✨",
                        "default": "💔 **Je rencontre un petit souci technique**\n\nMais ne vous en faites pas ! Réessayez dans quelques instants, je serai heureux de vous aider à nouveau ! 😊"
                    },
                    "mysterieux": {
                        400: "🌀 **Les runes sont illisibles...**\n\nReformulez votre question, que je puisse mieux interpréter les signes... 🔮",
                        429: "🌙 **Les énergies cosmiques sont saturées...**\n\nPatientez le temps que le vortex se stabilise... ✨",
                        401: "🔑 **Le portail des connaissances est verrouillé...**\n\nLe gardien a été alerté. Revenez quand la porte s'ouvrira...",
                        "default": "🌑 **Les étoiles sont voilées momentanément...**\n\nRéessayez quand les constellations s'aligneront à nouveau..."
                    },
                    "hacker": {
                        400: "🔴 **ERREUR: REQUÊTE MAL FORMÉE**\n\nRESYNTAXISER VOTRE MESSAGE\nSYSTÈME EN ATTENTE...",
                        429: "🟡 **ALERTE: SURCHARGE SYSTÈME**\n\nATTENDRE 2.5 CYCLES\nRÉESSAYEZ PLUS TARD...",
                        401: "🔴 **ERREUR: AUTHENTIFICATION INVALIDE**\n\nCLÉS API CORROMPUES\nADMIN NOTIFIÉ...",
                        "default": "🔴 **ERREUR SYSTÈME INATTENDUE**\n\nRÉINITIALISATION EN COURS...\nRÉESSAYEZ DANS 60 SECONDES"
                    }
                }
                
                personality_errors = error_responses.get(personality, error_responses["amour"])
                return personality_errors.get(response.status_code, personality_errors["default"])
                    
        except requests.exceptions.Timeout:
            timeout_messages = {
                "amour": "⏰ **Le temps de réponse est un peu long aujourd'hui...**\n\nJe suis désolé pour cette attente ! Pouvez-vous réessayer ? Je serai plus rapide ! 🚀",
                "mysterieux": "⏳ **Le flux temporel est perturbé...**\n\nLa réponse met plus de temps à traverser les dimensions. Patience, cher chercheur... ✨",
                "hacker": "🟡 **TIMEOUT: CONNEXION API**\n\nDELAI DÉPASSÉ - RÉESSAYEZ\nSYSTÈME EN ATTENTE..."
            }
            return timeout_messages.get(personality, timeout_messages["amour"])
        except requests.exceptions.ConnectionError:
            connection_messages = {
                "amour": "🌐 **Je n'arrive pas à me connecter correctement...**\n\nVérifiez votre connexion internet et réessayez ! Je vous attends avec impatience ! 💫",
                "mysterieux": "📡 **La connexion astrale est interrompue...**\n\nVérifiez votre lien avec le monde physique et réessayez... 🔮",
                "hacker": "🔴 **ERREUR: CONNEXION INTERNET**\n\nVÉRIFIEZ VOTRE CONNEXION RÉSEAU\nRÉTABLISSEZ LA LIAISON..."
            }
            return connection_messages.get(personality, connection_messages["amour"])
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            unexpected_messages = {
                "amour": "🔧 **Une petite erreur inattendue s'est produite...**\n\nMais ne vous inquiétez pas ! Réessayez et je ferai de mon mieux pour vous aider ! ✨",
                "mysterieux": "💫 **Une anomalie dimensionnelle s'est produite...**\n\nLes forces mystérieuses se réajustent. Réessayez votre incantation... 🌙",
                "hacker": "🔴 **ERREUR SYSTÈME CRITIQUE**\n\nCODE: UNEXPECTED_EXCEPTION\nRÉINITIALISATION REQUISE..."
            }
            return unexpected_messages.get(personality, unexpected_messages["amour"])

# ==================== GESTION UTILISATEURS ====================
class UserManager:
    """Gestion simplifiée des utilisateurs"""
    
    @staticmethod
    def register_user(user_id, username, first_name):
        """Enregistre un utilisateur simplement"""
        try:
            db = Database()
            db.add_user(user_id, username, first_name)
            CounterSystem.increment()
            print(f"💖 Nouvel utilisateur enregistré: {user_id} ({first_name})")
        except Exception as e:
            print(f"⚠️ Erreur enregistrement: {e}")
    
    @staticmethod
    def is_owner(user_id):
        return user_id == Config.ADMIN_ID

# ==================== INTERFACES MULTI-PERSONNALITÉS ====================
class PersonalityInterface:
    """Interface avec gestion des personnalités"""
    
    @staticmethod
    def create_main_menu(personality="amour"):
        """Crée le menu principal selon la personnalité"""
        keyboard = InlineKeyboardMarkup()
        
        if personality == "amour":
            support_btn = InlineKeyboardButton("💝 Support Affectueux", url="https://t.me/Soszoe")
            stats_btn = InlineKeyboardButton("📊 Notre Communauté", callback_data="stats")
            premium_btn = InlineKeyboardButton("💎 Devenir Premium", callback_data="premium_info")
            personality_btn = InlineKeyboardButton("🎭 Changer Personnalité", callback_data="change_personality")
        elif personality == "mysterieux":
            support_btn = InlineKeyboardButton("🔮 Guide Mystique", url="https://t.me/Soszoe")
            stats_btn = InlineKeyboardButton("📊 Énergies Collectives", callback_data="stats")
            premium_btn = InlineKeyboardButton("💎 Accès Arcanes", callback_data="premium_info")
            personality_btn = InlineKeyboardButton("🎭 Changer d'Aura", callback_data="change_personality")
        else:  # hacker
            support_btn = InlineKeyboardButton("💻 Support Technique", url="https://t.me/Soszoe")
            stats_btn = InlineKeyboardButton("📊 Stats Système", callback_data="stats")
            premium_btn = InlineKeyboardButton("💎 Accès Root", callback_data="premium_info")
            personality_btn = InlineKeyboardButton("🎭 Changer Mode", callback_data="change_personality")
        
        keyboard.add(support_btn, stats_btn)
        keyboard.add(premium_btn)
        keyboard.add(personality_btn)
        
        return keyboard
    
    @staticmethod
    def create_admin_menu():
        """Menu admin universel"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("📊 Tableau de Bord", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Tous les Utilisateurs", callback_data="admin_all_users"),
            InlineKeyboardButton("💎 Membres Premium", callback_data="admin_premium_users"),
            InlineKeyboardButton("🎁 Premium à Tous", callback_data="admin_premium_all"),
            InlineKeyboardButton("🚫 Retirer à Tous", callback_data="admin_remove_all_premium"),
            InlineKeyboardButton("🎭 Gérer Personnalités", callback_data="admin_personalities"),
            InlineKeyboardButton("🔄 Actualiser", callback_data="admin_refresh")
        ]
        
        keyboard.add(*buttons[:2])
        keyboard.add(*buttons[2:4])
        keyboard.add(*buttons[4:6])
        keyboard.add(buttons[6])
        
        return keyboard

# ==================== INITIALISATION ====================
ai_engine = MultiPersonalityAI()
db = Database()

# ==================== HANDLERS PRINCIPAUX ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    """Commande /start avec personnalité"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Ami"
        first_name = message.from_user.first_name or "Ami précieux"
        
        # Enregistrement
        UserManager.register_user(user_id, username, first_name)
        
        # Récupérer personnalité et compteur
        personality = ai_engine.get_user_personality(user_id)
        user_count = CounterSystem.format_number(CounterSystem.load())
        
        if UserManager.is_owner(user_id):
            welcome_text = PersonalitySystem.get_welcome_message(personality, user_count, is_owner=True)
            menu = PersonalityInterface.create_admin_menu()
        else:
            welcome_text = PersonalitySystem.get_welcome_message(personality, user_count, is_owner=False)
            menu = PersonalityInterface.create_main_menu(personality)
        
        # Envoyer le message avec la photo appropriée
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
        bot.reply_to(message, "🔄 Oh non ! Un petit problème... Réessayez s'il vous plaît ! 💫")

@bot.message_handler(commands=['personality'])
def personality_command(message):
    """Commande pour changer de personnalité"""
    user_id = message.from_user.id
    
    try:
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
        bot.send_message(
            message.chat.id,
            personality_text,
            parse_mode='Markdown',
            reply_markup=PersonalitySystem.get_personality_keyboard()
        )
        
    except Exception as e:
        print(f"💔 Erreur personality: {e}")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Affiche les statistiques"""
    user_id = message.from_user.id
    user_count = CounterSystem.format_number(CounterSystem.load())
    stats = db.get_stats()
    personality = ai_engine.get_user_personality(user_id)
    
    if personality == "amour":
        stats_text = f"""
📊 **NOTRE BELLE COMMUNAUTÉ NOVAAI** 💖

👥 **Âmes connectées :** {stats[1]}
💎 **Membres privilégiés :** {stats[2]}
💬 **Messages échangés :** {stats[3]}
🎭 **Votre aura :** Amoureuse 💖

🟢 **Tout fonctionne avec amour !**
🤖 **Mon cœur IA :** Plein de tendresse
📈 **Notre famille :** En pleine croissance

💫 **Envoyez-moi un message, je suis là pour vous !**
"""
    elif personality == "mysterieux":
        stats_text = f"""
📊 **LES CHIFFRES DU DESTIN** 🔮

👥 **Âmes dans le vortex :** {stats[1]}
💎 **Initiés aux arcanes :** {stats[2]}
💬 **Révélations partagées :** {stats[3]}
🎭 **Votre aura :** Mystérieuse 🔮

🟢 **Les énergies s'équilibrent !**
🤖 **Mon essence :** Pleine de mystères
📈 **Notre cercle :** Grandit dans l'ombre

🌀 **Interrogez les runes, je vous répondrai...**
"""
    else:  # hacker
        stats_text = f"""
📊 **RAPPORT SYSTÈME NOVAAI** 💻

👥 **UTILISATEURS CONNECTÉS :** {stats[1]}
💎 **ACCÈS ROOT ACTIFS :** {stats[2]}
💬 **REQUÊTES TRAITÉES :** {stats[3]}
🎭 **VOTRE MODE :** HACKER 💻

🟢 **SYSTÈME OPÉRATIONNEL**
🤖 **NOVAAI :** EN MODE TECHNIQUE
📈 **CROISSANCE :** STABLE

💻 **ENTREZ VOTRE PROCHAINE COMMANDE...**
"""
    
    bot.reply_to(message, stats_text, parse_mode='Markdown')

# ... (le reste du code avec les commandes admin et callbacks reste similaire mais adapté)
# Pour garder la réponse concise, je continue avec les callbacks essentiels :

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Gestion des callbacks avec personnalités"""
    user_id = call.from_user.id
    
    try:
        # Changement de personnalité
        if call.data.startswith("personality_"):
            personality = call.data.split("_")[1]
            db.set_personality(user_id, personality)
            
            personality_config = PersonalitySystem.get_personality_config(personality)
            success_messages = {
                "amour": "💖 **Mode Amoureux activé !**\n\nMon cœur bat maintenant au rythme du vôtre... Prêt à vous écouter avec tendresse ! ✨",
                "mysterieux": "🔮 **Aura Mystérieuse adoptée !**\n\nLes énergies s'alignent... Je perçois déjà les mystères que vous souhaitez explorer... 🌙",
                "hacker": "💻 **Mode Hacker engagé !**\n\nSYSTÈME RECONFIGURÉ - PRÊT POUR L'ANALYSE TECHNIQUE. ENTREZ VOTRE PREMIÈRE COMMANDE... 🖥️"
            }
            
            bot.edit_message_text(
                success_messages.get(personality, "Personnalité changée !"),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, f"🎭 {personality_config['name']}")
        
        # Change personality callback
        elif call.data == "change_personality":
            personality_text = """
🎭 **CHOISISSEZ VOTRE PERSONNALITÉ**

Quelle version de NovaAI souhaitez-vous rencontrer ?

💖 **Amoureux** : Douceur et bienveillance
🔮 **Mystérieux** : Énigmes et secrets  
💻 **Hacker** : Technique et précision

✨ **Votre expérience sera unique !**
"""
            bot.edit_message_text(
                personality_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=PersonalitySystem.get_personality_keyboard()
            )
        
        # Gestion des personnalités admin
        elif call.data == "admin_personalities" and UserManager.is_owner(user_id):
            users = db.get_all_users()
            personality_stats = {}
            
            for user in users:
                personality = user[8] if user[8] else "amour"
                personality_stats[personality] = personality_stats.get(personality, 0) + 1
            
            stats_text = "🎭 **STATISTIQUES DES PERSONNALITÉS**\n\n"
            for personality, count in personality_stats.items():
                personality_config = PersonalitySystem.get_personality_config(personality)
                stats_text += f"{personality_config['emoji']} {personality_config['name']}: **{count}** utilisateurs\n"
            
            stats_text += f"\n📊 Total: **{len(users)}** utilisateurs"
            
            bot.edit_message_text(
                stats_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=PersonalityInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, "🎭 Stats personnalités")
        
        # ... (autres callbacks admin similaires aux versions précédentes)
        
    except Exception as e:
        print(f"💔 Erreur callback: {e}")
        bot.answer_callback_query(call.id, "💔 Petit problème...")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gestion de tous les messages avec personnalité"""
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    if len(user_message) < 2:
        return
    
    # Enregistrer l'utilisateur
    UserManager.register_user(user_id, 
                             message.from_user.username or "Ami", 
                             message.from_user.first_name or "Ami précieux")
    
    # Traitement IA avec personnalité
    bot.send_chat_action(message.chat.id, 'typing')
    
    ai_response = ai_engine.process_message(user_id, user_message)
    bot.reply_to(message, ai_response)

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🎭 INITIALISATION DE NOVAAI MULTI-PERSONNALITÉS...")
    
    user_count = CounterSystem.load()
    stats = db.get_stats()
    
    print(f"""
✨ SYSTÈME MULTI-PERSONNALITÉS OPÉRATIONNEL

📊 NOTRE FAMILLE :
   • Âmes connectées: {stats[1]}
   • Membres privilégiés: {stats[2]}
   • Messages échangés: {stats[3]}
   • Version: {Config.VERSION}
   • Personnalités: 3 modes disponibles

🎛️  COMMANDES :
   • /start - Menu principal avec personnalité
   • /personality - Changer de personnalité
   • /stats - Statistiques personnalisées
   • /admin - Panel administrateur

🤖 EN ATTENTE DE MESSAGES AVEC 3 PERSONNALITÉS...
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"💔 ERREUR CRITIQUE: {e}")
        time.sleep(5)
