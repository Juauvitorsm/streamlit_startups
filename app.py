import streamlit as st
import requests
import pandas as pd
from config import API_URL 
import base64 
import os 

st.set_page_config(page_title="Busca de Empresas", page_icon="🏢", layout="wide")

params = st.query_params

# Inicializa estado da sessão e define a página inicial
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
if "current_page" not in st.session_state: 
    st.session_state["current_page"] = "Home"


# --- FUNÇÃO DE CALLBACK PARA O BOTÃO POR LINHA ---
def view_company_dashboard(company_data):
    """Salva os dados da empresa e ativa a visualização do dashboard."""
    st.session_state["selected_company_data"] = company_data
    st.session_state["show_dashboard"] = True
    st.rerun()

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

    # Corrigido o botão de retorno para garantir que o estado de exibição seja limpo
    if st.button("<- Voltar para a Lista de Empresas", key="dashboard_back_button"):
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
    
    # 1. Cabeçalho visualmente atraente (AGORA COM SOMBRA FORTE E FUNDO CLARO)
    st.markdown("""
    <div class="header-banner">
        <h1 class="main-title">Pesquisa de Empresas</h1>
        <p class="subtitle">Obtenha dados estratégicos e tendências de empresas rapidamente.</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Container Centralizado para a Busca (Harmonizado)
    st.markdown('<h2 class="search-section-title">Busca Rápida de Empresas</h2>', unsafe_allow_html=True)

    # CORREÇÃO DO ERRO NoneType: Garantir que company_data_safe é sempre uma lista
    company_data_safe = st.session_state.get('all_companies_data')
    if company_data_safe is None:
        company_data_safe = []
        
    all_phases = sorted(list(set(comp.get('fase_da_startup', 'N/A') for comp in company_data_safe)))
    all_phases.insert(0, "Todas as Fases")

    # Contêiner customizado para aplicar sombra e bordas
    # Criamos o formulário aqui para agrupar os inputs e o botão de submit
    with st.form("quick_search_form"): 
        
        # Campos de input principal
        query_main = st.text_input("Pesquisar", placeholder="Digite nome, setor, ou solução...", label_visibility="collapsed", key="home_query_input_main")
        
        # Campos de filtro na mesma linha
        col_query_filter, col_phase = st.columns([3, 1])
        
        with col_query_filter:
            query_filter = st.text_input("Filtro de Texto", placeholder="Filtro secundário (opcional)...", label_visibility="collapsed", key="home_query_input_filter")
            
        with col_phase:
            selected_phase = st.selectbox("Fase:", all_phases, label_visibility="collapsed", key="home_phase_select") 
        
        # Botão de busca harmonizado (Azul Marinho)
        if st.form_submit_button("Executar Busca", use_container_width=True, type="primary"): 
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            # Lógica de busca
            try:
                # COMBINEI AS BUSCAS AQUI, SE PRECISO
                params = {"query": query_main + " " + query_filter} 
                if selected_phase != "Todas as Fases":
                    params["fase"] = selected_phase
                response = requests.get(f"{API_URL}/optimized_search", params=params, headers=headers)
                response.raise_for_status()
                st.session_state["home_page_search_results"] = response.json()
                st.rerun()
            except requests.exceptions.RequestException as err:
                st.error(f"Erro: {err}")
            
    # 3. Exibição dos Resultados (COM LIMITE DE 5)
    
    # === CORREÇÃO: DEFININDO AS VARIÁVEIS AQUI ===
    results = st.session_state.get("home_page_search_results", [])
    
    if results is None:
        results = []
    
    total_found = len(results)
    limited_results = results[:5] 
    # ===============================================

    if limited_results:
        st.markdown("---")
        # Mensagem mais informativa
        if total_found > 5:
            st.warning(f"Foram encontradas {total_found} empresas. Exibindo os 5 resultados mais relevantes. Use a 'Lista de Empresas' para ver todos.")
        else:
            st.success(f"Encontramos {total_found} empresas:")
            
        # Novo visual: Cards de Resultado 
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
            if col_button.button("Ver Dashboard", use_container_width=True, key="home_view_dashboard", type="secondary"): 
                st.session_state["show_dashboard"] = True
                st.rerun()
                
    elif results == [] and st.session_state.get("home_page_search_results") is not None:
        st.info("Nenhuma empresa encontrada com estes critérios. Tente refinar a busca.")

# ------------------- LISTAR EMPRESAS (MOSTRA TODOS POR PADRÃO) -------------------
def list_companies_page():
    # CHAVE 1: SE O DASHBOARD ESTIVER ATIVO, EXIBE ELE E ENCERRA A FUNÇÃO
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
        
        if st.button("Aplicar Filtros", type="primary"): 
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
        
        # --- COLUNAS E DADOS DA TABELA (AJUSTADO PARA 6 COLUNAS) ---
        cols_config = {
            'Nome da Empresa': 3,
            'Setor Principal': 2,
            'Fase da Startup': 2,
            'Colaboradores': 2,
            'Investimento?': 2,
            'Ação': 1 # Nova coluna para o botão
        }
        cols_to_display = list(cols_config.keys())
        col_widths = list(cols_config.values())

        # 1. CABEÇALHO CUSTOMIZADO
        header_cols = st.columns(col_widths)
        for i, header in enumerate(cols_to_display):
            header_cols[i].markdown(f'<div class="custom-table-header">{header}</div>', unsafe_allow_html=True)
        
        # 2. LINHAS DE DADOS CUSTOMIZADAS COM BOTÃO
        for index, company in enumerate(current_list_to_display):
            
            # Formata os dados para as colunas
            row_data = [
                company.get('nome_da_empresa'),
                company.get('setor_principal'),
                company.get('fase_da_startup'),
                company.get('colaboradores'),
                company.get('recebeu_investimento')
            ]
            
            # Define o estilo da linha (Zebra)
            row_class = "custom-table-row-even" if index % 2 == 0 else "custom-table-row-odd"
            
            # Renderiza as 6 colunas
            row_cols = st.columns(col_widths)
            
            # Renderiza as 5 colunas de dados
            for i, data in enumerate(row_data):
                row_cols[i].markdown(
                    f'<div class="{row_class} custom-table-cell">{data if data else "N/A"}</div>', 
                    unsafe_allow_html=True
                )
            
            # Renderiza a 6ª coluna: o BOTÃO "Detalhes"
            with row_cols[5]:
                st.button(
                    'Detalhes', # Texto do botão
                    key=f"view_dash_{company.get('id', index)}", 
                    on_click=view_company_dashboard, 
                    args=(company,),
                    use_container_width=True
                )
        
    else:
        st.info("Nenhuma empresa encontrada com estes filtros.")

# ------------------- LOGIN / REGISTRO -------------------
def login_form():
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="seu.email@mti.com")
        password = st.text_input("Senha", type="password", placeholder="Insira sua senha")
        if st.form_submit_button("Entrar", type="primary"):
            response = requests.post(f"{API_URL}/token", data={"username": email, "password": password}, headers={"Content-Type":"application/x-www-form-urlencoded"})
            if response.status_code == 200:
                st.session_state["token"] = response.json()["access_token"]
                st.query_params["token"] = st.session_state["token"]
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")
    
    if st.button("Criar nova conta", on_click=lambda: st.session_state.update({"form_type": "register"}), key="switch_to_register_login", use_container_width=True):
        st.rerun()

def register_form():
    st.header("Criar Conta")
    with st.form("register_form"):
        email = st.text_input("E-mail", placeholder="seu.email@mti.com")
        password = st.text_input("Senha", type="password", placeholder="Sua senha deve conter letras e pelo menos dois números")
        if st.form_submit_button("Cadastrar", type="primary"):
            response = requests.post(f"{API_URL}/register", json={"email": email, "password": password})
            if response.status_code == 200:
                st.success("Conta criada com sucesso! Faça login.")
                st.session_state["form_type"] = "login"
                st.rerun()
            else:
                st.error(f"Erro: {response.json().get('detail','Erro desconhecido')}")
    
    if st.button("Já tem conta? Login", on_click=lambda: st.session_state.update({"form_type": "login"}), key="switch_to_login_register", use_container_width=True):
        st.rerun()

def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()

# --- FUNÇÃO DO NOVO MENU CUSTOMIZADO E LIMPO (Final) ---
def custom_sidebar_menu():
    
    menu_items = [
        {"label": '<i class="bi bi-house-door-fill"></i> Home', "page": "Home"},
        {"label": '<i class="bi bi-building-fill"></i> Listar Empresas', "page": "Listar Empresas"},
        {"label": '<i class="bi bi-box-arrow-right"></i> Sair', "page": "Sair"},
    ]
    
    # 1. Título do Menu
    st.markdown("""
        <div class="menu-title-container">MENU PRINCIPAL</div>
    """, unsafe_allow_html=True)
    
    # Função de navegação agora atribui estado e força o rerun
    def set_page(page_name):
        st.session_state["current_page"] = page_name
        st.rerun()

    # 2. Renderiza os botões (itens de menu)
    for item in menu_items:
        is_selected = st.session_state["current_page"] == item["page"]
        
        # Renderiza o botão Streamlit real (invisível e funcional)
        if st.button(
            ' ', # Label vazio para não aparecer na tela
            key=f"nav_button_{item['page']}", 
            use_container_width=True, 
            on_click=set_page, 
            args=(item['page'],)
        ):
            pass 
        
        # 3. Renderiza a APARÊNCIA ESTILIZADA (MARKDOWN)
        style_class = "menu-item-selected" if is_selected else "menu-item-unselected"
        st.markdown(
            f'''
            <div id="item_{item['page']}" class="{style_class} menu-item-overlay">
                {item['label']}
            </div>
            ''', unsafe_allow_html=True
        )


# ------------------- MAIN -------------------
def main():
    # Tenta ler e codificar a logo em Base64
    logo_base64 = ""
    logo_filename = "logo.png"
    if os.path.exists(logo_filename):
        try:
            with open(logo_filename, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            # Em produção, você pode querer remover este aviso
            st.warning(f"Não foi possível ler a imagem '{logo_filename}': {e}")


    # 1. INJEÇÃO DE CSS GLOBAL (CORPORATIVO E MENU CUSTOMIZADO)
    st.markdown("""
    <style>
    /* Paleta: Azul Marinho (#1B2D45), Destaque Dourado/Cítrico (#FFC300) */
    
    /* Importa Bootstrap Icons */
    @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

    /* Oculta o aviso de "Calling st.rerun() within a callback is a no-op." */
    div[data-testid="stStatusWidget"], .stAlert {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        position: absolute !important;
    }
    .stApp > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:has(.stAlert) {
         display: none !important;
    }


    /* 1. Estilo de Fundo Geral */
    .stApp > div:first-child {
        background-color: #F8F9FA; 
    }

    /* 2. LOGO NO CANTO SUPERIOR DIREITO (FIXO APÓS LOGIN) */
    .logo-container {
        position: fixed;
        top: 10px; 
        right: 15px; 
        z-index: 1000;
        width: 150px; 
        text-align: right;
    }
    .logo-container img {
        max-width: 100%;
        height: auto;
    }

    /* 2b. LOGO CENTRALIZADA (PRÉ-LOGIN) */
    .logo-centered {
        display: block;
        width: 200px; /* Um pouco maior para destaque na tela de login */
        margin: 50px auto 30px auto; /* Centraliza horizontalmente e adiciona margem */
    }
    
    /* 3. Estilo da Sidebar e Menu CUSTOMIZADO (FORÇANDO AZUL MARINHO) */
    .css-1d391kg, .css-1lcbmhc, [data-testid="stSidebarContent"] { 
        background-color: #1B2D45 !important; /* Fundo AZUL MARINHO FORÇADO */
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2); 
        color: #F8F9FA; 
        padding-top: 25px; 
    }
    
    /* ESTILIZANDO OS BOTÕES STREAMLIT REAIS */

    /* Alvo: O contêiner pai do botão Streamlit, que força o layout */
    div[data-testid="stSidebarContent"] .stButton {
        position: relative; 
        z-index: 900;
        height: 40px; /* Altura da área de clique (para evitar quebra) */
        margin-bottom: 10px !important;
        margin-left: 15px;
        margin-right: 15px;
        width: calc(100% - 30px); /* Ocupa a largura total menos as margens */
    }

    /* CHAVE 1: Estilizando o Botão Real (para ser transparente e clicável) */
    div[data-testid="stSidebarContent"] .stButton > button {
        /* Torna o botão Streamlit real totalmente transparente e clicável */
        background-color: transparent !important;
        border: none !important;
        color: rgba(0, 0, 0, 0) !important; /* Texto do botão invisível */
        position: absolute !important;
        top: 0px !important; 
        left: 0;
        right: 0;
        height: 100% !important; 
        z-index: 999; /* Garante que o botão (área de clique) fique por cima */
        border-radius: 8px !important;
        /* Limpa margens e paddings nativos */
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    
    /* CHAVE 2: Estilo da APARÊNCIA VISUAL (MARKDOWN) */
    .menu-item-overlay {
        font-size: 17px;
        font-weight: 500;
        padding: 12px 15px;
        border-radius: 8px;
        transition: background-color 0.2s, color 0.2s, box-shadow 0.2s;
        display: flex;
        align-items: center;
        gap: 10px;
        white-space: nowrap; 
        /* Puxa o estilo para cima do botão transparente */
        margin: -40px 15px 0 15px; 
        position: relative;
        z-index: 800; 
    }
    
    /* Itens NÃO SELECIONADOS (Visual) */
    .menu-item-unselected {
        color: #F8F9FA; /* Texto BRANCO */
        background-color: transparent;
    }
    .menu-item-unselected:hover {
        background-color: rgba(255, 255, 255, 0.1); 
        color: #FFC300; 
    }

    /* Itens SELECIONADOS (Visual Dourado) */
    .menu-item-selected {
        background-color: #FFC300 !important; /* Fundo DOURADO */
        color: #1B2D45 !important; /* Texto AZUL MARINHO */
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); 
    }
    .menu-item-selected:hover {
        background-color: #ff9f00 !important; /* Dourado escuro no hover */
        color: #1B2D45 !important;
    }

    /* Título do Menu Principal */
    .menu-title-container {
        color: #DCE0E6; 
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
        padding: 0 15px 8px 15px; 
        margin-bottom: 15px;
        margin-top: 20px; 
        font-weight: 600;
    }
    
    /* Estilos para Ícones */
    .bi {
        font-size: 20px;
        margin-right: 10px; 
        vertical-align: middle;
    }
    
    /* OUTROS ESTILOS DA PÁGINA (HOME PAGE) */

    /* Banner de Cabeçalho - AGORA COM SOMBRA DE ELEVAÇÃO */
    .header-banner {
        background: #ffffff !important; /* Fundo Branco Sólido Forçado */
        padding: 40px 30px; 
        border-radius: 15px; 
        margin-bottom: 40px;
        border-left: 8px solid #1B2D45; 
        /* CHAVE DO VISUAL: Sombra de elevação mais forte e moderna */
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.18); 
        display: flex; 
        flex-direction: column;
        justify-content: center;
        min-height: 150px;
    }
    .main-title {
        color: #1B2D45; 
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 42px; 
        font-weight: 800; 
        letter-spacing: -1px; 
    }
    .subtitle {
        color: #4A5568; 
        font-size: 19px; 
        line-height: 1.6;
        max-width: 700px; 
    }

    /* Seção de Busca */
    .search-section-title {
        color: #1B2D45; 
        font-size: 26px; 
        font-weight: 600;
        margin-top: 40px; 
        margin-bottom: 25px;
        padding-left: 5px; 
        border-bottom: 2px solid #DCE0E6; 
        padding-bottom: 10px;
    }

    /* Contêiner do Formulário de Busca */
    div[data-testid="stForm"] > div:first-child {
        padding: 30px;
        background-color: #F8F9FA; /* Fundo muito leve */
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); /* Sombra suave para a seção */
        margin-bottom: 40px;
        border: 1px solid #E0E4E8; /* Borda mais discreta */
    }

    /* Estilo dos Inputs de Texto (text_input) */
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 8px; 
        border: 1px solid #CBD5E0; 
        padding: 12px 15px; 
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); 
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #1B2D45; 
        box-shadow: 0 0 0 2px rgba(27, 45, 69, 0.2); 
        outline: none;
    }

    /* Estilo dos Selectbox (selectbox) */
    div[data-testid="stSelectbox"] > div > button {
        border-radius: 8px;
        border: 1px solid #CBD5E0;
        padding: 10px 15px; 
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
        height: auto; 
    }
    div[data-testid="stSelectbox"] > div > button:focus {
        border-color: #1B2D45;
        box-shadow: 0 0 0 2px rgba(27, 45, 69, 0.2);
        outline: none;
    }
    /* Estilo do dropdown arrow */
    div[data-testid="stSelectbox"] .st-bh, div[data-testid="stSelectbox"] .st-bv { 
        color: #1B2D45 !important;
    }
    
    /* Botão Primário (Executar Busca) - AZUL MARINHO */
    button[data-testid="stFormSubmitButton"] {
        background-color: #1B2D45 !important; 
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 25px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(27, 45, 69, 0.2);
        transition: all 0.2s ease-in-out;
        margin-top: 25px; 
    }
    /* MIRA O ELEMENTO INTERNO DO BOTÃO (O BOTÃO REAL) PARA ANULAR O TEMA VERMELHO */
    button[data-testid^="stBaseButton-primaryFormSubmit"] {
        background-color: #1B2D45 !important; 
        border-color: #1B2D45 !important;
    }

    button[data-testid="stFormSubmitButton"]:hover {
        background-color: #0F1E33 !important; 
        box-shadow: 0 6px 15px rgba(27, 45, 69, 0.3);
        transform: translateY(-2px); 
    }
    button[data-testid^="stBaseButton-primaryFormSubmit"]:hover {
        background-color: #0F1E33 !important; 
        border-color: #0F1E33 !important;
    }

    /* Botão Secundário (Ver Dashboard) */
    button[data-testid="stSecondaryButton"] {
        background-color: #F0F4F7 !important; 
        color: #1B2D45 !important; 
        border: 1px solid #DCE0E6 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
    }
    button[data-testid="stSecondaryButton"]:hover {
        background-color: #DCE0E6 !important; 
        border-color: #BCC4CD !important;
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    }
    
    .login-container { max-width: 400px; margin: 50px auto; padding: 30px; border-radius: 10px; background-color: #ffffff; box-shadow: 0 0 25px rgba(0, 0, 0, 0.1); text-align: center; }
    
    /* Esconde o cabeçalho padrão Streamlit */
    #MainMenu, footer, header {visibility: hidden;}

    
    /* --- ESTILOS PARA TABELA CUSTOMIZADA --- */
    
    /* Container Principal */
    div[data-testid="stHorizontalBlock"] {
        padding: 0px !important;
    }

    /* CABEÇALHO CUSTOMIZADO */
    .custom-table-header {
        background-color: #1B2D45; /* Azul Marinho */
        color: white;
        font-weight: 700; 
        font-size: 15px;
        padding: 12px 5px; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 3px solid #FFC300; /* Destaque dourado */
        margin: 0;
        text-align: left;
    }

    /* Estilo das Células de Dados */
    .custom-table-cell {
        padding: 10px 5px; 
        font-size: 14px;
        color: #333333;
        min-height: 40px;
        display: flex;
        align-items: center;
        border: none;
    }

    /* Fundo da Linha Ímpar (Branco) */
    .custom-table-row-odd .custom-table-cell {
        background-color: white; 
    }

    /* Fundo da Linha Par (Zebra) */
    .custom-table-row-even .custom-table-cell {
        background-color: #F0F4F7; /* Azul muito claro */
    }
    
    /* Hover Efeito: Usamos o seletor mais próximo para o bloco de colunas */
    div[data-testid^="stHorizontalBlock"]:has(.custom-table-row-odd):hover .custom-table-cell,
    div[data-testid^="stHorizontalBlock"]:has(.custom-table-row-even):hover .custom-table-cell {
        background-color: #DCE0E6 !important; 
        /* Borda vertical Dourada na esquerda, aplicada apenas na primeira célula se quisermos */
        box-shadow: inset 4px 0 0 #FFC300;
        cursor: pointer;
    }

    /* Ajuste para o botão "Detalhes" para ficar menor e centralizado na célula */
    div[data-testid="stHorizontalBlock"] > div > div > div > button {
        padding: 6px 10px !important; /* Ajusta o padding para um botão menor */
        font-size: 13px !important; /* Tamanho da fonte menor */
        background-color: #1B2D45 !important; /* Azul Marinho */
        border-color: #1B2D45 !important;
        color: white !important;
        border-radius: 5px !important; /* Borda levemente arredondada */
        transition: background-color 0.2s, transform 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        display: block; /* Garante que o botão ocupe sua largura e se centralize */
        margin: auto; /* Centraliza o botão dentro da célula */
    }
    div[data-testid="stHorizontalBlock"] > div > div > div > button:hover {
        background-color: #0F1E33 !important; /* Azul Marinho mais escuro no hover */
        transform: translateY(-1px); /* Pequeno efeito de elevação */
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    </style>
    """, unsafe_allow_html=True)

    # 4. Inserção da Logo no corpo principal
    if logo_base64:
        if st.session_state.get("token"):
            # POSICIONAMENTO FIXO (PÓS-LOGIN)
            st.markdown(
                f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{logo_base64}" alt="Logo da Empresa">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # POSICIONAMENTO CENTRALIZADO (PRÉ-LOGIN)
            # Renderiza a logo centralizada acima do contêiner de login
            st.markdown(
                f"""
                <img src="data:image/png;base64,{logo_base64}" alt="Logo da Empresa" class="logo-centered">
                """,
                unsafe_allow_html=True
            )


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
            
            custom_sidebar_menu() 

        # Lógica de navegação baseada no estado da sessão
        if st.session_state["current_page"]=="Home":
            home_page()
        elif st.session_state["current_page"]=="Listar Empresas":
            list_companies_page()
        elif st.session_state["current_page"]=="Sair":
            logout()
    else:
        # Quando deslogado, a tela de login/registro aparece após a logo centralizada
        col_center = st.columns([1, 2, 1])
        with col_center[1]:

            if st.session_state["form_type"]=="register":
                register_form()
            else:
                login_form()
            st.markdown('</div>', unsafe_allow_html=True)

if __name__=="__main__":
    main()