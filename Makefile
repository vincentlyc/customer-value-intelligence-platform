install:
	pip install -r requirements.txt

data:
	python -m src.generate_fake_data

pipeline:
	python -m src.pipeline

viz:
	python -m src.visualize

run:
	streamlit run src/app.py

demo:
	python -m src.generate_fake_data --customers 1000 --transactions 20000 --seed 42
	python -m src.pipeline --data-dir ./data --output-dir ./outputs
	streamlit run src/app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true

test:
	pytest -q
