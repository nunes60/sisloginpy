"""
Sistema de Login e Cadastro de Usuários

Este módulo implementa um sistema completo de autenticação com interface de linha
de comando estilo COBOL. Inclui funcionalidades de login, cadastro de usuários,
recuperação de senha, e gerenciamento de usuários para administradores.

O sistema utiliza arquivos JSON para persistência de dados e implementa
mecanismos de segurança como limite de tentativas de login, bloqueio temporário
de conta, e criptografia de senhas.
"""
import json
import hashlib
import os
import time
import random
import string
import getpass
from datetime import datetime, timedelta
import sys
from config import (DATABASE_FILE, BACKUP_FILE, ATTEMPTS_FILE, 
                   MAX_LOGIN_ATTEMPTS, LOCKOUT_TIME, PASSWORD_MIN_LENGTH,
                   ADMIN_USERNAME, ADMIN_PASSWORD, SYSTEM_NAME,
                   HEADER_LENGTH, SCREEN_WIDTH)

# Atualizar os caminhos dos arquivos
DATABASE_FILE = 'data/users.json'
BACKUP_FILE = 'data/users_backup.json'
ATTEMPTS_FILE = 'data/login_attempts.json'

# Cores para o terminal
class Colors:
    """
    Classe contendo códigos ANSI para cores e formatação de texto no terminal.
    
    Estes códigos permitem adicionar cores e estilos ao texto exibido no console,
    melhorando a legibilidade e tornando a interface mais amigável.
    """
    HEADER = '\033[95m'  # Roxo claro para cabeçalhos
    BLUE = '\033[94m'    # Azul para elementos de destaque
    GREEN = '\033[92m'   # Verde para mensagens de sucesso
    WARNING = '\033[93m'  # Amarelo para avisos
    FAIL = '\033[91m'    # Vermelho para erros
    ENDC = '\033[0m'     # Código para finalizar a formatação
    BOLD = '\033[1m'     # Texto em negrito
    UNDERLINE = '\033[4m'  # Texto sublinhado
    ITALIC = '\033[3m'   # Texto em itálico

class LoginSystem:
    """
    Classe principal do sistema de login e gerenciamento de usuários.
    
    Esta classe gerencia todas as operações relacionadas aos usuários:
    - Carregamento e salvamento de dados
    - Registro de novos usuários
    - Autenticação de usuários
    - Recuperação de senha
    - Listagem de usuários (para administradores)
    """
    def __init__(self):
        """
        Inicializa o sistema de login.
        
        Configura os dicionários para armazenar usuários e tentativas de login,
        e carrega os dados existentes dos arquivos de persistência.
        """
        self.users = {}  # Dicionário para armazenar dados dos usuários
        self.login_attempts = {}  # Dicionário para armazenar tentativas de login
        self.load_data()  # Carrega dados dos arquivos
        
    def load_data(self):
        """
        Carrega os dados dos usuários e tentativas de login a partir dos arquivos JSON.
        
        Se os arquivos não existirem ou estiverem corrompidos, cria novas estruturas
        de dados vazias. Para o arquivo de usuários, cria um usuário administrador padrão
        se o arquivo não existir.
        """
        # Carrega os usuários
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r') as file:
                    self.users = json.load(file)
            except json.JSONDecodeError:
                print(f"{Colors.FAIL}Erro ao carregar arquivo de usuários. Criando novo.{Colors.ENDC}")
                self.users = {}
        else:
            # Cria o admin padrão se o arquivo não existir
            self.users = {
                ADMIN_USERNAME: {
                    "password": self.hash_password(ADMIN_PASSWORD),
                    "role": "admin",
                    "created_at": str(datetime.now()),
                    "last_login": None,
                    "recovery_code": None
                }
            }
            self.save_data()
        
        # Carrega as tentativas de login
        if os.path.exists(ATTEMPTS_FILE):
            try:
                with open(ATTEMPTS_FILE, 'r') as file:
                    self.login_attempts = json.load(file)
            except json.JSONDecodeError:
                self.login_attempts = {}
        else:
            self.login_attempts = {}

    def save_data(self):
        """
        Salva os dados dos usuários e tentativas de login nos arquivos JSON.
        
        Antes de salvar os dados dos usuários, cria um backup do arquivo atual
        como medida de segurança contra corrupção de dados.
        
        Em caso de erro durante o salvamento, exibe mensagens de erro apropriadas.
        """
        # Cria o diretório 'data' se não existir
        if not os.path.exists('data'):
            os.makedirs('data')

        # Cria um backup antes de salvar
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r') as file:
                    with open(BACKUP_FILE, 'w') as backup:
                        backup.write(file.read())
            except Exception as e:
                print(f"{Colors.FAIL}Erro ao criar backup: {str(e)}{Colors.ENDC}")
        
        # Salva os usuários
        try:
            with open(DATABASE_FILE, 'w') as file:
                json.dump(self.users, file, indent=4)
        except Exception as e:
            print(f"{Colors.FAIL}Erro ao salvar dados: {str(e)}{Colors.ENDC}")
        
        # Salva as tentativas de login
        try:
            with open(ATTEMPTS_FILE, 'w') as file:
                json.dump(self.login_attempts, file, indent=4)
        except Exception as e:
            print(f"{Colors.FAIL}Erro ao salvar tentativas de login: {str(e)}{Colors.ENDC}")

    def hash_password(self, password):
        """
        Criptografa a senha usando o algoritmo SHA-256.
        
        Args:
            password (str): Senha em texto plano a ser criptografada
            
        Returns:
            str: Hash hexadecimal da senha
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, confirm_password):
        """
        Registra um novo usuário no sistema.
        
        Verifica se o usuário já existe, se a senha atende aos requisitos mínimos
        e se a confirmação da senha corresponde à senha original.
        
        Args:
            username (str): Nome de usuário desejado
            password (str): Senha desejada
            confirm_password (str): Confirmação da senha
            
        Returns:
            tuple: (bool, str) - Sucesso da operação e mensagem explicativa
        """
        # Verificação básica
        if username in self.users:
            return False, "Usuário já existe."
        
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"A senha deve ter pelo menos {PASSWORD_MIN_LENGTH} caracteres."
        
        if password != confirm_password:
            return False, "As senhas não conferem."
        
        # Registro do usuário
        self.users[username] = {
            "password": self.hash_password(password),
            "role": "user",
            "created_at": str(datetime.now()),
            "last_login": None,
            "recovery_code": None
        }
        
        self.save_data()
        return True, "Usuário registrado com sucesso!"
    
    def login(self, username, password):
        """
        Verifica as credenciais e realiza o login do usuário.
        
        Implementa mecanismos de segurança como limite de tentativas de login
        e bloqueio temporário de conta após muitas tentativas incorretas.
        
        Args:
            username (str): Nome de usuário
            password (str): Senha do usuário
            
        Returns:
            tuple: (bool, str) - Sucesso do login e mensagem explicativa
        """
        # Verifica se o usuário existe
        if username not in self.users:
            return False, "Usuário não encontrado."
        
        # Verifica se o usuário está bloqueado
        if username in self.login_attempts:
            attempts = self.login_attempts[username]
            if "lockout_until" in attempts:
                lockout_time = datetime.fromisoformat(attempts["lockout_until"])
                if datetime.now() < lockout_time:
                    remaining = (lockout_time - datetime.now()).seconds
                    return False, f"Conta bloqueada. Tente novamente em {remaining} segundos."
                else:
                    # Remove o bloqueio
                    del self.login_attempts[username]["lockout_until"]
                    self.login_attempts[username]["count"] = 0
        
        # Verifica a senha
        if self.users[username]["password"] != self.hash_password(password):
            # Incrementa as tentativas de login
            if username not in self.login_attempts:
                self.login_attempts[username] = {"count": 0}
            
            self.login_attempts[username]["count"] += 1
            
            # Bloqueia a conta após MAX_LOGIN_ATTEMPTS tentativas
            if self.login_attempts[username]["count"] >= MAX_LOGIN_ATTEMPTS:
                lockout_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
                self.login_attempts[username]["lockout_until"] = lockout_until.isoformat()
                self.save_data()
                return False, f"Conta bloqueada por {LOCKOUT_TIME//60} minutos devido a muitas tentativas incorretas."
            
            remaining = MAX_LOGIN_ATTEMPTS - self.login_attempts[username]["count"]
            self.save_data()
            return False, f"Senha incorreta. Tentativas restantes: {remaining}."
        
        # Login bem-sucedido
        if username in self.login_attempts:
            self.login_attempts[username]["count"] = 0
        
        self.users[username]["last_login"] = str(datetime.now())
        self.save_data()
        return True, "Login realizado com sucesso!"

    def list_users(self):
        """
        Lista todos os usuários cadastrados no sistema.
        
        Esta função é primariamente usada pela interface administrativa.
        
        Returns:
            dict: Dicionário contendo todos os dados dos usuários
        """
        return self.users
    
    def generate_recovery_code(self, username):
        """
        Gera um código de recuperação para o usuário.
        
        O código de recuperação pode ser usado para redefinir a senha
        caso o usuário a tenha esquecido.
        
        Args:
            username (str): Nome do usuário que precisa recuperar a senha
            
        Returns:
            tuple: (bool, str) - Sucesso da operação e código/mensagem de erro
        """
        if username not in self.users:
            return False, "Usuário não encontrado."
        
        # Gera um código aleatório
        recovery_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.users[username]["recovery_code"] = recovery_code
        self.save_data()
        
        return True, recovery_code
    
    def reset_password(self, username, recovery_code, new_password):
        """
        Redefine a senha do usuário usando o código de recuperação.
        
        Args:
            username (str): Nome do usuário
            recovery_code (str): Código de recuperação previamente gerado
            new_password (str): Nova senha desejada
            
        Returns:
            tuple: (bool, str) - Sucesso da operação e mensagem explicativa
        """
        if username not in self.users:
            return False, "Usuário não encontrado."
        
        user = self.users[username]
        
        if not user["recovery_code"] or user["recovery_code"] != recovery_code:
            return False, "Código de recuperação inválido."
        
        if len(new_password) < PASSWORD_MIN_LENGTH:
            return False, f"A nova senha deve ter pelo menos {PASSWORD_MIN_LENGTH} caracteres."
        
        # Atualiza a senha
        user["password"] = self.hash_password(new_password)
        user["recovery_code"] = None
        self.save_data()
        
        return True, "Senha redefinida com sucesso!"

# Interface CLI estilo COBOL
class CobolInterface:
    """
    Interface de linha de comando com design inspirado em sistemas COBOL.
    
    Esta classe gerencia a interação com o usuário, fornecendo menus, mensagens formatadas
    e uma experiência de usuário consistente para todas as funcionalidades do sistema.
    """
    def __init__(self):
        """
        Inicializa a interface do sistema.
        
        Configura a conexão com o sistema de login e variáveis de estado para
        o controle da sessão do usuário.
        """
        self.system = LoginSystem()  # Instância do sistema de login
        self.logged_user = None      # Usuário atualmente logado (None se ninguém estiver logado)
        self.is_admin = False        # Flag indicando se o usuário logado é admin
    
    def clear_screen(self):
        """
        Limpa a tela do terminal.
        
        Usa comandos específicos do sistema operacional para limpar o terminal,
        proporcionando uma interface mais limpa entre os diferentes menus.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """
        Imprime o cabeçalho estilizado do sistema no estilo COBOL.
        
        Exibe o nome do sistema dentro de uma caixa delimitada por asteriscos,
        com formatação colorida para melhor visualização.
        """
        self.clear_screen()
        print(Colors.BLUE + "*" * HEADER_LENGTH + Colors.ENDC)
        print(Colors.BLUE + "*" + " " * (HEADER_LENGTH - 2) + "*" + Colors.ENDC)
        print(Colors.BLUE + "*" + Colors.BOLD + SYSTEM_NAME.center(HEADER_LENGTH - 2) + Colors.ENDC + Colors.BLUE + "*" + Colors.ENDC)
        print(Colors.BLUE + "*" + " " * (HEADER_LENGTH - 2) + "*" + Colors.ENDC)
        print(Colors.BLUE + "*" * HEADER_LENGTH + Colors.ENDC)
        print()
    
    def print_menu(self, options):
        """
        Imprime um menu de opções para o usuário.
        
        Args:
            options (list): Lista de strings com as opções do menu
        """
        for idx, option in enumerate(options, 1):
            print(f"{Colors.GREEN}{idx}. {option}{Colors.ENDC}")
        print(f"{Colors.GREEN}0. Sair{Colors.ENDC}")
        print()
    
    def get_input(self, prompt):
        """
        Solicita entrada do usuário com um prompt formatado.
        
        Args:
            prompt (str): Texto a ser exibido ao solicitar a entrada
            
        Returns:
            str: Entrada fornecida pelo usuário
        """
        print(f"{Colors.BOLD}{prompt}: {Colors.ENDC}", end="")
        return input()
    
    def get_password(self, prompt):
        """
        Solicita senha do usuário de forma segura, sem exibir os caracteres.
        
        Tenta usar getpass para ocultar a senha, mas tem um fallback para input()
        caso getpass não funcione no ambiente atual.
        
        Args:
            prompt (str): Texto a ser exibido ao solicitar a senha
            
        Returns:
            str: Senha fornecida pelo usuário
        """
        print(f"{Colors.BOLD}{prompt}: {Colors.ENDC}", end="")
        print(f"{Colors.WARNING}(A senha não será exibida enquanto você digita){Colors.ENDC}")
        try:
            return getpass.getpass("")
        except Exception as e:
            print(f"\n{Colors.WARNING}Erro ao usar método seguro para senha. Usando método alternativo.{Colors.ENDC}")
            print(f"{Colors.BOLD}{prompt}: {Colors.ENDC}", end="")
            return input()
    
    def show_message(self, message, is_error=False):
        """
        Exibe uma mensagem formatada para o usuário e aguarda confirmação.
        
        Args:
            message (str): Mensagem a ser exibida
            is_error (bool, optional): Se True, exibe como erro (vermelho).
                                       Se False, exibe como sucesso (verde).
        """
        color = Colors.FAIL if is_error else Colors.GREEN
        print(f"\n{color}{message}{Colors.ENDC}")
        input(f"\n{Colors.BOLD}Pressione ENTER para continuar...{Colors.ENDC}")
    
    def register_menu(self):
        """
        Exibe e gerencia o menu de registro de novo usuário.
        
        Solicita nome de usuário e senha, valida os dados e
        registra o novo usuário no sistema se todos os dados forem válidos.
        """
        self.print_header()
        print(f"{Colors.BOLD}CADASTRO DE NOVO USUÁRIO{Colors.ENDC}\n")
        
        username = self.get_input("Nome de usuário")
        
        # Verifica antecipadamente se o usuário já existe
        if username in self.system.users:
            self.show_message(f"O usuário '{username}' já existe no sistema. Por favor, escolha outro nome de usuário.", True)
            return
        
        password = self.get_password("Senha")
        confirm = self.get_password("Confirme a senha")
        
        success, message = self.system.register(username, password, confirm)
        self.show_message(message, not success)
    
    def login_menu(self):
        """
        Exibe e gerencia o menu de login de usuário.
        
        Solicita nome de usuário e senha, autentica o usuário e,
        se bem-sucedido, configura a sessão atual.
        """
        self.print_header()
        print(f"{Colors.BOLD}LOGIN DE USUÁRIO{Colors.ENDC}\n")
        
        username = self.get_input("Nome de usuário")
        
        # Verifica antecipadamente se o usuário existe
        if username not in self.system.users:
            self.show_message(f"O usuário '{username}' não existe no sistema.", True)
            return
        
        password = self.get_password("Senha")
        
        success, message = self.system.login(username, password)
        if success:
            self.logged_user = username
            self.is_admin = self.system.users[username]["role"] == "admin"
        
        self.show_message(message, not success)
    
    def format_date(self, date_str):
        """
        Formata uma string de data ISO para formato mais amigável.
        
        Args:
            date_str (str): String de data no formato ISO ou valor especial (None, "N/A")
            
        Returns:
            str: Data formatada como "DD/MM/YYYY às HH:MM" ou o valor especial original
        """
        if date_str in ["N/A", "Nunca", None]:
            return date_str
        
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%d/%m/%Y às %H:%M")
        except ValueError:
            return date_str
    
    def list_users_menu(self):
        """
        Exibe e gerencia o menu de listagem de usuários.
        
        Este menu é acessível apenas para administradores e exibe
        uma tabela formatada com todos os usuários cadastrados.
        """
        if not self.is_admin:
            self.show_message("Acesso negado! Apenas administradores podem acessar esta função.", True)
            return
        
        self.print_header()
        print(f"{Colors.BOLD}{Colors.BLUE}LISTA DE USUÁRIOS CADASTRADOS{Colors.ENDC}\n")
        
        users = self.system.list_users()
        
        # Cabeçalho da tabela com cores
        print(f"{Colors.BOLD}{'Usuário':<20}{'Papel':<15}{'Criado em':<25}{'Último login':<25}{Colors.ENDC}")
        print(f"{Colors.BLUE}{'-' * SCREEN_WIDTH}{Colors.ENDC}")
        
        # Contador de usuários
        count = 0
        
        for username, data in users.items():
            count += 1
            role = data.get("role", "user")
            created_at = self.format_date(data.get("created_at", "N/A"))
            last_login = self.format_date(data.get("last_login", "Nunca"))
            
            # Destaque para o admin
            if role == "admin":
                print(f"{Colors.WARNING}{username:<20}{role:<15}{created_at:<25}{last_login:<25}{Colors.ENDC}")
            else:
                print(f"{username:<20}{role:<15}{created_at:<25}{last_login:<25}")
        
        print(f"{Colors.BLUE}{'-' * SCREEN_WIDTH}{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Total de usuários: {count}{Colors.ENDC}")
        
        input(f"\n{Colors.BOLD}Pressione ENTER para voltar ao menu principal...{Colors.ENDC}")
    
    def recovery_menu(self):
        """
        Exibe e gerencia o menu de recuperação de senha.
        
        Oferece opções para gerar um código de recuperação ou
        redefinir a senha usando um código previamente gerado.
        """
        self.print_header()
        print(f"{Colors.BOLD}RECUPERAÇÃO DE SENHA{Colors.ENDC}\n")
        
        option = self.get_input("1. Gerar código de recuperação\n2. Redefinir senha com código\n\nEscolha uma opção")
        
        if option == "1":
            username = self.get_input("Nome de usuário")
            
            # Verifica antecipadamente se o usuário existe
            if username not in self.system.users:
                self.show_message(f"O usuário '{username}' não existe no sistema.", True)
                return
                
            success, result = self.system.generate_recovery_code(username)
            
            if success:
                message = f"Código de recuperação gerado: {result}\nGuarde este código!"
            else:
                message = result
            
            self.show_message(message, not success)
        
        elif option == "2":
            username = self.get_input("Nome de usuário")
            
            # Verifica antecipadamente se o usuário existe
            if username not in self.system.users:
                self.show_message(f"O usuário '{username}' não existe no sistema.", True)
                return
                
            recovery_code = self.get_input("Código de recuperação")
            
            # Verifica se o código de recuperação foi configurado
            if not self.system.users[username].get("recovery_code"):
                self.show_message("Este usuário não possui um código de recuperação ativo. Gere um primeiro.", True)
                return
                
            new_password = self.get_password("Nova senha")
            
            success, message = self.system.reset_password(username, recovery_code, new_password)
            self.show_message(message, not success)
        
        else:
            self.show_message("Opção inválida!", True)
    
    def run(self):
        """
        Método principal que executa o sistema de login.
        
        Implementa o loop principal da aplicação, exibindo o menu apropriado
        com base no status de autenticação do usuário e lidando com as
        diversas opções escolhidas.
        """
        while True:
            self.print_header()
            
            if self.logged_user:
                role = "Administrador" if self.is_admin else "Usuário"
                print(f"Logado como: {Colors.BOLD}{self.logged_user}{Colors.ENDC} ({role})\n")
                
                if self.is_admin:
                    self.print_menu(["Visualizar todos os usuários do sistema", "Sair da conta"])
                    option = self.get_input("Escolha uma opção")
                    
                    if option == "1":
                        self.list_users_menu()
                    elif option == "2" or option == "0":
                        self.logged_user = None
                        self.is_admin = False
                        self.show_message("Logout realizado com sucesso!")
                    else:
                        self.show_message("Opção inválida!", True)
                
                else:
                    self.print_menu(["Sair da conta"])
                    option = self.get_input("Escolha uma opção")
                    
                    if option == "1" or option == "0":
                        self.logged_user = None
                        self.show_message("Logout realizado com sucesso!")
                    else:
                        self.show_message("Opção inválida!", True)
            
            else:
                self.print_menu(["Login", "Cadastrar", "Recuperar senha"])
                option = self.get_input("Escolha uma opção")
                
                if option == "1":
                    self.login_menu()
                elif option == "2":
                    self.register_menu()
                elif option == "3":
                    self.recovery_menu()
                elif option == "0":
                    self.print_header()
                    print(f"{Colors.BOLD}Obrigado por usar o {SYSTEM_NAME}!{Colors.ENDC}")
                    sys.exit(0)
                else:
                    self.show_message("Opção inválida!", True)

if __name__ == "__main__":
    """
    Ponto de entrada do programa.
    
    Inicializa a interface e trata exceções para garantir que o programa
    seja encerrado de forma elegante.
    """
    try:
        interface = CobolInterface()  # Cria a interface
        interface.run()               # Inicia o sistema
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado pelo usuário.")
    except Exception as e:
        print(f"\n{Colors.FAIL}Erro inesperado: {str(e)}{Colors.ENDC}")
        input("Pressione ENTER para sair...")
