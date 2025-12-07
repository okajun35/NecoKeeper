# Japanese Documentation Backup

This directory contains the original Japanese versions of documentation files that have been translated to English for the hackathon.

## Structure

- `steering/` - Original Japanese steering files from `.kiro/steering/`
- `specs/` - Original Japanese spec files from `.kiro/specs/`

## Purpose

These files are preserved as a backup. The English versions in `.kiro/` are now the primary documentation for international collaboration during the hackathon.

## Restoration

If you need to restore the Japanese versions:

```bash
# Restore steering files
cp docs/ja/steering/*.md .kiro/steering/

# Restore spec files
cp -r docs/ja/specs/* .kiro/specs/
```

## Date

Backup created: 2024-12-07
