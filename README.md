# 🔐 Sistema de Autenticação e Gerenciamento de Usuários

Um sistema completo de autenticação e gerenciamento de usuários com interface de linha de comando, desenvolvido em Python puro.

## 📋 Sobre o Projeto

Este sistema implementa funcionalidades completas de autenticação e gerenciamento de usuários com foco em segurança e usabilidade. A interface de linha de comando é inspirada em sistemas COBOL, oferecendo uma experiência nostálgica mas funcional. O projeto foi desenvolvido em Python puro, utilizando apenas bibliotecas padrão, e armazena dados em arquivos JSON para persistência.

## ✨ Recursos

- 🔒 **Autenticação segura**
  - Armazenamento de senhas com hash SHA-256
  - Proteção contra tentativas excessivas de login
  - Bloqueio temporário de contas

- 👤 **Gerenciamento de usuários**
  - Cadastro de novos usuários
  - Login/logout
  - Recuperação de senha via código de segurança

- 👮 **Painel administrativo**
  - Visualização de todos os usuários cadastrados
  - Informações detalhadas sobre cada usuário

- 🛡️ **Segurança**
  - Criptografia de senhas
  - Bloqueio temporário após múltiplas tentativas
  - Backup automático da base de dados

- 🎨 **Interface amigável**
  - Terminal colorido com estilo retrô
  - Menus intuitivos
  - Feedback visual para todas as ações

## 🚀 Começando

### Pré-requisitos

- Python 3.6 ou superior
- Sistema operacional com suporte a terminais ANSI (Windows, macOS, Linux)

### Instalação

1. Clone o repositório ou baixe os arquivos para seu computador
   ```
   git clone https://github.com/nunes60/sisloginpy.git
   ```

2. Navegue até o diretório do projeto
   ```
   cd sisloginpy
   ```

3. Execute o programa principal
   ```
   python login_system.py
   ```

### Configuração

Todas as configurações do sistema estão centralizadas no arquivo `config.py`. Ajuste conforme necessário:

- `DATABASE_FILE` - Nome do arquivo da base de dados principal
- `MAX_LOGIN_ATTEMPTS` - Número máximo de tentativas de login
- `LOCKOUT_TIME` - Tempo de bloqueio em segundos
- `PASSWORD_MIN_LENGTH` - Comprimento mínimo das senhas
- `ADMIN_USERNAME` e `ADMIN_PASSWORD` - Credenciais do administrador padrão

⚠️ **IMPORTANTE**: Em ambientes de produção, altere a senha padrão do administrador!

## 📂 Estrutura do Projeto

```
Sistema de Login e Cadastro/
├── config.py                # Configurações do sistema
├── login_system.py          # Código principal da aplicação
├── data/                    # Diretório para arquivos de dados
│   ├── users.json           # Base de dados de usuários (gerado automaticamente)
│   ├── users_backup.json    # Backup da base de dados (gerado automaticamente)
│   └── login_attempts.json  # Registro de tentativas de login (gerado automaticamente)
└── README.md                # Este arquivo
```

## 📚 Bibliotecas Utilizadas

Este projeto utiliza apenas as bibliotecas padrão do Python, garantindo que não há dependências externas a serem instaladas. As principais bibliotecas utilizadas são:

- `json`: Para manipulação de arquivos JSON, onde os dados dos usuários e tentativas de login são armazenados.
- `hashlib`: Para criptografia das senhas utilizando o algoritmo SHA-256, garantindo a segurança das informações.
- `os`: Para interações com o sistema operacional, como limpar a tela do terminal e verificar a existência de arquivos.
- `time`: Para manipulação de tempo, como implementar o bloqueio temporário de contas após tentativas de login incorretas.
- `random` e `string`: Para geração de códigos de recuperação de senha aleatórios e seguros.
- `getpass`: Para solicitar a senha do usuário de forma segura, sem exibir os caracteres no terminal.
- `datetime`: Para manipulação de datas e horários, como registrar a data de criação dos usuários e o último login.
- `sys`: Para interações com o ambiente de execução do Python, como encerrar o programa.

## 🔧 Como Usar

### Primeiro Acesso

1. Execute o programa:
   ```
   python login_system.py
   ```

2. Faça login com o usuário administrador padrão:
   - Usuário: `admin`
   - Senha: `admin123`

### Funções Principais

#### Para Usuários Comuns:
- **Login**: Acesse sua conta com nome de usuário e senha
- **Cadastro**: Crie uma nova conta de usuário
- **Recuperação de senha**: Solicite um código de recuperação e redefina sua senha

#### Para Administradores:
- Todas as funções de usuários comuns
- **Listagem de usuários**: Visualize todos os usuários cadastrados com detalhes

## 🔐 Segurança

O sistema implementa várias camadas de segurança:

- Senhas armazenadas como hash SHA-256, não em texto simples
- Bloqueio temporário após várias tentativas de login incorretas
- Recuperação de senha segura através de códigos temporários
- Backup automático do banco de dados antes de qualquer alteração

## 🔄 Persistência de Dados

Todos os dados são armazenados em arquivos JSON no diretório `data`:

- `data/users.json`: Dados dos usuários (nomes, senhas hash, datas)
- `data/login_attempts.json`: Registros de tentativas de login e bloqueios
- `data/users_backup.json`: Backup automático da base de usuários

## ✏️ Customização

A interface de terminal utiliza cores ANSI para melhorar a legibilidade. Se estiver usando um terminal que não suporta cores ANSI, você pode desabilitar as cores editando a classe `Colors` no arquivo `login_system.py`.

## ❓ Perguntas Frequentes

### Esqueci a senha do administrador, o que fazer?

Se você esqueceu a senha de administrador e não há outros administradores no sistema, você precisará:

1. Excluir os arquivos `users.json` e `login_attempts.json`
2. Reiniciar a aplicação - isso irá recriar o usuário admin padrão

### As cores não estão aparecendo corretamente no meu terminal, o que posso fazer para resolver?

Alguns terminais Windows mais antigos não suportam códigos ANSI por padrão. Recomendamos:
- Usar Windows Terminal (disponível na Microsoft Store)
- Usar o console Anaconda
- Usar um terminal Linux via WSL
