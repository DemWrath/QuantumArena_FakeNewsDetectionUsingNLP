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
            # Batch process through loaded Huggingface pipeline mappings
            outputs = analyzer_instance.classifier(texts)
            for out in outputs:
                label = out["label"].upper()
                score = out["score"]
                # Convert into probability lists [ REAL%, FAKE% ]
                if label == "FAKE" or label == "LABEL_0":
                    probs = [1.0 - score, score]
                else:
                    probs = [score, 1.0 - score]
                results.append(probs)
            return np.array(results)
            
        try:
            # Process strictly the top 15 features to prevent endless permutation blocking
            exp = self.explainer.explain_instance(text, predictor, num_features=15)
            
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
