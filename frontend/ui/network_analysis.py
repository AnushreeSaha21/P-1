import streamlit as st
import networkx as nx
import pandas as pd

from backend.network_analysis.network_service import (
    build_analysis_graph,
    find_transaction_cycles
)


def show_network_analysis():

    st.title("🧠 PAN Network Analysis")

    st.write(
        "Analyze transaction relationships and identify "
        "meaningful network patterns between PANs."
    )

    st.divider()

    
    if "selected_cycle_graph" not in st.session_state:
        st.session_state.selected_cycle_graph = None

    # =========================================================
    # NETWORK SUMMARY
    # =========================================================

    st.subheader("📊 Network Summary")

    col1, col2, col3 = st.columns(3)

    analysis_graph = build_analysis_graph()

    col1.metric(
        "PANs",
        analysis_graph.number_of_nodes()
    )

    col2.metric(
        "Relationships",
        analysis_graph.number_of_edges()
    )

    col3.metric(
        "Connected Components",
        nx.number_weakly_connected_components(
            analysis_graph
        )
    )

    st.divider()

    # =========================================================
    # CIRCULAR TRANSACTION PATTERNS
    # =========================================================

    st.subheader("🔄 Circular Transaction Patterns")

    cycles = find_transaction_cycles(
        analysis_graph,
        max_cycle_length=5,
        limit=100
    )

    if not cycles:

        st.info(
            "No circular transaction patterns were detected."
        )

    else:

        cycle_rows = []

        for index, cycle in enumerate(
            cycles,
            start=1
        ):

            path = cycle["PANs"]

            total_transactions = sum(
                relationship["transactions"]
                for relationship in cycle["relationships"]
            )

            cycle_rows.append({

                "Pattern": index,

                "Transaction Cycle": (
                    " → ".join(path)
                    + " → "
                    + path[0]
                ),

                "PANs": cycle["Length"],

                "Transactions": total_transactions,

                "_cycle": path,

                "_relationships": cycle["relationships"]

            })

        cycles_df = pd.DataFrame(
            cycle_rows
        )

        display_cycles_df = cycles_df.drop(
            columns=[
                "_cycle",
                "_relationships"
            ]
        )

        st.dataframe(
            display_cycles_df,
            use_container_width=True,
            hide_index=True
        )

        cycle_options = {
            row["Pattern"]: row["Transaction Cycle"]
            for _, row in cycles_df.iterrows()
        }

        selected_pattern = st.selectbox(
            "Select a cycle to investigate",
            options=list(cycle_options.keys()),
            format_func=lambda x: cycle_options[x]
        )

        if st.button(
            "🌐 Visualize Selected Cycle"
        ):

            selected_row = cycles_df[
                cycles_df["Pattern"] == selected_pattern
            ].iloc[0]

            relationships = selected_row[
                "_relationships"
            ]

            cycle_graph = nx.DiGraph()

            for relationship in relationships:

                cycle_graph.add_edge(

                    relationship["source"],

                    relationship["target"],

                    transactions=relationship[
                        "transactions"
                    ],

                    alerts=relationship[
                        "alerts"
                    ]

                )

            st.session_state.selected_cycle_graph = (
                cycle_graph
            )

    # ---------------------------------------------------------
    # Selected cycle information
    # ---------------------------------------------------------

    if st.session_state.selected_cycle_graph is not None:

        cycle_graph = (
            st.session_state.selected_cycle_graph
        )

        st.subheader("🌐 Selected Cycle")

        st.write(
            f"**PANs involved:** "
            f"{cycle_graph.number_of_nodes()}"
        )

        st.write(
            f"**Relationships:** "
            f"{cycle_graph.number_of_edges()}"
        )

    st.divider()

    
    # =========================================================
    # RECIPROCAL RELATIONSHIPS
    # =========================================================

    st.subheader("🔁 Reciprocal Relationships")

    st.info(
        "Reciprocal PAN relationships will appear here."
    )

    st.divider()

    # =========================================================
    # MULTI-HOP PATHS
    # =========================================================

    st.subheader("🔗 Multi-Hop Transaction Paths")

    st.info(
        "Transaction paths will appear here."
    )

    st.divider()

    # =========================================================
    # PAN CONNECTION SEARCH
    # =========================================================

    st.subheader("🔎 Find Connection Between PANs")

    col1, col2 = st.columns(2)

    with col1:

        source_pan = st.text_input(
            "Source PAN",
            placeholder="e.g. ABCDE1234F"
        )

    with col2:

        target_pan = st.text_input(
            "Target PAN",
            placeholder="e.g. XYZAB5678C"
        )

    if st.button(
        "🔎 Find Path",
        use_container_width=True
    ):

        if not source_pan or not target_pan:

            st.warning(
                "Please enter both Source PAN and Target PAN."
            )

        else:

            st.info(
                f"Path analysis will be performed between "
                f"{source_pan.strip().upper()} and "
                f"{target_pan.strip().upper()}."
            )

    st.divider()

    # =========================================================
    # SELECTED PATTERN VISUALIZATION
    # =========================================================

    st.subheader("🌐 Selected Pattern")

    st.info(
        "A selected transaction pattern will be visualized here."
    )

    st.divider()

    # =========================================================
    # AI ANALYSIS
    # =========================================================

    st.subheader("🤖 AI Network Insights")

    st.info(
        "AI analysis will be added after the network "
        "patterns are implemented."
    )






    st.divider()

    if st.button("🧪 Test Network Analysis"):

        st.write(
            "Nodes:",
            analysis_graph.number_of_nodes()
        )

        st.write(
            "Relationships:",
            analysis_graph.number_of_edges()
        )

        st.write(
            "Cycles detected:",
            len(cycles)
        )

        if cycles:

            st.json(
                cycles[0]
            )