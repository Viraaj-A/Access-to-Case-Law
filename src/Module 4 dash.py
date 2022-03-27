import re
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container
from dash.dependencies import Input, Output
from pickle import load
import networkx as nx
import json
import plotly.io as pio
import plotly.graph_objects as go
import spacy

# load spacy model for classifier
nlp = spacy.load("output/model-best")

# load all plots from module 3
network_plot = pio.read_json('output/plotly_network.json')
line_plot = pio.read_json('output/plotly_bycountry.json')
cm_plot = pio.read_json('output/plotly_cm.json')
judges_plot = pio.read_json('output/plotly_sb_judge.json')
articles_plot = pio.read_json('output/plotly_sb_art.json')

# assign logo hrefs
echr_logo = 'https://www.mediadefence.org/wp-content/uploads/2020/06/Logo_European_Court_of_Human_Rights_1_linedrawing.jpg'
github_logo = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'

# links to github, hudoc & spacy
hudoc_link = 'https://hudoc.echr.coe.int/eng#{%22documentcollectionid2%22:[%22GRANDCHAMBER%22,%22CHAMBER%22]}'
github_link = 'https://github.com/juka19/Magna-Carta-Mining'
spacy_link = "https://spacy.io/api/architectures#TextCatBOW"

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUMEN],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale= 1.0'}]) # importing bootstrap css theme Lumen


# Create top bar
navbar = dbc.Row(
    dbc.Container(
            dbc.Row(
                [
                    dbc.Col(html.A([html.Img(src=echr_logo, height='60px')], href=hudoc_link), width=1, className='float-left'),
                    dbc.Col(html.H2("Magna Carta Mining"), width={'size': 6, 'offset':2}, className='ms-2 text-center'),
                    dbc.Col(html.A([html.Img(src=github_logo, height='60px')], href=github_link), className='float-right', width={'size': 1, 'offset':2})
                ],
                align='center', className='g-0'
            )
    )
)

# Create layout: Very simple, header & 5 tabs
app.layout = html.Div([
    navbar, 
    dbc.Row(
        dbc.Col(
            html.Div(
                children=[
                    dcc.Tabs(id="tabs", value="tab-1", children=[
                        dcc.Tab(label="Overview", value='tab-1'),
                        dcc.Tab(label="Judgments over Time", value='tab-2'),
                        dcc.Tab(label="Network Graph", value='tab-3'),
                        dcc.Tab(label="Text Classification", value='tab-4'),
                        dcc.Tab(label='Allegations by Country, Article & Judge', value='tab-5')
                    ], className='mb-4 h4 text-center'),
                    html.Div(id='tab-content')
                ], style={'margin':'auto', 'padding': '30px', 'align': 'center', 'font-family': 'Sans-serif'})
        )
    )
])

# Create callback for tabs
@app.callback(Output('tab-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    """
    Functions that establishes HTML formatting for each tab of the final dashboard.
    """
    if tab == 'tab-1':
        return html.Div([
            html.H3('Overview'),
            html.Div(children=[
                html.H2("Magna Carta Mining"),
                html.P("""Every person located in the territorial jurisdiction of the European Court of Human Rights is owed human rights by the respective member state. People can use these rights against the State and State organs. However, people are unaware of what their rights are, how their rights evolve, and what their rights even mean. The HUDOC European Court of Human Rights database provides access to all relevant European Union human rights case law, but fails to make the underlying information accessible to the people it serves."""),
                html.P("""Magna Carta mining provides easy to use infographics that users can drill down to obtain the relevant data they might require. This tool can be used by individuals, Governments, researchers , and politicians to obtain a high level and detailed overview of human rights in the European Union. Currently, users can view the following infographics: Judgements over Time; Network Graph; Text Classification; and Allegations by Country, Article & Judge."""),
                html.H3('Judgements over Time'),
                html.P("""Judgments over time, for every member state, details the number of judgements issues in the year. This graph instantly provides insight to what Member States are being litigated against most frequently and relatively to other Member States. For example, preliminary insight would show that between 1995 and 2000, Turkey was the most litigated against state. However, this changed at 2005 where Italy became the most litigated against state. Insight such as this is not instantly obtainable using the HUDOC database."""),
                html.P("""Possibly unsurprisingly, the number of cases decreased during 2020, this may be correlated to the COVID-19 pandemic. A future infographic could include articles alleged over time, to understand whether there has been a shift in what the most important rights at the time are."""),
                html.H3("Network Graph"),
                html.P("""The Network Graph displays which cases are linked to other cases. The cases on the Network Graph must be linked to at least 5 other cases to be displayed. In summary, this graph displays what the most commonly cited cases are alternatively what cases have the highest precedent value. If a researcher, lawyer, or student wishes to identify the most important cases in a given area quickly, they can click through this infographic instead of conducting primary research and reading large amounts of material."""),
                html.P("""At a conceptual level, this graph also shows the links between all areas of law. If someone wishes how a breach of one human rights impacts another, the user could simply trace through this Network Graph. A further development would be to expand the network graph to the lower Chamber and make it searchable with callbacks."""),
                html.H3("Text Classification"),
                html.P("""We trained a spacy Bag-of-Words model on the texts of the judgements, using a constructed label from the metadata of the judgement that yields four categories: No violation, Violation, Other (violation is not mentioned in the judgements conclusion) and Mixed (which indicates that there is both violations and non-violations present in the conlusion)."""),
                html.P("""As expected, the model is far from being perfect! It overestimates the labels Violation and Other, and almost never predicts Non-violation and Mixed (which is probably very difficult!). You can test the model's predictions and see how it scores your text. We are also reporting the confusion matrix below the model that plots the predicted labels against the true labels from our test dataset."""),
                html.A(html.P('See here for the model architecture.'), href=spacy_link, className='link-light text-light'),
                html.H3("""Sunburst Plots"""),
                html.P("""The Sunburst Plot efficiently displays which specific articles are alleged most commonly against each State. From these plots, we can see that Article 41 is mostly commonly alleged, however, the second most common allegation differs across each State. This information can provide a useful method to assess where a State is specifically failing in fulfilling their human rights obligations. """),
                html.P("""The Number of Allegations by Country determined by Judge provides a quick method to assess the most prolific judges. This can prove useful to gain an insight into which judges deliver the most amount of judgements consequently to understand the most important judges in the country without conducting an primary research. """),
            ], style={'height': '100%', 'width':'80%', 
            'background-color':'rgb(83, 130, 241)', 
            'margin': 'auto', 'font-family': 
            'Sans-serif', 'padding': '20px', 
            'color': 'white'}, className='rounded')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Judgments over Time'),
            dcc.Graph(
                id='line_plot',
                figure=line_plot,
                style={'width': '100%', 'height': '60%', 'margin': 'auto'}
            )
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Network Graph'),
            dcc.Graph(
               id='network_plot',
               figure=network_plot,
               style={'width': '70%', 'height': '800px', 'margin': 'auto'} 
            )
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Text Classification'),
            html.P('Does your text violate human rights? Input text to find out!'),
            dcc.Textarea(
                id='text-input',
                value="""
                ALLEGED VIOLATION OF ARTICLE 10 OF THE CONVENTION ON ACCOUNT OF THE APPLICANT’S CRIMINAL CONVICTION
                77.  The applicant complained under Article 10 of the Convention about his criminal conviction on account of his editorial choices relating to the publication of the material under the headline “Death to Russia!”.
                78.  The relevant parts of Article 10 of the Convention read as follows:
                “1.  Everyone has the right to freedom of expression. This right shall include freedom to hold opinions and to receive and impart information and ideas without interference by public authority and regardless of frontiers. ...
                2.  The exercise of these freedoms, since it carries with it duties and responsibilities, may be subject to such formalities, conditions, restrictions or penalties as are prescribed by law and are necessary in a democratic society, in the interests of national security, territorial integrity or public safety, for the prevention of disorder or crime, for the protection of health or morals, for the protection of the reputation or rights of others, for preventing the disclosure of information received in confidence, or for maintaining the authority and impartiality of the judiciary.”""",
                style={'width': '100%', 'height': 300},
            ),
            html.Br(),
            html.H5('Model Prediction'),
            html.Div(id='model-output', style={'whiteSpace': 'pre-line'}),
            html.Br(),
            html.H3('Confusion Matrix of Text Classifier'),
            dcc.Graph(
               id='cm_plot',
               figure=cm_plot,
               style={'width': '100%', 'height': '100%'}
            )
        ])
    elif tab == 'tab-5':
        return html.Div([
            html.H3('Sunburst Plots of Allegations by Country'),
            dcc.Graph(
               id='articles_plot',
               figure=articles_plot,
               style={'width': '700px', 'height': '700px', 'margin': 'auto', 'display': 'inline-block'} 
            ),
            dcc.Graph(
               id='judges_plot',
               figure=judges_plot,
               style={'width': '700px', 'height': '700px', 'margin': 'auto', 'display': 'inline-block'} 
            )
        ])
# Create callback for Text classifier
@app.callback(Output('model-output', 'children'), Input('text-input', 'value'))
def update_output(value):
    return f"Probability of no violation: {round(nlp(value).cats['no_violation'], 2)} | Probability of violation: {round(nlp(value).cats['violation'], 2)} | Probability of Other: {round(nlp(value).cats['other'], 2)} | Probability of Mixed: {round(nlp(value).cats['mixed'], 2)}"

if __name__ == '__main__':
    app.run_server(debug=True)