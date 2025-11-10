import streamlit as st
import sys
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import time

# Add logic folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'logic'))

# Import all main functions
from logic.partitioning import partition_pdf_to_json
from logic.cleaning import cleaning
from logic.isolate_pdf import isolate_pdf
from logic.extractfitz import extract_fitz
from logic.extractplumber import extract_plumber
from logic.merging import reconstruct_document
from logic.chunking import chunking
from logic.embedding import vectorize_chunks
from logic.llm_access import access_llm

st.set_page_config(
    page_title="LocalRAG Demo - Interface",
    page_icon="🔍",
    layout="wide"
)

st.title("LocalRAG Demo")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a page",
    [
        "Text Processing",
        "LLM Access"
    ]
)

# Function to capture outputs
def run_with_capture(func, *args, **kwargs):
    """Execute a function and capture its output"""
    output = StringIO()
    error_output = StringIO()
    try:
        with redirect_stdout(output), redirect_stderr(error_output):
            result = func(*args, **kwargs)
        return output.getvalue(), error_output.getvalue(), None
    except Exception as e:
        return output.getvalue(), error_output.getvalue(), str(e)

# Function to load and display PDF
def display_pdf(pdf_path="inputs/file_example.pdf"):
    """Load and display PDF file"""
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            return pdf_bytes
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")
            return None
    else:
        st.warning(f"PDF file not found: {pdf_path}")
        return None

# Page 1: Text Processing
if page == "Text Processing":
    st.header("📄 Text Processing Pipeline")
    st.markdown("Execute all text processing steps automatically in sequence")
    
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = None
    if 'last_completed' not in st.session_state:
        st.session_state.last_completed = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'pipeline_completed' not in st.session_state:
        st.session_state.pipeline_completed = False
    
    # Display completion status if pipeline finished
    if st.session_state.pipeline_completed:
        st.success("✅ **Pipeline completed successfully!** All text processing steps have been executed and the document is ready for LLM queries.")
    
    # Button to start processing (moved to top)
    if st.button("🚀 Start Text Processing", type="primary", disabled=st.session_state.processing):
        st.session_state.processing = True
        st.session_state.current_step = None
        st.session_state.last_completed = None
        st.session_state.pipeline_completed = False
        st.rerun()
    
    # Execute pipeline if processing is active
    if st.session_state.processing:
        # Define processing steps
        steps = [
            {
                "name": "1. Partition PDF",
                "func": partition_pdf_to_json,
                "args": ("inputs/file_example", "inputs/file_example-partitioned"),
                "kwargs": {}
            },
            {
                "name": "2. Cleaning",
                "func": cleaning,
                "args": ("inputs/file_example-partitioned", "inputs/file_example-partitioned-cleaned"),
                "kwargs": {}
            },
            {
                "name": "3. Isolate PDF",
                "func": isolate_pdf,
                "args": ("inputs/file_example", "inputs/file_example-partitioned-cleaned", "inputs/extracts/pdf"),
                "kwargs": {}
            },
            {
                "name": "4. Extract Fitz",
                "func": extract_fitz,
                "args": ("inputs/extracts/pdf", "inputs/extracts/fitz"),
                "kwargs": {}
            },
            {
                "name": "5. Extract Plumber",
                "func": extract_plumber,
                "args": ("inputs/extracts/pdf", "inputs/extracts/plumber"),
                "kwargs": {}
            },
            {
                "name": "6. Merging",
                "func": reconstruct_document,
                "args": ("inputs/extracts/plumber", "inputs/extracts/fitz", "inputs/file_example-partitioned-cleaned"),
                "kwargs": {}
            },
            {
                "name": "7. Chunking",
                "func": chunking,
                "args": ("inputs/file-reconstituted", "inputs/file-chunked"),
                "kwargs": {}
            },
            {
                "name": "8. Vectorization",
                "func": vectorize_chunks,
                "args": ("inputs/file-chunked", "inputs/vectorstore"),
                "kwargs": {}
            }
        ]
        
        # Initialize step index if not exists
        if 'step_index' not in st.session_state:
            st.session_state.step_index = 0
            st.session_state.pipeline_error = None
        
        # Create placeholders for status display
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        log_placeholder = st.empty()
        
        total_steps = len(steps)
        current_step_idx = st.session_state.step_index
        
        # Execute current step
        if current_step_idx < total_steps:
            step = steps[current_step_idx]
            
            # Update progress bar
            progress = (current_step_idx) / total_steps
            progress_bar.progress(progress)
            
            # Display status
            status_text = []
            if current_step_idx > 0:
                status_text.append(f"✓ Completed: {steps[current_step_idx-1]['name']}")
            status_text.append(f"▶ Running: {step['name']}...")
            status_placeholder.info("\n".join(status_text))
            
            # Execute step
            with st.spinner(f"Executing {step['name']}..."):
                stdout, stderr, error = run_with_capture(step['func'], *step['args'], **step['kwargs'])
            
            # Display logs if available
            if stdout or stderr:
                with log_placeholder.expander(f"📋 Logs: {step['name']}", expanded=False):
                    if stdout:
                        st.text("STDOUT:")
                        st.text(stdout)
                    if stderr:
                        st.text("STDERR:")
                        st.warning(stderr)
            
            if error:
                st.session_state.pipeline_error = error
                status_placeholder.error(f"❌ {step['name']} FAILED: {error}")
                st.error(f"**Error in {step['name']}:** {error}")
                st.session_state.processing = False
                st.session_state.step_index = 0
            else:
                # Mark step as completed
                progress = (current_step_idx + 1) / total_steps
                progress_bar.progress(progress)
                
                status_text = [f"✓ Completed: {step['name']}"]
                if current_step_idx < total_steps - 1:
                    status_text.append(f"⏳ Next: {steps[current_step_idx + 1]['name']}")
                status_placeholder.success("\n".join(status_text))
                
                # Move to next step
                st.session_state.step_index += 1
                
                # If not the last step, rerun to continue
                if st.session_state.step_index < total_steps:
                    time.sleep(0.5)  # Small delay for UI update
                    st.rerun()
                else:
                    # All steps completed
                    st.session_state.current_step = None
                    st.session_state.last_completed = "All steps"
                    st.session_state.pipeline_completed = True
                    st.session_state.processing = False
                    st.session_state.step_index = 0
                    progress_bar.progress(1.0)
                    status_placeholder.success("🎉 All processing steps completed successfully! ✓✓✓")
                    st.balloons()
                    st.rerun()
        else:
            # Reset if somehow we're past the last step
            st.session_state.step_index = 0
            st.session_state.processing = False
    
    st.markdown("---")
    
    # Section to view base PDF file
    st.markdown("### Base Document")
    pdf_bytes = display_pdf()
    if pdf_bytes:
        st.markdown("**PDF Preview:**")
        st.pdf(pdf_bytes)
    
   

# Page 2: LLM Access
elif page == "LLM Access":
    st.header("👾 LLM Access")
    st.markdown("Ask questions to the LLM using semantic search")
    
    # Question input
    question = st.text_area(
        "Enter your question:",
        value="What is the Surface Area Consumed (m²) of RC (Resin Coated) Paper?",
        height=100
    )
    
    # Semantic query input
    query_semantic = st.text_input(
        "Semantic search query:",
        value="RC (Resin Coated) Paper"
    )
    
    
    debug_mode = st.checkbox("Debug mode", value=False)
    
    if st.button("🔍 Ask LLM", type="primary"):
        with st.spinner("Searching and generating response..."):
            try:
                output = StringIO()
                error_output = StringIO()
                
                with redirect_stdout(output), redirect_stderr(error_output):
                    response = access_llm(question, query_semantic, debug_mode)
                
                stdout = output.getvalue()
                stderr = error_output.getvalue()
                
                # Display debug output if available
                if debug_mode and stdout:
                    with st.expander("Debug Output"):
                        st.text(stdout)
                
                if stderr:
                    st.warning(f"Warning: {stderr}")
                
                # Display LLM response
                if response:
                    st.markdown("### 💬 LLM Response")
                    st.success(response)
                else:
                    st.error("No response received from LLM")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Section to view base PDF file
    st.markdown("### Base Document")
    pdf_bytes = display_pdf()
    if pdf_bytes:
        st.markdown("**PDF Preview:**")
        st.pdf(pdf_bytes)
    
  
