import nltk

_NLTK_PACKAGES = [
    ('corpora',    'stopwords'),
    ('tokenizers', 'punkt'),
    ('tokenizers', 'punkt_tab'),
    ('taggers',    'averaged_perceptron_tagger'),      # older NLTK versions
    ('taggers',    'averaged_perceptron_tagger_eng'),  # newer NLTK versions
]

for _category, _pkg in _NLTK_PACKAGES:
    try:
        nltk.data.find(f'{_category}/{_pkg}')
    except LookupError:
        print(f"  Downloading NLTK: {_pkg}")
        nltk.download(_pkg, quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

STOPWORDS = set(stopwords.words("english"))
import re
import nltk
import html as html_module
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
#Utilities - BeautifulSoup + NLTK


def clean_html(text):
    """ Use BeautifulSoap to strip all HTML tags, decode entities, 
    and return clean plain text"""
    if not text:
        return ""
    soup = BeautifulSoup(text, "lxml")

    # Remove Script/Style blocks entirely
    for tag in soup(["script", "style", "sup", "table"]):
        tag.decompose()
    
    #Get plain text, preserve spacing between block elements
    clean = soup.get_text(separator=" ")

    #Decode remaining html entities
    clean = html_module.unescape(clean)

    #Remove citation markers liek [1], [note 2]
    clean = re.sub(r"\[\w*\s*\d*\]", "", clean)

    #Normalize Whitespace
    clean = re.sub(r"\s+", " ", clean).strip()

    return clean

def nltk_sentences(text):
    """ Use NLTK send_tokenize to split text into proper sentences."""
    
    if not text:
        return []
    sentences = sent_tokenize(text)
    return [s.strip() for s in sentences if len(s.strip())>15]

def chunk_by_sentences(text, max_tokens=512, overlap_sentences=50):
    """ Chunk text by sentence boundaries using NLTK.
    max_tokens: maximum words per chunk
    overlap_sentences: how many sentences carry over into the next chunk"""

    sentences = nltk_sentences(text)
    chunks, current_sent, current_count = [], [], 0

    for sent in sentences:
        word_count = len(word_tokenize(sent))

        if current_count + word_count > max_tokens and current_count:
            chunks.append(" ".join(current_sent))

            # overlap: keep last N sentences for context continuity
            current_sent = current_sent[-overlap_sentences:]
            current_count = sum(len(word_tokenize(s)) for s in current_sent)
        
        current_sent.append(sent)
        current_count += word_count

    if current_sent:
        chunks.append(" ".join(current_sent))

    return [ c for c in chunks if len(c.strip())>30]

def extract_keywords(text, top_n = 8):
    """ Use NLTK to extract top N keywords from text
    Filters stopwords and short tokens, returns most frequent.
    Useful as metadata for keyword-based filtering in RAG"""

    tokens = word_tokenize(text.lower())
    keywords = [
        t for t in tokens if t.isalpha() and t not in STOPWORDS and len(t)>3
    ]

    most_common = Counter(keywords).most_common(top_n)
    return [ word for word, freq in most_common]

def extract_noun_phrases(text):
    """ Use NLTK POS tagging to extract noun prhases(NNP, NN sequences)
    Good for entity-level metadata in RAG"""

    tokens = word_tokenize(text)
    tagged = nltk.pos_tag(tokens)

    noun_phrases, current_np = [], []

    for word, tag in tagged:
        if tag in ("NN", "NNS", "NNP", "NNPS"):
            current_np.append(word)
        else:
            if len(current_np)>2:
                noun_phrases.append(" ".join(current_np))
                current_np = []
    
    if len(current_np)>2:
        noun_phrases.append(" ".join(current_np))
    
    return list(set(noun_phrases))[:10]

def make_doc(text, metadata):
    """ Wrap a chunk with metadata, word count, and NLTK keywords."""
    return {
        "text": text, 
        "metadata": metadata,
        "char_count": len(text),
        "word_count": len(word_tokenize(text)), 
        "keywords": extract_keywords(text),
        "sentences": len(nltk_sentences(text))
    }

def parse_search_results(raw, query):

    """ BeautifulSoup cleans HTML snippets from search results
    NLTK extracts keywords from metadata"""

    docs = []

    for rank, item in enumerate(raw,1):
        title = item.get("title", "")
        snippet = clean_html(item.get("snippet", ""))
        pageid = item.get("pageid")

        text = f"{title}. {snippet}"
        metadata = {
            "source": "wikipedia_search",
            "query": query,
            "title": title,
            "pageid": pageid,
            "rank": rank,
            "url": f"https://en.wikipedia.org/?curid={pageid}",
            "retrieved_at": datetime.utcnow().isoformat()
        }
        docs.append(make_doc(text, metadata))
    return docs

def parse_summary(raw):
    """ BeautifulSoap cleans description.
    NLTK extracts noun phrases for entity metadata."""

    title = raw.get("title", "")
    extract = clean_html(raw.get("extract", ""))
    desc = clean_html(raw.get("description", ""))

    text = f"{title} : {desc} : {extract}" if desc else f" {title} : {extract}"

    metadata = {
        "source" : "wikipedia_summary", 
        "title" : title,
        "description" : desc,
        "page_id" : raw.get("pageid"),
        "language" : raw.get("lang", "en"), 
        "url" : raw.get("content_urls", {}).get("desktop", {}).get("page", ""),
        "noun_phrases": extract_noun_phrases(text),
        "retrieved": datetime.utcnow().isoformat()
        
    }
    return [make_doc(text, metadata)]

def parse_article_content(raw, max_tokens = 512, overlap = 50):
    """ BeautifulSoup strips any embedded HTML.
     NLTK sentence tokenizer splits into proper sentence-boundary chunks. """
    
    title = raw.get("title", "")
    extract = clean_html(raw.get("extract", ""))
    pageid = raw.get("pageid")
    url = f"https://en.wikipedia.org/?curid={pageid}" if pageid else ""

    if not extract:
        return []
    
    chunks = chunk_by_sentences(extract, max_tokens, overlap)
    docs = []

    for i, chunk in enumerate(chunks):
        metadata = {
            "source": "wikipedia_content",
            "title": title,
            "page_id": pageid,
            "url": url,
            "total_chunks": len(chunks),
            "noun_phrases": extract_noun_phrases(chunk),
            "chunk_index": i,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        docs.append(make_doc(chunk, metadata))
    return docs

def parse_article_sections(raw, article_title):
    """ BeautifulSoup cleans section titles (sometimes contain HTML)
    Each section becomes a RAG doc for section-level retrieval"""

    docs = []
    for section in raw:
        number = section.get("number", "")
        title = clean_html(section.get("line", ""))

        if not title:
            continue
        text = f"{article_title} - Section {number}: {title}"

        metadata ={
            "source": "wikipedia_section",
            "article_title": article_title,
            "section_number": number,
            "section_title": title,
            "section_level": section.get("toclevel", 1),
            "anchor": section.get("anchor", ""),

            "url": (
                f"https://en.wikipedia.org/wiki/"
                f"{quote(article_title.replace(' ', '_'))}#{section.get('anchor', '')}"
            ),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        docs.append(make_doc(text, metadata))
    return docs

def parse_featured_article(raw):
    """ BeautifulSoup + NLTK sentence chunking on featured article"""

    if not raw:
        return []
    
    title = raw.get("title", "")
    extract = clean_html(raw.get("extract", ""))
    chunks = chunk_by_sentences(extract)

    docs = []
    for i, chunk in enumerate(chunks):
        metadata = {
            "source": "wikipedia_featured", 
            "title": title,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "chunk_index": i,
            "url": raw.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "retrieved_at": datetime.utcnow().isoformat()

        }
        docs.append(make_doc(chunk, metadata))
    return docs






    