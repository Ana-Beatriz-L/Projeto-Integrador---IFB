# 🚀 Guia Rápido para Execução (Apresentação)

Caso precise rodar o projeto em uma nova máquina, abra o terminal na pasta do projeto e siga estes comandos:

1. **Criar o ambiente virtual:**
   python -m venv venv

2. **Ativar o ambiente virtual:**
   - No Windows (Git Bash / CMD): `source venv/Scripts/activate` (ou `venv\Scripts\activate`)
   - No Linux/Mac: `source venv/bin/activate`

3. **Instalar as dependências:**
   pip install -r requirements.txt

4. **Rodar as migrações do banco de dados:**
   python manage.py migrate

5. **Popular os dados (Seed/CSV):**
   *(Comando do script que vocês criaram para gerar os dados no banco)*

6. **Iniciar o servidor Django:**
   python manage.py runserver

7. **Acessar no navegador:**
   - Documentação Swagger: http://127.0.0.1:8000/api/docs/

