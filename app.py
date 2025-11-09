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
        
        # Create placeholder for status display
        status_placeholder = st.empty()
        
        error = None
        # Execute each step
        for i, step in enumerate(steps):
            # Update current step
            st.session_state.current_step = step['name']
            st.session_state.last_completed = steps[i-1]['name'] if i > 0 else None
            
            # Display status
            status_text = []
            if st.session_state.last_completed:
                status_text.append(f"✓ Completed: {st.session_state.last_completed}")
            status_text.append(f"▶ Running: {st.session_state.current_step}...")
            status_placeholder.info("\n".join(status_text))
            
            # Execute step
            stdout, stderr, error = run_with_capture(step['func'], *step['args'], **step['kwargs'])
            
            if error:
                status_placeholder.error(f"❌ {step['name']} FAILED: {error}")
                st.error(f"Error in {step['name']}: {error}")
                break
            
            # Mark as completed
            st.session_state.last_completed = step['name']
            st.session_state.current_step = None
            
            # Update status display
            status_text = [f"✓ Completed: {st.session_state.last_completed}"]
            if i < len(steps) - 1:
                status_text.append(f"⏳ Next: {steps[i+1]['name']}")
            status_placeholder.success("\n".join(status_text))
        
        # Final status
        if not error:
            st.session_state.current_step = None
            st.session_state.last_completed = "All steps"
            st.session_state.pipeline_completed = True
            status_placeholder.success("🎉 All processing steps completed successfully! ✓✓✓")
        
        st.session_state.processing = False
        st.rerun()
    
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
    
  
