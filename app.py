import streamlit as st
import pandas as pd
import os

# 🔹 Arquivos de dados
USER_DATA_FILE = "users.csv"
BASE_DATA_FILE = "amostra_1000_dados.csv"

# 🔹 Criar arquivo de usuários se não existir
if not os.path.exists(USER_DATA_FILE):
    pd.DataFrame(columns=["email", "username", "contador"]).to_csv(USER_DATA_FILE, index=False)

# 🔹 Função para verificar se usuário existe
def user_exists(email):
    users = pd.read_csv(USER_DATA_FILE)
    return email in users["email"].values

# 🔹 Função para obter o username e contador do usuário
def get_user_data(email):
    users = pd.read_csv(USER_DATA_FILE)
    if user_exists(email):
        user_row = users.loc[users["email"] == email]
        return user_row["username"].values[0], int(user_row["contador"].values[0])
    return None, None

# 🔹 Função para registrar usuário
def register_user(email, username):
    users = pd.read_csv(USER_DATA_FILE)
    if user_exists(email):
        return False
    new_user = pd.DataFrame([[email, username, 0]], columns=["email", "username", "contador"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_DATA_FILE, index=False)
    return True

# 🔹 Função para atualizar o contador no arquivo CSV
def update_user_progress(email, contador):
    users = pd.read_csv(USER_DATA_FILE)
    users.loc[users["email"] == email, "contador"] = contador
    users.to_csv(USER_DATA_FILE, index=False)

# 🔹 Função para salvar a classificação do usuário
def save_classification(username, text, sentiment):
    user_file = f"classificacoes_{username}.csv"
    if os.path.exists(user_file):
        df_user = pd.read_csv(user_file)
    else:
        df_user = pd.DataFrame(columns=["text", "sentimento"])
    
    new_entry = pd.DataFrame([[text, sentiment]], columns=["text", "sentimento"])
    df_user = pd.concat([df_user, new_entry], ignore_index=True)
    df_user.to_csv(user_file, index=False)

# 🔹 Inicializar sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.email = None
    st.session_state.username = None
    st.session_state.contador = 0  # Inicializa contador de progresso

# 🔹 Tela de login e cadastro
if not st.session_state.authenticated:
    st.title("🔐 Acesso ao Sistema")
    option = st.radio("Selecione uma opção:", ["Entrar", "Registrar"])

    email = st.text_input("Email")
    username = st.text_input("Nome de usuário") if option == "Registrar" else None

    if st.button("Continuar"):
        users = pd.read_csv(USER_DATA_FILE)
        if option == "Registrar":
            if register_user(email, username):
                st.success("Registro bem-sucedido! Agora você pode acessar.")
            else:
                st.error("Este email já está cadastrado. Faça login.")
        else:
            if user_exists(email):
                username, contador = get_user_data(email)
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.username = username
                st.session_state.contador = contador
                st.success(f"Bem-vindo, {username}!")
                st.rerun()
            else:
                st.error("Usuário não encontrado. Registre-se primeiro.")
else:
    # 🔹 Logout
    st.sidebar.write(f"👤 Usuário: {st.session_state.username}")
    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.session_state.email = None
        st.session_state.username = None
        st.session_state.contador = 0  # Reset contador ao sair
        st.rerun()

    # 🔹 Carregar os dados-base
    df = pd.read_csv(BASE_DATA_FILE)
    
    # 🔹 Verificar se ainda há textos não classificados
    if st.session_state.contador >= len(df):
        st.success("Parabéns! Você já classificou todos os textos.")
    else:
        st.title(f"Classificação de Sentimentos ({st.session_state.username})")
        st.write(f"🔹 Texto {st.session_state.contador + 1} de {len(df)}")

        # 🔹 Selecionar o próximo texto não classificado
        texto_atual = df.loc[st.session_state.contador, "text"]
        st.write(texto_atual)

        # 🔹 Função para salvar resposta e avançar
        def salvar_resposta(sentimento):
            save_classification(st.session_state.username, texto_atual, sentimento)  # Salvar no arquivo do usuário
            st.session_state.contador += 1  # Avançar contador
            update_user_progress(st.session_state.email, st.session_state.contador)  # Salvar progresso no CSV
            st.rerun()

        # 🔹 Botões de classificação
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("😃 Positivo"):
                salvar_resposta("Positivo")
        with col2:
            if st.button("😠 Negativo"):
                salvar_resposta("Negativo")
        with col3:
            if st.button("🤔 Não sei"):
                salvar_resposta("Não sei")

    # 🔹 Exibir progresso
    progresso = min(st.session_state.contador / len(df), 1.0)
    st.progress(progresso)

    # 🔹 Botão para baixar as classificações do usuário
    user_file = f"classificacoes_{st.session_state.username}.csv"
    if os.path.exists(user_file):
        with open(user_file, "rb") as f:
            st.download_button(
                label="📥 Baixar minhas classificações",
                data=f,
                file_name=f"classificacoes_{st.session_state.username}.csv",
                mime="text/csv"
            )
