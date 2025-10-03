# Makefile for mDNS alias publisher

.PHONY: test test-mdns test-publish clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  test          - Run all tests"
	@echo "  test-mdns     - Run mdns_publisher tests only"
	@echo "  test-publish  - Run publish_aliases tests only"
	@echo "  clean         - Clean up __pycache__ directories"
	@echo "  help          - Show this help message"

# Run all tests
test:
	@echo "Running all tests..."
	@cd tests && python3 run_tests.py

# Run mdns_publisher tests only
test-mdns:
	@echo "Running mdns_publisher tests..."
	@cd tests && python3 -m unittest test_mdns_publisher -v

# Run publish_aliases tests only
test-publish:
	@echo "Running publish_aliases tests..."
	@cd tests && python3 -m unittest test_publish_aliases -v

# Clean up Python cache files
clean:
	@echo "Cleaning up __pycache__ directories..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup complete."