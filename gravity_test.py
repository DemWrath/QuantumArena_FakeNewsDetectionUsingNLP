from transformers import pipeline

text = '''A mysterious “gravity blackout” reportedly struck several major cities overnight, causing objects to briefly float midair and disrupting transportation systems, according to unverified social media posts. Eyewitnesses claimed cars lifted slightly off the ground and water in rivers appeared to ripple upward, while officials allegedly imposed temporary curfews to “stabilize atmospheric conditions.” Some sources suggested the phenomenon was linked to a secret experiment involving quantum energy fields, though no credible scientific organization has confirmed such claims. Authorities have neither confirmed nor denied the incident, and experts urge the public to treat these reports with skepticism until reliable evidence emerges.'''

p = pipeline('text-classification', model='mrm8488/bert-tiny-finetuned-fake-news-detection')
print(p(text))
