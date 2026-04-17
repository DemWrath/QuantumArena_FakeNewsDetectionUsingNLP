from lime.lime_text import LimeTextExplainer
import numpy as np
from typing import Dict, Any

class ExplainLayer:
    def __init__(self, class_names=["REAL", "FAKE"]):
        # Initializes the explainer mapped to standard Binary outcome classes.
        self.explainer = LimeTextExplainer(class_names=class_names)
        
    def generate_explanation(self, text: str, analyzer_instance) -> Dict[str, Any]:
        """Runs LIME permutations across the DistilBERT Analyzer to isolate semantic weights."""
        if not analyzer_instance or not getattr(analyzer_instance, 'classifier', None):
            return {"error": "Transformers Classifier not provided or not initialized."}
            
        if not text or not text.strip():
            return {"error": "No text provided for explanation."}

        def predictor(texts):
            results = []
            outputs = analyzer_instance.classifier(texts)
            for out in outputs:
                label = out["label"].upper()
                score = out["score"]
                # ISOT convention: LABEL_0 = REAL, LABEL_1 = FAKE
                # class_names=["REAL", "FAKE"] → index 0 = REAL prob, index 1 = FAKE prob
                if label in ("FAKE", "LABEL_1"):
                    probs = [1.0 - score, score]   # [REAL%, FAKE%]
                else:
                    probs = [score, 1.0 - score]   # [REAL%, FAKE%]
                results.append(probs)
            return np.array(results)
            
        try:
            # We limit to top 15 features and 100 permutations to save processing time on CPU
            exp = self.explainer.explain_instance(text, predictor, num_features=15, num_samples=100)
            
            triggers = []
            for word, weight in exp.as_list():
                triggers.append({
                    "word": word,
                    "weight": round(weight, 4),
                    "impact_type": "FAKE_TRIGGER" if weight > 0 else "REAL_TRIGGER"
                })
            
            return {
                "limes_processed": True,
                "triggers": triggers
            }
        except Exception as e:
            return {"error": f"LIME feature mapping failed natively: {e}"}
