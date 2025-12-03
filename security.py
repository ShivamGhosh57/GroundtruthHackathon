from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class SecurityLayer:
    def __init__(self):
        print("🛡️ SECURITY: Initializing Microsoft Presidio (NLP Engine)...")
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def sanitize_input(self, user_input):
        redaction_log = []
        
        # 1. Analyze (Detect sensitive data)
        results = self.analyzer.analyze(
            text=user_input,
            entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION"],
            language='en'
        )

        # 2. Anonymize (Redact the data)
        anonymized_result = self.anonymizer.anonymize(
            text=user_input,
            analyzer_results=results,
            operators={
                "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
                "PERSON": OperatorConfig("replace", {"new_value": "<NAME_REDACTED>"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE_REDACTED>"}),
            }
        )

        # 3. Log generation
        for res in results:
            redaction_log.append(f"⚠️ [SECURITY] Detected {res.entity_type} -> Redacted.")

        return anonymized_result.text, redaction_log