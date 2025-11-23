# Contributing to TRMNL E-Ink Display Integration

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Include:
   - Home Assistant version
   - Integration version
   - Device type (Standard/Terminus/Generic BYOS)
   - Steps to reproduce
   - Expected vs actual behavior
   - Log output (if applicable)

### Suggesting Enhancements

1. Check existing discussions/issues
2. Describe the enhancement clearly
3. Explain the use case and benefits
4. Include any relevant examples

### Submitting Code Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Follow code style (see below)
6. Commit with clear messages: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature`
8. Open a Pull Request

## Code Style

### Python

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Keep lines under 100 characters
- Use meaningful variable names

Example:
```python
async def send_image(
    device_id: str,
    image_url: str,
    refresh_rate: Optional[int] = None,
) -> Dict[str, Any]:
    """Send image to TRMNL device.

    Args:
        device_id: MAC address of device
        image_url: URL to image file
        refresh_rate: Optional refresh interval in seconds

    Returns:
        Dictionary with success status and any error messages
    """
    # Implementation here
    pass
```

### Comments

- Explain WHY, not WHAT (code shows what)
- Use complete sentences
- Update comments when changing code

## Testing

- Test with multiple device types if possible
- Test error cases
- Include rate limiting scenarios
- Document any manual testing steps

## Commit Messages

- Use present tense: "Add feature" not "Added feature"
- Be descriptive but concise
- Reference issues: "Fixes #123"
- Include why the change was needed

Examples:
```
Add support for custom refresh rates
Implement per-device rate limiting
Fix webhook registration for Standard TRMNL
```

## Documentation

- Update README if behavior changes
- Add docstrings to new functions
- Include examples for new features
- Document any breaking changes

## Pull Request Process

1. Update README.md with details of changes
2. Update version numbers following semantic versioning
3. Ensure code follows style guidelines
4. Get approval from maintainers
5. Rebase and merge

## Development Setup

### Prerequisites
- Python 3.10+
- Home Assistant development environment
- Git

### Local Testing
```bash
# Clone your fork
git clone https://github.com/yourusername/ha-trmnl-integration.git
cd ha-trmnl-integration

# Copy to Home Assistant
cp -r custom_components/trmnl ~/.homeassistant/custom_components/

# Restart Home Assistant
```

## Questions?

- Open a GitHub Discussion
- Ask in a GitHub Issue
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
