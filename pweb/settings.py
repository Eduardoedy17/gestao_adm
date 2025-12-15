"""
Django settings for pweb project.
Arquivo configurado para Deploy na Vercel com PostgreSQL.
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURANÇA ---
# Em produção (Vercel), busca a chave do ambiente. Localmente, usa a chave insegura.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-t_-cl2580se4quu7kbgb3pfsgmvx_966^1xby%l8_2bwfgjf9&')

# DEBUG: Desativa automaticamente se estiver na Vercel
DEBUG = 'VERCEL' not in os.environ

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.vercel.app', '.now.sh']


# --- APLICAÇÕES ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home', # Seu app principal
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utils.context_processors.data_atual', # Seu processador de contexto
            ],
        },
    },
]

WSGI_APPLICATION = 'pweb.wsgi.application'


# --- BANCO DE DADOS (Lógica Híbrida: Vercel Postgres vs SQLite Local) ---

# 1. Tenta pegar a variável de ambiente do Postgres da Vercel
postgres_url = os.environ.get("POSTGRES_URL")

if postgres_url:
    # CONFIGURAÇÃO DE PRODUÇÃO (VERCEL)
    DATABASES = {
        'default': dj_database_url.parse(
            postgres_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True, # Vercel exige SSL
        )
    }
else:
    # CONFIGURAÇÃO LOCAL (SEU COMPUTADOR)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# --- VALIDAÇÃO DE SENHA ---

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- INTERNACIONALIZAÇÃO ---

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = False
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'


# --- ARQUIVOS ESTÁTICOS (CSS/JS) ---

# 1. URL pública (Obrigatório ter a barra no início)
STATIC_URL = '/static/'

# 2. Pasta onde você edita os arquivos no seu PC
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 3. Pasta onde o Vercel vai guardar os arquivos processados
# A Vercel procura em 'staticfiles_build', mas o navegador espera '/static/'
# Por isso, salvamos dentro de 'staticfiles_build/static'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

# --- ARQUIVOS DE MÍDIA (UPLOADS) ---
# Nota: Na Vercel, arquivos de mídia (uploads) são temporários e somem após um tempo.
# Para produção real, seria necessário usar AWS S3 ou similar.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- OUTROS ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'