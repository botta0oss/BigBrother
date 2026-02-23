![Logo_software](docs/images/software_logo.png)
# BigBrother

> **Automated analysis of Telegram groups**  
> "New technologies for investigations: a software to support communication analysis"
> _Bachelor's thesis – University of Turin_

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![NLP](https://img.shields.io/badge/NLP-HuggingFace_Transformers-brightgreen)](https://huggingface.co/transformers/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io/)
[![DeepL](https://img.shields.io/badge/API-DeepL-blueviolet)](https://www.deepl.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-lightgrey)](https://ollama.com/)

---

The growing volume of unstructured data from instant messaging platforms poses a significant challenge for investigative analysis, generating information overload that slows down and complicates investigations. BigBrother was created in response to this challenge: a software prototype that orchestrates a complete pipeline to transform chaotic Telegram conversations into structured, actionable intelligence.
Using advanced Natural Language Processing (NLP) and Large Language Models (LLM) techniques, the system automates data acquisition, sentiment analysis, and topic modelling. Finally, it presents the results in an interactive dashboard designed for investigative exploration. The goal is to provide analysts with a support tool to quickly identify patterns, key players, and critical themes, drastically reducing manual analysis time.

Try the demo at [bigbrother.streamlit.app](https://bigbrother.streamlit.app/).

---

## Screenshots of the Dashboard

<details>
  <summary>Click here to see a preview of the interface</summary>
  
  ### 1. Overview
  *The dashboard provides an overview with key metrics: total messages, number of users, and general emotional polarisation of the chat. User analysis is organised into practical tabs showing messages, average sentiment, and emoji usage for each participant.*
  ![Dashboard Overview](docs/images/01_panoramica.png)

  ---
  
  ### 2. Overall Content Analysis
  *Aggregate visualisations show the evolution of sentiment over time and the most common words used throughout the chat, with an interactive slider to adjust the number of words displayed.*
  ![Temporal Analysis and Common Words](docs/images/02_analisi_contenuto.png)

  ---

  ### 3. Detailed Analysis per User
  *By selecting a user from the sidebar, you can explore their specific activity in detail through three different sections: most used words, personal sentiment trends, and favourite emojis.*

| Most Frequently Used Words by the User | Personal Sentiment Trend | Most Used Emojis |
| :---: | :---: | :---: |
| ![Most Frequently Used Words by the User](docs/images/03_utente_parole.png) | ![Personal Sentiment Trend](docs/images/04_utente_sentiment.png) | ![ Most Used Emojis](docs/images/05_utente_emoji.png) |

  ---
  
  ### 4. Search by Keywords
  *A search function allows you to analyse the use of specific keywords, showing who uses them, how often over time and the exact context of the messages, with the searched words highlighted in red.*
  ![Keyword Search Functionality](docs/images/06_ricerca_keyword.png)

  ---
  
  ### 5. Analysis by Topic (Clustering)
  *Messages are grouped into thematic clusters to identify the main topics. The dashboard displays the distribution of topics, the average sentiment of each cluster, and an interactive map to explore the semantic proximity of messages.*
  ![Cluster Analysis](docs/images/07_cluster_analisi.png)

  ---

  ### 6. Cluster Explorer
  *You can select a specific topic from a drop-down menu to analyse its messages, most active users and popularity over time in detail.*
   ![Cluster Explorer](docs/images/08_esploratore_cluster.png)

</details>

---

## Technology Stack

-   **Language and Core Libraries**:
    -   **Python 3.9.10**: Main programming language.
    -   **Pandas**: For manipulation and analysis of tabular data.

-   **Data Acquisition and Translation**:
    -   **Telethon**: For interacting with Telegram API, acting as a user client to access the complete chat history.
    -   **DeepL API**: For automatic translation of English texts, chosen for its high quality, which is necessary to maximise the performance of NLP models.

-   **Natural Language Processing (NLP)**:
    -   **Hugging Face Transformers**: For sentiment analysis, using the pre-trained model `tabularisai/multilingual-sentiment-analysis`.
    -   **NLTK**: For removing stopwords during the analysis of the most common words.
    - **Sentence-Transformers**: For generating high-quality text embeddings that capture the semantic meaning of messages.

-   **Topic Modelling and Clustering**:
    -   **BERTopic**: Advanced framework for semantic clustering of messages and identification of latent topics.
    -   **UMAP**: Algorithm for dimensional reduction of embeddings, used for 2D visualisation of clusters.

-   **Large Language Models (LLM)**:
    -   **Ollama**: For running local language models (e.g. Mistral) for the automatic generation of descriptive and interpretable labels for identified clusters.

-   **Data Visualisation**:
    -   **Streamlit**: For quickly creating an interactive web dashboard.
    -   **Plotly**: For generating interactive and dynamic graphs within the dashboard.

---

## Project Structure

-   `main.py`: System entry point. Orchestrates the sequential execution of scraping, translation, analysis and clustering, then launches the dashboard.
-   `scraper.py`: Module that connects to Telegram, prompts the user to select a chat and downloads messages in CSV format..
-   `traduttore.py`: Module that uses DeepL's API to translate messages into English.
-   `Analysis.py`: Module that contains logic for statistical analysis (message frequency, common words, emoji usage) and sentiment analysis. Saves results to CSV files.
-   `clustering.py`: Module that performs topic modelling with BERTopic and, optionally, queries a local LLM via Ollama to label the identified clusters.
-   `dashboard.py`: Module that defines the web user interface with Streamlit, displaying the complete analysis results interactively.
-   `config.json`: Configuration file for storing API keys (Telegram, DeepL) and system settings (e.g. Ollama activation and model selection).
-   `clustering_prompt.txt`: Prompt template used to instruct the LLM on how to generate labels for clusters.
-   `style.css`: Style sheet for customising the appearance of the Streamlit dashboard.
-   `requirements.txt`: List of Python dependencies required to run the project.
-   `/data`: Main directory where subfolders are created for each analysis session, containing all raw data and processed results.

---

## Workflow

1.  **Scraping**: `main.py` starts `scraper.py`. The user logs into Telegram, selects a chat and the number of messages to download. The data is saved in a `[chat_name].csv` file inside a new folder in `/data`.
2.  **Translation**: `traduttore.py` reads the CSV, translates the messages into English using the DeepL API, and saves the results in the file `[chat_name]_translated.csv`.
3.  **Analysis**: `Analysis.py` processes the translated file, performing statistical and sentiment analysis. The results are saved in multiple CSV files (e.g. `sentiment.csv`, `top_words.csv`) in the subfolders `/analysis`.
4.  **Clustering**: `clustering.py` uses the `sentiment.csv` file and groups messages into semantic clusters using BERTopic. It saves the results in `cluster.csv` and, if Ollama is active, generates labels in `cluster_label.csv`.
5.  **Path Aggregation**: At the end of the pipeline, `main.py` collects all the paths of the generated files and saves them in a single configuration file `[chat_name].json`.
6.  **Visualisation**: Finally, `main.py` launches the dashboard (`dashboard.py`) by passing the path to the `[chat_name].json` file. The dashboard dynamically loads all the data and presents it to the user.
---

## Installation and Configuration

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/botta0oss/BigBrother.git
    cd BigBrother
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API and settings**:
    Create the `config.json` file in the root directory of your project and enter your keys and settings.

    *(To obtain `api_id` and `api_hash`, register at [my.telegram.org](https://my.telegram.org/auth). For `auth_key`, sign up for an API plan at [DeepL.com](https://www.deepl.com/pro-api)).*

    Use this template for your `config.json`:
    ```json
    {
        "api_id": "YOUR_TELEGRAM_API_ID",
        "api_hash": "YOUR_TELEGRAM_API_HASH",
        "phone": "+391234567890",
        "ollama": true,
        "modello": "mistral",
        "auth_key": "YOUR_AUTH_KEY_DEEPL"
    }
    ```
    -   `phone`: Your telephone number associated with your Telegram account, in international format.
    -   `ollama`: Set to `true` to enable automatic cluster labelling, `false` to disable it.
    -   `modello`: The name of the model you downloaded with Ollama (es. `mistral`, `llama3`).
    -   `auth_key`: Ensure you include the suffix `:fx` if you are using a free DeepL API account.

4.  **(Optional) Configure Ollama**:
    To use the automatic cluster labelling feature, ensure that you have installed and started [Ollama](https://ollama.com/) and that you have downloaded the template specified in `config.json`.
    ```bash
    # Example of how to download the Mistral model
    ollama pull mistral
    ```

5.  **Start up the complete system**:
    ```bash
    python main.py
    ```
    The terminal will guide you through the authentication and scraping process. Once the entire analysis pipeline is complete, the Streamlit dashboard will automatically open in your browser.

---

## Thesis objectives

-   Demonstrate the feasibility of an end-to-end system to automate the entire analysis flow: from the acquisition of raw data from Telegram to its transformation into structured and viewable information.
-   Apply and validate advanced NLP techniques to extract qualitative insights, in particular through Sentiment Analysis to map emotional polarity and Topic Modelling to identify the main topics of discussion without supervision.
-   Introduce an innovative approach to the interpretability of results, using a local Large Language Model (LLM) to automatically generate semantic labels for message clusters, solving a common problem in topic modelling.
-   Design a visualisation dashboard that is not just a simple static report, but an interactive exploration tool that guides the analyst in understanding the relational and temporal dynamics of the conversation.
-   Validate the prototype's usefulness in a realistic operational context, demonstrating how it can support and accelerate an analyst's work in identifying relevant evidence and information within large volumes of text.

---

## Author

**Francesco Bottacin**  
Bachelor's degree in _Strategic and Security Sciences_   
**University of Turin**  
**15/09/2025**
