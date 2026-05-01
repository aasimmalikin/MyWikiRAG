from wiki import(
    search_articles,
    get_article_summary,
    get_article_content,
    get_todays_featured_article,
    get_random_article,
    get_article_section
)

def main():
    print("\n SEARCH RESULTS for 'Artificial Intelligence':")
    results = search_articles("Artificial Intelligence", limit =3)
    for i, r in enumerate(results,1):
        print(f"{i}. {r['title']}")
    
    print("\n SUMMARY OF 'Machine Learning':")
    summary = get_article_summary("Machine Learning")
    print(f"Title: {summary['title']}")
    print(f"Extract: {summary['extract'][:200]}")
    print(f"URL: {summary['content_urls']['desktop']['page']}")

    print("\n CONTENT OF 'Large language model':")
    content = get_article_content("Large language model", intro_only=True)
    print(f"{content['extract']}")

    
    
    print("\n RANDOM ARTICLE:")
    random = get_random_article()
    print(f"  Title   : {random['title']}")
    print(f"  Extract : {random.get('extract', '')[:150]}...")

    print("\n TODAY'S FEATURED ARTICLE:")
    featured = get_todays_featured_article()
    if featured:
        print(f"  Title   : {featured['title']}")
        print(f"  Extract : {featured.get('extract', '')[:150]}...")
    
    print("\n SECTIONS of 'Large language model':")
    sections = get_article_section("Large language model")
    for sec in sections[:5]:
        print(f"  [{sec['number']}] {sec['line']}")
    
if __name__ =="__main__":
    main()


