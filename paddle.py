import streamlit as st
import pandas as pd
import plotly.express as px

# Page title
st.title("Paddle Sales Dashboard FY2025")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("paddle_opp_data")

df = load_data()

# Rename 'Customer_Size' to 'Customer_Segment'
df = df.rename(columns={"Company_Size": "Customer_Segment"})

# Sidebar Filters
with st.sidebar:
    st.header("Filters")
    region_options = df["Region"].unique()
    selected_regions = st.multiselect("Select Region(s):", options=region_options, default=region_options)

    segment_options = df["Customer_Segment"].unique()
    selected_segments = st.multiselect("Select Segment(s):", options=segment_options, default=segment_options)

# Apply global filters (Region and Customer Segment)
filtered_data = df[
    (df["Region"].isin(selected_regions)) &
    (df["Customer_Segment"].isin(selected_segments))
]

### ---- SECTION 1: PIPELINE ANALYSIS ----
with st.expander("📊 Pipeline Analysis"):
    # ---- Pipeline Value by Region ----
    st.subheader("Pipeline Value by Region")
    total_pipeline = filtered_data[~filtered_data["Deal_Stage"].isin(["Closed Won", "Closed Lost"])]
    regional_pipeline = total_pipeline.groupby("Region").agg(
        Total_Pipeline_Value=("Deal_Size", "sum"),
        Total_Open_Deals=("Deal_ID", "count"),
        Avg_Pipeline_Deal_Size=("Deal_Size", "mean")
    ).reset_index()

    # Yellow bar graph for brand consistency
    fig_pipeline = px.bar(
        regional_pipeline,
        x="Region",
        y="Total_Pipeline_Value",
        text="Total_Pipeline_Value",
        title="Pipeline Value by Region",
        labels={"Total_Pipeline_Value": "Total Value (£)", "Region": "Region"},
        template="plotly_white"
    )
    fig_pipeline.update_traces(marker_color="yellow", texttemplate='%{text:.2s}', textposition="outside")
    st.plotly_chart(fig_pipeline)

    # ---- Pipeline by Deal Stage ----
    st.subheader("Pipeline by Deal Stage")

    # Filter data to exclude Closed Won and Closed Lost
    stage_filtered_data = filtered_data[~filtered_data["Deal_Stage"].isin(["Closed Won", "Closed Lost"])]

    # Grouping and aggregating the data
    stage_summary = stage_filtered_data.groupby("Deal_Stage").agg(
        Total_Value=("Deal_Size", "sum")
    ).reset_index()

    # Bar Chart: Pipeline by Deal Stage with Correct Figures
    fig_stage = px.bar(
        stage_summary,
        x="Deal_Stage",
        y="Total_Value",
        title="Pipeline by Deal Stage",
        labels={"Total_Value": "Total Value (£)", "Deal_Stage": "Stage"},
        template="plotly_white"
    )

    # Fixing the issue with values above bars by converting to readable strings
    fig_stage.update_traces(
        marker_color="yellow", 
        text=stage_summary["Total_Value"].apply(lambda x: f"£{x:,.0f}"),
        texttemplate='%{text}', 
        textposition="outside"
    )

    # Displaying the corrected chart within the expander
    st.plotly_chart(fig_stage)

### ---- SECTION 2: LEAD SOURCE ANALYSIS ----
with st.expander("📈 Lead Source Analysis"):
    st.subheader("Total Deal Value by Lead Source")
    lead_source_summary = filtered_data.groupby("Lead_Source").agg(
        Total_Deals=("Deal_ID", "count"),
        Total_Deal_Value=("Deal_Size", "sum")
    ).reset_index()

    fig_lead_source = px.bar(
        lead_source_summary,
        x="Lead_Source",
        y="Total_Deal_Value",
        text="Total_Deal_Value",
        title="Total Deal Value by Lead Source",
        labels={"Total_Deal_Value": "Total Value (£)", "Lead_Source": "Lead Source"},
        template="plotly_white"
    )
    fig_lead_source.update_traces(marker_color="yellow", texttemplate='%{text:.2s}', textposition="outside")
    st.plotly_chart(fig_lead_source)

    # Pie chart remains unchanged
    st.subheader("Deal Count by Lead Source")
    fig_lead_source_pie = px.pie(
        lead_source_summary,
        names="Lead_Source",
        values="Total_Deals",
        title="Deal Count by Lead Source",
        template="plotly_white"
    )
    st.plotly_chart(fig_lead_source_pie)

### ---- SECTION 3: CUSTOMER SEGMENT ANALYSIS ----
with st.expander("🧩 Customer Segment Analysis"):
    st.subheader("Total Deal Value by Customer Segment")

    # Summary table for Customer Segment Analysis
    segment_summary = filtered_data.groupby("Customer_Segment").agg(
        Total_Deals=("Deal_ID", "count"),
        Total_Deal_Value=("Deal_Size", "sum"),
        Avg_Deal_Value=("Deal_Size", "mean")
    ).reset_index()

    # Bar Chart: Total Deal Value by Customer Segment
    fig_segment = px.bar(
        segment_summary,
        x="Customer_Segment",
        y="Total_Deal_Value",
        text="Total_Deal_Value",
        title="Total Deal Value by Customer Segment",
        labels={"Total_Deal_Value": "Total Value (£)", "Customer_Segment": "Customer Segment"},
        template="plotly_white"
    )
    fig_segment.update_traces(marker_color="yellow", texttemplate='%{text:.2s}', textposition="outside")
    st.plotly_chart(fig_segment)

    # ---- Deal Size Distribution by Customer Segment ----
    st.subheader("Deal Size Distribution by Customer Segment")

    # Allow multiple segment selection
    selected_deal_segments = st.multiselect(
        "Filter by Customer Segment:", 
        options=segment_options, 
        default=segment_options,
        key="segment_filter_box"
    )

    # Filter the data based on multiple selections
    segment_filtered_data = filtered_data[filtered_data["Customer_Segment"].isin(selected_deal_segments)]

    # Box Plot: Deal Size Distribution with Multiple Segment Filtering
    fig_segment_box = px.box(
        segment_filtered_data,
        x="Customer_Segment",
        y="Deal_Size",
        title="Deal Size Distribution by Customer Segment",
        labels={"Deal_Size": "Deal Size (£)", "Customer_Segment": "Customer Segment"},
        template="plotly_white"
    )

    # Apply Paddle's brand color
    fig_segment_box.update_traces(marker_color="yellow")

    # Display the chart
    st.plotly_chart(fig_segment_box)




### ---- SECTION 4: SALESPERSON PERFORMANCE ----
with st.expander("💼 Salesperson Performance"):
    st.markdown("#### Filter by Deal Stage")
    table_stage_options = filtered_data["Deal_Stage"].unique()
    selected_table_stages = st.multiselect(
        "Select Deal Stage(s):",
        options=table_stage_options,
        default=table_stage_options,
        key="deal_stage_table_filter"
    )

    # Interactive Salesperson Performance Table
    table_filtered_data = filtered_data[filtered_data["Deal_Stage"].isin(selected_table_stages)]
    salesperson_summary = table_filtered_data.groupby("Salesperson").agg(
        Total_Deals=("Deal_ID", "count"),
        Total_Deal_Value=("Deal_Size", "sum"),
        Avg_Deal_Value=("Deal_Size", "mean")
    ).reset_index()

    # Display table and download option
    st.dataframe(salesperson_summary, use_container_width=True)
    st.download_button(
        label="Download Table as CSV",
        data=salesperson_summary.to_csv(index=False).encode("utf-8"),
        file_name="salesperson_performance.csv",
        mime="text/csv"
    )


# ---- SECTION 5: REVENUE ANALYSIS ----
with st.expander("📊 Revenue Analysis"):
    
    # ---- Key Revenue Metrics (Updated and Reorganized) ----
    st.subheader("Key Revenue Metrics")

    # Ensure 'Deal_Closure_Date' is a datetime object and filter invalid values
    filtered_data["Deal_Closure_Date"] = pd.to_datetime(
        filtered_data["Deal_Closure_Date"], errors="coerce"
    )

    # Remove rows where 'Deal_Closure_Date' could not be converted
    filtered_data = filtered_data.dropna(subset=["Deal_Closure_Date"])

    # Filter only Closed Won deals for revenue metrics
    closed_won_filtered = filtered_data[filtered_data["Deal_Stage"] == "Closed Won"]

    # Win Rate Calculation (Closed Won / Total Deals)
    total_deals = filtered_data["Deal_ID"].nunique()
    total_closed_won = closed_won_filtered["Deal_ID"].nunique()
    win_rate = (total_closed_won / total_deals) * 100 if total_deals > 0 else 0

    # Calculations for Key Metrics
    total_revenue = closed_won_filtered["Deal_Size"].sum()
    avg_deal_size = closed_won_filtered["Deal_Size"].mean()

    # Display Key Metrics using two rows for better layout
    col1, col2 = st.columns(2)
    col1.metric("Total Revenue", f"£{total_revenue:,.0f}")
    col2.metric("Average Deal Size", f"£{avg_deal_size:,.0f}")

    # Second row for Closed Won Deals and Win Rate
    col3, col4 = st.columns(2)
    col3.metric("Total Closed Won Deals", total_closed_won)
    col4.metric("Win Rate", f"{win_rate:.2f}%")

    # ---- Revenue Over Time ----
    st.subheader("Revenue Over Time")

    # Add a Quarter column to display in hover tooltips
    closed_won_filtered["Quarter"] = closed_won_filtered["Deal_Closure_Date"].dt.to_period("Q").astype(str)

    # Group by quarter for the line chart
    revenue_by_quarter_filtered = closed_won_filtered.groupby("Quarter").agg(
        Total_Revenue=("Deal_Size", "sum")
    ).reset_index().sort_values("Quarter")

    # Line Chart: Cumulative Closed Won Revenue Over Time (Yellow Line)
    fig_revenue_time_filtered = px.line(
        revenue_by_quarter_filtered,
        x="Quarter",
        y="Total_Revenue",
        title="Cumulative Closed Won Revenue Over Time",
        labels={"Quarter", "Quarter", "Total Revenue (£)"},
        template="plotly_dark",
        markers=True
    )
    fig_revenue_time_filtered.update_traces(line=dict(color="yellow", width=3))
    st.plotly_chart(fig_revenue_time_filtered)

    # ---- Revenue by Region ----
    st.subheader("Revenue by Region")

    # Group by Region for the bar chart
    regional_revenue = closed_won_filtered.groupby("Region").agg(
        Total_Revenue=("Deal_Size", "sum")
    ).reset_index()

    # Bar Chart: Revenue by Region (Yellow Bars)
    fig_regional_revenue = px.bar(
        regional_revenue,
        x="Region",
        y="Total_Revenue",
        text="Total_Revenue",
        title="Total Closed Won Revenue by Region",
        labels={"Total_Revenue": "Total Revenue (£)", "Region": "Region"},
        template="plotly_white"
    )
    fig_regional_revenue.update_traces(
        marker_color="yellow",  
        texttemplate='%{text:.2s}', textposition="outside"
    )
    st.plotly_chart(fig_regional_revenue)

    # ---- Revenue by Segment ----
    st.subheader("Revenue by Customer Segment")

    # Group data for revenue by segment analysis
    revenue_by_segment = closed_won_filtered.groupby("Customer_Segment").agg(
        Total_Revenue=("Deal_Size", "sum")
    ).reset_index()

    # Bar Chart: Total Closed Won Revenue by Segment (Yellow Bar)
    fig_revenue_segment = px.bar(
        revenue_by_segment,
        x="Customer_Segment",
        y="Total_Revenue",
        text="Total_Revenue",
        title="Total Closed Won Revenue by Customer Segment",
        labels={"Total_Revenue": "Total Revenue (£)", "Customer_Segment": "Segment"},
        template="plotly_white"
    )

    # Apply Paddle's yellow branding
    fig_revenue_segment.update_traces(
        marker_color="yellow",
        texttemplate='%{text:.2s}', 
        textposition="outside"
    )
    st.plotly_chart(fig_revenue_segment)

