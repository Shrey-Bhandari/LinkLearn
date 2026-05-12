import streamlit as st
from src.core.pipeline import Link2LearnPipeline


def style_page() -> None:
    st.set_page_config(
        page_title="Link2Learn",
        page_icon="📘",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .reportview-container {
            background: #f6f8fb;
        }
        .css-1d391kg {
            padding-top: 0.5rem;
        }
        .stButton>button {
            background-color:#1f77b4;
            color:#ffffff;
            border:none;
        }
        .stButton>button:hover {
            background-color:#155d8f;
        }
        .card {
            border-radius: 18px;
            border: 1px solid rgba(31, 119, 180, 0.15);
            padding: 1.2rem;
            background: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 10px 30px rgba(31, 119, 180, 0.08);
        }
        .section-title {
            color: #1f77b4;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_graph_dot(graph_data: dict) -> str:
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    if not nodes or not edges:
        return "digraph G { rankdir=LR; }"

    dot = ["digraph G {", "rankdir=LR;", "node [shape=box, style=rounded, color=\"#1f77b4\", fontname=Helvetica];"]
    for node in nodes:
        label = node.replace('"', '\\"')
        dot.append(f'"{label}";')
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        relation = edge.get("type", "related-to")
        if source and target:
            dot.append(f'"{source}" -> "{target}" [label="{relation}", fontsize=10];')
    dot.append("}")
    return "\n".join(dot)


def main() -> None:
    style_page()

    with st.sidebar:
        st.image(
            "https://raw.githubusercontent.com/LinkLearn/LinkLearn/main/docs/link2learn-logo.png",
            width=220,
        )
        st.header("Link2Learn")
        st.write("Convert educational URLs into exam-ready notes, graph insights, flashcards, and MCQs.")
        st.markdown("---")
        st.write("**How it works**")
        st.write(
            "1. Scrapes and cleans web content\n"
            "2. Extracts academic concepts\n"
            "3. Builds a knowledge graph\n"
            "4. Generates flashcards and MCQs"
        )
        st.markdown("---")
        st.caption("Tip: paste 1-3 educator-focused URLs for best results.")

    st.title("Link2Learn Learning Pipeline")
    st.markdown(
        "Use the workspace below to enter educational web URLs and generate structured learning artifacts that are ready for exam preparation."
    )

    input_urls = st.text_area(
        "Educational URLs",
        value="https://www.geeksforgeeks.org/cpp/unordered_map-in-cpp-stl/",
        height=130,
        help="Enter one URL per line. Focus on technical or educational article pages.",
    )

    use_groq = st.checkbox("Enable Groq API generation", value=False)
    submitted = st.button("Generate Learning Artifacts")

    if submitted:
        urls = [line.strip() for line in input_urls.splitlines() if line.strip()]
        if not urls:
            st.error("Please enter at least one URL.")
            return

        with st.spinner("Processing URLs and assembling exam-ready artifacts..."):
            pipeline = Link2LearnPipeline(use_groq=use_groq)
            result = pipeline.process_urls(urls)

        st.success("Pipeline complete.")
        st.markdown("---")

        st.subheader("Output Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Notes", len(result.notes))
        col2.metric("Flashcards", len(result.flashcards))
        col3.metric("MCQs", len(result.mcqs))

        st.markdown("---")

        with st.expander("Notes and Concept Summaries", expanded=True):
            for note in result.notes:
                st.markdown(f"<div class=\"card\"> <h4 class=\"section-title\">{note.heading}</h4> <p>{note.definition}</p> <p><strong>Source:</strong> {note.source_url}</p> </div>", unsafe_allow_html=True)

        with st.expander("Knowledge Graph", expanded=True):
            graph_dot = build_graph_dot(result.graph.model_dump())
            st.graphviz_chart(graph_dot)

        with st.expander("Flashcards", expanded=False):
            for card in result.flashcards:
                st.markdown(
                    f"<div class=\"card\"><strong>{card.type.title()}:</strong> {card.question}<br><em>{card.answer}</em></div>",
                    unsafe_allow_html=True,
                )

        with st.expander("MCQs", expanded=False):
            for mcq in result.mcqs:
                st.markdown(
                    f"<div class=\"card\"><strong>{mcq.question}</strong><br>Options: {', '.join(mcq.options)}<br><strong>Answer:</strong> {mcq.correct} <span style=\"color:#1f77b4;\">({mcq.difficulty})</span></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.caption("Link2Learn is optimized for educational content with clear concept structure and example-driven reasoning.")


if __name__ == "__main__":
    main()
