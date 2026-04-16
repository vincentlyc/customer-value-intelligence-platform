install:
	pip install -r requirements.txt

data:
	python src/generate_fake_data.py

pipeline:
	python src/pipeline.py

viz:
	python src/visualize.py

run:
	streamlit run src/app.py

test:
	pytest -q
