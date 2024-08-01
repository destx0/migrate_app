import json

def process_option3(data):
    # This function will be called from the main application
    # 'data' is the content of a single JSON file, but we need to process a JSONL file
    # So we'll ignore the 'data' parameter and process the JSONL file directly
    
    input_file = data.get('input_file', 'input.jsonl')  # Default to 'input.jsonl' if not specified
    output_file = data.get('output_file', 'output.json')  # Default to 'output.json' if not specified
    
    extract_content(input_file, output_file)
    
    return {"message": f"Processed JSONL file. Output saved to {output_file}"}

def extract_content(input_file, output_file):
    sections = [
        {"name": "General Intelligence and Reasoning", "questions": []},
        {"name": "General Awareness", "questions": []},
        {"name": "Quantitative Aptitude", "questions": []},
        {"name": "English Comprehension", "questions": []},
    ]
    extracted_count = 0

    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            try:
                data = json.loads(line)
                if "response" in data and "body" in data["response"]:
                    body = data["response"]["body"]
                    if "choices" in body and len(body["choices"]) > 0:
                        message = body["choices"][0]["message"]
                        if "content" in message:
                            content = message["content"]
                            start = content.find("{")
                            if start != -1:
                                end = content.rfind("}")
                                if end != -1 and end > start:
                                    extracted_content = content[start : end + 1]
                                    section_index = extracted_count // 25
                                    if section_index < len(sections):
                                        sections[section_index]["questions"].append(
                                            extracted_content.strip()
                                        )
                                    extracted_count += 1
                                else:
                                    print(
                                        f"Couldn't find closing '}}' in content: {content[:50]}..."
                                    )
                            else:
                                print(
                                    f"Couldn't find opening '{{' in content: {content[:50]}..."
                                )
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON in line: {line[:50]}... Error: {str(e)}")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("{\n")
        outfile.write('    "title": "General Knowledge Quiz",\n')
        outfile.write('    "description": "Test your knowledge!",\n')
        outfile.write('    "thumbnailLink": "https://example.com/thumbnail.jpg",\n')
        outfile.write('    "duration": 30,\n')
        outfile.write('    "positiveScore": 1,\n')
        outfile.write('    "negativeScore": 0.25,\n')
        outfile.write('    "sections": [\n')
        
        for i, section in enumerate(sections):
            outfile.write("        {\n")
            outfile.write(f'            "name": "{section["name"]}",\n')
            outfile.write('            "questions": [\n')
            for j, question in enumerate(section["questions"]):
                outfile.write(f"                {question}")
                if j < len(section["questions"]) - 1:
                    outfile.write(",")
                outfile.write("\n")
            outfile.write("            ]\n")
            outfile.write("        }")
            if i < len(sections) - 1:
                outfile.write(",")
            outfile.write("\n")
        
        outfile.write("    ]\n")
        outfile.write("}\n")

    print(
        f"Extracted {extracted_count} content blocks, grouped into 4 sections, and saved to {output_file}"
    )