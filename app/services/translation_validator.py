"""
Translation Validation Service for QR Info Portal
Provides validation functionality accessible from the Admin interface
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any


class TranslationValidator:
    """Service to validate translation files for completeness and issues."""
    
    PLACEHOLDER_PATTERNS = [
        r'\[admin\..*?\]',
        r'\[kiosk\..*?\]',
        r'\[.*?\..*?\]'  # Generic bracket placeholders
    ]
    
    def __init__(self, base_path: Path = None):
        """Initialize validator with base path to translations."""
        self.base_path = base_path or Path("app/translations")
        
    def validate_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Validate a single translation file.
        
        Returns:
            Dict with:
                - valid: bool
                - issues: List of issue descriptions
                - stats: Dict with statistics
        """
        issues = []
        stats = {
            'total_keys': 0,
            'empty_values': 0,
            'placeholders': 0,
            'valid_translations': 0
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for placeholder patterns
            for pattern in self.PLACEHOLDER_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    stats['placeholders'] += len(matches)
                    # Group similar placeholders
                    unique_prefixes = set()
                    for match in matches:
                        prefix = match.split('.')[0] + '.' + (match.split('.')[1] if '.' in match else '')
                        unique_prefixes.add(prefix)
                    
                    for prefix in sorted(unique_prefixes):
                        count = sum(1 for m in matches if m.startswith(prefix))
                        issues.append({
                            'type': 'placeholder',
                            'prefix': prefix,
                            'count': count,
                            'severity': 'error'
                        })
            
            # Parse JSON and check for empty values
            data = json.loads(content)
            
            def count_and_check(obj, path=""):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, dict):
                        count_and_check(value, current_path)
                    elif isinstance(value, str):
                        stats['total_keys'] += 1
                        if not value.strip():
                            stats['empty_values'] += 1
                            issues.append({
                                'type': 'empty_value',
                                'path': current_path,
                                'severity': 'warning'
                            })
                        elif not any(re.match(pattern, value) for pattern in self.PLACEHOLDER_PATTERNS):
                            stats['valid_translations'] += 1
                            
            count_and_check(data)
            
        except json.JSONDecodeError as e:
            issues.append({
                'type': 'invalid_json',
                'message': str(e),
                'severity': 'critical'
            })
        except Exception as e:
            issues.append({
                'type': 'file_error',
                'message': str(e),
                'severity': 'critical'
            })
            
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'stats': stats
        }
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all translation files.
        
        Returns:
            Dict with validation results for each language
        """
        results = {}
        languages = ['th', 'en', 'de']
        
        for lang in languages:
            filepath = self.base_path / f"{lang}.json"
            if filepath.exists():
                results[lang] = self.validate_file(filepath)
                results[lang]['exists'] = True
            else:
                results[lang] = {
                    'exists': False,
                    'valid': False,
                    'issues': [{'type': 'missing_file', 'severity': 'critical'}],
                    'stats': {}
                }
                
        # Calculate totals
        total_issues = sum(len(r['issues']) for r in results.values())
        total_placeholders = sum(r['stats'].get('placeholders', 0) for r in results.values())
        total_keys = sum(r['stats'].get('total_keys', 0) for r in results.values())
        total_valid = sum(r['stats'].get('valid_translations', 0) for r in results.values())
        
        return {
            'languages': results,
            'summary': {
                'total_issues': total_issues,
                'total_placeholders': total_placeholders,
                'total_keys': total_keys,
                'total_valid': total_valid,
                'completion_rate': round((total_valid / total_keys * 100) if total_keys > 0 else 0, 1)
            }
        }
    
    def get_fix_suggestions(self) -> List[Dict[str, str]]:
        """Get suggestions for fixing common issues."""
        return [
            {
                'issue': 'Placeholder Keys',
                'description': 'Translation keys wrapped in brackets like [admin.example]',
                'fix': 'Replace with actual translations in all languages',
                'command': 'grep -r "\\[.*\\]" app/translations/'
            },
            {
                'issue': 'Empty Values',
                'description': 'Translation keys with empty or whitespace-only values',
                'fix': 'Add proper translations for all empty keys',
                'command': 'grep -E \'": *"[ ]*"\' app/translations/'
            },
            {
                'issue': 'Service Names',
                'description': 'Services defined only in German in config.yml',
                'fix': 'Update config.yml to use multilingual structure',
                'command': 'cat config.yml | grep -A5 "services:"'
            }
        ]