import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Project Manager Assistant", layout="wide")
st.title("🤖 Project Manager Assistant Agent")

st.info("Upload a project description and a team CSV file to generate a project plan.")

# --- Helper Functions ---
def plot_gantt_chart(results_data, iteration):
    """Plots a Gantt chart for a specific iteration."""
    try:
        schedule_data = results_data['schedule_iteration'][iteration]['schedule']
        allocation_data = results_data['task_allocations_iteration'][iteration]['task_allocations']
        
        schedule_df = pd.DataFrame([s['task'] for s in schedule_data])
        schedule_df['start_day'] = [s['start_day'] for s in schedule_data]
        schedule_df['end_day'] = [s['end_day'] for s in schedule_data]

        alloc_df = pd.DataFrame([a['task'] for a in allocation_data])
        alloc_df['team_member'] = [a['team_member']['name'] for a in allocation_data]
        
        # Merge dataframes
        df = pd.merge(schedule_df, alloc_df, on='id', suffixes=('', '_y'))
        df = df.drop(columns=[col for col in df.columns if col.endswith('_y')])
        
        # Convert days to dates for plotting
        current_date = datetime.today()
        df['start'] = df['start_day'].apply(lambda x: current_date + timedelta(days=x))
        df['end'] = df['end_day'].apply(lambda x: current_date + timedelta(days=x))

        df.rename(columns={'team_member': 'Team Member'}, inplace=True)
        df.sort_values(by='Team Member', inplace=True)

        fig = px.timeline(
            df, 
            x_start="start", 
            x_end="end", 
            y="task_name", 
            color="Team Member", 
            title=f"Gantt Chart - Iteration {iteration + 1}"
        )
        fig.update_layout(
            xaxis_title="Timeline",
            yaxis_title="Tasks",
            yaxis=dict(autorange="reversed"),
            title_x=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

    except (KeyError, IndexError, TypeError) as e:
        st.error(f"Could not generate Gantt chart for iteration {iteration + 1}. Error: {e}")


# --- UI Components ---
with st.sidebar:
    st.header("Inputs")
    project_description = st.text_area("Project Description", height=200, value="Our business aims to deliver a chatbot application for our customers to ensure 24/7 support and advice on product choices.")
    uploaded_file = st.file_uploader("Choose a Team CSV file", type="csv")

if uploaded_file is not None:
    st.sidebar.dataframe(pd.read_csv(uploaded_file))

if st.sidebar.button("Generate Project Plan", use_container_width=True):
    if not project_description or uploaded_file is None:
        st.error("Please provide both a project description and a team file.")
    else:
        with st.spinner("Submitting job to the agent..."):
            files = {'team_file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
            data = {'project_description': project_description}
            try:
                response = requests.post(f"{API_URL}/v1/plans", files=files, data=data)
                response.raise_for_status()
                job_info = response.json()
                st.session_state.job_id = job_info['job_id']
                st.success(f"Job submitted successfully! Job ID: {st.session_state.job_id}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to submit job: {e}")
                st.session_state.job_id = None

# --- Polling for results ---
if 'job_id' in st.session_state and st.session_state.job_id:
    job_id = st.session_state.job_id
    st.header("Agent Progress & Results")
    
    with st.spinner(f"Waiting for job {job_id} to complete..."):
        status = ""
        while status not in ["finished", "failed"]:
            try:
                response = requests.get(f"{API_URL}/v1/plans/{job_id}")
                response.raise_for_status()
                result_data = response.json()
                status = result_data.get("status")
                st.write(f"Job status: `{status}`")
                time.sleep(5)
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to get job status: {e}")
                break
    
    if status == "finished":
        st.success("🎉 Project plan generated!")
        results = result_data.get("result", {})
        
        st.subheader("Risk Score Evolution")
        risk_scores = results.get('project_risk_score_iterations', [])
        if risk_scores:
            df_risk = pd.DataFrame({
                'Iteration': range(1, len(risk_scores) + 1),
                'Risk Score': risk_scores
            })
            st.line_chart(df_risk.set_index('Iteration'))

        st.subheader("Final Project Plan (Gantt Charts)")
        num_iterations = results.get('iteration_number', 0)
        for i in range(num_iterations):
            plot_gantt_chart(results, i)
        
        st.subheader("Full Agent State")
        st.json(results)

    elif status == "failed":
        st.error("Job failed to complete.") 