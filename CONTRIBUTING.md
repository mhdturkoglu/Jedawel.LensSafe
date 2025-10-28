# Contributing to Jedawel LensSafe

Thank you for your interest in contributing to Jedawel LensSafe! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, camera type)
- Error messages or logs

### Suggesting Enhancements

We welcome enhancement suggestions! Please:
- Check if the feature has already been requested
- Clearly describe the proposed feature
- Explain why it would be useful
- Provide examples of how it would work

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/mhdturkoglu/Jedawel.LensSafe.git
   cd Jedawel.LensSafe
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

5. **Test your changes**
   ```bash
   python test_setup.py
   python baby_monitor.py --debug
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: clear description of your changes"
   ```

7. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

Example:
```python
def calculate_distance(self, point1, point2):
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: Tuple of (x, y) coordinates
        point2: Tuple of (x, y) coordinates
        
    Returns:
        float: Distance between the points
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
```

### Testing

- Test on multiple platforms (Windows, macOS, Linux)
- Verify camera functionality
- Check different lighting conditions
- Test with various camera resolutions
- Ensure no regression in existing features

### Documentation

Update documentation when you:
- Add new features
- Change configuration options
- Modify API or interfaces
- Fix significant bugs

Files to update:
- `README.md` - User-facing changes
- `ARCHITECTURE.md` - Technical changes
- `QUICKSTART.md` - Installation/usage changes
- Code comments - Implementation details

## Project Structure

```
Jedawel.LensSafe/
├── baby_monitor.py        # Main application
├── config.json           # Default configuration
├── requirements.txt      # Dependencies
├── test_setup.py        # System verification
├── generate_alert_sound.py  # Utility script
├── examples.py          # Usage examples
├── README.md           # User documentation
├── QUICKSTART.md       # Quick start guide
├── ARCHITECTURE.md     # Technical documentation
├── CONTRIBUTING.md     # This file
└── LICENSE            # MIT License
```

## Areas for Contribution

### High Priority
- [ ] Add unit tests for core functions
- [ ] Support for IP cameras (RTSP streams)
- [ ] Mobile notification integration
- [ ] Multi-language support
- [ ] Performance optimization

### Medium Priority
- [ ] GUI configuration editor
- [ ] Recording of detected events
- [ ] Statistics and analytics dashboard
- [ ] Multiple baby tracking
- [ ] Night vision/IR camera support

### Documentation
- [ ] Video tutorials
- [ ] Troubleshooting guide expansion
- [ ] Non-English documentation
- [ ] API documentation

### Examples
- [ ] Raspberry Pi deployment guide
- [ ] Docker containerization
- [ ] Cloud deployment examples
- [ ] Integration examples (Home Assistant, etc.)

## Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why this feature would be useful

## Proposed Implementation
How it could be implemented (optional)

## Alternatives Considered
Other ways to achieve the same goal

## Additional Context
Screenshots, mockups, or examples
```

## Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## System Information
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g., 3.9.5]
- Camera Type: [e.g., Built-in webcam, USB camera]
- Dependencies: [Run `pip list`]

## Error Messages
```
Paste any error messages here
```

## Screenshots
If applicable, add screenshots
```

## Code Review Process

All contributions will be reviewed for:
- Code quality and style
- Functionality and correctness
- Performance impact
- Security considerations
- Documentation completeness
- Test coverage

## Community Guidelines

- Be respectful and constructive
- Welcome newcomers
- Help others learn
- Give credit where due
- Focus on the issue, not the person
- Assume good intentions

## Questions?

If you have questions:
- Check existing issues and documentation
- Create a new issue with the "question" label
- Be specific about what you're trying to do

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)
- README acknowledgments (for major features)

Thank you for contributing to Jedawel LensSafe! 🎉
