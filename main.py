"""
🚀 ULTIMATE AI Trading Signal Platform - Enhanced Version
The most powerful mobile-friendly trading dashboard - Main Entry Point
"""

def main():
    """Main entry point for the AI Trading Dashboard"""
    try:
        # Import and run the enhanced demo
        from demo import main as demo_main
        demo_main()
    except ImportError as e:
        import streamlit as st
        st.error(f"❌ Error importing demo module: {e}")
        st.info("Please ensure demo.py is available and all dependencies are installed")
        st.code("""
        Required packages:
        - streamlit
        - plotly  
        - pandas
        - numpy
        - yfinance
        """)
    except Exception as e:
        import streamlit as st
        st.error(f"❌ Error running application: {e}")
        st.info("Please check the application logs for more details")
        # Show a basic fallback interface
        st.markdown("## 🚀 AI Trading Dashboard")
        st.info("The application is starting up. Please refresh the page in a moment.")

if __name__ == "__main__":
    main()
