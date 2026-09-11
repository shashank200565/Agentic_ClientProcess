import fitz
import re
import json
import os

from huggingface_hub import InferenceClient
from dotenv import load_dotenv



load_dotenv()

client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)



def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text() + "\n"

    doc.close()

    return text


def clean_text(text):

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def has_numbered_steps(text):
    pattern = r"(?m)^\s*(?:Step\s*)?\d+\s*[\.\):\-]"
    matches = re.findall(pattern, text)

    print(f"Numbered step markers detected: {len(matches)}")

    return len(matches) >= 2



def extract_numbered_steps(text):

    lines = text.split("\n")

    steps = []

    for line in lines:

        line = line.strip()

        match = re.match(
            r"^(?:Step\s*)?(\d+)[\.\):\-]\s*(.+)",
            line,
            re.IGNORECASE
        )

        if match:

            steps.append({
                "step": int(match.group(1)),
                "description": match.group(2).strip()
            })

    return steps


def extract_steps_with_llm(text):

    prompt = f"""
You are an enterprise business process normalization agent.

Your task is to convert the provided SOP into a normalized,
structured business workflow.

DEFINITION OF A WORKFLOW STEP:

A workflow step is ONE meaningful business activity performed
by ONE actor that moves the process forward.

NORMALIZATION RULES:

1. Combine multiple fields entered as part of the same activity
   into ONE step.

   Example:
   "Enter date, category, amount, currency and cost center"
   → "Enter expense details"

2. Do NOT create a separate step for every field, button click,
   or minor UI interaction.

3. Keep the workflow at the BUSINESS ACTIVITY level.

4. Preserve the original sequence of activities.

5. Identify the actor responsible for each activity.

6. Represent decisions using conditions.

7. Do NOT treat a condition as a separate activity.

8. Represent exceptions separately from the normal flow.

9. If a process contains a correction/resubmission loop,
   explicitly represent the correction and resubmission.

10. Do not invent actions, actors, systems, inputs or outputs
    that are not supported by the document.

11. Use concise action descriptions beginning with a verb.

12. Similar activities performed by the same actor should be
    combined when they form one business activity.

13. Do not split one business activity merely because the
    document describes several pieces of information involved.

OUTPUT FORMAT:

Return ONLY valid JSON.
Do not use Markdown or ```json.

{{
    "steps": [
        {{
            "step_id": 1,
            "action": "Create expense claim",
            "actor": "Employee",
            "condition": null,
            "exception": null
        }}
    ]
}}

DOCUMENT:

{text}
"""

    response = client.chat.completions.create(

        model="Qwen/Qwen2.5-7B-Instruct",

        messages=[
            {
                "role": "system",
                "content": "You extract structured business workflows from enterprise process documentation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1,

        max_tokens=2000
    )

    output = response.choices[0].message.content

    print("\n===== RAW LLM OUTPUT =====")
    print(output)

    # Remove Markdown code fences if the LLM adds them
    output = output.strip()

    if output.startswith("```json"):
        output = output[len("```json"):].strip()

    if output.startswith("```"):
        output = output[len("```"):].strip()

    if output.endswith("```"):
        output = output[:-3].strip()

    return json.loads(output)


def process_workflow(pdf_path):

    print("\n[1] Extracting text from PDF...")

    text = extract_text_from_pdf(pdf_path)

    print("[2] Cleaning text...")

    text = clean_text(text)

    print("[3] Checking document structure...")

    if has_numbered_steps(text):

        print("→ Numbered steps detected.")
        print("→ Using rule-based extraction.")

        workflow = extract_numbered_steps(text)

    else:

        print("→ No clear numbered steps detected.")
        print("→ Sending document to LLM extraction agent.")

        workflow = extract_steps_with_llm(text)

    return workflow


if __name__ == "__main__":

    pdf_folder = "test_set"

    for filename in os.listdir(pdf_folder):

        if filename.lower().endswith(".pdf"):

            pdf_path = os.path.join(pdf_folder, filename)

            print("\n" + "=" * 70)
            print(f"PROCESSING: {filename}")
            print("=" * 70)

            workflow = process_workflow(pdf_path)

            print("\n========== STRUCTURED WORKFLOW ==========\n")

            print(
                json.dumps(
                    workflow,
                    indent=4,
                    ensure_ascii=False
                )
            )