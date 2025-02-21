import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# Grafico 1 - Mostra quantos leads foram gerados por dia para cada origem
def grafico_quantidade_registros_por_origem(hubspot_data):
    dados_agrupados = hubspot_data.groupby(["data_criado", "origem"])['cpf'].size().reset_index(name='Quantidade')
    fig = px.bar(
        dados_agrupados, x="data_criado", y="Quantidade", color="origem",
        title="Quantidade de Registros por Data de Criação e Origem",
        text="Quantidade",
        labels={"criado": "Data de Criação", "Quantidade": "Quantidade de Registros", "origem": "Origem"},
        barmode="group"
    )
    
    fig.update_layout(
        title="Quantidade de leads por Origem",  # Título personalizado
        xaxis_title="Data de Criação",  # Título do eixo X
        yaxis_title="Quantidade de leads",
        xaxis=dict(
            showgrid=False,  # Remove as grades do eixo X
            tickangle=30,  # Inclina os rótulos do eixo X para melhorar a legibilidade
            tickmode='linear',  # Define a exibição de ticks de forma linear
            tickfont=dict(size=18),  # Ajusta o tamanho da fonte dos rótulos do eixo X
            zeroline=False,  # Remove a linha zero do eixo X
        ),
        yaxis=dict(
            showgrid=True,  # Mantém as grades no eixo Y para facilitar a leitura
            tickfont=dict(size=16),  # Ajusta o tamanho da fonte dos rótulos do eixo Y
            zeroline=True,  # Exibe a linha zero do eixo Y
        ),
        margin=dict(l=0, r=0, t=40, b=40),  # Ajusta as margens para dar mais espaço
        width=1600,  # Largura do gráfico
        height=600,  # Altura do gráfico
        template='plotly_dark',
    )

    return fig



# Grafico 2 - Tabela que mostra quantos disparos foram feitos pra cada convenio/produto, quantos leads gerou e proporção
def grafico_tabela_disparos_leads(hubspot_data, disparos_data):
    data = hubspot_data.groupby(['data_criado', 'convenio', 'produto2', 'origem'])['id'].size().reset_index(name='leads')
    merged_data = data.merge(disparos_data, on=['data_criado', 'convenio', 'produto2', 'origem'], how='inner')
    df_grouped = merged_data.groupby(['convenio', 'produto2'])[['quantidade', 'leads']].sum().reset_index()
    df_grouped['proporcao %'] = ((df_grouped['leads'] / df_grouped['quantidade']) * 100).round(2)
    df_grouped = df_grouped.sort_values(by='proporcao %', ascending=False)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Convênio</b>", "<b>Produto</b>", "<b>Quantidade Disparada</b>", "<b>Leads Gerados</b>", "<b>Proporção %</b>"],
            fill_color='rgb(0, 123, 255)',  # Azul para o cabeçalho
            font=dict(size=16, color='white'),  # Fonte branca e maior
            align='center',
            height=40
        ),
        cells=dict(
            values=[df_grouped['convenio'], df_grouped['produto2'], df_grouped['quantidade'], df_grouped['leads'], df_grouped['proporcao %'].round(2)],
            fill_color=[['white', '#f8f9fa'] * (len(df_grouped) // 2)],  # Cores alternadas para as células
            align='center',
            font=dict(size=14, color='black'),  # Fonte preta e tamanho ajustado
            height=30
        )
    )])
    
    # Atualizando o layout do gráfico
    fig.update_layout(
        title="<b>Tabela de Disparos e Leads por Convênio e Produto</b>",  # Título mais destacado
        height=800,  # Ajuste a altura para melhorar a visualização
        margin=dict(l=0, r=00, t=60, b=20),  # Ajuste nas margens
        template='plotly_dark',  # Usando o tema 'plotly_dark' para destacar a tabela
        showlegend=False  # Removendo a legenda, pois não é necessária
    )
    
    return fig

def grafico_tabela(hubspot_data, disparos_data):
    data = hubspot_data.groupby(['data_criado', 'convenio', 'produto2', 'origem'])['id'].size().reset_index(name='leads')
    merged_data = data.merge(disparos_data, on=['data_criado', 'convenio', 'produto2', 'origem'], how='inner')
    df_grouped = merged_data.groupby(['convenio', 'produto2'])[['quantidade', 'leads']].sum().reset_index()
    df_grouped['proporcao %'] = ((df_grouped['leads'] / df_grouped['quantidade']) * 100).round(2)
    df_grouped = df_grouped.sort_values(by='proporcao %', ascending=False)

    fig = px.bar(
        df_grouped,
        x='convenio',
        y='proporcao %',
        color='produto2',
        hover_data={'quantidade': True, 'leads': True},  # Exibe as colunas quantidade e leads no hover
        labels={'convenio': 'Convênio', 'proporcao %': 'Proporção (%)', 'produto2': 'Produto'},
        title="Proporção de Leads por Convênio e Produto"
    )

    fig.update_layout(
        title="Proporção de Leads por Convênio e Produto",  # Título personalizado
        xaxis_title="Convênio",  # Título do eixo X
        yaxis_title="Proporção de Leads (%)",
        xaxis=dict(
            showgrid=False,  # Remove as grades do eixo X
            tickangle=55,  # Inclina os rótulos do eixo X para melhorar a legibilidade
            tickmode='linear',  # Define a exibição de ticks de forma linear
            tickfont=dict(size=18),  # Ajusta o tamanho da fonte dos rótulos do eixo X
            zeroline=False,  # Remove a linha zero do eixo X
        ),
        yaxis=dict(
            showgrid=True,  # Mantém as grades no eixo Y para facilitar a leitura
            tickfont=dict(size=16),  # Ajusta o tamanho da fonte dos rótulos do eixo Y
            zeroline=True,  # Exibe a linha zero do eixo Y
        ),
        margin=dict(l=40, r=20, t=40, b=40),  # Ajusta as margens para dar mais espaço
        width=800,  # Largura do gráfico
        height=700,  # Altura do gráfico
        template='plotly_dark',
    )
    return fig


# Grafico 3 - Mostra pra cada etapa do hubspot quantos leads estão nessa etapa (segmentado pela origem)
def grafico_etapas_origem(hubspot_data):
    grouped_data = hubspot_data.groupby(['etapa', 'origem'])['cpf'].size().reset_index(name='Quantidade')

    fig = px.bar(
        grouped_data, x='etapa', y='Quantidade', color='origem',
        barmode='group', title='Distribuição de CPF por Etapa e Origem',
        labels={'etapa': 'Etapa', 'Quantidade': 'Quantidade de CPFs', 'origem': 'Origem'},
        category_orders={'etapa': ['LEAD', 'NEGOCIAÇÃO', 'CONTRATAÇÃO', 'PAGO', 'PERDA']}  # Define a ordem das etapas
    )
    
    fig.update_layout(
        title="Quantidade de leads por Etapa",  # Título personalizado
        xaxis_title="Etapa",  # Título do eixo X
        yaxis_title="Quantidade de leads",
        xaxis=dict(
            showgrid=False,  # Remove as grades do eixo X
            tickangle=0,  # Inclina os rótulos do eixo X para melhorar a legibilidade
            tickmode='linear',  # Define a exibição de ticks de forma linear
            tickfont=dict(size=18),  # Ajusta o tamanho da fonte dos rótulos do eixo X
            zeroline=False,  # Remove a linha zero do eixo X
        ),
        yaxis=dict(
            showgrid=True,  # Mantém as grades no eixo Y para facilitar a leitura
            tickfont=dict(size=16),  # Ajusta o tamanho da fonte dos rótulos do eixo Y
            zeroline=True,  # Exibe a linha zero do eixo Y
        ),
        margin=dict(l=40, r=20, t=40, b=40),  # Ajusta as margens para dar mais espaço
        width=1600,  # Largura do gráfico
        height=600,  # Altura do gráfico
        template='plotly_dark',
    )
    return fig


# Grafico 4 - Mostra quantos leads foram gerados pra cada convênio por cada origem
def grafico_cpf_por_convenio(hubspot_data):
    grouped_data = hubspot_data.groupby(['convenio', 'origem'])['cpf'].size().reset_index(name='Quantidade')
    fig = px.bar(
        grouped_data, y='convenio', x='Quantidade', color='origem',
        orientation='h', title='Quantidade de Leads por Convênio e Origem',
        labels={'convenio': 'Convênio', 'Quantidade': 'Quantidade de Leads', 'origem': 'Origem'}
    )
    
    return fig
