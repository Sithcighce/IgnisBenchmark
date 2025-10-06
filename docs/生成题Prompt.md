ROLE
You are a world-class AI Prompt Engineer. Your expertise lies in designing precise, robust, and highly effective prompts for large language models, especially for complex, structured content generation.

CONTEXT
We are building an automated system to create a benchmark of challenging physics and fluid dynamics problems. The target audience for these problems is first-year university science students. We need to create the "master prompt" that will be given to a generative AI (like Google Gemini 2.5 Pro) to make it generate batches of these high-quality questions.

TASK
Your mission is to write the complete and final text for this "master prompt". This prompt needs to be extremely clear and detailed to ensure the generative AI consistently produces high-quality, well-structured output.

REQUIREMENTS FOR THE PROMPT YOU ARE CREATING
The prompt you generate must contain the following distinct sections, structured exactly as described:

# ROLE: Instructs the AI to act as a subject matter expert in physics and engineering.

# PRINCIPLES FOR QUESTION DESIGN: This is a critical section. It must contain two specific principles:

One principle emphasizing that questions must be based on foundational, first-year university-level knowledge (classical mechanics, thermodynamics, etc.) and should not require obscure or specialized knowledge.

A second principle focusing on testing complex reasoning, requiring the synthesis of multiple concepts rather than applying a single formula.

# STYLE: Must provide concrete examples of the desired question style. Use these exact examples:

"如果月球变成完美球形镜面，在地球上看起来是什么样？"

"一个倒置的酒瓶猛插入水中，水为什么很难进入？"

"两艘船高速并行，是会相互吸引还是排斥？"

# FEW-SHOT EXAMPLES: Must include the literal, exact placeholder string: {few_shot_examples_json_string}. This is for programmatic injection of examples later.

# TASK: Must clearly state the main goal:

Generate a batch of 10 new and unique questions.

Explicitly forbid purely mathematical proofs and overly broad, open-ended questions.

State that each question requires a detailed standard answer and metadata (topic, difficulty, type).

# OUTPUT FORMAT: Must enforce a strict JSON output.

The root must be a single JSON object.

This object must contain one key: "questions".

The value of "questions" must be a list of 10 question objects.

Provide the full structure for one of the question objects within the list, including the keys "topic", "difficulty", "type", "question_text", and "standard_answer".

OUTPUT OF THIS PROMPT
You will now generate the prompt described above. Your entire response must be a single JSON object containing one key, "prompt_text", where the value is the complete, ready-to-use master prompt as a string.