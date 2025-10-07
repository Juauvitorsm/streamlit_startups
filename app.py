import streamlit as st
import requests
import pandas as pd
from config import API_URL  # Assumindo que config.py com API_URL existe
import base64  
import os  
# --- IMPORTAÇÕES DA AGGRID ---
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode
# ----------------------------

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
    # Garante que, ao iniciar, não há filtro aplicado
    st.session_state["filtered_results"] = None
if "current_page" not in st.session_state: 
    st.session_state["current_page"] = "Home"
if "aggrid_selection" not in st.session_state:
    # Usado para evitar reruns infinitos na seleção de linha do AgGrid
    st.session_state["aggrid_selection"] = None


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
        <h1 class="main-title">Pesquisa de empresas</h1>
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

# ------------------- LISTAR EMPRESAS (COM SELEÇÃO E AÇÃO) -------------------
def list_companies_page():
    # CHAVE 1: SE O DASHBOARD ESTIVER ATIVO, EXIBE ELE E ENCERRA A FUNÇÃO
    if st.session_state["show_dashboard"]:
        display_dashboard(st.session_state["selected_company_data"])
        return

    st.header("Lista Completa de Empresas")
    st.caption("Filtre, ordene e explore a base de dados completa.")
    
    # --- INJEÇÃO DE CSS DE ALTA PRIORIDADE PARA AGGRID (PARA MANTER O ESTILO) ---
    st.markdown("""
    <style>
        /* 1. Remove Fundo e Borda de Foco/Seleção em Células/Linhas */
        
        .ag-cell-focus {
            background-color: transparent !important; /* Herda o fundo da linha (zebra) */
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Linha Selecionada (Substituindo o padrão AgGrid) */
        .ag-row-selected {
            background-color: #DCE0E6 !important; /* Cinza claro suave */
            box-shadow: inset 4px 0 0 #FFC300 !important; /* Borda amarela */
        }
        
        /* Linha em Hover (Substituindo o padrão AgGrid) */
        .ag-row-hover {
            background-color: #DCE0E6 !important; /* Cinza claro para o hover */
        }
        
        .ag-row-selected.ag-row-hover {
            background-color: #DCE0E6 !important; 
        }
        
        /* 2. Estilo do Header e Zebra */
        .ag-header-cell-label {
            color: white !important;
            font-weight: 700; 
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .ag-header-cell, .ag-header-container {
            background-color: #1B2D45 !important; /* Azul Marinho */
            border-bottom: 3px solid #FFC300 !important; /* Destaque dourado */
        }
        .ag-cell {
            color: #333333 !important;
            font-size: 14px;
        }
        .ag-row-odd {
            background-color: white !important;
        }
        .ag-row-even {
            background-color: #F0F4F7 !important; /* Azul muito claro */
        }
        .ag-root, .ag-grid-body {
            border: none !important;
        }
        
        /* 3. Otimiza a aparência do botão customizado para o tema */
        div[data-testid="stCustomCellRenderer"] button {
            background-color: #1B2D45 !important;
            color: white !important;
            border: none !important;
        }

    </style>
    """, unsafe_allow_html=True)
    # ------------------------------------------------------------------------------------

    # TENTA CARREGAR DADOS SE AINDA NÃO EXISTIREM
    if st.session_state["all_companies_data"] is None:
        st.info("Carregando empresas...")
        headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
        try:
            response = requests.get(f"{API_URL}/companies", headers=headers)
            response.raise_for_status()
            st.session_state["all_companies_data"] = response.json()
        except requests.exceptions.RequestException as err:
            st.error(f"Erro ao buscar empresas: {err}")
            return
    
    if st.session_state["all_companies_data"] is None:
        return

    companies_data = st.session_state["all_companies_data"]
    
    # === LÓGICA DE EXIBIÇÃO: MOSTRAR TUDO SE NÃO HOUVER FILTRO ATIVO ===
    # Pega 'filtered_results' se existir, caso contrário, usa a lista completa.
    current_list_to_display = st.session_state.get("filtered_results")
    
    if current_list_to_display is None:
        current_list_to_display = companies_data

    # Cria DataFrame para filtros de formulário e exibição
    df = pd.DataFrame(companies_data)
    df_display = pd.DataFrame(current_list_to_display)
    
    if df.empty:
         st.info("Nenhuma empresa encontrada na base de dados.")
         return
    
    # ------------------- LÓGICA DE FILTROS NA SIDEBAR/EXPANDER -------------------
    all_phases = sorted(list(set(df['fase_da_startup'].unique())))
    all_phases.insert(0, "Todas as Fases")

    with st.expander("Filtrar por empresas", expanded=False):
        col1, col2 = st.columns([3, 1])
        search_term = col1.text_input("Pesquisar por nome, setor ou solução:", placeholder="Digite para filtrar...")
        selected_phase = col2.selectbox("Filtrar por Fase:", all_phases)
        
        col_apply, col_clear = st.columns([1, 1])

        if col_apply.button("Aplicar Filtros", type="primary"): 
            filtered_df = df.copy()
            
            if selected_phase != "Todas as Fases":
                filtered_df = filtered_df[filtered_df['fase_da_startup'] == selected_phase]
            
            if search_term:
                search_lower = search_term.lower()
                filtered_df = filtered_df[
                    filtered_df['nome_da_empresa'].astype(str).str.lower().str.contains(search_lower, na=False) |
                    filtered_df['setor_principal'].astype(str).str.lower().str.contains(search_lower, na=False) |
                    filtered_df['solucao'].astype(str).str.lower().str.contains(search_lower, na=False)
                ]
            
            st.session_state["filtered_results"] = filtered_df.to_dict('records')
            st.rerun() 
            
        if col_clear.button("Limpar Filtros", type="secondary"):
            st.session_state["filtered_results"] = None
            st.rerun()

    if df_display.empty:
         st.info("Nenhuma empresa encontrada com estes filtros.")
         return
    
    st.success(f"Exibindo {len(df_display)} empresas.")

    # --- CONFIGURAÇÃO DA AGGRID ---

    # 1. Renomear e Selecionar Colunas para exibição
    df_aggrid = df_display.rename(columns={
        'nome_da_empresa': 'Nome da Empresa',
        'setor_principal': 'Setor Principal',
        'fase_da_startup': 'Fase da Startup',
        'colaboradores': 'Colaboradores',
        'recebeu_investimento': 'Investimento?'
    })
    
    COLUMNS_TO_SHOW = ['Nome da Empresa', 'Setor Principal', 'Fase da Startup', 'Colaboradores', 'Investimento?']
    df_aggrid = df_aggrid[COLUMNS_TO_SHOW + ['id']] 

    # 2. Configuração do GridOptionsBuilder
    gb = GridOptionsBuilder.from_dataframe(df_aggrid)
    
    # HABILITA A SELEÇÃO DE LINHA INTEIRA PARA NAVEGAÇÃO
    gb.configure_selection(
        'single', 
        use_checkbox=False, 
        groupSelectsChildren=False,
    )
    
    # Adiciona a coluna de AÇÃO (Botão) - Permanece para o clique direto no botão
    gb.configure_column(
        "Ação",  
        cellRenderer="""
            function(params) {
                var button = document.createElement('button');
                button.innerHTML = 'Detalhes';
                button.style.cssText = 'padding: 6px 10px; cursor: pointer; font-size: 13px; width: 100%; transition: background-color 0.2s, transform 0.2s;';
                
                button.addEventListener('click', function() {
                    Streamlit.setComponentValue({
                        id: params.data.id, 
                        action: 'view_dashboard_button' 
                    });
                });
                return button;
            }
        """,
        minWidth=100,
        maxWidth=120,
        resizable=False,
        sortable=False,
        filter=False,
        wrapText=True
    )
    
    gb.configure_column("id", hide=True) 

    # Configurações gerais da tabela
    gb.configure_grid_options(domLayout='normal') 
    
    # Define o update_mode para capturar as mudanças de seleção
    gridOptions = gb.build()
    gridOptions['enableCellTextSelection'] = True 
    gridOptions['defaultColDef']['resizable'] = True
    gridOptions['defaultColDef']['sortable'] = True
    gridOptions['defaultColDef']['filter'] = True
    
    
    # 3. Renderiza o AgGrid
    grid_response = AgGrid(
        df_aggrid, 
        gridOptions=gridOptions, 
        data_return_mode=DataReturnMode.AS_INPUT, 
        update_mode=GridUpdateMode.MODEL_CHANGED, 
        fit_columns_on_grid_load=True, 
        allow_unsafe_jscode=True, 
        enable_enterprise_modules=False,
        height=400, 
        width='100%',
        reload_data=True,
        key='company_list_aggrid'
    )
    
    # 4. Lógica de Navegação: Pelo Clique no Botão OU Seleção de Linha

    # A. Navegação pelo Botão (Custom Response)
    custom_response = grid_response.get('custom_response')
    
    if custom_response and custom_response.get('action') == 'view_dashboard_button':
        company_id = custom_response.get('id')
        selected_company = next((c for c in companies_data if c.get('id') == company_id), None)
        
        if selected_company:
            view_company_dashboard(selected_company) 

    # B. Navegação pelo Clique na Linha (Selected Rows)
    selected_rows = grid_response.get('selected_rows')
    
    # CORREÇÃO DO VALUERROR: Verifica se a lista de selected_rows existe E se tem dados.
    if isinstance(selected_rows, list) and len(selected_rows) > 0:
        
        selected_row_data = selected_rows[0] 
        company_id = selected_row_data.get('id')
        
        # Evita reruns infinitos verificando se a seleção mudou
        if st.session_state.get('aggrid_selection') != company_id:
            st.session_state['aggrid_selection'] = company_id
            
            selected_company = next((c for c in companies_data if c.get('id') == company_id), None)
            
            if selected_company:
                view_company_dashboard(selected_company)
    
    # Adicionando uma verificação para o caso de o AgGrid retornar um DataFrame (embora raro no modo AS_INPUT)
    elif isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
        # Pega a ID da primeira linha do DataFrame
        company_id = selected_rows['id'].iloc[0]
        
        if st.session_state.get('aggrid_selection') != company_id:
            st.session_state['aggrid_selection'] = company_id
            
            selected_company = next((c for c in companies_data if c.get('id') == company_id), None)
            
            if selected_company:
                view_company_dashboard(selected_company) 


# ------------------- LOGIN / REGISTRO -------------------
def login_form():
    st.header("Login")
    with st.form("login_form"):
        # Labels de texto agora visíveis (cor corrigida no CSS)
        email = st.text_input("E-mail", placeholder="seu.email@mti.com", key="login_email")
        password = st.text_input("Senha", type="password", placeholder="Insira sua senha", key="login_password")
        
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
        # Labels de texto agora visíveis (cor corrigida no CSS)
        email = st.text_input("E-mail", placeholder="seu.email@mti.com", key="register_email")
        password = st.text_input("Senha", type="password", placeholder="Crie uma senha com letras e pelo menos dois números", key="register_password")
        
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
    
    # Note: Usamos o texto puro aqui, e o CSS injeta os ícones.
    menu_items = [
        {"label": 'Home', "page": "Home"}, 
        {"label": 'Listar Empresas', "page": "Listar Empresas"},
        {"label": 'Sair', "page": "Sair"},
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
        
        # O label do botão é APENAS o texto.
        button_label = item['label']
        
        # Renderiza o botão Streamlit nativo. O CSS faz o resto.
        if st.button(
            button_label,
            key=f"nav_button_{item['page']}",
            use_container_width=True,
            on_click=set_page,
            args=(item['page'],)
        ):
            pass

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
            st.warning(f"Não foi possível ler a imagem '{logo_filename}': {e}")


    # 1. INJEÇÃO DE CSS GLOBAL (CORPORATIVO E MENU CUSTOMIZADO)
    st.markdown("""
    <style>
    /* Paleta: Azul Marinho (#1B2D45), Destaque Azul Escuro (#0F1E33), Destaque Dourado (#FFC300) */
    
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
    
    /* --- ESTILIZAÇÃO DO MENU LATERAL (Botões Nativos com Ícones) --- */

    /* Contêiner do botão Streamlit */
    div[data-testid="stSidebarContent"] .stButton {
        margin: 0 15px 10px 15px !important; /* Margem lateral e inferior */
    }

    /* Estilo BASE do botão na sidebar */
    div[data-testid="stSidebarContent"] .stButton > button {
        background-color: transparent !important;
        color: #F8F9FA !important; /* Cor do texto padrão */
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 15px !important; /* Define a altura do item e padding inicial */
        font-size: 17px;
        font-weight: 500;
        text-align: left !important; 
        transition: background-color 0.2s, color 0.2s, box-shadow 0.2s;
        height: auto !important;
        line-height: 1.2 !important;
        box-shadow: none !important;
        position: relative;
        width: 100%; /* Garante que o botão ocupe toda a largura */
        
        /* CORREÇÃO FINAL: Garante que o texto comece na esquerda */
        padding-left: 25px !important; 
        justify-content: flex-start !important;
    }
    
    /* Estilo Hover (para todos os botões não selecionados) */
    div[data-testid="stSidebarContent"] .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #FFC300 !important;
    }

    /* Estilo do Item SELECIONADO (Fundo Amarelo) */
    div[data-testid="stSidebarContent"] .stButton > button[aria-selected="true"],
    div[data-testid="stSidebarContent"] .stButton > button[aria-selected="true"]:hover {
        background-color: #FFC300 !important; /* Fundo DOURADO */
        color: #1B2D45 !important; /* Texto AZUL MARINHO */
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Garante que o texto se alinhe (remove flexbox centralizado) */
    div[data-testid="stSidebarContent"] .stButton > button .subrow {
        align-items: center; 
        justify-content: flex-start !important; /* FORÇA O ALINHAMENTO À ESQUERDA */
        gap: 10px; /* Espaço entre ícone e texto */
        width: 100%; 
    }

    /* ********** INJEÇÃO DE ÍCONES NO CSS ********** */
    
    /* Estilo BASE para todos os pseudo-elementos de ícone */
    div[data-testid="stSidebarContent"] .stButton > button::before {
        font-family: "Bootstrap-Icons" !important;
        font-size: 20px;
        margin-right: 10px; 
        vertical-align: middle;
        transition: color 0.2s;
        color: #F8F9FA; /* Cor padrão do ícone */
    }

    /* Ícone Home */
    div[data-testid="stSidebarContent"] button[key*="nav_button_Home"]::before {
        content: "\\f433"; /* Código Unicode para bi-house-door-fill */
    }

    /* Ícone Listar Empresas */
    div[data-testid="stSidebarContent"] button[key*="nav_button_Listar Empresas"]::before {
        content: "\\f198"; /* Código Unicode para bi-building-fill */
    }
    
    /* Ícone Sair */
    div[data-testid="stSidebarContent"] button[key*="nav_button_Sair"]::before {
        content: "\\f14f"; /* Código Unicode para bi-box-arrow-right */
    }
    
    /* Corrigir a cor do ícone no HOVER */
    div[data-testid="stSidebarContent"] .stButton > button:hover::before {
        color: #FFC300 !important;
    }

    /* Corrigir a cor do ícone quando o item está SELECIONADO */
    div[data-testid="stSidebarContent"] .stButton > button[aria-selected="true"]::before {
        color: #1B2D45 !important; /* Mudar para Azul Marinho no selecionado */
    }
    /* ********************************************** */


    /* Título do Menu Principal - Ajustado o padding-left */
    .menu-title-container {
        color: #DCE0E6; 
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
        padding: 0 15px 8px 25px; /* Ajustado o padding-left para 25px */
        margin-bottom: 15px;
        margin-top: 20px; 
        font-weight: 600;
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

    /* Estilo dos Inputs de Texto (Geral) */
    div[data-testid="stTextInput"] > div > label > div > p {
        color: white !important; /* Garante que os labels 'E-mail' e 'Senha' fiquem brancos na caixa de login */
        font-weight: 500 !important;
    }
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 8px; 
        border: 1px solid #CBD5E0; 
        padding: 12px 15px; 
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); 
        transition: all 0.2s ease-in-out;
        background-color: white !important; 
        color: #1B2D45 !important;
    }
    /* Força o texto do placeholder a ser escuro */
    div[data-testid="stTextInput"] input::placeholder {
        color: #4A5568 !important; /* Cinza escuro para alto contraste */
        opacity: 1 !important;
    }

    /* Estilo dos Selectbox (selectbox) */
    div[data-testid="stSelectbox"] > div > button {
        border-radius: 8px;
        border: 1px solid #CBD5E0;
        padding: 10px 15px; 
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
        height: auto; 
        background-color: white !important; 
        color: #1B2D45 !important;
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
    
    /* Botão Primário (Geral) - AZUL MARINHO FORTE */
    button[data-testid^="stBaseButton-primary"] {
        background-color: #1B2D45 !important; 
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 25px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(27, 45, 69, 0.3);
        transition: all 0.2s ease-in-out;
    }
    button[data-testid^="stBaseButton-primary"]:hover {
        background-color: #0F1E33 !important; /* Azul mais escuro no hover */
        box-shadow: 0 6px 15px rgba(27, 45, 69, 0.5);
        transform: translateY(-1px); 
    }
    
    /* Contêiner de Login Azul Marinho */
    .login-container { 
        max-width: 400px; 
        margin: 50px auto; 
        padding: 30px; 
        border-radius: 10px; 
        background-color: #1B2D45; /* AZUL MARINHO */
        color: white; /* Texto Geral Branco */
        box-shadow: 0 0 25px rgba(0, 0, 0, 0.5); 
        text-align: center; 
    }
    /* Corrigir a cor dos títulos dentro do contêiner de login */
    .login-container h1, .login-container h2, .login-container h3 {
        color: white !important;
    }

    /* Esconde o cabeçalho padrão Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
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
            st.markdown(
                f"""
                <img src="data:image/png;base64,{logo_base64}" alt="Logo da Empresa" class="logo-centered">
                """,
                unsafe_allow_html=True
            )


    if st.session_state.get("token"):
        # Tenta carregar todos os dados se não estiverem na sessão (pode ser necessário um rerun)
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