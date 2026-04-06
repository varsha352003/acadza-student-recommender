import re


def normalize_marks(marks):
    """
    Convert various mark formats to 0-100 scale.
    
    Handles:
    - "68/100"
    - "+52 -12"
    - "34/75 (45.3%)"
    - 72
    - "28"
    """
    if marks is None or marks == "":
        return 0
    
    marks_str = str(marks).strip()
    
    # Extract percentage from brackets if present
    percentage_match = re.search(r'\((\d+(?:\.\d+)?)%\)', marks_str)
    if percentage_match:
        return min(100, max(0, float(percentage_match.group(1))))
    
    # Handle +a -b format
    if '+' in marks_str or '-' in marks_str:
        plus_minus = re.findall(r'([+-]\d+)', marks_str)
        if plus_minus:
            total = sum(int(x) for x in plus_minus)
            # Scale to 0-100 if result exceeds
            return min(100, max(0, total))
    
    # Handle x/y format
    if '/' in marks_str:
        parts = marks_str.split('/')
        if len(parts) == 2:
            try:
                obtained = float(parts[0].strip())
                total = float(parts[1].strip())
                if total > 0:
                    percentage = (obtained / total) * 100
                    return min(100, max(0, percentage))
            except ValueError:
                pass
    
    # Handle numeric value (direct score)
    try:
        score = float(marks_str)
        return min(100, max(0, score))
    except ValueError:
        return 0


def normalize_question_id(raw_id):
    """
    Extract question ID from various formats.
    
    Handles:
    - {"$oid": "..."}
    - flat string
    """
    if isinstance(raw_id, dict):
        if "$oid" in raw_id:
            return raw_id["$oid"]
        return None
    
    return str(raw_id) if raw_id else None
