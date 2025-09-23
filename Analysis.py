from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, os, nltk, re, emoji
import pandas as pd 
from dateutil.parser import parse
from collections import Counter



## FUNZIONI DI UTILITA'

#creazione cartella di lavoro 
def creazione_cartella(path_database, cartella):
    path_completo = os.path.join(path_database, cartella)
    try:
        os.mkdir(path_completo)
    except FileExistsError:
        print(f"la cartella '{cartella}' esiste già")
    except PermissionError:
        print(f"Non è possibile creare la cartella '{cartella}', mancano privilegi")
    except Exception as e:
        print(f"Errore: '{e}'")
    return path_completo


## PARTE STATISTICA 

# quanti messaggi invia ogni persona
def quantità_messaggi_utenti(df, path_analisi): 
    utente_id = df['sender_id'].value_counts().sort_values(ascending=False)
    path = os.path.join(path_analisi, 'msg_per_utente.csv')
    msg_nome_df = utente_id.reset_index()
    msg_nome_df.columns = ['nome', 'messaggi']
    msg_nome_df.to_csv(path,  index=False, header=True)   
    print(f"Csv salvato in: {path}... ")

    return path

# quanti messaggi per anno, mese, giorno, ora
def messaggi_per_data(df, path_analisi):
    date = list(df['date'])
    date_pulite = {}
    for idx, time in enumerate(date):
        dt = parse(time)
        date_pulite[idx] = {
            'anno': dt.year,
            'mese': dt.month,
            'giorno': dt.day,
            'ora': dt.hour,
            'minuto': dt.minute,
        }
    
    dataframe_date = pd.DataFrame.from_dict(date_pulite, orient='index')
    path = os.path.join(path_analisi, 'date_messaggi.csv')
    path_date_csv = dataframe_date.to_csv(path,  index=False, header=True)  

    return path_date_csv

# funzione per gestire la logice dell'analisi delle parole 
def pulisci_e_conta_parole(serie_testo:pd.Series, lingua:str = 'italian')-> pd.DataFrame:
    if serie_testo.dropna().empty:
        return pd.DataFrame(columns=['parola','frequenza'])
    stopwords = set(nltk.corpus.stopwords.words(lingua))
    re_stopwords = r'\b(?:{})\b'.format('|'.join(map(re.escape, stopwords)))
    parole = (
        serie_testo
        .dropna()
        .str.lower()
        .replace([r'\|', re_stopwords, r'[^\w\s]'], ' ', regex=True)
        .str.split()
        .explode() 
    )
    parole_valide = parole.loc[parole.str.len() > 1]
    if parole_valide.empty:
        return pd.DataFrame(columns=['parola', 'frequenza'])
    conteggio = parole_valide.value_counts().reset_index()
    conteggio.columns = ['parola', 'frequenza']
    return conteggio

# parole più usate nei messaggi 
def parole_comuni(df, path_analisi, lingua='italian'):
    df_conteggio = pulisci_e_conta_parole(df['messaggio_originale'], lingua=lingua)
    if df_conteggio.empty:
        print("Nessuna parola significativa trovata.")
        return None
    path_csv = os.path.join(path_analisi, "top_parole.csv")
    df_conteggio.to_csv(path_csv, header=True, index=False) 
    print(f"Csv salvato in: {path_csv}\n")
    return path_csv


def parole_comuni_per_utente(df, path_analisi, lingua='italian'):

    df_finale = (
        df.groupby('sender_id')['messaggio_originale']
          .apply(lambda series: pulisci_e_conta_parole(series, lingua=lingua))
          .reset_index()
    )
    df_finale.drop('level_1', axis=1, inplace=True)
    if df_finale.empty:
        print("Nessuna parola significativa trovata per nessun utente.")
        return None 
    path_csv = os.path.join(path_analisi, "top_parole_per_utente.csv")
    df_finale.to_csv(path_csv, index=False, header=True)
    print(f"Csv salvato in: {path_csv}\n")
    return path_csv



# gestione EMOJI

# funzione per fare una classifica delle emoji più usate
def conta_emoji(df, path_analisi): 
    emojis = (df['emoji'].loc[lambda x: x != ""].value_counts().sort_values(ascending=False))
    emoji_df = emojis.reset_index()
    emoji_df.columns = ['emoji', 'frequenza']
    path_csv_emoji = os.path.join(path_analisi, 'classifica_emoji.csv')
    emoji_df.to_csv(path_csv_emoji, index=False)
    print(f"Csv classifica emoji salvato in: {path_csv_emoji}")
    
    return path_csv_emoji

# funzione per contare le emoji all'interno dei messaggi
def conta_emoji(testo):
    return len(emoji.emoji_list(testo))

def emoji_per_utente(df, path_analisi):
    # creare colonna solo per emoji > 0
    df['num_emoji'] = df['emoji'].apply(conta_emoji)
    # filtrare solo righe con almeno 1 emoji
    df_con_emoji = df[df['num_emoji'] > 0]
    # raggruppo per utente
    emoji_per_user = df_con_emoji.groupby('sender_id')['num_emoji'].sum().reset_index()
    path = os.path.join(path_analisi,"emoji_utente.csv")
    emoji_per_user.to_csv(path)
    return path

# funzione per aggiungere al database una colonna con solo le emoji di ogni messaggio
def messaggi_emoji(df):
    testo = list(df['message'])
    for idx, messaggio in enumerate(testo):
        contenuto = emoji.emoji_list(messaggio)
        solo_emoji = ''.join(e['emoji'] for e in contenuto)
        df.at[idx,'emoji'] = solo_emoji
    return df 


## PARTE SENTIMENT ANALYSIS

# funzione per tabularsai
def predict_sentiment(texts, tokenizer, model):
    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length = 512) 
    with torch.no_grad():
        outputs = model(**inputs)
    probabilità = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentimenti = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
    risultati = []
    for probs in probabilità:
        indice_max = torch.argmax(probs).item()
        label = sentimenti[indice_max]
        score = probs[indice_max].item()
        risultati.append({'label': label, 'score': score})
    
    return risultati

# funzione per mappare il sentiment con un numero per successive analisi 
def sentiment_map(df):
    sentiment_map = {
    'Very Negative': -2,
    'Negative': -1,
    'Neutral': 0,
    'Positive': 1,
    'Very Positive': 2
    }
    df['sentiment_map'] = df['label'].map(sentiment_map)
    return df

# sentiment analysis
def Tabularisai(df, path_analisi, nome_file):
    model_name = "tabularisai/multilingual-sentiment-analysis"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    dati = {}
    testo = df['message'].apply(lambda text: emoji.demojize(str(text))) # trasforma emoji in testo per aiutare il modello 
    for idx, messaggio in enumerate(testo):
        risultati = predict_sentiment(messaggio, tokenizer, model)
        classificazioni = risultati[0]
        dati[idx] = { 
            'message_id': df['message_id'].iloc[idx],
            'message': emoji.emojize(messaggio), # ritrasformo in emoji per il csv
            'messaggio_originale': df['messaggio_originale'].iloc[idx],
            'emoji': df['emoji'].iloc[idx],
            'label' : classificazioni.get('label'),
            'score': classificazioni.get('score'),
            'nome' : df['nome'].iloc[idx],
            'sender_id' : df['sender_id'].iloc[idx],
            'date': df['date'].iloc[idx],
            'cognome': df['cognome'].iloc[idx],
            'nome_vero': df['nome_vero'].iloc[idx],
            'risposta': df['risposta'].iloc[idx],
        }
    sentimenti = pd.DataFrame.from_dict(dati, orient='index')
    sentimenti = sentiment_map(sentimenti)
    sentimenti.set_index('message_id', inplace=True)
    path = os.path.join(path_analisi, nome_file)
    sentimenti.to_csv(path)
    print(f"Csv salvato in: {path} \n")
    return path, sentimenti

def avg_sentiment(df, path_analisi):
    inverse_sentiment_map = {
    -2: 'Very Negative',
    -1: 'Negative',
     0: 'Neutral',
     1: 'Positive',
     2: 'Very Positive'
    }
    # calcolo la media generale di polarizzazione della chat
    media_generale = df['sentiment_map'].mean()
    media_generale_rounded = int(round(media_generale))  # arrotonda e converte in int
    sentimento_generale = inverse_sentiment_map[media_generale_rounded]
    polarizzazione = [media_generale, sentimento_generale]
    
    # calcolo il sentimento medio per utente
    media_per_utente = df.groupby('sender_id')['sentiment_map'].mean().reset_index()
    media_per_utente.columns = ['utente', 'media_sentiment']
    media_per_utente['sentiment_score_rounded'] = media_per_utente['media_sentiment'].round().astype(int)
    media_per_utente['sentiment_label'] = media_per_utente['sentiment_score_rounded'].map(inverse_sentiment_map)
    path_m_utente = os.path.join(path_analisi, "sentiment_utente.csv")
    media_per_utente.to_csv(path_m_utente, index=False)
    print(f"Csv salvato in: {path_m_utente}... ")
   
    # calcolo il sentimento medio giornaliero 
    df['date'] = pd.to_datetime(df['date'])
    media_temporale = df.groupby(df['date'].dt.date)['sentiment_map'].mean().reset_index()
    media_temporale.columns = ['date', 'media_sentiment']
    media_temporale['date'] = pd.to_datetime(media_temporale['date'])
    media_temporale = media_temporale.sort_values('date')
    media_temporale['sentiment_score_rounded'] = media_temporale['media_sentiment'].round().astype(int)
    media_temporale['sentiment_label'] = media_temporale['sentiment_score_rounded'].map(inverse_sentiment_map)
    path_s_temporale = os.path.join(path_analisi, "sentiment_temporale.csv")
    media_temporale.to_csv(path_s_temporale, index=False)
    print(f"Csv salvato in: {path_s_temporale}... ")
    return polarizzazione, path_m_utente, path_s_temporale




def starter(database):
    df = pd.read_csv(database)
    path = os.path.dirname(database)
    
    # creazione cartella per csv delle analisi 
    path_analisi = creazione_cartella(path,"analisi")
    nltk.download('stopwords', quiet=True)
    csv_parole = parole_comuni(df, path_analisi) 
    csv_parole_utenti = parole_comuni_per_utente(df, path_analisi)
    csv_msg_utenti = quantità_messaggi_utenti(df, path_analisi)   
    df = messaggi_emoji(df) 
    emoji_utente_csv= emoji_per_utente(df, path_analisi)
    path_date_csv = messaggi_per_data(df, path_analisi)
    Tabularisai_csv, df = Tabularisai(df, path_analisi,"sentiment.csv") 
    polarizzazione, csv_s_utente, csv_s_temporale = avg_sentiment(df, path_analisi)

    return Tabularisai_csv, csv_parole,csv_parole_utenti, csv_msg_utenti, path_date_csv, emoji_utente_csv,polarizzazione, csv_s_utente, csv_s_temporale



database = None

if __name__ == "__main__":
    starter(database)


