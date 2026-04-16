"""G4: URL Fork Validator"""
import re
from typing import List

def validate_org_urls(file_path: str) -> List[dict]:
    with open(file_path) as f:
        content = f.read()
    issues = []
    for match in re.finditer(r'terrylica/alpha-forge', content):
        line_num = content[:match.start()].count('\n') + 1
        issues.append({'type': 'FORK_URL', 'line': line_num, 'severity': 'error', 'message': 'Use org URL not fork'})
    return issues
