from datetime import datetime

violations = []


def log_violation(vtype):

    violations.append({
        "type": vtype,
        "time": datetime.now().strftime("%H:%M:%S")
    })


def get_violations():
    return violations


def get_violation_count():
    return len(violations)


def clear_violations():
    violations.clear()