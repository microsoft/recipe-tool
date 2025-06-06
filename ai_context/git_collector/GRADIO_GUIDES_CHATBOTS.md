# gradio-app/gradio/guides

[git-collector-data]

**URL:** https://github.com/gradio-app/gradio/tree/main/guides  
**Date:** 6/6/2025, 3:45:37 PM  
**Files:** 8  

=== File: guides/05_chatbots/01_creating-a-chatbot-fast.md ===
# How to Create a Chatbot with Gradio

Tags: LLM, CHATBOT, NLP

## Introduction

Chatbots are a popular application of large language models (LLMs). Using Gradio, you can easily build a chat application and share that with your users, or try it yourself using an intuitive UI.

This tutorial uses `gr.ChatInterface()`, which is a high-level abstraction that allows you to create your chatbot UI fast, often with a _few lines of Python_. It can be easily adapted to support multimodal chatbots, or chatbots that require further customization.

**Prerequisites**: please make sure you are using the latest version of Gradio:

```bash
$ pip install --upgrade gradio
```

## Note for OpenAI-API compatible endpoints

If you have a chat server serving an OpenAI-API compatible endpoint (such as Ollama), you can spin up a ChatInterface in a single line of Python. First, also run `pip install openai`. Then, with your own URL, model, and optional token:

```python
import gradio as gr

gr.load_chat("http://localhost:11434/v1/", model="llama3.2", token="***").launch()
```

Read about `gr.load_chat` in [the docs](https://www.gradio.app/docs/gradio/load_chat). If you have your own model, keep reading to see how to create an application around any chat model in Python!

## Defining a chat function

To create a chat application with `gr.ChatInterface()`, the first thing you should do is define your **chat function**. In the simplest case, your chat function should accept two arguments: `message` and `history` (the arguments can be named anything, but must be in this order).

- `message`: a `str` representing the user's most recent message.
- `history`: a list of openai-style dictionaries with `role` and `content` keys, representing the previous conversation history. May also include additional keys representing message metadata.

For example, the `history` could look like this:

```python
[
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "Paris"}
]
```

while the next `message` would be:

```py
"And what is its largest city?"
```

Your chat function simply needs to return: 

* a `str` value, which is the chatbot's response based on the chat `history` and most recent `message`, for example, in this case:

```
Paris is also the largest city.
```

Let's take a look at a few example chat functions:

**Example: a chatbot that randomly responds with yes or no**

Let's write a chat function that responds `Yes` or `No` randomly.

Here's our chat function:

```python
import random

def random_response(message, history):
    return random.choice(["Yes", "No"])
```

Now, we can plug this into `gr.ChatInterface()` and call the `.launch()` method to create the web interface:

```python
import gradio as gr

gr.ChatInterface(
    fn=random_response, 
    type="messages"
).launch()
```

Tip: Always set type="messages" in gr.ChatInterface. The default value (type="tuples") is deprecated and will be removed in a future version of Gradio.

That's it! Here's our running demo, try it out:

$demo_chatinterface_random_response

**Example: a chatbot that alternates between agreeing and disagreeing**

Of course, the previous example was very simplistic, it didn't take user input or the previous history into account! Here's another simple example showing how to incorporate a user's input as well as the history.

```python
import gradio as gr

def alternatingly_agree(message, history):
    if len([h for h in history if h['role'] == "assistant"]) % 2 == 0:
        return f"Yes, I do think that: {message}"
    else:
        return "I don't think so"

gr.ChatInterface(
    fn=alternatingly_agree, 
    type="messages"
).launch()
```

We'll look at more realistic examples of chat functions in our next Guide, which shows [examples of using `gr.ChatInterface` with popular LLMs](../guides/chatinterface-examples). 

## Streaming chatbots

In your chat function, you can use `yield` to generate a sequence of partial responses, each replacing the previous ones. This way, you'll end up with a streaming chatbot. It's that simple!

```python
import time
import gradio as gr

def slow_echo(message, history):
    for i in range(len(message)):
        time.sleep(0.3)
        yield "You typed: " + message[: i+1]

gr.ChatInterface(
    fn=slow_echo, 
    type="messages"
).launch()
```

While the response is streaming, the "Submit" button turns into a "Stop" button that can be used to stop the generator function.

Tip: Even though you are yielding the latest message at each iteration, Gradio only sends the "diff" of each message from the server to the frontend, which reduces latency and data consumption over your network.

## Customizing the Chat UI

If you're familiar with Gradio's `gr.Interface` class, the `gr.ChatInterface` includes many of the same arguments that you can use to customize the look and feel of your Chatbot. For example, you can:

- add a title and description above your chatbot using `title` and `description` arguments.
- add a theme or custom css using `theme` and `css` arguments respectively.
- add `examples` and even enable `cache_examples`, which make your Chatbot easier for users to try it out.
- customize the chatbot (e.g. to change the height or add a placeholder) or textbox (e.g. to add a max number of characters or add a placeholder).

**Adding examples**

You can add preset examples to your `gr.ChatInterface` with the `examples` parameter, which takes a list of string examples. Any examples will appear as "buttons" within the Chatbot before any messages are sent. If you'd like to include images or other files as part of your examples, you can do so by using this dictionary format for each example instead of a string: `{"text": "What's in this image?", "files": ["cheetah.jpg"]}`. Each file will be a separate message that is added to your Chatbot history.

You can change the displayed text for each example by using the `example_labels` argument. You can add icons to each example as well using the `example_icons` argument. Both of these arguments take a list of strings, which should be the same length as the `examples` list.

If you'd like to cache the examples so that they are pre-computed and the results appear instantly, set `cache_examples=True`.

**Customizing the chatbot or textbox component**

If you want to customize the `gr.Chatbot` or `gr.Textbox` that compose the `ChatInterface`, then you can pass in your own chatbot or textbox components. Here's an example of how we to apply the parameters we've discussed in this section:

```python
import gradio as gr

def yes_man(message, history):
    if message.endswith("?"):
        return "Yes"
    else:
        return "Ask me anything!"

gr.ChatInterface(
    yes_man,
    type="messages",
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder="Ask me a yes or no question", container=False, scale=7),
    title="Yes Man",
    description="Ask Yes Man any question",
    theme="ocean",
    examples=["Hello", "Am I cool?", "Are tomatoes vegetables?"],
    cache_examples=True,
).launch()
```

Here's another example that adds a "placeholder" for your chat interface, which appears before the user has started chatting. The `placeholder` argument of `gr.Chatbot` accepts Markdown or HTML:

```python
gr.ChatInterface(
    yes_man,
    type="messages",
    chatbot=gr.Chatbot(placeholder="<strong>Your Personal Yes-Man</strong><br>Ask Me Anything"),
...
```

The placeholder appears vertically and horizontally centered in the chatbot.

## Multimodal Chat Interface

You may want to add multimodal capabilities to your chat interface. For example, you may want users to be able to upload images or files to your chatbot and ask questions about them. You can make your chatbot "multimodal" by passing in a single parameter (`multimodal=True`) to the `gr.ChatInterface` class.

When `multimodal=True`, the signature of your chat function changes slightly: the first parameter of your function (what we referred to as `message` above) should accept a dictionary consisting of the submitted text and uploaded files that looks like this: 

```py
{
    "text": "user input", 
    "files": [
        "updated_file_1_path.ext",
        "updated_file_2_path.ext", 
        ...
    ]
}
```

This second parameter of your chat function, `history`, will be in the same openai-style dictionary format as before. However, if the history contains uploaded files, the `content` key for a file will be not a string, but rather a single-element tuple consisting of the filepath. Each file will be a separate message in the history. So after uploading two files and asking a question, your history might look like this:

```python
[
    {"role": "user", "content": ("cat1.png")},
    {"role": "user", "content": ("cat2.png")},
    {"role": "user", "content": "What's the difference between these two images?"},
]
```

The return type of your chat function does *not change* when setting `multimodal=True` (i.e. in the simplest case, you should still return a string value). We discuss more complex cases, e.g. returning files [below](#returning-complex-responses).

If you are customizing a multimodal chat interface, you should pass in an instance of `gr.MultimodalTextbox` to the `textbox` parameter. You can customize the `MultimodalTextbox` further by passing in the `sources` parameter, which is a list of sources to enable. Here's an example that illustrates how to set up and customize and multimodal chat interface:
 

```python
import gradio as gr

def count_images(message, history):
    num_images = len(message["files"])
    total_images = 0
    for message in history:
        if isinstance(message["content"], tuple):
            total_images += 1
    return f"You just uploaded {num_images} images, total uploaded: {total_images+num_images}"

demo = gr.ChatInterface(
    fn=count_images, 
    type="messages", 
    examples=[
        {"text": "No files", "files": []}
    ], 
    multimodal=True,
    textbox=gr.MultimodalTextbox(file_count="multiple", file_types=["image"], sources=["upload", "microphone"])
)

demo.launch()
```

## Additional Inputs

You may want to add additional inputs to your chat function and expose them to your users through the chat UI. For example, you could add a textbox for a system prompt, or a slider that sets the number of tokens in the chatbot's response. The `gr.ChatInterface` class supports an `additional_inputs` parameter which can be used to add additional input components.

The `additional_inputs` parameters accepts a component or a list of components. You can pass the component instances directly, or use their string shortcuts (e.g. `"textbox"` instead of `gr.Textbox()`). If you pass in component instances, and they have _not_ already been rendered, then the components will appear underneath the chatbot within a `gr.Accordion()`. 

Here's a complete example:

$code_chatinterface_system_prompt

If the components you pass into the `additional_inputs` have already been rendered in a parent `gr.Blocks()`, then they will _not_ be re-rendered in the accordion. This provides flexibility in deciding where to lay out the input components. In the example below, we position the `gr.Textbox()` on top of the Chatbot UI, while keeping the slider underneath.

```python
import gradio as gr
import time

def echo(message, history, system_prompt, tokens):
    response = f"System prompt: {system_prompt}\n Message: {message}."
    for i in range(min(len(response), int(tokens))):
        time.sleep(0.05)
        yield response[: i+1]

with gr.Blocks() as demo:
    system_prompt = gr.Textbox("You are helpful AI.", label="System Prompt")
    slider = gr.Slider(10, 100, render=False)

    gr.ChatInterface(
        echo, additional_inputs=[system_prompt, slider], type="messages"
    )

demo.launch()
```

**Examples with additional inputs**

You can also add example values for your additional inputs. Pass in a list of lists to the `examples` parameter, where each inner list represents one sample, and each inner list should be `1 + len(additional_inputs)` long. The first element in the inner list should be the example value for the chat message, and each subsequent element should be an example value for one of the additional inputs, in order. When additional inputs are provided, examples are rendered in a table underneath the chat interface.

If you need to create something even more custom, then its best to construct the chatbot UI using the low-level `gr.Blocks()` API. We have [a dedicated guide for that here](/guides/creating-a-custom-chatbot-with-blocks).

## Additional Outputs

In the same way that you can accept additional inputs into your chat function, you can also return additional outputs. Simply pass in a list of components to the `additional_outputs` parameter in `gr.ChatInterface` and return additional values for each component from your chat function. Here's an example that extracts code and outputs it into a separate `gr.Code` component:

$code_chatinterface_artifacts

**Note:** unlike the case of additional inputs, the components passed in `additional_outputs` must be already defined in your `gr.Blocks` context -- they are not rendered automatically. If you need to render them after your `gr.ChatInterface`, you can set `render=False` when they are first defined and then `.render()` them in the appropriate section of your `gr.Blocks()` as we do in the example above.

## Returning Complex Responses

We mentioned earlier that in the simplest case, your chat function should return a `str` response, which will be rendered as Markdown in the chatbot. However, you can also return more complex responses as we discuss below:


**Returning files or Gradio components**

Currently, the following Gradio components can be displayed inside the chat interface:
* `gr.Image`
* `gr.Plot`
* `gr.Audio`
* `gr.HTML`
* `gr.Video`
* `gr.Gallery`
* `gr.File`

Simply return one of these components from your function to use it with `gr.ChatInterface`. Here's an example that returns an audio file:

```py
import gradio as gr

def music(message, history):
    if message.strip():
        return gr.Audio("https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav")
    else:
        return "Please provide the name of an artist"

gr.ChatInterface(
    music,
    type="messages",
    textbox=gr.Textbox(placeholder="Which artist's music do you want to listen to?", scale=7),
).launch()
```

Similarly, you could return image files with `gr.Image`, video files with `gr.Video`, or arbitrary files with the `gr.File` component.

**Returning Multiple Messages**

You can return multiple assistant messages from your chat function simply by returning a `list` of messages, each of which is a valid chat type. This lets you, for example, send a message along with files, as in the following example:

$code_chatinterface_echo_multimodal


**Displaying intermediate thoughts or tool usage**

The `gr.ChatInterface` class supports displaying intermediate thoughts or tool usage direct in the chatbot.

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/nested-thought.png)

 To do this, you will need to return a `gr.ChatMessage` object from your chat function. Here is the schema of the `gr.ChatMessage` data class as well as two internal typed dictionaries:
 
 ```py
@dataclass
class ChatMessage:
    content: str | Component
    metadata: MetadataDict = None
    options: list[OptionDict] = None

class MetadataDict(TypedDict):
    title: NotRequired[str]
    id: NotRequired[int | str]
    parent_id: NotRequired[int | str]
    log: NotRequired[str]
    duration: NotRequired[float]
    status: NotRequired[Literal["pending", "done"]]

class OptionDict(TypedDict):
    label: NotRequired[str]
    value: str
 ```
 
As you can see, the `gr.ChatMessage` dataclass is similar to the openai-style message format, e.g. it has a "content" key that refers to the chat message content. But it also includes a "metadata" key whose value is a dictionary. If this dictionary includes a "title" key, the resulting message is displayed as an intermediate thought with the title being displayed on top of the thought. Here's an example showing the usage:

$code_chatinterface_thoughts

You can even show nested thoughts, which is useful for agent demos in which one tool may call other tools. To display nested thoughts, include "id" and "parent_id" keys in the "metadata" dictionary. Read our [dedicated guide on displaying intermediate thoughts and tool usage](/guides/agents-and-tool-usage) for more realistic examples.

**Providing preset responses**

When returning an assistant message, you may want to provide preset options that a user can choose in response. To do this, again, you will again return a `gr.ChatMessage` instance from your chat function. This time, make sure to set the `options` key specifying the preset responses.

As shown in the schema for `gr.ChatMessage` above, the value corresponding to the `options` key should be a list of dictionaries, each with a `value` (a string that is the value that should be sent to the chat function when this response is clicked) and an optional `label` (if provided, is the text displayed as the preset response instead of the `value`). 

This example illustrates how to use preset responses:

$code_chatinterface_options

## Modifying the Chatbot Value Directly

You may wish to modify the value of the chatbot with your own events, other than those prebuilt in the `gr.ChatInterface`. For example, you could create a dropdown that prefills the chat history with certain conversations or add a separate button to clear the conversation history. The `gr.ChatInterface` supports these events, but you need to use the `gr.ChatInterface.chatbot_value` as the input or output component in such events. In this example, we use a `gr.Radio` component to prefill the the chatbot with certain conversations:

$code_chatinterface_prefill

## Using Your Chatbot via API

Once you've built your Gradio chat interface and are hosting it on [Hugging Face Spaces](https://hf.space) or somewhere else, then you can query it with a simple API at the `/chat` endpoint. The endpoint just expects the user's message and will return the response, internally keeping track of the message history.

![](https://github.com/gradio-app/gradio/assets/1778297/7b10d6db-6476-4e2e-bebd-ecda802c3b8f)

To use the endpoint, you should use either the [Gradio Python Client](/guides/getting-started-with-the-python-client) or the [Gradio JS client](/guides/getting-started-with-the-js-client). Or, you can deploy your Chat Interface to other platforms, such as a:

* Discord bot [[tutorial]](../guides/creating-a-discord-bot-from-a-gradio-app)
* Slack bot [[tutorial]](../guides/creating-a-slack-bot-from-a-gradio-app)
* Website widget [[tutorial]](../guides/creating-a-website-widget-from-a-gradio-chatbot)

## Chat History

You can enable persistent chat history for your ChatInterface, allowing users to maintain multiple conversations and easily switch between them. When enabled, conversations are stored locally and privately in the user's browser using local storage. So if you deploy a ChatInterface e.g. on [Hugging Face Spaces](https://hf.space), each user will have their own separate chat history that won't interfere with other users' conversations. This means multiple users can interact with the same ChatInterface simultaneously while maintaining their own private conversation histories.

To enable this feature, simply set `gr.ChatInterface(save_history=True)` (as shown in the example in the next section). Users will then see their previous conversations in a side panel and can continue any previous chat or start a new one.

## Collecting User Feedback

To gather feedback on your chat model, set `gr.ChatInterface(flagging_mode="manual")` and users will be able to thumbs-up or thumbs-down assistant responses. Each flagged response, along with the entire chat history, will get saved in a CSV file in the app working directory (this can be configured via the `flagging_dir` parameter). 

You can also change the feedback options via `flagging_options` parameter. The default options are "Like" and "Dislike", which appear as the thumbs-up and thumbs-down icons. Any other options appear under a dedicated flag icon. This example shows a ChatInterface that has both chat history (mentioned in the previous section) and user feedback enabled:

$code_chatinterface_streaming_echo

Note that in this example, we set several flagging options: "Like", "Spam", "Inappropriate", "Other". Because the case-sensitive string "Like" is one of the flagging options, the user will see a thumbs-up icon next to each assistant message. The three other flagging options will appear in a dropdown under the flag icon.

## What's Next?

Now that you've learned about the `gr.ChatInterface` class and how it can be used to create chatbot UIs quickly, we recommend reading one of the following:

* [Our next Guide](../guides/chatinterface-examples) shows examples of how to use `gr.ChatInterface` with popular LLM libraries.
* If you'd like to build very custom chat applications from scratch, you can build them using the low-level Blocks API, as [discussed in this Guide](../guides/creating-a-custom-chatbot-with-blocks).
* Once you've deployed your Gradio Chat Interface, its easy to use in other applications because of the built-in API. Here's a tutorial on [how to deploy a Gradio chat interface as a Discord bot](../guides/creating-a-discord-bot-from-a-gradio-app).




=== File: guides/05_chatbots/02_chatinterface-examples.md ===
# Using Popular LLM libraries and APIs

Tags: LLM, CHATBOT, API

In this Guide, we go through several examples of how to use `gr.ChatInterface` with popular LLM libraries and API providers.

We will cover the following libraries and API providers:

* [Llama Index](#llama-index)
* [LangChain](#lang-chain)
* [OpenAI](#open-ai)
* [Hugging Face `transformers`](#hugging-face-transformers)
* [SambaNova](#samba-nova)
* [Hyperbolic](#hyperbolic)
* [Anthropic's Claude](#anthropics-claude)

For many LLM libraries and providers, there exist community-maintained integration libraries that make it even easier to spin up Gradio apps. We reference these libraries in the appropriate sections below.

## Llama Index

Let's start by using `llama-index` on top of `openai` to build a RAG chatbot on any text or PDF files that you can demo and share in less than 30 lines of code. You'll need to have an OpenAI key for this example (keep reading for the free, open-source equivalent!)

$code_llm_llamaindex

## LangChain

Here's an example using `langchain` on top of `openai` to build a general-purpose chatbot. As before, you'll need to have an OpenAI key for this example.

$code_llm_langchain

Tip: For quick prototyping, the community-maintained <a href='https://github.com/AK391/langchain-gradio'>langchain-gradio repo</a>  makes it even easier to build chatbots on top of LangChain.

## OpenAI

Of course, we could also use the `openai` library directy. Here a similar example to the LangChain , but this time with streaming as well:

Tip: For quick prototyping, the  <a href='https://github.com/gradio-app/openai-gradio'>openai-gradio library</a> makes it even easier to build chatbots on top of OpenAI models.


## Hugging Face `transformers`

Of course, in many cases you want to run a chatbot locally. Here's the equivalent example using the SmolLM2-135M-Instruct model using the Hugging Face `transformers` library.

$code_llm_hf_transformers

## SambaNova

The SambaNova Cloud API provides access to full-precision open-source models, such as the Llama family. Here's an example of how to build a Gradio app around the SambaNova API

$code_llm_sambanova

Tip: For quick prototyping, the  <a href='https://github.com/gradio-app/sambanova-gradio'>sambanova-gradio library</a> makes it even easier to build chatbots on top of SambaNova models.

## Hyperbolic

The Hyperbolic AI API provides access to many open-source models, such as the Llama family. Here's an example of how to build a Gradio app around the Hyperbolic

$code_llm_hyperbolic

Tip: For quick prototyping, the  <a href='https://github.com/HyperbolicLabs/hyperbolic-gradio'>hyperbolic-gradio library</a> makes it even easier to build chatbots on top of Hyperbolic models.


## Anthropic's Claude 

Anthropic's Claude model can also be used via API. Here's a simple 20 questions-style game built on top of the Anthropic API:

$code_llm_claude




=== File: guides/05_chatbots/03_agents-and-tool-usage.md ===
# Building a UI for an LLM Agent

Tags: LLM, AGENTS, CHAT

The Gradio Chatbot can natively display intermediate thoughts and tool usage in a collapsible accordion next to a chat message. This makes it perfect for creating UIs for LLM agents and chain-of-thought (CoT) or reasoning demos. This guide will show you how to display thoughts and tool usage with `gr.Chatbot` and `gr.ChatInterface`.

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/nested-thoughts.png)

## The `ChatMessage` dataclass

Each message in Gradio's chatbot is a dataclass of type `ChatMessage` (this is assuming that chatbot's `type="message"`, which is strongly recommended). The schema of `ChatMessage` is as follows:

 ```py
@dataclass
class ChatMessage:
    content: str | Component
    role: Literal["user", "assistant"]
    metadata: MetadataDict = None
    options: list[OptionDict] = None

class MetadataDict(TypedDict):
    title: NotRequired[str]
    id: NotRequired[int | str]
    parent_id: NotRequired[int | str]
    log: NotRequired[str]
    duration: NotRequired[float]
    status: NotRequired[Literal["pending", "done"]]

class OptionDict(TypedDict):
    label: NotRequired[str]
    value: str
 ```


For our purposes, the most important key is the `metadata` key, which accepts a dictionary. If this dictionary includes a `title` for the message, it will be displayed in a collapsible accordion representing a thought. It's that simple! Take a look at this example:


```python
import gradio as gr

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        type="messages",
        value=[
            gr.ChatMessage(
                role="user", 
                content="What is the weather in San Francisco?"
            ),
            gr.ChatMessage(
                role="assistant", 
                content="I need to use the weather API tool?",
                metadata={"title":  "🧠 Thinking"}
        ]
    )

demo.launch()
```



In addition to `title`, the dictionary provided to `metadata` can take several optional keys:

* `log`: an optional string value to be displayed in a subdued font next to the thought title.
* `duration`: an optional numeric value representing the duration of the thought/tool usage, in seconds. Displayed in a subdued font next inside parentheses next to the thought title.
* `status`: if set to `"pending"`, a spinner appears next to the thought title and the accordion is initialized open.  If `status` is `"done"`, the thought accordion is initialized closed. If `status` is not provided, the thought accordion is initialized open and no spinner is displayed.
* `id` and `parent_id`: if these are provided, they can be used to nest thoughts inside other thoughts.

Below, we show several complete examples of using `gr.Chatbot` and `gr.ChatInterface` to display tool use or thinking UIs.

## Building with Agents

### A real example using transformers.agents

We'll create a Gradio application simple agent that has access to a text-to-image tool.

Tip: Make sure you read the [smolagents documentation](https://huggingface.co/docs/smolagents/index) first

We'll start by importing the necessary classes from transformers and gradio. 

```python
import gradio as gr
from gradio import ChatMessage
from transformers import Tool, ReactCodeAgent  # type: ignore
from transformers.agents import stream_to_gradio, HfApiEngine  # type: ignore

# Import tool from Hub
image_generation_tool = Tool.from_space(
    space_id="black-forest-labs/FLUX.1-schnell",
    name="image_generator",
    description="Generates an image following your prompt. Returns a PIL Image.",
    api_name="/infer",
)

llm_engine = HfApiEngine("Qwen/Qwen2.5-Coder-32B-Instruct")
# Initialize the agent with both tools and engine
agent = ReactCodeAgent(tools=[image_generation_tool], llm_engine=llm_engine)
```

Then we'll build the UI:

```python
def interact_with_agent(prompt, history):
    messages = []
    yield messages
    for msg in stream_to_gradio(agent, prompt):
        messages.append(asdict(msg))
        yield messages
    yield messages


demo = gr.ChatInterface(
    interact_with_agent,
    chatbot= gr.Chatbot(
        label="Agent",
        type="messages",
        avatar_images=(
            None,
            "https://em-content.zobj.net/source/twitter/53/robot-face_1f916.png",
        ),
    ),
    examples=[
        ["Generate an image of an astronaut riding an alligator"],
        ["I am writing a children's book for my daughter. Can you help me with some illustrations?"],
    ],
    type="messages",
)
```

You can see the full demo code [here](https://huggingface.co/spaces/gradio/agent_chatbot/blob/main/app.py).


![transformers_agent_code](https://github.com/freddyaboulton/freddyboulton/assets/41651716/c8d21336-e0e6-4878-88ea-e6fcfef3552d)


### A real example using langchain agents

We'll create a UI for langchain agent that has access to a search engine.

We'll begin with imports and setting up the langchain agent. Note that you'll need an .env file with the following environment variables set - 

```
SERPAPI_API_KEY=
HF_TOKEN=
OPENAI_API_KEY=
```

```python
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent, load_tools
from langchain_openai import ChatOpenAI
from gradio import ChatMessage
import gradio as gr

from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(temperature=0, streaming=True)

tools = load_tools(["serpapi"])

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(
    model.with_config({"tags": ["agent_llm"]}), tools, prompt
)
agent_executor = AgentExecutor(agent=agent, tools=tools).with_config(
    {"run_name": "Agent"}
)
```

Then we'll create the Gradio UI

```python
async def interact_with_langchain_agent(prompt, messages):
    messages.append(ChatMessage(role="user", content=prompt))
    yield messages
    async for chunk in agent_executor.astream(
        {"input": prompt}
    ):
        if "steps" in chunk:
            for step in chunk["steps"]:
                messages.append(ChatMessage(role="assistant", content=step.action.log,
                                  metadata={"title": f"🛠️ Used tool {step.action.tool}"}))
                yield messages
        if "output" in chunk:
            messages.append(ChatMessage(role="assistant", content=chunk["output"]))
            yield messages


with gr.Blocks() as demo:
    gr.Markdown("# Chat with a LangChain Agent 🦜⛓️ and see its thoughts 💭")
    chatbot = gr.Chatbot(
        type="messages",
        label="Agent",
        avatar_images=(
            None,
            "https://em-content.zobj.net/source/twitter/141/parrot_1f99c.png",
        ),
    )
    input = gr.Textbox(lines=1, label="Chat Message")
    input.submit(interact_with_langchain_agent, [input_2, chatbot_2], [chatbot_2])

demo.launch()
```

![langchain_agent_code](https://github.com/freddyaboulton/freddyboulton/assets/41651716/762283e5-3937-47e5-89e0-79657279ea67)

That's it! See our finished langchain demo [here](https://huggingface.co/spaces/gradio/langchain-agent).


## Building with Visibly Thinking LLMs


The Gradio Chatbot can natively display intermediate thoughts of a _thinking_ LLM. This makes it perfect for creating UIs that show how an AI model "thinks" while generating responses. Below guide will show you how to build a chatbot that displays Gemini AI's thought process in real-time.


### A real example using Gemini 2.0 Flash Thinking API

Let's create a complete chatbot that shows its thoughts and responses in real-time. We'll use Google's Gemini API for accessing Gemini 2.0 Flash Thinking LLM and Gradio for the UI.

We'll begin with imports and setting up the gemini client. Note that you'll need to [acquire a Google Gemini API key](https://aistudio.google.com/apikey) first -

```python
import gradio as gr
from gradio import ChatMessage
from typing import Iterator
import google.generativeai as genai

genai.configure(api_key="your-gemini-api-key")
model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-1219")
```

First, let's set up our streaming function that handles the model's output:

```python
def stream_gemini_response(user_message: str, messages: list) -> Iterator[list]:
    """
    Streams both thoughts and responses from the Gemini model.
    """
    # Initialize response from Gemini
    response = model.generate_content(user_message, stream=True)
    
    # Initialize buffers
    thought_buffer = ""
    response_buffer = ""
    thinking_complete = False
    
    # Add initial thinking message
    messages.append(
        ChatMessage(
            role="assistant",
            content="",
            metadata={"title": "⏳Thinking: *The thoughts produced by the Gemini2.0 Flash model are experimental"}
        )
    )
    
    for chunk in response:
        parts = chunk.candidates[0].content.parts
        current_chunk = parts[0].text
        
        if len(parts) == 2 and not thinking_complete:
            # Complete thought and start response
            thought_buffer += current_chunk
            messages[-1] = ChatMessage(
                role="assistant",
                content=thought_buffer,
                metadata={"title": "⏳Thinking: *The thoughts produced by the Gemini2.0 Flash model are experimental"}
            )
            
            # Add response message
            messages.append(
                ChatMessage(
                    role="assistant",
                    content=parts[1].text
                )
            )
            thinking_complete = True
            
        elif thinking_complete:
            # Continue streaming response
            response_buffer += current_chunk
            messages[-1] = ChatMessage(
                role="assistant",
                content=response_buffer
            )
            
        else:
            # Continue streaming thoughts
            thought_buffer += current_chunk
            messages[-1] = ChatMessage(
                role="assistant",
                content=thought_buffer,
                metadata={"title": "⏳Thinking: *The thoughts produced by the Gemini2.0 Flash model are experimental"}
            )
        
        yield messages
```

Then, let's create the Gradio interface:

```python
with gr.Blocks() as demo:
    gr.Markdown("# Chat with Gemini 2.0 Flash and See its Thoughts 💭")
    
    chatbot = gr.Chatbot(
        type="messages",
        label="Gemini2.0 'Thinking' Chatbot",
        render_markdown=True,
    )
    
    input_box = gr.Textbox(
        lines=1,
        label="Chat Message",
        placeholder="Type your message here and press Enter..."
    )
    
    # Set up event handlers
    msg_store = gr.State("")  # Store for preserving user message
    
    input_box.submit(
        lambda msg: (msg, msg, ""),  # Store message and clear input
        inputs=[input_box],
        outputs=[msg_store, input_box, input_box],
        queue=False
    ).then(
        user_message,  # Add user message to chat
        inputs=[msg_store, chatbot],
        outputs=[input_box, chatbot],
        queue=False
    ).then(
        stream_gemini_response,  # Generate and stream response
        inputs=[msg_store, chatbot],
        outputs=chatbot
    )

demo.launch()
```

This creates a chatbot that:

- Displays the model's thoughts in a collapsible section
- Streams the thoughts and final response in real-time
- Maintains a clean chat history

 That's it! You now have a chatbot that not only responds to users but also shows its thinking process, creating a more transparent and engaging interaction. See our finished Gemini 2.0 Flash Thinking demo [here](https://huggingface.co/spaces/ysharma/Gemini2-Flash-Thinking).


 ## Building with Citations 

The Gradio Chatbot can display citations from LLM responses, making it perfect for creating UIs that show source documentation and references. This guide will show you how to build a chatbot that displays Claude's citations in real-time.

### A real example using Anthropic's Citations API
Let's create a complete chatbot that shows both responses and their supporting citations. We'll use Anthropic's Claude API with citations enabled and Gradio for the UI.

We'll begin with imports and setting up the Anthropic client. Note that you'll need an `ANTHROPIC_API_KEY` environment variable set:

```python
import gradio as gr
import anthropic
import base64
from typing import List, Dict, Any

client = anthropic.Anthropic()
```

First, let's set up our message formatting functions that handle document preparation:

```python
def encode_pdf_to_base64(file_obj) -> str:
    """Convert uploaded PDF file to base64 string."""
    if file_obj is None:
        return None
    with open(file_obj.name, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def format_message_history(
    history: list, 
    enable_citations: bool,
    doc_type: str,
    text_input: str,
    pdf_file: str
) -> List[Dict]:
    """Convert Gradio chat history to Anthropic message format."""
    formatted_messages = []
    
    # Add previous messages
    for msg in history[:-1]:
        if msg["role"] == "user":
            formatted_messages.append({"role": "user", "content": msg["content"]})
    
    # Prepare the latest message with document
    latest_message = {"role": "user", "content": []}
    
    if enable_citations:
        if doc_type == "plain_text":
            latest_message["content"].append({
                "type": "document",
                "source": {
                    "type": "text",
                    "media_type": "text/plain",
                    "data": text_input.strip()
                },
                "title": "Text Document",
                "citations": {"enabled": True}
            })
        elif doc_type == "pdf" and pdf_file:
            pdf_data = encode_pdf_to_base64(pdf_file)
            if pdf_data:
                latest_message["content"].append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    },
                    "title": pdf_file.name,
                    "citations": {"enabled": True}
                })
    
    # Add the user's question
    latest_message["content"].append({"type": "text", "text": history[-1]["content"]})
    
    formatted_messages.append(latest_message)
    return formatted_messages
```

Then, let's create our bot response handler that processes citations:

```python
def bot_response(
    history: list,
    enable_citations: bool,
    doc_type: str,
    text_input: str,
    pdf_file: str
) -> List[Dict[str, Any]]:
    try:
        messages = format_message_history(history, enable_citations, doc_type, text_input, pdf_file)
        response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=1024, messages=messages)
        
        # Initialize main response and citations
        main_response = ""
        citations = []
        
        # Process each content block
        for block in response.content:
            if block.type == "text":
                main_response += block.text
                if enable_citations and hasattr(block, 'citations') and block.citations:
                    for citation in block.citations:
                        if citation.cited_text not in citations:
                            citations.append(citation.cited_text)
        
        # Add main response
        history.append({"role": "assistant", "content": main_response})
        
        # Add citations in a collapsible section
        if enable_citations and citations:
            history.append({
                "role": "assistant",
                "content": "\n".join([f"• {cite}" for cite in citations]),
                "metadata": {"title": "📚 Citations"}
            })
        
        return history
            
    except Exception as e:
        history.append({
            "role": "assistant",
            "content": "I apologize, but I encountered an error while processing your request."
        })
        return history
```

Finally, let's create the Gradio interface:

```python
with gr.Blocks() as demo:
    gr.Markdown("# Chat with Citations")
    
    with gr.Row(scale=1):
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(type="messages", bubble_full_width=False, show_label=False, scale=1)
            msg = gr.Textbox(placeholder="Enter your message here...", show_label=False, container=False)
            
        with gr.Column(scale=1):
            enable_citations = gr.Checkbox(label="Enable Citations", value=True, info="Toggle citation functionality" )
            doc_type_radio = gr.Radio( choices=["plain_text", "pdf"], value="plain_text", label="Document Type", info="Choose the type of document to use")
            text_input = gr.Textbox(label="Document Content", lines=10, info="Enter the text you want to reference")
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"], file_count="single", visible=False)
    
    # Handle message submission
    msg.submit(
        user_message,
        [msg, chatbot, enable_citations, doc_type_radio, text_input, pdf_input],
        [msg, chatbot]
    ).then(
        bot_response,
        [chatbot, enable_citations, doc_type_radio, text_input, pdf_input],
        chatbot
    )

demo.launch()
```

This creates a chatbot that:
- Supports both plain text and PDF documents for Claude to cite from 
- Displays Citations in collapsible sections using our `metadata` feature
- Shows source quotes directly from the given documents

The citations feature works particularly well with the Gradio Chatbot's `metadata` support, allowing us to create collapsible sections that keep the chat interface clean while still providing easy access to source documentation.

That's it! You now have a chatbot that not only responds to users but also shows its sources, creating a more transparent and trustworthy interaction. See our finished Citations demo [here](https://huggingface.co/spaces/ysharma/anthropic-citations-with-gradio-metadata-key).



=== File: guides/05_chatbots/04_creating-a-custom-chatbot-with-blocks.md ===
# How to Create a Custom Chatbot with Gradio Blocks

Tags: NLP, TEXT, CHAT
Related spaces: https://huggingface.co/spaces/gradio/chatbot_streaming, https://huggingface.co/spaces/project-baize/Baize-7B,

## Introduction

**Important Note**: if you are getting started, we recommend using the `gr.ChatInterface` to create chatbots -- its a high-level abstraction that makes it possible to create beautiful chatbot applications fast, often with a single line of code. [Read more about it here](/guides/creating-a-chatbot-fast).

This tutorial will show how to make chatbot UIs from scratch with Gradio's low-level Blocks API. This will give you full control over your Chatbot UI. You'll start by first creating a a simple chatbot to display text, a second one to stream text responses, and finally a chatbot that can handle media files as well. The chatbot interface that we create will look something like this:

$demo_chatbot_streaming

**Prerequisite**: We'll be using the `gradio.Blocks` class to build our Chatbot demo.
You can [read the Guide to Blocks first](https://gradio.app/blocks-and-event-listeners) if you are not already familiar with it. Also please make sure you are using the **latest version** version of Gradio: `pip install --upgrade gradio`.

## A Simple Chatbot Demo

Let's start with recreating the simple demo above. As you may have noticed, our bot simply randomly responds "How are you?", "Today is a great day", or "I'm very hungry" to any input. Here's the code to create this with Gradio:

$code_chatbot_simple

There are three Gradio components here:

- A `Chatbot`, whose value stores the entire history of the conversation, as a list of response pairs between the user and bot.
- A `Textbox` where the user can type their message, and then hit enter/submit to trigger the chatbot response
- A `ClearButton` button to clear the Textbox and entire Chatbot history

We have a single function, `respond()`, which takes in the entire history of the chatbot, appends a random message, waits 1 second, and then returns the updated chat history. The `respond()` function also clears the textbox when it returns.

Of course, in practice, you would replace `respond()` with your own more complex function, which might call a pretrained model or an API, to generate a response.

$demo_chatbot_simple

Tip: For better type hinting and auto-completion in your IDE, you can use the `gr.ChatMessage` dataclass:

```python
from gradio import ChatMessage

def chat_function(message, history):
    history.append(ChatMessage(role="user", content=message))
    history.append(ChatMessage(role="assistant", content="Hello, how can I help you?"))
    return history
```

## Add Streaming to your Chatbot

There are several ways we can improve the user experience of the chatbot above. First, we can stream responses so the user doesn't have to wait as long for a message to be generated. Second, we can have the user message appear immediately in the chat history, while the chatbot's response is being generated. Here's the code to achieve that:

$code_chatbot_streaming

You'll notice that when a user submits their message, we now _chain_ two event events with `.then()`:

1. The first method `user()` updates the chatbot with the user message and clears the input field. Because we want this to happen instantly, we set `queue=False`, which would skip any queue had it been enabled. The chatbot's history is appended with `{"role": "user", "content": user_message}`.

2. The second method, `bot()` updates the chatbot history with the bot's response. Finally, we construct the message character by character and `yield` the intermediate outputs as they are being constructed. Gradio automatically turns any function with the `yield` keyword [into a streaming output interface](/guides/key-features/#iterative-outputs).


Of course, in practice, you would replace `bot()` with your own more complex function, which might call a pretrained model or an API, to generate a response.


## Adding Markdown, Images, Audio, or Videos

The `gr.Chatbot` component supports a subset of markdown including bold, italics, and code. For example, we could write a function that responds to a user's message, with a bold **That's cool!**, like this:

```py
def bot(history):
    response = {"role": "assistant", "content": "**That's cool!**"}
    history.append(response)
    return history
```

In addition, it can handle media files, such as images, audio, and video. You can use the `MultimodalTextbox` component to easily upload all types of media files to your chatbot. You can customize the `MultimodalTextbox` further by passing in the `sources` parameter, which is a list of sources to enable. To pass in a media file, we must pass in the file a dictionary with a `path` key pointing to a local file and an `alt_text` key. The `alt_text` is optional, so you can also just pass in a tuple with a single element `{"path": "filepath"}`, like this:

```python
def add_message(history, message):
    for x in message["files"]:
        history.append({"role": "user", "content": {"path": x}})
    if message["text"] is not None:
        history.append({"role": "user", "content": message["text"]})
    return history, gr.MultimodalTextbox(value=None, interactive=False, file_types=["image"], sources=["upload", "microphone"])
```

Putting this together, we can create a _multimodal_ chatbot with a multimodal textbox for a user to submit text and media files. The rest of the code looks pretty much the same as before:

$code_chatbot_multimodal
$demo_chatbot_multimodal

And you're done! That's all the code you need to build an interface for your chatbot model. Finally, we'll end our Guide with some links to Chatbots that are running on Spaces so that you can get an idea of what else is possible:

- [project-baize/Baize-7B](https://huggingface.co/spaces/project-baize/Baize-7B): A stylized chatbot that allows you to stop generation as well as regenerate responses.
- [MAGAer13/mPLUG-Owl](https://huggingface.co/spaces/MAGAer13/mPLUG-Owl): A multimodal chatbot that allows you to upvote and downvote responses.


=== File: guides/05_chatbots/05_chatbot-specific-events.md ===
# Chatbot-Specific Events

Tags: LLM, CHAT

Users expect modern chatbot UIs to let them easily interact with individual chat messages: for example, users might want to retry message generations, undo messages, or click on a like/dislike button to upvote or downvote a generated message.

Thankfully, the Gradio Chatbot exposes several events, such as `.retry`, `.undo`, `.like`, and `.clear`, to let you build this functionality into your application. As an application developer, you can attach functions to any of these event, allowing you to run arbitrary Python functions e.g. when a user interacts with a message.

In this demo, we'll build a UI that implements these events. You can see our finished demo deployed on Hugging Face spaces here:

$demo_chatbot_retry_undo_like

Tip: `gr.ChatInterface` automatically uses the `retry` and `.undo` events so it's best to start there in order get a fully working application quickly.


## The UI

First, we'll build the UI without handling these events and build from there. 
We'll use the Hugging Face InferenceClient in order to get started without setting up
any API keys.

This is what the first draft of our application looks like:

```python
from huggingface_hub import InferenceClient
import gradio as gr

client = InferenceClient()

def respond(
    prompt: str,
    history,
):
    if not history:
        history = [{"role": "system", "content": "You are a friendly chatbot"}]
    history.append({"role": "user", "content": prompt})

    yield history

    response = {"role": "assistant", "content": ""}
    for message in client.chat_completion(
        history,
        temperature=0.95,
        top_p=0.9,
        max_tokens=512,
        stream=True,
        model="HuggingFaceH4/zephyr-7b-beta"
    ):
        response["content"] += message.choices[0].delta.content or ""

        yield history + [response]


with gr.Blocks() as demo:
    gr.Markdown("# Chat with Hugging Face Zephyr 7b 🤗")
    chatbot = gr.Chatbot(
        label="Agent",
        type="messages",
        avatar_images=(
            None,
            "https://em-content.zobj.net/source/twitter/376/hugging-face_1f917.png",
        ),
    )
    prompt = gr.Textbox(max_lines=1, label="Chat Message")
    prompt.submit(respond, [prompt, chatbot], [chatbot])
    prompt.submit(lambda: "", None, [prompt])


if __name__ == "__main__":
    demo.launch()
```

## The Undo Event

Our undo event will populate the textbox with the previous user message and also remove all subsequent assistant responses.

In order to know the index of the last user message, we can pass `gr.UndoData` to our event handler function like so:

```python
def handle_undo(history, undo_data: gr.UndoData):
    return history[:undo_data.index], history[undo_data.index]['content']
```

We then pass this function to the `undo` event!

```python
    chatbot.undo(handle_undo, chatbot, [chatbot, prompt])
```

You'll notice that every bot response will now have an "undo icon" you can use to undo the response - 

![undo_event](https://github.com/user-attachments/assets/180b5302-bc4a-4c3e-903c-f14ec2adcaa6)

Tip: You can also access the content of the user message with `undo_data.value`

## The Retry Event

The retry event will work similarly. We'll use `gr.RetryData` to get the index of the previous user message and remove all the subsequent messages from the history. Then we'll use the `respond` function to generate a new response. We could also get the previous prompt via the `value` property of `gr.RetryData`.

```python
def handle_retry(history, retry_data: gr.RetryData):
    new_history = history[:retry_data.index]
    previous_prompt = history[retry_data.index]['content']
    yield from respond(previous_prompt, new_history)

...

chatbot.retry(handle_retry, chatbot, chatbot)
```

You'll see that the bot messages have a "retry" icon now -

![retry_event](https://github.com/user-attachments/assets/cec386a7-c4cd-4fb3-a2d7-78fd806ceac6)

Tip: The Hugging Face inference API caches responses, so in this demo, the retry button will not generate a new response.

## The Like Event

By now you should hopefully be seeing the pattern!
To let users like a message, we'll add a `.like` event to our chatbot.
We'll pass it a function that accepts a `gr.LikeData` object.
In this case, we'll just print the message that was either liked or disliked.

```python
def handle_like(data: gr.LikeData):
    if data.liked:
        print("You upvoted this response: ", data.value)
    else:
        print("You downvoted this response: ", data.value)

...

chatbot.like(vote, None, None)
```

## The Edit Event

Same idea with the edit listener! with `gr.Chatbot(editable=True)`, you can capture user edits. The `gr.EditData` object tells us the index of the message edited and the new text of the mssage. Below, we use this object to edit the history, and delete any subsequent messages. 

```python
def handle_edit(history, edit_data: gr.EditData):
    new_history = history[:edit_data.index]
    new_history[-1]['content'] = edit_data.value
    return new_history

...

chatbot.edit(handle_edit, chatbot, chatbot)
```

## The Clear Event

As a bonus, we'll also cover the `.clear()` event, which is triggered when the user clicks the clear icon to clear all messages. As a developer, you can attach additional events that should happen when this icon is clicked, e.g. to handle clearing of additional chatbot state:

```python
from uuid import uuid4
import gradio as gr


def clear():
    print("Cleared uuid")
    return uuid4()


def chat_fn(user_input, history, uuid):
    return f"{user_input} with uuid {uuid}"


with gr.Blocks() as demo:
    uuid_state = gr.State(
        uuid4
    )
    chatbot = gr.Chatbot(type="messages")
    chatbot.clear(clear, outputs=[uuid_state])

    gr.ChatInterface(
        chat_fn,
        additional_inputs=[uuid_state],
        chatbot=chatbot,
        type="messages"
    )

demo.launch()
```

In this example, the `clear` function, bound to the `chatbot.clear` event, returns a new UUID into our session state, when the chat history is cleared via the trash icon. This can be seen in the `chat_fn` function, which references the UUID saved in our session state.

This example also shows that you can use these events with `gr.ChatInterface` by passing in a custom `gr.Chatbot` object.

## Conclusion

That's it! You now know how you can implement the retry, undo, like, and clear events for the Chatbot.





=== File: guides/05_chatbots/06_creating-a-discord-bot-from-a-gradio-app.md ===
# 🚀 Creating Discord Bots with Gradio 🚀

Tags: CHAT, DEPLOY, DISCORD

You can make your Gradio app available as a Discord bot to let users in your Discord server interact with it directly. 

## How does it work?

The Discord bot will listen to messages mentioning it in channels. When it receives a message (which can include text as well as files), it will send it to your Gradio app via Gradio's built-in API. Your bot will reply with the response it receives from the API. 

Because Gradio's API is very flexible, you can create Discord bots that support text, images, audio, streaming, chat history, and a wide variety of other features very easily. 

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/Screen%20Recording%202024-12-18%20at%204.26.55%E2%80%AFPM.gif)

## Prerequisites

* Install the latest version of `gradio` and the `discord.py` libraries:

```
pip install --upgrade gradio discord.py~=2.0
```

* Have a running Gradio app. This app can be running locally or on Hugging Face Spaces. In this example, we will be using the [Gradio Playground Space](https://huggingface.co/spaces/abidlabs/gradio-playground-bot), which takes in an image and/or text and generates the code to generate the corresponding Gradio app.

Now, we are ready to get started!


### 1. Create a Discord application

First, go to the [Discord apps dashboard](https://discord.com/developers/applications). Look for the "New Application" button and click it. Give your application a name, and then click "Create".

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/discord-4.png)

On the resulting screen, you will see basic information about your application. Under the Settings section, click on the "Bot" option. You can update your bot's username if you would like.

Then click on the "Reset Token" button. A new token will be generated. Copy it as we will need it for the next step.

Scroll down to the section that says "Privileged Gateway Intents". Your bot will need certain permissions to work correctly. In this tutorial, we will only be using the "Message Content Intent" so click the toggle to enable this intent. Save the changes.

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/discord-3.png)



### 2. Write a Discord bot

Let's start by writing a very simple Discord bot, just to make sure that everything is working. Write the following Python code in a file called `bot.py`, pasting the discord bot token from the previous step:

```python
# bot.py
import discord

TOKEN = #PASTE YOUR DISCORD BOT TOKEN HERE

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)
```

Now, run this file: `python bot.py`, which should run and print a message like:

```text
We have logged in as GradioPlaygroundBot#1451
```

If that is working, we are ready to add Gradio-specific code. We will be using the [Gradio Python Client](https://www.gradio.app/guides/getting-started-with-the-python-client) to query the Gradio Playground Space mentioned above. Here's the updated `bot.py` file:

```python
import discord
from gradio_client import Client, handle_file
import httpx
import os

TOKEN = #PASTE YOUR DISCORD BOT TOKEN HERE

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
gradio_client = Client("abidlabs/gradio-playground-bot")

def download_image(attachment):
    response = httpx.get(attachment.url)
    image_path = f"./images/{attachment.filename}"
    os.makedirs("./images", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(response.content)
    return image_path

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the bot is mentioned in the message and reply
    if client.user in message.mentions:
        # Extract the message content without the bot mention
        clean_message = message.content.replace(f"<@{client.user.id}>", "").strip()

        # Handle images (only the first image is used)
        files = []
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']):
                    image_path = download_image(attachment)
                    files.append(handle_file(image_path))
                    break
        
        # Stream the responses to the channel
        for response in gradio_client.submit(
            message={"text": clean_message, "files": files},
        ):
            await message.channel.send(response[-1])

client.run(TOKEN)
```

### 3. Add the bot to your Discord Server

Now we are ready to install the bot on our server. Go back to the [Discord apps dashboard](https://discord.com/developers/applications). Under the Settings section, click on the "OAuth2" option. Scroll down to the "OAuth2 URL Generator" box and select the "bot" checkbox:

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/discord-2.png)



Then in "Bot Permissions" box that pops up underneath, enable the following permissions:

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/discord-1.png)


Copy the generated URL that appears underneath, which should look something like:

```text
https://discord.com/oauth2/authorize?client_id=1319011745452265575&permissions=377957238784&integration_type=0&scope=bot
```

Paste it into your browser, which should allow you to add the Discord bot to any Discord server that you manage.


### 4. That's it!

Now you can mention your bot from any channel in your Discord server, optionally attach an image, and it will respond with generated Gradio app code!

The bot will:
1. Listen for mentions
2. Process any attached images
3. Send the text and images to your Gradio app
4. Stream the responses back to the Discord channel

 This is just a basic example - you can extend it to handle more types of files, add error handling, or integrate with different Gradio apps.

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/Screen%20Recording%202024-12-18%20at%204.26.55%E2%80%AFPM.gif)

If you build a Discord bot from a Gradio app, feel free to share it on X and tag [the Gradio account](https://x.com/Gradio), and we are happy to help you amplify!

=== File: guides/05_chatbots/07_creating-a-slack-bot-from-a-gradio-app.md ===
# 🚀 Creating a Slack Bot from a Gradio App 🚀

Tags: CHAT, DEPLOY, SLACK

You can make your Gradio app available as a Slack bot to let users in your Slack workspace interact with it directly. 

## How does it work?

The Slack bot will listen to messages mentioning it in channels. When it receives a message (which can include text as well as files), it will send it to your Gradio app via Gradio's built-in API. Your bot will reply with the response it receives from the API. 

Because Gradio's API is very flexible, you can create Slack bots that support text, images, audio, streaming, chat history, and a wide variety of other features very easily. 

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/Screen%20Recording%202024-12-19%20at%203.30.00%E2%80%AFPM.gif)

## Prerequisites

* Install the latest version of `gradio` and the `slack-bolt` library:

```bash
pip install --upgrade gradio slack-bolt~=1.0
```

* Have a running Gradio app. This app can be running locally or on Hugging Face Spaces. In this example, we will be using the [Gradio Playground Space](https://huggingface.co/spaces/abidlabs/gradio-playground-bot), which takes in an image and/or text and generates the code to generate the corresponding Gradio app.

Now, we are ready to get started!

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click "Create New App"
2. Choose "From scratch" and give your app a name
3. Select the workspace where you want to develop your app
4. Under "OAuth & Permissions", scroll to "Scopes" and add these Bot Token Scopes:
   - `app_mentions:read`
   - `chat:write`
   - `files:read`
   - `files:write`
5. In the same "OAuth & Permissions" page, scroll back up and click the button to install the app to your workspace.
6. Note the "Bot User OAuth Token" (starts with `xoxb-`) that appears as we'll need it later
7. Click on "Socket Mode" in the menu bar. When the page loads, click the toggle to "Enable Socket Mode"
8. Give your token a name, such as `socket-token` and copy the token that is generated (starts with `xapp-`) as we'll need it later.
9. Finally, go to the "Event Subscription" option in the menu bar. Click the toggle to "Enable Events" and subscribe to the `app_mention` bot event.

### 2. Write a Slack bot

Let's start by writing a very simple Slack bot, just to make sure that everything is working. Write the following Python code in a file called `bot.py`, pasting the two tokens from step 6 and step 8 in the previous section.

```py
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = # PASTE YOUR SLACK BOT TOKEN HERE
SLACK_APP_TOKEN = # PASTE YOUR SLACK APP TOKEN HERE

app = App(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
def handle_app_mention_events(body, say):
    user_id = body["event"]["user"]
    say(f"Hi <@{user_id}>! You mentioned me and said: {body['event']['text']}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
```

If that is working, we are ready to add Gradio-specific code. We will be using the [Gradio Python Client](https://www.gradio.app/guides/getting-started-with-the-python-client) to query the Gradio Playground Space mentioned above. Here's the updated `bot.py` file:

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = # PASTE YOUR SLACK BOT TOKEN HERE
SLACK_APP_TOKEN = # PASTE YOUR SLACK APP TOKEN HERE

app = App(token=SLACK_BOT_TOKEN)
gradio_client = Client("abidlabs/gradio-playground-bot")

def download_image(url, filename):
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    response = httpx.get(url, headers=headers)
    image_path = f"./images/{filename}"
    os.makedirs("./images", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(response.content)
    return image_path

def slackify_message(message):   
    # Replace markdown links with slack format and remove code language specifier after triple backticks
    pattern = r'\[(.*?)\]\((.*?)\)'
    cleaned = re.sub(pattern, r'<\2|\1>', message)
    cleaned = re.sub(r'```\w+\n', '```', cleaned)
    return cleaned.strip()

@app.event("app_mention")
def handle_app_mention_events(body, say):
    # Extract the message content without the bot mention
    text = body["event"]["text"]
    bot_user_id = body["authorizations"][0]["user_id"]
    clean_message = text.replace(f"<@{bot_user_id}>", "").strip()
    
    # Handle images if present
    files = []
    if "files" in body["event"]:
        for file in body["event"]["files"]:
            if file["filetype"] in ["png", "jpg", "jpeg", "gif", "webp"]:
                image_path = download_image(file["url_private_download"], file["name"])
                files.append(handle_file(image_path))
                break
    
    # Submit to Gradio and send responses back to Slack
    for response in gradio_client.submit(
        message={"text": clean_message, "files": files},
    ):
        cleaned_response = slackify_message(response[-1])
        say(cleaned_response)

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
```
### 3. Add the bot to your Slack Workplace

Now, create a new channel or navigate to an existing channel in your Slack workspace where you want to use the bot. Click the "+" button next to "Channels" in your Slack sidebar and follow the prompts to create a new channel.

Finally, invite your bot to the channel:
1. In your new channel, type `/invite @YourBotName`
2. Select your bot from the dropdown
3. Click "Invite to Channel"

### 4. That's it!

Now you can mention your bot in any channel it's in, optionally attach an image, and it will respond with generated Gradio app code!

The bot will:
1. Listen for mentions
2. Process any attached images
3. Send the text and images to your Gradio app
4. Stream the responses back to the Slack channel

This is just a basic example - you can extend it to handle more types of files, add error handling, or integrate with different Gradio apps!

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/Screen%20Recording%202024-12-19%20at%203.30.00%E2%80%AFPM.gif)

If you build a Slack bot from a Gradio app, feel free to share it on X and tag [the Gradio account](https://x.com/Gradio), and we are happy to help you amplify!

=== File: guides/05_chatbots/08_creating-a-website-widget-from-a-gradio-chatbot.md ===
# 🚀 Creating a Website Chat Widget with Gradio 🚀

Tags: CHAT, DEPLOY, WEB

You can make your Gradio Chatbot available as an embedded chat widget on your website, similar to popular customer service widgets like Intercom. This is particularly useful for:

- Adding AI assistance to your documentation pages
- Providing interactive help on your portfolio or product website
- Creating a custom chatbot interface for your Gradio app

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/Screen%20Recording%202024-12-19%20at%203.32.46%E2%80%AFPM.gif)

## How does it work?

The chat widget appears as a small button in the corner of your website. When clicked, it opens a chat interface that communicates with your Gradio app via the JavaScript Client API. Users can ask questions and receive responses directly within the widget.


## Prerequisites

* A running Gradio app (local or on Hugging Face Spaces). In this example, we'll use the [Gradio Playground Space](https://huggingface.co/spaces/abidlabs/gradio-playground-bot), which helps generate code for Gradio apps based on natural language descriptions.

### 1. Create and Style the Chat Widget

First, add this HTML and CSS to your website:

```html
<div id="chat-widget" class="chat-widget">
    <button id="chat-toggle" class="chat-toggle">💬</button>
    <div id="chat-container" class="chat-container hidden">
        <div id="chat-header">
            <h3>Gradio Assistant</h3>
            <button id="close-chat">×</button>
        </div>
        <div id="chat-messages"></div>
        <div id="chat-input-area">
            <input type="text" id="chat-input" placeholder="Ask a question...">
            <button id="send-message">Send</button>
        </div>
    </div>
</div>

<style>
.chat-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
}

.chat-toggle {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #007bff;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
}

.chat-container {
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 300px;
    height: 400px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
}

.chat-container.hidden {
    display: none;
}

#chat-header {
    padding: 10px;
    background: #007bff;
    color: white;
    border-radius: 10px 10px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

#chat-messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px;
}

#chat-input-area {
    padding: 10px;
    border-top: 1px solid #eee;
    display: flex;
}

#chat-input {
    flex-grow: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-right: 8px;
}

.message {
    margin: 8px 0;
    padding: 8px;
    border-radius: 4px;
}

.user-message {
    background: #e9ecef;
    margin-left: 20px;
}

.bot-message {
    background: #f8f9fa;
    margin-right: 20px;
}
</style>
```

### 2. Add the JavaScript

Then, add the following JavaScript code (which uses the Gradio JavaScript Client to connect to the Space) to your website by including this in the `<head>` section of your website:

```html
<script type="module">
    import { Client } from "https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js";
    
    async function initChatWidget() {
        const client = await Client.connect("https://abidlabs-gradio-playground-bot.hf.space");
        
        const chatToggle = document.getElementById('chat-toggle');
        const chatContainer = document.getElementById('chat-container');
        const closeChat = document.getElementById('close-chat');
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-message');
        const messagesContainer = document.getElementById('chat-messages');
    
        chatToggle.addEventListener('click', () => {
            chatContainer.classList.remove('hidden');
        });
    
        closeChat.addEventListener('click', () => {
            chatContainer.classList.add('hidden');
        });
    
        async function sendMessage() {
            const userMessage = chatInput.value.trim();
            if (!userMessage) return;

            appendMessage(userMessage, 'user');
            chatInput.value = '';

            try {
                const result = await client.predict("/chat", {
                    message: {"text": userMessage, "files": []}
                });
                const message = result.data[0];
                console.log(result.data[0]);
                const botMessage = result.data[0].join('\n');
                appendMessage(botMessage, 'bot');
            } catch (error) {
                console.error('Error:', error);
                appendMessage('Sorry, there was an error processing your request.', 'bot');
            }
        }
    
        function appendMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            if (sender === 'bot') {
                messageDiv.innerHTML = marked.parse(text);
            } else {
                messageDiv.textContent = text;
            }
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
    
    initChatWidget();
</script>
```

### 3. That's it!

Your website now has a chat widget that connects to your Gradio app! Users can click the chat button to open the widget and start interacting with your app.

### Customization

You can customize the appearance of the widget by modifying the CSS. Some ideas:
- Change the colors to match your website's theme
- Adjust the size and position of the widget
- Add animations for opening/closing
- Modify the message styling

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/Screen%20Recording%202024-12-19%20at%203.32.46%E2%80%AFPM.gif)

If you build a website widget from a Gradio app, feel free to share it on X and tag [the Gradio account](https://x.com/Gradio), and we are happy to help you amplify!
