from search.pdf_search import PDFSearchEngine

engine = PDFSearchEngine()

results = engine.search("Generative AI")

for pdf in results:

    print("--------------------------------")

    print("PDF :", pdf["filename"])

    print("Score :", pdf["score"])

    print("Content :")

    print(pdf["content"])