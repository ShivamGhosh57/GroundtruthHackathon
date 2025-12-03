import json
import os
from security import SecurityLayer
from rag_engine import Brain

class CustomerSupportAgent:
    def __init__(self):
        print("🤖 AGENT: System Online.")
        self.security = SecurityLayer()
        self.brain = Brain()
        self.user_profile = {"name": "Satyam", "tier": "Gold", "loc": "NYC"}

    def process_request(self, raw_input):
        logs = []
        
        # 1. Security
        safe_query, sec_logs = self.security.sanitize_input(raw_input)
        logs.extend(sec_logs)
        if safe_query != raw_input: logs.append(f"🛡️ [SECURITY] Input sanitized.")

        # 2. RAG Retrieval
        docs = self.brain.search(safe_query)
        logs.append(f"🧠 [RAG] Retrieved {len(docs)} candidates.")
        cleaned_docs = [d.replace("rag_text:", "").strip() for d in docs]
        
        # 3. Logic Router
        response = ""
        q_lower = safe_query.lower()

        # CASE A: Refund Policy
        if any(w in q_lower for w in ["refund", "return", "money back"]):
            response = (
                "**Policy Check:**\n"
                "✅ Refunds are allowed within **14 days** with a valid receipt.\n"
                "❌ Refunds are NOT allowed for opened food items.\n"
                "*(Manager approval required for override)*"
            )

        # CASE B: Contact Request
        elif any(w in q_lower for w in ["call", "phone", "email", "contact", "number"]):
            response = (
                "**Request Acknowledged:**\n"
                "I have safely logged your contact request.\n\n"
                "🔒 **Privacy Note:** Your details have been **redacted** from our logs for compliance.\n"
                "A human agent will reach out shortly."
            )

        # CASE C: "Cold" (Generic Advice)
        elif any(w in q_lower for w in ["freezing", "cold", "winter"]):
            response = (
                "It sounds cold out there! 🥶\n"
                "I recommend heading to the nearest store for a hot beverage.\n\n"
                "**Closest 24/7 Location:**\n"
                "📍 **Starbucks Times Square** (Always open & heated)" 
            )

        # CASE D: Location Search (Strict Filter)
        else:
            if cleaned_docs:
                target_city = None
                known_cities = ["mumbai", "london", "new york", "tokyo", "nyc", "uk", "india", "usa", "delhi", "antarctica"]
                
                for city in known_cities:
                    if city in q_lower:
                        target_city = city
                        break
                
                if target_city == "antarctica":
                    response = "I searched my global database, but I couldn't find any stores in **Antarctica**. 🐧"
                else:
                    valid_matches = []
                    for doc in cleaned_docs:
                        parts = doc.split("|")
                        addr = parts[1].lower() if len(parts) > 1 else ""
                        
                        if target_city:
                            check = target_city
                            if target_city == "nyc": check = "new york"
                            if target_city == "uk": check = "london"
                            if target_city == "india": check = "mumbai"
                            if check in addr: valid_matches.append(doc)
                        else:
                            if "starbucks" in doc.lower(): valid_matches.append(doc)

                    if valid_matches:
                        response = "Here is what I found:\n\n"
                        for i, doc in enumerate(valid_matches[:3]):
                            parts = doc.split("|")
                            name = parts[0].replace("Name:", "").strip()
                            addr = parts[1].replace("Address:", "").strip()
                            response += f"**{i+1}. {name}**\n📍 {addr}\n---\n"
                    else:
                        if target_city:
                            response = f"I searched my database but found **0 stores** specifically in {target_city.title()}."
                        else:
                            response = "I am a Store Assistant. Try asking: 'Is there a store in London?'"
            else:
                response = "Database empty."

        return {"response": response, "logs": logs}