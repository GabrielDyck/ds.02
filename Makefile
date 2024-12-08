# Define variables
PYTHON := python3
SCRIPT := github_contributions.py
OUTPUT := github_contributions.csv
export GITHUB_USER := GabrielDyck

# Default target to run the script
run: $(SCRIPT)
	$(PYTHON) $(SCRIPT)

# Clean up generated files
clean:
	rm -f $(OUTPUT)

# Help message
help:
	@echo "Makefile Targets:"
	@echo "  run    - Execute the Python script to fetch GitHub contributions."
	@echo "  clean  - Remove generated files (e.g., CSV files)."
	@echo "  help   - Display this help message."
