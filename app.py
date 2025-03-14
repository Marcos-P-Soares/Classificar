import streamlit as st
import pandas as pd
import os
import yaml
from streamlit_authenticator import Authenticate

# 🔹 Configuração da autenticação 🔹
CONFIG = {
    "credentials": {
        "usernames": {}
    },
    "cookie": {
        "expiry_days": 30,
        "key": "random_key"
    },
    "preauthorized": {
        "emails": []
    }
}

# Criar autenticação
authenticator = Authenticate(CONFIG["credentials"], CONFIG["cookie"]["key"], "app_name", CONFIG["cookie"]["expiry_days"])

# Exibir formulário de login
email, authentication_status, username = authenticator.login("Login", "main")

# Se usuário autenticado:
if authentication_status:
    st.sidebar.write(f"**Usuário:** {username}")
    authenticator.logout("Sair", "sidebar")

    # Nome do arquivo de progresso do usuário
    user_file = f"classificacoes_{username}.csv"

    # 🔹 Carregar dados 🔹
    file_path = "amostra_1000_dados.csv"
    df = pd.read_csv(file_path)

    # Criar arquivo do usuário se não existir
    if not os.path.exists(user_file):
        df_user = df.copy()
        df_user["Sent"] = df_user["Sent"].fillna("")
        df_user.to_csv(user_file, index=False)
    else:
        df_user = pd.read_csv(user_file)

    # 🔹 Recuperar progresso 🔹
    if "index" not in st.session_state:
        # Encontrar o primeiro índice não classificado
        textos_nao_classificados = df_user[df_user["Sent"] == ""].index
        st.session_state.index = textos_nao_classificados[0] if len(textos_nao_classificados) > 0 else len(df_user)

    st.title(f"Classificação de Sentimentos ({username})")
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
            
            # Buscar próximo índice não classificado
            textos_nao_classificados = df_user[df_user["Sent"] == ""].index
            st.session_state.index = textos_nao_classificados[0] if len(textos_nao_classificados) > 0 else len(df_user)
            
            st.experimental_rerun()

    # Mostrar progresso
    st.progress(st.session_state.index / len(df_user))

    # Botão para baixar a classificação feita
    st.download_button(
        "Baixar minhas classificações",
        data=df_user.to_csv(index=False).encode("utf-8"),
        file_name=f"classificacoes_{username}.csv",
        mime="text/csv"
    )

# 🔹 Caso o login falhe 🔹
elif authentication_status == False:
    st.error("Email/senha incorretos. Tente novamente.")

elif authentication_status == None:
    st.warning("Por favor, faça login.")
