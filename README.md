#  Patrimoine App

Application web complète de gestion des patrimoines culturels et historiques avec localisation géographique, développée avec FastAPI.

##  Fonctionnalités

###  Gestion des utilisateurs
-  Inscription et connexion sécurisées
-  Authentification JWT avec tokens
-  Rôles utilisateur (user/admin)
-  Protection contre les tentatives de connexion échouées
-  Gestion du profil (email, mot de passe)

###  Gestion des patrimoines
-  CRUD complet sur les biens patrimoniaux
-  Localisation GPS (latitude/longitude)
-  Upload et gestion de photos
-  Recherche par ville
-  Export des données (PDF, GPX)

###  Interface utilisateur
-  Interface web moderne avec Jinja2
-  Pages : login, register, dashboard, map, profil
-  Design responsive
-  Navigation intuitive

###  Administration
-  Panel admin pour gérer les utilisateurs
-  Activation/désactivation de comptes
-  Déblocage des comptes bloqués
-  Liste des utilisateurs avec rôles

##  Architecture Technique

###  Stack Technique
- **Backend** : FastAPI 0.129.0
- **Base de données** : SQLite (configurable MySQL/PostgreSQL)
- **ORM** : SQLAlchemy 2.0.46
- **Authentification** : JWT + Argon2
- **Templates** : Jinja2
- **Validation** : Pydantic v2

###  Structure du projet
```
patrimoine_app/
    main.py              # Application FastAPI principale
    models.py            # Modèles SQLAlchemy (User, Patrimoine)
    config.py            # Configuration Pydantic Settings
    database.py          # Configuration base de données
    auth.py              # Logique d'authentification
    schemas.py           # Schémas Pydantic
    routers/             # Routes API
        users.py         # Gestion utilisateurs
        patrimoines.py   # Gestion patrimoines
        exports.py       # Fonctions export
    templates/           # Pages HTML
    static/              # Fichiers statiques
    photos/              # Upload photos
    tests/               # Tests unitaires
```

##  Installation

###  Prérequis
- Python 3.8+
- Git

###  Étapes
```bash
# Cloner le projet
git clone https://github.com/Nojo25-Sys/patrimoine-app.git
cd patrimoine-app

# Créer environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos configurations
```

###  Configuration (.env)
```env
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=1
MAIL_FROM=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_application_gmail
DATABASE_URL=sqlite:///./patrimoine.db
```

##  Lancement

###  Développement
```bash
# Serveur de développement avec rechargement automatique
python -m uvicorn main:app --reload

# Sur un port spécifique (si 8000 occupé)
python -m uvicorn main:app --port 8001
```

###  Production
```bash
# Serveur de production
uvicorn main:app --host 0.0.0.0 --port 8000
```

##  Accès

###  Interface web
- **Login** : http://127.0.0.1:8000/page/login
- **Register** : http://127.0.0.1:8000/page/register
- **Dashboard** : http://127.0.0.1:8000/page/dashboard
- **Map** : http://127.0.0.1:8000/page/map
- **Profil** : http://127.0.0.1:8000/page/profil

###  API Documentation
- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc
- **OpenAPI JSON** : http://127.0.0.1:8000/openapi.json

###  Health Check
- **Status** : http://127.0.0.1:8000/health

##  Utilisation

###  Créer un compte admin
1. S'inscrire via l'interface web
2. Mettre à jour le rôle en base de données :
```sql
UPDATE users SET role = 'admin' WHERE username = 'votre_nom';
```

###  API Endpoints principaux

#### Authentification
- `POST /users/` - Créer un utilisateur
- `POST /login` - Connexion
- `GET /users/me` - Profil utilisateur

#### Patrimoines
- `GET /patrimoines/` - Lister les patrimoines
- `POST /patrimoines/` - Créer un patrimoine
- `PUT /patrimoines/{id}` - Modifier un patrimoine
- `DELETE /patrimoines/{id}` - Supprimer un patrimoine
- `POST /patrimoines/{id}/photo` - Upload photo
- `GET /patrimoines/ville/{ville}` - Rechercher par ville

#### Exports
- `GET /exports/pdf/{ville}` - Export PDF
- `GET /exports/gpx/{ville}` - Export GPX
- `POST /exports/mail/{ville}` - Envoyer par email

##  Sécurité

###  Mesures implémentées
-  Hachage des mots de passe avec Argon2
-  Tokens JWT avec expiration
-  Validation des entrées avec Pydantic
-  Protection contre les attaques par force brute
-  CORS configuré
-  Validation des fichiers uploadés

###  Recommandations
-  Utiliser des clés secrètes fortes
-  Configurer HTTPS en production
-  Limiter la taille des uploads
-  Sauvegarder régulièrement la base de données

##  Tests

###  Lancer les tests
```bash
# Installer pytest si nécessaire
pip install pytest

# Lancer tous les tests
pytest

# Lancer avec coverage
pytest --cov=. --cov-report=html
```

###  Structure des tests
- `tests/test_auth.py` - Tests authentification
- `tests/test_users.py` - Tests utilisateurs
- `tests/test_patrimoines.py` - Tests patrimoines
- `tests/test_exports.py` - Tests exports

##  Déploiement

###  Docker (recommandé)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

###  Variables d'environnement en production
- Utiliser des variables d'environnement réelles
- Configurer une base de données robuste (PostgreSQL/MySQL)
- Configurer les emails avec un service SMTP
- Activer HTTPS

##  Contribuer

###  Guidelines
1. Fork le projet
2. Créer une branche feature
3. Faire les modifications
4. Ajouter des tests
5. Soumettre une pull request

###  Code style
- Respecter PEP 8
- Ajouter des docstrings
- Commenter le code complexe
- Maintenir la cohérence du style existant

##  Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

##  Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Consulter la documentation API
- Vérifier les logs du serveur

---

**Développé avec  par Nojo25-Sys**