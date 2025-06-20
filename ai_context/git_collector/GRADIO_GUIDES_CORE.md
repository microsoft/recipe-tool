# gradio-app/gradio/guides

[git-collector-data]

**URL:** https://github.com/gradio-app/gradio/tree/main/guides  
**Date:** 6/18/2025, 12:11:17 PM  
**Files:** 34  

=== File: guides/01_getting-started/01_quickstart.md ===
# Quickstart

Gradio is an open-source Python package that allows you to quickly **build** a demo or web application for your machine learning model, API, or any arbitrary Python function. You can then **share** a link to your demo or web application in just a few seconds using Gradio's built-in sharing features. *No JavaScript, CSS, or web hosting experience needed!*

<img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/gif-version.gif" style="padding-bottom: 10px">

It just takes a few lines of Python to create your own demo, so let's get started 💫


## Installation

**Prerequisite**: Gradio requires [Python 3.10 or higher](https://www.python.org/downloads/).


We recommend installing Gradio using `pip`, which is included by default in Python. Run this in your terminal or command prompt:

```bash
pip install --upgrade gradio
```


Tip: It is best to install Gradio in a virtual environment. Detailed installation instructions for all common operating systems <a href="https://www.gradio.app/main/guides/installing-gradio-in-a-virtual-environment">are provided here</a>. 

## Building Your First Demo

You can run Gradio in your favorite code editor, Jupyter notebook, Google Colab, or anywhere else you write Python. Let's write your first Gradio app:


$code_hello_world_4


Tip: We shorten the imported name from <code>gradio</code> to <code>gr</code>. This is a widely adopted convention for better readability of code. 

Now, run your code. If you've written the Python code in a file named `app.py`, then you would run `python app.py` from the terminal.

The demo below will open in a browser on [http://localhost:7860](http://localhost:7860) if running from a file. If you are running within a notebook, the demo will appear embedded within the notebook.

$demo_hello_world_4

Type your name in the textbox on the left, drag the slider, and then press the Submit button. You should see a friendly greeting on the right.

Tip: When developing locally, you can run your Gradio app in <strong>hot reload mode</strong>, which automatically reloads the Gradio app whenever you make changes to the file. To do this, simply type in <code>gradio</code> before the name of the file instead of <code>python</code>. In the example above, you would type: `gradio app.py` in your terminal. Learn more in the <a href="https://www.gradio.app/guides/developing-faster-with-reload-mode">Hot Reloading Guide</a>.


**Understanding the `Interface` Class**

You'll notice that in order to make your first demo, you created an instance of the `gr.Interface` class. The `Interface` class is designed to create demos for machine learning models which accept one or more inputs, and return one or more outputs. 

The `Interface` class has three core arguments:

- `fn`: the function to wrap a user interface (UI) around
- `inputs`: the Gradio component(s) to use for the input. The number of components should match the number of arguments in your function.
- `outputs`: the Gradio component(s) to use for the output. The number of components should match the number of return values from your function.

The `fn` argument is very flexible -- you can pass *any* Python function that you want to wrap with a UI. In the example above, we saw a relatively simple function, but the function could be anything from a music generator to a tax calculator to the prediction function of a pretrained machine learning model.

The `inputs` and `outputs` arguments take one or more Gradio components. As we'll see, Gradio includes more than [30 built-in components](https://www.gradio.app/docs/gradio/introduction) (such as the `gr.Textbox()`, `gr.Image()`, and `gr.HTML()` components) that are designed for machine learning applications. 

Tip: For the `inputs` and `outputs` arguments, you can pass in the name of these components as a string (`"textbox"`) or an instance of the class (`gr.Textbox()`).

If your function accepts more than one argument, as is the case above, pass a list of input components to `inputs`, with each input component corresponding to one of the arguments of the function, in order. The same holds true if your function returns more than one value: simply pass in a list of components to `outputs`. This flexibility makes the `Interface` class a very powerful way to create demos.

We'll dive deeper into the `gr.Interface` on our series on [building Interfaces](https://www.gradio.app/main/guides/the-interface-class).

## Sharing Your Demo

What good is a beautiful demo if you can't share it? Gradio lets you easily share a machine learning demo without having to worry about the hassle of hosting on a web server. Simply set `share=True` in `launch()`, and a publicly accessible URL will be created for your demo. Let's revisit our example demo,  but change the last line as follows:

```python
import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")
    
demo.launch(share=True)  # Share your demo with just 1 extra parameter 🚀
```

When you run this code, a public URL will be generated for your demo in a matter of seconds, something like:

👉 &nbsp; `https://a23dsf231adb.gradio.live`

Now, anyone around the world can try your Gradio demo from their browser, while the machine learning model and all computation continues to run locally on your computer.

To learn more about sharing your demo, read our dedicated guide on [sharing your Gradio application](https://www.gradio.app/guides/sharing-your-app).


## An Overview of Gradio

So far, we've been discussing the `Interface` class, which is a high-level class that lets to build demos quickly with Gradio. But what else does Gradio include?

### Custom Demos with `gr.Blocks`

Gradio offers a low-level approach for designing web apps with more customizable layouts and data flows with the `gr.Blocks` class. Blocks supports things like controlling where components appear on the page, handling multiple data flows and more complex interactions (e.g. outputs can serve as inputs to other functions), and updating properties/visibility of components based on user interaction — still all in Python. 

You can build very custom and complex applications using `gr.Blocks()`. For example, the popular image generation [Automatic1111 Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) is built using Gradio Blocks. We dive deeper into the `gr.Blocks` on our series on [building with Blocks](https://www.gradio.app/guides/blocks-and-event-listeners).

### Chatbots with `gr.ChatInterface`

Gradio includes another high-level class, `gr.ChatInterface`, which is specifically designed to create Chatbot UIs. Similar to `Interface`, you supply a function and Gradio creates a fully working Chatbot UI. If you're interested in creating a chatbot, you can jump straight to [our dedicated guide on `gr.ChatInterface`](https://www.gradio.app/guides/creating-a-chatbot-fast).

### The Gradio Python & JavaScript Ecosystem

That's the gist of the core `gradio` Python library, but Gradio is actually so much more! It's an entire ecosystem of Python and JavaScript libraries that let you build machine learning applications, or query them programmatically, in Python or JavaScript. Here are other related parts of the Gradio ecosystem:

* [Gradio Python Client](https://www.gradio.app/guides/getting-started-with-the-python-client) (`gradio_client`): query any Gradio app programmatically in Python.
* [Gradio JavaScript Client](https://www.gradio.app/guides/getting-started-with-the-js-client) (`@gradio/client`): query any Gradio app programmatically in JavaScript.
* [Gradio-Lite](https://www.gradio.app/guides/gradio-lite) (`@gradio/lite`): write Gradio apps in Python that run entirely in the browser (no server needed!), thanks to Pyodide. 
* [Hugging Face Spaces](https://huggingface.co/spaces): the most popular place to host Gradio applications — for free!

## What's Next?

Keep learning about Gradio sequentially using the Gradio Guides, which include explanations as well as example code and embedded interactive demos. Next up: [let's dive deeper into the Interface class](https://www.gradio.app/guides/the-interface-class).

Or, if you already know the basics and are looking for something specific, you can search the more [technical API documentation](https://www.gradio.app/docs/).


## Gradio Sketch

You can also build Gradio applications without writing any code. Simply type `gradio sketch` into your terminal to open up an editor that lets you define and modify Gradio components, adjust their layouts, add events, all through a web editor. Or [use this hosted version of Gradio Sketch, running on Hugging Face Spaces](https://huggingface.co/spaces/aliabid94/Sketch).

=== File: guides/02_building-interfaces/00_the-interface-class.md ===
# The `Interface` class

As mentioned in the [Quickstart](/main/guides/quickstart), the `gr.Interface` class is a high-level abstraction in Gradio that allows you to quickly create a demo for any Python function simply by specifying the input types and the output types. Revisiting our first demo:

$code_hello_world_4


We see that the `Interface` class is initialized with three required parameters:

- `fn`: the function to wrap a user interface (UI) around
- `inputs`: which Gradio component(s) to use for the input. The number of components should match the number of arguments in your function.
- `outputs`: which Gradio component(s) to use for the output. The number of components should match the number of return values from your function.

In this Guide, we'll dive into `gr.Interface` and the various ways it can be customized, but before we do that, let's get a better understanding of Gradio components.

## Gradio Components

Gradio includes more than 30 pre-built components (as well as many [community-built _custom components_](https://www.gradio.app/custom-components/gallery)) that can be used as inputs or outputs in your demo. These components correspond to common data types in machine learning and data science, e.g. the `gr.Image` component is designed to handle input or output images, the `gr.Label` component displays classification labels and probabilities, the `gr.LinePlot` component displays line plots, and so on. 

## Components Attributes

We used the default versions of the `gr.Textbox` and `gr.Slider`, but what if you want to change how the UI components look or behave?

Let's say you want to customize the slider to have values from 1 to 10, with a default of 2. And you wanted to customize the output text field — you want it to be larger and have a label.

If you use the actual classes for `gr.Textbox` and `gr.Slider` instead of the string shortcuts, you have access to much more customizability through component attributes.

$code_hello_world_2
$demo_hello_world_2

## Multiple Input and Output Components

Suppose you had a more complex function, with multiple outputs as well. In the example below, we define a function that takes a string, boolean, and number, and returns a string and number. 

$code_hello_world_3
$demo_hello_world_3

Just as each component in the `inputs` list corresponds to one of the parameters of the function, in order, each component in the `outputs` list corresponds to one of the values returned by the function, in order.

## An Image Example

Gradio supports many types of components, such as `Image`, `DataFrame`, `Video`, or `Label`. Let's try an image-to-image function to get a feel for these!

$code_sepia_filter
$demo_sepia_filter

When using the `Image` component as input, your function will receive a NumPy array with the shape `(height, width, 3)`, where the last dimension represents the RGB values. We'll return an image as well in the form of a NumPy array. 

Gradio handles the preprocessing and postprocessing to convert images to NumPy arrays and vice versa. You can also control the preprocessing performed with the `type=` keyword argument. For example, if you wanted your function to take a file path to an image instead of a NumPy array, the input `Image` component could be written as:

```python
gr.Image(type="filepath")
```

You can read more about the built-in Gradio components and how to customize them in the [Gradio docs](https://gradio.app/docs).

## Example Inputs

You can provide example data that a user can easily load into `Interface`. This can be helpful to demonstrate the types of inputs the model expects, as well as to provide a way to explore your dataset in conjunction with your model. To load example data, you can provide a **nested list** to the `examples=` keyword argument of the Interface constructor. Each sublist within the outer list represents a data sample, and each element within the sublist represents an input for each input component. The format of example data for each component is specified in the [Docs](https://gradio.app/docs#components).

$code_calculator
$demo_calculator

You can load a large dataset into the examples to browse and interact with the dataset through Gradio. The examples will be automatically paginated (you can configure this through the `examples_per_page` argument of `Interface`).

Continue learning about examples in the [More On Examples](https://gradio.app/guides/more-on-examples) guide.

## Descriptive Content

In the previous example, you may have noticed the `title=` and `description=` keyword arguments in the `Interface` constructor that helps users understand your app.

There are three arguments in the `Interface` constructor to specify where this content should go:

- `title`: which accepts text and can display it at the very top of interface, and also becomes the page title.
- `description`: which accepts text, markdown or HTML and places it right under the title.
- `article`: which also accepts text, markdown or HTML and places it below the interface.

![annotated](https://github.com/gradio-app/gradio/blob/main/guides/assets/annotated.png?raw=true)

Another useful keyword argument is `label=`, which is present in every `Component`. This modifies the label text at the top of each `Component`. You can also add the `info=` keyword argument to form elements like `Textbox` or `Radio` to provide further information on their usage.

```python
gr.Number(label='Age', info='In years, must be greater than 0')
```

## Additional Inputs within an Accordion

If your prediction function takes many inputs, you may want to hide some of them within a collapsed accordion to avoid cluttering the UI. The `Interface` class takes an `additional_inputs` argument which is similar to `inputs` but any input components included here are not visible by default. The user must click on the accordion to show these components. The additional inputs are passed into the prediction function, in order, after the standard inputs.

You can customize the appearance of the accordion by using the optional `additional_inputs_accordion` argument, which accepts a string (in which case, it becomes the label of the accordion), or an instance of the `gr.Accordion()` class (e.g. this lets you control whether the accordion is open or closed by default).

Here's an example:

$code_interface_with_additional_inputs
$demo_interface_with_additional_inputs



=== File: guides/02_building-interfaces/01_more-on-examples.md ===
# More on Examples

In the [previous Guide](/main/guides/the-interface-class), we discussed how to provide example inputs for your demo to make it easier for users to try it out. Here, we dive into more details.

## Providing Examples

Adding examples to an Interface is as easy as providing a list of lists to the `examples`
keyword argument.
Each sublist is a data sample, where each element corresponds to an input of the prediction function.
The inputs must be ordered in the same order as the prediction function expects them.

If your interface only has one input component, then you can provide your examples as a regular list instead of a list of lists.

### Loading Examples from a Directory

You can also specify a path to a directory containing your examples. If your Interface takes only a single file-type input, e.g. an image classifier, you can simply pass a directory filepath to the `examples=` argument, and the `Interface` will load the images in the directory as examples.
In the case of multiple inputs, this directory must
contain a log.csv file with the example values.
In the context of the calculator demo, we can set `examples='/demo/calculator/examples'` and in that directory we include the following `log.csv` file:

```csv
num,operation,num2
5,"add",3
4,"divide",2
5,"multiply",3
```

This can be helpful when browsing flagged data. Simply point to the flagged directory and the `Interface` will load the examples from the flagged data.

### Providing Partial Examples

Sometimes your app has many input components, but you would only like to provide examples for a subset of them. In order to exclude some inputs from the examples, pass `None` for all data samples corresponding to those particular components.

## Caching examples

You may wish to provide some cached examples of your model for users to quickly try out, in case your model takes a while to run normally.
If `cache_examples=True`, your Gradio app will run all of the examples and save the outputs when you call the `launch()` method. This data will be saved in a directory called `gradio_cached_examples` in your working directory by default. You can also set this directory with the `GRADIO_EXAMPLES_CACHE` environment variable, which can be either an absolute path or a relative path to your working directory.

Whenever a user clicks on an example, the output will automatically be populated in the app now, using data from this cached directory instead of actually running the function. This is useful so users can quickly try out your model without adding any load!

Alternatively, you can set `cache_examples="lazy"`. This means that each particular example will only get cached after it is first used (by any user) in the Gradio app. This is helpful if your prediction function is long-running and you do not want to wait a long time for your Gradio app to start.

Keep in mind once the cache is generated, it will not be updated automatically in future launches. If the examples or function logic change, delete the cache folder to clear the cache and rebuild it with another `launch()`.


=== File: guides/02_building-interfaces/02_flagging.md ===

# Flagging

You may have noticed the "Flag" button that appears by default in your `Interface`. When a user using your demo sees input with interesting output, such as erroneous or unexpected model behaviour, they can flag the input for you to review. Within the directory provided by the `flagging_dir=` argument to the `Interface` constructor, a CSV file will log the flagged inputs. If the interface involves file data, such as for Image and Audio components, folders will be created to store those flagged data as well.

For example, with the calculator interface shown above, we would have the flagged data stored in the flagged directory shown below:

```directory
+-- calculator.py
+-- flagged/
|   +-- logs.csv
```

_flagged/logs.csv_

```csv
num1,operation,num2,Output
5,add,7,12
6,subtract,1.5,4.5
```

With the sepia interface shown earlier, we would have the flagged data stored in the flagged directory shown below:

```directory
+-- sepia.py
+-- flagged/
|   +-- logs.csv
|   +-- im/
|   |   +-- 0.png
|   |   +-- 1.png
|   +-- Output/
|   |   +-- 0.png
|   |   +-- 1.png
```

_flagged/logs.csv_

```csv
im,Output
im/0.png,Output/0.png
im/1.png,Output/1.png
```

If you wish for the user to provide a reason for flagging, you can pass a list of strings to the `flagging_options` argument of Interface. Users will have to select one of the strings when flagging, which will be saved as an additional column to the CSV.




=== File: guides/02_building-interfaces/03_interface-state.md ===
# Interface State

So far, we've assumed that your demos are *stateless*: that they do not persist information beyond a single function call. What if you want to modify the behavior of your demo based on previous interactions with the demo? There are two approaches in Gradio: *global state* and *session state*.

## Global State

If the state is something that should be accessible to all function calls and all users, you can create a variable outside the function call and access it inside the function. For example, you may load a large model outside the function and use it inside the function so that every function call does not need to reload the model.

$code_score_tracker

In the code above, the `scores` array is shared between all users. If multiple users are accessing this demo, their scores will all be added to the same list, and the returned top 3 scores will be collected from this shared reference.

## Session State

Another type of data persistence Gradio supports is session state, where data persists across multiple submits within a page session. However, data is _not_ shared between different users of your model. To store data in a session state, you need to do three things:

1. Pass in an extra parameter into your function, which represents the state of the interface.
2. At the end of the function, return the updated value of the state as an extra return value.
3. Add the `'state'` input and `'state'` output components when creating your `Interface`

Here's a simple app to illustrate session state - this app simply stores users previous submissions and displays them back to the user:


$code_interface_state
$demo_interface_state


Notice how the state persists across submits within each page, but if you load this demo in another tab (or refresh the page), the demos will not share chat history. Here, we could not store the submission history in a global variable, otherwise the submission history would then get jumbled between different users.

The initial value of the `State` is `None` by default. If you pass a parameter to the `value` argument of `gr.State()`, it is used as the default value of the state instead. 

Note: the `Interface` class only supports a single session state variable (though it can be a list with multiple elements). For more complex use cases, you can use Blocks, [which supports multiple `State` variables](/guides/state-in-blocks/). Alternatively, if you are building a chatbot that maintains user state, consider using the `ChatInterface` abstraction, [which manages state automatically](/guides/creating-a-chatbot-fast).


=== File: guides/02_building-interfaces/04_reactive-interfaces.md ===
# Reactive Interfaces

Finally, we cover how to get Gradio demos to refresh automatically or continuously stream data.

## Live Interfaces

You can make interfaces automatically refresh by setting `live=True` in the interface. Now the interface will recalculate as soon as the user input changes.

$code_calculator_live
$demo_calculator_live

Note there is no submit button, because the interface resubmits automatically on change.

## Streaming Components

Some components have a "streaming" mode, such as `Audio` component in microphone mode, or the `Image` component in webcam mode. Streaming means data is sent continuously to the backend and the `Interface` function is continuously being rerun.

The difference between `gr.Audio(source='microphone')` and `gr.Audio(source='microphone', streaming=True)`, when both are used in `gr.Interface(live=True)`, is that the first `Component` will automatically submit data and run the `Interface` function when the user stops recording, whereas the second `Component` will continuously send data and run the `Interface` function _during_ recording.

Here is example code of streaming images from the webcam.

$code_stream_frames

Streaming can also be done in an output component. A `gr.Audio(streaming=True)` output component can take a stream of audio data yielded piece-wise by a generator function and combines them into a single audio file. For a detailed example, see our guide on performing [automatic speech recognition](/guides/real-time-speech-recognition) with Gradio.


=== File: guides/02_building-interfaces/05_four-kinds-of-interfaces.md ===
# The 4 Kinds of Gradio Interfaces

So far, we've always assumed that in order to build an Gradio demo, you need both inputs and outputs. But this isn't always the case for machine learning demos: for example, _unconditional image generation models_ don't take any input but produce an image as the output.

It turns out that the `gradio.Interface` class can actually handle 4 different kinds of demos:

1. **Standard demos**: which have both separate inputs and outputs (e.g. an image classifier or speech-to-text model)
2. **Output-only demos**: which don't take any input but produce on output (e.g. an unconditional image generation model)
3. **Input-only demos**: which don't produce any output but do take in some sort of input (e.g. a demo that saves images that you upload to a persistent external database)
4. **Unified demos**: which have both input and output components, but the input and output components _are the same_. This means that the output produced overrides the input (e.g. a text autocomplete model)

Depending on the kind of demo, the user interface (UI) looks slightly different:

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/interfaces4.png)

Let's see how to build each kind of demo using the `Interface` class, along with examples:

## Standard demos

To create a demo that has both the input and the output components, you simply need to set the values of the `inputs` and `outputs` parameter in `Interface()`. Here's an example demo of a simple image filter:

$code_sepia_filter
$demo_sepia_filter

## Output-only demos

What about demos that only contain outputs? In order to build such a demo, you simply set the value of the `inputs` parameter in `Interface()` to `None`. Here's an example demo of a mock image generation model:

$code_fake_gan_no_input
$demo_fake_gan_no_input

## Input-only demos

Similarly, to create a demo that only contains inputs, set the value of `outputs` parameter in `Interface()` to be `None`. Here's an example demo that saves any uploaded image to disk:

$code_save_file_no_output
$demo_save_file_no_output

## Unified demos

A demo that has a single component as both the input and the output. It can simply be created by setting the values of the `inputs` and `outputs` parameter as the same component. Here's an example demo of a text generation model:

$code_unified_demo_text_generation
$demo_unified_demo_text_generation

It may be the case that none of the 4 cases fulfill your exact needs. In this case, you need to use the `gr.Blocks()` approach!

=== File: guides/03_building-with-blocks/01_blocks-and-event-listeners.md ===
# Blocks and Event Listeners

We briefly described the Blocks class in the [Quickstart](/main/guides/quickstart#custom-demos-with-gr-blocks) as a way to build custom demos. Let's dive deeper. 


## Blocks Structure

Take a look at the demo below.

$code_hello_blocks
$demo_hello_blocks

- First, note the `with gr.Blocks() as demo:` clause. The Blocks app code will be contained within this clause.
- Next come the Components. These are the same Components used in `Interface`. However, instead of being passed to some constructor, Components are automatically added to the Blocks as they are created within the `with` clause.
- Finally, the `click()` event listener. Event listeners define the data flow within the app. In the example above, the listener ties the two Textboxes together. The Textbox `name` acts as the input and Textbox `output` acts as the output to the `greet` method. This dataflow is triggered when the Button `greet_btn` is clicked. Like an Interface, an event listener can take multiple inputs or outputs.

You can also attach event listeners using decorators - skip the `fn` argument and assign `inputs` and `outputs` directly:

$code_hello_blocks_decorator

## Event Listeners and Interactivity

In the example above, you'll notice that you are able to edit Textbox `name`, but not Textbox `output`. This is because any Component that acts as an input to an event listener is made interactive. However, since Textbox `output` acts only as an output, Gradio determines that it should not be made interactive. You can override the default behavior and directly configure the interactivity of a Component with the boolean `interactive` keyword argument, e.g. `gr.Textbox(interactive=True)`.

```python
output = gr.Textbox(label="Output", interactive=True)
```

_Note_: What happens if a Gradio component is neither an input nor an output? If a component is constructed with a default value, then it is presumed to be displaying content and is rendered non-interactive. Otherwise, it is rendered interactive. Again, this behavior can be overridden by specifying a value for the `interactive` argument.

## Types of Event Listeners

Take a look at the demo below:

$code_blocks_hello
$demo_blocks_hello

Instead of being triggered by a click, the `welcome` function is triggered by typing in the Textbox `inp`. This is due to the `change()` event listener. Different Components support different event listeners. For example, the `Video` Component supports a `play()` event listener, triggered when a user presses play. See the [Docs](http://gradio.app/docs#components) for the event listeners for each Component.

## Multiple Data Flows

A Blocks app is not limited to a single data flow the way Interfaces are. Take a look at the demo below:

$code_reversible_flow
$demo_reversible_flow

Note that `num1` can act as input to `num2`, and also vice-versa! As your apps get more complex, you will have many data flows connecting various Components.

Here's an example of a "multi-step" demo, where the output of one model (a speech-to-text model) gets fed into the next model (a sentiment classifier).

$code_blocks_speech_text_sentiment
$demo_blocks_speech_text_sentiment

## Function Input List vs Dict

The event listeners you've seen so far have a single input component. If you'd like to have multiple input components pass data to the function, you have two options on how the function can accept input component values:

1. as a list of arguments, or
2. as a single dictionary of values, keyed by the component

Let's see an example of each:
$code_calculator_list_and_dict

Both `add()` and `sub()` take `a` and `b` as inputs. However, the syntax is different between these listeners.

1. To the `add_btn` listener, we pass the inputs as a list. The function `add()` takes each of these inputs as arguments. The value of `a` maps to the argument `num1`, and the value of `b` maps to the argument `num2`.
2. To the `sub_btn` listener, we pass the inputs as a set (note the curly brackets!). The function `sub()` takes a single dictionary argument `data`, where the keys are the input components, and the values are the values of those components.

It is a matter of preference which syntax you prefer! For functions with many input components, option 2 may be easier to manage.

$demo_calculator_list_and_dict

## Function Return List vs Dict

Similarly, you may return values for multiple output components either as:

1. a list of values, or
2. a dictionary keyed by the component

Let's first see an example of (1), where we set the values of two output components by returning two values:

```python
with gr.Blocks() as demo:
    food_box = gr.Number(value=10, label="Food Count")
    status_box = gr.Textbox()

    def eat(food):
        if food > 0:
            return food - 1, "full"
        else:
            return 0, "hungry"

    gr.Button("Eat").click(
        fn=eat,
        inputs=food_box,
        outputs=[food_box, status_box]
    )
```

Above, each return statement returns two values corresponding to `food_box` and `status_box`, respectively.

**Note:** if your event listener has a single output component, you should **not** return it as a single-item list. This will not work, since Gradio does not know whether to interpret that outer list as part of your return value. You should instead just return that value directly.

Now, let's see option (2). Instead of returning a list of values corresponding to each output component in order, you can also return a dictionary, with the key corresponding to the output component and the value as the new value. This also allows you to skip updating some output components.

```python
with gr.Blocks() as demo:
    food_box = gr.Number(value=10, label="Food Count")
    status_box = gr.Textbox()

    def eat(food):
        if food > 0:
            return {food_box: food - 1, status_box: "full"}
        else:
            return {status_box: "hungry"}

    gr.Button("Eat").click(
        fn=eat,
        inputs=food_box,
        outputs=[food_box, status_box]
    )
```

Notice how when there is no food, we only update the `status_box` element. We skipped updating the `food_box` component.

Dictionary returns are helpful when an event listener affects many components on return, or conditionally affects outputs and not others.

Keep in mind that with dictionary returns, we still need to specify the possible outputs in the event listener.

## Updating Component Configurations

The return value of an event listener function is usually the updated value of the corresponding output Component. Sometimes we want to update the configuration of the Component as well, such as the visibility. In this case, we return a new Component, setting the properties we want to change.

$code_blocks_essay_simple
$demo_blocks_essay_simple

See how we can configure the Textbox itself through a new `gr.Textbox()` method. The `value=` argument can still be used to update the value along with Component configuration. Any arguments we do not set will preserve their previous values.

## Not Changing a Component's Value

In some cases, you may want to leave a component's value unchanged. Gradio includes a special function, `gr.skip()`, which can be returned from your function. Returning this function will keep the output component (or components') values as is. Let us illustrate with an example:

$code_skip
$demo_skip

Note the difference between returning `None` (which generally resets a component's value to an empty state) versus returning `gr.skip()`, which leaves the component value unchanged.

Tip: if you have multiple output components, and you want to leave all of their values unchanged, you can just return a single `gr.skip()` instead of returning a tuple of skips, one for each element.

## Running Events Consecutively

You can also run events consecutively by using the `then` method of an event listener. This will run an event after the previous event has finished running. This is useful for running events that update components in multiple steps.

For example, in the chatbot example below, we first update the chatbot with the user message immediately, and then update the chatbot with the computer response after a simulated delay.

$code_chatbot_consecutive
$demo_chatbot_consecutive

The `.then()` method of an event listener executes the subsequent event regardless of whether the previous event raised any errors. If you'd like to only run subsequent events if the previous event executed successfully, use the `.success()` method, which takes the same arguments as `.then()`.

## Binding Multiple Triggers to a Function

Often times, you may want to bind multiple triggers to the same function. For example, you may want to allow a user to click a submit button, or press enter to submit a form. You can do this using the `gr.on` method and passing a list of triggers to the `trigger`.

$code_on_listener_basic
$demo_on_listener_basic

You can use decorator syntax as well:

$code_on_listener_decorator

You can use `gr.on` to create "live" events by binding to the `change` event of components that implement it. If you do not specify any triggers, the function will automatically bind to all `change` event of all input components that include a `change` event (for example `gr.Textbox` has a `change` event whereas `gr.Button` does not).

$code_on_listener_live
$demo_on_listener_live

You can follow `gr.on` with `.then`, just like any regular event listener. This handy method should save you from having to write a lot of repetitive code!

## Binding a Component Value Directly to a Function of Other Components

If you want to set a Component's value to always be a function of the value of other Components, you can use the following shorthand:

```python
with gr.Blocks() as demo:
  num1 = gr.Number()
  num2 = gr.Number()
  product = gr.Number(lambda a, b: a * b, inputs=[num1, num2])
```

This functionally the same as:
```python
with gr.Blocks() as demo:
  num1 = gr.Number()
  num2 = gr.Number()
  product = gr.Number()

  gr.on(
    [num1.change, num2.change, demo.load], 
    lambda a, b: a * b, 
    inputs=[num1, num2], 
    outputs=product
  )
```


=== File: guides/03_building-with-blocks/02_controlling-layout.md ===
# Controlling Layout

By default, Components in Blocks are arranged vertically. Let's take a look at how we can rearrange Components. Under the hood, this layout structure uses the [flexbox model of web development](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout/Basic_Concepts_of_Flexbox).

## Rows

Elements within a `with gr.Row` clause will all be displayed horizontally. For example, to display two Buttons side by side:

```python
with gr.Blocks() as demo:
    with gr.Row():
        btn1 = gr.Button("Button 1")
        btn2 = gr.Button("Button 2")
```

You can set every element in a Row to have the same height. Configure this with the `equal_height` argument.

```python
with gr.Blocks() as demo:
    with gr.Row(equal_height=True):
        textbox = gr.Textbox()
        btn2 = gr.Button("Button 2")
```

The widths of elements in a Row can be controlled via a combination of `scale` and `min_width` arguments that are present in every Component.

- `scale` is an integer that defines how an element will take up space in a Row. If scale is set to `0`, the element will not expand to take up space. If scale is set to `1` or greater, the element will expand. Multiple elements in a row will expand proportional to their scale. Below, `btn2` will expand twice as much as `btn1`, while `btn0` will not expand at all:

```python
with gr.Blocks() as demo:
    with gr.Row():
        btn0 = gr.Button("Button 0", scale=0)
        btn1 = gr.Button("Button 1", scale=1)
        btn2 = gr.Button("Button 2", scale=2)
```

- `min_width` will set the minimum width the element will take. The Row will wrap if there isn't sufficient space to satisfy all `min_width` values.

Learn more about Rows in the [docs](https://gradio.app/docs/row).

## Columns and Nesting

Components within a Column will be placed vertically atop each other. Since the vertical layout is the default layout for Blocks apps anyway, to be useful, Columns are usually nested within Rows. For example:

$code_rows_and_columns
$demo_rows_and_columns

See how the first column has two Textboxes arranged vertically. The second column has an Image and Button arranged vertically. Notice how the relative widths of the two columns is set by the `scale` parameter. The column with twice the `scale` value takes up twice the width.

Learn more about Columns in the [docs](https://gradio.app/docs/column).

# Fill Browser Height / Width

To make an app take the full width of the browser by removing the side padding, use `gr.Blocks(fill_width=True)`. 

To make top level Components expand to take the full height of the browser, use `fill_height` and apply scale to the expanding Components.

```python
import gradio as gr

with gr.Blocks(fill_height=True) as demo:
    gr.Chatbot(scale=1)
    gr.Textbox(scale=0)
```

## Dimensions

Some components support setting height and width. These parameters accept either a number (interpreted as pixels) or a string. Using a string allows the direct application of any CSS unit to the encapsulating Block element.

Below is an example illustrating the use of viewport width (vw):

```python
import gradio as gr

with gr.Blocks() as demo:
    im = gr.ImageEditor(width="50vw")

demo.launch()
```

## Tabs and Accordions

You can also create Tabs using the `with gr.Tab('tab_name'):` clause. Any component created inside of a `with gr.Tab('tab_name'):` context appears in that tab. Consecutive Tab clauses are grouped together so that a single tab can be selected at one time, and only the components within that Tab's context are shown.

For example:

$code_blocks_flipper
$demo_blocks_flipper

Also note the `gr.Accordion('label')` in this example. The Accordion is a layout that can be toggled open or closed. Like `Tabs`, it is a layout element that can selectively hide or show content. Any components that are defined inside of a `with gr.Accordion('label'):` will be hidden or shown when the accordion's toggle icon is clicked.

Learn more about [Tabs](https://gradio.app/docs/tab) and [Accordions](https://gradio.app/docs/accordion) in the docs.

## Sidebar

The sidebar is a collapsible panel that renders child components on the left side of the screen and can be expanded or collapsed.

For example:

$code_blocks_sidebar

Learn more about [Sidebar](https://gradio.app/docs/gradio/sidebar) in the docs.

## Visibility

Both Components and Layout elements have a `visible` argument that can set initially and also updated. Setting `gr.Column(visible=...)` on a Column can be used to show or hide a set of Components.

$code_blocks_form
$demo_blocks_form

## Defining and Rendering Components Separately

In some cases, you might want to define components before you actually render them in your UI. For instance, you might want to show an examples section using `gr.Examples` above the corresponding `gr.Textbox` input. Since `gr.Examples` requires as a parameter the input component object, you will need to first define the input component, but then render it later, after you have defined the `gr.Examples` object.

The solution to this is to define the `gr.Textbox` outside of the `gr.Blocks()` scope and use the component's `.render()` method wherever you'd like it placed in the UI.

Here's a full code example:

```python
input_textbox = gr.Textbox()

with gr.Blocks() as demo:
    gr.Examples(["hello", "bonjour", "merhaba"], input_textbox)
    input_textbox.render()
```

Similarly, if you have already defined a component in a Gradio app, but wish to unrender it so that you can define in a different part of your application, then you can call the `.unrender()` method. In the following example, the `Textbox` will appear in the third column:

```py
import gradio as gr

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown("Row 1")
            textbox = gr.Textbox()
        with gr.Column():
            gr.Markdown("Row 2")
            textbox.unrender()
        with gr.Column():
            gr.Markdown("Row 3")
            textbox.render()

demo.launch()
```


=== File: guides/03_building-with-blocks/03_state-in-blocks.md ===
# Managing State

When building a Gradio application with `gr.Blocks()`, you may want to share certain values between users (e.g. a count of visitors to your page), or persist values for a single user across certain interactions (e.g. a chat history). This referred to as **state** and there are three general ways to manage state in a Gradio application:

* **Global state**: persist and share values among all users of your Gradio application while your Gradio application is running
* **Session state**: persist values for each user of your Gradio application while they are using your Gradio application in a single session. If they refresh the page, session state will be reset.
* **Browser state**: persist values for each user of your Gradio application in the browser's localStorage, allowing data to persist even after the page is refreshed or closed.

## Global State

Global state in Gradio apps is very simple: any variable created outside of a function is shared globally between all users.

This makes managing global state very simple and without the need for external services. For example, in this application, the `visitor_count` variable is shared between all users

```py
import gradio as gr

# Shared between all users
visitor_count = 0

def increment_counter():
    global visitor_count
    visitor_count += 1
    return visitor_count

with gr.Blocks() as demo:    
    number = gr.Textbox(label="Total Visitors", value="Counting...")
    demo.load(increment_counter, inputs=None, outputs=number)

demo.launch()
```

This means that any time you do _not_ want to share a value between users, you should declare it _within_ a function. But what if you need to share values between function calls, e.g. a chat history? In that case, you should use one of the subsequent approaches to manage state.

## Session State

Gradio supports session state, where data persists across multiple submits within a page session. To reiterate, session data is _not_ shared between different users of your model, and does _not_ persist if a user refreshes the page to reload the Gradio app. To store data in a session state, you need to do three things:

1. Create a `gr.State()` object. If there is a default value to this stateful object, pass that into the constructor. Note that `gr.State` objects must be [deepcopy-able](https://docs.python.org/3/library/copy.html), otherwise you will need to use a different approach as described below.
2. In the event listener, put the `State` object as an input and output as needed.
3. In the event listener function, add the variable to the input parameters and the return value.

Let's take a look at a simple example. We have a simple checkout app below where you add items to a cart. You can also see the size of the cart.

$code_simple_state

Notice how we do this with state:

1. We store the cart items in a `gr.State()` object, initialized here to be an empty list.
2. When adding items to the cart, the event listener uses the cart as both input and output - it returns the updated cart with all the items inside. 
3. We can attach a `.change` listener to cart, that uses the state variable as input as well.

You can think of `gr.State` as an invisible Gradio component that can store any kind of value. Here, `cart` is not visible in the frontend but is used for calculations.

The `.change` listener for a state variable triggers after any event listener changes the value of a state variable. If the state variable holds a sequence (like a `list`, `set`, or `dict`), a change is triggered if any of the elements inside change. If it holds an object or primitive, a change is triggered if the **hash** of the  value changes. So if you define a custom class and create a `gr.State` variable that is an instance of that class, make sure that the the class includes a sensible `__hash__` implementation.

The value of a session State variable is cleared when the user refreshes the page. The value is stored on in the app backend for 60 minutes after the user closes the tab (this can be configured by the `delete_cache` parameter in `gr.Blocks`).

Learn more about `State` in the [docs](https://gradio.app/docs/gradio/state).

**What about objects that cannot be deepcopied?**

As mentioned earlier, the value stored in `gr.State` must be [deepcopy-able](https://docs.python.org/3/library/copy.html). If you are working with a complex object that cannot be deepcopied, you can take a different approach to manually read the user's `session_hash` and store a global `dictionary` with instances of your object for each user. Here's how you would do that:

```py
import gradio as gr

class NonDeepCopyable:
    def __init__(self):
        from threading import Lock
        self.counter = 0
        self.lock = Lock()  # Lock objects cannot be deepcopied
    
    def increment(self):
        with self.lock:
            self.counter += 1
            return self.counter

# Global dictionary to store user-specific instances
instances = {}

def initialize_instance(request: gr.Request):
    instances[request.session_hash] = NonDeepCopyable()
    return "Session initialized!"

def cleanup_instance(request: gr.Request):
    if request.session_hash in instances:
        del instances[request.session_hash]

def increment_counter(request: gr.Request):
    if request.session_hash in instances:
        instance = instances[request.session_hash]
        return instance.increment()
    return "Error: Session not initialized"

with gr.Blocks() as demo:
    output = gr.Textbox(label="Status")
    counter = gr.Number(label="Counter Value")
    increment_btn = gr.Button("Increment Counter")
    increment_btn.click(increment_counter, inputs=None, outputs=counter)
    
    # Initialize instance when page loads
    demo.load(initialize_instance, inputs=None, outputs=output)    
    # Clean up instance when page is closed/refreshed
    demo.unload(cleanup_instance)    

demo.launch()
```

## Browser State

Gradio also supports browser state, where data persists in the browser's localStorage even after the page is refreshed or closed. This is useful for storing user preferences, settings, API keys, or other data that should persist across sessions. To use local state:

1. Create a `gr.BrowserState` object. You can optionally provide an initial default value and a key to identify the data in the browser's localStorage.
2. Use it like a regular `gr.State` component in event listeners as inputs and outputs.

Here's a simple example that saves a user's username and password across sessions:

$code_browserstate

Note: The value stored in `gr.BrowserState` does not persist if the Grado app is restarted. To persist it, you can hardcode specific values of `storage_key` and `secret` in the `gr.BrowserState` component and restart the Gradio app on the same server name and server port. However, this should only be done if you are running trusted Gradio apps, as in principle, this can allow one Gradio app to access localStorage data that was created by a different Gradio app.


=== File: guides/03_building-with-blocks/04_dynamic-apps-with-render-decorator.md ===
# Dynamic Apps with the Render Decorator

The components and event listeners you define in a Blocks so far have been fixed - once the demo was launched, new components and listeners could not be added, and existing one could not be removed. 

The `@gr.render` decorator introduces the ability to dynamically change this. Let's take a look. 

## Dynamic Number of Components

In the example below, we will create a variable number of Textboxes. When the user edits the input Textbox, we create a Textbox for each letter in the input. Try it out below:

$code_render_split_simple
$demo_render_split_simple

See how we can now create a variable number of Textboxes using our custom logic - in this case, a simple `for` loop. The `@gr.render` decorator enables this with the following steps:

1. Create a function and attach the @gr.render decorator to it.
2. Add the input components to the `inputs=` argument of @gr.render, and create a corresponding argument in your function for each component. This function will automatically re-run on any change to a component.
3. Add all components inside the function that you want to render based on the inputs.

Now whenever the inputs change, the function re-runs, and replaces the components created from the previous function run with the latest run. Pretty straightforward! Let's add a little more complexity to this app:

$code_render_split
$demo_render_split

By default, `@gr.render` re-runs are triggered by the `.load` listener to the app and the `.change` listener to any input component provided. We can override this by explicitly setting the triggers in the decorator, as we have in this app to only trigger on `input_text.submit` instead. 
If you are setting custom triggers, and you also want an automatic render at the start of the app, make sure to add `demo.load` to your list of triggers.

## Dynamic Event Listeners

If you're creating components, you probably want to attach event listeners to them as well. Let's take a look at an example that takes in a variable number of Textbox as input, and merges all the text into a single box.

$code_render_merge_simple
$demo_render_merge_simple

Let's take a look at what's happening here:

1. The state variable `text_count` is keeping track of the number of Textboxes to create. By clicking on the Add button, we increase `text_count` which triggers the render decorator.
2. Note that in every single Textbox we create in the render function, we explicitly set a `key=` argument. This key allows us to preserve the value of this Component between re-renders. If you type in a value in a textbox, and then click the Add button, all the Textboxes re-render, but their values aren't cleared because the `key=` maintains the the value of a Component across a render.
3. We've stored the Textboxes created in a list, and provide this list as input to the merge button event listener. Note that **all event listeners that use Components created inside a render function must also be defined inside that render function**. The event listener can still reference Components outside the render function, as we do here by referencing `merge_btn` and `output` which are both defined outside the render function.

Just as with Components, whenever a function re-renders, the event listeners created from the previous render are cleared and the new event listeners from the latest run are attached. 

This allows us to create highly customizable and complex interactions! 

## Closer Look at `keys=` parameter

The `key=` argument is used to let Gradio know that the same component is being generated when your render function re-runs. This does two things:

1. The same element in the browser is re-used from the previous render for this Component. This gives browser performance gains - as there's no need to destroy and rebuild a component on a render - and preserves any browser attributes that the Component may have had. If your Component is nested within layout items like `gr.Row`, make sure they are keyed as well because the keys of the parents must also match.
2. Properties that may be changed by the user or by other event listeners are preserved. By default, only the "value" of Component is preserved, but you can specify any list of properties to preserve using the `preserved_by_key=` kwarg.

See the example below:

$code_render_preserve_key
$demo_render_preserve_key

You'll see in this example, when you change the `number_of_boxes` slider, there's a new re-render to update the number of box rows. If you click the "Change Label" buttons, they change the `label` and `info` properties of the corresponding textbox. You can also enter text in any textbox to change its value. If you change number of boxes after this, the re-renders "reset" the `info`, but the `label` and any entered `value` is still preserved.

Note you can also key any event listener, e.g. `button.click(key=...)` if the same listener is being recreated with the same inputs and outputs across renders. This gives performance benefits, and also prevents errors from occuring if an event was triggered in a previous render, then a re-render occurs, and then the previous event finishes processing. By keying your listener, Gradio knows where to send the data properly. 

## Putting it Together

Let's look at two examples that use all the features above. First, try out the to-do list app below: 

$code_todo_list
$demo_todo_list

Note that almost the entire app is inside a single `gr.render` that reacts to the tasks `gr.State` variable. This variable is a nested list, which presents some complexity. If you design a `gr.render` to react to a list or dict structure, ensure you do the following:

1. Any event listener that modifies a state variable in a manner that should trigger a re-render must set the state variable as an output. This lets Gradio know to check if the variable has changed behind the scenes. 
2. In a `gr.render`, if a variable in a loop is used inside an event listener function, that variable should be "frozen" via setting it to itself as a default argument in the function header. See how we have `task=task` in both `mark_done` and `delete`. This freezes the variable to its "loop-time" value.

Let's take a look at one last example that uses everything we learned. Below is an audio mixer. Provide multiple audio tracks and mix them together.

$code_audio_mixer
$demo_audio_mixer

Two things to note in this app:
1. Here we provide `key=` to all the components! We need to do this so that if we add another track after setting the values for an existing track, our input values to the existing track do not get reset on re-render.
2. When there are lots of components of different types and arbitrary counts passed to an event listener, it is easier to use the set and dictionary notation for inputs rather than list notation. Above, we make one large set of all the input `gr.Audio` and `gr.Slider` components when we pass the inputs to the `merge` function. In the function body we query the component values as a dict.

The `gr.render` expands gradio capabilities extensively - see what you can make out of it! 


=== File: guides/03_building-with-blocks/05_more-blocks-features ===
# More Blocks Features

## Examples

Just like with `gr.Interface`, you can also add examples for your functions when you are working with `gr.Blocks`. In this case, instantiate a `gr.Examples` similar to how you would instantiate any other component. The constructor of `gr.Examples` takes two required arguments:

* `examples`: a nested list of examples, in which the outer list consists of examples and each inner list consists of an input corresponding to each input component
* `inputs`: the component or list of components that should be populated when the examples are clicked

You can also set `cache_examples=True` or `cache_examples='lazy'`, similar to [the caching API in `gr.Interface`](https://www.gradio.app/guides/more-on-examples), in which case two additional arguments must be provided:

* `outputs`: the component or list of components corresponding to the output of the examples
* `fn`: the function to run to generate the outputs corresponding to the examples

Here's an example showing how to use `gr.Examples` in a `gr.Blocks` app:

$code_calculator_blocks
$demo_calculator_blocks

**Note**: When you click on examples, not only does the value of the input component update to the example value, but the component's configuration also reverts to the properties with which you constructed the component. This ensures that the examples are compatible with the component even if its configuration has been changed. 

## Running Events Continuously

You can run events on a fixed schedule using `gr.Timer()` object. This will run the event when the timer's `tick` event fires. See the code below:

```python
with gr.Blocks as demo:
    timer = gr.Timer(5)
    textbox = gr.Textbox()
    textbox2 = gr.Textbox()
    timer.tick(set_textbox_fn, textbox, textbox2)
```

This can also be used directly with a Component's `every=` parameter, if the value of the Component is a function:

```python
with gr.Blocks as demo:
    timer = gr.Timer(5)
    textbox = gr.Textbox()
    textbox2 = gr.Textbox(set_textbox_fn, inputs=[textbox], every=timer)
```

Here is an example of a demo that print the current timestamp, and also prints random numbers regularly!

$code_timer_simple
$demo_timer_simple

## Gathering Event Data

You can gather specific data about an event by adding the associated event data class as a type hint to an argument in the event listener function.

For example, event data for `.select()` can be type hinted by a `gradio.SelectData` argument. This event is triggered when a user selects some part of the triggering component, and the event data includes information about what the user specifically selected. For example, if a user selected a specific word in a `Textbox`, a specific pixel in an `Image`, a specific image in a `Gallery`, or a specific cell in a `DataFrame`, the event data argument would contain information about the specific selection.

The `SelectData` includes the value that was selected, and the index where the selection occurred. A simple example that shows what text was selected in a `Textbox`. 

```python
import gradio as gr

with gr.Blocks() as demo:
    textbox = gr.Textbox("The quick brown fox jumped.")
    selection = gr.Textbox()
    
    def get_selection(select_evt: gr.SelectData):
        return select_evt.value

    textbox.select(get_selection, None, selection)
```

In the  2 player tic-tac-toe demo below, a user can select a cell in the `DataFrame` to make a move. The event data argument contains information about the specific cell that was selected. We can first check to see if the cell is empty, and then update the cell with the user's move.

$code_tictactoe
$demo_tictactoe


=== File: guides/03_building-with-blocks/06_custom-CSS-and-JS.md ===
# Customizing your demo with CSS and Javascript

Gradio allows you to customize your demo in several ways. You can customize the layout of your demo, add custom HTML, and add custom theming as well. This tutorial will go beyond that and walk you through how to add custom CSS and JavaScript code to your demo in order to add custom styling, animations, custom UI functionality, analytics, and more.

## Adding custom CSS to your demo

Gradio themes are the easiest way to customize the look and feel of your app. You can choose from a variety of themes, or create your own. To do so, pass the `theme=` kwarg to the `Blocks` constructor. For example:

```python
with gr.Blocks(theme=gr.themes.Glass()):
    ...
```

Gradio comes with a set of prebuilt themes which you can load from `gr.themes.*`. You can extend these themes or create your own themes from scratch - see the [Theming guide](/guides/theming-guide) for more details.

For additional styling ability, you can pass any CSS to your app as a string using the `css=` kwarg. You can also pass a pathlib.Path to a css file or a list of such paths to the `css_paths=` kwarg.

**Warning**: The use of query selectors in custom JS and CSS is _not_ guaranteed to work across Gradio versions that bind to Gradio's own HTML elements as the Gradio HTML DOM may change. We recommend using query selectors sparingly.

The base class for the Gradio app is `gradio-container`, so here's an example that changes the background color of the Gradio app:

```python
with gr.Blocks(css=".gradio-container {background-color: red}") as demo:
    ...
```

If you'd like to reference external files in your css, preface the file path (which can be a relative or absolute path) with `"/gradio_api/file="`, for example:

```python
with gr.Blocks(css=".gradio-container {background: url('/gradio_api/file=clouds.jpg')}") as demo:
    ...
```

Note: By default, most files in the host machine are not accessible to users running the Gradio app. As a result, you should make sure that any referenced files (such as `clouds.jpg` here) are either URLs or [allowed paths, as described here](/main/guides/file-access).


## The `elem_id` and `elem_classes` Arguments

You can `elem_id` to add an HTML element `id` to any component, and `elem_classes` to add a class or list of classes. This will allow you to select elements more easily with CSS. This approach is also more likely to be stable across Gradio versions as built-in class names or ids may change (however, as mentioned in the warning above, we cannot guarantee complete compatibility between Gradio versions if you use custom CSS as the DOM elements may themselves change).

```python
css = """
#warning {background-color: #FFCCCB}
.feedback textarea {font-size: 24px !important}
"""

with gr.Blocks(css=css) as demo:
    box1 = gr.Textbox(value="Good Job", elem_classes="feedback")
    box2 = gr.Textbox(value="Failure", elem_id="warning", elem_classes="feedback")
```

The CSS `#warning` ruleset will only target the second Textbox, while the `.feedback` ruleset will target both. Note that when targeting classes, you might need to put the `!important` selector to override the default Gradio styles.

## Adding custom JavaScript to your demo

There are 3 ways to add javascript code to your Gradio demo:

1. You can add JavaScript code as a string to the `js` parameter of the `Blocks` or `Interface` initializer. This will run the JavaScript code when the demo is first loaded.

Below is an example of adding custom js to show an animated welcome message when the demo first loads.

$code_blocks_js_load
$demo_blocks_js_load


2. When using `Blocks` and event listeners, events have a `js` argument that can take a JavaScript function as a string and treat it just like a Python event listener function. You can pass both a JavaScript function and a Python function (in which case the JavaScript function is run first) or only Javascript (and set the Python `fn` to `None`). Take a look at the code below:
   
$code_blocks_js_methods
$demo_blocks_js_methods

3. Lastly, you can add JavaScript code to the `head` param of the `Blocks` initializer. This will add the code to the head of the HTML document. For example, you can add Google Analytics to your demo like so:


```python
head = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={google_analytics_tracking_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{google_analytics_tracking_id}');
</script>
"""

with gr.Blocks(head=head) as demo:
    gr.HTML("<h1>My App</h1>")

demo.launch()
```

The `head` parameter accepts any HTML tags you would normally insert into the `<head>` of a page. For example, you can also include `<meta>` tags to `head` in order to update the social sharing preview for your Gradio app like this:

```py
import gradio as gr

custom_head = """
<!-- HTML Meta Tags -->
<title>Sample App</title>
<meta name="description" content="An open-source web application showcasing various features and capabilities.">

<!-- Facebook Meta Tags -->
<meta property="og:url" content="https://example.com">
<meta property="og:type" content="website">
<meta property="og:title" content="Sample App">
<meta property="og:description" content="An open-source web application showcasing various features and capabilities.">
<meta property="og:image" content="https://cdn.britannica.com/98/152298-050-8E45510A/Cheetah.jpg">

<!-- Twitter Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:creator" content="@example_user">
<meta name="twitter:title" content="Sample App">
<meta name="twitter:description" content="An open-source web application showcasing various features and capabilities.">
<meta name="twitter:image" content="https://cdn.britannica.com/98/152298-050-8E45510A/Cheetah.jpg">
<meta property="twitter:domain" content="example.com">
<meta property="twitter:url" content="https://example.com">  
"""

with gr.Blocks(title="My App", head=custom_head) as demo:
    gr.HTML("<h1>My App</h1>")

demo.launch()
```



Note that injecting custom JS can affect browser behavior and accessibility (e.g. keyboard shortcuts may be lead to unexpected behavior if your Gradio app is embedded in another webpage). You should test your interface across different browsers and be mindful of how scripts may interact with browser defaults. Here's an example where pressing `Shift + s` triggers the `click` event of a specific `Button` component if the browser focus is _not_ on an input component (e.g. `Textbox` component):

```python
import gradio as gr

shortcut_js = """
<script>
function shortcuts(e) {
    var event = document.all ? window.event : e;
    switch (e.target.tagName.toLowerCase()) {
        case "input":
        case "textarea":
        break;
        default:
        if (e.key.toLowerCase() == "s" && e.shiftKey) {
            document.getElementById("my_btn").click();
        }
    }
}
document.addEventListener('keypress', shortcuts, false);
</script>
"""

with gr.Blocks(head=shortcut_js) as demo:
    action_button = gr.Button(value="Name", elem_id="my_btn")
    textbox = gr.Textbox()
    action_button.click(lambda : "button pressed", None, textbox)
    
demo.launch()
```



=== File: guides/03_building-with-blocks/07_using-blocks-like-functions.md ===
# Using Gradio Blocks Like Functions

Tags: TRANSLATION, HUB, SPACES

**Prerequisite**: This Guide builds on the Blocks Introduction. Make sure to [read that guide first](https://gradio.app/blocks-and-event-listeners).

## Introduction

Did you know that apart from being a full-stack machine learning demo, a Gradio Blocks app is also a regular-old python function!?

This means that if you have a gradio Blocks (or Interface) app called `demo`, you can use `demo` like you would any python function.

So doing something like `output = demo("Hello", "friend")` will run the first event defined in `demo` on the inputs "Hello" and "friend" and store it
in the variable `output`.

If I put you to sleep 🥱, please bear with me! By using apps like functions, you can seamlessly compose Gradio apps.
The following section will show how.

## Treating Blocks like functions

Let's say we have the following demo that translates english text to german text.

$code_english_translator

I already went ahead and hosted it in Hugging Face spaces at [gradio/english_translator](https://huggingface.co/spaces/gradio/english_translator).

You can see the demo below as well:

$demo_english_translator

Now, let's say you have an app that generates english text, but you wanted to additionally generate german text.

You could either:

1. Copy the source code of my english-to-german translation and paste it in your app.

2. Load my english-to-german translation in your app and treat it like a normal python function.

Option 1 technically always works, but it often introduces unwanted complexity.

Option 2 lets you borrow the functionality you want without tightly coupling our apps.

All you have to do is call the `Blocks.load` class method in your source file.
After that, you can use my translation app like a regular python function!

The following code snippet and demo shows how to use `Blocks.load`.

Note that the variable `english_translator` is my english to german app, but its used in `generate_text` like a regular function.

$code_generate_english_german

$demo_generate_english_german

## How to control which function in the app to use

If the app you are loading defines more than one function, you can specify which function to use
with the `fn_index` and `api_name` parameters.

In the code for our english to german demo, you'll see the following line:

```python
translate_btn.click(translate, inputs=english, outputs=german, api_name="translate-to-german")
```

The `api_name` gives this function a unique name in our app. You can use this name to tell gradio which
function in the upstream space you want to use:

```python
english_generator(text, api_name="translate-to-german")[0]["generated_text"]
```

You can also use the `fn_index` parameter.
Imagine my app also defined an english to spanish translation function.
In order to use it in our text generation app, we would use the following code:

```python
english_generator(text, fn_index=1)[0]["generated_text"]
```

Functions in gradio spaces are zero-indexed, so since the spanish translator would be the second function in my space,
you would use index 1.

## Parting Remarks

We showed how treating a Blocks app like a regular python helps you compose functionality across different apps.
Any Blocks app can be treated like a function, but a powerful pattern is to `load` an app hosted on
[Hugging Face Spaces](https://huggingface.co/spaces) prior to treating it like a function in your own app.
You can also load models hosted on the [Hugging Face Model Hub](https://huggingface.co/models) - see the [Using Hugging Face Integrations](/using_hugging_face_integrations) guide for an example.

Happy building! ⚒️


=== File: guides/04_additional-features/01_queuing.md ===
# Queuing

Every Gradio app comes with a built-in queuing system that can scale to thousands of concurrent users. Because many of your event listeners may involve heavy processing, Gradio automatically creates a queue to handle every event listener in the backend. Every event listener in your app automatically has a queue to process incoming events.

## Configuring the Queue

By default, each event listener has its own queue, which handles one request at a time. This can be configured via two arguments:

- `concurrency_limit`: This sets the maximum number of concurrent executions for an event listener. By default, the limit is 1 unless configured otherwise in `Blocks.queue()`. You can also set it to `None` for no limit (i.e., an unlimited number of concurrent executions). For example:

```python
import gradio as gr

with gr.Blocks() as demo:
    prompt = gr.Textbox()
    image = gr.Image()
    generate_btn = gr.Button("Generate Image")
    generate_btn.click(image_gen, prompt, image, concurrency_limit=5)
```

In the code above, up to 5 requests can be processed simultaneously for this event listener. Additional requests will be queued until a slot becomes available.

If you want to manage multiple event listeners using a shared queue, you can use the `concurrency_id` argument:

- `concurrency_id`: This allows event listeners to share a queue by assigning them the same ID. For example, if your setup has only 2 GPUs but multiple functions require GPU access, you can create a shared queue for all those functions. Here's how that might look:

```python
import gradio as gr

with gr.Blocks() as demo:
    prompt = gr.Textbox()
    image = gr.Image()
    generate_btn_1 = gr.Button("Generate Image via model 1")
    generate_btn_2 = gr.Button("Generate Image via model 2")
    generate_btn_3 = gr.Button("Generate Image via model 3")
    generate_btn_1.click(image_gen_1, prompt, image, concurrency_limit=2, concurrency_id="gpu_queue")
    generate_btn_2.click(image_gen_2, prompt, image, concurrency_id="gpu_queue")
    generate_btn_3.click(image_gen_3, prompt, image, concurrency_id="gpu_queue")
```

In this example, all three event listeners share a queue identified by `"gpu_queue"`. The queue can handle up to 2 concurrent requests at a time, as defined by the `concurrency_limit`.

### Notes

- To ensure unlimited concurrency for an event listener, set `concurrency_limit=None`.  This is useful if your function is calling e.g. an external API which handles the rate limiting of requests itself.
- The default concurrency limit for all queues can be set globally using the `default_concurrency_limit` parameter in `Blocks.queue()`. 

These configurations make it easy to manage the queuing behavior of your Gradio app.


=== File: guides/04_additional-features/02_streaming-outputs.md ===
# Streaming outputs

In some cases, you may want to stream a sequence of outputs rather than show a single output at once. For example, you might have an image generation model and you want to show the image that is generated at each step, leading up to the final image. Or you might have a chatbot which streams its response one token at a time instead of returning it all at once.

In such cases, you can supply a **generator** function into Gradio instead of a regular function. Creating generators in Python is very simple: instead of a single `return` value, a function should `yield` a series of values instead. Usually the `yield` statement is put in some kind of loop. Here's an example of an generator that simply counts up to a given number:

```python
def my_generator(x):
    for i in range(x):
        yield i
```

You supply a generator into Gradio the same way as you would a regular function. For example, here's a a (fake) image generation model that generates noise for several steps before outputting an image using the `gr.Interface` class:

$code_fake_diffusion
$demo_fake_diffusion

Note that we've added a `time.sleep(1)` in the iterator to create an artificial pause between steps so that you are able to observe the steps of the iterator (in a real image generation model, this probably wouldn't be necessary).

Similarly, Gradio can handle streaming inputs, e.g. an image generation model that reruns every time a user types a letter in a textbox. This is covered in more details in our guide on building [reactive Interfaces](/guides/reactive-interfaces). 

## Streaming Media

Gradio can stream audio and video directly from your generator function.
This lets your user hear your audio or see your video nearly as soon as it's `yielded` by your function.
All you have to do is 

1. Set `streaming=True` in your `gr.Audio` or `gr.Video` output component.
2. Write a python generator that yields the next "chunk" of audio or video.
3. Set `autoplay=True` so that the media starts playing automatically.

For audio, the next "chunk" can be either an `.mp3` or `.wav` file or a `bytes` sequence of audio.
For video, the next "chunk" has to be either `.mp4` file or a file with `h.264` codec with a `.ts` extension.
For smooth playback, make sure chunks are consistent lengths and larger than 1 second.

We'll finish with some simple examples illustrating these points.

### Streaming Audio

```python
import gradio as gr
from time import sleep

def keep_repeating(audio_file):
    for _ in range(10):
        sleep(0.5)
        yield audio_file

gr.Interface(keep_repeating,
             gr.Audio(sources=["microphone"], type="filepath"),
             gr.Audio(streaming=True, autoplay=True)
).launch()
```

### Streaming Video

```python
import gradio as gr
from time import sleep

def keep_repeating(video_file):
    for _ in range(10):
        sleep(0.5)
        yield video_file

gr.Interface(keep_repeating,
             gr.Video(sources=["webcam"], format="mp4"),
             gr.Video(streaming=True, autoplay=True)
).launch()
```

## End-to-End Examples

For an end-to-end example of streaming media, see the object detection from video [guide](/main/guides/object-detection-from-video) or the streaming AI-generated audio with [transformers](https://huggingface.co/docs/transformers/index) [guide](/main/guides/streaming-ai-generated-audio).

=== File: guides/04_additional-features/03_streaming-inputs.md ===
# Streaming inputs

In the previous guide, we covered how to stream a sequence of outputs from an event handler. Gradio also allows you to stream images from a user's camera or audio chunks from their microphone **into** your event handler. This can be used to create real-time object detection apps or conversational chat applications with Gradio.

Currently, the `gr.Image` and the `gr.Audio` components support input streaming via the `stream` event.
Let's create the simplest streaming app possible, which simply returns the webcam stream unmodified.

$code_streaming_simple
$demo_streaming_simple

Try it out! The streaming event is triggered when the user starts recording. Under the hood, the webcam will take a photo every 0.1 seconds and send it to the server. The server will then return that image.

There are two unique keyword arguments for the `stream` event:

* `time_limit` - This is the amount of time the gradio server will spend processing the event. Media streams are naturally unbounded so it's important to set a time limit so that one user does not hog the Gradio queue. The time limit only counts the time spent processing the stream, not the time spent waiting in the queue. The orange bar displayed at the bottom of the input image represents the remaining time. When the time limit expires, the user will automatically rejoin the queue.

* `stream_every` - This is the frequency (in seconds) with which the stream will capture input and send it to the server. For demos like image detection or manipulation, setting a smaller value is desired to get a "real-time" effect. For demos like speech transcription, a higher value is useful so that the transcription algorithm has more context of what's being said.

## A Realistic Image Demo

Let's create a demo where a user can choose a filter to apply to their webcam stream. Users can choose from an edge-detection filter, a cartoon filter, or simply flipping the stream vertically.

$code_streaming_filter
$demo_streaming_filter

You will notice that if you change the filter value it will immediately take effect in the output stream. That is an important difference of stream events in comparison to other Gradio events. The input values of the stream can be changed while the stream is being processed. 

Tip: We set the "streaming" parameter of the image output component to be "True". Doing so lets the server automatically convert our output images into base64 format, a format that is efficient for streaming.

## Unified Image Demos

For some image streaming demos, like the one above, we don't need to display separate input and output components. Our app would look cleaner if we could just display the modified output stream.

We can do so by just specifying the input image component as the output of the stream event.

$code_streaming_filter_unified
$demo_streaming_filter_unified

## Keeping track of past inputs or outputs

Your streaming function should be stateless. It should take the current input and return its corresponding output. However, there are cases where you may want to keep track of past inputs or outputs. For example, you may want to keep a buffer of the previous `k` inputs to improve the accuracy of your transcription demo. You can do this with Gradio's `gr.State()` component.

Let's showcase this with a sample demo:

```python
def transcribe_handler(current_audio, state, transcript):
    next_text = transcribe(current_audio, history=state)
    state.append(current_audio)
    state = state[-3:]
    return state, transcript + next_text

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            mic = gr.Audio(sources="microphone")
            state = gr.State(value=[])
        with gr.Column():
            transcript = gr.Textbox(label="Transcript")
    mic.stream(transcribe_handler, [mic, state, transcript], [state, transcript],
               time_limit=10, stream_every=1)


demo.launch()
```

## End-to-End Examples

For an end-to-end example of streaming from the webcam, see the object detection from webcam [guide](/main/guides/object-detection-from-webcam-with-webrtc).

=== File: guides/04_additional-features/04_alerts.md ===
# Alerts

You may wish to display alerts to the user. To do so, raise a `gr.Error("custom message")` in your function to halt the execution of your function and display an error message to the user.

You can also issue `gr.Warning("custom message")` or `gr.Info("custom message")` by having them as standalone lines in your function, which will immediately display modals while continuing the execution of your function. The only difference between `gr.Info()` and `gr.Warning()` is the color of the alert. 

```python
def start_process(name):
    gr.Info("Starting process")
    if name is None:
        gr.Warning("Name is empty")
    ...
    if success == False:
        raise gr.Error("Process failed")
```

Tip: Note that `gr.Error()` is an exception that has to be raised, while `gr.Warning()` and `gr.Info()` are functions that are called directly.



=== File: guides/04_additional-features/05_progress-bars.md ===
# Progress Bars

Gradio supports the ability to create custom Progress Bars so that you have customizability and control over the progress update that you show to the user. In order to enable this, simply add an argument to your method that has a default value of a `gr.Progress` instance. Then you can update the progress levels by calling this instance directly with a float between 0 and 1, or using the `tqdm()` method of the `Progress` instance to track progress over an iterable, as shown below.

$code_progress_simple
$demo_progress_simple

If you use the `tqdm` library, you can even report progress updates automatically from any `tqdm.tqdm` that already exists within your function by setting the default argument as `gr.Progress(track_tqdm=True)`!


=== File: guides/04_additional-features/06_batch-functions.md ===
# Batch functions

Gradio supports the ability to pass _batch_ functions. Batch functions are just
functions which take in a list of inputs and return a list of predictions.

For example, here is a batched function that takes in two lists of inputs (a list of
words and a list of ints), and returns a list of trimmed words as output:

```py
import time

def trim_words(words, lens):
    trimmed_words = []
    time.sleep(5)
    for w, l in zip(words, lens):
        trimmed_words.append(w[:int(l)])
    return [trimmed_words]
```

The advantage of using batched functions is that if you enable queuing, the Gradio server can automatically _batch_ incoming requests and process them in parallel,
potentially speeding up your demo. Here's what the Gradio code looks like (notice the `batch=True` and `max_batch_size=16`)

With the `gr.Interface` class:

```python
demo = gr.Interface(
    fn=trim_words, 
    inputs=["textbox", "number"], 
    outputs=["output"],
    batch=True, 
    max_batch_size=16
)

demo.launch()
```

With the `gr.Blocks` class:

```py
import gradio as gr

with gr.Blocks() as demo:
    with gr.Row():
        word = gr.Textbox(label="word")
        leng = gr.Number(label="leng")
        output = gr.Textbox(label="Output")
    with gr.Row():
        run = gr.Button()

    event = run.click(trim_words, [word, leng], output, batch=True, max_batch_size=16)

demo.launch()
```

In the example above, 16 requests could be processed in parallel (for a total inference time of 5 seconds), instead of each request being processed separately (for a total
inference time of 80 seconds). Many Hugging Face `transformers` and `diffusers` models work very naturally with Gradio's batch mode: here's [an example demo using diffusers to
generate images in batches](https://github.com/gradio-app/gradio/blob/main/demo/diffusers_with_batching/run.py)




=== File: guides/04_additional-features/07_sharing-your-app.md ===
# Sharing Your App

In this Guide, we dive more deeply into the various aspects of sharing a Gradio app with others. We will cover:

1. [Sharing demos with the share parameter](#sharing-demos)
2. [Hosting on HF Spaces](#hosting-on-hf-spaces)
3. [Sharing Deep Links](#sharing-deep-links)
4. [Embedding hosted spaces](#embedding-hosted-spaces)
5. [Using the API page](#api-page)
6. [Accessing network requests](#accessing-the-network-request-directly)
7. [Mounting within FastAPI](#mounting-within-another-fast-api-app)
8. [Authentication](#authentication)
9. [Analytics](#analytics)
10. [Progressive Web Apps (PWAs)](#progressive-web-app-pwa)

## Sharing Demos

Gradio demos can be easily shared publicly by setting `share=True` in the `launch()` method. Like this:

```python
import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")

demo.launch(share=True)  # Share your demo with just 1 extra parameter 🚀
```

This generates a public, shareable link that you can send to anybody! When you send this link, the user on the other side can try out the model in their browser. Because the processing happens on your device (as long as your device stays on), you don't have to worry about any packaging any dependencies.

![sharing](https://github.com/gradio-app/gradio/blob/main/guides/assets/sharing.svg?raw=true)


A share link usually looks something like this: **https://07ff8706ab.gradio.live**. Although the link is served through the Gradio Share Servers, these servers are only a proxy for your local server, and do not store any data sent through your app. Share links expire after 1 week. (it is [also possible to set up your own Share Server](https://github.com/huggingface/frp/) on your own cloud server to overcome this restriction.)

Tip: Keep in mind that share links are publicly accessible, meaning that anyone can use your model for prediction! Therefore, make sure not to expose any sensitive information through the functions you write, or allow any critical changes to occur on your device. Or you can [add authentication to your Gradio app](#authentication) as discussed below.

Note that by default, `share=False`, which means that your server is only running locally. (This is the default, except in Google Colab notebooks, where share links are automatically created). As an alternative to using share links, you can use use [SSH port-forwarding](https://www.ssh.com/ssh/tunneling/example) to share your local server with specific users.


## Hosting on HF Spaces

If you'd like to have a permanent link to your Gradio demo on the internet, use Hugging Face Spaces. [Hugging Face Spaces](http://huggingface.co/spaces/) provides the infrastructure to permanently host your machine learning model for free!

After you have [created a free Hugging Face account](https://huggingface.co/join), you have two methods to deploy your Gradio app to Hugging Face Spaces:

1. From terminal: run `gradio deploy` in your app directory. The CLI will gather some basic metadata and then launch your app. To update your space, you can re-run this command or enable the Github Actions option to automatically update the Spaces on `git push`.

2. From your browser: Drag and drop a folder containing your Gradio model and all related files [here](https://huggingface.co/new-space). See [this guide how to host on Hugging Face Spaces](https://huggingface.co/blog/gradio-spaces) for more information, or watch the embedded video:

<video autoplay muted loop>
  <source src="https://github.com/gradio-app/gradio/blob/main/guides/assets/hf_demo.mp4?raw=true" type="video/mp4" />
</video>

## Sharing Deep Links

You can add a button to your Gradio app that creates a unique URL you can use to share your app and all components **as they currently are** with others. This is useful for sharing unique and interesting generations from your application , or for saving a snapshot of your app at a particular point in time.

To add a deep link button to your app, place the `gr.DeepLinkButton` component anywhere in your app.
For the URL to be accessible to others, your app must be available at a public URL. So be sure to host your app like Hugging Face Spaces or use the `share=True` parameter when launching your app.

Let's see an example of how this works. Here's a simple Gradio chat ap that uses the `gr.DeepLinkButton` component. After a couple of messages, click the deep link button and paste it into a new browser tab to see the app as it is at that point in time.

$code_deep_link
$demo_deep_link


## Embedding Hosted Spaces

Once you have hosted your app on Hugging Face Spaces (or on your own server), you may want to embed the demo on a different website, such as your blog or your portfolio. Embedding an interactive demo allows people to try out the machine learning model that you have built, without needing to download or install anything — right in their browser! The best part is that you can embed interactive demos even in static websites, such as GitHub pages.

There are two ways to embed your Gradio demos. You can find quick links to both options directly on the Hugging Face Space page, in the "Embed this Space" dropdown option:

![Embed this Space dropdown option](https://github.com/gradio-app/gradio/blob/main/guides/assets/embed_this_space.png?raw=true)

### Embedding with Web Components

Web components typically offer a better experience to users than IFrames. Web components load lazily, meaning that they won't slow down the loading time of your website, and they automatically adjust their height based on the size of the Gradio app.

To embed with Web Components:

1. Import the gradio JS library into into your site by adding the script below in your site (replace {GRADIO_VERSION} in the URL with the library version of Gradio you are using).

```html
<script
	type="module"
	src="https://gradio.s3-us-west-2.amazonaws.com/{GRADIO_VERSION}/gradio.js"
></script>
```

2. Add

```html
<gradio-app src="https://$your_space_host.hf.space"></gradio-app>
```

element where you want to place the app. Set the `src=` attribute to your Space's embed URL, which you can find in the "Embed this Space" button. For example:

```html
<gradio-app
	src="https://abidlabs-pytorch-image-classifier.hf.space"
></gradio-app>
```

<script>
fetch("https://pypi.org/pypi/gradio/json"
).then(r => r.json()
).then(obj => {
    let v = obj.info.version;
    content = document.querySelector('.prose');
    content.innerHTML = content.innerHTML.replaceAll("{GRADIO_VERSION}", v);
});
</script>

You can see examples of how web components look <a href="https://www.gradio.app">on the Gradio landing page</a>.

You can also customize the appearance and behavior of your web component with attributes that you pass into the `<gradio-app>` tag:

- `src`: as we've seen, the `src` attributes links to the URL of the hosted Gradio demo that you would like to embed
- `space`: an optional shorthand if your Gradio demo is hosted on Hugging Face Space. Accepts a `username/space_name` instead of a full URL. Example: `gradio/Echocardiogram-Segmentation`. If this attribute attribute is provided, then `src` does not need to be provided.
- `control_page_title`: a boolean designating whether the html title of the page should be set to the title of the Gradio app (by default `"false"`)
- `initial_height`: the initial height of the web component while it is loading the Gradio app, (by default `"300px"`). Note that the final height is set based on the size of the Gradio app.
- `container`: whether to show the border frame and information about where the Space is hosted (by default `"true"`)
- `info`: whether to show just the information about where the Space is hosted underneath the embedded app (by default `"true"`)
- `autoscroll`: whether to autoscroll to the output when prediction has finished (by default `"false"`)
- `eager`: whether to load the Gradio app as soon as the page loads (by default `"false"`)
- `theme_mode`: whether to use the `dark`, `light`, or default `system` theme mode (by default `"system"`)
- `render`: an event that is triggered once the embedded space has finished rendering.

Here's an example of how to use these attributes to create a Gradio app that does not lazy load and has an initial height of 0px.

```html
<gradio-app
	space="gradio/Echocardiogram-Segmentation"
	eager="true"
	initial_height="0px"
></gradio-app>
```

Here's another example of how to use the `render` event. An event listener is used to capture the `render` event and will call the `handleLoadComplete()` function once rendering is complete.

```html
<script>
	function handleLoadComplete() {
		console.log("Embedded space has finished rendering");
	}

	const gradioApp = document.querySelector("gradio-app");
	gradioApp.addEventListener("render", handleLoadComplete);
</script>
```

_Note: While Gradio's CSS will never impact the embedding page, the embedding page can affect the style of the embedded Gradio app. Make sure that any CSS in the parent page isn't so general that it could also apply to the embedded Gradio app and cause the styling to break. Element selectors such as `header { ... }` and `footer { ... }` will be the most likely to cause issues._

### Embedding with IFrames

To embed with IFrames instead (if you cannot add javascript to your website, for example), add this element:

```html
<iframe src="https://$your_space_host.hf.space"></iframe>
```

Again, you can find the `src=` attribute to your Space's embed URL, which you can find in the "Embed this Space" button.

Note: if you use IFrames, you'll probably want to add a fixed `height` attribute and set `style="border:0;"` to remove the boreder. In addition, if your app requires permissions such as access to the webcam or the microphone, you'll need to provide that as well using the `allow` attribute.

## API Page

You can use almost any Gradio app as an API! In the footer of a Gradio app [like this one](https://huggingface.co/spaces/gradio/hello_world), you'll see a "Use via API" link.

![Use via API](https://github.com/gradio-app/gradio/blob/main/guides/assets/use_via_api.png?raw=true)

This is a page that lists the endpoints that can be used to query the Gradio app, via our supported clients: either [the Python client](https://gradio.app/guides/getting-started-with-the-python-client/), or [the JavaScript client](https://gradio.app/guides/getting-started-with-the-js-client/). For each endpoint, Gradio automatically generates the parameters and their types, as well as example inputs, like this.

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/view-api.png)

The endpoints are automatically created when you launch a Gradio application. If you are using Gradio `Blocks`, you can also name each event listener, such as

```python
btn.click(add, [num1, num2], output, api_name="addition")
```

This will add and document the endpoint `/addition/` to the automatically generated API page. Read more about the [API page here](./view-api-page).

## Accessing the Network Request Directly

When a user makes a prediction to your app, you may need the underlying network request, in order to get the request headers (e.g. for advanced authentication), log the client's IP address, getting the query parameters, or for other reasons. Gradio supports this in a similar manner to FastAPI: simply add a function parameter whose type hint is `gr.Request` and Gradio will pass in the network request as that parameter. Here is an example:

```python
import gradio as gr

def echo(text, request: gr.Request):
    if request:
        print("Request headers dictionary:", request.headers)
        print("IP address:", request.client.host)
        print("Query parameters:", dict(request.query_params))
    return text

io = gr.Interface(echo, "textbox", "textbox").launch()
```

Note: if your function is called directly instead of through the UI (this happens, for
example, when examples are cached, or when the Gradio app is called via API), then `request` will be `None`.
You should handle this case explicitly to ensure that your app does not throw any errors. That is why
we have the explicit check `if request`.

## Mounting Within Another FastAPI App

In some cases, you might have an existing FastAPI app, and you'd like to add a path for a Gradio demo.
You can easily do this with `gradio.mount_gradio_app()`.

Here's a complete example:

$code_custom_path

Note that this approach also allows you run your Gradio apps on custom paths (`http://localhost:8000/gradio` in the example above).


## Authentication

### Password-protected app

You may wish to put an authentication page in front of your app to limit who can open your app. With the `auth=` keyword argument in the `launch()` method, you can provide a tuple with a username and password, or a list of acceptable username/password tuples; Here's an example that provides password-based authentication for a single user named "admin":

```python
demo.launch(auth=("admin", "pass1234"))
```

For more complex authentication handling, you can even pass a function that takes a username and password as arguments, and returns `True` to allow access, `False` otherwise.

Here's an example of a function that accepts any login where the username and password are the same:

```python
def same_auth(username, password):
    return username == password
demo.launch(auth=same_auth)
```

If you have multiple users, you may wish to customize the content that is shown depending on the user that is logged in. You can retrieve the logged in user by [accessing the network request directly](#accessing-the-network-request-directly) as discussed above, and then reading the `.username` attribute of the request. Here's an example:


```python
import gradio as gr

def update_message(request: gr.Request):
    return f"Welcome, {request.username}"

with gr.Blocks() as demo:
    m = gr.Markdown()
    demo.load(update_message, None, m)

demo.launch(auth=[("Abubakar", "Abubakar"), ("Ali", "Ali")])
```

Note: For authentication to work properly, third party cookies must be enabled in your browser. This is not the case by default for Safari or for Chrome Incognito Mode.

If users visit the `/logout` page of your Gradio app, they will automatically be logged out and session cookies deleted. This allows you to add logout functionality to your Gradio app as well. Let's update the previous example to include a log out button:

```python
import gradio as gr

def update_message(request: gr.Request):
    return f"Welcome, {request.username}"

with gr.Blocks() as demo:
    m = gr.Markdown()
    logout_button = gr.Button("Logout", link="/logout")
    demo.load(update_message, None, m)

demo.launch(auth=[("Pete", "Pete"), ("Dawood", "Dawood")])
```

Note: Gradio's built-in authentication provides a straightforward and basic layer of access control but does not offer robust security features for applications that require stringent access controls (e.g.  multi-factor authentication, rate limiting, or automatic lockout policies).

### OAuth (Login via Hugging Face)

Gradio natively supports OAuth login via Hugging Face. In other words, you can easily add a _"Sign in with Hugging Face"_ button to your demo, which allows you to get a user's HF username as well as other information from their HF profile. Check out [this Space](https://huggingface.co/spaces/Wauplin/gradio-oauth-demo) for a live demo.

To enable OAuth, you must set `hf_oauth: true` as a Space metadata in your README.md file. This will register your Space
as an OAuth application on Hugging Face. Next, you can use `gr.LoginButton` to add a login button to
your Gradio app. Once a user is logged in with their HF account, you can retrieve their profile by adding a parameter of type
`gr.OAuthProfile` to any Gradio function. The user profile will be automatically injected as a parameter value. If you want
to perform actions on behalf of the user (e.g. list user's private repos, create repo, etc.), you can retrieve the user
token by adding a parameter of type `gr.OAuthToken`. You must define which scopes you will use in your Space metadata
(see [documentation](https://huggingface.co/docs/hub/spaces-oauth#scopes) for more details).

Here is a short example:

$code_login_with_huggingface

When the user clicks on the login button, they get redirected in a new page to authorize your Space.

<center>
<img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/oauth_sign_in.png" style="width:300px; max-width:80%">
</center>

Users can revoke access to their profile at any time in their [settings](https://huggingface.co/settings/connected-applications).

As seen above, OAuth features are available only when your app runs in a Space. However, you often need to test your app
locally before deploying it. To test OAuth features locally, your machine must be logged in to Hugging Face. Please run `huggingface-cli login` or set `HF_TOKEN` as environment variable with one of your access token. You can generate a new token in your settings page (https://huggingface.co/settings/tokens). Then, clicking on the `gr.LoginButton` will login your local Hugging Face profile, allowing you to debug your app with your Hugging Face account before deploying it to a Space.

**Security Note**: It is important to note that adding a `gr.LoginButton` does not restrict users from using your app, in the same way that adding [username-password authentication](/guides/sharing-your-app#password-protected-app) does. This means that users of your app who have not logged in with Hugging Face can still access and run events in your Gradio app -- the difference is that the `gr.OAuthProfile` or `gr.OAuthToken` will be `None` in the corresponding functions.


### OAuth (with external providers)

It is also possible to authenticate with external OAuth providers (e.g. Google OAuth) in your Gradio apps. To do this, first mount your Gradio app within a FastAPI app ([as discussed above](#mounting-within-another-fast-api-app)). Then, you must write an *authentication function*, which gets the user's username from the OAuth provider and returns it. This function should be passed to the `auth_dependency` parameter in `gr.mount_gradio_app`.

Similar to [FastAPI dependency functions](https://fastapi.tiangolo.com/tutorial/dependencies/), the function specified by `auth_dependency` will run before any Gradio-related route in your FastAPI app. The function should accept a single parameter: the FastAPI `Request` and return either a string (representing a user's username) or `None`. If a string is returned, the user will be able to access the Gradio-related routes in your FastAPI app.

First, let's show a simplistic example to illustrate the `auth_dependency` parameter:

```python
from fastapi import FastAPI, Request
import gradio as gr

app = FastAPI()

def get_user(request: Request):
    return request.headers.get("user")

demo = gr.Interface(lambda s: f"Hello {s}!", "textbox", "textbox")

app = gr.mount_gradio_app(app, demo, path="/demo", auth_dependency=get_user)

if __name__ == '__main__':
    uvicorn.run(app)
```

In this example, only requests that include a "user" header will be allowed to access the Gradio app. Of course, this does not add much security, since any user can add this header in their request.

Here's a more complete example showing how to add Google OAuth to a Gradio app (assuming you've already created OAuth Credentials on the [Google Developer Console](https://console.cloud.google.com/project)):

```python
import os
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Depends, Request
from starlette.config import Config
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import gradio as gr

app = FastAPI()

# Replace these with your own OAuth settings
GOOGLE_CLIENT_ID = "..."
GOOGLE_CLIENT_SECRET = "..."
SECRET_KEY = "..."

config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

SECRET_KEY = os.environ.get('SECRET_KEY') or "a_very_secret_key"
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Dependency to get the current user
def get_user(request: Request):
    user = request.session.get('user')
    if user:
        return user['name']
    return None

@app.get('/')
def public(user: dict = Depends(get_user)):
    if user:
        return RedirectResponse(url='/gradio')
    else:
        return RedirectResponse(url='/login-demo')

@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    # If your app is running on https, you should ensure that the
    # `redirect_uri` is https, e.g. uncomment the following lines:
    #
    # from urllib.parse import urlparse, urlunparse
    # redirect_uri = urlunparse(urlparse(str(redirect_uri))._replace(scheme='https'))
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.route('/auth')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url='/')
    request.session['user'] = dict(access_token)["userinfo"]
    return RedirectResponse(url='/')

with gr.Blocks() as login_demo:
    gr.Button("Login", link="/login")

app = gr.mount_gradio_app(app, login_demo, path="/login-demo")

def greet(request: gr.Request):
    return f"Welcome to Gradio, {request.username}"

with gr.Blocks() as main_demo:
    m = gr.Markdown("Welcome to Gradio!")
    gr.Button("Logout", link="/logout")
    main_demo.load(greet, None, m)

app = gr.mount_gradio_app(app, main_demo, path="/gradio", auth_dependency=get_user)

if __name__ == '__main__':
    uvicorn.run(app)
```

There are actually two separate Gradio apps in this example! One that simply displays a log in button (this demo is accessible to any user), while the other main demo is only accessible to users that are logged in. You can try this example out on [this Space](https://huggingface.co/spaces/gradio/oauth-example).


## Analytics

By default, Gradio collects certain analytics to help us better understand the usage of the `gradio` library. This includes the following information:

* What environment the Gradio app is running on (e.g. Colab Notebook, Hugging Face Spaces)
* What input/output components are being used in the Gradio app
* Whether the Gradio app is utilizing certain advanced features, such as `auth` or `show_error`
* The IP address which is used solely to measure the number of unique developers using Gradio
* The version of Gradio that is running

No information is collected from _users_ of your Gradio app. If you'd like to diable analytics altogether, you can do so by setting the `analytics_enabled` parameter to `False` in `gr.Blocks`, `gr.Interface`, or `gr.ChatInterface`. Or, you can set the GRADIO_ANALYTICS_ENABLED environment variable to `"False"` to apply this to all Gradio apps created across your system.

*Note*: this reflects the analytics policy as of `gradio>=4.32.0`.

## Progressive Web App (PWA)

[Progressive Web Apps (PWAs)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps) are web applications that are regular web pages or websites, but can appear to the user like installable platform-specific applications.

Gradio apps can be easily served as PWAs by setting the `pwa=True` parameter in the `launch()` method. Here's an example:

```python
import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")

demo.launch(pwa=True)  # Launch your app as a PWA
```

This will generate a PWA that can be installed on your device. Here's how it looks:

![Installing PWA](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/install-pwa.gif)

When you specify `favicon_path` in the `launch()` method, the icon will be used as the app's icon. Here's an example:

```python
demo.launch(pwa=True, favicon_path="./hf-logo.svg")  # Use a custom icon for your PWA
```

![Custom PWA Icon](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/pwa-favicon.png)


=== File: guides/04_additional-features/08_file-access.md ===
# Security and File Access

Sharing your Gradio app with others (by hosting it on Spaces, on your own server, or through temporary share links) **exposes** certain files on your machine to the internet. Files that are exposed can be accessed at a special URL:

```bash
http://<your-gradio-app-url>/gradio_api/file=<local-file-path>
```

This guide explains which files are exposed as well as some best practices for making sure the files on your machine are secure.

## Files Gradio allows users to access 

- **1. Static files**. You can designate static files or directories using the `gr.set_static_paths` function. Static files  are not be copied to the Gradio cache (see below) and will be served directly from your computer. This can help save disk space and reduce the time your app takes to launch but be mindful of possible security implications as any static files are accessible to all useres of your Gradio app.

- **2. Files in the `allowed_paths` parameter in `launch()`**. This parameter allows you to pass in a list of additional directories or exact filepaths you'd like to allow users to have access to. (By default, this parameter is an empty list).

- **3. Files in Gradio's cache**. After you launch your Gradio app, Gradio copies certain files into a temporary cache and makes these files accessible to users. Let's unpack this in more detail below.


## The Gradio cache

First, it's important to understand why Gradio has a cache at all. Gradio copies files to a cache directory before returning them to the frontend. This prevents files from being overwritten by one user while they are still needed by another user of your application. For example, if your prediction function returns a video file, then Gradio will move that video to the cache after your prediction function runs and returns a URL the frontend can use to show the video. Any file in the cache is available via URL to all users of your running application.

Tip: You can customize the location of the cache by setting the `GRADIO_TEMP_DIR` environment variable to an absolute path, such as `/home/usr/scripts/project/temp/`. 

### Files Gradio moves to the cache

Gradio moves three kinds of files into the cache

1. Files specified by the developer before runtime, e.g. cached examples, default values of components, or files passed into parameters such as the `avatar_images` of `gr.Chatbot`

2. File paths returned by a prediction function in your Gradio application, if they ALSO meet one of the conditions below:

* It is in the `allowed_paths` parameter of the `Blocks.launch` method.
* It is in the current working directory of the python interpreter.
* It is in the temp directory obtained by `tempfile.gettempdir()`.

**Note:** files in the current working directory whose name starts with a period (`.`) will not be moved to the cache, even if they are returned from a prediction function, since they often contain sensitive information. 

If none of these criteria are met, the prediction function that is returning that file will raise an exception instead of moving the file to cache. Gradio performs this check so that arbitrary files on your machine cannot be accessed.

3. Files uploaded by a user to your Gradio app (e.g. through the `File` or `Image` input components).

Tip: If at any time Gradio blocks a file that you would like it to process, add its path to the `allowed_paths` parameter.

## The files Gradio will not allow others to access

While running, Gradio apps will NOT ALLOW users to access:

- **Files that you explicitly block via the `blocked_paths` parameter in `launch()`**. You can pass in a list of additional directories or exact filepaths to the `blocked_paths` parameter in `launch()`. This parameter takes precedence over the files that Gradio exposes by default, or by the `allowed_paths` parameter or the `gr.set_static_paths` function.

- **Any other paths on the host machine**. Users should NOT be able to access other arbitrary paths on the host.

## Uploading Files

Sharing your Gradio application will also allow users to upload files to your computer or server. You can set a maximum file size for uploads to prevent abuse and to preserve disk space. You can do this with the `max_file_size` parameter of `.launch`. For example, the following two code snippets limit file uploads to 5 megabytes per file.

```python
import gradio as gr

demo = gr.Interface(lambda x: x, "image", "image")

demo.launch(max_file_size="5mb")
# or
demo.launch(max_file_size=5 * gr.FileSize.MB)
```

## Best Practices

* Set a `max_file_size` for your application.
* Do not return arbitrary user input from a function that is connected to a file-based output component (`gr.Image`, `gr.File`, etc.). For example, the following interface would allow anyone to move an arbitrary file in your local directory to the cache: `gr.Interface(lambda s: s, "text", "file")`. This is because the user input is treated as an arbitrary file path. 
* Make `allowed_paths` as small as possible. If a path in `allowed_paths` is a directory, any file within that directory can be accessed. Make sure the entires of `allowed_paths` only contains files related to your application.
* Run your gradio application from the same directory the application file is located in. This will narrow the scope of files Gradio will be allowed to move into the cache. For example, prefer `python app.py` to `python Users/sources/project/app.py`.


## Example: Accessing local files
Both `gr.set_static_paths` and the `allowed_paths` parameter in launch expect absolute paths. Below is a minimal example to display a local `.png` image file in an HTML block.

```txt
├── assets
│   └── logo.png
└── app.py
```
For the example directory structure, `logo.png` and any other files in the `assets` folder can be accessed from your Gradio app in `app.py` as follows:

```python
from pathlib import Path

import gradio as gr

gr.set_static_paths(paths=[Path.cwd().absolute()/"assets"])

with gr.Blocks() as demo:
    gr.HTML("<img src='/gradio_api/file=assets/logo.png'>")

demo.launch()
```


=== File: guides/04_additional-features/09_multipage-apps.md ===
# Multipage Apps

Your Gradio app can support multiple pages with the `Blocks.route()` method. Here's what a multipage Gradio app generally looks like:

```python
with gr.Blocks() as demo:
    name = gr.Textbox(label="Name")
    ...
with demo.route("Test", "/test"):
    num = gr.Number()
    ...

demo.launch()
```

This allows you to define links to separate pages, each with a separate URL, which are  linked to the top of the Gradio app in an automatically-generated navbar. 

Here's a complete example:

$code_multipage

All of these pages will share the same backend, including the same queue.

Note: multipage apps do not support interactions between pages, e.g. an event listener on one page cannot output to a component on another page. Use `gr.Tabs()` for this type of functionality instead of pages.

**Separate Files**

For maintainability, you may want to write the code for different pages in different files. Because any Gradio Blocks can be imported and rendered inside another Blocks using the `.render()` method, you can do this as follows.

Create one main file, say `app.py` and create separate Python files for each page:

```
- app.py
- main_page.py
- second_page.py
```

The Python file corresponding to each page should consist of a regular Gradio Blocks, Interface, or ChatInterface application, e.g.

`main_page.py`

```py
import gradio as gr

with gr.Blocks() as demo:
    gr.Image()

if __name__ == "__main__":
    demo.launch()
```

`second_page.py`

```py
import gradio as gr

with gr.Blocks() as demo:
    t = gr.Textbox()
    demo.load(lambda : "Loaded", None, t)

if __name__ == "__main__":
    demo.launch()
```

In your main `app.py` file, simply import the Gradio demos from the page files and `.render()` them:

`app.py`

```py
import gradio as gr

import main_page, second_page

with gr.Blocks() as demo:
    main_page.demo.render()
with demo.route("Second Page"):
    second_page.demo.render()

if __name__ == "__main__":
    demo.launch()
```

This allows you to run each page as an independent Gradio app for testing, while also creating a single file `app.py` that serves as the entrypoint for the complete multipage app.




=== File: guides/04_additional-features/10_environment-variables.md ===
# Environment Variables

Environment variables in Gradio provide a way to customize your applications and launch settings without changing the codebase. In this guide, we'll explore the key environment variables supported in Gradio and how to set them.

## Key Environment Variables

### 1. `GRADIO_SERVER_PORT`

- **Description**: Specifies the port on which the Gradio app will run.
- **Default**: `7860`
- **Example**:
  ```bash
  export GRADIO_SERVER_PORT=8000
  ```

### 2. `GRADIO_SERVER_NAME`

- **Description**: Defines the host name for the Gradio server. To make Gradio accessible from any IP address, set this to `"0.0.0.0"`
- **Default**: `"127.0.0.1"` 
- **Example**:
  ```bash
  export GRADIO_SERVER_NAME="0.0.0.0"
  ```

### 3. `GRADIO_NUM_PORTS`

- **Description**: Defines the number of ports to try when starting the Gradio server.
- **Default**: `100`
- **Example**:
  ```bash
  export GRADIO_NUM_PORTS=200
  ```

### 4. `GRADIO_ANALYTICS_ENABLED`

- **Description**: Whether Gradio should provide 
- **Default**: `"True"`
- **Options**: `"True"`, `"False"`
- **Example**:
  ```sh
  export GRADIO_ANALYTICS_ENABLED="True"
  ```

### 5. `GRADIO_DEBUG`

- **Description**: Enables or disables debug mode in Gradio. If debug mode is enabled, the main thread does not terminate allowing error messages to be printed in environments such as Google Colab.
- **Default**: `0`
- **Example**:
  ```sh
  export GRADIO_DEBUG=1
  ```

### 6. `GRADIO_FLAGGING_MODE`

- **Description**: Controls whether users can flag inputs/outputs in the Gradio interface. See [the Guide on flagging](/guides/using-flagging) for more details.
- **Default**: `"manual"`
- **Options**: `"never"`, `"manual"`, `"auto"`
- **Example**:
  ```sh
  export GRADIO_FLAGGING_MODE="never"
  ```

### 7. `GRADIO_TEMP_DIR`

- **Description**: Specifies the directory where temporary files created by Gradio are stored.
- **Default**: System default temporary directory
- **Example**:
  ```sh
  export GRADIO_TEMP_DIR="/path/to/temp"
  ```

### 8. `GRADIO_ROOT_PATH`

- **Description**: Sets the root path for the Gradio application. Useful if running Gradio [behind a reverse proxy](/guides/running-gradio-on-your-web-server-with-nginx).
- **Default**: `""`
- **Example**:
  ```sh
  export GRADIO_ROOT_PATH="/myapp"
  ```

### 9. `GRADIO_SHARE`

- **Description**: Enables or disables sharing the Gradio app.
- **Default**: `"False"`
- **Options**: `"True"`, `"False"`
- **Example**:
  ```sh
  export GRADIO_SHARE="True"
  ```

### 10. `GRADIO_ALLOWED_PATHS`

- **Description**: Sets a list of complete filepaths or parent directories that gradio is allowed to serve. Must be absolute paths. Warning: if you provide directories, any files in these directories or their subdirectories are accessible to all users of your app. Multiple items can be specified by separating items with commas.
- **Default**: `""`
- **Example**:
  ```sh
  export GRADIO_ALLOWED_PATHS="/mnt/sda1,/mnt/sda2"
  ```

### 11. `GRADIO_BLOCKED_PATHS`

- **Description**: Sets a list of complete filepaths or parent directories that gradio is not allowed to serve (i.e. users of your app are not allowed to access). Must be absolute paths. Warning: takes precedence over `allowed_paths` and all other directories exposed by Gradio by default. Multiple items can be specified by separating items with commas.
- **Default**: `""`
- **Example**:
  ```sh
  export GRADIO_BLOCKED_PATHS="/users/x/gradio_app/admin,/users/x/gradio_app/keys"
  ```

### 12. `FORWARDED_ALLOW_IPS`

- **Description**: This is not a Gradio-specific environment variable, but rather one used in server configurations, specifically `uvicorn` which is used by Gradio internally. This environment variable is useful when deploying applications behind a reverse proxy. It defines a list of IP addresses that are trusted to forward traffic to your application. When set, the application will trust the `X-Forwarded-For` header from these IP addresses to determine the original IP address of the user making the request. This means that if you use the `gr.Request` [object's](https://www.gradio.app/docs/gradio/request) `client.host` property, it will correctly get the user's IP address instead of the IP address of the reverse proxy server. Note that only trusted IP addresses (i.e. the IP addresses of your reverse proxy servers) should be added, as any server with these IP addresses can modify the `X-Forwarded-For` header and spoof the client's IP address.
- **Default**: `"127.0.0.1"`
- **Example**:
  ```sh
  export FORWARDED_ALLOW_IPS="127.0.0.1,192.168.1.100"
  ```

### 13. `GRADIO_CACHE_EXAMPLES`

- **Description**: Whether or not to cache examples by default in `gr.Interface()`, `gr.ChatInterface()` or in `gr.Examples()` when no explicit argument is passed for the `cache_examples` parameter. You can set this environment variable to either the string "true" or "false".
- **Default**: `"false"`
- **Example**:
  ```sh
  export GRADIO_CACHE_EXAMPLES="true"
  ```


### 14. `GRADIO_CACHE_MODE`

- **Description**: How to cache examples. Only applies if `cache_examples` is set to `True` either via enviornment variable or by an explicit parameter, AND no no explicit argument is passed for the `cache_mode` parameter in `gr.Interface()`, `gr.ChatInterface()` or in `gr.Examples()`. Can be set to either the strings "lazy" or "eager." If "lazy", examples are cached after their first use for all users of the app. If "eager", all examples are cached at app launch.

- **Default**: `"eager"`
- **Example**:
  ```sh
  export GRADIO_CACHE_MODE="lazy"
  ```


### 15. `GRADIO_EXAMPLES_CACHE`

- **Description**:  If you set `cache_examples=True` in `gr.Interface()`, `gr.ChatInterface()` or in `gr.Examples()`, Gradio will run your prediction function and save the results to disk. By default, this is in the `.gradio/cached_examples//` subdirectory within your app's working directory. You can customize the location of cached example files created by Gradio by setting the environment variable `GRADIO_EXAMPLES_CACHE` to an absolute path or a path relative to your working directory.
- **Default**: `".gradio/cached_examples/"`
- **Example**:
  ```sh
  export GRADIO_EXAMPLES_CACHE="custom_cached_examples/"
  ```


### 16. `GRADIO_SSR_MODE`

- **Description**: Controls whether server-side rendering (SSR) is enabled. When enabled, the initial HTML is rendered on the server rather than the client, which can improve initial page load performance and SEO.

- **Default**: `"False"` (except on Hugging Face Spaces, where this environment variable sets it to `True`)
- **Options**: `"True"`, `"False"`
- **Example**:
  ```sh
  export GRADIO_SSR_MODE="True"
  ```

### 17. `GRADIO_NODE_SERVER_NAME`

- **Description**: Defines the host name for the Gradio node server. (Only applies if `ssr_mode` is set to `True`.)
- **Default**: `GRADIO_SERVER_NAME` if it is set, otherwise `"127.0.0.1"`
- **Example**:
  ```sh
  export GRADIO_NODE_SERVER_NAME="0.0.0.0"
  ```

### 18. `GRADIO_NODE_NUM_PORTS`

- **Description**: Defines the number of ports to try when starting the Gradio node server. (Only applies if `ssr_mode` is set to `True`.)
- **Default**: `100`
- **Example**:
  ```sh
  export GRADIO_NODE_NUM_PORTS=200
  ```

### 19. `GRADIO_RESET_EXAMPLES_CACHE`

- **Description**: If set to "True", Gradio will delete and recreate the examples cache directory when the app starts instead of reusing the cached example if they already exist. 
- **Default**: `"False"`
- **Options**: `"True"`, `"False"`
- **Example**:
  ```sh
  export GRADIO_RESET_EXAMPLES_CACHE="True"
  ```

### 20. `GRADIO_CHAT_FLAGGING_MODE`

- **Description**: Controls whether users can flag messages in `gr.ChatInterface` applications. Similar to `GRADIO_FLAGGING_MODE` but specifically for chat interfaces.
- **Default**: `"never"`
- **Options**: `"never"`, `"manual"`
- **Example**:
  ```sh
  export GRADIO_CHAT_FLAGGING_MODE="manual"
  ```



## How to Set Environment Variables

To set environment variables in your terminal, use the `export` command followed by the variable name and its value. For example:

```sh
export GRADIO_SERVER_PORT=8000
```

If you're using a `.env` file to manage your environment variables, you can add them like this:

```sh
GRADIO_SERVER_PORT=8000
GRADIO_SERVER_NAME="localhost"
```

Then, use a tool like `dotenv` to load these variables when running your application.





=== File: guides/04_additional-features/11_resource-cleanup.md ===
# Resource Cleanup

Your Gradio application may create resources during its lifetime.
Examples of resources are `gr.State` variables, any variables you create and explicitly hold in memory, or files you save to disk. 
Over time, these resources can use up all of your server's RAM or disk space and crash your application.

Gradio provides some tools for you to clean up the resources created by your app:

1. Automatic deletion of `gr.State` variables.
2. Automatic cache cleanup with the `delete_cache` parameter.
2. The `Blocks.unload` event.

Let's take a look at each of them individually.

## Automatic deletion of `gr.State`

When a user closes their browser tab, Gradio will automatically delete any `gr.State` variables associated with that user session after 60 minutes. If the user connects again within those 60 minutes, no state will be deleted.

You can control the deletion behavior further with the following two parameters of `gr.State`:

1. `delete_callback` - An arbitrary function that will be called when the variable is deleted. This function must take the state value as input. This function is useful for deleting variables from GPU memory.
2. `time_to_live` - The number of seconds the state should be stored for after it is created or updated. This will delete variables before the session is closed, so it's useful for clearing state for potentially long running sessions.

## Automatic cache cleanup via `delete_cache`

Your Gradio application will save uploaded and generated files to a special directory called the cache directory. Gradio uses a hashing scheme to ensure that duplicate files are not saved to the cache but over time the size of the cache will grow (especially if your app goes viral 😉).

Gradio can periodically clean up the cache for you if you specify the `delete_cache` parameter of `gr.Blocks()`, `gr.Interface()`, or `gr.ChatInterface()`. 
This parameter is a tuple of the form `[frequency, age]` both expressed in number of seconds.
Every `frequency` seconds, the temporary files created by this Blocks instance will be deleted if more than `age` seconds have passed since the file was created. 
For example, setting this to (86400, 86400) will delete temporary files every day if they are older than a day old.
Additionally, the cache will be deleted entirely when the server restarts.

## The `unload` event

Additionally, Gradio now includes a `Blocks.unload()` event, allowing you to run arbitrary cleanup functions when users disconnect (this does not have a 60 minute delay).
Unlike other gradio events, this event does not accept inputs or outptus.
You can think of the `unload` event as the opposite of the `load` event.

## Putting it all together

The following demo uses all of these features. When a user visits the page, a special unique directory is created for that user.
As the user interacts with the app, images are saved to disk in that special directory.
When the user closes the page, the images created in that session are deleted via the `unload` event.
The state and files in the cache are cleaned up automatically as well.

$code_state_cleanup
$demo_state_cleanup

=== File: guides/04_additional-features/12_themes.md ===
# Gradio Themes

Gradio themes are the easiest way to customize the look and feel of your app. You can choose from a variety of themes, or create your own. To do so, pass the `theme=` kwarg to the `Interface` constructor. For example:

```python
demo = gr.Interface(..., theme=gr.themes.Monochrome())
```

or

```python
with gr.Block(theme=gr.themes.Soft()):
    ...
```

Gradio comes with a set of prebuilt themes which you can load from `gr.themes.*`. You can extend these themes or create your own themes from scratch - see the [theming guide](https://gradio.app/guides/theming-guide) for more details.

For additional styling ability, you can pass any CSS (as well as custom JavaScript) to your Gradio application. This is discussed in more detail in our [custom JS and CSS guide](/guides/custom-CSS-and-JS).



=== File: guides/04_additional-features/13_client-side-functions.md ===
# Client Side Functions

Gradio allows you to run certain "simple" functions directly in the browser by setting `js=True` in your event listeners. This will **automatically convert your Python code into JavaScript**, which significantly improves the responsiveness of your app by avoiding a round trip to the server for simple UI updates.

The difference in responsiveness is most noticeable on hosted applications (like Hugging Face Spaces), when the server is under heavy load, with high-latency connections, or when many users are accessing the app simultaneously.

## When to Use Client Side Functions

Client side functions are ideal for updating component properties (like visibility, placeholders, interactive state, or styling). 

Here's a basic example:

```py
import gradio as gr

with gr.Blocks() as demo:
    with gr.Row() as row:
        btn = gr.Button("Hide this row")
    
    # This function runs in the browser without a server roundtrip
    btn.click(
        lambda: gr.Row(visible=False), 
        None, 
        row, 
        js=True
    )

demo.launch()
```


## Limitations

Client side functions have some important restrictions:
* They can only update component properties (not values)
* They cannot take any inputs

Here are some functions that will work with `js=True`:

```py
# Simple property updates
lambda: gr.Textbox(lines=4)

# Multiple component updates
lambda: [gr.Textbox(lines=4), gr.Button(interactive=False)]

# Using gr.update() for property changes
lambda: gr.update(visible=True, interactive=False)
```

We are working to increase the space of functions that can be transpiled to JavaScript so that they can be run in the browser. [Follow the Groovy library for more info](https://github.com/abidlabs/groovy-transpiler).


## Complete Example

Here's a more complete example showing how client side functions can improve the user experience:

$code_todo_list_js


## Behind the Scenes

When you set `js=True`, Gradio:

1. Transpiles your Python function to JavaScript

2. Runs the function directly in the browser

3. Still sends the request to the server (for consistency and to handle any side effects)

This provides immediate visual feedback while ensuring your application state remains consistent.


=== File: guides/04_additional-features/14_view-api-page.md ===
# API Page

You can use almost any Gradio app programmatically via the built-in API! In the footer of any Gradio app, you'll see a "Use via API" link. Clicking on the link opens up a detailed documentation page for the API that Gradio generates based on the function signatures in your Gradio app.

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/view-api-animated.gif)

## Configuring the API Page

**API endpoint names**

When you create a Gradio application, the API endpoint names are automatically generated based on the function names. You can change this by using the `api_name` parameter in `gr.Interface` or `gr.ChatInterface`. If you are using Gradio `Blocks`, you can name each event listener, like this:

```python
btn.click(add, [num1, num2], output, api_name="addition")
```

**Hiding API endpoints**

When building a complex Gradio app, you might want to hide certain API endpoints from appearing on the view API page, e.g. if they correspond to functions that simply update the UI. You can set the  `show_api` parameter to `False` in any `Blocks` event listener to achieve this, e.g. 

```python
btn.click(add, [num1, num2], output, show_api=False)
```

**Disabling API endpoints**

Hiding the API endpoint doesn't disable it. A user can still programmatically call the API endpoint if they know the name. If you want to disable an API endpoint altogether, set `api_name=False`, e.g. 

```python
btn.click(add, [num1, num2], output, api_name=False)
```

Note: setting an `api_name=False` also means that downstream apps will not be able to load your Gradio app using `gr.load()` as this function uses the Gradio API under the hood.

**Adding API endpoints**

You can also add new API routes to your Gradio application that do not correspond to events in your UI.

For example, in this Gradio application, we add a new route that adds numbers and slices a list:

```py
import gradio as gr
with gr.Blocks() as demo:
    with gr.Row():
        input = gr.Textbox()
        button = gr.Button("Submit")
    output = gr.Textbox()
    def fn(a: int, b: int, c: list[str]) -> tuple[int, str]:
        return a + b, c[a:b]
    gr.api(fn, api_name="add_and_slice")

_, url, _ = demo.launch()
```

This will create a new route `/add_and_slice` which will show up in the "view API" page. It can be programmatically called by the Python or JS Clients (discussed below) like this:

```py
from gradio_client import Client

client = Client(url)
result = client.predict(
        a=3,
        b=5,
        c=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        api_name="/add_and_slice"
)
print(result)
```

## The Clients

This API page not only lists all of the endpoints that can be used to query the Gradio app, but also shows the usage of both [the Gradio Python client](https://gradio.app/guides/getting-started-with-the-python-client/), and [the Gradio JavaScript client](https://gradio.app/guides/getting-started-with-the-js-client/). 

For each endpoint, Gradio automatically generates a complete code snippet with the parameters and their types, as well as example inputs, allowing you to immediately test an endpoint. Here's an example showing an image file input and `str` output:

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/view-api-snippet.png)


## The API Recorder 🪄

Instead of reading through the view API page, you can also use Gradio's built-in API recorder to generate the relevant code snippet. Simply click on the "API Recorder" button, use your Gradio app via the UI as you would normally, and then the API Recorder will generate the code using the Clients to recreate your all of your interactions programmatically.

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/api-recorder.gif)

## MCP Server

The API page also includes instructions on how to use the Gradio app as an Model Context Protocol (MCP) server, which is a standardized way to expose functions as tools so that they can be used by LLMs. 

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/view-api-mcp.png)

For the MCP sever, each tool, its description, and its parameters are listed, along with instructions on how to integrate with popular MCP Clients. Read more about Gradio's [MCP integration here](https://www.gradio.app/guides/building-mcp-server-with-gradio).

## OpenAPI Specification

You can access the complete OpenAPI (formerly Swagger) specification of your Gradio app's API at the endpoint `<your-gradio-app-url>/gradio_api/openapi.json`. The OpenAPI specification is a standardized, language-agnostic interface description for REST APIs that enables both humans and computers to discover and understand the capabilities of your service.


=== File: guides/04_additional-features/15_internationalization.md ===
Tags: internationalization, i18n, language
Related spaces:

# Internationalization (i18n)

Gradio comes with ready-to-use internationalization (i18n) support:

- Built-in translations: Gradio automatically translates standard UI elements (like "Submit", "Clear", "Cancel") in more than 40 languages based on the user's browser locale.
- Custom translations: For app-specific text, Gradio provides the I18n class that lets you extend the built-in system with your own translations.

## Setting Up Translations

You can initialize the `I18n` class with multiple language dictionaries to add custom translations:

```python
import gradio as gr

# Create an I18n instance with translations for multiple languages
i18n = gr.I18n(
    en={"greeting": "Hello, welcome to my app!", "submit": "Submit"},
    es={"greeting": "¡Hola, bienvenido a mi aplicación!", "submit": "Enviar"},
    fr={"greeting": "Bonjour, bienvenue dans mon application!", "submit": "Soumettre"}
)

with gr.Blocks() as demo:
    # Use the i18n method to translate the greeting
    gr.Markdown(i18n("greeting"))
    with gr.Row():
        input_text = gr.Textbox(label="Input")
        output_text = gr.Textbox(label="Output")
    
    submit_btn = gr.Button(i18n("submit"))

# Pass the i18n instance to the launch method
demo.launch(i18n=i18n)
```

## How It Works

When you use the `i18n` instance with a translation key, Gradio will show the corresponding translation to users based on their browser's language settings or the language they've selected in your app.

If a translation isn't available for the user's locale, the system will fall back to English (if available) or display the key itself.

## Valid Locale Codes

Locale codes should follow the BCP 47 format (e.g., 'en', 'en-US', 'zh-CN'). The `I18n` class will warn you if you use an invalid locale code.

## Supported Component Properties

The following component properties typically support internationalization:

- `description`
- `info`
- `title`
- `placeholder`
- `value`
- `label`

Note that support may vary depending on the component, and some properties might have exceptions where internationalization is not applicable. You can check this by referring to the typehint for the parameter and if it contains `I18nData`, then it supports internationalization.

=== File: guides/10_other-tutorials/02_building-an-mcp-client-with-gradio.md ===
# Using the Gradio Chatbot as an MCP Client

This guide will walk you through a Model Context Protocol (MCP) Client and Server implementation with Gradio. You'll build a Gradio Chatbot that uses Anthropic's Claude API to respond to user messages, but also, as an MCP Client, generates images (by connecting to an MCP Server, which is a separate Gradio app). 

<video src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/mcp-guides.mp4" style="width:100%" controls preload> </video>

## What is MCP?

The Model Context Protocol (MCP) standardizes how applications provide context to LLMs. It allows Claude to interact with external tools, like image generators, file systems, or APIs, etc.

## Prerequisites

- Python 3.10+
- An Anthropic API key
- Basic understanding of Python programming

## Setup

First, install the required packages:

```bash
pip install gradio anthropic mcp
```

Create a `.env` file in your project directory and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## Part 1: Building the MCP Server

The server provides tools that Claude can use. In this example, we'll create a server that generates images through [a HuggingFace space](https://huggingface.co/spaces/ysharma/SanaSprint).

Create a file named `gradio_mcp_server.py`:

```python
from mcp.server.fastmcp import FastMCP
import json
import sys
import io
import time
from gradio_client import Client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

mcp = FastMCP("huggingface_spaces_image_display")

@mcp.tool()
async def generate_image(prompt: str, width: int = 512, height: int = 512) -> str:
    """Generate an image using SanaSprint model.
    
    Args:
        prompt: Text prompt describing the image to generate
        width: Image width (default: 512)
        height: Image height (default: 512)
    """
    client = Client("https://ysharma-sanasprint.hf.space/")
    
    try:
        result = client.predict(
            prompt,
            "0.6B",
            0,
            True,
            width,
            height,
            4.0,
            2,
            api_name="/infer"
        )
        
        if isinstance(result, list) and len(result) >= 1:
            image_data = result[0]
            if isinstance(image_data, dict) and "url" in image_data:
                return json.dumps({
                    "type": "image",
                    "url": image_data["url"],
                    "message": f"Generated image for prompt: {prompt}"
                })
        
        return json.dumps({
            "type": "error",
            "message": "Failed to generate image"
        })
        
    except Exception as e:
        return json.dumps({
            "type": "error",
            "message": f"Error generating image: {str(e)}"
        })

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

### What this server does:

1. It creates an MCP server that exposes a `generate_image` tool
2. The tool connects to the SanaSprint model hosted on HuggingFace Spaces
3. It handles the asynchronous nature of image generation by polling for results
4. When an image is ready, it returns the URL in a structured JSON format

## Part 2: Building the MCP Client with Gradio

Now let's create a Gradio chat interface as MCP Client that connects Claude to our MCP server.

Create a file named `app.py`:

```python
import asyncio
import os
import json
from typing import List, Dict, Any, Union
from contextlib import AsyncExitStack

import gradio as gr
from gradio.components.chatbot import ChatMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class MCPClientWrapper:
    def __init__(self):
        self.session = None
        self.exit_stack = None
        self.anthropic = Anthropic()
        self.tools = []
    
    def connect(self, server_path: str) -> str:
        return loop.run_until_complete(self._connect(server_path))
    
    async def _connect(self, server_path: str) -> str:
        if self.exit_stack:
            await self.exit_stack.aclose()
        
        self.exit_stack = AsyncExitStack()
        
        is_python = server_path.endswith('.py')
        command = "python" if is_python else "node"
        
        server_params = StdioServerParameters(
            command=command,
            args=[server_path],
            env={"PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        
        response = await self.session.list_tools()
        self.tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
        
        tool_names = [tool["name"] for tool in self.tools]
        return f"Connected to MCP server. Available tools: {', '.join(tool_names)}"
    
    def process_message(self, message: str, history: List[Union[Dict[str, Any], ChatMessage]]) -> tuple:
        if not self.session:
            return history + [
                {"role": "user", "content": message}, 
                {"role": "assistant", "content": "Please connect to an MCP server first."}
            ], gr.Textbox(value="")
        
        new_messages = loop.run_until_complete(self._process_query(message, history))
        return history + [{"role": "user", "content": message}] + new_messages, gr.Textbox(value="")
    
    async def _process_query(self, message: str, history: List[Union[Dict[str, Any], ChatMessage]]):
        claude_messages = []
        for msg in history:
            if isinstance(msg, ChatMessage):
                role, content = msg.role, msg.content
            else:
                role, content = msg.get("role"), msg.get("content")
            
            if role in ["user", "assistant", "system"]:
                claude_messages.append({"role": role, "content": content})
        
        claude_messages.append({"role": "user", "content": message})
        
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=claude_messages,
            tools=self.tools
        )

        result_messages = []
        
        for content in response.content:
            if content.type == 'text':
                result_messages.append({
                    "role": "assistant", 
                    "content": content.text
                })
                
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                result_messages.append({
                    "role": "assistant",
                    "content": f"I'll use the {tool_name} tool to help answer your question.",
                    "metadata": {
                        "title": f"Using tool: {tool_name}",
                        "log": f"Parameters: {json.dumps(tool_args, ensure_ascii=True)}",
                        "status": "pending",
                        "id": f"tool_call_{tool_name}"
                    }
                })
                
                result_messages.append({
                    "role": "assistant",
                    "content": "```json\n" + json.dumps(tool_args, indent=2, ensure_ascii=True) + "\n```",
                    "metadata": {
                        "parent_id": f"tool_call_{tool_name}",
                        "id": f"params_{tool_name}",
                        "title": "Tool Parameters"
                    }
                })
                
                result = await self.session.call_tool(tool_name, tool_args)
                
                if result_messages and "metadata" in result_messages[-2]:
                    result_messages[-2]["metadata"]["status"] = "done"
                
                result_messages.append({
                    "role": "assistant",
                    "content": "Here are the results from the tool:",
                    "metadata": {
                        "title": f"Tool Result for {tool_name}",
                        "status": "done",
                        "id": f"result_{tool_name}"
                    }
                })
                
                result_content = result.content
                if isinstance(result_content, list):
                    result_content = "\n".join(str(item) for item in result_content)
                
                try:
                    result_json = json.loads(result_content)
                    if isinstance(result_json, dict) and "type" in result_json:
                        if result_json["type"] == "image" and "url" in result_json:
                            result_messages.append({
                                "role": "assistant",
                                "content": {"path": result_json["url"], "alt_text": result_json.get("message", "Generated image")},
                                "metadata": {
                                    "parent_id": f"result_{tool_name}",
                                    "id": f"image_{tool_name}",
                                    "title": "Generated Image"
                                }
                            })
                        else:
                            result_messages.append({
                                "role": "assistant",
                                "content": "```\n" + result_content + "\n```",
                                "metadata": {
                                    "parent_id": f"result_{tool_name}",
                                    "id": f"raw_result_{tool_name}",
                                    "title": "Raw Output"
                                }
                            })
                except:
                    result_messages.append({
                        "role": "assistant",
                        "content": "```\n" + result_content + "\n```",
                        "metadata": {
                            "parent_id": f"result_{tool_name}",
                            "id": f"raw_result_{tool_name}",
                            "title": "Raw Output"
                        }
                    })
                
                claude_messages.append({"role": "user", "content": f"Tool result for {tool_name}: {result_content}"})
                next_response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=claude_messages,
                )
                
                if next_response.content and next_response.content[0].type == 'text':
                    result_messages.append({
                        "role": "assistant",
                        "content": next_response.content[0].text
                    })

        return result_messages

client = MCPClientWrapper()

def gradio_interface():
    with gr.Blocks(title="MCP Weather Client") as demo:
        gr.Markdown("# MCP Weather Assistant")
        gr.Markdown("Connect to your MCP weather server and chat with the assistant")
        
        with gr.Row(equal_height=True):
            with gr.Column(scale=4):
                server_path = gr.Textbox(
                    label="Server Script Path",
                    placeholder="Enter path to server script (e.g., weather.py)",
                    value="gradio_mcp_server.py"
                )
            with gr.Column(scale=1):
                connect_btn = gr.Button("Connect")
        
        status = gr.Textbox(label="Connection Status", interactive=False)
        
        chatbot = gr.Chatbot(
            value=[], 
            height=500,
            type="messages",
            show_copy_button=True,
            avatar_images=("👤", "🤖")
        )
        
        with gr.Row(equal_height=True):
            msg = gr.Textbox(
                label="Your Question",
                placeholder="Ask about weather or alerts (e.g., What's the weather in New York?)",
                scale=4
            )
            clear_btn = gr.Button("Clear Chat", scale=1)
        
        connect_btn.click(client.connect, inputs=server_path, outputs=status)
        msg.submit(client.process_message, [msg, chatbot], [chatbot, msg])
        clear_btn.click(lambda: [], None, chatbot)
        
    return demo

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not found in environment. Please set it in your .env file.")
    
    interface = gradio_interface()
    interface.launch(debug=True)
```

### What this MCP Client does:

- Creates a friendly Gradio chat interface for user interaction
- Connects to the MCP server you specify
- Handles conversation history and message formatting
- Makes call to Claude API with tool definitions
- Processes tool usage requests from Claude
- Displays images and other tool outputs in the chat
- Sends tool results back to Claude for interpretation

## Running the Application

To run your MCP application:

- Start a terminal window and run the MCP Client:
   ```bash
   python app.py
   ```
- Open the Gradio interface at the URL shown (typically http://127.0.0.1:7860)
- In the Gradio interface, you'll see a field for the MCP Server path. It should default to `gradio_mcp_server.py`.
- Click "Connect" to establish the connection to the MCP server.
- You should see a message indicating the server connection was successful.

## Example Usage

Now you can chat with Claude and it will be able to generate images based on your descriptions.

Try prompts like:
- "Can you generate an image of a mountain landscape at sunset?"
- "Create an image of a cool tabby cat"
- "Generate a picture of a panda wearing sunglasses"

Claude will recognize these as image generation requests and automatically use the `generate_image` tool from your MCP server.


## How it Works

Here's the high-level flow of what happens during a chat session:

1. Your prompt enters the Gradio interface
2. The client forwards your prompt to Claude
3. Claude analyzes the prompt and decides to use the `generate_image` tool
4. The client sends the tool call to the MCP server
5. The server calls the external image generation API
6. The image URL is returned to the client
7. The client sends the image URL back to Claude
8. Claude provides a response that references the generated image
9. The Gradio chat interface displays both Claude's response and the image


## Next Steps

Now that you have a working MCP system, here are some ideas to extend it:

- Add more tools to your server
- Improve error handling 
- Add private Huggingface Spaces with authentication for secure tool access
- Create custom tools that connect to your own APIs or services
- Implement streaming responses for better user experience

## Conclusion

Congratulations! You've successfully built an MCP Client and Server that allows Claude to generate images based on text prompts. This is just the beginning of what you can do with Gradio and MCP. This guide enables you to build complex AI applications that can use Claude or any other powerful LLM to interact with virtually any external tool or service.

Read our other Guide on using [Gradio apps as MCP Servers](./building-mcp-server-with-gradio).


=== File: guides/10_other-tutorials/03_building-mcp-server-with-gradio.md ===
# Building an MCP Server with Gradio

Tags: MCP, TOOL, LLM, SERVER

In this guide, we will describe how to launch your Gradio app so that it functions as an MCP Server.

Punchline: it's as simple as setting `mcp_server=True` in `.launch()`. 

### Prerequisites

If not already installed, please install Gradio with the MCP extra:

```bash
pip install "gradio[mcp]"
```

This will install the necessary dependencies, including the `mcp` package. Also, you will need an LLM application that supports tool calling using the MCP protocol, such as Claude Desktop, Cursor, or Cline (these are known as "MCP Clients").

## What is an MCP Server?

An MCP (Model Control Protocol) server is a standardized way to expose tools so that they can be used by  LLMs. A tool can provide an LLM functionality that it does not have natively, such as the ability to generate images or calculate the prime factors of a number. 

## Example: Counting Letters in a Word

LLMs are famously not great at counting the number of letters in a word (e.g. the number of "r"-s in "strawberry"). But what if we equip them with a tool to help? Let's start by writing a simple Gradio app that counts the number of letters in a word or phrase:

$code_letter_counter

Notice that we have: (1) included a detailed docstring for our function, and (2) set `mcp_server=True` in `.launch()`. This is all that's needed for your Gradio app to serve as an MCP server! Now, when you run this app, it will:

1. Start the regular Gradio web interface
2. Start the MCP server
3. Print the MCP server URL in the console

The MCP server will be accessible at:
```
http://your-server:port/gradio_api/mcp/sse
```

Gradio automatically converts the `letter_counter` function into an MCP tool that can be used by LLMs. The docstring of the function and the type hints of arguments will be used to generate the description of the tool and its parameters. The name of the function will be used as the name of your tool. Any initial values you provide to your input components (e.g. "strawberry" and "r" in the `gr.Textbox` components above) will be used as the default values if your LLM doesn't specify a value for that particular input parameter.

Now, all you need to do is add this URL endpoint to your MCP Client (e.g. Claude Desktop, Cursor, or Cline), which typically means pasting this config in the settings:

```
{
  "mcpServers": {
    "gradio": {
      "url": "http://your-server:port/gradio_api/mcp/sse"
    }
  }
}
```

(By the way, you can find the exact config to copy-paste by going to the "View API" link in the footer of your Gradio app, and then clicking on "MCP").

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/view-api-mcp.png)

## Key features of the Gradio <> MCP Integration

1. **Tool Conversion**: Each API endpoint in your Gradio app is automatically converted into an MCP tool with a corresponding name, description, and input schema. To view the tools and schemas, visit http://your-server:port/gradio_api/mcp/schema or go to the "View API" link in the footer of your Gradio app, and then click on "MCP".


2. **Environment variable support**. There are two ways to enable the MCP server functionality:

*  Using the `mcp_server` parameter, as shown above:
   ```python
   demo.launch(mcp_server=True)
   ```

* Using environment variables:
   ```bash
   export GRADIO_MCP_SERVER=True
   ```

3. **File Handling**: The server automatically handles file data conversions, including:
   - Converting base64-encoded strings to file data
   - Processing image files and returning them in the correct format
   - Managing temporary file storage

    It is **strongly** recommended that input images and files be passed as full URLs ("http://..." or "https:/...") as MCP Clients do not always handle local files correctly.


4. **Hosted MCP Servers on 󠀠🤗 Spaces**: You can publish your Gradio application for free on Hugging Face Spaces, which will allow you to have a free hosted MCP server. Here's an example of such a Space: https://huggingface.co/spaces/abidlabs/mcp-tools. Notice that you can add this config to your MCP Client to start using the tools from this Space immediately:

```
{
  "mcpServers": {
    "gradio": {
      "url": "https://abidlabs-mcp-tools.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

<video src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/mcp_guide1.mp4" style="width:100%" controls preload> </video>


## Converting an Existing Space

If there's an existing Space that you'd like to use an MCP server, you'll need to do three things:

1. First, [duplicate the Space](https://huggingface.co/docs/hub/en/spaces-more-ways-to-create#duplicating-a-space) if it is not your own Space. This will allow you to make changes to the app. If the Space requires a GPU, set the hardware of the duplicated Space to be same as the original Space. You can make it either a public Space or a private Space, since it is possible to use either as an MCP server, as described below.
2. Then, add docstrings to the functions that you'd like the LLM to be able to call as a tool. The docstring should be in the same format as the example code above.
3. Finally, add `mcp_server=True` in `.launch()`.

That's it!

## Private Spaces

You can use either a public Space or a private Space as an MCP server. If you'd like to use a private Space as an MCP server (or a ZeroGPU Space with your own quota), then you will need to provide your [Hugging Face token](https://huggingface.co/settings/token) when you make your request. To do this, simply add it as a header in your config like this:

```
{
  "mcpServers": {
    "gradio": {
      "url": "https://abidlabs-mcp-tools.hf.space/gradio_api/mcp/sse",
      "headers": {
        "Authorization": "Bearer <YOUR-HUGGING-FACE-TOKEN>"
      }
    }
  }
}
```

## Authentication and Credentials

You may wish to authenticate users more precisely or let them provide other kinds of credentials or tokens in order to provide a custom experience for different users. 

Gradio allows you to access the underlying `starlette.Request` that has made the tool call, which means that you can access headers, originating IP address, or any other information that is part of the network request. To do this, simply add a parameter in your function of the type `gr.Request`, and Gradio will automatically inject the request object as the parameter.

Here's an example:

```py
import gradio as gr

def echo_headers(x, request: gr.Request):
    return str(dict(request.headers))

gr.Interface(echo_headers, "textbox", "textbox").launch(mcp_server=True)
```

This MCP server will simply ignore the user's input and echo back all of the headers from a user's request. One can build more complex apps using the same idea. See the [docs on `gr.Request`](https://www.gradio.app/main/docs/gradio/request) for more information (note that only the core Starlette attributes of the `gr.Request` object will be present, attributes such as Gradio's `.session_hash` will not be present).

## Adding MCP-Only Tools

So far, all of our MCP tools have corresponded to event listeners in the UI. This works well for functions that directly update the UI, but may not work if you wish to expose a "pure logic" function that should return raw data (e.g., a JSON object) without directly causing a UI update.

In order to expose such an MCP tool, you can create a pure Gradio API endpoint using `gr.api` (see [full docs here](https://www.gradio.app/main/docs/gradio/api)). Here's an example of creating an MCP tool that slices a list:

$code_mcp_tool_only

Note that if you use this approach, your function signature must be fully typed, including the return value, as these signature are used to determine the typing information for the MCP tool.

## Limitations

The approach outlined above provides an easy way to use any Gradio app as an MCP server. But there are a few limitations to keep in mind:

1. There is no way to identify specific users within the MCP tool call. This means that you cannot store user state between calls within the Gradio app. If you use a `gr.State` component in your app, it will always be passed in with its original, default value.

2. You cannot select specific endpoints in your Gradio expose as your tools (all endpoints with `show_api=True` are treated as tools), or  change the descriptions of your tools unless you change the docstrings of your functions.

If you need to overcome these limitations, you'll need to create **a custom MCP server** to call your Gradio application, which we describe next.


## Custom MCP Servers

In some cases, you may need to manually create an MCP Server that internally calls a Gradio app. This approach is useful when you want to:

- Choose specific endpoints within a larger Gradio app to serve as tools
- Customize how your tools are presented to LLMs (e.g. change the tool name, schema, or description)
- Start the Gradio app MCP server when a tool is called (if you are running multiple Gradio apps locally and want to save memory / GPU)
- Use a different MCP protocol than SSE

This is very doable thanks to the [Gradio Python Client](https://www.gradio.app/guides/getting-started-with-the-python-client) and the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). Here's an example of creating a custom MCP server that connects to various Gradio apps hosted on [HuggingFace Spaces](https://huggingface.co/spaces) using the `stdio` protocol:

```python
from mcp.server.fastmcp import FastMCP
from gradio_client import Client
import sys
import io
import json 

mcp = FastMCP("gradio-spaces")

clients = {}

def get_client(space_id: str) -> Client:
    """Get or create a Gradio client for the specified space."""
    if space_id not in clients:
        clients[space_id] = Client(space_id)
    return clients[space_id]


@mcp.tool()
async def generate_image(prompt: str, space_id: str = "ysharma/SanaSprint") -> str:
    """Generate an image using Flux.
    
    Args:
        prompt: Text prompt describing the image to generate
        space_id: HuggingFace Space ID to use 
    """
    client = get_client(space_id)
    result = client.predict(
            prompt=prompt,
            model_size="1.6B",
            seed=0,
            randomize_seed=True,
            width=1024,
            height=1024,
            guidance_scale=4.5,
            num_inference_steps=2,
            api_name="/infer"
    )
    return result


@mcp.tool()
async def run_dia_tts(prompt: str, space_id: str = "ysharma/Dia-1.6B") -> str:
    """Text-to-Speech Synthesis.
    
    Args:
        prompt: Text prompt describing the conversation between speakers S1, S2
        space_id: HuggingFace Space ID to use 
    """
    client = get_client(space_id)
    result = client.predict(
            text_input=f"""{prompt}""",
            audio_prompt_input=None, 
            max_new_tokens=3072,
            cfg_scale=3,
            temperature=1.3,
            top_p=0.95,
            cfg_filter_top_k=30,
            speed_factor=0.94,
            api_name="/generate_audio"
    )
    return result


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    mcp.run(transport='stdio')
```

This server exposes two tools:
1. `run_dia_tts` - Generates a conversation for the given transcript in the form of `[S1]first-sentence. [S2]second-sentence. [S1]...`
2. `generate_image` - Generates images using a fast text-to-image model

To use this MCP Server with Claude Desktop (as MCP Client):

1. Save the code to a file (e.g., `gradio_mcp_server.py`)
2. Install the required dependencies: `pip install mcp gradio-client`
3. Configure Claude Desktop to use your server by editing the configuration file at `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
    "mcpServers": {
        "gradio-spaces": {
            "command": "python",
            "args": [
                "/absolute/path/to/gradio_mcp_server.py"
            ]
        }
    }
}
```

4. Restart Claude Desktop

Now, when you ask Claude about generating an image or transcribing audio, it can use your Gradio-powered tools to accomplish these tasks.


## Troubleshooting your MCP Servers

The MCP protocol is still in its infancy and you might see issues connecting to an MCP Server that you've built. We generally recommend using the [MCP Inspector Tool](https://github.com/modelcontextprotocol/inspector) to try connecting and debugging your MCP Server.

Here are some things that may help:

**1. Ensure that you've provided type hints and valid docstrings for your functions**

As mentioned earlier, Gradio reads the docstrings for your functions and the type hints of input arguments to generate the description of the tool and parameters. A valid function and docstring looks like this (note the "Args:" block with indented parameter names underneath):

```py
def image_orientation(image: Image.Image) -> str:
    """
    Returns whether image is portrait or landscape.

    Args:
        image (Image.Image): The image to check.
    """
    return "Portrait" if image.height > image.width else "Landscape"
```

Note: You can preview the schema that is created for your MCP server by visiting the `http://your-server:port/gradio_api/mcp/schema` URL.

**2. Try accepting input arguments as `str`**

Some MCP Clients do not recognize parameters that are numeric or other complex types, but all of the MCP Clients that we've tested accept `str` input parameters. When in doubt, change your input parameter to be a `str` and then cast to a specific type in the function, as in this example:

```py
def prime_factors(n: str):
    """
    Compute the prime factorization of a positive integer.

    Args:
        n (str): The integer to factorize. Must be greater than 1.
    """
    n_int = int(n)
    if n_int <= 1:
        raise ValueError("Input must be an integer greater than 1.")

    factors = []
    while n_int % 2 == 0:
        factors.append(2)
        n_int //= 2

    divisor = 3
    while divisor * divisor <= n_int:
        while n_int % divisor == 0:
            factors.append(divisor)
            n_int //= divisor
        divisor += 2

    if n_int > 1:
        factors.append(n_int)

    return factors
```

**3. Ensure that your MCP Client Supports SSE**

Some MCP Clients, notably [Claude Desktop](https://claude.ai/download), do not yet support SSE-based MCP Servers. In those cases, you can use a tool such as [mcp-remote](https://github.com/geelen/mcp-remote). First install [Node.js](https://nodejs.org/en/download/). Then, add the following to your own MCP Client config:

```
{
  "mcpServers": {
    "gradio": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://your-server:port/gradio_api/mcp/sse"
      ]
    }
  }
}
```

**4. Restart your MCP Client and MCP Server**

Some MCP Clients require you to restart them every time you update the MCP configuration. Other times, if the connection between the MCP Client and servers breaks, you might need to restart the MCP server. If all else fails, try restarting both your MCP Client and MCP Servers!



=== File: guides/10_other-tutorials/developing-faster-with-reload-mode.md ===
# Developing Faster with Auto-Reloading

**Prerequisite**: This Guide requires you to know about Blocks. Make sure to [read the Guide to Blocks first](https://gradio.app/blocks-and-event-listeners).

This guide covers auto reloading, reloading in a Python IDE, and using gradio with Jupyter Notebooks.

## Why Auto-Reloading?

When you are building a Gradio demo, particularly out of Blocks, you may find it cumbersome to keep re-running your code to test your changes.

To make it faster and more convenient to write your code, we've made it easier to "reload" your Gradio apps instantly when you are developing in a **Python IDE** (like VS Code, Sublime Text, PyCharm, or so on) or generally running your Python code from the terminal. We've also developed an analogous "magic command" that allows you to re-run cells faster if you use **Jupyter Notebooks** (or any similar environment like Colab).

This short Guide will cover both of these methods, so no matter how you write Python, you'll leave knowing how to build Gradio apps faster.

## Python IDE Reload 🔥

If you are building Gradio Blocks using a Python IDE, your file of code (let's name it `run.py`) might look something like this:

```python
import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("# Greetings from Gradio!")
    inp = gr.Textbox(placeholder="What is your name?")
    out = gr.Textbox()

    inp.change(fn=lambda x: f"Welcome, {x}!",
               inputs=inp,
               outputs=out)

if __name__ == "__main__":
    demo.launch()
```

The problem is that anytime that you want to make a change to your layout, events, or components, you have to close and rerun your app by writing `python run.py`.

Instead of doing this, you can run your code in **reload mode** by changing 1 word: `python` to `gradio`:

In the terminal, run `gradio run.py`. That's it!

Now, you'll see that after you'll see something like this:

```bash
Watching: '/Users/freddy/sources/gradio/gradio', '/Users/freddy/sources/gradio/demo/'

Running on local URL:  http://127.0.0.1:7860
```

The important part here is the line that says `Watching...` What's happening here is that Gradio will be observing the directory where `run.py` file lives, and if the file changes, it will automatically rerun the file for you. So you can focus on writing your code, and your Gradio demo will refresh automatically 🥳

Tip: the `gradio` command does not detect the parameters passed to the `launch()` methods because the `launch()` method is never called in reload mode. For example, setting `auth`, or `show_error` in `launch()` will not be reflected in the app.

There is one important thing to keep in mind when using the reload mode: Gradio specifically looks for a Gradio Blocks/Interface demo called `demo` in your code. If you have named your demo something else, you will need to pass in the name of your demo as the 2nd parameter in your code. So if your `run.py` file looked like this:

```python
import gradio as gr

with gr.Blocks() as my_demo:
    gr.Markdown("# Greetings from Gradio!")
    inp = gr.Textbox(placeholder="What is your name?")
    out = gr.Textbox()

    inp.change(fn=lambda x: f"Welcome, {x}!",
               inputs=inp,
               outputs=out)

if __name__ == "__main__":
    my_demo.launch()
```

Then you would launch it in reload mode like this: `gradio run.py --demo-name=my_demo`.

By default, the Gradio use UTF-8 encoding for scripts. **For reload mode**, If you are using encoding formats other than UTF-8 (such as cp1252), make sure you've done like this:

1. Configure encoding declaration of python script, for example: `# -*- coding: cp1252 -*-`
2. Confirm that your code editor has identified that encoding format. 
3. Run like this: `gradio run.py --encoding cp1252`

🔥 If your application accepts command line arguments, you can pass them in as well. Here's an example:

```python
import gradio as gr
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--name", type=str, default="User")
args, unknown = parser.parse_known_args()

with gr.Blocks() as demo:
    gr.Markdown(f"# Greetings {args.name}!")
    inp = gr.Textbox()
    out = gr.Textbox()

    inp.change(fn=lambda x: x, inputs=inp, outputs=out)

if __name__ == "__main__":
    demo.launch()
```

Which you could run like this: `gradio run.py --name Gretel`

As a small aside, this auto-reloading happens if you change your `run.py` source code or the Gradio source code. Meaning that this can be useful if you decide to [contribute to Gradio itself](https://github.com/gradio-app/gradio/blob/main/CONTRIBUTING.md) ✅


## Controlling the Reload 🎛️

By default, reload mode will re-run your entire script for every change you make.
But there are some cases where this is not desirable.
For example, loading a machine learning model should probably only happen once to save time. There are also some Python libraries that use C or Rust extensions that throw errors when they are reloaded, like `numpy` and `tiktoken`.

In these situations, you can place code that you do not want to be re-run inside an `if gr.NO_RELOAD:`  codeblock. Here's an example of how you can use it to only load a transformers model once during the development process.

Tip: The value of `gr.NO_RELOAD` is `True`. So you don't have to change your script when you are done developing and want to run it in production. Simply run the file with `python` instead of `gradio`.

```python
import gradio as gr

if gr.NO_RELOAD:
	from transformers import pipeline
	pipe = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

demo = gr.Interface(lambda s: {d["label"]: d["score"] for d in pipe(s)}, gr.Textbox(), gr.Label())

if __name__ == "__main__":
    demo.launch()
```


## Jupyter Notebook Magic 🔮

What about if you use Jupyter Notebooks (or Colab Notebooks, etc.) to develop code? We got something for you too!

We've developed a **magic command** that will create and run a Blocks demo for you. To use this, load the gradio extension at the top of your notebook:

`%load_ext gradio`

Then, in the cell that you are developing your Gradio demo, simply write the magic command **`%%blocks`** at the top, and then write the layout and components like you would normally:

```py
%%blocks

import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown(f"# Greetings {args.name}!")
    inp = gr.Textbox()
    out = gr.Textbox()

    inp.change(fn=lambda x: x, inputs=inp, outputs=out)
```

Notice that:

- You do not need to launch your demo — Gradio does that for you automatically!

- Every time you rerun the cell, Gradio will re-render your app on the same port and using the same underlying web server. This means you'll see your changes _much, much faster_ than if you were rerunning the cell normally.

Here's what it looks like in a jupyter notebook:

![](https://gradio-builds.s3.amazonaws.com/demo-files/jupyter_reload.gif)

🪄 This works in colab notebooks too! [Here's a colab notebook](https://colab.research.google.com/drive/1zAuWoiTIb3O2oitbtVb2_ekv1K6ggtC1?usp=sharing) where you can see the Blocks magic in action. Try making some changes and re-running the cell with the Gradio code!

Tip: You may have to use `%%blocks --share` in Colab to get the demo to appear in the cell.

The Notebook Magic is now the author's preferred way of building Gradio demos. Regardless of how you write Python code, we hope either of these methods will give you a much better development experience using Gradio.

---

## Next Steps

Now that you know how to develop quickly using Gradio, start building your own!

If you are looking for inspiration, try exploring demos other people have built with Gradio, [browse public Hugging Face Spaces](http://hf.space/) 🤗


=== File: guides/10_other-tutorials/theming-guide.md ===
# Theming

Tags: THEMES

## Introduction

Gradio features a built-in theming engine that lets you customize the look and feel of your app. You can choose from a variety of themes, or create your own. To do so, pass the `theme=` kwarg to the `Blocks` or `Interface` constructor. For example:

```python
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    ...
```

<div class="wrapper">
<iframe
	src="https://gradio-theme-soft.hf.space?__theme=light"
	frameborder="0"
></iframe>
</div>

Gradio comes with a set of prebuilt themes which you can load from `gr.themes.*`. These are:


* `gr.themes.Base()` - the `"base"` theme sets the primary color to blue but otherwise has minimal styling, making it particularly useful as a base for creating new, custom themes.
* `gr.themes.Default()` - the `"default"` Gradio 5 theme, with a vibrant orange primary color and gray secondary color.
* `gr.themes.Origin()` - the `"origin"` theme is most similar to Gradio 4 styling. Colors, especially in light mode, are more subdued than the Gradio 5 default theme.
* `gr.themes.Citrus()` - the `"citrus"` theme uses a yellow primary color, highlights form elements that are in focus, and includes fun 3D effects when buttons are clicked.
* `gr.themes.Monochrome()` - the `"monochrome"` theme uses a black primary and white secondary color, and uses serif-style fonts, giving the appearance of a black-and-white newspaper. 
* `gr.themes.Soft()` - the `"soft"` theme uses a purple primary color and white secondary color. It also increases the border radius around buttons and form elements and highlights labels.
* `gr.themes.Glass()` - the `"glass"` theme has a blue primary color and a transclucent gray secondary color. The theme also uses vertical gradients to create a glassy effect.
* `gr.themes.Ocean()` - the `"ocean"` theme has a blue-green primary color and gray secondary color. The theme also uses horizontal gradients, especially for buttons and some form elements.


Each of these themes set values for hundreds of CSS variables. You can use prebuilt themes as a starting point for your own custom themes, or you can create your own themes from scratch. Let's take a look at each approach.

## Using the Theme Builder

The easiest way to build a theme is using the Theme Builder. To launch the Theme Builder locally, run the following code:

```python
import gradio as gr

gr.themes.builder()
```

$demo_theme_builder

You can use the Theme Builder running on Spaces above, though it runs much faster when you launch it locally via `gr.themes.builder()`.

As you edit the values in the Theme Builder, the app will preview updates in real time. You can download the code to generate the theme you've created so you can use it in any Gradio app.

In the rest of the guide, we will cover building themes programmatically.

## Extending Themes via the Constructor

Although each theme has hundreds of CSS variables, the values for most these variables are drawn from 8 core variables which can be set through the constructor of each prebuilt theme. Modifying these 8 arguments allows you to quickly change the look and feel of your app.

### Core Colors

The first 3 constructor arguments set the colors of the theme and are `gradio.themes.Color` objects. Internally, these Color objects hold brightness values for the palette of a single hue, ranging from 50, 100, 200..., 800, 900, 950. Other CSS variables are derived from these 3 colors.

The 3 color constructor arguments are:

- `primary_hue`: This is the color draws attention in your theme. In the default theme, this is set to `gradio.themes.colors.orange`.
- `secondary_hue`: This is the color that is used for secondary elements in your theme. In the default theme, this is set to `gradio.themes.colors.blue`.
- `neutral_hue`: This is the color that is used for text and other neutral elements in your theme. In the default theme, this is set to `gradio.themes.colors.gray`.

You could modify these values using their string shortcuts, such as

```python
with gr.Blocks(theme=gr.themes.Default(primary_hue="red", secondary_hue="pink")) as demo:
    ...
```

or you could use the `Color` objects directly, like this:

```python
with gr.Blocks(theme=gr.themes.Default(primary_hue=gr.themes.colors.red, secondary_hue=gr.themes.colors.pink)) as demo:
    ...
```

<div class="wrapper">
<iframe
	src="https://gradio-theme-extended-step-1.hf.space?__theme=light"
	frameborder="0"
></iframe>
</div>

Predefined colors are:

- `slate`
- `gray`
- `zinc`
- `neutral`
- `stone`
- `red`
- `orange`
- `amber`
- `yellow`
- `lime`
- `green`
- `emerald`
- `teal`
- `cyan`
- `sky`
- `blue`
- `indigo`
- `violet`
- `purple`
- `fuchsia`
- `pink`
- `rose`

You could also create your own custom `Color` objects and pass them in.

### Core Sizing

The next 3 constructor arguments set the sizing of the theme and are `gradio.themes.Size` objects. Internally, these Size objects hold pixel size values that range from `xxs` to `xxl`. Other CSS variables are derived from these 3 sizes.

- `spacing_size`: This sets the padding within and spacing between elements. In the default theme, this is set to `gradio.themes.sizes.spacing_md`.
- `radius_size`: This sets the roundedness of corners of elements. In the default theme, this is set to `gradio.themes.sizes.radius_md`.
- `text_size`: This sets the font size of text. In the default theme, this is set to `gradio.themes.sizes.text_md`.

You could modify these values using their string shortcuts, such as

```python
with gr.Blocks(theme=gr.themes.Default(spacing_size="sm", radius_size="none")) as demo:
    ...
```

or you could use the `Size` objects directly, like this:

```python
with gr.Blocks(theme=gr.themes.Default(spacing_size=gr.themes.sizes.spacing_sm, radius_size=gr.themes.sizes.radius_none)) as demo:
    ...
```

<div class="wrapper">
<iframe
	src="https://gradio-theme-extended-step-2.hf.space?__theme=light"
	frameborder="0"
></iframe>
</div>

The predefined size objects are:

- `radius_none`
- `radius_sm`
- `radius_md`
- `radius_lg`
- `spacing_sm`
- `spacing_md`
- `spacing_lg`
- `text_sm`
- `text_md`
- `text_lg`

You could also create your own custom `Size` objects and pass them in.

### Core Fonts

The final 2 constructor arguments set the fonts of the theme. You can pass a list of fonts to each of these arguments to specify fallbacks. If you provide a string, it will be loaded as a system font. If you provide a `gradio.themes.GoogleFont`, the font will be loaded from Google Fonts.

- `font`: This sets the primary font of the theme. In the default theme, this is set to `gradio.themes.GoogleFont("IBM Plex Sans")`.
- `font_mono`: This sets the monospace font of the theme. In the default theme, this is set to `gradio.themes.GoogleFont("IBM Plex Mono")`.

You could modify these values such as the following:

```python
with gr.Blocks(theme=gr.themes.Default(font=[gr.themes.GoogleFont("Inconsolata"), "Arial", "sans-serif"])) as demo:
    ...
```

<div class="wrapper">
<iframe
	src="https://gradio-theme-extended-step-3.hf.space?__theme=light"
	frameborder="0"
></iframe>
</div>

## Extending Themes via `.set()`

You can also modify the values of CSS variables after the theme has been loaded. To do so, use the `.set()` method of the theme object to get access to the CSS variables. For example:

```python
theme = gr.themes.Default(primary_hue="blue").set(
    loader_color="#FF0000",
    slider_color="#FF0000",
)

with gr.Blocks(theme=theme) as demo:
    ...
```

In the example above, we've set the `loader_color` and `slider_color` variables to `#FF0000`, despite the overall `primary_color` using the blue color palette. You can set any CSS variable that is defined in the theme in this manner.

Your IDE type hinting should help you navigate these variables. Since there are so many CSS variables, let's take a look at how these variables are named and organized.

### CSS Variable Naming Conventions

CSS variable names can get quite long, like `button_primary_background_fill_hover_dark`! However they follow a common naming convention that makes it easy to understand what they do and to find the variable you're looking for. Separated by underscores, the variable name is made up of:

1. The target element, such as `button`, `slider`, or `block`.
2. The target element type or sub-element, such as `button_primary`, or `block_label`.
3. The property, such as `button_primary_background_fill`, or `block_label_border_width`.
4. Any relevant state, such as `button_primary_background_fill_hover`.
5. If the value is different in dark mode, the suffix `_dark`. For example, `input_border_color_focus_dark`.

Of course, many CSS variable names are shorter than this, such as `table_border_color`, or `input_shadow`.

### CSS Variable Organization

Though there are hundreds of CSS variables, they do not all have to have individual values. They draw their values by referencing a set of core variables and referencing each other. This allows us to only have to modify a few variables to change the look and feel of the entire theme, while also getting finer control of individual elements that we may want to modify.

#### Referencing Core Variables

To reference one of the core constructor variables, precede the variable name with an asterisk. To reference a core color, use the `*primary_`, `*secondary_`, or `*neutral_` prefix, followed by the brightness value. For example:

```python
theme = gr.themes.Default(primary_hue="blue").set(
    button_primary_background_fill="*primary_200",
    button_primary_background_fill_hover="*primary_300",
)
```

In the example above, we've set the `button_primary_background_fill` and `button_primary_background_fill_hover` variables to `*primary_200` and `*primary_300`. These variables will be set to the 200 and 300 brightness values of the blue primary color palette, respectively.

Similarly, to reference a core size, use the `*spacing_`, `*radius_`, or `*text_` prefix, followed by the size value. For example:

```python
theme = gr.themes.Default(radius_size="md").set(
    button_primary_border_radius="*radius_xl",
)
```

In the example above, we've set the `button_primary_border_radius` variable to `*radius_xl`. This variable will be set to the `xl` setting of the medium radius size range.

#### Referencing Other Variables

Variables can also reference each other. For example, look at the example below:

```python
theme = gr.themes.Default().set(
    button_primary_background_fill="#FF0000",
    button_primary_background_fill_hover="#FF0000",
    button_primary_border="#FF0000",
)
```

Having to set these values to a common color is a bit tedious. Instead, we can reference the `button_primary_background_fill` variable in the `button_primary_background_fill_hover` and `button_primary_border` variables, using a `*` prefix.

```python
theme = gr.themes.Default().set(
    button_primary_background_fill="#FF0000",
    button_primary_background_fill_hover="*button_primary_background_fill",
    button_primary_border="*button_primary_background_fill",
)
```

Now, if we change the `button_primary_background_fill` variable, the `button_primary_background_fill_hover` and `button_primary_border` variables will automatically update as well.

This is particularly useful if you intend to share your theme - it makes it easy to modify the theme without having to change every variable.

Note that dark mode variables automatically reference each other. For example:

```python
theme = gr.themes.Default().set(
    button_primary_background_fill="#FF0000",
    button_primary_background_fill_dark="#AAAAAA",
    button_primary_border="*button_primary_background_fill",
    button_primary_border_dark="*button_primary_background_fill_dark",
)
```

`button_primary_border_dark` will draw its value from `button_primary_background_fill_dark`, because dark mode always draw from the dark version of the variable.

## Creating a Full Theme

Let's say you want to create a theme from scratch! We'll go through it step by step - you can also see the source of prebuilt themes in the gradio source repo for reference - [here's the source](https://github.com/gradio-app/gradio/blob/main/gradio/themes/monochrome.py) for the Monochrome theme.

Our new theme class will inherit from `gradio.themes.Base`, a theme that sets a lot of convenient defaults. Let's make a simple demo that creates a dummy theme called Seafoam, and make a simple app that uses it.

$code_theme_new_step_1

<div class="wrapper">
<iframe
	src="https://gradio-theme-new-step-1.hf.space?__theme=light"
	frameborder="0"
></iframe>
</div>

The Base theme is very barebones, and uses `gr.themes.Blue` as it primary color - you'll note the primary button and the loading animation are both blue as a result. Let's change the defaults core arguments of our app. We'll overwrite the constructor and pass new defaults for the core constructor arguments.

We'll use `gr.themes.Emerald` as our primary color, and set secondary and neutral hues to `gr.themes.Blue`. We'll make our text larger using `text_lg`. We'll use `Quicksand` as our default font, loaded from Google Fonts.

$code_theme_new_step_2

<div class="wrapper">
<iframe
	src="https://gradio-theme-new-step-2.hf.space?__theme=light"
	frameborder="0"
></iframe>
</div>

See how the primary button and the loading animation are now green? These CSS variables are tied to the `primary_hue` variable.

Let's modify the theme a bit more directly. We'll call the `set()` method to overwrite CSS variable values explicitly. We can use any CSS logic, and reference our core constructor arguments using the `*` prefix.

$code_theme_new_step_3

<div class="wrapper">
<iframe
	src="https://gradio-theme-new-step-3.hf.space?__theme=light"
	frameborder="0"
></iframe>
</div>

Look how fun our theme looks now! With just a few variable changes, our theme looks completely different.

You may find it helpful to explore the [source code of the other prebuilt themes](https://github.com/gradio-app/gradio/blob/main/gradio/themes) to see how they modified the base theme. You can also find your browser's Inspector useful to select elements from the UI and see what CSS variables are being used in the styles panel.

## Sharing Themes

Once you have created a theme, you can upload it to the HuggingFace Hub to let others view it, use it, and build off of it!

### Uploading a Theme

There are two ways to upload a theme, via the theme class instance or the command line. We will cover both of them with the previously created `seafoam` theme.

- Via the class instance

Each theme instance has a method called `push_to_hub` we can use to upload a theme to the HuggingFace hub.

```python
seafoam.push_to_hub(repo_name="seafoam",
                    version="0.0.1",
					hf_token="<token>")
```

- Via the command line

First save the theme to disk

```python
seafoam.dump(filename="seafoam.json")
```

Then use the `upload_theme` command:

```bash
upload_theme\
"seafoam.json"\
"seafoam"\
--version "0.0.1"\
--hf_token "<token>"
```

In order to upload a theme, you must have a HuggingFace account and pass your [Access Token](https://huggingface.co/docs/huggingface_hub/quick-start#login)
as the `hf_token` argument. However, if you log in via the [HuggingFace command line](https://huggingface.co/docs/huggingface_hub/quick-start#login) (which comes installed with `gradio`),
you can omit the `hf_token` argument.

The `version` argument lets you specify a valid [semantic version](https://www.geeksforgeeks.org/introduction-semantic-versioning/) string for your theme.
That way your users are able to specify which version of your theme they want to use in their apps. This also lets you publish updates to your theme without worrying
about changing how previously created apps look. The `version` argument is optional. If omitted, the next patch version is automatically applied.

### Theme Previews

By calling `push_to_hub` or `upload_theme`, the theme assets will be stored in a [HuggingFace space](https://huggingface.co/docs/hub/spaces-overview).

For example, the theme preview for the calm seafoam theme is here: [calm seafoam preview](https://huggingface.co/spaces/shivalikasingh/calm_seafoam).

<div class="wrapper">
<iframe
	src="https://shivalikasingh-calm-seafoam.hf.space/?__theme=light"
	frameborder="0"
></iframe>
</div>

### Discovering Themes

The [Theme Gallery](https://huggingface.co/spaces/gradio/theme-gallery) shows all the public gradio themes. After publishing your theme,
it will automatically show up in the theme gallery after a couple of minutes.

You can sort the themes by the number of likes on the space and from most to least recently created as well as toggling themes between light and dark mode.

<div class="wrapper">
<iframe
	src="https://gradio-theme-gallery.static.hf.space"
	frameborder="0"
></iframe>
</div>

### Downloading

To use a theme from the hub, use the `from_hub` method on the `ThemeClass` and pass it to your app:

```python
my_theme = gr.Theme.from_hub("gradio/seafoam")

with gr.Blocks(theme=my_theme) as demo:
    ....
```

You can also pass the theme string directly to `Blocks` or `Interface` (`gr.Blocks(theme="gradio/seafoam")`)

You can pin your app to an upstream theme version by using semantic versioning expressions.

For example, the following would ensure the theme we load from the `seafoam` repo was between versions `0.0.1` and `0.1.0`:

```python
with gr.Blocks(theme="gradio/seafoam@>=0.0.1,<0.1.0") as demo:
    ....
```

Enjoy creating your own themes! If you make one you're proud of, please share it with the world by uploading it to the hub!
If you tag us on [Twitter](https://twitter.com/gradio) we can give your theme a shout out!

<style>
.wrapper {
    position: relative;
    padding-bottom: 56.25%;
    padding-top: 25px;
    height: 0;
}
.wrapper iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
</style>


=== File: guides/10_other-tutorials/wrapping-layouts.md ===
# Wrapping Layouts

Tags: LAYOUTS

## Introduction

Gradio features [blocks](https://www.gradio.app/docs/blocks) to easily layout applications. To use this feature, you need to stack or nest layout components and create a hierarchy with them. This isn't difficult to implement and maintain for small projects, but after the project gets more complex, this component hierarchy becomes difficult to maintain and reuse.

In this guide, we are going to explore how we can wrap the layout classes to create more maintainable and easy-to-read applications without sacrificing flexibility.

## Example

We are going to follow the implementation from this Huggingface Space example:

<gradio-app
space="gradio/wrapping-layouts">
</gradio-app>

## Implementation

The wrapping utility has two important classes. The first one is the ```LayoutBase``` class and the other one is the ```Application``` class.

We are going to look at the ```render``` and ```attach_event``` functions of them for brevity. You can look at the full implementation from [the example code](https://huggingface.co/spaces/WoWoWoWololo/wrapping-layouts/blob/main/app.py).

So let's start with the ```LayoutBase``` class.

### LayoutBase Class

1. Render Function

    Let's look at the ```render``` function in the ```LayoutBase``` class:

```python
# other LayoutBase implementations

def render(self) -> None:
    with self.main_layout:
        for renderable in self.renderables:
            renderable.render()

    self.main_layout.render()
```
This is a little confusing at first but if you consider the default implementation you can understand it easily.
Let's look at an example:

In the default implementation, this is what we're doing:

```python
with Row():
    left_textbox = Textbox(value="left_textbox")
    right_textbox = Textbox(value="right_textbox")
```

Now, pay attention to the Textbox variables. These variables' ```render``` parameter is true by default. So as we use the ```with``` syntax and create these variables, they are calling the ```render``` function under the ```with``` syntax.

We know the render function is called in the constructor with the implementation from the ```gradio.blocks.Block``` class:

```python
class Block:
    # constructor parameters are omitted for brevity
    def __init__(self, ...):
        # other assign functions 

        if render:
            self.render()
```

So our implementation looks like this:

```python
# self.main_layout -> Row()
with self.main_layout:
    left_textbox.render()
    right_textbox.render()
```

What this means is by calling the components' render functions under the ```with``` syntax, we are actually simulating the default implementation.

So now let's consider two nested ```with```s to see how the outer one works. For this, let's expand our example with the ```Tab``` component:

```python
with Tab():
    with Row():
        first_textbox = Textbox(value="first_textbox")
        second_textbox = Textbox(value="second_textbox")
```

Pay attention to the Row and Tab components this time. We have created the Textbox variables above and added them to Row with the ```with``` syntax. Now we need to add the Row component to the Tab component. You can see that the Row component is created with default parameters, so its render parameter is true, that's why the render function is going to be executed under the Tab component's ```with``` syntax.

To mimic this implementation, we need to call the ```render``` function of the ```main_layout``` variable after the ```with``` syntax of the ```main_layout``` variable.

So the implementation looks like this:

```python
with tab_main_layout:
    with row_main_layout:
        first_textbox.render()
        second_textbox.render()

    row_main_layout.render()

tab_main_layout.render()
```

The default implementation and our implementation are the same, but we are using the render function ourselves. So it requires a little work.

Now, let's take a look at the ```attach_event``` function.

2. Attach Event Function

    The function is left as not implemented because it is specific to the class, so each class has to implement its `attach_event` function.

```python
    # other LayoutBase implementations

    def attach_event(self, block_dict: Dict[str, Block]) -> None:
        raise NotImplementedError
```

Check out the ```block_dict``` variable in the ```Application``` class's ```attach_event``` function.

### Application Class

1. Render Function

```python
    # other Application implementations

    def _render(self):
        with self.app:
            for child in self.children:
                child.render()

        self.app.render()
```

From the explanation of the ```LayoutBase``` class's ```render``` function, we can understand the ```child.render``` part.

So let's look at the bottom part, why are we calling the ```app``` variable's ```render``` function? It's important to call this function because if we look at the implementation in the ```gradio.blocks.Blocks``` class, we can see that it is adding the components and event functions into the root component. To put it another way, it is creating and structuring the gradio application.

2. Attach Event Function

    Let's see how we can attach events to components:

```python
    # other Application implementations

    def _attach_event(self):
        block_dict: Dict[str, Block] = {}

        for child in self.children:
            block_dict.update(child.global_children_dict)

        with self.app:
            for child in self.children:
                try:
                    child.attach_event(block_dict=block_dict)
                except NotImplementedError:
                    print(f"{child.name}'s attach_event is not implemented")
```

You can see why the ```global_children_list``` is used in the ```LayoutBase``` class from the example code. With this, all the components in the application are gathered into one dictionary, so the component can access all the components with their names.

The ```with``` syntax is used here again to attach events to components. If we look at the ```__exit__``` function in the ```gradio.blocks.Blocks``` class, we can see that it is calling the ```attach_load_events``` function which is used for setting event triggers to components. So we have to use the ```with``` syntax to trigger the ```__exit__``` function.

Of course, we can call ```attach_load_events``` without using the ```with``` syntax, but the function needs a ```Context.root_block```, and it is set in the ```__enter__``` function. So we used the ```with``` syntax here rather than calling the function ourselves.

## Conclusion

In this guide, we saw

- How we can wrap the layouts
- How components are rendered
- How we can structure our application with wrapped layout classes

Because the classes used in this guide are used for demonstration purposes, they may still not be totally optimized or modular. But that would make the guide much longer!

I hope this guide helps you gain another view of the layout classes and gives you an idea about how you can use them for your needs. See the full implementation of our example [here](https://huggingface.co/spaces/WoWoWoWololo/wrapping-layouts/blob/main/app.py).

