import pandas as pd
import spacy
from pickle import load, dump
import re
from datetime import date
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from spacy.tokens import DocBin
from spacy.matcher import Matcher
from spacy.util import filter_spans

class Judgment:
    """Contains all essential information of the respective Judgment.

    Args:
        title (str): Title of the Judgment.
        text (str): Full text of the Judgment.
        url (str): URL of the Judgement.
        case_details (dict): Dictionary of case_details.
    
    Attributes:
        title (str): Title of the Judgment.
        text (str): Full text of the Judgment.
        url (str): URL of the Judgment.
        case_details (str): String of case_details.
    
    """
    def __init__(self, title: str, ident: str, text:str, url:str, case_details: str):
        self.title = title
        self.ident = ident
        self.text = text
        self.url = url
        self.case_details = case_details

# open scraped data from module 1 as raw_data (important to define class judgement first!)
with open('data/scraped_data.pickle', 'rb') as handle:
    raw_data = load(handle)


def extract_data(raw_data):
    """Generates initial dataframe. Takes raw data as input, returns data frame and extracts case details.
    
    The data fram contains information about the title, identy, text, url, and case details. For the case details in particular, the importance level, conclusion, articles, seperate opinions, keywords, dates, related cases and respondant states are extracted. 
    
    Args:
        raw_data (dict): Dictionary containing raw, scraped Judgements.
        
    Returns:
        The initial data frame. 
        
    """
    # Transform to Dataframe
    attributes = ['title', 'ident', 'text', 'url', 'case_details']
    df = pd.DataFrame([{fn: getattr(raw_data[key], fn) for fn in attributes} for key in raw_data])
    
    # Extract case details:
    df = pd.concat([
        df,
        df['case_details'].str.extract(r"(?:[Ii]mportance\s[lL]evel\n)(?P<importance_lvl>.*)(?:\n[Rr]epresented\sby|[Rr]espondent\s[sS]tate)", flags=re.S),
        df['case_details'].str.extract(r"(?:[Cc]onclusion\(s\)?\n?)(?P<conclusion>.*)(?:\n[Aa]rticle\(s\))", flags=re.S),
        df['case_details'].str.extract(r"(?:[Aa]rticle\(s\))(?P<articles>.*)(?:[Ss]eparate\s[oO]pinion\(s\))", flags=re.S),
        df['case_details'].str.extract(r"(?:[Ss]eparate\s[oO]pinion\(s\)\n?)(?P<separate_opinion>Yes|No)(?:\n[Dd]omestic\s[Ll]aw|\n[Ss]trasbourg\s[Cc]ase-[Ll]aw|\n[Kk]eywords)?", flags=re.S),
        df['case_details'].str.extract(r"(?:[kK]eywords\n)(?P<keywords>.*)(?:\nECLI)", flags=re.S),
        df['case_details'].str.extract(r"(?:[Jj]udgment\s[dD]ate\n)(?P<date>\d{2}/\d{2}/\d{4})", flags=re.S),
        df['case_details'].str.extract(r"(?:[Ss]trasbourg\s[Cc]ase-[lL]aw\n)(?P<related_cases>.*)(?:\n[Kk]eywords)", flags=re.S),
        df['case_details'].str.extract(r"(?:[Rr]espondent\s[Ss]tate\(s\)\n)(?P<respondent_state>.*)(?:\n[Jj]udgment\s[Dd]ate|[Rr]eference\s[Dd]ate)", flags=re.S)
        ], 
        axis=1
        )
    return df


def clean_data(df):
    """Takes initial dataframe as argument, drops NA's, formats date, and performs string cleaning on remaining fields.
    
    This function also labels each Judgement according to whether there it violates the result of any other Judgement.
    
    Args:
        df (df): Initial dataframe containing the scraped Jugement.
        
    Returns:
        The cleaned data frame.
    """
    df.dropna(inplace=True)
    df['date'] = pd.to_datetime(df['date'], errors="ignore", format="%d/%m/%Y")
    df['respondent_state'] = df['respondent_state'].str.extract(r"(?P<respondent_state>.*)")
    df['importance_lvl'] = df['importance_lvl'].str.extract(r"(?P<importance_lvl>\d|Key\scases)")
    df['the_law'] = df['text'].str.extract(r"(?:THE\sLAW)(?P<the_law>.*)(?:FOR\sTHESE\sREASONS)", flags=re.S)
    df['articles'] = [list(filter(None, re.sub('\d{1,2}-\d{1,2}-?.?', '', re.sub('(?<=P\d)-', '#', j)).replace('Rules of Court', '').split('\n'))) for j in df['articles']]
    df['related_cases'] = [re.findall(r"\d{3,5}\/\d{2}", row, flags=re.S) for row in df['related_cases']]
    pattern = "(?:[^Nn][^o])(?P<article_violation>\s[vV]iolation\sof\s(?:[Aa]rticle|[Aa]rt[.])\sP?\d{1,2})"
    df['violations'] = [re.findall(pattern=pattern, string=i, flags=re.S) if re.findall(pattern=pattern, string=i, flags=re.S) else None for i in df['conclusion']]
    pattern = "(?P<no_article_violation>[nN]o\s[vV]iolation\sof\s(?:[Aa]rticle|[Aa]rt[.])\sP?\d{1,2})"
    df['no_violations'] = [re.findall(pattern=pattern, string=i, flags=re.S) if re.findall(pattern=pattern, string=i, flags=re.S) else None for i in df['conclusion']]
    df['intro_text'] = df['text'].str.extract(r"(?:composed\sof)(?P<intro_text>.*?)(?:following\sjudgment[,]?)", flags=re.S)

    labels = []
    for v, n in zip(df['violations'], df['no_violations']):
        if n and not v:
            labels.append('no_violation')
        elif v and not n:
            labels.append('violation')
        elif not v and not n:
            labels.append('other')
        elif v and n:
            labels.append('mixed')
    df['label'] = labels
    
    df = df.loc[df['text'].str.len() < 1000000]
    return df

# Extracting & Cleaning of data
df = extract_data(raw_data)
df = clean_data(df)


### Extraction of judge names with spaCy's rule-based Matching Engine
nlp=spacy.load("en_core_web_sm")
n = 1
judges = []

matcher = Matcher(nlp.vocab)
pattern = [{"ENT_TYPE": "PERSON", "OP": "+"}] # Match on or multiple Entities of type Person

matcher.add("judge", [pattern])
for doc, ident in zip(nlp.pipe(df['intro_text'], batch_size=10, n_process=3), list(df['ident'])):
    matches = matcher(doc)
    spans = [doc[start:end] for match_id, start, end in matches] # get spans of matches in doc
    judges.append([re.sub("(Mr\s?|Mrs\s?|Sir\s?)", "", span.text) for span in filter_spans(spans)]) # Filter_spans removes duplicate entities (e.g. First and Last name separate)
    print(f'Completed iteration {n} of {len(df["intro_text"])}')
    n += 1

# Include judges into dataframe
df['judges'] = judges

# Write dataframe to disk
with open('data/data_cleaned.pickle', 'wb') as handle:
    dump(df, handle)


## create train-test split, stratifying the data as categories are imbalanced
X_train, X_test, y_train, y_test = train_test_split(
    df['the_law'], df['label'], test_size=0.3, random_state=42,
    stratify=df['label']
)
train_data = [(text, label) for text, label in zip(X_train, y_train)]
test_data = [(text, label) for text, label in zip(X_test, y_test)]


def make_docs(df):
    """Takes cleaned dataframe as argument and formats the Judgement as docs.
    
    Docs are sequences of tokens and are required for accessing linguistic annotations using spaCy. This function also assignes a dummy variable indicating whether the case conflicts with other Judgements or not.
    
    Args:
        df (df): Cleaned dataframe containing the scraped Judgement.
        
    Returns:
        A doc of the Judgement.
        
    """
    n = 1
    docs = []
    for doc, label in nlp.pipe(df, batch_size=10, n_process=3, as_tuples=True):
        if label == 'no_violation':
            doc.cats['no_violation'] = 1
            doc.cats['violation'] = 0
            doc.cats['other'] = 0
            doc.cats['mixed'] = 0
        if label == 'violation':
            doc.cats['no_violation'] = 0
            doc.cats['violation'] = 1
            doc.cats['other'] = 0
            doc.cats['mixed'] = 0
        if label == 'other':
            doc.cats['no_violation'] = 0
            doc.cats['violation'] = 0
            doc.cats['other'] = 1
            doc.cats['mixed'] = 0
        if label == 'mixed':
            doc.cats['no_violation'] = 0
            doc.cats['violation'] = 0
            doc.cats['other'] = 0
            doc.cats['mixed'] = 1
        docs.append(doc)
        print(f"Processed {n} out of {len(df)}")
        n += 1
    return(docs)

# Process both training and test datasets and save them. This will take quite some time
train_docs = make_docs(train_data)
doc_bin = DocBin(docs=train_docs)
doc_bin.to_disk("./data/train.spacy")

test_docs = make_docs(test_data)
doc_bin = DocBin(docs=test_docs)
doc_bin.to_disk("./data/test.spacy")

# For training the model, go to directory, open anaconda and run python -m spacy init fill-config ./base_config.cfg ./config.cfg 
# Then, run config file: python -m spacy train config.cfg --output ./output
# This takes quite some time too, so we saved the model in the GitHub repo

# Load trained model
nlp = spacy.load("output/model-best")

# Make predictions on test dataset
y_pred = [max(nlp(text).cats, key=nlp(text).cats.get) for text in X_test]

# Create confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Save CM for further viz
with open('data/cm.pickle', 'wb') as handle:
    dump(cm, handle)