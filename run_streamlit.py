import streamlit
import sys
import traceback

try:
    sys.argv = ["streamlit", "run", "streamlit_app.py", "--server.port", "9876", "--server.address", "0.0.0.0"]
    streamlit.web.bootstrap.run(sys.argv, "", "", "")
except Exception as e:
    print(f"Error: {str(e)}")
    print(traceback.format_exc())