import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Análise do Mercado de Trabalho Júnior",
    page_icon="🐣",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

df_jr = df["senioridade"] == 'junior'
apenas_jr = df[df_jr]

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(apenas_jr['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(apenas_jr['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(apenas_jr['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = apenas_jr[
    (apenas_jr['ano'].isin(anos_selecionados)) &
    (apenas_jr['contrato'].isin(contratos_selecionados)) &
    (apenas_jr['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title('🐣 Análise do Mercado de Trabalho Júnior')
st.markdown('Dashboard Interativo: Uma análise de dados sobre salários e a distribuição geográfica de profissionais de tecnologia em início de carreira. Utilize os filtros à esquerda para refinar sua análise.')

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not apenas_jr.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

#grafico com salarios por ano em linha

with col_graf1:
    if not apenas_jr.empty:
# Identificar os cargos juniores mais comuns (por exemplo, os 5 mais comuns)
        top_cargos_juniores = df_filtrado['cargo'].value_counts().nlargest(5).index.tolist()

# Filtrar o DataFrame de juniores para incluir apenas os cargos selecionados
        apenas_jr_top_cargos = df_filtrado[df_filtrado['cargo'].isin(top_cargos_juniores)]

# Agrupar os dados filtrados por ano e cargo, e calcular o salário médio
        salario_medio_por_ano_cargo = apenas_jr_top_cargos.groupby(['ano', 'cargo'])['usd'].mean().reset_index()

# criar o gráfico
        fig = px.line(salario_medio_por_ano_cargo,
              x='ano',
              y='usd',
              color='cargo', 
              title='Evolução do Salário Médio Anual para Cargos Juniores Selecionados',
              labels={'ano': 'Ano', 'usd': 'Salário Médio (USD)', 'cargo': 'Cargo'})

        fig.update_layout(xaxis = dict(tickmode = 'linear', tick0 = salario_medio_por_ano_cargo['ano'].min(), dtick = 1), 
            width=800,  # Definir a largura
            height=500 )# Definir a altura 
            
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")
                
#grafico com media por paises em barra

# Mapeamento de siglas para nomes completos em português para os países do top 10 juniores
salario_medio_jr_por_pais = df_filtrado.groupby('residencia')['usd'].mean().reset_index()

# Selecionar os top 10 países com maiores salários médios
top10_paises_jr = salario_medio_jr_por_pais.sort_values(by='usd', ascending=False).head(10)

país_top10_jr = {
    'CZ': 'CZE',
    'EG': 'EGY', 
    'CN': 'CHN', 
    'BA': 'BIH', 
    'US': 'USA', 
    'AU': 'AUS', 
    'BM': 'BMU', 
    'IQ': 'IRQ', 
    'JE': 'JEY', 
    'IR': 'IRN'  
}

# Criar uma nova coluna com os nomes completos dos países
top10_paises_jr['País'] = top10_paises_jr['residencia'].map(país_top10_jr)

with col_graf2:
    if not df_filtrado.empty:
        fig = px.bar(top10_paises_jr,
        x='País',
        y='usd',
        color= 'País',
        title='Top 10 Países com Maior Salário Médio para Juniores',             
        labels={'residencia': 'País', 'usd': 'Salário Médio Anual (USD)'}
        )

        fig.update_layout(
            bargap= 0,
            width=800,
            height=500)

        st.plotly_chart(fig)

    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

#grafico de homme ou presencial em pizza

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

#grafico de quantidade de emprego em mapa
with col_graf4:
    if not df_filtrado.empty:
        # Agrupamos e contamos o número de empregos usando residencia_iso3
        df_ds_quantidade = df_filtrado.groupby('residencia_iso3').size().reset_index(name='quantidade_empregos')

        grafico_paises = px.choropleth(
            df_ds_quantidade,
            locations='residencia_iso3', # Volte a usar o formato ISO-3 que funciona
            color='quantidade_empregos', 
            color_continuous_scale='bluered_r',
            range_color=[0,100],
            title='Quantidade de Empregos de Juniores por país',
            labels={'quantidade_empregos': 'Quantidade de Empregos', 'residencia_iso3': 'País'}
        )
        
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")


# Crie as colunas: a do meio será 3x maior que as laterais
col_esquerda, col_centro, col_direita = st.columns([1, 3, 1])

# Posicione o gráfico na coluna do meio
with col_centro:
    if not df_filtrado.empty:
        contagem_cargos = df_filtrado['cargo'].value_counts()
        top_10_cargos = contagem_cargos.head(10).reset_index()
        top_10_cargos.columns = ['cargo', 'frequencia']
        fig = px.bar(top_10_cargos,
        x='frequencia',
        y='cargo',
        color= 'cargo',
        orientation='h', # Gráfico horizontal para melhor leitura dos nomes dos cargos
        title='Top 10 Profissões Mais Frequentes',
        labels={'frequencia': 'Quantidade de cargos', 'cargo': 'Profissão'}
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'},
                          xaxis_range=[0, 1800],
                          width=1800,
                          height=500
        )

# ... seu comando para exibir o gráfico (st.plotly_chart(fig))
        # Agrupamos e contamos o número de empregos usando residencia_iso3
        st.plotly_chart(fig)
    else:
        st.warning("Nenhum dado para exibir no gráfico.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(apenas_jr)

