# gradio-app/gradio/guides

[git-collector-data]

**URL:** https://github.com/gradio-app/gradio/tree/main/guides  
**Date:** 6/3/2025, 3:30:07 PM  
**Files:** 9  

=== File: guides/08_custom-components/01_custom-components-in-five-minutes.md ===
# Custom Components in 5 minutes

Gradio includes the ability for developers to create their own custom components and use them in Gradio apps. You can publish your components as Python packages so that other users can use them as well.

Users will be able to use all of Gradio's existing functions, such as `gr.Blocks`, `gr.Interface`, API usage, themes, etc. with Custom Components. This guide will cover how to get started making custom components.

## Installation

You will need to have:

* Python 3.10+ (<a href="https://www.python.org/downloads/" target="_blank">install here</a>)
* pip 21.3+ (`python -m pip install --upgrade pip`)
* Node.js 20+ (<a href="https://nodejs.dev/en/download/package-manager/" target="_blank">install here</a>)
* npm 9+ (<a href="https://docs.npmjs.com/downloading-and-installing-node-js-and-npm/" target="_blank">install here</a>)
* Gradio 5+ (`pip install --upgrade gradio`)

## The Workflow

The Custom Components workflow consists of 4 steps: create, dev, build, and publish.

1. create: creates a template for you to start developing a custom component.
2. dev: launches a development server with a sample app & hot reloading allowing you to easily develop your custom component
3. build: builds a python package containing to your custom component's Python and JavaScript code -- this makes things official!
4. publish: uploads your package to [PyPi](https://pypi.org/) and/or a sample app to [HuggingFace Spaces](https://hf.co/spaces).

Each of these steps is done via the Custom Component CLI. You can invoke it with `gradio cc` or `gradio component`

Tip: Run `gradio cc --help` to get a help menu of all available commands. There are some commands that are not covered in this guide. You can also append `--help` to any command name to bring up a help page for that command, e.g. `gradio cc create --help`.

## 1. create

Bootstrap a new template by running the following in any working directory:

```bash
gradio cc create MyComponent --template SimpleTextbox
```

Instead of `MyComponent`, give your component any name.

Instead of `SimpleTextbox`, you can use any Gradio component as a template. `SimpleTextbox` is actually a special component that a stripped-down version of the `Textbox` component that makes it particularly useful when creating your first custom component.
Some other components that are good if you are starting out: `SimpleDropdown`, `SimpleImage`, or `File`.

Tip: Run `gradio cc show` to get a list of available component templates.

The `create` command will:

1. Create a directory with your component's name in lowercase with the following structure:
```directory
- backend/ <- The python code for your custom component
- frontend/ <- The javascript code for your custom component
- demo/ <- A sample app using your custom component. Modify this to develop your component!
- pyproject.toml <- Used to build the package and specify package metadata.
```

2. Install the component in development mode

Each of the directories will have the code you need to get started developing!

## 2. dev

Once you have created your new component, you can start a development server by `entering the directory` and running

```bash
gradio cc dev
```

You'll see several lines that are printed to the console.
The most important one is the one that says:

> Frontend Server (Go here): http://localhost:7861/

The port number might be different for you.
Click on that link to launch the demo app in hot reload mode.
Now, you can start making changes to the backend and frontend you'll see the results reflected live in the sample app!
We'll go through a real example in a later guide.

Tip: You don't have to run dev mode from your custom component directory. The first argument to `dev` mode is the path to the directory. By default it uses the current directory.

## 3. build

Once you are satisfied with your custom component's implementation, you can `build` it to use it outside of the development server.

From your component directory, run:

```bash
gradio cc build
```

This will create a `tar.gz` and `.whl` file in a `dist/` subdirectory.
If you or anyone installs that `.whl` file (`pip install <path-to-whl>`) they will be able to use your custom component in any gradio app!

The `build` command will also generate documentation for your custom component. This takes the form of an interactive space and a static `README.md`. You can disable this by passing `--no-generate-docs`. You can read more about the documentation generator in [the dedicated guide](https://gradio.app/guides/documenting-custom-components).

## 4. publish

Right now, your package is only available on a `.whl` file on your computer.
You can share that file with the world with the `publish` command!

Simply run the following command from your component directory:

```bash
gradio cc publish
```

This will guide you through the following process:

1. Upload your distribution files to PyPi. This makes it easier to upload the demo to Hugging Face spaces. Otherwise your package must be at a publicly available url. If you decide to upload to PyPi, you will need a PyPI username and password. You can get one [here](https://pypi.org/account/register/).
2. Upload a demo of your component to hugging face spaces. This is also optional.


Here is an example of what publishing looks like:

<video autoplay muted loop>
  <source src="https://gradio-builds.s3.amazonaws.com/assets/text_with_attachments_publish.mov" type="video/mp4" />
</video>


## Conclusion

Now that you know the high-level workflow of creating custom components, you can go in depth in the next guides!
After reading the guides, check out this [collection](https://huggingface.co/collections/gradio/custom-components-65497a761c5192d981710b12) of custom components on the HuggingFace Hub so you can learn from other's code.

Tip: If you want to start off from someone else's custom component see this [guide](./frequently-asked-questions#do-i-always-need-to-start-my-component-from-scratch).


=== File: guides/08_custom-components/02_key-component-concepts.md ===
# Gradio Components: The Key Concepts

In this section, we discuss a few important concepts when it comes to components in Gradio.
It's important to understand these concepts when developing your own component.
Otherwise, your component may behave very different to other Gradio components!

Tip:  You can skip this section if you are familiar with the internals of the Gradio library, such as each component's preprocess and postprocess methods.

## Interactive vs Static

Every component in Gradio comes in a `static` variant, and most come in an `interactive` version as well.
The `static` version is used when a component is displaying a value, and the user can **NOT** change that value by interacting with it. 
The `interactive` version is used when the user is able to change the value by interacting with the Gradio UI.

Let's see some examples:

```python
import gradio as gr

with gr.Blocks() as demo:
   gr.Textbox(value="Hello", interactive=True)
   gr.Textbox(value="Hello", interactive=False)

demo.launch()

```
This will display two textboxes.
The only difference: you'll be able to edit the value of the Gradio component on top, and you won't be able to edit the variant on the bottom (i.e. the textbox will be disabled).

Perhaps a more interesting example is with the `Image` component:

```python
import gradio as gr

with gr.Blocks() as demo:
   gr.Image(interactive=True)
   gr.Image(interactive=False)

demo.launch()
```

The interactive version of the component is much more complex -- you can upload images or snap a picture from your webcam -- while the static version can only be used to display images.

Not every component has a distinct interactive version. For example, the `gr.AnnotatedImage` only appears as a static version since there's no way to interactively change the value of the annotations or the image.

### What you need to remember

* Gradio will use the interactive version (if available) of a component if that component is used as the **input** to any event; otherwise, the static version will be used.

* When you design custom components, you **must** accept the boolean interactive keyword in the constructor of your Python class. In the frontend, you **may** accept the `interactive` property, a `bool` which represents whether the component should be static or interactive. If you do not use this property in the frontend, the component will appear the same in interactive or static mode.

## The value and how it is preprocessed/postprocessed

The most important attribute of a component is its `value`.
Every component has a `value`.
The value that is typically set by the user in the frontend (if the component is interactive) or displayed to the user (if it is static). 
It is also this value that is sent to the backend function when a user triggers an event, or returned by the user's function e.g. at the end of a prediction.

So this value is passed around quite a bit, but sometimes the format of the value needs to change between the frontend and backend. 
Take a look at this example:

```python
import numpy as np
import gradio as gr

def sepia(input_img):
    sepia_filter = np.array([
        [0.393, 0.769, 0.189], 
        [0.349, 0.686, 0.168], 
        [0.272, 0.534, 0.131]
    ])
    sepia_img = input_img.dot(sepia_filter.T)
    sepia_img /= sepia_img.max()
    return sepia_img

demo = gr.Interface(sepia, gr.Image(width=200, height=200), "image")
demo.launch()
```

This will create a Gradio app which has an `Image` component as the input and the output. 
In the frontend, the Image component will actually **upload** the file to the server and send the **filepath** but this is converted to a `numpy` array before it is sent to a user's function. 
Conversely, when the user returns a `numpy` array from their function, the numpy array is converted to a file so that it can be sent to the frontend and displayed by the `Image` component.

Tip: By default, the `Image` component sends numpy arrays to the python function because it is a common choice for machine learning engineers, though the Image component also supports other formats using the `type` parameter.  Read the `Image` docs [here](https://www.gradio.app/docs/image) to learn more.

Each component does two conversions:

1. `preprocess`: Converts the `value` from the format sent by the frontend to the format expected by the python function. This usually involves going from a web-friendly **JSON** structure to a **python-native** data structure, like a `numpy` array or `PIL` image. The `Audio`, `Image` components are good examples of `preprocess` methods.

2. `postprocess`: Converts the value returned by the python function to the format expected by the frontend. This usually involves going from a **python-native** data-structure, like a `PIL` image to a **JSON** structure.

### What you need to remember

* Every component must implement `preprocess` and `postprocess` methods. In the rare event that no conversion needs to happen, simply return the value as-is. `Textbox` and `Number` are examples of this. 

* As a component author, **YOU** control the format of the data displayed in the frontend as well as the format of the data someone using your component will receive. Think of an ergonomic data-structure a **python** developer will find intuitive, and control the conversion from a **Web-friendly JSON** data structure (and vice-versa) with `preprocess` and `postprocess.`

## The "Example Version" of a Component

Gradio apps support providing example inputs -- and these are very useful in helping users get started using your Gradio app. 
In `gr.Interface`, you can provide examples using the `examples` keyword, and in `Blocks`, you can provide examples using the special `gr.Examples` component.

At the bottom of this screenshot, we show a miniature example image of a cheetah that, when clicked, will populate the same image in the input Image component:

![img](https://user-images.githubusercontent.com/1778297/277548211-a3cb2133-2ffc-4cdf-9a83-3e8363b57ea6.png)


To enable the example view, you must have the following two files in the top of the `frontend` directory:

* `Example.svelte`: this corresponds to the "example version" of your component
* `Index.svelte`: this corresponds to the "regular version"

In the backend, you typically don't need to do anything. The user-provided example `value` is processed using the same `.postprocess()` method described earlier. If you'd like to do process the data differently (for example, if the `.postprocess()` method is computationally expensive), then you can write your own `.process_example()` method for your custom component, which will be used instead. 

The `Example.svelte` file and `process_example()` method will be covered in greater depth in the dedicated [frontend](./frontend) and [backend](./backend) guides respectively.

### What you need to remember

* If you expect your component to be used as input, it is important to define an "Example" view.
* If you don't, Gradio will use a default one but it won't be as informative as it can be!

## Conclusion

Now that you know the most important pieces to remember about Gradio components, you can start to design and build your own!


=== File: guides/08_custom-components/03_configuration.md ===
# Configuring Your Custom Component

The custom components workflow focuses on [convention over configuration](https://en.wikipedia.org/wiki/Convention_over_configuration) to reduce the number of decisions you as a developer need to make when developing your custom component.
That being said, you can still configure some aspects of the custom component package and directory.
This guide will cover how.

## The Package Name

By default, all custom component packages are called `gradio_<component-name>` where `component-name` is the name of the component's python class in lowercase.

As an example, let's walkthrough changing the name of a component from `gradio_mytextbox` to `supertextbox`. 

1. Modify the `name` in the `pyproject.toml` file. 

```bash
[project]
name = "supertextbox"
```

2. Change all occurrences of `gradio_<component-name>` in `pyproject.toml` to `<component-name>`

```bash
[tool.hatch.build]
artifacts = ["/backend/supertextbox/templates", "*.pyi"]

[tool.hatch.build.targets.wheel]
packages = ["/backend/supertextbox"]
```

3. Rename the `gradio_<component-name>` directory in `backend/` to `<component-name>`

```bash
mv backend/gradio_mytextbox backend/supertextbox
```


Tip: Remember to change the import statement in `demo/app.py`!

## Top Level Python Exports

By default, only the custom component python class is a top level export. 
This means that when users type `from gradio_<component-name> import ...`, the only class that will be available is the custom component class.
To add more classes as top level exports, modify the `__all__` property in `__init__.py`

```python
from .mytextbox import MyTextbox
from .mytextbox import AdditionalClass, additional_function

__all__ = ['MyTextbox', 'AdditionalClass', 'additional_function']
```

## Python Dependencies

You can add python dependencies by modifying the `dependencies` key in `pyproject.toml`

```bash
dependencies = ["gradio", "numpy", "PIL"]
```


Tip: Remember to run `gradio cc install` when you add dependencies!

## Javascript Dependencies

You can add JavaScript dependencies by modifying the `"dependencies"` key in `frontend/package.json`

```json
"dependencies": {
    "@gradio/atoms": "0.2.0-beta.4",
    "@gradio/statustracker": "0.3.0-beta.6",
    "@gradio/utils": "0.2.0-beta.4",
    "your-npm-package": "<version>"
}
```

## Directory Structure

By default, the CLI will place the Python code in `backend` and the JavaScript code in `frontend`.
It is not recommended to change this structure since it makes it easy for a potential contributor to look at your source code and know where everything is.
However, if you did want to this is what you would have to do:

1. Place the Python code in the subdirectory of your choosing. Remember to modify the `[tool.hatch.build]` `[tool.hatch.build.targets.wheel]` in the `pyproject.toml` to match!

2. Place the JavaScript code in the subdirectory of your choosing.

2. Add the `FRONTEND_DIR` property on the component python class. It must be the relative path from the file where the class is defined to the location of the JavaScript directory.

```python
class SuperTextbox(Component):
    FRONTEND_DIR = "../../frontend/"
```

The JavaScript and Python directories must be under the same common directory!

## Conclusion


Sticking to the defaults will make it easy for others to understand and contribute to your custom component.
After all, the beauty of open source is that anyone can help improve your code!
But if you ever need to deviate from the defaults, you know how!

=== File: guides/08_custom-components/04_backend.md ===
# The Backend 🐍

This guide will cover everything you need to know to implement your custom component's backend processing.

## Which Class to Inherit From

All components inherit from one of three classes `Component`, `FormComponent`, or `BlockContext`.
You need to inherit from one so that your component behaves like all other gradio components.
When you start from a template with `gradio cc create --template`, you don't need to worry about which one to choose since the template uses the correct one. 
For completeness, and in the event that you need to make your own component from scratch, we explain what each class is for.

* `FormComponent`: Use this when you want your component to be grouped together in the same `Form` layout with other `FormComponents`. The `Slider`, `Textbox`, and `Number` components are all `FormComponents`.
* `BlockContext`: Use this when you want to place other components "inside" your component. This enabled `with MyComponent() as component:` syntax.
* `Component`: Use this for all other cases.

Tip: If your component supports streaming output, inherit from the `StreamingOutput` class.

Tip: If you inherit from `BlockContext`, you also need to set the metaclass to be `ComponentMeta`. See example below.

```python
from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta




@document()
class Row(BlockContext, metaclass=ComponentMeta):
    pass
```

## The methods you need to implement

When you inherit from any of these classes, the following methods must be implemented.
Otherwise the Python interpreter will raise an error when you instantiate your component!

### `preprocess` and `postprocess`

Explained in the [Key Concepts](./key-component-concepts#the-value-and-how-it-is-preprocessed-postprocessed) guide. 
They handle the conversion from the data sent by the frontend to the format expected by the python function.

```python
    def preprocess(self, x: Any) -> Any:
        """
        Convert from the web-friendly (typically JSON) value in the frontend to the format expected by the python function.
        """
        return x

    def postprocess(self, y):
        """
        Convert from the data returned by the python function to the web-friendly (typically JSON) value expected by the frontend.
        """
        return y
```

### `process_example`

Takes in the original Python value and returns the modified value that should be displayed in the examples preview in the app. 
If not provided, the `.postprocess()` method is used instead. Let's look at the following example from the `SimpleDropdown` component.

```python
def process_example(self, input_data):
    return next((c[0] for c in self.choices if c[1] == input_data), None)
```

Since `self.choices` is a list of tuples corresponding to (`display_name`, `value`), this converts the value that a user provides to the display value (or if the value is not present in `self.choices`, it is converted to `None`).


### `api_info`

A JSON-schema representation of the value that the `preprocess` expects. 
This powers api usage via the gradio clients. 
You do **not** need to implement this yourself if you components specifies a `data_model`. 
The `data_model` in the following section.

```python
def api_info(self) -> dict[str, list[str]]:
    """
    A JSON-schema representation of the value that the `preprocess` expects and the `postprocess` returns.
    """
    pass
```

### `example_payload`

An example payload for your component, e.g. something that can be passed into the `.preprocess()` method
of your component. The example input is displayed in the `View API` page of a Gradio app that uses your custom component. 
Must be JSON-serializable. If your component expects a file, it is best to use a publicly accessible URL.

```python
def example_payload(self) -> Any:
    """
    The example inputs for this component for API usage. Must be JSON-serializable.
    """
    pass
```

### `example_value`

An example value for your component, e.g. something that can be passed into the `.postprocess()` method
of your component. This is used as the example value in the default app that is created in custom component development.

```python
def example_payload(self) -> Any:
    """
    The example inputs for this component for API usage. Must be JSON-serializable.
    """
    pass
```

### `flag`

Write the component's value to a format that can be stored in the `csv` or `json` file used for flagging.
You do **not** need to implement this yourself if you components specifies a `data_model`. 
The `data_model` in the following section.

```python
def flag(self, x: Any | GradioDataModel, flag_dir: str | Path = "") -> str:
    pass
```

### `read_from_flag`
Convert from the format stored in the `csv` or `json` file used for flagging to the component's python `value`.
You do **not** need to implement this yourself if you components specifies a `data_model`. 
The `data_model` in the following section.

```python
def read_from_flag(
    self,
    x: Any,
) -> GradioDataModel | Any:
    """
    Convert the data from the csv or jsonl file into the component state.
    """
    return x
```

## The `data_model`

The `data_model` is how you define the expected data format your component's value will be stored in the frontend.
It specifies the data format your `preprocess` method expects and the format the `postprocess` method returns.
It is not necessary to define a `data_model` for your component but it greatly simplifies the process of creating a custom component.
If you define a custom component you only need to implement four methods - `preprocess`, `postprocess`, `example_payload`, and `example_value`!

You define a `data_model` by defining a [pydantic model](https://docs.pydantic.dev/latest/concepts/models/#basic-model-usage) that inherits from either `GradioModel` or `GradioRootModel`.

This is best explained with an example. Let's look at the core `Video` component, which stores the video data as a JSON object with two keys `video` and `subtitles` which point to separate files.

```python
from gradio.data_classes import FileData, GradioModel

class VideoData(GradioModel):
    video: FileData
    subtitles: Optional[FileData] = None

class Video(Component):
    data_model = VideoData
```

By adding these four lines of code, your component automatically implements the methods needed for API usage, the flagging methods, and example caching methods!
It also has the added benefit of self-documenting your code.
Anyone who reads your component code will know exactly the data it expects.

Tip: If your component expects files to be uploaded from the frontend, your must use the `FileData` model! It will be explained in the following section. 

Tip: Read the pydantic docs [here](https://docs.pydantic.dev/latest/concepts/models/#basic-model-usage).

The difference between a `GradioModel` and a `GradioRootModel` is that the `RootModel` will not serialize the data to a dictionary.
For example, the `Names` model will serialize the data to `{'names': ['freddy', 'pete']}` whereas the `NamesRoot` model will serialize it to `['freddy', 'pete']`.

```python
from typing import List

class Names(GradioModel):
    names: List[str]

class NamesRoot(GradioRootModel):
    root: List[str]
```

Even if your component does not expect a "complex" JSON data structure it can be beneficial to define a `GradioRootModel` so that you don't have to worry about implementing the API and flagging methods.

Tip: Use classes from the Python typing library to type your models. e.g. `List` instead of `list`.

## Handling Files

If your component expects uploaded files as input, or returns saved files to the frontend, you **MUST** use the `FileData` to type the files in your `data_model`.

When you use the `FileData`:

* Gradio knows that it should allow serving this file to the frontend. Gradio automatically blocks requests to serve arbitrary files in the computer running the server.

* Gradio will automatically place the file in a cache so that duplicate copies of the file don't get saved.

* The client libraries will automatically know that they should upload input files prior to sending the request. They will also automatically download files.

If you do not use the `FileData`, your component will not work as expected!


## Adding Event Triggers To Your Component

The events triggers for your component are defined in the `EVENTS` class attribute.
This is a list that contains the string names of the events.
Adding an event to this list will automatically add a method with that same name to your component!

You can import the `Events` enum from `gradio.events` to access commonly used events in the core gradio components.

For example, the following code will define `text_submit`, `file_upload` and `change` methods in the `MyComponent` class.

```python
from gradio.events import Events
from gradio.components import FormComponent

class MyComponent(FormComponent):

    EVENTS = [
        "text_submit",
        "file_upload",
        Events.change
    ]
```


Tip: Don't forget to also handle these events in the JavaScript code!

## Conclusion



=== File: guides/08_custom-components/05_frontend.md ===
# The Frontend 🌐⭐️

This guide will cover everything you need to know to implement your custom component's frontend.

Tip: Gradio components use Svelte. Writing Svelte is fun! If you're not familiar with it, we recommend checking out their interactive [guide](https://learn.svelte.dev/tutorial/welcome-to-svelte).

## The directory structure 

The frontend code should have, at minimum, three files:

* `Index.svelte`: This is the main export and where your component's layout and logic should live.
* `Example.svelte`: This is where the example view of the component is defined.

Feel free to add additional files and subdirectories. 
If you want to export any additional modules, remember to modify the `package.json` file

```json
"exports": {
    ".": "./Index.svelte",
    "./example": "./Example.svelte",
    "./package.json": "./package.json"
},
```

## The Index.svelte file

Your component should expose the following props that will be passed down from the parent Gradio application.

```typescript
import type { LoadingStatus } from "@gradio/statustracker";
import type { Gradio } from "@gradio/utils";

export let gradio: Gradio<{
    event_1: never;
    event_2: never;
}>;

export let elem_id = "";
export let elem_classes: string[] = [];
export let scale: number | null = null;
export let min_width: number | undefined = undefined;
export let loading_status: LoadingStatus | undefined = undefined;
export let mode: "static" | "interactive";
```

* `elem_id` and `elem_classes` allow Gradio app developers to target your component with custom CSS and JavaScript from the Python `Blocks` class.

* `scale` and `min_width` allow Gradio app developers to control how much space your component takes up in the UI.

* `loading_status` is used to display a loading status over the component when it is the output of an event.

* `mode` is how the parent Gradio app tells your component whether the `interactive` or `static` version should be displayed.

* `gradio`: The `gradio` object is created by the parent Gradio app. It stores some application-level configuration that will be useful in your component, like internationalization. You must use it to dispatch events from your component.

A minimal `Index.svelte` file would look like:

```svelte
<script lang="ts">
	import type { LoadingStatus } from "@gradio/statustracker";
    import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { Gradio } from "@gradio/utils";

	export let gradio: Gradio<{
		event_1: never;
		event_2: never;
	}>;

    export let value = "";
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus | undefined = undefined;
    export let mode: "static" | "interactive";
</script>

<Block
	visible={true}
	{elem_id}
	{elem_classes}
	{scale}
	{min_width}
	allow_overflow={false}
	padding={true}
>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
		/>
	{/if}
    <p>{value}</p>
</Block>
```

## The Example.svelte file

The `Example.svelte` file should expose the following props:

```typescript
    export let value: string;
    export let type: "gallery" | "table";
    export let selected = false;
    export let index: number;
```

* `value`: The example value that should be displayed.

* `type`: This is a variable that can be either `"gallery"` or `"table"` depending on how the examples are displayed. The `"gallery"` form is used when the examples correspond to a single input component, while the `"table"` form is used when a user has multiple input components, and the examples need to populate all of them. 

* `selected`: You can also adjust how the examples are displayed if a user "selects" a particular example by using the selected variable.

* `index`: The current index of the selected value.

* Any additional props your "non-example" component takes!

This is the `Example.svelte` file for the code `Radio` component:

```svelte
<script lang="ts">
	export let value: string;
	export let type: "gallery" | "table";
	export let selected = false;
</script>

<div
	class:table={type === "table"}
	class:gallery={type === "gallery"}
	class:selected
>
	{value}
</div>

<style>
	.gallery {
		padding: var(--size-1) var(--size-2);
	}
</style>
```

## Handling Files

If your component deals with files, these files **should** be uploaded to the backend server. 
The `@gradio/client` npm package provides the `upload` and `prepare_files` utility functions to help you do this.

The `prepare_files` function will convert the browser's `File` datatype to gradio's internal `FileData` type.
You should use the `FileData` data in your component to keep track of uploaded files.

The `upload` function will upload an array of `FileData` values to the server.

Here's an example of loading files from an `<input>` element when its value changes.


```svelte
<script lang="ts">
    import { upload, prepare_files, type FileData } from "@gradio/client";
    export let root;
    export let value;
    let uploaded_files;

    async function handle_upload(file_data: FileData[]): Promise<void> {
        await tick();
        uploaded_files = await upload(file_data, root);
    }

    async function loadFiles(files: FileList): Promise<void> {
        let _files: File[] = Array.from(files);
        if (!files.length) {
            return;
        }
        if (file_count === "single") {
            _files = [files[0]];
        }
        let file_data = await prepare_files(_files);
        await handle_upload(file_data);
    }

    async function loadFilesFromUpload(e: Event): Promise<void> {
		const target = e.target;

		if (!target.files) return;
		await loadFiles(target.files);
	}
</script>

<input
    type="file"
    on:change={loadFilesFromUpload}
    multiple={true}
/>
```

The component exposes a prop named `root`. 
This is passed down by the parent gradio app and it represents the base url that the files will be uploaded to and fetched from.

For WASM support, you should get the upload function from the `Context` and pass that as the third parameter of the `upload` function.

```typescript
<script lang="ts">
    import { getContext } from "svelte";
    const upload_fn = getContext<typeof upload_files>("upload_files");

    async function handle_upload(file_data: FileData[]): Promise<void> {
        await tick();
        await upload(file_data, root, upload_fn);
    }
</script>
```

## Leveraging Existing Gradio Components

Most of Gradio's frontend components are published on [npm](https://www.npmjs.com/), the javascript package repository.
This means that you can use them to save yourself time while incorporating common patterns in your component, like uploading files.
For example, the `@gradio/upload` package has `Upload` and `ModifyUpload` components for properly uploading files to the Gradio server. 
Here is how you can use them to create a user interface to upload and display PDF files.

```svelte
<script>
	import { type FileData, Upload, ModifyUpload } from "@gradio/upload";
	import { Empty, UploadText, BlockLabel } from "@gradio/atoms";
</script>

<BlockLabel Icon={File} label={label || "PDF"} />
{#if value === null && interactive}
    <Upload
        filetype="application/pdf"
        on:load={handle_load}
        {root}
        >
        <UploadText type="file" i18n={gradio.i18n} />
    </Upload>
{:else if value !== null}
    {#if interactive}
        <ModifyUpload i18n={gradio.i18n} on:clear={handle_clear}/>
    {/if}
    <iframe title={value.orig_name || "PDF"} src={value.data} height="{height}px" width="100%"></iframe>
{:else}
    <Empty size="large"> <File/> </Empty>	
{/if}
```

You can also combine existing Gradio components to create entirely unique experiences.
Like rendering a gallery of chatbot conversations. 
The possibilities are endless, please read the documentation on our javascript packages [here](https://gradio.app/main/docs/js).
We'll be adding more packages and documentation over the coming weeks!

## Matching Gradio Core's Design System

You can explore our component library via Storybook. You'll be able to interact with our components and see them in their various states.

For those interested in design customization, we provide the CSS variables consisting of our color palette, radii, spacing, and the icons we use - so you can easily match up your custom component with the style of our core components. This Storybook will be regularly updated with any new additions or changes.

[Storybook Link](https://gradio.app/main/docs/js/storybook)

## Custom configuration

If you want to make use of the vast vite ecosystem, you can use the `gradio.config.js` file to configure your component's build process. This allows you to make use of tools like tailwindcss, mdsvex, and more.

Currently, it is possible to configure the following:

Vite options:
- `plugins`: A list of vite plugins to use.

Svelte options:
- `preprocess`: A list of svelte preprocessors to use.
- `extensions`: A list of file extensions to compile to `.svelte` files.
- `build.target`: The target to build for, this may be necessary to support newer javascript features. See the [esbuild docs](https://esbuild.github.io/api/#target) for more information.

The `gradio.config.js` file should be placed in the root of your component's `frontend` directory. A default config file is created for you when you create a new component. But you can also create your own config file, if one doesn't exist, and use it to customize your component's build process.

### Example for a Vite plugin

Custom components can use Vite plugins to customize the build process. Check out the [Vite Docs](https://vitejs.dev/guide/using-plugins.html) for more information. 

Here we configure [TailwindCSS](https://tailwindcss.com), a utility-first CSS framework. Setup is easiest using the version 4 prerelease. 

```
npm install tailwindcss@next @tailwindcss/vite@next
```

In `gradio.config.js`:

```typescript
import tailwindcss from "@tailwindcss/vite";
export default {
    plugins: [tailwindcss()]
};
```

Then create a `style.css` file with the following content:

```css
@import "tailwindcss";
```

Import this file into `Index.svelte`. Note, that you need to import the css file containing `@import` and cannot just use a `<style>` tag and use `@import` there. 

```svelte
<script lang="ts">
[...]
import "./style.css";
[...]
</script>
```

### Example for Svelte options

In `gradio.config.js` you can also specify a some Svelte options to apply to the Svelte compilation. In this example we will add support for [`mdsvex`](https://mdsvex.pngwn.io), a Markdown preprocessor for Svelte. 

In order to do this we will need to add a [Svelte Preprocessor](https://svelte.dev/docs/svelte-compiler#preprocess) to the `svelte` object in `gradio.config.js` and configure the [`extensions`](https://github.com/sveltejs/vite-plugin-svelte/blob/HEAD/docs/config.md#config-file) field. Other options are not currently supported.

First, install the `mdsvex` plugin:

```bash
npm install mdsvex
```

Then add the following to `gradio.config.js`:

```typescript
import { mdsvex } from "mdsvex";

export default {
    svelte: {
        preprocess: [
            mdsvex()
        ],
        extensions: [".svelte", ".svx"]
    }
};
```

Now we can create `mdsvex` documents in our component's `frontend` directory and they will be compiled to `.svelte` files.

```md
<!-- HelloWorld.svx -->

<script lang="ts">
    import { Block } from "@gradio/atoms";

    export let title = "Hello World";
</script>

<Block label="Hello World">

# {title}

This is a markdown file.

</Block>
```

We can then use the `HelloWorld.svx` file in our components:

```svelte
<script lang="ts">
    import HelloWorld from "./HelloWorld.svx";
</script>

<HelloWorld />
```

## Conclusion

You now know how to create delightful frontends for your components!



=== File: guides/08_custom-components/06_frequently-asked-questions.md ===
# Frequently Asked Questions

## What do I need to install before using Custom Components?

Before using Custom Components, make sure you have Python 3.10+, Node.js v18+, npm 9+, and Gradio 4.0+ (preferably Gradio 5.0+) installed.

## Are custom components compatible between Gradio 4.0 and 5.0?

Custom components built with Gradio 5.0 should be compatible with Gradio 4.0. If you built your custom component in Gradio 4.0 you will have to rebuild your component to be compatible with Gradio 5.0. Simply follow these steps:
1. Update the `@gradio/preview` package. `cd` into the `frontend` directory and run `npm update`.
2.  Modify the `dependencies` key in `pyproject.toml` to pin the maximum allowed Gradio version at version 5, e.g. `dependencies = ["gradio>=4.0,<6.0"]`.
3. Run the build and publish commands

## What templates can I use to create my custom component?
Run `gradio cc show` to see the list of built-in templates.
You can also start off from other's custom components!
Simply `git clone` their repository and make your modifications.

## What is the development server?
When you run `gradio cc dev`, a development server will load and run a Gradio app of your choosing.
This is like when you run `python <app-file>.py`, however the `gradio` command will hot reload so you can instantly see your changes. 

## The development server didn't work for me 

**1. Check your terminal and browser console**

Make sure there are no syntax errors or other obvious problems in your code. Exceptions triggered from python will be displayed in the terminal. Exceptions from javascript will be displayed in the browser console and/or the terminal.

**2. Are you developing on Windows?**

Chrome on Windows will block the local compiled svelte files for security reasons. We recommend developing your custom component in the windows subsystem for linux (WSL) while the team looks at this issue.

**3. Inspect the window.__GRADIO_CC__ variable**

In the browser console, print the `window.__GRADIO__CC` variable (just type it into the console). If it is an empty object, that means
that the CLI could not find your custom component source code. Typically, this happens when the custom component is installed in a different virtual environment than the one used to run the dev command. Please use the `--python-path` and `gradio-path` CLI arguments to specify the path of the python and gradio executables for the environment your component is installed in. For example, if you are using a virtualenv located at `/Users/mary/venv`, pass in `/Users/mary/bin/python` and `/Users/mary/bin/gradio` respectively.

If the `window.__GRADIO__CC` variable is not empty (see below for an example), then the dev server should be working correctly. 

![](https://gradio-builds.s3.amazonaws.com/demo-files/gradio_CC_DEV.png)

**4. Make sure you are using a virtual environment**
It is highly recommended you use a virtual environment to prevent conflicts with other python dependencies installed in your system.


## Do I always need to start my component from scratch?
No! You can start off from an existing gradio component as a template, see the [five minute guide](./custom-components-in-five-minutes).
You can also start from an existing custom component if you'd like to tweak it further. Once you find the source code of a custom component you like, clone the code to your computer and run `gradio cc install`. Then you can run the development server to make changes.If you run into any issues, contact the author of the component by opening an issue in their repository. The [gallery](https://www.gradio.app/custom-components/gallery) is a good place to look for published components. For example, to start from the [PDF component](https://www.gradio.app/custom-components/gallery?id=freddyaboulton%2Fgradio_pdf), clone the space with `git clone https://huggingface.co/spaces/freddyaboulton/gradio_pdf`, `cd` into the `src` directory, and run `gradio cc install`.


## Do I need to host my custom component on HuggingFace Spaces?
You can develop and build your custom component without hosting or connecting to HuggingFace.
If you would like to share your component with the gradio community, it is recommended to publish your package to PyPi and host a demo on HuggingFace so that anyone can install it or try it out.

## What methods are mandatory for implementing a custom component in Gradio?

You must implement the `preprocess`, `postprocess`, `example_payload`, and `example_value` methods. If your component does not use a data model, you must also define the `api_info`, `flag`, and `read_from_flag` methods. Read more in the [backend guide](./backend).

## What is the purpose of a `data_model` in Gradio custom components?

A `data_model` defines the expected data format for your component, simplifying the component development process and self-documenting your code. It streamlines API usage and example caching.

## Why is it important to use `FileData` for components dealing with file uploads?

Utilizing `FileData` is crucial for components that expect file uploads. It ensures secure file handling, automatic caching, and streamlined client library functionality.

## How can I add event triggers to my custom Gradio component?

You can define event triggers in the `EVENTS` class attribute by listing the desired event names, which automatically adds corresponding methods to your component.

## Can I implement a custom Gradio component without defining a `data_model`?

Yes, it is possible to create custom components without a `data_model`, but you are going to have to manually implement `api_info`, `flag`, and `read_from_flag` methods.

## Are there sample custom components I can learn from?

We have prepared this [collection](https://huggingface.co/collections/gradio/custom-components-65497a761c5192d981710b12) of custom components on the HuggingFace Hub that you can use to get started!

## How can I find custom components created by the Gradio community?

We're working on creating a gallery to make it really easy to discover new custom components.
In the meantime, you can search for HuggingFace Spaces that are tagged as a `gradio-custom-component` [here](https://huggingface.co/search/full-text?q=gradio-custom-component&type=space)

=== File: guides/08_custom-components/07_pdf-component-example.md ===
# Case Study: A Component to Display PDFs

Let's work through an example of building a custom gradio component for displaying PDF files.
This component will come in handy for showcasing [document question answering](https://huggingface.co/models?pipeline_tag=document-question-answering&sort=trending) models, which typically work on PDF input.
This is a sneak preview of what our finished component will look like:

![demo](https://gradio-builds.s3.amazonaws.com/assets/PDFDisplay.png)

## Step 0: Prerequisites
Make sure you have gradio 5.0 or higher installed as well as node 20+.
As of the time of publication, the latest release is 4.1.1.
Also, please read the [Five Minute Tour](./custom-components-in-five-minutes) of custom components and the [Key Concepts](./key-component-concepts) guide before starting.


## Step 1: Creating the custom component

Navigate to a directory of your choosing and run the following command:

```bash
gradio cc create PDF
```


Tip: You should change the name of the component.
Some of the screenshots assume the component is called `PDF` but the concepts are the same!

This will create a subdirectory called `pdf` in your current working directory.
There are three main subdirectories in `pdf`: `frontend`, `backend`, and `demo`.
If you open `pdf` in your code editor, it will look like this:

![directory structure](https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/CodeStructure.png)

Tip: For this demo we are not templating off a current gradio component. But you can see the list of available templates with `gradio cc show` and then pass the template name to the `--template` option, e.g. `gradio cc create <Name> --template <foo>`

## Step 2: Frontend - modify javascript dependencies

We're going to use the [pdfjs](https://mozilla.github.io/pdf.js/) javascript library to display the pdfs in the frontend. 
Let's start off by adding it to our frontend project's dependencies, as well as adding a couple of other projects we'll need.

From within the `frontend` directory, run `npm install @gradio/client @gradio/upload @gradio/icons @gradio/button` and `npm install --save-dev pdfjs-dist@3.11.174`.
Also, let's uninstall the `@zerodevx/svelte-json-view` dependency by running `npm uninstall @zerodevx/svelte-json-view`.

The complete `package.json` should look like this:

```json
{
  "name": "gradio_pdf",
  "version": "0.2.0",
  "description": "Gradio component for displaying PDFs",
  "type": "module",
  "author": "",
  "license": "ISC",
  "private": false,
  "main_changeset": true,
  "exports": {
    ".": "./Index.svelte",
    "./example": "./Example.svelte",
    "./package.json": "./package.json"
  },
  "devDependencies": {
    "pdfjs-dist": "3.11.174"
  },
  "dependencies": {
    "@gradio/atoms": "0.2.0",
    "@gradio/statustracker": "0.3.0",
    "@gradio/utils": "0.2.0",
    "@gradio/client": "0.7.1",
    "@gradio/upload": "0.3.2",
    "@gradio/icons": "0.2.0",
    "@gradio/button": "0.2.3",
    "pdfjs-dist": "3.11.174"
  }
}
```


Tip: Running `npm install` will install the latest version of the package available. You can install a specific version with `npm install package@<version>`.  You can find all of the gradio javascript package documentation [here](https://www.gradio.app/main/docs/js). It is recommended you use the same versions as me as the API can change.

Navigate to `Index.svelte` and delete mentions of `JSONView`

```ts
import { JsonView } from "@zerodevx/svelte-json-view";
```

```svelte
<JsonView json={value} />
```

## Step 3: Frontend - Launching the Dev Server

Run the `dev` command to launch the development server.
This will open the demo in `demo/app.py` in an environment where changes to the `frontend` and `backend` directories will reflect instantaneously in the launched app.

After launching the dev server, you should see a link printed to your console that says `Frontend Server (Go here): ... `.
 
![](https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/dev_server_terminal.png)

You should see the following:

![](https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/frontend_start.png)


Its not impressive yet but we're ready to start coding!

## Step 4: Frontend - The basic skeleton

We're going to start off by first writing the skeleton of our frontend and then adding the pdf rendering logic.
Add the following imports and expose the following properties to the top of your file in the `<script>` tag.
You may get some warnings from your code editor that some props are not used.
That's ok.

```ts
    import { tick } from "svelte";
    import type { Gradio } from "@gradio/utils";
    import { Block, BlockLabel } from "@gradio/atoms";
    import { File } from "@gradio/icons";
    import { StatusTracker } from "@gradio/statustracker";
    import type { LoadingStatus } from "@gradio/statustracker";
    import type { FileData } from "@gradio/client";
    import { Upload, ModifyUpload } from "@gradio/upload";

	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: FileData | null = null;
	export let container = true;
	export let scale: number | null = null;
	export let root: string;
	export let height: number | null = 500;
	export let label: string;
	export let proxy_url: string;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	export let gradio: Gradio<{
		change: never;
		upload: never;
	}>;

    let _value = value;
    let old_value = _value;
```


Tip: The `gradio`` object passed in here contains some metadata about the application as well as some utility methods. One of these utilities is a dispatch method. We want to dispatch change and upload events whenever our PDF is changed or updated. This line provides type hints that these are the only events we will be dispatching.

We want our frontend component to let users upload a PDF document if there isn't one already loaded.
If it is loaded, we want to display it underneath a "clear" button that lets our users upload a new document. 
We're going to use the `Upload` and `ModifyUpload` components that come with the `@gradio/upload` package to do this.
Underneath the `</script>` tag, delete all the current code and add the following:

```svelte
<Block {visible} {elem_id} {elem_classes} {container} {scale} {min_width}>
    {#if loading_status}
        <StatusTracker
            autoscroll={gradio.autoscroll}
            i18n={gradio.i18n}
            {...loading_status}
        />
    {/if}
    <BlockLabel
        show_label={label !== null}
        Icon={File}
        float={value === null}
        label={label || "File"}
    />
    {#if _value}
        <ModifyUpload i18n={gradio.i18n} absolute />
    {:else}
        <Upload
            filetype={"application/pdf"}
            file_count="single"
            {root}
        >
            Upload your PDF
        </Upload>
    {/if}
</Block>
```

You should see the following when you navigate to your app after saving your current changes:

![](https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/frontend_1.png)

## Step 5: Frontend - Nicer Upload Text

The `Upload your PDF` text looks a bit small and barebones. 
Lets customize it!

Create a new file called `PdfUploadText.svelte` and copy the following code.
Its creating a new div to display our "upload text" with some custom styling.

Tip: Notice that we're leveraging Gradio core's existing css variables here: `var(--size-60)` and `var(--body-text-color-subdued)`. This allows our component to work nicely in light mode and dark mode, as well as with Gradio's built-in themes.


```svelte
<script lang="ts">
	import { Upload as UploadIcon } from "@gradio/icons";
	export let hovered = false;

</script>

<div class="wrap">
	<span class="icon-wrap" class:hovered><UploadIcon /> </span>
    Drop PDF
    <span class="or">- or -</span>
    Click to Upload
</div>

<style>
	.wrap {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		min-height: var(--size-60);
		color: var(--block-label-text-color);
		line-height: var(--line-md);
		height: 100%;
		padding-top: var(--size-3);
	}

	.or {
		color: var(--body-text-color-subdued);
		display: flex;
	}

	.icon-wrap {
		width: 30px;
		margin-bottom: var(--spacing-lg);
	}

	@media (--screen-md) {
		.wrap {
			font-size: var(--text-lg);
		}
	}

	.hovered {
		color: var(--color-accent);
	}
</style>
```

Now import `PdfUploadText.svelte` in your `<script>` and pass it to the `Upload` component!

```svelte
	import PdfUploadText from "./PdfUploadText.svelte";

...

    <Upload
        filetype={"application/pdf"}
        file_count="single"
        {root}
    >
        <PdfUploadText />
    </Upload>
```

After saving your code, the frontend should now look like this:

![](https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/better_upload.png)

## Step 6: PDF Rendering logic

This is the most advanced javascript part.
It took me a while to figure it out!
Do not worry if you have trouble, the important thing is to not be discouraged 💪
Ask for help in the gradio [discord](https://discord.gg/hugging-face-879548962464493619) if you need and ask for help.

With that out of the way, let's start off by importing `pdfjs` and loading the code of the pdf worker from the mozilla cdn.

```ts
	import pdfjsLib from "pdfjs-dist";
    ...
    pdfjsLib.GlobalWorkerOptions.workerSrc =  "https://cdn.bootcss.com/pdf.js/3.11.174/pdf.worker.js";
```

Also create the following variables:

```ts
    let pdfDoc;
    let numPages = 1;
    let currentPage = 1;
    let canvasRef;
```

Now, we will use `pdfjs` to render a given page of the PDF onto an `html` document.
Add the following code to `Index.svelte`:

```ts
    async function get_doc(value: FileData) {
        const loadingTask = pdfjsLib.getDocument(value.url);
        pdfDoc = await loadingTask.promise;
        numPages = pdfDoc.numPages;
        render_page();
    }

    function render_page() {
    // Render a specific page of the PDF onto the canvas
        pdfDoc.getPage(currentPage).then(page => {
            const ctx  = canvasRef.getContext('2d')
            ctx.clearRect(0, 0, canvasRef.width, canvasRef.height);
            let viewport = page.getViewport({ scale: 1 });
            let scale = height / viewport.height;
            viewport = page.getViewport({ scale: scale });

            const renderContext = {
                canvasContext: ctx,
                viewport,
            };
            canvasRef.width = viewport.width;
            canvasRef.height = viewport.height;
            page.render(renderContext);
        });
    }

    // If the value changes, render the PDF of the currentPage
    $: if(JSON.stringify(old_value) != JSON.stringify(_value)) {
        if (_value){
            get_doc(_value);
        }
        old_value = _value;
        gradio.dispatch("change");
    }
```


Tip: The `$:` syntax in svelte is how you declare statements to be reactive. Whenever any of the inputs of the statement change, svelte will automatically re-run that statement.

Now place the `canvas` underneath the `ModifyUpload` component:

```svelte
<div class="pdf-canvas" style="height: {height}px">
    <canvas bind:this={canvasRef}></canvas>
</div>
```

And add the following styles to the `<style>` tag:

```svelte
<style>
    .pdf-canvas {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>
```

## Step 7: Handling The File Upload And Clear

Now for the fun part - actually rendering the PDF when the file is uploaded!
Add the following functions to the `<script>` tag:

```ts
    async function handle_clear() {
        _value = null;
        await tick();
        gradio.dispatch("change");
    }

    async function handle_upload({detail}: CustomEvent<FileData>): Promise<void> {
        value = detail;
        await tick();
        gradio.dispatch("change");
        gradio.dispatch("upload");
    }
```


Tip: The `gradio.dispatch` method is actually what is triggering the `change` or `upload` events in the backend. For every event defined in the component's backend, we will explain how to do this in Step 9, there must be at least one `gradio.dispatch("<event-name>")` call. These are called `gradio` events and they can be listended from the entire Gradio application. You can dispatch a built-in `svelte` event with the `dispatch` function. These events can only be listened to from the component's direct parent. Learn about svelte events from the [official documentation](https://learn.svelte.dev/tutorial/component-events).

Now we will run these functions whenever the `Upload` component uploads a file and whenever the `ModifyUpload` component clears the current file. The `<Upload>` component dispatches a `load` event with a payload of type `FileData` corresponding to the uploaded file. The `on:load` syntax tells `Svelte` to automatically run this function in response to the event.

```svelte
    <ModifyUpload i18n={gradio.i18n} on:clear={handle_clear} absolute />
    
    ...
    
    <Upload
        on:load={handle_upload}
        filetype={"application/pdf"}
        file_count="single"
        {root}
    >
        <PdfUploadText/>
    </Upload>
```

Congratulations! You have a working pdf uploader!

![upload-gif](https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/pdf_component_gif_docs.gif)

## Step 8: Adding buttons to navigate pages

If a user uploads a PDF document with multiple pages, they will only be able to see the first one.
Let's add some buttons to help them navigate the page.
We will use the `BaseButton` from `@gradio/button` so that they look like regular Gradio buttons.

Import the `BaseButton` and add the following functions that will render the next and previous page of the PDF.

```ts
    import { BaseButton } from "@gradio/button";

    ...

    function next_page() {
        if (currentPage >= numPages) {
            return;
        }
        currentPage++;
        render_page();
    }

    function prev_page() {
        if (currentPage == 1) {
            return;
        }
        currentPage--;
        render_page();
    }
```

Now we will add them underneath the canvas in a separate `<div>`

```svelte
    ...

    <ModifyUpload i18n={gradio.i18n} on:clear={handle_clear} absolute />
    <div class="pdf-canvas" style="height: {height}px">
        <canvas bind:this={canvasRef}></canvas>
    </div>
    <div class="button-row">
        <BaseButton on:click={prev_page}>
            ⬅️
        </BaseButton>
        <span class="page-count"> {currentPage} / {numPages} </span>
        <BaseButton on:click={next_page}>
            ➡️
        </BaseButton>
    </div>
    
    ...

<style>
    .button-row {
        display: flex;
        flex-direction: row;
        width: 100%;
        justify-content: center;
        align-items: center;
    }

    .page-count {
        margin: 0 10px;
        font-family: var(--font-mono);
    }
```

Congratulations! The frontend is almost complete 🎉

![multipage-pdf-gif](https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/pdf_multipage.gif)

## Step 8.5: The Example view

We're going to want users of our component to get a preview of the PDF if its used as an `example` in a `gr.Interface` or `gr.Examples`.

To do so, we're going to add some of the pdf rendering logic in `Index.svelte` to `Example.svelte`.


```svelte
<script lang="ts">
	export let value: string;
	export let type: "gallery" | "table";
	export let selected = false;
	import pdfjsLib from "pdfjs-dist";
	pdfjsLib.GlobalWorkerOptions.workerSrc =  "https://cdn.bootcss.com/pdf.js/3.11.174/pdf.worker.js";
	
	let pdfDoc;
	let canvasRef;

	async function get_doc(url: string) {
		const loadingTask = pdfjsLib.getDocument(url);
		pdfDoc = await loadingTask.promise;
		renderPage();
		}

	function renderPage() {
		// Render a specific page of the PDF onto the canvas
			pdfDoc.getPage(1).then(page => {
				const ctx  = canvasRef.getContext('2d')
				ctx.clearRect(0, 0, canvasRef.width, canvasRef.height);
				
				const viewport = page.getViewport({ scale: 0.2 });
				
				const renderContext = {
					canvasContext: ctx,
					viewport
				};
				canvasRef.width = viewport.width;
				canvasRef.height = viewport.height;
				page.render(renderContext);
			});
		}
	
	$: get_doc(value);
</script>

<div
	class:table={type === "table"}
	class:gallery={type === "gallery"}
	class:selected
	style="justify-content: center; align-items: center; display: flex; flex-direction: column;"
>
	<canvas bind:this={canvasRef}></canvas>
</div>

<style>
	.gallery {
		padding: var(--size-1) var(--size-2);
	}
</style>
```


Tip: Exercise for the reader - reduce the code duplication between `Index.svelte` and `Example.svelte` 😊


You will not be able to render examples until we make some changes to the backend code in the next step!

## Step 9: The backend

The backend changes needed are smaller.
We're almost done!

What we're going to do is:
* Add `change` and `upload` events to our component.
* Add a `height` property to let users control the height of the PDF.
* Set the `data_model` of our component to be `FileData`. This is so that Gradio can automatically cache and safely serve any files that are processed by our component.
* Modify the `preprocess` method to return a string corresponding to the path of our uploaded PDF.
* Modify the `postprocess` to turn a path to a PDF created in an event handler to a `FileData`.

When all is said an done, your component's backend code should look like this:

```python
from __future__ import annotations
from typing import Any, Callable, TYPE_CHECKING

from gradio.components.base import Component
from gradio.data_classes import FileData
from gradio import processing_utils
if TYPE_CHECKING:
    from gradio.components import Timer

class PDF(Component):

    EVENTS = ["change", "upload"]

    data_model = FileData

    def __init__(self, value: Any = None, *,
                 height: int | None = None,
                 label: str | I18nData | None = None,
                 info: str | I18nData | None = None,
                 show_label: bool | None = None,
                 container: bool = True,
                 scale: int | None = None,
                 min_width: int | None = None,
                 interactive: bool | None = None,
                 visible: bool = True,
                 elem_id: str | None = None,
                 elem_classes: list[str] | str | None = None,
                 render: bool = True,
                 load_fn: Callable[..., Any] | None = None,
                 every: Timer | float | None = None):
        super().__init__(value, label=label, info=info,
                         show_label=show_label, container=container,
                         scale=scale, min_width=min_width,
                         interactive=interactive, visible=visible,
                         elem_id=elem_id, elem_classes=elem_classes,
                         render=render, load_fn=load_fn, every=every)
        self.height = height

    def preprocess(self, payload: FileData) -> str:
        return payload.path

    def postprocess(self, value: str | None) -> FileData:
        if not value:
            return None
        return FileData(path=value)

    def example_payload(self):
        return "https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/fw9.pdf"

    def example_value(self):
        return "https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/fw9.pdf"
```

## Step 10: Add a demo and publish!

To test our backend code, let's add a more complex demo that performs Document Question and Answering with huggingface transformers.

In our `demo` directory, create a `requirements.txt` file with the following packages

```
torch
transformers
pdf2image
pytesseract
```


Tip: Remember to install these yourself and restart the dev server! You may need to install extra non-python dependencies for `pdf2image`. See [here](https://pypi.org/project/pdf2image/). Feel free to write your own demo if you have trouble.


```python
import gradio as gr
from gradio_pdf import PDF
from pdf2image import convert_from_path
from transformers import pipeline
from pathlib import Path

dir_ = Path(__file__).parent

p = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
)

def qa(question: str, doc: str) -> str:
    img = convert_from_path(doc)[0]
    output = p(img, question)
    return sorted(output, key=lambda x: x["score"], reverse=True)[0]['answer']


demo = gr.Interface(
    qa,
    [gr.Textbox(label="Question"), PDF(label="Document")],
    gr.Textbox(),
)

demo.launch()
```

See our demo in action below!

<video autoplay muted loop>
  <source src="https://gradio-builds.s3.amazonaws.com/assets/pdf-guide/PDFDemo.mov" type="video/mp4" />
</video>

Finally lets build our component with `gradio cc build` and publish it with the `gradio cc publish` command!
This will guide you through the process of uploading your component to [PyPi](https://pypi.org/) and [HuggingFace Spaces](https://huggingface.co/spaces).


Tip: You may need to add the following lines to the `Dockerfile` of your HuggingFace Space.

```Dockerfile
RUN mkdir -p /tmp/cache/
RUN chmod a+rwx -R /tmp/cache/
RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr

ENV TRANSFORMERS_CACHE=/tmp/cache/
```

## Conclusion

In order to use our new component in **any** gradio 4.0 app, simply install it with pip, e.g. `pip install gradio-pdf`. Then you can use it like the built-in `gr.File()` component (except that it will only accept and display PDF files).

Here is a simple demo with the Blocks api:

```python
import gradio as gr
from gradio_pdf import PDF

with gr.Blocks() as demo:
    pdf = PDF(label="Upload a PDF", interactive=True)
    name = gr.Textbox()
    pdf.upload(lambda f: f, pdf, name)

demo.launch()
```


I hope you enjoyed this tutorial!
The complete source code for our component is [here](https://huggingface.co/spaces/freddyaboulton/gradio_pdf/tree/main/src).
Please don't hesitate to reach out to the gradio community on the [HuggingFace Discord](https://discord.gg/hugging-face-879548962464493619) if you get stuck.


=== File: guides/08_custom-components/08_multimodal-chatbot-part1.md ===
# Build a Custom Multimodal Chatbot - Part 1

This is the first in a two part series where we build a custom Multimodal Chatbot component.
In part 1, we will modify the Gradio Chatbot component to display text and media files (video, audio, image) in the same message.
In part 2, we will build a custom Textbox component that will be able to send multimodal messages (text and media files) to the chatbot.

You can follow along with the author of this post as he implements the chatbot component in the following YouTube video!

<iframe width="560" height="315" src="https://www.youtube.com/embed/IVJkOHTBPn0?si=bs-sBv43X-RVA8ly" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

Here's a preview of what our multimodal chatbot component will look like:

![MultiModal Chatbot](https://gradio-builds.s3.amazonaws.com/assets/MultimodalChatbot.png)


## Part 1 - Creating our project

For this demo we will be tweaking the existing Gradio `Chatbot` component to display text and media files in the same message.
Let's create a new custom component directory by templating off of the `Chatbot` component source code.

```bash
gradio cc create MultimodalChatbot --template Chatbot
```

And we're ready to go!

Tip: Make sure to modify the `Author` key in the `pyproject.toml` file.

## Part 2a - The backend data_model

Open up the `multimodalchatbot.py` file in your favorite code editor and let's get started modifying the backend of our component.

The first thing we will do is create the `data_model` of our component.
The `data_model` is the data format that your python component will receive and send to the javascript client running the UI.
You can read more about the `data_model` in the [backend guide](./backend).

For our component, each chatbot message will consist of two keys: a `text` key that displays the text message and an optional list of media files that can be displayed underneath the text.

Import the `FileData` and `GradioModel` classes from `gradio.data_classes` and modify the existing `ChatbotData` class to look like the following:

```python
class FileMessage(GradioModel):
    file: FileData
    alt_text: Optional[str] = None


class MultimodalMessage(GradioModel):
    text: Optional[str] = None
    files: Optional[List[FileMessage]] = None


class ChatbotData(GradioRootModel):
    root: List[Tuple[Optional[MultimodalMessage], Optional[MultimodalMessage]]]


class MultimodalChatbot(Component):
    ...
    data_model = ChatbotData
```


Tip: The `data_model`s are implemented using `Pydantic V2`. Read the documentation [here](https://docs.pydantic.dev/latest/).

We've done the hardest part already!

## Part 2b - The pre and postprocess methods

For the `preprocess` method, we will keep it simple and pass a list of `MultimodalMessage`s to the python functions that use this component as input. 
This will let users of our component access the chatbot data with `.text` and `.files` attributes.
This is a design choice that you can modify in your implementation!
We can return the list of messages with the `root` property of the `ChatbotData` like so:

```python
def preprocess(
    self,
    payload: ChatbotData | None,
) -> List[MultimodalMessage] | None:
    if payload is None:
        return payload
    return payload.root
```


Tip: Learn about the reasoning behind the `preprocess` and `postprocess` methods in the [key concepts guide](./key-component-concepts)

In the `postprocess` method we will coerce each message returned by the python function to be a `MultimodalMessage` class. 
We will also clean up any indentation in the `text` field so that it can be properly displayed as markdown in the frontend.

We can leave the `postprocess` method as is and modify the `_postprocess_chat_messages`

```python
def _postprocess_chat_messages(
    self, chat_message: MultimodalMessage | dict | None
) -> MultimodalMessage | None:
    if chat_message is None:
        return None
    if isinstance(chat_message, dict):
        chat_message = MultimodalMessage(**chat_message)
    chat_message.text = inspect.cleandoc(chat_message.text or "")
    for file_ in chat_message.files:
        file_.file.mime_type = client_utils.get_mimetype(file_.file.path)
    return chat_message
```

Before we wrap up with the backend code, let's modify the `example_value` and `example_payload` method to return a valid dictionary representation of the `ChatbotData`:

```python
def example_value(self) -> Any:
    return [[{"text": "Hello!", "files": []}, None]]

def example_payload(self) -> Any:
    return [[{"text": "Hello!", "files": []}, None]]
```

Congrats - the backend is complete!

## Part 3a - The Index.svelte file

The frontend for the `Chatbot` component is divided into two parts - the `Index.svelte` file and the `shared/Chatbot.svelte` file.
The `Index.svelte` file applies some processing to the data received from the server and then delegates the rendering of the conversation to the `shared/Chatbot.svelte` file.
First we will modify the `Index.svelte` file to apply processing to the new data type the backend will return.

Let's begin by porting our custom types  from our python `data_model` to typescript.
Open `frontend/shared/utils.ts` and add the following type definitions at the top of the file:

```ts
export type FileMessage = {
	file: FileData;
	alt_text?: string;
};


export type MultimodalMessage = {
	text: string;
	files?: FileMessage[];
}
```

Now let's import them in `Index.svelte` and modify the type annotations for `value` and `_value`.

```ts
import type { FileMessage, MultimodalMessage } from "./shared/utils";

export let value: [
    MultimodalMessage | null,
    MultimodalMessage | null
][] = [];

let _value: [
    MultimodalMessage | null,
    MultimodalMessage | null
][];
```

We need to normalize each message to make sure each file has a proper URL to fetch its contents from.
We also need to format any embedded file links in the `text` key.
Let's add a `process_message` utility function and apply it whenever the `value` changes.

```ts
function process_message(msg: MultimodalMessage | null): MultimodalMessage | null {
    if (msg === null) {
        return msg;
    }
    msg.text = redirect_src_url(msg.text);
    msg.files = msg.files.map(normalize_messages);
    return msg;
}

$: _value = value
    ? value.map(([user_msg, bot_msg]) => [
            process_message(user_msg),
            process_message(bot_msg)
        ])
    : [];
```

## Part 3b - the Chatbot.svelte file

Let's begin similarly to the `Index.svelte` file and let's first modify the type annotations.
Import `Mulimodal` message at the top of the `<script>` section and use it to type the `value` and `old_value` variables.

```ts
import type { MultimodalMessage } from "./utils";

export let value:
    | [
            MultimodalMessage | null,
            MultimodalMessage | null
        ][]
    | null;
let old_value:
    | [
            MultimodalMessage | null,
            MultimodalMessage | null
        ][]
    | null = null;
```

We also need to modify the `handle_select` and `handle_like` functions:

```ts
function handle_select(
    i: number,
    j: number,
    message: MultimodalMessage | null
): void {
    dispatch("select", {
        index: [i, j],
        value: message
    });
}

function handle_like(
    i: number,
    j: number,
    message: MultimodalMessage | null,
    liked: boolean
): void {
    dispatch("like", {
        index: [i, j],
        value: message,
        liked: liked
    });
}
```

Now for the fun part, actually rendering the text and files in the same message!

You should see some code like the following that determines whether a file or a markdown message should be displayed depending on the type of the message:

```svelte
{#if typeof message === "string"}
    <Markdown
        {message}
        {latex_delimiters}
        {sanitize_html}
        {render_markdown}
        {line_breaks}
        on:load={scroll}
    />
{:else if message !== null && message.file?.mime_type?.includes("audio")}
    <audio
        data-testid="chatbot-audio"
        controls
        preload="metadata"
        ...
```

We will modify this code to always display the text message and then loop through the files and display all of them that are present:

```svelte
<Markdown
    message={message.text}
    {latex_delimiters}
    {sanitize_html}
    {render_markdown}
    {line_breaks}
    on:load={scroll}
/>
{#each message.files as file, k}
    {#if file !== null && file.file.mime_type?.includes("audio")}
        <audio
            data-testid="chatbot-audio"
            controls
            preload="metadata"
            src={file.file?.url}
            title={file.alt_text}
            on:play
            on:pause
            on:ended
        />
    {:else if message !== null && file.file?.mime_type?.includes("video")}
        <video
            data-testid="chatbot-video"
            controls
            src={file.file?.url}
            title={file.alt_text}
            preload="auto"
            on:play
            on:pause
            on:ended
        >
            <track kind="captions" />
        </video>
    {:else if message !== null && file.file?.mime_type?.includes("image")}
        <img
            data-testid="chatbot-image"
            src={file.file?.url}
            alt={file.alt_text}
        />
    {:else if message !== null && file.file?.url !== null}
        <a
            data-testid="chatbot-file"
            href={file.file?.url}
            target="_blank"
            download={window.__is_colab__
                ? null
                : file.file?.orig_name || file.file?.path}
        >
            {file.file?.orig_name || file.file?.path}
        </a>
    {:else if pending_message && j === 1}
        <Pending {layout} />
    {/if}
{/each}
```

We did it! 🎉

## Part 4 - The demo

For this tutorial, let's keep the demo simple and just display a static conversation between a hypothetical user and a bot.
This demo will show how both the user and the bot can send files. 
In part 2 of this tutorial series we will build a fully functional chatbot demo!

The demo code will look like the following:

```python
import gradio as gr
from gradio_multimodalchatbot import MultimodalChatbot
from gradio.data_classes import FileData

user_msg1 = {"text": "Hello, what is in this image?",
             "files": [{"file": FileData(path="https://gradio-builds.s3.amazonaws.com/diffusion_image/cute_dog.jpg")}]
             }
bot_msg1 = {"text": "It is a very cute dog",
            "files": []}

user_msg2 = {"text": "Describe this audio clip please.",
             "files": [{"file": FileData(path="cantina.wav")}]}
bot_msg2 = {"text": "It is the cantina song from Star Wars",
            "files": []}

user_msg3 = {"text": "Give me a video clip please.",
             "files": []}
bot_msg3 = {"text": "Here is a video clip of the world",
            "files": [{"file": FileData(path="world.mp4")},
                      {"file": FileData(path="cantina.wav")}]}

conversation = [[user_msg1, bot_msg1], [user_msg2, bot_msg2], [user_msg3, bot_msg3]]

with gr.Blocks() as demo:
    MultimodalChatbot(value=conversation, height=800)


demo.launch()
```


Tip: Change the filepaths so that they correspond to files on your machine. Also, if you are running in development mode, make sure the files are located in the top level of your custom component directory.

## Part 5 - Deploying and Conclusion

Let's build and deploy our demo with `gradio cc build` and `gradio cc deploy`!

You can check out our component deployed to [HuggingFace Spaces](https://huggingface.co/spaces/freddyaboulton/gradio_multimodalchatbot) and all of the source code is available [here](https://huggingface.co/spaces/freddyaboulton/gradio_multimodalchatbot/tree/main/src).

See you in the next installment of this series!

=== File: guides/08_custom-components/09_documenting-custom-components.md ===
# Documenting Custom Components

In 4.15, we added a  new `gradio cc docs` command to the Gradio CLI to generate rich documentation for your custom component. This command will generate documentation for users automatically, but to get the most out of it, you need to do a few things.

## How do I use it?

The documentation will be generated when running `gradio cc build`. You can pass the `--no-generate-docs` argument to turn off this behaviour.

There is also a standalone `docs` command that allows for greater customisation. If you are running this command manually it should be run _after_ the `version` in your `pyproject.toml` has been bumped but before building the component.

All arguments are optional.

```bash
gradio cc docs
  path # The directory of the custom component.
  --demo-dir # Path to the demo directory.
  --demo-name # Name of the demo file
  --space-url # URL of the Hugging Face Space to link to
  --generate-space # create a documentation space.
  --no-generate-space # do not create a documentation space
  --readme-path # Path to the README.md file.
  --generate-readme # create a REAMDE.md file
  --no-generate-readme # do not create a README.md file
  --suppress-demo-check # suppress validation checks and warnings
```

## What gets generated?

The `gradio cc docs` command will generate an interactive Gradio app and a static README file with various features. You can see an example here:

- [Gradio app deployed on Hugging Face Spaces]()
- [README.md rendered by GitHub]()

The README.md and space both have the following features:

- A description.
- Installation instructions.
- A fully functioning code snippet.
- Optional links to PyPi, GitHub, and Hugging Face Spaces.
- API documentation including:
  - An argument table for component initialisation showing types, defaults, and descriptions.
  - A description of how the component affects the user's predict function.
  - A table of events and their descriptions.
  - Any additional interfaces or classes that may be used during initialisation or in the pre- or post- processors.

Additionally, the Gradio includes:

- A live demo.
- A richer, interactive version of the parameter tables.
- Nicer styling!

## What do I need to do?

The documentation generator uses existing standards to extract the necessary information, namely Type Hints and Docstrings. There are no Gradio-specific APIs for documentation, so following best practices will generally yield the best results.

If you already use type hints and docstrings in your component source code, you don't need to do much to benefit from this feature, but there are some details that you should be aware of.

### Python version

To get the best documentation experience, you need to use Python `3.10` or greater when generating documentation. This is because some introspection features used to generate the documentation were only added in `3.10`.

### Type hints

Python type hints are used extensively to provide helpful information for users. 

<details> 
<summary> What are type hints?</summary>


If you need to become more familiar with type hints in Python, they are a simple way to express what Python types are expected for arguments and return values of functions and methods. They provide a helpful in-editor experience, aid in maintenance, and integrate with various other tools. These types can be simple primitives, like `list` `str` `bool`; they could be more compound types like `list[str]`, `str | None` or `tuple[str, float | int]`; or they can be more complex types using utility classed like [`TypedDict`](https://peps.python.org/pep-0589/#abstract).

[Read more about type hints in Python.](https://realpython.com/lessons/type-hinting/)


</details>

#### What do I need to add hints to?

You do not need to add type hints to every part of your code. For the documentation to work correctly, you will need to add type hints to the following component methods:

- `__init__` parameters should be typed.
- `postprocess` parameters and return value should be typed.
- `preprocess` parameters and return value should be typed.

If you are using `gradio cc create`, these types should already exist, but you may need to tweak them based on any changes you make.

##### `__init__`

Here, you only need to type the parameters. If you have cloned a template with `gradio` cc create`, these should already be in place. You will only need to add new hints for anything you have added or changed:

```py
def __init__(
  self,
  value: str | None = None,
  *,
  sources: Literal["upload", "microphone"] = "upload,
  every: Timer | float | None = None,
  ...
):
  ...
```

##### `preprocess` and `postprocess`

The `preprocess` and `postprocess` methods determine the value passed to the user function and the value that needs to be returned.

Even if the design of your component is primarily as an input or an output, it is worth adding type hints to both the input parameters and the return values because Gradio has no way of limiting how components can be used.

In this case, we specifically care about:

- The return type of `preprocess`.
- The input type of `postprocess`.

```py
def preprocess(
  self, payload: FileData | None # input is optional
) -> tuple[int, str] | str | None:

# user function input  is the preprocess return ▲
# user function output is the postprocess input ▼

def postprocess(
  self, value: tuple[int, str] | None
) -> FileData | bytes | None: # return is optional
  ...
```

### Docstrings

Docstrings are also used extensively to extract more meaningful, human-readable descriptions of certain parts of the API.

<details> 
<summary> What are docstrings?</summary>


If you need to become more familiar with docstrings in Python, they are a way to annotate parts of your code with human-readable decisions and explanations. They offer a rich in-editor experience like type hints, but unlike type hints, they don't have any specific syntax requirements. They are simple strings and can take almost any form. The only requirement is where they appear. Docstrings should be "a string literal that occurs as the first statement in a module, function, class, or method definition".

[Read more about Python docstrings.](https://peps.python.org/pep-0257/#what-is-a-docstring)

</details>

While docstrings don't have any syntax requirements, we need a particular structure for documentation purposes.

As with type hint, the specific information we care about is as follows:

- `__init__` parameter docstrings.
- `preprocess` return docstrings.
- `postprocess` input parameter docstrings.

Everything else is optional.

Docstrings should always take this format to be picked up by the documentation generator:

#### Classes

```py
"""
A description of the class.

This can span multiple lines and can _contain_ *markdown*.
"""
```

#### Methods and functions 

Markdown in these descriptions will not be converted into formatted text.

```py
"""
Parameters:
    param_one: A description for this parameter.
    param_two: A description for this parameter.
Returns:
    A description for this return value.
"""
```

### Events

In custom components, events are expressed as a list stored on the `events` field of the component class. While we do not need types for events, we _do_ need a human-readable description so users can understand the behaviour of the event.

To facilitate this, we must create the event in a specific way.

There are two ways to add events to a custom component.

#### Built-in events

Gradio comes with a variety of built-in events that may be enough for your component. If you are using built-in events, you do not need to do anything as they already have descriptions we can extract:

```py
from gradio.events import Events

class ParamViewer(Component):
  ...

  EVENTS = [
    Events.change,
    Events.upload,
  ]
```

#### Custom events

You can define a custom event if the built-in events are unsuitable for your use case. This is a straightforward process, but you must create the event in this way for docstrings to work correctly:

```py
from gradio.events import Events, EventListener

class ParamViewer(Component):
  ...

  EVENTS = [
    Events.change,
    EventListener(
        "bingbong",
        doc="This listener is triggered when the user does a bingbong."
      )
  ]
```

### Demo

The `demo/app.py`, often used for developing the component, generates the live demo and code snippet. The only strict rule here is that the `demo.launch()` command must be contained with a `__name__ == "__main__"` conditional as below:

```py
if __name__ == "__main__":
  demo.launch()
```

The documentation generator will scan for such a clause and error if absent. If you are _not_ launching the demo inside the `demo/app.py`, then you can pass `--suppress-demo-check` to turn off this check.

#### Demo recommendations

Although there are no additional rules, there are some best practices you should bear in mind to get the best experience from the documentation generator.

These are only guidelines, and every situation is unique, but they are sound principles to remember.

##### Keep the demo compact

Compact demos look better and make it easier for users to understand what the demo does. Try to remove as many extraneous UI elements as possible to focus the users' attention on the core use case. 

Sometimes, it might make sense to have a `demo/app.py` just for the docs and an additional, more complex app for your testing purposes. You can also create other spaces, showcasing more complex examples and linking to them from the main class docstring or the `pyproject.toml` description.

#### Keep the code concise

The 'getting started' snippet utilises the demo code, which should be as short as possible to keep users engaged and avoid confusion.

It isn't the job of the sample snippet to demonstrate the whole API; this snippet should be the shortest path to success for a new user. It should be easy to type or copy-paste and easy to understand. Explanatory comments should be brief and to the point.

#### Avoid external dependencies

As mentioned above, users should be able to copy-paste a snippet and have a fully working app. Try to avoid third-party library dependencies to facilitate this.

You should carefully consider any examples; avoiding examples that require additional files or that make assumptions about the environment is generally a good idea.

#### Ensure the `demo` directory is self-contained

Only the `demo` directory will be uploaded to Hugging Face spaces in certain instances, as the component will be installed via PyPi if possible. It is essential that this directory is self-contained and any files needed for the correct running of the demo are present.

### Additional URLs

The documentation generator will generate a few buttons, providing helpful information and links to users. They are obtained automatically in some cases, but some need to be explicitly included in the `pyproject.yaml`. 

- PyPi Version and link - This is generated automatically.
- GitHub Repository - This is populated via the `pyproject.toml`'s `project.urls.repository`.
- Hugging Face Space - This is populated via the `pyproject.toml`'s `project.urls.space`.

An example `pyproject.toml` urls section might look like this:

```toml
[project.urls]
repository = "https://github.com/user/repo-name"
space = "https://huggingface.co/spaces/user/space-name"
```
