import streamlit as st
import networkx as nx
import pandas as pd
import tempfile

from backend.network_analysis.network_service import (
    build_analysis_graph,
    find_transaction_cycles,
    build_cycle_visualization,
    find_reciprocal_relationships,
    find_pan_path,
    find_pan_neighbors,
    build_pan_visualization
)

from backend.ai.ollama_service import (
    
    analyze_pan_explorer
)


def swap_path_pans():
    (
        st.session_state.path_source_pan,
        st.session_state.path_target_pan
    ) = (
        st.session_state.path_target_pan,
        st.session_state.path_source_pan
    )

@st.fragment
def render_pan_ai_analysis(pan_context):


    st.write(
        "Generate an evidence-based summary of the "
        "selected PAN's network structure."
    )

    if st.button(
        "🤖 Analyze PAN Network",
        use_container_width=True,
        key="analyze_pan_network"
    ):

        with st.spinner(
            "Analyzing PAN network..."
        ):

            ai_result = analyze_pan_explorer(
                pan_context
            )

        st.markdown(ai_result)

def show_network_analysis():

    st.title("🧠 PAN Network Analysis")

    st.write(
        "Analyze transaction relationships and identify "
        "meaningful network patterns between PANs."
    )

    st.divider()

    # =========================================================
    # SESSION STATE
    # =========================================================

    if "selected_cycle_graph" not in st.session_state:
        st.session_state.selected_cycle_graph = None

    if "selected_cycle" not in st.session_state:
        st.session_state.selected_cycle = None

    # =========================================================
    # BUILD NETWORK
    # =========================================================

    analysis_graph = build_analysis_graph()

    # =========================================================
    # NETWORK SUMMARY
    # =========================================================

    st.subheader("📊 Network Summary")

    col1, col2, col3 = st.columns(3)

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
    # INVESTIGATION TABS
    # =========================================================

    tab_circular, tab_path, tab_reciprocal, tab_explorer  = st.tabs(
        [
            "🔄 Circular Transactions",
            "🔗 Source → Target Path",
            "🔁 Reciprocal Relationships",
            "🕸️ PAN Explorer"
        ]
    )

    # =========================================================
    # TAB 1 — CIRCULAR TRANSACTIONS
    # =========================================================

    with tab_circular:

        st.subheader(
            "🔄 Circular Transaction Patterns"
        )

        st.write(
            "Identify transaction relationships where a path "
            "returns to the originating PAN."
        )

        cycles = find_transaction_cycles(
            analysis_graph,
            max_cycle_length=5,
            limit=100
        )

        if not cycles:

            st.info(
                "No circular transaction patterns were detected."
            )

            # Clear stale selection
            st.session_state.selected_cycle = None
            st.session_state.selected_cycle_graph = None

        else:

            # -------------------------------------------------
            # Build cycle table
            # -------------------------------------------------

            cycle_rows = []

            for index, cycle in enumerate(
                cycles,
                start=1
            ):

                path = cycle["PANs"]

                total_transactions = sum(
                    relationship["transactions"]
                    for relationship in cycle[
                        "relationships"
                    ]
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

                    "Common ISIN": (
                        ", ".join(
                            cycle.get(
                                "Common_ISINs",
                                []
                            )
                        )
                        if cycle.get(
                            "Common_ISINs",
                            []
                        )
                        else "None"
                    ),

                    "Chronological": (
                        "Yes"
                        if cycle.get(
                            "Chronological",
                            False
                        )
                        else "No"
                    ),

                    "_cycle": path,

                    "_relationships": cycle[
                        "relationships"
                    ]

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

            # -------------------------------------------------
            # Select cycle
            # -------------------------------------------------

            cycle_options = {
                row["Pattern"]:
                    row["Transaction Cycle"]
                for _, row in cycles_df.iterrows()
            }

            selected_pattern = st.selectbox(
                "Select a cycle to investigate",
                options=list(
                    cycle_options.keys()
                ),
                format_func=lambda x:
                    cycle_options[x]
            )

            # -------------------------------------------------
            # Visualize selected cycle
            # -------------------------------------------------

            if st.button(
                "🌐 Visualize Selected Cycle",
                key="visualize_cycle"
            ):

                selected_row = cycles_df[
                    cycles_df["Pattern"]
                    == selected_pattern
                ].iloc[0]

                selected_cycle = cycles[
                    selected_pattern - 1
                ]

                st.session_state.selected_cycle = (
                    selected_cycle
                )

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

            # -------------------------------------------------
            # Selected cycle analysis
            # -------------------------------------------------

            if (
                st.session_state.selected_cycle
                is not None
            ):

                selected_cycle = (
                    st.session_state.selected_cycle
                )

                st.markdown(
                    "### 📋 Cycle Analysis"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "PANs",
                    selected_cycle["Length"]
                )

                col2.metric(
                    "Transactions",
                    sum(
                        relationship["transactions"]
                        for relationship
                        in selected_cycle[
                            "relationships"
                        ]
                    )
                )

                col3.metric(
                    "Chronological",
                    (
                        "Yes"
                        if selected_cycle.get(
                            "Chronological",
                            False
                        )
                        else "No"
                    )
                )

                common_isins = (
                    selected_cycle.get(
                        "Common_ISINs",
                        []
                    )
                )

                if common_isins:

                    st.info(
                        "Common ISIN across all "
                        "relationships: "
                        + ", ".join(
                            common_isins
                        )
                    )

                else:

                    st.info(
                        "No single ISIN was observed "
                        "across all relationships "
                        "in this cycle."
                    )

                # -------------------------------------------------
                # Transaction path
                # -------------------------------------------------

                st.markdown(
                    "### 🔄 Transaction Path"
                )

                path = selected_cycle["PANs"]

                st.code(
                    " → ".join(path)
                    + " → "
                    + path[0],
                    language="text"
                )

                # -------------------------------------------------
                # Relationship details
                # -------------------------------------------------

                st.markdown(
                    "### 📋 Relationship Details"
                )

                relationship_rows = []

                for relationship in selected_cycle[
                    "relationships"
                ]:

                    relationship_rows.append({

                        "Source PAN":
                            relationship["source"],

                        "Target PAN":
                            relationship["target"],

                        "Transactions":
                            relationship.get(
                                "transactions",
                                0
                            ),

                        "Alerts":
                            len(
                                relationship.get(
                                    "alerts",
                                    []
                                )
                            )

                    })

                relationship_df = pd.DataFrame(
                    relationship_rows
                )

                st.dataframe(
                    relationship_df,
                    use_container_width=True,
                    hide_index=True
                )

                # -------------------------------------------------
                # Visualization
                # -------------------------------------------------

                st.markdown(
                    "### 🌐 Selected Pattern Visualization"
                )

                if (
                    st.session_state
                    .selected_cycle_graph
                    is not None
                ):

                    network = (
                        build_cycle_visualization(
                            st.session_state
                            .selected_cycle_graph
                        )
                    )

                    tmp = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".html"
                    )

                    network.save_graph(tmp.name)

                    with open(
                        tmp.name,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        html_content = f.read()

                    # Remove default white border/background
                    html_content = html_content.replace(
                        "</head>",
                        """
                        <style>

                        html,
                        body {
                            margin: 0 !important;
                            padding: 0 !important;
                            background: #0E1117 !important;
                            overflow: hidden !important;
                        }

                        #mynetwork {
                            border: none !important;
                            margin: 0 !important;
                            padding: 0 !important;
                        }

                        canvas {
                            border: none !important;
                        }

                        /* ---------------------------------------------
                        PyVis navigation buttons
                        --------------------------------------------- */

                        .vis-navigation .vis-button {
                            background-color: #FFFFFF !important;
                            border: 1px solid #4B5563 !important;
                            border-radius: 6px !important;
                            box-shadow: none !important;
                        }

                        .vis-navigation .vis-button:hover {
                            background-color: #374151 !important;
                            border-color: #6B7280 !important;
                        }

                        </style>
                        </head>
                        """
                    )

                    from streamlit.components.v1 import html

                    html(
                        html_content,
                        height=660,
                        scrolling=False
                    )

    # =========================================================
    # TAB 2 — SOURCE → TARGET PATH
    # =========================================================

    with tab_path:

        st.subheader(
            "🔗 Find Connection Between PANs"
        )

        st.write(
            "Find a transaction path between two PANs "
            "within the network."
        )

        col1, col2 = st.columns(2)

        with col1:

            source_pan = st.text_input(
                "Source PAN",
                placeholder="e.g. ABCDE1234F",
                key="path_source_pan"
            )

        with col2:

            target_pan = st.text_input(
                "Target PAN",
                placeholder="e.g. XYZAB5678C",
                key="path_target_pan"
            )

        st.button(
            "⇄ Swap Source ↔ Target",
            use_container_width=True,
            key="swap_pan_button",
            on_click=swap_path_pans
        )

        st.divider()

        if st.button(
            "🔎 Find Path",
            use_container_width=True,
            key="find_pan_path"
        ):

            source = source_pan.strip().upper()
            target = target_pan.strip().upper()

            if not source or not target:

                st.warning(
                    "Please enter both Source PAN and Target PAN."
                )

            else:

                with st.spinner(
                    "Searching transaction network..."
                ):

                    path_result = find_pan_path(
                        analysis_graph,
                        source,
                        target,
                        max_hops=5
                    )

                if path_result is None:

                    st.error(
                        "No transaction path was found "
                        "between the supplied PANs."
                    )

                elif path_result.get(
                    "exceeds_limit",
                    False
                ):

                    st.warning(
                        f"A path exists, but it requires "
                        f"{path_result['hops']} hops. "
                        f"The current investigation limit "
                        f"is 5 hops."
                    )

                else:

                    if source == target:

                        st.info(
                            f"The source and target are the same PAN: "
                            f"{source}. This represents a self-loop query."
                        )

                    else:

                        st.success(
                            "Transaction path found."
                        )

                    st.markdown(
                        "### 🔗 Transaction Path"
                    )

                    path = path_result["path"]

                    st.code(
                        " → ".join(path),
                        language="text"
                    )

                    col1, col2 = st.columns(2)

                    col1.metric(
                        "PANs Involved",
                        len(path)
                    )

                    col2.metric(
                        "Hops",
                        path_result["hops"]
                    )

                    st.markdown(
                        "### 📋 Path Relationships"
                    )

                    path_rows = []

                    for relationship in path_result[
                        "relationships"
                    ]:

                        path_rows.append({

                            "Source PAN":
                                relationship["source"],

                            "Target PAN":
                                relationship["target"],

                            "Transactions":
                                relationship["transactions"],

                            "Alerts":
                                relationship["alerts"],

                            "ISINs": (
                                ", ".join(
                                    relationship["isins"]
                                )
                                if relationship["isins"]
                                else "Not available"
                            )

                        })

                    path_df = pd.DataFrame(
                        path_rows
                    )

                    st.dataframe(
                        path_df,
                        use_container_width=True,
                        hide_index=True
                    )

    # =========================================================
    # TAB 3 — RECIPROCAL RELATIONSHIPS
    # =========================================================

    with tab_reciprocal:

        st.subheader(
            "🔁 Reciprocal Relationships"
        )

        st.write(
            "Identify PAN pairs that have transaction "
            "relationships in both directions."
        )

        reciprocal_relationships = (
            find_reciprocal_relationships(
                analysis_graph,
                limit=100
            )
        )

        if not reciprocal_relationships:

            st.info(
                "No reciprocal PAN relationships "
                "were detected."
            )

        else:

            reciprocal_rows = []

            for index, relationship in enumerate(
                reciprocal_relationships,
                start=1
            ):

                source = relationship["source"]
                target = relationship["target"]

                reciprocal_rows.append({

                    "Pattern": index,

                    "PAN Pair": (
                        f"{source} ↔ {target}"
                    ),

                    "Forward Transactions": (
                        relationship[
                            "forward_transactions"
                        ]
                    ),

                    "Reverse Transactions": (
                        relationship[
                            "reverse_transactions"
                        ]
                    ),

                    "Total Transactions": (
                        relationship[
                            "forward_transactions"
                        ]
                        +
                        relationship[
                            "reverse_transactions"
                        ]
                    ),

                    "_data": relationship

                })

            reciprocal_df = pd.DataFrame(
                reciprocal_rows
            )

            display_reciprocal_df = (
                reciprocal_df.drop(
                    columns=["_data"]
                )
            )

            st.dataframe(
                display_reciprocal_df,
                use_container_width=True,
                hide_index=True
            )

            reciprocal_options = {
                row["Pattern"]:
                    row["PAN Pair"]
                for _, row
                in reciprocal_df.iterrows()
            }

            selected_reciprocal = st.selectbox(
                "Select a reciprocal relationship "
                "to investigate",
                options=list(
                    reciprocal_options.keys()
                ),
                format_func=lambda x:
                    reciprocal_options[x]
            )

            selected_data = reciprocal_df[
                reciprocal_df["Pattern"]
                == selected_reciprocal
            ].iloc[0]["_data"]

            st.markdown(
                "### 🔎 Relationship Details"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"**{selected_data['source']} "
                    f"→ "
                    f"{selected_data['target']}**"
                )

                st.metric(
                    "Transactions",
                    selected_data[
                        "forward_transactions"
                    ]
                )

                st.write(
                    "**ISINs:**",
                    (
                        ", ".join(
                            selected_data[
                                "forward_isins"
                            ]
                        )
                        if selected_data[
                            "forward_isins"
                        ]
                        else "Not available"
                    )
                )

            with col2:

                st.markdown(
                    f"**{selected_data['target']} "
                    f"→ "
                    f"{selected_data['source']}**"
                )

                st.metric(
                    "Transactions",
                    selected_data[
                        "reverse_transactions"
                    ]
                )

                st.write(
                    "**ISINs:**",
                    (
                        ", ".join(
                            selected_data[
                                "reverse_isins"
                            ]
                        )
                        if selected_data[
                            "reverse_isins"
                        ]
                        else "Not available"
                    )
                )

    # =========================================================
    # TAB 4 — PAN EXPLORER
    # =========================================================

    with tab_explorer:

        st.subheader(
            "🕸️ PAN Explorer"
        )

        st.write(
            "Explore the immediate incoming and outgoing "
            "transaction relationships of a PAN."
        )

        st.divider()

        pan_input = st.text_input(
            "Search PAN",
            placeholder="e.g. ABCDE1234F",
            key="pan_explorer_input"
        )

        if st.button(
            "🔎 Explore PAN",
            use_container_width=True,
            key="explore_pan_button"
        ):

            pan = (
                pan_input
                .strip()
                .upper()
            )

            if not pan:

                st.warning(
                    "Please enter a PAN."
                )

            else:

                with st.spinner(
                    "Exploring PAN relationships..."
                ):

                    explorer_result = find_pan_neighbors(
                        analysis_graph,
                        pan
                    )

                if explorer_result is None:

                    st.error(
                        f"PAN {pan} was not found "
                        "in the transaction network."
                    )

                else:

                    st.session_state.pan_explorer_result = (
                        explorer_result
                    )

        # =====================================================
        # DISPLAY RESULT
        # =====================================================

        if (
            "pan_explorer_result"
            in st.session_state
            and
            st.session_state.pan_explorer_result
            is not None
        ):

            explorer_result = (
                st.session_state.pan_explorer_result
            )

            pan = explorer_result["pan"]

            incoming = explorer_result[
                "incoming"
            ]

            outgoing = explorer_result[
                "outgoing"
            ]

            # =================================================
            # SUMMARY
            # =================================================

            st.subheader(
                f"PAN: {pan}"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Direct Connections",
                explorer_result[
                    "total_connections"
                ]
            )

            col2.metric(
                "Incoming",
                len(incoming)
            )

            col3.metric(
                "Outgoing",
                len(outgoing)
            )

            st.divider()

            # =================================================
            # VISUALIZATION
            # =================================================

            st.subheader(
                "🌐 Direct Relationship Network"
            )

            network = build_pan_visualization(
                analysis_graph,
                pan
            )

            if network is not None:

                tmp = tempfile.NamedTemporaryFile(
                                       delete=False,
                                       suffix=".html"
                                   )
               
                network.save_graph(tmp.name)
               
                with open(
                    tmp.name,
                                       "r",
                                       encoding="utf-8"
                                   ) as f:
               
                    html_content = f.read()

                html_content = html_content.replace(
                    "</head>",
                    """
                    <style>

                    html,
                    body {
                        margin: 0 !important;
                        padding: 0 !important;
                        background: #0E1117 !important;
                        overflow: hidden !important;
                    }

                    #mynetwork {
                        border: none !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }

                    canvas {
                        border: none !important;
                    }

                    .vis-navigation .vis-button {
                        background-color: #FFFFFF !important;
                        border: 1px solid #30363D !important;
                        border-radius: 6px !important;
                        box-shadow: none !important;
                    }

                    .vis-navigation .vis-button:hover {
                        background-color: #21262D !important;
                        border-color: #58A6FF !important;
                    }

                    </style>
                    </head>
                    """
                )

                from streamlit.components.v1 import html

                html(
                    html_content,
                    height=660,
                    scrolling=False
                )

            st.divider()

            # =================================================
            # INCOMING RELATIONSHIPS
            # =================================================

            st.subheader(
                "⬅️ Incoming Relationships"
            )

            if incoming:

                incoming_rows = []

                for relationship in incoming:

                    alerts = relationship.get(
                        "alerts",
                        []
                    )

                    reporting_periods = sorted(
                        set(
                            (
                                f"{a.get('report_year')}-"
                                f"{a.get('report_month')}-"
                                f"{a.get('report_fortnight')}"
                            )
                            for a in alerts
                            if a.get("report_year") is not None
                        )
                    )

                    incoming_rows.append({

                        "Source PAN":
                            relationship["source"],

                        "Target PAN":
                            relationship["target"],

                        "Transactions":
                            relationship["transactions"],

                        "Alerts":
                            len(alerts),

                        "ISINs": (
                            ", ".join(
                                relationship.get(
                                    "isins",
                                    []
                                )
                            )
                            if relationship.get(
                                "isins"
                            )
                            else "Not available"
                        ),

                        "Reporting Periods": (
                            ", ".join(
                                reporting_periods
                            )
                            if reporting_periods
                            else "Not available"
                        )

                    })

                incoming_df = pd.DataFrame(
                    incoming_rows
                )

                st.dataframe(
                    incoming_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No incoming relationships found."
                )

            # =================================================
            # OUTGOING RELATIONSHIPS
            # =================================================

            st.subheader(
                "➡️ Outgoing Relationships"
            )

            if outgoing:

                outgoing_rows = []

                for relationship in outgoing:

                    alerts = relationship.get(
                        "alerts",
                        []
                    )

                    reporting_periods = sorted(
                        set(
                            (
                                f"{a.get('report_year')}-"
                                f"{a.get('report_month')}-"
                                f"{a.get('report_fortnight')}"
                            )
                            for a in alerts
                            if a.get("report_year") is not None
                        )
                    )

                    outgoing_rows.append({

                        "Source PAN":
                            relationship["source"],

                        "Target PAN":
                            relationship["target"],

                        "Transactions":
                            relationship["transactions"],

                        "Alerts":
                            len(alerts),

                        "ISINs": (
                            ", ".join(
                                relationship.get(
                                    "isins",
                                    []
                                )
                            )
                            if relationship.get(
                                "isins"
                            )
                            else "Not available"
                        ),

                        "Reporting Periods": (
                            ", ".join(
                                reporting_periods
                            )
                            if reporting_periods
                            else "Not available"
                        )

                    })

                outgoing_df = pd.DataFrame(
                    outgoing_rows
                )

                st.dataframe(
                    outgoing_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No outgoing relationships found."
                )

            # =========================================================
            # AI NETWORK ANALYSIS
            # =========================================================

            st.divider()

            st.subheader("🤖 AI Network Insights")

            # ---------------------------------------------------------
            # Self-loop
            # ---------------------------------------------------------

            self_loop = analysis_graph.has_edge(
                pan,
                pan
            )

            self_loop_transactions = 0

            if self_loop:

                self_loop_transactions = analysis_graph[
                    pan
                ][
                    pan
                ].get(
                    "transactions",
                    0
                )


            # ---------------------------------------------------------
            # Reciprocal relationships
            # ---------------------------------------------------------

            pan_reciprocal_relationships = [

                relationship

                for relationship in reciprocal_relationships

                if (
                    relationship["source"] == pan
                    or
                    relationship["target"] == pan
                )
            ]


            # ---------------------------------------------------------
            # Circular relationships
            # ---------------------------------------------------------

            pan_circular_patterns = [

                cycle

                for cycle in cycles

                if pan in cycle["PANs"]
            ]


            # ---------------------------------------------------------
            # Transaction totals
            # ---------------------------------------------------------

            incoming_transactions = sum(
                relationship.get(
                    "transactions",
                    0
                )
                for relationship in incoming
            )

            outgoing_transactions = sum(
                relationship.get(
                    "transactions",
                    0
                )
                for relationship in outgoing
            )


            # ---------------------------------------------------------
            # Unique ISINs
            # ---------------------------------------------------------

            all_isins = set()

            for relationship in incoming + outgoing:

                for isin in relationship.get(
                    "isins",
                    []
                ):

                    all_isins.add(isin)


            # ---------------------------------------------------------
            # AI Context
            # ---------------------------------------------------------

            pan_context = {

                "pan": pan,

                "direct_relationships": (
                    explorer_result[
                        "total_connections"
                    ]
                ),

                "incoming_relationships": len(
                    incoming
                ),

                "outgoing_relationships": len(
                    outgoing
                ),

                "incoming_transactions": (
                    incoming_transactions
                ),

                "outgoing_transactions": (
                    outgoing_transactions
                ),

                "total_transactions": (
                    incoming_transactions
                    +
                    outgoing_transactions
                ),

                "unique_isins": len(
                    all_isins
                ),

                "isin_values": sorted(
                    all_isins
                ),

                "self_loop": self_loop,

                "self_loop_transactions": (
                    self_loop_transactions
                ),

                "reciprocal_relationship": (
                    len(
                        pan_reciprocal_relationships
                    ) > 0
                ),

                "reciprocal_relationship_count": (
                    len(
                        pan_reciprocal_relationships
                    )
                ),

                "circular_transaction": (
                    len(
                        pan_circular_patterns
                    ) > 0
                ),

                "circular_pattern_count": (
                    len(
                        pan_circular_patterns
                    )
                )
            }


            render_pan_ai_analysis(
                pan_context
            )