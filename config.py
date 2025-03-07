"""
Módulo de configuração do Sistema de Autenticação.

Este módulo contém todas as configurações centrais usadas pelo sistema,
incluindo configurações de arquivos, segurança e interface.
"""

# Configurações de arquivos e diretórios
DATABASE_FILE = "data/users.json"  # Arquivo principal que armazena dados dos usuários
BACKUP_FILE = "data/users_backup.json"  # Arquivo de backup para dados dos usuários
ATTEMPTS_FILE = "data/login_attempts.json"  # Arquivo que armazena tentativas de login

# Configurações de segurança
MAX_LOGIN_ATTEMPTS = 3  # Número máximo de tentativas de login antes do bloqueio
LOCKOUT_TIME = 300  # Tempo de bloqueio em segundos (5 minutos)
PASSWORD_MIN_LENGTH = 6  # Comprimento mínimo para senhas
ADMIN_USERNAME = "admin"  # Nome de usuário para o administrador padrão
ADMIN_PASSWORD = "admin123"  # Senha para o administrador padrão (alterar em produção)

# Configurações de interface
SYSTEM_NAME = "SISTEMA DE AUTENTICAÇÃO"  # Nome exibido no cabeçalho do sistema
HEADER_LENGTH = 80  # Largura do cabeçalho em caracteres
SCREEN_WIDTH = 80  # Largura máxima da tela para formatação de texto
