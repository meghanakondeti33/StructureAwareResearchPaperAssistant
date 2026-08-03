"""
app.py

Main pipeline for the Structure-Aware Multimodal Research Paper Assistant.

Author: Meghana
"""
import joblib
from src.core.parser import PDFParser
from src.core.section_detector import SectionDetector
from src.core.metadata_builder import MetadataBuilder

from src.retrieval.chunker import SectionChunker
from src.retrieval.embeddings import EmbeddingGenerator
from src.retrieval.vector_store import VectorStore
from src.retrieval.retriever import Retriever

from src.generation.gemini_client import GeminiClient


def main():

    print("=" * 80)
    print("Structure-Aware Research Paper Assistant")
    print("=" * 80)

    # ---------------------------------------------------------
    # Load PDF
    # ---------------------------------------------------------

    parser = PDFParser("data/papers/attention.pdf")

    total_pages = parser.get_total_pages()

    print(f"\nTotal Pages : {total_pages}")

    # ---------------------------------------------------------
    # Extract Lines & Spans
    # ---------------------------------------------------------

    all_lines = []
    all_spans = []

    for page in range(total_pages):

        all_lines.extend(
            parser.extract_lines(page)
        )

        all_spans.extend(
            parser.extract_spans(page)
        )

    # ---------------------------------------------------------
    # Heading Detection
    # ---------------------------------------------------------

    detector = SectionDetector()

    headings = detector.detect_sections(all_lines)

    print(f"\nDetected Headings : {len(headings)}")

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    builder = MetadataBuilder()

    sections = builder.build_sections(
        all_spans,
        headings
    )

    print(f"Metadata Sections : {len(sections)}")

    # ---------------------------------------------------------
    # Chunking
    # ---------------------------------------------------------

    chunker = SectionChunker(
        chunk_size=800,
        overlap=100
    )

    chunks = chunker.chunk_sections(
    sections
)

    print(f"Generated Chunks : {len(chunks)}")

    # Save chunks for Streamlit
    joblib.dump(chunks, "data/chunks.pkl")
    print("Chunks saved to data/chunks.pkl")

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    print("\nGenerating embeddings...")

    embedder = EmbeddingGenerator()

    embeddings = embedder.embed_chunks(chunks)

    print(f"Embedding Shape : {embeddings.shape}")

    # ---------------------------------------------------------
    # Build FAISS Index
    # ---------------------------------------------------------

    vector_store = VectorStore()

    vector_store.build_index(embeddings)

    vector_store.save_index()

    # ---------------------------------------------------------
    # Retriever
    # ---------------------------------------------------------

    retriever = Retriever()

    retriever.load()

    # ---------------------------------------------------------
    # Gemini
    # ---------------------------------------------------------

    gemini = GeminiClient()

    print("\n" + "=" * 80)

    while True:

        question = input("\nAsk a question (type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        results = retriever.retrieve(
            question,
            chunks,
            top_k=3
        )

        print("\nRetrieving relevant sections...\n")

        answer = gemini.generate_answer(
            question,
            results
        )

        print("=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(answer)

        print("\n" + "=" * 80)
        print("Retrieved Sections")
        print("=" * 80)

        for i, result in enumerate(results):

            chunk = result["chunk"]

            print(f"\n{i+1}. {chunk['title']}")

            print(f"Page : {chunk['page']+1}")

            print(f"Similarity : {result['score']:.4f}")

    print("\nThank you for using the Research Paper Assistant!")


if __name__ == "__main__":
    main()