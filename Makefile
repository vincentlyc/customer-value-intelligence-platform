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

test:
	pytest -q
