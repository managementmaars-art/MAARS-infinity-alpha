"""G5: RNG Determinism Validator"""
import re
from typing import List

def validate_rng_isolation(file_path: str) -> List[dict]:
    """Detect global np.random.seed() usage"""
    with open(file_path) as f:
        content = f.read()
    issues = []
    # Match np.random.seed( with optional whitespace
    pattern = r'np\s*\.\s*random\s*\.\s*seed\s*\('
    for match in re.finditer(pattern, content):
        line_num = content[:match.start()].count('\n') + 1
        issues.append({
            'type': 'GLOBAL_RNG_SEED',
            'line': line_num,
            'severity': 'error',
            'message': 'Global np.random.seed() pollutes test state'
        })
    return issues
