import pandas as pd
import os, time, deepl
from deepl.exceptions import TooManyRequestsException

def translate_batch_safe(batch_messaggi,deepl_translator, retries=5, base_sleep=2):
    for attempt in range(retries):
        try:
            results = deepl_translator.translate_text(
                batch_messaggi, source_lang="IT", target_lang="EN-US"
            )
            return [r.text for r in results]
        except TooManyRequestsException:
            wait = base_sleep * (2 ** attempt)
            print(f"[Rate limit] Attendo {wait} secondi (tentativo {attempt+1}/{retries})...")
            time.sleep(wait)
    raise RuntimeError("Superato il numero massimo di tentativi per un batch")


def main(df,deepl_translator, path, nome, batch_dimensione=50):
    risultati = {}

    messaggi = df['message'].tolist()
    totale = len(messaggi)

    for batch_inizio in range(0, totale, batch_dimensione):
        batch_fine = min(batch_inizio + batch_dimensione, totale)
        batch_messaggi = messaggi[batch_inizio:batch_fine]

        print(f"\nTraducendo batch {batch_inizio}-{batch_fine - 1} / {totale}")

        batch_tradotto = translate_batch_safe(batch_messaggi,deepl_translator)

        for i, traduzione in enumerate(batch_tradotto):
            idx = batch_inizio + i
            risultati[idx] = {
                "message_id": df['message_id'].iloc[idx],
                "message": traduzione,
                "messaggio_originale": df['message'].iloc[idx],
                "sender_id": df['sender_id'].iloc[idx],
                "nome": df['nome'].iloc[idx],
                "cognome": df['cognome'].iloc[idx],
                "nome_vero": df['nome_vero'].iloc[idx],
                "date": df['date'].iloc[idx],
                "risposta": df['risposta'].iloc[idx]
            }

        #attesa breve tra i batch
        time.sleep(2)

    # Salvataggio finale
    traduzione = pd.DataFrame.from_dict(risultati, orient='index')
    traduzione.set_index('message_id', inplace=True)
    nome = nome + "_tradotto.csv"
    path_completo = os.path.join(path, nome)
    traduzione.to_csv(path_completo)

    return path_completo



# chiamo le funzioni 
def starter(database, auth_key, nome_csv):
    deepl_translator = deepl.Translator(str(auth_key))
    print(f"pre traduzione:  {deepl_translator.get_usage()}")
    path_salvataggio = os.path.split(database)[0]
    df = pd.read_csv(database)
    path = main(df, deepl_translator, path_salvataggio, nome_csv)
    print(f"post traduzione: {deepl_translator.get_usage()}")
    return path



database = None

if __name__ == "__main__":
    starter(database, auth_key, nome_csv)
