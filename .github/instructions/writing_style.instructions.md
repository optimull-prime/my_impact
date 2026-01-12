---
alwaysApply: true
always_on: true
trigger: always_on
applyTo: "**/*.md"
description: Writing Style and Tone
---

# Writing Style and Tone

DO:
- Use clear, professional language
- Use bold text for emphasis (**important**)
- Use code formatting for technical terms (`container`, `main`)
- Use status indicators: [SUCCESS], [FAILED], [WARNING]
- Use checkmarks in tables: "Yes" or "No" (not symbols)
- Focus on clarity and readability

DO NOT:
- Use emoji in documentation or code comments
- Use excessive formatting (multiple exclamation points, all caps)
- Use colloquial language or slang in technical docs
- Overuse bold or italic formatting
- Use decorative characters or ASCII art for headings

**Exception:** Emoji acceptable in commit messages for convention (e.g., `:bug:` for bug fixes) if project uses conventional commits with emoji.

**Rationale:**
- Professional tone appropriate for enterprise/production environments
- Accessibility: Screen readers handle text better than emoji
- Consistency: Plain text is universally understood across cultures and tools
- Searchability: Text-based indicators easier to find in documentation
