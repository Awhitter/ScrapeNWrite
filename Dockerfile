FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9876

CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port 9876 --server.address 0.0.0.0 2>&1 | tee streamlit.log"]
