def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "llm: mark test as a LLM test")
    config.addinivalue_line("markers", "asyncio: mark test as an async test")
