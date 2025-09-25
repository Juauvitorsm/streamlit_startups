import streamlit as st
import requests
import pandas as pd
from streamlit_option_menu import option_menu

from config import API_URL

st.set_page_config(page_title="Busca de Empresas", page_icon="🏢", layout="wide")

params = st.query_params

if "token" not in st.session_state:
    st.session_state["token"] = params.get("token", "")
if "selected_company_data" not in st.session_state:
    st.session_state["selected_company_data"] = {}
if "search_results" not in st.session_state:
    st.session_state["search_results"] = []
if "show_dashboard" not in st.session_state:
    st.session_state["show_dashboard"] = False
if "form_type" not in st.session_state:
    st.session_state["form_type"] = "login"
if "all_companies_data" not in st.session_state:
    st.session_state["all_companies_data"] = None
if "home_page_search_results" not in st.session_state:
    st.session_state["home_page_search_results"] = None


def display_dashboard(company_data):
    st.markdown(f"## 📊 Dashboard: **{company_data.get('nome_da_empresa', 'N/A')}**")
    st.caption(f"ID da Empresa: {company_data.get('id', 'N/A')}")
    st.markdown("---")

    if st.button("⬅️ Voltar para a Lista"):
        st.session_state["show_dashboard"] = False
        st.rerun()

    st.subheader("📌 Visão Geral")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚀 Fase da Startup", company_data.get('fase_da_startup', 'N/A'))
    with col2:
        st.metric("📅 Ano de Fundação", company_data.get('ano_de_fundacao', 'N/A'))
    with col3:
        st.metric("👥 Colaboradores", company_data.get('colaboradores', 'N/A'))

    st.markdown("---")

    st.subheader("💰 Informações Financeiras e de Mercado")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("📈 Faturamento", company_data.get('faturamento', 'N/A'))
    with col5:
        st.metric("💵 Recebeu Investimento?", company_data.get('recebeu_investimento', 'N/A'))
    with col6:
        st.metric("🌍 Negócios no Exterior", company_data.get('negocios_no_exterior', 'N/A'))

    st.markdown("---")

    st.subheader("📑 Detalhes da Empresa")
    with st.expander("📬 Contato"):
        st.write(f"**Endereço:** {company_data.get('endereco', 'N/A')}")
        st.write(f"**CNPJ:** {company_data.get('cnpj', 'N/A')}")
        st.write(f"**E-mail:** {company_data.get('email', 'N/A')}")
        st.write(f"**Site:** {company_data.get('site', 'N/A')}")
        st.write(f"**Rede Social:** {company_data.get('rede_social', 'N/A')}")

    with st.expander("⚙️ Modelo e Tecnologia"):
        st.write(f"**Setor Principal:** {company_data.get('setor_principal', 'N/A')}")
        st.write(f"**Setor Secundário:** {company_data.get('setor_secundario', 'N/A')}")
        st.write(f"**Público Alvo:** {company_data.get('publico_alvo', 'N/A')}")
        st.write(f"**Modelo de Negócio:** {company_data.get('modelo_de_negocio', 'N/A')}")
        st.write(f"**Solução:** {company_data.get('solucao', 'N/A')}")

    with st.expander("📌 Status"):
        st.write(f"**Patente:** {company_data.get('patente', 'N/A')}")
        st.write(f"**Já Pivotou?:** {company_data.get('ja_pivotou', 'N/A')}")
        st.write(f"**Comunidades:** {company_data.get('comunidades', 'N/A')}")


def home_page():
    if st.session_state["show_dashboard"]:
        display_dashboard(st.session_state["selected_company_data"])
        return

    st.title("🏠 Home")
    st.write("Digite uma palavra-chave para buscar empresas.")

    all_phases = sorted(list(set(
        comp.get('fase_da_startup', 'N/A')
        for comp in st.session_state.get('all_companies_data', [])
    )))
    all_phases.insert(0, "Todas as Fases")

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("🔍 Pesquisar", key="query_input")
    with col2:
        selected_phase = st.selectbox("🚀 Filtrar por Fase:", all_phases, key="home_phase_select")

    search_button = st.button("Buscar")

    if search_button:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        try:
            params = {"query": query}
            if selected_phase != "Todas as Fases":
                params["fase"] = selected_phase
            
            response = requests.get(f"{API_URL}/optimized_search", params=params, headers=headers)
            
            response.raise_for_status()
            st.session_state["home_page_search_results"] = response.json()
            st.rerun()
        except requests.exceptions.RequestException as err:
            st.error(f"Erro: {err}")

    if st.session_state["home_page_search_results"]:
        results = st.session_state["home_page_search_results"]
        if results:
            st.success(f"Encontramos {len(results)} empresas:")
            df_results = pd.DataFrame(results)
            st.dataframe(df_results[['nome_da_empresa', 'setor_principal', 'fase_da_startup']])

            st.markdown("---")

            selected_company_name = st.selectbox(
                "Selecione uma empresa",
                [empresa['nome_da_empresa'] for empresa in results],
                key="select_company_dashboard"
            )

            selected_company = next(
                (empresa for empresa in results
                 if empresa['nome_da_empresa'] == selected_company_name),
                None
            )
            if selected_company:
                st.session_state["selected_company_data"] = selected_company
                if st.button("📊 Ver Dashboard"):
                    st.session_state["show_dashboard"] = True
                    st.rerun()
        else:
            st.info("Nenhuma empresa encontrada com estes critérios.")


def list_companies_page():
    if st.session_state["show_dashboard"]:
        display_dashboard(st.session_state["selected_company_data"])
        return

    st.title("📄 Lista de Empresas")

    if st.session_state["all_companies_data"] is None:
        st.info("Carregando empresas...")
        headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
        try:
            response = requests.get(f"{API_URL}/companies", headers=headers)
            response.raise_for_status()
            st.session_state["all_companies_data"] = response.json()
            st.rerun()
        except requests.exceptions.RequestException as err:
            st.error(f"Erro ao buscar empresas: {err}")
            return

    all_phases = sorted(list(set(
        comp.get('fase_da_startup', 'N/A')
        for comp in st.session_state["all_companies_data"]
    )))
    all_phases.insert(0, "Todas as Fases")

    with st.form("filter_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Pesquisar por nome, setor ou solução:", key="list_search")
        with col2:
            selected_phase = st.selectbox("🚀 Filtrar por Fase:", all_phases, key="phase_select")
        
        submit_button = st.form_submit_button("Aplicar Filtros")

    if submit_button or "filtered_results" not in st.session_state:
        filtered_companies = st.session_state["all_companies_data"]

        if selected_phase != "Todas as Fases":
            filtered_companies = [
                comp for comp in filtered_companies
                if comp.get('fase_da_startup', 'N/A') == selected_phase
            ]
        
        if search_term:
            filtered_companies = [
                comp for comp in filtered_companies
                if search_term.lower() in str(comp.get('nome_da_empresa', '')).lower()
                or search_term.lower() in str(comp.get('setor_principal', '')).lower()
                or search_term.lower() in str(comp.get('solucao', '')).lower()
            ]
        st.session_state["filtered_results"] = filtered_companies
    
    else:
        filtered_companies = st.session_state["filtered_results"]
    
    if filtered_companies:
        st.success(f"Exibindo {len(filtered_companies)} empresas:")
        df_filtered = pd.DataFrame(filtered_companies)
        st.dataframe(df_filtered[['nome_da_empresa', 'setor_principal', 'fase_da_startup']], use_container_width=True)

        st.markdown("---")

        selected_company_name = st.selectbox(
            "Selecione uma empresa para ver os detalhes",
            [comp['nome_da_empresa'] for comp in filtered_companies],
            key="list_select_company"
        )

        selected_company = next((comp for comp in filtered_companies if comp['nome_da_empresa'] == selected_company_name), None)

        if selected_company:
            st.session_state["selected_company_data"] = selected_company
            if st.button("📊 Ver Dashboard da Empresa"):
                st.session_state["show_dashboard"] = True
                st.rerun()
    else:
        st.info("Nenhuma empresa encontrada com estes filtros.")


def login_form():
    st.title("🔑 Login")
    with st.form("login_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Entrar")

    if submit_button:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["token"] = token
            st.query_params["token"] = token
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos.")

def register_form():
    st.title("📝 Criar Conta")
    with st.form("register_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Cadastrar")

    if submit_button:
        response = requests.post(
            f"{API_URL}/register",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            st.success("Conta criada com sucesso! Agora faça login.")
            st.session_state["form_type"] = "login"
            st.rerun()
        else:
            st.error(f"Erro: {response.json().get('detail', 'Erro desconhecido')}")

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()
    
def main():
    if st.session_state.get("token"):
        # Garante que a lista de empresas seja carregada após o login
        if st.session_state["all_companies_data"] is None:
            headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
            try:
                response = requests.get(f"{API_URL}/companies", headers=headers)
                response.raise_for_status()
                st.session_state["all_companies_data"] = response.json()
            except requests.exceptions.RequestException as err:
                st.error(f"Erro ao carregar empresas: {err}")
                
        with st.sidebar:
            st.markdown("## 🚀 Painel Interativo")
            escolha = option_menu(
                menu_title="Menu",
                options=["Home", "Listar Empresas", "Sair"],
                icons=["house", "building", "box-arrow-right"],
                menu_icon="cast",
                default_index=0,
            )

        if escolha == "Home":
            home_page()
        elif escolha == "Listar Empresas":
            list_companies_page()
        elif escolha == "Sair":
            logout()
    else:
        if st.session_state["form_type"] == "register":
            register_form()
            if st.button("Já tem conta? 👉 Login"):
                st.session_state["form_type"] = "login"
                st.rerun()
        else:
            login_form()
            if st.button("Criar nova conta"):
                st.session_state["form_type"] = "register"
                st.rerun()

if __name__ == "__main__":
    main()