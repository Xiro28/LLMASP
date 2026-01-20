import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os
import re

# --- CONFIGURAZIONE PERCORSI ---
BASE_RESULT_DIR = "../../experiments/results/" 
DATASET_PATH = "../../experiments/dataset/dataset.json"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="LLM Datalog Benchmark Analyzer", layout="wide")

# --- FUNZIONI DI UTILITÀ ---

def load_json_from_path(path):
    """Carica un file JSON da un percorso locale."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File non trovato: {path}")
        return None
    except json.JSONDecodeError:
        st.error(f"Errore nel decodificare il JSON: {path}")
        return None

def parse_datalog_facts(text):
    """Estrae i fatti datalog da una stringa (Versione Regex Robusta)."""
    if not isinstance(text, str):
        return [], False
    clean_text = text.replace('\n', ' ').strip()
    if not clean_text:
        return [], False
    
    # Regex migliorata per catturare predicati (es. edge(n1, n2).)
    pattern = r"\w+\([a-zA-Z0-9_]+(?:,\s*[a-zA-Z0-9_]+)*\)\."
    raw_facts = re.findall(pattern, clean_text)
    
    # Fallback semplice se la regex non trova nulla ma c'è testo
    if not raw_facts and clean_text:
         raw_facts = [f.strip() for f in clean_text.split('.') if f.strip()]

    has_duplicates = len(raw_facts) != len(set(raw_facts))
    return raw_facts, has_duplicates

def calculate_metrics(ground_truth_str, predicted_str):
    """Calcola metriche basate su insiemi."""
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
    
    # Mappa dataset
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
        
        # --- DATI AGGREGATI (Problem Level) ---
        llm_calls = problem_data.get("llm_calls", 0)
        solver_calls = problem_data.get("solver_calls", 0) # <--- ESTRAZIONE SOLVER CALLS
        
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
            "Solver Calls": solver_calls, # <--- AGGIUNTO AL DATAFRAME
            "Cache Hits (Monotone)": c_hit_m,
            "Cache Hits (Non-Mono)": c_hit_nm,
            "Cache Misses": total_misses,
            "Total Hits": total_hits,
            "Hit Rate %": hit_rate
        }
        problem_rows.append(prob_row)
        
        # --- DATI ISTANZA (Instance Level) ---
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

# --- INTERFACCIA UTENTE ---

st.title("📊 LLM Datalog Benchmark Analyzer")

# --- SIDEBAR: SELEZIONE CARTELLE E FILE ---
st.sidebar.header("📁 Selezione Test Locale")

# 1. Verifica esistenza cartella base
if not os.path.exists(BASE_RESULT_DIR):
    st.sidebar.error(f"La cartella base '{BASE_RESULT_DIR}' non esiste. Modifica la variabile `BASE_RESULT_DIR` nel codice.")
    st.stop()

# 2. Dropdown Data (Cartelle)
try:
    dates_folders = [d for d in os.listdir(BASE_RESULT_DIR) if os.path.isdir(os.path.join(BASE_RESULT_DIR, d))]
    dates_folders.sort(reverse=True) 
except Exception as e:
    st.sidebar.error(f"Errore lettura cartella: {e}")
    dates_folders = []

selected_date = st.sidebar.selectbox("1. Seleziona Data Test", dates_folders)

# 3. Dropdown File JSON 
json_files = []
if selected_date:
    date_path = os.path.join(BASE_RESULT_DIR, selected_date)
    try:
        json_files = [f for f in os.listdir(date_path) if f.endswith('.json')]
        json_files.sort()
    except:
        pass

if not json_files:
    st.sidebar.warning("Nessun file .json trovato nella cartella selezionata.")
else:
    file_a = st.sidebar.selectbox("2. Seleziona Test A (Principale)", json_files, index=0)
    file_b_options = ["None"] + json_files
    file_b = st.sidebar.selectbox("3. Seleziona Test B (Confronto - Opzionale)", file_b_options, index=0)

    # --- LOGICA DI CARICAMENTO ---
    
    if not os.path.exists(DATASET_PATH):
        st.error(f"Dataset non trovato al percorso: {DATASET_PATH}. Verifica la variabile `DATASET_PATH`.")
    else:
        dataset_data = load_json_from_path(DATASET_PATH)
        option_data = load_json_from_path(os.path.join(BASE_RESULT_DIR, selected_date, "options.json"))
        
        path_a = os.path.join(BASE_RESULT_DIR, selected_date, file_a)
        res1_data = load_json_from_path(path_a)
        
        if dataset_data and res1_data:
            inst_df1, prob_df1 = process_data(dataset_data, res1_data, "Model A")
            final_inst_df = inst_df1
            final_prob_df = prob_df1
            
            if file_b and file_b != "None":
                path_b = os.path.join(BASE_RESULT_DIR, selected_date, file_b)
                res2_data = load_json_from_path(path_b)
                
                if res2_data:
                    inst_df2, prob_df2 = process_data(dataset_data, res2_data, "Model B")
                    final_inst_df = pd.concat([inst_df1, inst_df2], ignore_index=True)
                    final_prob_df = pd.concat([prob_df1, prob_df2], ignore_index=True)

            # --- VISUALIZZAZIONE DASHBOARD ---
            
            st.header(f"Analisi del: {selected_date}")
            
            # --- FUNZIONE HELPER PER MOSTRARE I KPI ---
            def display_kpi_row(label, filename, inst_df, prob_df, baseline_metrics=None):
                """Mostra una riga di metriche per un modello specifico."""
                
                # Calcolo metriche correnti
                curr_f1 = inst_df['f1_score'].mean()
                curr_acc = inst_df['accuracy'].mean()
                curr_llm = prob_df['LLM Calls'].sum()
                curr_sol = prob_df['Solver Calls'].sum()
                curr_hit = prob_df['Hit Rate %'].mean()
                
                st.subheader(f"📌 {label}: {filename}")
                
                cols = st.columns(5)
                
                # Se abbiamo una baseline (cioè siamo nel Modello B)
                if baseline_metrics:
                    # 1. QUALITY (Higher is Better) -> Default Color (Pos=Green, Neg=Red)
                    # Calcolo: Corrente - Vecchio
                    cols[0].metric("Avg F1 Score", f"{curr_f1:.3f}", 
                                   delta=f"{curr_f1 - baseline_metrics['f1']:.3f}")
                    
                    cols[1].metric("Avg Accuracy", f"{curr_acc:.3f}", 
                                   delta=f"{curr_acc - baseline_metrics['acc']:.3f}")
                    
                    # 2. COSTS (Lower is Better) -> Inverse Color (Neg=Green, Pos=Red)
                    # Calcolo: Corrente - Vecchio (es. 50 - 100 = -50. Negativo è BENE)
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
                    # Nessuna baseline (Modello A), mostriamo valori puri
                    cols[0].metric("Avg F1 Score", f"{curr_f1:.3f}")
                    cols[1].metric("Avg Accuracy", f"{curr_acc:.3f}")
                    cols[2].metric("Total LLM Calls", f"{curr_llm}")
                    cols[3].metric("Total Solver Calls", f"{curr_sol}")
                    cols[4].metric("Avg Cache Hit %", f"{curr_hit:.1f}%")
                
                return {
                    'f1': curr_f1, 'acc': curr_acc, 
                    'llm': curr_llm, 'sol': curr_sol, 'hit': curr_hit
                }

            # 1. MOSTRA MODELLO A
            df_inst_a = final_inst_df[final_inst_df['Model'] == 'Model A']
            df_prob_a = final_prob_df[final_prob_df['Model'] == 'Model A']
            
            # Salviamo le metriche di A per usarle come confronto
            metrics_a = display_kpi_row("Model A", file_a, df_inst_a, df_prob_a)

            # 2. MOSTRA MODELLO B (Se esiste)
            if file_b and file_b != "None":
                st.markdown("---") # Separatore visivo
                df_inst_b = final_inst_df[final_inst_df['Model'] == 'Model B']
                df_prob_b = final_prob_df[final_prob_df['Model'] == 'Model B']
                
                # Passiamo metrics_a per generare i delta (frecce verdi/rosse)
                display_kpi_row("Model B", file_b, df_inst_b, df_prob_b, baseline_metrics=metrics_a)
            
            st.divider()
            
            # Tabs Grafici
            tab_qual, tab_solver, tab_res, tab_pareto = st.tabs([
                "📈 Quality (F1 & Acc)", 
                "🧠 Solver & Cache", 
                "⚡ Resources", 
                "⚖️ Pareto Frontier"
            ])
            
            # TAB 1: Quality
            with tab_qual:
                col1, col2 = st.columns(2)
                with col1:
                    fig_f1 = px.box(final_inst_df, x="Problem", y="f1_score", color="Model", 
                                    title="Distribuzione F1 Score")
                    st.plotly_chart(fig_f1, use_container_width=True)
                with col2:
                    perf_df = final_inst_df.groupby(["Model", "Problem"])["is_perfect"].mean().reset_index()
                    fig_perf = px.bar(perf_df, x="Problem", y="is_perfect", color="Model", barmode="group",
                                      title="% Estrazioni Perfette", labels={"is_perfect": "Ratio"})
                    st.plotly_chart(fig_perf, use_container_width=True)

            # TAB 2: Solver & Cache (AGGIORNATO)
            with tab_solver:
                st.subheader("Analisi Chiamate Solver, LLM e Cache")
                # Diviso in 3 colonne
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    fig_calls = px.bar(
                        final_prob_df, x="Problem", y="LLM Calls", color="Model", barmode="group",
                        text_auto=True, title="LLM Calls"
                    )
                    st.plotly_chart(fig_calls, use_container_width=True)

                with col_s2: # <--- NUOVA COLONNA PER SOLVER CALLS
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

                st.markdown("#### Dettaglio Utilizzo Cache (Hits vs Misses)")
                cache_melt = final_prob_df.melt(
                    id_vars=["Problem", "Model"], 
                    value_vars=["Cache Hits (Monotone)", "Cache Hits (Non-Mono)", "Cache Misses"],
                    var_name="Cache Type", value_name="Count"
                )
                fig_stack = px.bar(
                    cache_melt, x="Problem", y="Count", color="Cache Type", facet_col="Model",
                    title="Composizione Cache: Hits vs Misses",
                    color_discrete_map={
                        "Cache Hits (Monotone)": "#2ca02c", 
                        "Cache Hits (Non-Mono)": "#98df8a", 
                        "Cache Misses": "#d62728"
                    }
                )
                st.plotly_chart(fig_stack, use_container_width=True)

            # TAB 3: Risorse
            with tab_res:
                res_metric = st.selectbox("Metrica Risorse:", ["Energy (uJ)", "Time (s)", "Tokens In", "Tokens Out"])
                fig_res = px.bar(
                    final_prob_df, x="Problem", y=res_metric, color="Model", barmode="group",
                    title=f"Consumo Totale: {res_metric}"
                )
                st.plotly_chart(fig_res, use_container_width=True)

            # TAB 4: Pareto
            with tab_pareto:
                col_x, col_y = st.columns(2)
                # Aggiunto "Solver Calls" alle opzioni di costo
                x_ax = col_x.selectbox("Asse X (Costo)", ["Energy (uJ)", "Time (s)", "LLM Calls", "Solver Calls", "Tokens In"])
                y_ax = col_y.selectbox("Asse Y (Qualità)", ["f1_score", "accuracy", "is_perfect"])
                
                quality_agg = final_inst_df.groupby(["Model", "Problem"])[y_ax].mean().reset_index()
                cost_agg = final_prob_df[["Model", "Problem", x_ax]]
                
                pareto_df = pd.merge(quality_agg, cost_agg, on=["Model", "Problem"])
                
                
                fig_par = px.scatter(
                    pareto_df, x=x_ax, y=y_ax, color="Model", symbol="Problem",
                    text="Problem", size_max=15, title=f"Pareto: {y_ax} vs {x_ax}"
                )
                fig_par.update_traces(textposition='top center')
                st.plotly_chart(fig_par, use_container_width=True)