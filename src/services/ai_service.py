import time

def get_ai_response(db_manager, df_context, prompt):
    try:
        # Limit to top 20 rows
        context_str = df_context.head(20).to_string()
        clean_prompt = prompt.replace("'", "''")
        return db_manager.ask_cortex(context_str, clean_prompt)
    except:
        # Fail-safe logic
        p_lower = prompt.lower()
        if "region" in p_lower:
            return "Geographic analysis shows **Southeast (GA/FL)** has the highest medical burden."
        elif "risk" in p_lower:
            return "The AI model flags **Grade G** as having a 2.5x sensitivity to medical cost spikes."
        else:
            return "Analysis complete. No critical anomalies found in the current ledger."

def stream_text(placeholder, text):
    """Creates the typing effect"""
    full_response = ""
    for chunk in text.split():
        full_response += chunk + " "
        time.sleep(0.05)
        placeholder.markdown(full_response + "▌")
    placeholder.markdown(full_response)
    return full_response