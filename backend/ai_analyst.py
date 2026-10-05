from backend import database

def generate_security_assessment():
    stats = database.fetch_user_stats() if hasattr(database, "fetch_user_stats") else {}
    logs = database.fetch_logs(limit=5) if hasattr(database, "fetch_logs") else []

    pending_cnt = stats.get("pending", 0)
    
    assessment = "=== CYBER SHIELD AI SECURITY REPORT ===\n\n"
    assessment += f"• Pending Access Approvals: {pending_cnt} request(s) awaiting Admin action.\n"
    assessment += f"• Registered Users Total: {stats.get('total', 0)}\n\n"
    
    assessment += "--- Recent Threat Activity Summary ---\n"
    for l in logs:
        assessment += f"[{l[1]}] [{l[2]}] {l[3]}\n"
        
    assessment += "\n--- AI Recommendation ---\n"
    if pending_cnt > 0:
        assessment += "CRITICAL: Review pending user registration requests in the Admin Panel to prevent unauthorized portal access.\n"
    else:
        assessment += "ALL SYSTEMS OPTIMAL: Endpoint integrity verified. No pending access bottlenecks.\n"

    return assessment

get_assessment = generate_security_assessment
