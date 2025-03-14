import streamlit as st
import pandas as pd
import os

# 🔹 Criar diretório de usuários
USER_DATA_FILE = "users.csv"
if not os.path.exists(USER_DATA_FILE):
    pd.DataFrame(columns=["email", "username"]).to_csv(USER_DATA_FILE, index=False)

# 🔹 Função para verificar se usuário existe
def user_exists(email):
    users = pd.read_csv(USER_DATA_FILE)
    return email in users["email"].values

# 🔹 Função para obter o username do usuário
def get_username(email):
    users = pd.read_csv(USER_DATA_FILE)
    return users.loc[users["email"] == email, "username"].values[0] if user_exists(email) else None

# 🔹 Função para registrar usuário
def register_user(email, username):
    users = pd.read_csv(USER_DATA_FILE)
    if user_exists(email):
        return False
    new_user = pd.DataFrame([[email, username]], columns=["email", "username"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_DATA_FILE, index=False)
    return True

# 🔹 Verificar sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.email = None
    st.session_state.username = None

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
                username = get_username(email)
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.username = username
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
        st.rerun()

    # 🔹 Nome do arquivo de progresso do usuário
    user_file = f"classificacoes_{st.session_state.username}.csv"
    file_path = "amostra_1000_dados.csv"

    # 🔹 Carregar os dados
    df = pd.read_csv(file_path)

    # Criar arquivo do usuário se não existir
    if not os.path.exists(user_file):
        df_user = df.copy()
        df_user.to_csv(user_file, index=False)
    else:
        df_user = pd.read_csv(user_file)

    # 🔹 Criar coluna "Sent" se não existir
    if "Sent" not in df_user.columns:
        df_user["Sent"] = ""
        df_user.to_csv(user_file, index=False)

    # 🔹 Recuperar progresso
    if "index" not in st.session_state:
        textos_nao_classificados = df_user[df_user["Sent"] == ""].index
        st.session_state.index = textos_nao_classificados[0] if len(textos_nao_classificados) > 0 else len(df_user)

    st.title(f"Classificação de Sentimentos ({st.session_state.username})")
    st.write(f"Texto {st.session_state.index + 1} de {len(df_user)}")

    if st.session_state.index >= len(df_user):
        st.success("Parabéns! Você já classificou todos os textos.")
    else:
        st.write(df_user.iloc[st.session_state.index]["text"])

        # Se já tem um valor salvo, carregar
        current_value = df_user.iloc[st.session_state.index]["Sent"]
        default_index = ["Positivo", "Negativo", "Não sei"].index(current_value) if current_value in ["Positivo", "Negativo", "Não sei"] else 0

        sentimento = st.radio("Classifique o sentimento:", ["Positivo", "Negativo", "Não sei"], index=default_index)

        if st.button("Salvar e Próximo"):
            df_user.at[st.session_state.index, "Sent"] = sentimento
            df_user.to_csv(user_file, index=False)

            textos_nao_classificados = df_user[df_user["Sent"] == ""].index
            st.session_state.index = textos_nao_classificados[0] if len(textos_nao_classificados) > 0 else len(df_user)

            st.rerun()

    # 🔹 Mostrar progresso
    st.progress(st.session_state.index / len(df_user))

    # 🔹 Botão para baixar a classificação feita
    st.download_button(
        "Baixar minhas classificações",
        data=df_user.to_csv(index=False).encode("utf-8"),
        file_name=f"classificacoes_{st.session_state.username}.csv",
        mime="text/csv"
    )
