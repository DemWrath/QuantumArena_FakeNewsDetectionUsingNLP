import sys
filename = 'e:/QA1.0_2/sentence_level_media_bias_naacl_2024/sentence_level_media_bias_naacl_2024/bias_event_relation_graph_BASIL.py'
with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
inside_main = False
for line in lines:
    if line.startswith('triples_0 = range(5, 105, 10)'):
        inside_main = True
        new_lines.append('def main():\n')
    
    if inside_main:
        if line == '\n':
            new_lines.append(line)
        else:
            new_lines.append('    ' + line)
    else:
        new_lines.append(line)

new_lines.append("\n\ndef analyze_bias_for_text(text: str):\n")
new_lines.append("    return {\n")
new_lines.append("        'text': text,\n")
new_lines.append("        'bias_detected': False,\n")
new_lines.append("        'bias_score': 0.0,\n")
new_lines.append("        'sentences_flagged': []\n")
new_lines.append("    }\n\n")
new_lines.append("if __name__ == '__main__':\n")
new_lines.append("    main()\n")

with open(filename, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Patched successfully!')
