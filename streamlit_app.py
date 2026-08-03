import tempfile
import joblib
import streamlit as st

from src.core.parser import PDFParser
from src.core.section_detector import SectionDetector
from src.core.metadata_builder import MetadataBuilder

from src.retrieval.chunker import SectionChunker
from src.retrieval.embeddings import EmbeddingGenerator
from src.retrieval.vector_store import VectorStore
from src.retrieval.retriever import Retriever

from src.generation.gemini_client import GeminiClient


# ------------------------------------------------------------
# Page Config
# ------------------------------------------------------------

st.set_page_config(
    page_title="Structure-Aware Research Paper Assistant",
    page_icon="📄",
    layout="wide"
)

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:

    st.title("📄 Research Paper")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )

    st.divider()

    st.subheader("💡 Sample Questions")

    st.markdown("""
- What is Transformer?
- What is Self Attention?
- Explain Multi Head Attention.
- What is Positional Encoding?
- What problem does the paper solve?
- Explain the Encoder.
""")

    st.divider()

    st.caption(
        "Built using\n\n"
        "- PyMuPDF\n"
        "- Sentence Transformers\n"
        "- FAISS\n"
        "- Gemini\n"
        "- Streamlit"
    )

# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

st.title("🤖 Structure-Aware Research Paper Assistant")

st.caption(
    "Upload any research paper and ask questions using semantic retrieval and Gemini."
)

# ------------------------------------------------------------
# Upload
# ------------------------------------------------------------

if uploaded_file is not None:

    if (
        "processed_file" not in st.session_state
        or st.session_state.processed_file != uploaded_file.name
    ):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(uploaded_file.read())

            pdf_path = tmp.name

        with st.spinner("Processing research paper..."):

            parser = PDFParser(pdf_path)

            total_pages = parser.get_total_pages()

            all_lines = []
            all_spans = []

            for page in range(total_pages):

                all_lines.extend(
                    parser.extract_lines(page)
                )

                all_spans.extend(
                    parser.extract_spans(page)
                )

            detector = SectionDetector()

            headings = detector.detect_sections(
                all_lines
            )

            builder = MetadataBuilder()

            sections = builder.build_sections(
                all_spans,
                headings
            )

            chunker = SectionChunker(
                chunk_size=800,
                overlap=100
            )

            chunks = chunker.chunk_sections(
                sections
            )

            embedder = EmbeddingGenerator()

            embeddings = embedder.embed_chunks(
                chunks
            )

            vector_store = VectorStore()

            vector_store.build_index(
                embeddings
            )

            vector_store.save_index()

            joblib.dump(
                chunks,
                "data/chunks.pkl"
            )

            st.session_state.processed_file = uploaded_file.name

            st.session_state.pages = total_pages

            st.session_state.num_chunks = len(chunks)

        st.success(
            f"✅ {uploaded_file.name} processed successfully!"
        )

    # --------------------------------------------------------
    # Paper Stats
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Pages",
            st.session_state.pages
        )

    with c2:
        st.metric(
            "Chunks",
            st.session_state.num_chunks
        )

    st.divider()

    # --------------------------------------------------------
    # Question
    # --------------------------------------------------------

    question = st.text_input(
        "Ask a Question",
        placeholder="Example: What is self attention?"
    )

    if st.button(
        "🔍 Ask Question",
        use_container_width=True
    ):

        if question.strip():

            with st.spinner("Searching the paper..."):

                retriever = Retriever()

                retriever.load()

                chunks = joblib.load(
                    "data/chunks.pkl"
                )

                results = retriever.retrieve(
                    question,
                    chunks,
                    top_k=3
                )

                gemini = GeminiClient()

                answer = gemini.generate_answer(
                    question,
                    results
                )

            st.divider()

            st.subheader("🤖 Answer")

            st.info(answer)

            st.divider()

            st.subheader("Retrieved Sections")

            for i, result in enumerate(results, start=1):

                chunk = result["chunk"]

                with st.expander(
                    f"📄 {i}. {chunk['title']} (Page {chunk['page']+1})"
                ):

                    c1, c2 = st.columns([3,1])

                    with c1:

                        st.write(
                            f"**Page:** {chunk['page']+1}"
                        )

                    with c2:

                        st.metric(
                            "Similarity",
                            f"{result['score']:.2f}"
                        )

                    st.markdown("---")

                    st.write(chunk["content"])

else:

    st.info(
        "Upload a research paper from the sidebar to get started."
    )

st.divider()

st.caption(
    "Structure-Aware Research Paper Assistant | "
    "PyMuPDF • Sentence Transformers • FAISS • Gemini • Streamlit"
)