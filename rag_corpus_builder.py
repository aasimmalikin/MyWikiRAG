import json
import wiki
import wiki_parser as parser


def build_rag_corpus(topic: str) -> list:
    """Builds corpus for a single topic string."""
    all_docs = []
    try:
        all_docs += parser.parse_search_results(
            wiki.search_articles(topic, limit=5), topic
        )
        all_docs += parser.parse_article_content(
            wiki.get_article_content(topic)
        )
        all_docs += parser.parse_summary(
            wiki.get_article_summary(topic)
        )
        all_docs += parser.parse_article_sections(
            wiki.get_article_section(topic), topic
        )
    except Exception as e:
        print(f"  ✗ Failed for '{topic}': {e}")
    return all_docs


def deduplicate(docs: list) -> list:
    seen, unique = set(), []
    for doc in docs:
        key = doc["text"][:120]
        if key not in seen and doc["char_count"] >= 50:
            seen.add(key)
            unique.append(doc)
    return unique


if __name__ == "__main__":

    topics = [
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning",
        "Natural Language Processing",
        "Computer Vision",
        "Reinforcement Learning",
        "Generative AI",
        "AI Ethics",
        "AI in Healthcare",
        "AI in Finance",
        "Supervised Learning",
        "Unsupervised Learning",
        "Transfer Learning",
        "AI in Robotics",
        "AI in Education",
        "Data Augmentation",
        "Fine-Tuning",
        "Neural Network",
        "Transformer Models",
        "Convolutional Neural Network",
        "Recurrent Neural Network",
        "Large Language Model",
        "RAG",
        "AI startups in Benguluru"
    ]

    all_docs = []

    # ── Loop through each topic ──────────────
    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] Fetching: {topic}")
        topic_docs = build_rag_corpus(topic)
        all_docs += topic_docs
        print(f"        → {len(topic_docs)} docs fetched")

    # ── Deduplicate across all topics ───────────────────
    docs = deduplicate(all_docs)
    print(f"\n✅ {len(docs)} unique documents after deduplication\n")

    # ── Featured article (once, not per topic) ──────────
    try:
        featured = wiki.get_todays_featured_article()
        if featured:
            featured_docs = parser.parse_featured_article(featured)
            docs += featured_docs
            print(f"  + {len(featured_docs)} featured article doc(s) added")
    except Exception as e:
        print(f"  ✗ Featured article failed: {e}")

    # ── Print summary ────────────────────────────────────
    for doc in docs:
        print("─" * 60)
        print(f"  source    : {doc['metadata']['source']}")
        print(f"  title     : {doc['metadata'].get('title')}")
        print(f"  url       : {doc['metadata'].get('url')}")
        print(f"  chunk     : {doc['metadata'].get('chunk_index')}")
        print(f"  words     : {doc['word_count']}")
        print(f"  sentences : {doc['sentences']}")
        print(f"  keywords  : {doc['keywords']}")
        print(f"  text      : {doc['text'][:150]}...")

    # ── Save ─────────────────────────────────────────────
    with open("rag_corpus_nlp.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    print("\n💾 Saved → rag_corpus_nlp.json")