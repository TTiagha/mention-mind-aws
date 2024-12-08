# Mention Mind AWS

A project for managing and analyzing mentions using AWS services.

## Project Structure

```
mention-mind-aws/
├── src/
│   ├── config/         # Configuration files
│   ├── utils/          # Utility functions
│   └── __init__.py
├── tests/              # Test files
└── requirements.txt    # Project dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.template` to `.env` and fill in your configuration:
```bash
cp .env.template .env
```

## Development

- Follow PEP 8 style guide for Python code
- Write tests for new features
- Update requirements.txt when adding new dependencies

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## License

[Your chosen license]

Created: 2024-12-08
