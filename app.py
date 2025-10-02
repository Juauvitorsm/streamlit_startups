import streamlit as st
import requests
import pandas as pd
from streamlit_option_menu import option_menu
from config import API_URL # Certifique-se de que esta linha está correta para sua configuração

st.set_page_config(page_title="Busca de Empresas", page_icon="🏢", layout="wide")

params = st.query_params

# Inicializa estado da sessão
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
if "filtered_results" not in st.session_state:
    st.session_state["filtered_results"] = None

# ------------------- DASHBOARD UNIFICADO (SÓBRIO) -------------------
def display_dashboard(company_data):
    nome_empresa = company_data.get('nome_da_empresa', 'N/A')
    empresa_id = company_data.get('id', 'N/A')
    
    # CSS Específico do Dashboard
    st.markdown(f"""
    <style>
        .dashboard-header-exec {{
            background-color: #1B2D45; /* Azul Marinho */
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
        }}
        .dashboard-header-exec h2 {{
            color: #FFC300; /* Destaque Dourado */
            margin-top: 0;
            margin-bottom: 5px;
            font-size: 28px;
        }}
        .metric-card-exec {{
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
            margin-bottom: 15px;
            height: 100%; 
            border-left: 4px solid #FFC300; 
        }}
        .metric-card-exec h4 {{
            color: #6C7A89; 
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .metric-value-exec {{
            font-size: 26px;
            font-weight: bold;
            color: #1B2D45; 
        }}
        .info-block-exec {{
            background-color: #F8F9FA; 
            padding: 18px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 3px solid #1B2D45; 
            font-size: 14px;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Cabeçalho customizado Executivo
    st.markdown(f"""
    <div class="dashboard-header-exec">
        <h2>Dashboard - {nome_empresa}</h2>
        <p style='color: #DCE0E6; margin: 0;'>ID de Registro: {empresa_id}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("<- Voltar para a Lista de Empresas"):
        st.session_state["show_dashboard"] = False
        st.rerun()

    st.markdown("---")
    st.subheader("Informações Fundamentais")
    
    col1, col2, col3 = st.columns(3)
    
    col1.markdown(f"""
    <div class="metric-card-exec">
        <h4>Fase da Startup</h4>
        <div class="metric-value-exec">{company_data.get('fase_da_startup', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col2.markdown(f"""
    <div class="metric-card-exec">
        <h4>Ano de Fundação</h4>
        <div class="metric-value-exec">{company_data.get('ano_de_fundacao', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="metric-card-exec">
        <h4>Colaboradores</h4>
        <div class="metric-value-exec">{company_data.get('colaboradores', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("---")
    st.subheader("Indicadores Financeiros")
    
    col4, col5, col6 = st.columns(3)
    
    col4.markdown(f"""
    <div class="metric-card-exec">
        <h4>Faturamento (Estimado)</h4>
        <div class="metric-value-exec">{company_data.get('faturamento', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col5.markdown(f"""
    <div class="metric-card-exec">
        <h4>Recebeu Investimento?</h4>
        <div class="metric-value-exec">{company_data.get('recebeu_investimento', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

    col6.markdown(f"""
    <div class="metric-card-exec">
        <h4>Negócios no Exterior?</h4>
        <div class="metric-value-exec">{company_data.get('negocios_no_exterior', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Detalhes de Operação e Contato")
    
    col_detalhes, col_contato = st.columns(2)

    with col_detalhes:
        st.markdown("#### Modelo de Negócio e Mercado")
        st.markdown(f"""
        <div class="info-block-exec">
            <strong>Setor Principal:</strong> {company_data.get('setor_principal', 'N/A')}<br>
            <strong>Público Alvo:</strong> {company_data.get('publico_alvo', 'N/A')}<br>
            <strong>Modelo de Negócio:</strong> {company_data.get('modelo_de_negocio', 'N/A')}<br>
            <strong>Solução:</strong> {company_data.get('solucao', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
    with col_contato:
        st.markdown("#### Informações de Contato")
        st.markdown(f"""
        <div class="info-block-exec">
            <strong>Endereço:</strong> {company_data.get('endereco', 'N/A')}<br>
            <strong>E-mail:</strong> {company_data.get('email', 'N/A')}<br>
            <strong>Site:</strong> <a href="{company_data.get('site', '#')}" target="_blank">{company_data.get('site', 'N/A')}</a><br>
            <strong>CNPJ:</strong> {company_data.get('cnpj', 'N/A')}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Status de Inovação")
    
    col_status, col_inovacao = st.columns(2)

    with col_status:
        st.write(f"**Setor Secundário:** {company_data.get('setor_secundario', 'N/A')}")
    with col_inovacao:
        st.write(f"**Patente:** {company_data.get('patente', 'N/A')}")
        st.write(f"**Já Pivotou?:** {company_data.get('ja_pivotou', 'N/A')}")
        st.write(f"**Comunidades:** {company_data.get('comunidades', 'N/A')}")


# ------------------- HOME PAGE (CORPORATIVA E REFINADA COM LIMITE DE 5) -------------------
def home_page():
    if st.session_state["show_dashboard"]:
        display_dashboard(st.session_state["selected_company_data"])
        return
    
    # 1. Cabeçalho visualmente atraente (sóbrio)
    st.markdown("""
    <div style='background-color: #F0F4F7; padding: 25px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #1B2D45;'>
        <h1 style='color: #1B2D45; margin-top: 0;'>Pesquisa Executiva de Mercado</h1>
        <p style='color: #555555;'>Utilize a ferramenta de busca e filtragem para obter dados estratégicos sobre empresas e tendências de mercado.</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Container Centralizado para a Busca
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.subheader("Busca Rápida de Empresas")

    all_phases = sorted(list(set(comp.get('fase_da_startup', 'N/A') for comp in st.session_state.get('all_companies_data', []))))
    all_phases.insert(0, "Todas as Fases")

    col1, col2 = st.columns([3, 1])
    
    query = col1.text_input("Pesquisar", placeholder="Digite nome, setor, ou solução...", label_visibility="collapsed")
    selected_phase = col2.selectbox("Filtrar por Fase:", all_phases)

    if st.button("Executar Busca", use_container_width=True, key="home_search_button"):
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
            
    st.markdown('</div>', unsafe_allow_html=True) 

    # 3. Exibição dos Resultados (COM LIMITE DE 5)
    results = st.session_state.get("home_page_search_results", [])
    
    # --- CORREÇÃO DO ERRO NoneType ---
    if results is None:
        results = []
    # ----------------------------------
    
    total_found = len(results) # AGORA É SEGURO
    limited_results = results[:5] 
    
    if limited_results:
        # Mensagem mais informativa
        if total_found > 5:
            st.warning(f"Foram encontradas {total_found} empresas. Exibindo os 5 resultados mais relevantes. Use a 'Lista de Empresas' para ver todos.")
        else:
            st.success(f"Encontramos {total_found} empresas:")
            
        # Novo visual: Cards de Resultado 
        st.markdown("---")
        st.markdown("#### Principais Resultados")
        
        # Estrutura para os cards
        cols = st.columns(len(limited_results))
        
        for i, company in enumerate(limited_results):
            # Usando markdown para simular um card compacto em cada coluna
            cols[i].markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 3px solid #FFC300; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h5 style="color: #1B2D45; margin-top: 0; margin-bottom: 5px; font-weight: 600;">{company.get('nome_da_empresa', 'N/A')}</h5>
                <p style="font-size: 12px; color: #555;">Setor: <strong>{company.get('setor_principal', 'N/A')}</strong></p>
                <p style="font-size: 12px; color: #555;">Fase: <strong>{company.get('fase_da_startup', 'N/A')}</strong></p>
            </div>
            """, unsafe_allow_html=True)

        # Seleção e Botão fora do loop de cards
        st.markdown("---")
        st.markdown("#### Selecionar para Análise Completa")

        col_select, col_button = st.columns([3, 1])
        
        # Usa os resultados limitados para seleção
        with col_select:
            selected_company_name = st.selectbox("Selecione uma empresa", [e['nome_da_empresa'] for e in limited_results], label_visibility="collapsed", key="home_select_company")
        
        selected_company = next((e for e in results if e['nome_da_empresa']==selected_company_name), None)
        if selected_company:
            st.session_state["selected_company_data"] = selected_company
            # Botão sem emoji
            if col_button.button("Ver Dashboard", use_container_width=True, key="home_view_dashboard"):
                st.session_state["show_dashboard"] = True
                st.rerun()
                
    elif results == [] and st.session_state.get("home_page_search_results") is not None:
        st.info("Nenhuma empresa encontrada com estes critérios. Tente refinar a busca.")

# ------------------- LISTAR EMPRESAS (MOSTRA TODOS POR PADRÃO) -------------------
def list_companies_page():
    if st.session_state["show_dashboard"]:
        display_dashboard(st.session_state["selected_company_data"])
        return

    st.header("Lista Completa de Empresas")
    st.caption("Filtre e explore a base de dados completa.")

    # TENTA CARREGAR DADOS SE AINDA NÃO EXISTIREM
    if st.session_state["all_companies_data"] is None:
        st.info("Carregando empresas...")
        headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
        try:
            response = requests.get(f"{API_URL}/companies", headers=headers)
            response.raise_for_status()
            st.session_state["all_companies_data"] = response.json()
            st.session_state["filtered_results"] = st.session_state["all_companies_data"]
            st.rerun()
        except requests.exceptions.RequestException as err:
            st.error(f"Erro ao buscar empresas: {err}")
            return
    
    if st.session_state["all_companies_data"] is None:
        return

    current_list_to_display = st.session_state.get("filtered_results", st.session_state["all_companies_data"])
    if current_list_to_display is None:
        current_list_to_display = st.session_state["all_companies_data"]

    all_phases = sorted(list(set(comp.get('fase_da_startup', 'N/A') for comp in st.session_state["all_companies_data"])))
    all_phases.insert(0, "Todas as Fases")

    with st.expander("Filtrar empresas", expanded=False):
        col1, col2 = st.columns([3, 1])
        search_term = col1.text_input("Pesquisar por nome, setor ou solução:", placeholder="Digite para filtrar...")
        selected_phase = col2.selectbox("Filtrar por Fase:", all_phases)
        
        if st.button("Aplicar Filtros"):
            filtered_companies_temp = st.session_state["all_companies_data"]
            if selected_phase != "Todas as Fases":
                filtered_companies_temp = [c for c in filtered_companies_temp if c.get('fase_da_startup')==selected_phase]
            if search_term:
                filtered_companies_temp = [c for c in filtered_companies_temp if search_term.lower() in str(c.get('nome_da_empresa','')).lower() 
                                    or search_term.lower() in str(c.get('setor_principal','')).lower() 
                                    or search_term.lower() in str(c.get('solucao','')).lower()]
            st.session_state["filtered_results"] = filtered_companies_temp
            st.rerun() 

    if current_list_to_display:
        st.success(f"Exibindo {len(current_list_to_display)} empresas:")
        df_filtered = pd.DataFrame(current_list_to_display)
        # Mantém a exibição em tabela aqui para a lista completa
        st.dataframe(df_filtered[['nome_da_empresa', 'setor_principal', 'fase_da_startup']], use_container_width=True)

        st.markdown("---")
        col_select, col_button = st.columns([3, 1])
        with col_select:
            selected_company_name = st.selectbox("Selecione uma empresa para ver o dashboard", [c['nome_da_empresa'] for c in current_list_to_display], label_visibility="collapsed")
        
        selected_company = next((c for c in current_list_to_display if c['nome_da_empresa']==selected_company_name), None)
        if selected_company:
            st.session_state["selected_company_data"] = selected_company
            if col_button.button("Visualizar Dashboard da Empresa"):
                st.session_state["show_dashboard"] = True
                st.rerun()
    else:
        st.info("Nenhuma empresa encontrada com estes filtros.")

# ------------------- LOGIN / REGISTRO -------------------
def login_form():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            response = requests.post(f"{API_URL}/token", data={"username": email, "password": password}, headers={"Content-Type":"application/x-www-form-urlencoded"})
            if response.status_code == 200:
                st.session_state["token"] = response.json()["access_token"]
                st.query_params["token"] = st.session_state["token"]
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")
    st.markdown('</div>', unsafe_allow_html=True) 

def register_form():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.header("Criar Conta")
    with st.form("register_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        if st.form_submit_button("Cadastrar"):
            response = requests.post(f"{API_URL}/register", json={"email": email, "password": password})
            if response.status_code == 200:
                st.success("Conta criada com sucesso! Faça login.")
                st.session_state["form_type"] = "login"
                st.rerun()
            else:
                st.error(f"Erro: {response.json().get('detail','Erro desconhecido')}")
    st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()

# ------------------- MAIN -------------------
def main():
    # 1. INJEÇÃO DE CSS GLOBAL (CORPORATIVO E MENU AJUSTADO)
    st.markdown("""
    <style>
    /* Paleta: Azul Marinho (#1B2D45), Destaque Dourado/Cítrico (#FFC300) */
    
    /* 1. Estilo de Fundo Geral */
    .stApp > div:first-child {
        background-color: #F8F9FA; 
    }

    /* 2. Login/Registro */
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 30px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 0 25px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .login-container h2 {
        color: #1B2D45; 
        margin-bottom: 20px;
        font-weight: 600;
    }
    
    /* 3. Estilo da Busca na Home Page */
    .search-container {
        padding: 30px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
        text-align: center;
    }

    /* 4. Botões Primários */
    .stButton>button {
        background-color: #1B2D45; 
        color: white;
        border-radius: 5px;
        font-weight: bold;
        letter-spacing: 0.5px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #2C3E50; 
        color: white;
    }
    
    /* 5. Streamlit DataFrames */
    .stDataFrame {
        border: 1px solid #DCE0E6; 
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* 6. Estilo da Sidebar e Menu Principal */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #ffffff !important; 
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    }

    /* Ajustes Finos do option_menu (classes do streamlit) */
    .st-emotion-cache-1g8x7pt { 
        padding: 0 10px; 
    }
    .st-emotion-cache-12fmw3r { 
        font-weight: 500;
        font-size: 16px;
        color: #555555;
        padding: 10px 15px;
        border-radius: 6px;
        transition: background-color 0.2s, color 0.2s;
    }
    .st-emotion-cache-12fmw3r.st-emotion-cache-1whtkcc { 
        background-color: #FFC300 !important; 
        color: #1B2D45 !important; 
        font-weight: 700 !important;
        border-left: 4px solid #1B2D45; 
        margin-left: -15px; 
    }
    .st-emotion-cache-12fmw3r:hover {
        background-color: #F0F4F7;
        color: #1B2D45;
    }
    .st-emotion-cache-10o18g0 { 
        font-size: 14px;
        color: #8C99A6;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding-left: 15px;
        margin-top: 15px;
    }

    /* 7. Remove elementos nativos */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.get("token"):
        if st.session_state["all_companies_data"] is None:
            headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
            try:
                response = requests.get(f"{API_URL}/companies", headers=headers)
                response.raise_for_status()
                st.session_state["all_companies_data"] = response.json()
            except requests.exceptions.RequestException as err:
                st.error(f"Erro ao carregar empresas: {err}")

        with st.sidebar:
            st.markdown(f"""
                <div style='text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid #DCE0E6;'>
                    <h1 style='color: #1B2D45; font-size: 24px; margin: 0;'>Busca Pro</h1>
                    <p style='color: #8C99A6; font-size: 12px; margin: 0;'>Acesso Gerencial</p>
                </div>
                <br>
            """, unsafe_allow_html=True)
            
            # Navegação (Sem estilos in-line)
            escolha = option_menu(
                menu_title="Menu Principal", 
                options=["Home","Listar Empresas","Sair"], 
                icons=["house-door", "building", "box-arrow-right"], 
                menu_icon="cast", 
                default_index=0
            )

        if escolha=="Home":
            home_page()
        elif escolha=="Listar Empresas":
            list_companies_page()
        elif escolha=="Sair":
            logout()
    else:
        if st.session_state["form_type"]=="register":
            register_form()
            st.button("Já tem conta? Login", on_click=lambda: st.session_state.update({"form_type": "login"}), key="switch_to_login")
        else:
            login_form()
            st.button("Criar nova conta", on_click=lambda: st.session_state.update({"form_type": "register"}), key="switch_to_register")

if __name__=="__main__":
    main()