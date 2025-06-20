# recipes/example_*

[collect-files]

**Search:** ['recipes/example_*']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 6/18/2025, 12:10:57 PM
**Files:** 24

=== File: recipes/example_brave_search/README.md ===
# Brave Search Recipe

This recipe demonstrates use of the Brave Search API to perform a search and retrieve results.

It allows for passing of the BRAVE_API_KEY as either a context variable or an environment variable.

## Run the Recipe

### Use env var for API key

```bash
export BRAVE_API_KEY=your_api_key

# From the repo root, run the recipe with the test project
recipe-tool --execute recipes/example_brave_search/search.json \
   query="Tell me about model context protocol." \
   model=openai/o4-mini
```

### Use context variable for API key

```bash
# From the repo root, run the recipe with the test project
recipe-tool --execute recipes/example_brave_search/search.json \
   query="Tell me about model context protocol." \
   model=openai/o4-mini \
   brave_api_key=your_api_key
```


=== File: recipes/example_brave_search/search.json ===
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Perform a search for {{ query }} using the Brave Search API. Format the results, summarizing the content and extracting the most relevant information. The output should be a list of URLs and their corresponding summaries. Ensure that the search is comprehensive and covers various aspects of the query. Current date: {{ now }}",
        "model": "{{ model | default: 'openai/gpt-4o' }}",
        "mcp_servers": [
          {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
              "BRAVE_API_KEY": "{{ brave_api_key }}"
            }
          }
        ],
        "output_format": "text",
        "output_key": "search_results"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "search_results.md",
            "content_key": "search_results"
          }
        ],
        "root": "{{ output_root | default: 'output' }}"
      }
    }
  ]
}


=== File: recipes/example_builtin_tools/README.md ===
# Built-in Tools Examples

This directory contains example recipes demonstrating the use of OpenAI's built-in tools with the Recipe Tool.

## What are Built-in Tools?

Built-in tools are OpenAI's Responses API features that provide models with access to:
- **Web Search** (`web_search_preview`) - Search the web for current information

## Model Support

Built-in tools are only supported with Responses API models:
- `openai_responses/*` - OpenAI Responses API models
- `azure_responses/*` - Azure OpenAI Responses API models

## Examples

### Web Search Demo (`web_search_demo.json`)
Demonstrates using the web search tool to find current information about Python 3.13 features.

**Usage:**
```bash
# With OpenAI
recipe-tool --execute recipes/example_builtin_tools/web_search_demo.json model=openai_responses/gpt-4o

# With Azure OpenAI  
recipe-tool --execute recipes/example_builtin_tools/web_search_demo.json model=azure_responses/gpt-4o
```


## Recipe Structure

Built-in tools are specified using the `openai_builtin_tools` parameter in `llm_generate` steps:

```json
{
  "step_type": "llm_generate",
  "model": "openai_responses/gpt-4o",
  "openai_builtin_tools": [
    {"type": "web_search_preview"}
  ]
}
```

## Error Handling

- Built-in tools only work with `*_responses` models
- Only `web_search_preview` tool type is currently supported
- Clear error messages will be shown for invalid configurations

=== File: recipes/example_builtin_tools/web_search_demo.json ===
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "model": "{{ model | default: 'openai_responses/gpt-4o' }}",
        "openai_builtin_tools": [{ "type": "web_search_preview" }],
        "prompt": "Search the web for 'latest Python 3.13 features' and provide a comprehensive summary of the new features and improvements introduced in Python 3.13. Focus on the most significant changes that developers should know about.",
        "output_format": "text",
        "output_key": "features_summary"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "features_summary.md",
            "content_key": "features_summary"
          }
        ],
        "root": "{{ output_root | default: 'output' }}"
      }
    }
  ]
}


=== File: recipes/example_complex/README.md ===
# Complex Recipe Example

Multi-step workflow demonstrating file reading, LLM generation, and sub-recipe execution.

```bash
recipe-tool --execute recipes/example_complex/complex_example.json
```


=== File: recipes/example_complex/complex_example.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/git_collector/PYDANTIC_AI_DOCS.md",
        "content_key": "pydantic_ai_docs"
      }
    },
    {
      "type": "parallel",
      "config": {
        "substeps": [
          {
            "type": "llm_generate",
            "config": {
              "prompt": "You are an expert Python developer. Using the PydanticAI documentation below:\n\n{{pydantic_ai_docs}}\n\nGenerate a module named 'chat_client.py' that implements a simple chat client which connects to an LLM for conversation. The code should be well-structured and include error handling.",
              "model": "openai/gpt-4o",
              "mcp_servers": [
                { "command": "python-code-tools", "args": ["stdio"] }
              ],
              "output_format": "files",
              "output_key": "chat_client_file"
            }
          },
          {
            "type": "llm_generate",
            "config": {
              "prompt": "You are an expert Python developer. Using the PydanticAI documentation below:\n\n{{pydantic_ai_docs}}\n\nGenerate a module named 'chat_server.py' that implements a simple chat server which interacts with an LLM for handling conversations. Ensure the code structure is clear. IMPORTANT: Intentionally include a couple of deliberate syntax errors in the code to test error detection (for example, missing colon, unbalanced parentheses).",
              "model": "openai/gpt-4o",
              "mcp_servers": [
                { "command": "python-code-tools", "args": ["stdio"] }
              ],
              "output_format": "files",
              "output_key": "chat_server_file"
            }
          },
          {
            "type": "llm_generate",
            "config": {
              "prompt": "You are an expert Python developer. Using the PydanticAI documentation below:\n\n{{pydantic_ai_docs}}\n\nGenerate a module named 'linting_tool.py' that creates a function to lint Python code. The module should call an external linting tool, capture its output (lint report), and return both the possibly corrected code files and the lint report. Make sure the output is structured as a list of file specifications.\n",
              "model": "openai/gpt-4o",
              "mcp_servers": [
                { "command": "python-code-tools", "args": ["stdio"] }
              ],
              "output_format": "files",
              "output_key": "linting_result"
            }
          }
        ],
        "max_concurrency": 3,
        "delay": 0
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "You are given three JSON arrays representing file specifications from previous steps:\n\nChat Client Files: {{chat_client_file}}\n\nChat Server Files: {{chat_server_file}}\n\nLinting Result Files: {{linting_result}}\n\nCombine these arrays into a single JSON array of file specifications without modifying the content of the files. Return the result as a JSON array.",
        "model": "openai/gpt-4o",
        "mcp_servers": [{ "command": "python-code-tools", "args": ["stdio"] }],
        "output_format": "files",
        "output_key": "final_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "final_files",
        "root": "output/complex_example"
      }
    }
  ]
}


=== File: recipes/example_complex/recipe_creator_idea/complex_example_idea.md ===
Create a recipe file named `complex_example.json` that generates a recipe file based on the following scenario:

Let's write some code that uses the PydanticAI library (docs for it are located in `ai_context/git_collector/PYDANTIC_AI_DOCS.md`, have the recipe read the content of this file in) to create simple chat client that uses an LLM. Have it create multiple files and use the parallel step to generate them in parallel.

But let's also test the use of MCP servers within the LLM generate steps. Configure the LLM step to use our python code tools MCP server (details below). Then let's ask the LLM to generate some code to use it's linting tool and returning a report from that along with the code files. However, intentionally include some errors in the code in **one** of the modules. Finally write the final code to individual files in `output/complex_example`.

Here are the details for the python code tools MCP server:
command: `python-code-tools`
args: `stdio`


=== File: recipes/example_content_writer/data/ai_took_my_job-what_now.md ===
# [AI Took My Job — What Now?!](https://medium.com/@paradox921/ai-took-my-job-what-now-d08132c8f1ad)

[Brian Krabach](https://medium.com/@paradox921) | Apr, 2025 | Medium

Imagine spending months hand‑crafting a bespoke mechanical watch, only to wake up and find an automated manufacturing line has produced an indistinguishable copy overnight. That’s how it felt when an **AI system** took over the work I’d spent decades mastering. One day I was the craftsman with a rare skill and passion; the next, a cold algorithmic workflow replicated my output in a fraction of the time. I sat there, stunned. Did that really happen? My stomach dropped as confusion turned into panic. This wasn’t just losing a job — it felt like losing a piece of myself.

To be clear, I’m not unemployed. But I’m no longer doing the job I’ve done for decades. As a software engineer I’m not writing code every day — and I’m not sure there’s a place for me to keep doing so professionally, going forward.

> **The work hasn’t vanished, but the gate has swung open.** We still need high‑quality code; it’s simply becoming something anyone can generate with the right prompts. My value can’t hinge on access to the keyboard alone. It has to uplevel.

My story isn’t unique. The disruption that **AI technology** is bringing to software engineering mirrors what countless trades have faced when their lifelong skills were displaced by new inventions or made so accessible there was no longer a premium market for them.

# Fear of Obsolescence

Once the shock wore off, fear crept in.

If a machine could do in minutes what took me years to master, what did that say about my future? I felt like a wagon maker in the age of the automobile, a blacksmith watching an assembly line churn out steel horseshoes faster than I could hammer one. I had always taken pride in the intuition and craft I poured into every project. But now? I wasn’t sure those human touches mattered.

In the quiet moments I asked myself:

- Are my skills becoming obsolete?
- Is any part of what I do *not* replicable by code and silicon?

# This Isn’t New… But It Still Hit Hard

The latest tipping point came when OpenAI released a new Codex coding agent. I had recently worked on a project that automates software development using **AI tools** — a tool I was proud of, built over days and already accelerated by earlier automation. Curious, I asked Codex to try the same task. It did — *in minutes* — producing a passable version with tests and iterations. Suddenly I questioned whether I should even finish the new work I’d started.

I’ve felt that sting every few weeks for the past few years. My role puts me on the front lines of this wave — or, as my boss calls it, “running in front of the avalanche.” The very systems I help build inevitably make yesterday’s work unnecessary.

Every new breakthrough article, every clever demo, every excited conversation about what **AI tech** can do next is exhilarating. But it also feels like watching the horizon close in on what used to be mine. Projects that once needed a team — or at least me — now need a single person with the right **AI stack**. They don’t even need to be a software engineer.

# Reflection

After enough of those nights — the anxious ones followed by uncertain mornings — I realized I needed to step back and figure out what really mattered. I also thought about the broader impact, especially with my kids finishing college and stepping into careers certain to collide with the same disruption.

As I pondered, a subtle shift began. I remembered why I fell in love with coding in the first place. It wasn’t the routine tasks or job security; it was creating something from nothing, solving problems in inventive ways, and helping people through that work.

It was always about *what* I built and *who* it helped. That spark — my *why* — was still there, just buried under fear. Even if the *way* I worked was changing, the *goal* could stay the same. Ironically, the routine tasks I can offload to **AI tools** were what had been holding me back from spending more time doing the parts I loved. As someone close to me observed, when I don’t lean on automation, *I* become the bottleneck to my own creativity.

I have access to super‑powers I’ve never had before — **we all do**.

# A Familiar Pattern in History

Every generation faces a moment when a previously scarce skill becomes abundant:

- **Scribes → Printing Press**: Hand‑copied manuscripts gave way to mass‑produced books, freeing writers to reach orders of magnitude more readers.
- **Darkroom Photographers → Digital Cameras**: Mastery of chemicals and film stock became optional; storytelling through images exploded.
- **Gate‑kept Music Production → Home Studios**: What once required a record‑label budget now fits on a laptop, unleashing independent artists.
- **Accounting Ledgers → Spreadsheets**: Bean‑counting automated, while financial analysis and strategy ballooned.

Craftsmanship didn’t disappear in any of these shifts; it evolved. The same thing is happening with software development today.

# Reframing the Future

With that lens I stopped seeing automation as a threat and started treating it as raw material — powerful, but shapeable. The question shifted from *What have I lost?* to *What can I do now that I couldn’t before?*

I thought back to childhood evenings spent building wild spaceships from LEGO bricks. The pieces were just the medium; the magic was in the vision. **AI systems** started to feel like an enormous pile of self‑assembling bricks that still needs a human architect.

Then another realization hit me:

**This change isn’t coming — it has already happened.**

I haven’t written code by hand in more than two months. I feed ideas, specs, and goals into automation that generates what I need — blueprints and all. I’m tackling bigger ideas, faster, with less friction than ever before.

And I almost missed it happening. I’ve been having the time of my life, bringing more ideas to reality at a velocity I’ve never experienced.

I’ve moved from laying every brick myself to sketching the blueprints of entire structures — structures **AI tools** bring to life.

My craftsmanship shifted too. Offloading quality coding to automation frees me to obsess over the user experience. I spend less time per feature **_and more_** time testing it with a user’s eyes, iterating toward the *right* experience. Somehow, it still has my fingerprints all over it — in fact, in ways that are more visible than ever!

# Rediscovering My Why

This journey — from panic to possibility — brought me back to the core: the joy of creation, the thrill of solving something hard, the satisfaction of building work that matters.

**AI technology** didn’t extinguish that spark; it reignited it.

I don’t fixate on the tasks automation does better. I focus on what only I can do — vision, empathy, creative leaps. Those human elements sit in the center of my work again.

Fear still shows up, but it doesn’t stay long. The machine might produce the watch, but it can’t *dream* it up. It doesn’t get chills when the idea lands. It doesn’t have a why. It’s just a tool.

# Not Just My Story

I’m watching this play out everywhere:

- Product‑managers once blocked for months waiting for engineering resources are iterating on full prototypes before getting to that point.
- Solo entrepreneurs spin up cloud backends, analytics pipelines, and marketing sites, scaling their ideas from scratch.
- Data analysts use natural‑language SQL helpers to surface insights without being required to write programming-like queries.
- Teachers craft interactive lesson plans, complete with quizzes and graphics, in an afternoon.
- Designers co‑create concepts with generative imagery, then focus on nuance and brand.
- Friends in mid‑career switch tracks entirely, leveraging **AI tech** to cross skill gaps that once felt like walls.

# Practical Ways to Lean In (Right Now)

1.  **Uplevel Your Thinking First**: Let automation handle the mechanical steps — drafting prose, crunching numbers, laying out designs — so you can invest brainpower in strategy, creativity, and impact.
2.  **Prototype at Whiteboard Speed**: Ask AI tools for first‑pass drafts — concept sketches, schedules, or marketing pitches — then use your expertise to pressure‑test and refine.
3.  **Direct, Don’t Dictate**: Treat the tools like an eager apprentice — delegate repetitive chores, inspect its output for fit, and coach it with context only you possess.
4.  **Deepen Your Domain Mojo**: Whether you’re in finance, healthcare, art, or carpentry, the sharper your subject knowledge, the more transformative your automation‑powered solutions become.
5.  **Invest Saved Time in Human Value**: Pour reclaimed hours into client conversations, storytelling, mentorship, and bold experiments — the uniquely human work machines can’t replicate.

# What About You?

What’s been locked up for you?What could you create if the friction disappeared?What dream have you shelved that **AI super‑powers** might help revive?

You don’t have to have it all figured out. Your *real* job might be waiting on the other side of that first spark of curiosity.

It’s still uniquely human. Still uniquely yours.Still bursting with potential.


=== File: recipes/example_content_writer/data/embracing_ai_for_adhd_assistance.md ===
# [Embracing AI for ADHD Assistance](https://medium.com/@paradox921/embracing-ai-for-adhd-assistance-29dcb23a9d35)

[Brian Krabach](http://medium.com/@paradox921) | Apr, 2025 | Medium

My day job at Microsoft is to lead an innovation team centered on exploring the cutting edge of AI and making it more accessible for the benefit of everyone. I also have ADHD, which brings some significant advantages in this space as well as many challenges.

Here are some insights that didn't come about from a planned experiment. They emerged organically - as I navigated my own challenges with ADHD and observed the experiences of friends and colleagues in the community. Use of AI assistance here isn't meant to "fix" us; rather, it offers a way to leverage today's tools for safe, patient, always-on thinking, processing, and learning that adapts to our naturally diverse ways of thinking.

This is a collection of examples, drawn from my own experiences, that illustrate how AI can help us work with our "neurodivergent" brains instead of against them. While these tips stem from my personal journey, many of them apply more broadly as well.

## How I Use AI for Assistance

**Thinking Out Loud, Safely:**  
I process verbally. With AI, I can freely dump raw, mid-process thoughts without fear of misunderstanding or judgment. It helps me clarify my ideas faster and turn them into something structured and shareable.

**From Chaos to Clarity:**  
Whether it's from long voice sessions or typed notes, I can offload everything and later ask the AI to organize, distill, and clean it up without losing my voice.

**Different Formats for Different Audiences:**  
I can repurpose these raw interactions into "lightweight" versions - be it an outline, a summary, or a metaphor-rich narrative - tailoring the information to fit the needs and preferences of my audience.

**Digesting Heavy Material, My Way:**  
Long, dense documents can be overwhelming. I break them down into bite-sized pieces or have them restructured into story, metaphor, or Q&A formats - whichever helps me process and retain the info.

**Context-Carrying for Multitasking:**  
I bounce between topics constantly. AI can keep track of my context so I can jump back in later without missing a beat.

**Capturing Fast-Moving Thoughts:**  
I can chase multiple ideas at once, and the AI helps organize, label, and recover any useful insights - so I don't have to keep track manually.

**Accelerated Creative Breakthroughs:**  
I frequently compress a week's worth of "aha moments" into an afternoon by bouncing ideas around with the assistant.

**Leveraging Misinterpretation for Insight:**  
The AI sometimes misunderstands me, and that sparks new ideas. This feedback loop becomes a creative asset.

**Preprocessing for Human Interactions:**  
I now show up to team discussions or presentations more prepared and clearer - saving time and reducing confusion.

**Practicing Effective Dialogue Habits:**  
Having to speak in bursts - especially when technical hiccups lose the message, and it is hard for me to repeat a long, rambling message - led to discovering the value of more bi-directional exchange and has taught me to communicate in shorter, clearer, and more interactive exchanges with others.

**Learning Better Phrasing by Example:**  
I often ask the AI to rework rough drafts or emotional reactions into cleaner, more effective responses - and I've learned a lot from how it does that.

## Learnings from Others Around Me

The examples above, though drawn from my personal experience, resonate with many individuals navigating ADHD. Here are some generalized insights I've seen work for others - and that I'm learning from as well:

**Rebuilding Confidence:**  
Many of us have struggled with feeling misunderstood - sometimes even at the cost of relationships or opportunities. Using these tools enables us to engage more effectively, be heard, and be understood. It can be genuinely life-changing.

**Sharpening Communication Instincts:**  
By observing how the AI organizes and reframes input, you learn which parts of your message truly matter. This ongoing feedback helps you understand what information is essential and how best to present it.

**Refining Ideas Before Sharing:**  
Conversing privately with the AI allows you to test how something lands, adjust based on the response, and walk into conversations feeling more grounded and prepared.

**Turning Overwhelming Tasks into Fast Wins:**  
Tasks that once felt monumental - like compiling a detailed response or drafting important communication - now take minutes with AI support.

**Safe Emotional Offloading:**  
When emotions threaten to derail communication, the can AI provide a clear outlet to vent and later refine those raw thoughts into balanced, thoughtful expressions.

**Reducing Reactivity, Increasing Clarity:**  
The AI can act as a buffer, helping you reflect and respond thoughtfully rather than react impulsively.

## A New Chapter in Communication

These aren't just improvements in productivity - they're steps toward reclaiming control over how we think and communicate. AI assistance doesn't replace human interaction or magically produce the perfect response; it becomes a flexible tool that adapts to our strengths and fills in the gaps caused by ADHD. The evolution of these interactions can enhance creativity and insight while building a more confident, clear, and authentic way of being heard.

I hope these insights spark further exploration and conversation. Based on feedback that these learnings are helpful to others, I'll continue sharing new discoveries on how these tools are transforming not just the work we do, but the way we live and connect.

**Curious about the "how"?**  
Someone asked me about how I create that "verbal space" to transform raw ideas into clear, organized thoughts using AI, check out my follow-up post: [Vibing with AI to Process, Organize, and Communicate Ideas](https://medium.com/vibing-with-ai-to-process-organize-and-communicate-ideas-06bd107c987a).

_Exploring AI, one conversation at a time._


=== File: recipes/example_content_writer/generate_content.json ===
{
  "description": "Generate new Markdown content from an idea file plus optional context and reference style.",
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ idea }}",
        "content_key": "idea_content"
      }
    },
    {
      "type": "conditional",
      "config": {
        "condition": "{% if files %}true{% else %}false{% endif %}",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ files }}",
                "content_key": "additional_files_content",
                "merge_mode": "concat",
                "optional": true
              }
            }
          ]
        }
      }
    },
    {
      "type": "conditional",
      "config": {
        "condition": "{% if reference_content %}true{% else %}false{% endif %}",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ reference_content }}",
                "content_key": "reference_content",
                "merge_mode": "concat",
                "optional": true
              }
            }
          ]
        }
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "You are a professional writer.\\n\\n<IDEA>\\n{{ idea_content }}\\n</IDEA>\\n\\n{% if additional_files_content %}<ADDITIONAL_FILES>\\n{{ additional_files_content }}\\n</ADDITIONAL_FILES>\\n{% endif %}\\n\\n{% if reference_content %}<REFERENCE_CONTENT>\\n{{ reference_content }}\\n</REFERENCE_CONTENT>\\n{% endif %}\\n\\nUsing the IDEA (and ADDITIONAL_FILES for context if provided), write a complete Markdown article in the style of the REFERENCE_CONTENT if that section exists; otherwise use a crisp, conversational tech-blog tone.\\n\\nReturn exactly one JSON array with a single object matching this schema:\\n[\\n  {\\n    \\\"path\\\": \\\"{{ output_root | default: 'output' }}/<slugified_title>.md\\\",\\n    \\\"content\\\": \\\"<full_markdown_document>\\\"\\n  }\\n]\\n*Replace* <slugified_title> with a kebab-case version of the article title (e.g. \\\"AI-and-you\\\").\\nDo not add any keys or commentary outside that JSON array.",
        "model": "{{ model | default: 'openai/gpt-4o' }}",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files"
      }
    }
  ]
}


=== File: recipes/example_content_writer/recipe_creator_idea/content_from_idea.md ===
Create a recipe file named `generate_content.json` that generates new content based on the following scenario:

Input context variables:

- A file that contains the big idea for the new content: `idea` context variable, required.
- Additional files to include in the context for the content: `files` context variable, optional.
- Reference files used to demonstrate the user's voice and style: `reference_content` context variable, optional.
- The model to use for generating the content: `model` context variable, optional.
- The root directory for saving the generated content: `output_root` context variable, optional.

Read in the content of the files above and then:

Generate some new content based the combined context of the idea + any additional files and then, if provided, tartget the style of the reference content. The generated content should be saved in a file named `<content_title>.md` in the specified output directory.


=== File: recipes/example_mcp_step/mcp_step_example.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{input}}",
        "content_key": "code",
        "optional": false,
        "merge_mode": "concat"
      }
    },
    {
      "type": "mcp",
      "config": {
        "server": {
          "command": "python-code-tools",
          "args": ["stdio"]
        },
        "tool_name": "lint_code",
        "arguments": {
          "code": "{{code}}",
          "fix": true,
          "config": "{}"
        },
        "result_key": "code_analysis"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate a comprehensive report based on the following code analysis results:\n{{ code }}\n{{ code_analysis }}\n\nSave to: {{ input | split: '.' | first }}_code_analysis.md",
        "model": "openai/gpt-4o",
        "output_format": "files",
        "output_key": "generated_report"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_report",
        "root": "output"
      }
    }
  ]
}


=== File: recipes/example_mcp_step/prompt/mcp_step_idea.md ===
Create a recipe named `mcp_step_example.json` that demonstrates the use of the MCP step in a recipe. The recipe should:

- Read in a code file from a path provided via the `input` context variable.
- Pass the code file to the MCP step for processing using a specific tool call:

  - MCP Server:

    - Command: `python-code-tools`
    - Args: `stdio`

  - Tool Call:

    ```python
    async def lint_code(code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Lint Python code and optionally fix issues.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A dictionary containing the fixed code, issues found, and fix counts
    ```

- Pass the results of the tool call to an LLM step to generate a report and output as type `files`:

```prompt
Generate a comprehensive report based on the following code analysis results:
{{ code }}
{{ code_analysis }}

Save to: [{{ input }} file name w/o extension] + `_code_analysis.md`.
```

- Write the file to the `output` directory.


=== File: recipes/example_quarterly_report/demo-data/historical-sales.csv ===
Region,Product,Revenue,Units,Customers,Quarter
North,Product A,1100000,4800,380,Q1 2025
North,Product B,820000,3280,280,Q1 2025
North,Product C,480000,1920,160,Q1 2025
South,Product A,920000,3840,320,Q1 2025
South,Product B,1200000,4800,410,Q1 2025
South,Product C,600000,2400,200,Q1 2025
East,Product A,1000000,4200,350,Q1 2025
East,Product B,720000,2880,240,Q1 2025
East,Product C,400000,1600,130,Q1 2025
West,Product A,1300000,5400,460,Q1 2025
West,Product B,900000,3600,300,Q1 2025
West,Product C,660000,2640,220,Q1 2025
North,Product A,980000,4400,350,Q4 2024
North,Product B,740000,3000,260,Q4 2024
North,Product C,420000,1700,140,Q4 2024
South,Product A,850000,3600,300,Q4 2024
South,Product B,1050000,4300,380,Q4 2024
South,Product C,520000,2100,180,Q4 2024
East,Product A,930000,3900,330,Q4 2024
East,Product B,650000,2600,220,Q4 2024
East,Product C,350000,1400,120,Q4 2024
West,Product A,1150000,4800,410,Q4 2024
West,Product B,820000,3300,280,Q4 2024
West,Product C,580000,2350,200,Q4 2024

=== File: recipes/example_quarterly_report/demo-data/q2-2025-sales.csv ===
Region,Product,Revenue,Units,Customers,Quarter
North,Product A,1250000,5200,428,Q2 2025
North,Product B,890000,3560,312,Q2 2025
North,Product C,520000,2080,175,Q2 2025
South,Product A,980000,4100,350,Q2 2025
South,Product B,1340000,5360,462,Q2 2025
South,Product C,650000,2600,220,Q2 2025
East,Product A,1080000,4500,385,Q2 2025
East,Product B,760000,3040,261,Q2 2025
East,Product C,430000,1720,148,Q2 2025
West,Product A,1420000,5920,510,Q2 2025
West,Product B,960000,3840,330,Q2 2025
West,Product C,720000,2880,246,Q2 2025


=== File: recipes/example_quarterly_report/demo_quarterly_report_recipe.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ new_data_file }}",
        "content_key": "new_data_csv"
      }
    },
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists('{{ historical_data_file }}')",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ historical_data_file }}",
                "content_key": "historical_data_csv",
                "optional": true
              }
            }
          ]
        }
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "company_name",
        "value": "{{ company_name | default: 'Our Company' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "quarter",
        "value": "{{ quarter | default: 'auto-detect' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "output_root",
        "value": "{{ output_root | default: 'output' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "model",
        "value": "{{ model | default: 'openai/o4-mini' }}"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "You are a business analyst generating a quarterly business report for {{ company_name }} for {{ quarter }}. Use the new quarterly data CSV:\n{{ new_data_csv }}\n{% if historical_data_csv %}Also use the historical data CSV:\n{{ historical_data_csv }}\n{% endif %}Calculate key performance metrics (revenue growth, customer acquisition, etc.), compare the current quarter with historical trends, and identify significant patterns and outliers. Provide the results as a JSON object with the following structure:{\n  \"executive_summary\": \"...\",\n  \"metrics\": {\"revenue_growth\": \"...\", \"customer_acquisition\": \"...\"},\n  \"trends_chart\": \"<mermaid flowchart>...\",\n  \"product_performance_chart\": \"<mermaid pie>...\",\n  \"regional_analysis\": \"...\",\n  \"recommendations\": \"...\"\n}Only output valid JSON.",
        "model": "{{ model }}",
        "output_format": {
          "type": "object",
          "properties": {
            "company_name": {"type": "string"},
            "executive_summary": {"type": "string"},
            "metrics": {
              "type": "object",
              "properties": {
                "revenue_growth": {"type": "string"},
                "customer_acquisition": {"type": "string"}
              },
              "required": ["revenue_growth", "customer_acquisition"]
            },
            "trends_chart": {"type": "string"},
            "product_performance_chart": {"type": "string"},
            "quarter": {"type": "string"},
            "regional_analysis": {"type": "string"},
            "recommendations": {"type": "string"}
          },
          "required": ["executive_summary", "metrics", "trends_chart", "product_performance_chart", "regional_analysis", "recommendations"]
        },
        "output_key": "analysis"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Using the analysis in context and original data, generate a comprehensive markdown-formatted business report for {{ company_name }} for {{ quarter }}. Include an Executive Summary, Key Metrics table, Mermaid charts for trends and product performance using {{ analysis.trends_chart }} and {{ analysis.product_performance_chart }}, a Regional Performance Analysis section, and Strategic Recommendations. Reported generated on {{ 'now' | date: '%m-%d-%Y %H:%M' }}. Output the report in valid markdown.",
        "model": "{{ model }}",
        "output_format": "text",
        "output_key": "report_md"
      }
    },
    {
      "type": "write_files",
      "config": {
        "root": "{{ output_root }}/{{ analysis.company_name | replace: ' ', '_' }}",
        "files": [
          {
            "path": "Business_Report_{{ analysis.quarter | replace: ' ', '_' }}.md",
            "content_key": "report_md"
          }
        ]
      }
    }
  ]
}


=== File: recipes/example_simple/README.md ===
# Simple Recipe Example

Basic workflow demonstrating file reading, code generation, and writing.

## Quick Examples

```bash
# Generate code from a simple specification, producing a Hello World script.
recipe-tool --execute recipes/example_simple/code_from_spec_recipe.json \
   spec_file=recipes/example_simple/specs/hello-world-spec.txt
```

```bash
# Generate code for a Hello World app using Gradio.
recipe-tool --execute recipes/example_simple/code_from_spec_recipe.json \
   spec_file=recipes/example_simple/specs/hello-world-gradio-spec.md
```

```bash
# Generate a roll-up file from all text files in a directory.
recipe-tool --execute recipes/example_simple/code_from_spec_recipe.json \
   spec_file=recipes/example_simple/specs/file-rollup-tool-spec.md
```


=== File: recipes/example_simple/code_from_spec_recipe.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ spec_file | default: 'recipes/example_simple/specs/sample_spec.txt' }}",
        "content_key": "spec_text"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Using the following specification, generate a Python script:\n\n{{ spec_text }}",
        "model": "{{ model | default: 'openai/o4-mini' }}",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files",
        "root": "{{ output_root | default: 'output' }}"
      }
    }
  ]
}


=== File: recipes/example_simple/specs/file-rollup-tool-spec.md ===
A simple tool for creating a roll-up file of all of the text files in a directory.

Requirements:

- All text files in the directory should be rolled up into a single file.
- Command line arguments should be used to specify the input directory and the output file.
  - The input directory should be specified with the `--input` argument.
  - The output file should be specified with the `--output` argument.
- The tool should be able to handle subdirectories and roll up all text files in the directory tree.
- An optional argument `--exclude` should be provided to exclude certain files or directories from the roll-up.
  - The `--exclude` argument should accept a comma-separated list of file or directory names to exclude or a wildcard pattern.
- Any non-text files should be ignored.
- The tool should be named `rollup.py`.


=== File: recipes/example_simple/specs/hello-world-gradio-spec.md ===
Create a simple "Hello World" app using Gradio in python.


=== File: recipes/example_simple/specs/hello-world-spec.txt ===
Print "Hello, Test!" to the console.


=== File: recipes/example_templates/README.md ===
# Example Templates

# Extras Demo

This example shows how to use the `extra filters` feature of the Python Liquid support in `recipe_executor` to create a Markdown file for each item in a JSON array.

## Run the Recipe

```bash
# From the repo root, run the recipe with the test project
recipe-tool --execute recipes/example_templates/extras_demo.json \
   input_file=recipes/example_templates/data/items.json \
   output_root=output/templates \
   model=openai/o4-mini
```

## What’s happening

- **`read_files`** loads your data file and pulls in a JSON array as `items`.
- **`loop`** iterates each `item` and:
  - creates a `slug` via `snakecase`
  - parses & reformats `item.timestamp` with `datetime`
  - pretty-prints `item.metadata` with `json`
- **`write_files`** spits out one Markdown file per item, using those context vars in both filename and body.


=== File: recipes/example_templates/data/items.json ===
[
  {
    "name": "Sample Item",
    "timestamp": "2025-05-07T09:00:00Z",
    "metadata": {
      "color": "red",
      "size": "L"
    }
  },
  {
    "name": "Another Item",
    "timestamp": "2025-01-01T12:30:45Z",
    "metadata": {
      "color": "blue",
      "size": "M"
    }
  }
]


=== File: recipes/example_templates/extras_demo.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ input_file }}",
        "content_key": "items"
      }
    },
    {
      "type": "loop",
      "config": {
        "items": "items",
        "item_key": "item",
        "result_key": "item.content",
        "substeps": [
          {
            "type": "set_context",
            "config": {
              "key": "slug",
              "value": "{{ item.name | snakecase }}"
            }
          },
          {
            "type": "set_context",
            "config": {
              "key": "readable_date",
              "value": "{{ item.timestamp | datetime: format: 'MMM d, y' }}"
            }
          },
          {
            "type": "set_context",
            "config": {
              "key": "file_content",
              "value": "# {{ item.name }}\n\n- **Slug**: `{{ slug }}`\n- **Date**: {{ readable_date }}\n- **Metadata**:\n```json\n{{ item.metadata | json: indent: 2 }}\n```"
            }
          },
          {
            "type": "write_files",
            "config": {
              "files": [
                {
                  "path": "{{ slug }}.md",
                  "content_key": "file_content"
                }
              ],
              "root": "{{ output_root | default: 'output' }}"
            }
          }
        ]
      }
    }
  ]
}


