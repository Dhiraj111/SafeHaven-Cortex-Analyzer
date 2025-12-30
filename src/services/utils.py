def format_id(raw_id):
    """Masks raw hashes into professional IDs like 🔒 User-F40E"""
    if raw_id and len(str(raw_id)) > 10:
        return f"🔒 User-{str(raw_id)[:4].upper()}"
    return f"👤 {raw_id}"

def calculate_roi(risky_vol):
    """Simulates financial impact"""
    avg_loan = 35000
    potential_loss = risky_vol * avg_loan
    loss_avoided = potential_loss * 0.85
    return potential_loss, loss_avoided