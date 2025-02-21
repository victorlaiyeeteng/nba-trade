VENV_DIR = venv

# Install dependencies
install_dependencies:
	$(VENV_DIR)/bin/pip install -r requirements.txt

# Scripts
create_db:
	python src/db/create_db.py
clear_db:
	python src/db/clear_db.py


