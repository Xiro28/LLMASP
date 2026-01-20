import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os
import re

# --- PATH CONFIGURATION ---
BASE_RESULT_DIR = "../../experiments/results/" 
DATASET_PATH = "../../experiments/dataset/dataset.json"

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="LLMASP", layout="wide")

# --- UTILITY FUNCTIONS ---

def load_json_from_path(path):
    """Loads a JSON file from a local path."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File not found: {path}")
        return None
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON: {path}")
        return None

def parse_datalog_facts(text):
    """Extracts datalog facts from a string (Robust Regex Version)."""
    if not isinstance(text, str):
        return [], False
    clean_text = text.replace('\n', ' ').strip()
    if not clean_text:
        return [], False
    
    # Improved regex to capture predicates (e.g., edge(n1, n2).)
    pattern = r"\w+\([a-zA-Z0-9_]+(?:,\s*[a-zA-Z0-9_]+)*\)\."
    raw_facts = re.findall(pattern, clean_text)
    
    # Fallback if regex fails but text exists
    if not raw_facts and clean_text:
         raw_facts = [f.strip() for f in clean_text.split('.') if f.strip()]

    has_duplicates = len(raw_facts) != len(set(raw_facts))
    return raw_facts, has_duplicates

def calculate_metrics(ground_truth_str, predicted_str):
    """Calculates set-based metrics."""
    gt_list, _ = parse_datalog_facts(ground_truth_str)
    pred_list, has_duplicates = parse_datalog_facts(predicted_str)
    
    gt_set = set(gt_list)
    pred_set = set(pred_list)
    
    tp = len(gt_set.intersection(pred_set))
    fp = len(pred_set - gt_set)
    fn = len(gt_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    union = len(gt_set.union(pred_set))
    accuracy = tp / union if union > 0 else 0.0
    is_perfect = (f1 == 1.0) and (not has_duplicates)
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "accuracy": accuracy,
        "has_duplicates": has_duplicates,
        "is_perfect": is_perfect
    }

def process_data(dataset_json, result_json, model_name="Model"):
    instance_rows = []
    problem_rows = []
    
    # Map dataset
    dataset_map = {}
    for item in dataset_json:
        p_name = item.get("problem_name")
        if p_name not in dataset_map:
            dataset_map[p_name] = []
        dataset_map[p_name].append(item.get("output", ""))

    for problem_name, problem_data in result_json.items():
        if problem_name in ["final_data", "debug_info"]:
            continue
            
        predictions = problem_data.get("results", [])
        ground_truths = dataset_map.get(problem_name, [])
        
        # --- AGGREGATED DATA (Problem Level) ---
        llm_calls = problem_data.get("llm_calls", 0)
        solver_calls = problem_data.get("solver_calls", 0)
        
        c_hit_m = problem_data.get("cache_hits_monotone", 0)
        c_miss_m = problem_data.get("cache_miss_monotone", 0)
        c_hit_nm = problem_data.get("cache_hits_non_monotone", 0)
        c_miss_nm = problem_data.get("cache_miss_non_monotone", 0)
        
        total_hits = c_hit_m + c_hit_nm
        total_misses = c_miss_m + c_miss_nm
        total_reqs = total_hits + total_misses
        hit_rate = (total_hits / total_reqs * 100) if total_reqs > 0 else 0
        
        prob_row = {
            "Model": model_name,
            "Problem": problem_name,
            "Energy (uJ)": problem_data.get("total_energy_uJ", 0),
            "Time (s)": problem_data.get("total_time_seconds", 0),
            "Tokens In": problem_data.get("llm_tokens_in", 0),
            "Tokens Out": problem_data.get("llm_tokens_out", 0),
            "LLM Calls": llm_calls,
            "Solver Calls": solver_calls,
            "Cache Hits (Monotone)": c_hit_m,
            "Cache Hits (Non-Mono)": c_hit_nm,
            "Cache Misses": total_misses,
            "Total Hits": total_hits,
            "Hit Rate %": hit_rate
        }
        problem_rows.append(prob_row)
        
        # --- INSTANCE DATA (Instance Level) ---
        limit = min(len(predictions), len(ground_truths))
        for i in range(limit):
            gt = ground_truths[i]
            pred = predictions[i]
            metrics = calculate_metrics(gt, pred)
            
            inst_row = {
                "Model": model_name,
                "Problem": problem_name,
                "Instance ID": i,
                **metrics
            }
            instance_rows.append(inst_row)
            
    return pd.DataFrame(instance_rows), pd.DataFrame(problem_rows)

# --- FILE PARSING HELPERS ---

def get_file_metadata(filename):
    """
    Parses the filename to extract metadata.
    Expected format parts: 8b/70b, a1/a2, conditional/nonconditional, cached/noncached
    """
    # 1. Model Size
    if "70b" in filename: model = "70B"
    elif "8b" in filename: model = "8B"
    else: model = "Unknown"
    
    # 2. Strategy
    if "a2" in filename: strategy = "A2 (PBD)"
    elif "a1" in filename: strategy = "A1 (Std)"
    else: strategy = "Unknown"
    
    # 3. Condition
    # Check 'nonconditional' first as it contains 'conditional'
    if "nonconditional" in filename: condition = "No"
    elif "conditional" in filename: condition = "Yes"
    else: condition = "Unknown"
    
    # 4. Cache
    # Check 'noncached' first
    if "noncached" in filename: cache = "No"
    elif "cached" in filename: cache = "Yes"
    else: cache = "Unknown"
    
    return {
        "Filename": filename,
        "Model": model,
        "Strategy": strategy,
        "Condition": condition,
        "Cache": cache
    }

def render_file_selector(label, key_prefix, all_files):
    """
    Renders a set of dropdowns to filter and select a file.
    Returns the selected filename or None.
    """
    st.sidebar.markdown(f"### {label}")
    
    if not all_files:
        st.sidebar.warning("No files available.")
        return None

    # Parse all files into a DataFrame
    meta_list = [get_file_metadata(f) for f in all_files]
    df = pd.DataFrame(meta_list)
    
    # --- FILTERS ---
    c1, c2 = st.sidebar.columns(2)
    
    # Filter: Model
    avail_models = sorted(df['Model'].unique())
    sel_model = c1.selectbox("Model", avail_models, key=f"{key_prefix}_model")
    df = df[df['Model'] == sel_model]
    
    # Filter: Strategy
    avail_strat = sorted(df['Strategy'].unique())
    sel_strat = c2.selectbox("Strategy", avail_strat, key=f"{key_prefix}_strat")
    df = df[df['Strategy'] == sel_strat]
    
    c3, c4 = st.sidebar.columns(2)
    
    # Filter: Conditional
    avail_cond = sorted(df['Condition'].unique())
    sel_cond = c3.selectbox("Conditional?", avail_cond, key=f"{key_prefix}_cond")
    df = df[df['Condition'] == sel_cond]
    
    # Filter: Cache
    avail_cache = sorted(df['Cache'].unique())
    sel_cache = c4.selectbox("Cached?", avail_cache, key=f"{key_prefix}_cache")
    df = df[df['Cache'] == sel_cache]
    
    # --- FINAL SELECTION ---
    if df.empty:
        st.sidebar.error("No file matches these criteria.")
        return None
    
    # If multiple files remain (e.g. different timestamps or modes), let user pick
    # Otherwise auto-select the only one
    final_options = df['Filename'].tolist()
    selected_file = st.sidebar.selectbox("Select File", final_options, key=f"{key_prefix}_final")
    
    return selected_file

# --- USER INTERFACE ---

st.title("LLMASP Benchmark Analyzer")

# --- SIDEBAR ---
st.sidebar.header("Data Selection")

# 1. Check Base Directory
if not os.path.exists(BASE_RESULT_DIR):
    st.sidebar.error(f"Base directory '{BASE_RESULT_DIR}' does not exist. Please update `BASE_RESULT_DIR` code.")
    st.stop()

# 2. Select Date (Folder)
try:
    dates_folders = [d for d in os.listdir(BASE_RESULT_DIR) if os.path.isdir(os.path.join(BASE_RESULT_DIR, d))]
    dates_folders.sort(reverse=True) 
except Exception as e:
    st.sidebar.error(f"Error reading directory: {e}")
    dates_folders = []

selected_date = st.sidebar.selectbox("1. Test Date", dates_folders)

# 3. File Selection Logic
json_files = []
if selected_date:
    date_path = os.path.join(BASE_RESULT_DIR, selected_date)
    try:
        json_files = [f for f in os.listdir(date_path) if f.endswith('.json') and f != "options.json"]
        json_files.sort()
    except:
        pass

file_a = None
file_b = None

if not json_files:
    st.sidebar.warning("No JSON files found in selected date.")
else:
    # --- SELECTOR FOR TEST A ---
    file_a = render_file_selector("2. Select Test A (Main)", "test_a", json_files)
    
    st.sidebar.markdown("---")
    
    # --- SELECTOR FOR TEST B ---
    use_comparison = st.sidebar.checkbox("Compare with another test?", value=False)
    if use_comparison:
        file_b = render_file_selector("3. Select Test B (Comparison)", "test_b", json_files)

    # --- LOADING & PROCESSING ---
    
    if not os.path.exists(DATASET_PATH):
        st.error(f"Dataset not found at: {DATASET_PATH}")
    else:
        dataset_data = load_json_from_path(DATASET_PATH)
        
        # Load A
        res1_data = None
        if file_a:
            path_a = os.path.join(BASE_RESULT_DIR, selected_date, file_a)
            res1_data = load_json_from_path(path_a)
        
        if dataset_data and res1_data:
            inst_df1, prob_df1 = process_data(dataset_data, res1_data, "Model A")
            final_inst_df = inst_df1
            final_prob_df = prob_df1
            
            # Load B if selected
            if file_b:
                path_b = os.path.join(BASE_RESULT_DIR, selected_date, file_b)
                res2_data = load_json_from_path(path_b)
                
                if res2_data:
                    inst_df2, prob_df2 = process_data(dataset_data, res2_data, "Model B")
                    final_inst_df = pd.concat([inst_df1, inst_df2], ignore_index=True)
                    final_prob_df = pd.concat([prob_df1, prob_df2], ignore_index=True)

            # --- DASHBOARD VISUALIZATION ---
            
            readable_date = selected_date.replace("_", "/", 2).replace("_", " ", 1).replace("_", ":")
            st.header(f"Analysis: {readable_date}")
            
            # --- KPI DISPLAY HELPER ---
            def display_kpi_row(label, filename, inst_df, prob_df, baseline_metrics=None):
                
                curr_f1 = inst_df['f1_score'].mean()
                curr_acc = inst_df['accuracy'].mean()
                curr_llm = prob_df['LLM Calls'].sum()
                curr_sol = prob_df['Solver Calls'].sum()
                curr_hit = prob_df['Hit Rate %'].mean()
                
                st.subheader(f"📌 {label}: {filename}")
                
                cols = st.columns(5)
                
                if baseline_metrics:
                    # 1. QUALITY (Higher is Better) -> Default Color
                    cols[0].metric("Avg F1 Score", f"{curr_f1:.3f}", 
                                   delta=f"{curr_f1 - baseline_metrics['f1']:.3f}")
                    
                    cols[1].metric("Avg Accuracy", f"{curr_acc:.3f}", 
                                   delta=f"{curr_acc - baseline_metrics['acc']:.3f}")
                    
                    # 2. COSTS (Lower is Better) -> Inverse Color
                    cols[2].metric("Total LLM Calls", f"{curr_llm}", 
                                   delta=f"{curr_llm - baseline_metrics['llm']}", 
                                   delta_color="inverse")
                    
                    cols[3].metric("Total Solver Calls", f"{curr_sol}", 
                                   delta=f"{curr_sol - baseline_metrics['sol']}", 
                                   delta_color="inverse")
                    
                    # 3. CACHE HIT (Higher is Better) -> Default Color
                    cols[4].metric("Avg Cache Hit %", f"{curr_hit:.1f}%", 
                                   delta=f"{curr_hit - baseline_metrics['hit']:.1f}%")
                else:
                    cols[0].metric("Avg F1 Score", f"{curr_f1:.3f}")
                    cols[1].metric("Avg Accuracy", f"{curr_acc:.3f}")
                    cols[2].metric("Total LLM Calls", f"{curr_llm}")
                    cols[3].metric("Total Solver Calls", f"{curr_sol}")
                    cols[4].metric("Avg Cache Hit %", f"{curr_hit:.1f}%")
                
                return {
                    'f1': curr_f1, 'acc': curr_acc, 
                    'llm': curr_llm, 'sol': curr_sol, 'hit': curr_hit
                }

            # 1. SHOW MODEL A
            df_inst_a = final_inst_df[final_inst_df['Model'] == 'Model A']
            df_prob_a = final_prob_df[final_prob_df['Model'] == 'Model A']
            
            metrics_a = display_kpi_row("Model A", file_a, df_inst_a, df_prob_a)

            # 2. SHOW MODEL B (If exists)
            if file_b:
                st.markdown("---")
                df_inst_b = final_inst_df[final_inst_df['Model'] == 'Model B']
                df_prob_b = final_prob_df[final_prob_df['Model'] == 'Model B']
                
                display_kpi_row("Model B", file_b, df_inst_b, df_prob_b, baseline_metrics=metrics_a)
            
            st.divider()
            
            # --- CHARTS ---
            tab_qual, tab_solver, tab_res, tab_pareto = st.tabs([
                "Quality (F1 & Acc)", 
                "Solver & Cache", 
                "Resources", 
                "Pareto Frontier"
            ])
            
            # TAB 1: Quality
            with tab_qual:
                col1, col2 = st.columns(2)
                with col1:
                    fig_f1 = px.box(final_inst_df, x="Problem", y="f1_score", color="Model", 
                                    title="F1 Score Distribution")
                    st.plotly_chart(fig_f1, use_container_width=True)
                with col2:
                    perf_df = final_inst_df.groupby(["Model", "Problem"])["is_perfect"].mean().reset_index()
                    fig_perf = px.bar(perf_df, x="Problem", y="is_perfect", color="Model", barmode="group",
                                      title="% Perfect Extraction", labels={"is_perfect": "Ratio"})
                    st.plotly_chart(fig_perf, use_container_width=True)

            # TAB 2: Solver & Cache
            with tab_solver:
                st.subheader("Solver, LLM & Cache Analysis")
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    fig_calls = px.bar(
                        final_prob_df, x="Problem", y="LLM Calls", color="Model", barmode="group",
                        text_auto=True, title="LLM Calls"
                    )
                    st.plotly_chart(fig_calls, use_container_width=True)

                with col_s2:
                    fig_solver = px.bar(
                        final_prob_df, x="Problem", y="Solver Calls", color="Model", barmode="group",
                        text_auto=True, title="ASP Solver Calls"
                    )
                    st.plotly_chart(fig_solver, use_container_width=True)
                    
                with col_s3:
                    fig_rate = px.bar(
                        final_prob_df, x="Problem", y="Hit Rate %", color="Model", barmode="group",
                        text_auto='.1f', title="Cache Hit Rate %"
                    )
                    fig_rate.update_layout(yaxis_range=[0, 100])
                    st.plotly_chart(fig_rate, use_container_width=True)

                st.markdown("#### Cache Usage Detail (Hits vs Misses)")
                cache_melt = final_prob_df.melt(
                    id_vars=["Problem", "Model"], 
                    value_vars=["Cache Hits (Monotone)", "Cache Hits (Non-Mono)", "Cache Misses"],
                    var_name="Cache Type", value_name="Count"
                )
                fig_stack = px.bar(
                    cache_melt, x="Problem", y="Count", color="Cache Type", facet_col="Model",
                    title="Cache Composition",
                    color_discrete_map={
                        "Cache Hits (Monotone)": "#2ca02c", 
                        "Cache Hits (Non-Mono)": "#98df8a", 
                        "Cache Misses": "#d62728"
                    }
                )
                st.plotly_chart(fig_stack, use_container_width=True)

            # TAB 3: Resources
            with tab_res:
                res_metric = st.selectbox("Resource Metric:", ["Energy (uJ)", "Time (s)", "Tokens In", "Tokens Out"])
                fig_res = px.bar(
                    final_prob_df, x="Problem", y=res_metric, color="Model", barmode="group",
                    title=f"Total Consumption: {res_metric}"
                )
                st.plotly_chart(fig_res, use_container_width=True)

            # TAB 4: Pareto
            with tab_pareto:
                col_x, col_y = st.columns(2)
                x_ax = col_x.selectbox("X Axis (Cost)", ["Energy (uJ)", "Time (s)", "LLM Calls", "Solver Calls", "Tokens In"])
                y_ax = col_y.selectbox("Y Axis (Quality)", ["f1_score", "accuracy", "is_perfect"])
                
                quality_agg = final_inst_df.groupby(["Model", "Problem"])[y_ax].mean().reset_index()
                cost_agg = final_prob_df[["Model", "Problem", x_ax]]
                
                pareto_df = pd.merge(quality_agg, cost_agg, on=["Model", "Problem"])
                
                
                fig_par = px.scatter(
                    pareto_df, x=x_ax, y=y_ax, color="Model", symbol="Problem",
                    text="Problem", size_max=15, title=f"Pareto: {y_ax} vs {x_ax}"
                )
                fig_par.update_traces(textposition='top center')
                st.plotly_chart(fig_par, use_container_width=True)