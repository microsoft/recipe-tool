# gradio-app/gradio/gradio

[git-collector-data]

**URL:** https://github.com/gradio-app/gradio/tree/main/gradio  
**Date:** 6/18/2025, 12:11:07 PM  
**Files:** 50  

=== File: gradio/components/__init__.py ===
from gradio.components.annotated_image import AnnotatedImage
from gradio.components.audio import Audio
from gradio.components.base import (
    Component,
    FormComponent,
    StreamingInput,
    StreamingOutput,
    _Keywords,
    component,
    get_component_instance,
)
from gradio.components.browser_state import BrowserState
from gradio.components.button import Button
from gradio.components.chatbot import Chatbot, ChatMessage, MessageDict
from gradio.components.checkbox import Checkbox
from gradio.components.checkboxgroup import CheckboxGroup
from gradio.components.clear_button import ClearButton
from gradio.components.code import Code
from gradio.components.color_picker import ColorPicker
from gradio.components.dataframe import Dataframe
from gradio.components.dataset import Dataset
from gradio.components.datetime import DateTime
from gradio.components.deep_link_button import DeepLinkButton
from gradio.components.download_button import DownloadButton
from gradio.components.dropdown import Dropdown
from gradio.components.duplicate_button import DuplicateButton
from gradio.components.fallback import Fallback
from gradio.components.file import File
from gradio.components.file_explorer import FileExplorer
from gradio.components.gallery import Gallery
from gradio.components.highlighted_text import HighlightedText
from gradio.components.html import HTML
from gradio.components.image import Image
from gradio.components.image_editor import ImageEditor
from gradio.components.imageslider import ImageSlider
from gradio.components.json_component import JSON
from gradio.components.label import Label
from gradio.components.login_button import LoginButton
from gradio.components.markdown import Markdown
from gradio.components.model3d import Model3D
from gradio.components.multimodal_textbox import MultimodalTextbox
from gradio.components.native_plot import BarPlot, LinePlot, NativePlot, ScatterPlot
from gradio.components.number import Number
from gradio.components.paramviewer import ParamViewer
from gradio.components.plot import Plot
from gradio.components.radio import Radio
from gradio.components.slider import Slider
from gradio.components.state import State
from gradio.components.textbox import Textbox
from gradio.components.timer import Timer
from gradio.components.upload_button import UploadButton
from gradio.components.video import Video
from gradio.layouts import Form

Text = Textbox
DataFrame = Dataframe
Highlightedtext = HighlightedText
Annotatedimage = AnnotatedImage
Highlight = HighlightedText
Checkboxgroup = CheckboxGroup
Json = JSON

__all__ = [
    "Audio",
    "BarPlot",
    "Button",
    "Chatbot",
    "ChatMessage",
    "ClearButton",
    "Component",
    "component",
    "get_component_instance",
    "_Keywords",
    "Checkbox",
    "CheckboxGroup",
    "Code",
    "ColorPicker",
    "Dataframe",
    "DataFrame",
    "Dataset",
    "DownloadButton",
    "DuplicateButton",
    "Fallback",
    "Form",
    "FormComponent",
    "Gallery",
    "HTML",
    "FileExplorer",
    "Image",
    "JSON",
    "Json",
    "Label",
    "LinePlot",
    "BrowserState",
    "LoginButton",
    "Markdown",
    "MessageDict",
    "Textbox",
    "DateTime",
    "Dropdown",
    "Model3D",
    "File",
    "HighlightedText",
    "AnnotatedImage",
    "CheckboxGroup",
    "Text",
    "Highlightedtext",
    "Annotatedimage",
    "Highlight",
    "Checkboxgroup",
    "Number",
    "Plot",
    "Radio",
    "ScatterPlot",
    "Slider",
    "State",
    "Timer",
    "UploadButton",
    "Video",
    "StreamingInput",
    "StreamingOutput",
    "ImageEditor",
    "ImageSlider",
    "ParamViewer",
    "MultimodalTextbox",
    "NativePlot",
    "DeepLinkButton",
]


=== File: gradio/components/annotated_image.py ===
"""gr.AnnotatedImage() component."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import gradio_client.utils as client_utils
import numpy as np
import PIL.Image
from gradio_client import handle_file
from gradio_client.documentation import document

from gradio import processing_utils, utils
from gradio.components.base import Component
from gradio.data_classes import FileData, GradioModel
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer

PIL.Image.init()  # fixes https://github.com/gradio-app/gradio/issues/2843


class Annotation(GradioModel):
    image: FileData
    label: str


class AnnotatedImageData(GradioModel):
    image: FileData
    annotations: list[Annotation]


@document()
class AnnotatedImage(Component):
    """
    Creates a component to displays a base image and colored annotations on top of that image. Annotations can take the from of rectangles (e.g. object detection) or masks (e.g. image segmentation).
    As this component does not accept user input, it is rarely used as an input component.

    Demos: image_segmentation
    """

    EVENTS = [Events.select]

    data_model = AnnotatedImageData

    def __init__(
        self,
        value: (
            tuple[
                np.ndarray | PIL.Image.Image | str,
                list[tuple[np.ndarray | tuple[int, int, int, int], str]],
            ]
            | None
        ) = None,
        *,
        format: str = "webp",
        show_legend: bool = True,
        height: int | str | None = None,
        width: int | str | None = None,
        color_map: dict[str, str] | None = None,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        show_fullscreen_button: bool = True,
    ):
        """
        Parameters:
            value: Tuple of base image and list of (annotation, label) pairs.
            format: Format used to save images before it is returned to the front end, such as 'jpeg' or 'png'. This parameter only takes effect when the base image is returned from the prediction function as a numpy array or a PIL Image. The format should be supported by the PIL library.
            show_legend: If True, will show a legend of the annotations.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.
            width: The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.
            color_map: A dictionary mapping labels to colors. The colors must be specified as hex codes.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: Relative width compared to adjacent Components in a Row. For example, if Component A has scale=2, and Component B has scale=1, A will be twice as wide as B. Should be an integer.
            min_width: Minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            show_fullscreen_button: If True, will show a button to allow the image to be viewed in fullscreen mode.
        """
        self.format = format
        self.show_legend = show_legend
        self.height = height
        self.width = width
        self.color_map = color_map
        self.show_fullscreen_button = show_fullscreen_button
        self._value_description = "a tuple of type [image: str, annotations: list[tuple[mask: str, label: str]]] where 'image' is the path to the base image and 'annotations' is a list of tuples where each tuple has a 'mask' image filepath and a corresponding label."
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def preprocess(
        self, payload: AnnotatedImageData | None
    ) -> tuple[str, list[tuple[str, str]]] | None:
        """
        Parameters:
            payload: Dict of base image and list of annotations.
        Returns:
            Passes its value as a `tuple` consisting of a `str` filepath to a base image and `list` of annotations. Each annotation itself is `tuple` of a mask (as a `str` filepath to image) and a `str` label.
        """
        if payload is None:
            return None
        base_img = payload.image.path
        annotations = [(a.image.path, a.label) for a in payload.annotations]
        return (base_img, annotations)

    def postprocess(
        self,
        value: (
            tuple[
                np.ndarray | PIL.Image.Image | str,
                Sequence[tuple[np.ndarray | tuple[int, int, int, int], str]],
            ]
            | None
        ),
    ) -> AnnotatedImageData | None:
        """
        Parameters:
            value: Expects a a tuple of a base image and list of annotations: a `tuple[Image, list[Annotation]]`. The `Image` itself can be `str` filepath, `numpy.ndarray`, or `PIL.Image`. Each `Annotation` is a `tuple[Mask, str]`. The `Mask` can be either a `tuple` of 4 `int`'s representing the bounding box coordinates (x1, y1, x2, y2), or 0-1 confidence mask in the form of a `numpy.ndarray` of the same shape as the image, while the second element of the `Annotation` tuple is a `str` label.
        Returns:
            Tuple of base image file and list of annotations, with each annotation a two-part tuple where the first element image path of the mask, and the second element is the label.
        """
        if value is None:
            return None
        base_img = value[0]
        if isinstance(base_img, str):
            if client_utils.is_http_url_like(base_img):
                base_img = processing_utils.save_url_to_cache(
                    base_img, cache_dir=self.GRADIO_CACHE
                )
            base_img_path = base_img
            base_img = np.array(PIL.Image.open(base_img))
        elif isinstance(base_img, np.ndarray):
            base_file = processing_utils.save_img_array_to_cache(
                base_img, cache_dir=self.GRADIO_CACHE, format=self.format
            )
            base_img_path = str(utils.abspath(base_file))
        elif isinstance(base_img, PIL.Image.Image):
            base_file = processing_utils.save_pil_to_cache(
                base_img, cache_dir=self.GRADIO_CACHE, format=self.format
            )
            base_img_path = str(utils.abspath(base_file))
            base_img = np.array(base_img)
        else:
            raise ValueError(
                "AnnotatedImage only accepts filepaths, PIL images or numpy arrays for the base image."
            )

        sections = []
        color_map = self.color_map or {}

        def hex_to_rgb(value):
            value = value.lstrip("#")
            lv = len(value)
            return [int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3)]

        for mask, label in value[1]:
            mask_array = np.zeros((base_img.shape[0], base_img.shape[1]))
            if isinstance(mask, np.ndarray):
                mask_array = mask
            else:
                x1, y1, x2, y2 = mask
                border_width = 3
                mask_array[y1:y2, x1:x2] = 0.5
                mask_array[y1:y2, x1 : x1 + border_width] = 1
                mask_array[y1:y2, x2 - border_width : x2] = 1
                mask_array[y1 : y1 + border_width, x1:x2] = 1
                mask_array[y2 - border_width : y2, x1:x2] = 1

            if label in color_map:
                rgb_color = hex_to_rgb(color_map[label])
            else:
                rgb_color = [255, 0, 0]
            colored_mask = np.zeros((base_img.shape[0], base_img.shape[1], 4))
            solid_mask = np.copy(mask_array)
            solid_mask[solid_mask > 0] = 1

            colored_mask[:, :, 0] = rgb_color[0] * solid_mask
            colored_mask[:, :, 1] = rgb_color[1] * solid_mask
            colored_mask[:, :, 2] = rgb_color[2] * solid_mask
            colored_mask[:, :, 3] = mask_array * 255

            colored_mask_img = PIL.Image.fromarray((colored_mask).astype(np.uint8))

            # RGBA does not support transparency
            mask_file = processing_utils.save_pil_to_cache(
                colored_mask_img, cache_dir=self.GRADIO_CACHE, format="png"
            )
            mask_file_path = str(utils.abspath(mask_file))
            sections.append(
                Annotation(image=FileData(path=mask_file_path), label=label)
            )

        return AnnotatedImageData(
            image=FileData(path=base_img_path),
            annotations=sections,
        )

    def example_payload(self) -> Any:
        return {
            "image": handle_file(
                "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
            ),
            "annotations": [],
        }

    def example_value(self) -> Any:
        return (
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",
            [([0, 0, 100, 100], "bus")],
        )


=== File: gradio/components/api_component.py ===
"""gr.Api() component."""

from __future__ import annotations

from typing import Any

from gradio.components.base import Component


class Api(Component):
    """
    A generic component that holds any value. Used for generating APIs with no actual frontend component.
    """

    EVENTS = []

    def __init__(
        self,
        value: Any,
        _api_info: dict[str, str],
        label: str = "API",
    ):
        """
        Parameters:
            value: default value.
        """
        self._api_info = _api_info
        super().__init__(value=value, label=label)

    def preprocess(self, payload: Any) -> Any:
        return payload

    def postprocess(self, value: Any) -> Any:
        return value

    def api_info(self) -> dict[str, str]:
        return self._api_info

    def example_payload(self) -> Any:
        return self.value if self.value is not None else "..."

    def example_value(self) -> Any:
        return self.value if self.value is not None else "..."

    # def get_block_name(self) -> str:
    #     return "state"  # so that it does not render in the frontend, just like state


=== File: gradio/components/audio.py ===
"""gr.Audio() component."""

from __future__ import annotations

import dataclasses
import io
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import anyio
import httpx
import numpy as np
from gradio_client import handle_file
from gradio_client import utils as client_utils
from gradio_client.documentation import document
from pydub import AudioSegment

from gradio import processing_utils, utils, wasm_utils
from gradio.components.base import Component, StreamingInput, StreamingOutput
from gradio.data_classes import FileData, FileDataDict, MediaStreamChunk
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
@dataclasses.dataclass
class WaveformOptions:
    """
    A dataclass for specifying options for the waveform display in the Audio component. An instance of this class can be passed into the `waveform_options` parameter of `gr.Audio`.
    Parameters:
        waveform_color: The color (as a hex string or valid CSS color) of the full waveform representing the amplitude of the audio. Defaults to a light gray color.
        waveform_progress_color: The color (as a hex string or valid CSS color) that the waveform fills with to as the audio plays. Defaults to the accent color.
        trim_region_color: The color (as a hex string or valid CSS color) of the trim region. Defaults to the accent color.
        show_recording_waveform: If True, shows a waveform when recording audio or playing audio. If False, uses the default browser audio players. For streamed audio, the default browser audio player is always used.
        show_controls: Deprecated and has no effect. Use `show_recording_waveform` instead.
        skip_length: The percentage (between 0 and 100) of the audio to skip when clicking on the skip forward / skip backward buttons.
        sample_rate: The output sample rate (in Hz) of the audio after editing.
    """

    waveform_color: str | None = None
    waveform_progress_color: str | None = None
    trim_region_color: str | None = None
    show_recording_waveform: bool = True
    show_controls: bool = False
    skip_length: int | float = 5
    sample_rate: int = 44100


@document()
class Audio(
    StreamingInput,
    StreamingOutput,
    Component,
):
    """
    Creates an audio component that can be used to upload/record audio (as an input) or display audio (as an output).
    Demos: generate_tone, reverse_audio
    Guides: real-time-speech-recognition
    """

    EVENTS = [
        Events.stream,
        Events.change,
        Events.clear,
        Events.play,
        Events.pause,
        Events.stop,
        Events.pause,
        Events.start_recording,
        Events.pause_recording,
        Events.stop_recording,
        Events.upload,
        Events.input,
    ]

    data_model = FileData

    def __init__(
        self,
        value: str | Path | tuple[int, np.ndarray] | Callable | None = None,
        *,
        sources: list[Literal["upload", "microphone"]]
        | Literal["upload", "microphone"]
        | None = None,
        type: Literal["numpy", "filepath"] = "numpy",
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        streaming: bool = False,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        format: Literal["wav", "mp3"] | None = None,
        autoplay: bool = False,
        show_download_button: bool | None = None,
        show_share_button: bool | None = None,
        editable: bool = True,
        min_length: int | None = None,
        max_length: int | None = None,
        waveform_options: WaveformOptions | dict | None = None,
        loop: bool = False,
        recording: bool = False,
    ):
        """
        Parameters:
            value: A path, URL, or [sample_rate, numpy array] tuple (sample rate in Hz, audio data as a float or int numpy array) for the default value that Audio component is going to take. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            sources: A list of sources permitted for audio. "upload" creates a box where user can drop an audio file, "microphone" creates a microphone input. The first element in the list will be used as the default source. If None, defaults to ["upload", "microphone"], or ["microphone"] if `streaming` is True.
            type: The format the audio file is converted to before being passed into the prediction function. "numpy" converts the audio to a tuple consisting of: (int sample rate, numpy.array for the data), "filepath" passes a str path to a temporary file containing the audio.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: Relative width compared to adjacent Components in a Row. For example, if Component A has scale=2, and Component B has scale=1, A will be twice as wide as B. Should be an integer.
            min_width: Minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: If True, will allow users to upload and edit an audio file. If False, can only be used to play audio. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            streaming: If set to True when used in a `live` interface as an input, will automatically stream webcam feed. When used set as an output, takes audio chunks yield from the backend and combines them into one streaming audio output.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: if False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            format: the file extension with which to save audio files. Either 'wav' or 'mp3'. wav files are lossless but will tend to be larger files. mp3 files tend to be smaller. This parameter applies both when this component is used as an input (and `type` is "filepath") to determine which file format to convert user-provided audio to, and when this component is used as an output to determine the format of audio returned to the user. If None, no file format conversion is done and the audio is kept as is. In the case where output audio is returned from the prediction function as numpy array and no `format` is provided, it will be returned as a "wav" file.
            autoplay: Whether to automatically play the audio when the component is used as an output. Note: browsers will not autoplay audio files if the user has not interacted with the page yet.
            show_download_button: If True, will show a download button in the corner of the component for saving audio. If False, icon does not appear. By default, it will be True for output components and False for input components.
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            editable: If True, allows users to manipulate the audio file if the component is interactive. Defaults to True.
            min_length: The minimum length of audio (in seconds) that the user can pass into the prediction function. If None, there is no minimum length.
            max_length: The maximum length of audio (in seconds) that the user can pass into the prediction function. If None, there is no maximum length.
            waveform_options: A dictionary of options for the waveform display. Options include: waveform_color (str), waveform_progress_color (str), show_controls (bool), skip_length (int), trim_region_color (str). Default is None, which uses the default values for these options. [See `gr.WaveformOptions` docs](#waveform-options).
            loop: If True, the audio will loop when it reaches the end and continue playing from the beginning.
            recording: If True, the audio component will be set to record audio from the microphone if the source is set to "microphone". Defaults to False.
        """
        valid_sources: list[Literal["upload", "microphone"]] = ["upload", "microphone"]
        if sources is None:
            self.sources = ["microphone"] if streaming else valid_sources
        elif isinstance(sources, str) and sources in valid_sources:
            self.sources = [sources]
        elif isinstance(sources, list):
            self.sources = sources
        else:
            raise ValueError(
                f"`sources` must be a list consisting of elements in {valid_sources}"
            )
        for source in self.sources:
            if source not in valid_sources:
                raise ValueError(
                    f"`sources` must a list consisting of elements in {valid_sources}"
                )
        valid_types = ["numpy", "filepath"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {' '.join(valid_types)}"
            )
        self.type = type
        self.streaming = streaming
        if self.streaming and "microphone" not in self.sources:
            raise ValueError(
                "Audio streaming only available if sources includes 'microphone'."
            )
        valid_formats = ["wav", "mp3"]
        if format is not None and format.lower() not in valid_formats:
            raise ValueError(
                f"Invalid value for parameter `format`: {format}. Please choose from one of: {' '.join(valid_formats)}"
            )
        self.format = format and format.lower()
        self.autoplay = autoplay
        self.loop = loop
        self.show_download_button = show_download_button
        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        self.editable = editable
        if waveform_options is None:
            self.waveform_options = WaveformOptions()
        elif isinstance(waveform_options, dict):
            self.waveform_options = WaveformOptions(**waveform_options)
        else:
            self.waveform_options = waveform_options
        if self.waveform_options.show_controls is not False:
            warnings.warn(
                "The `show_controls` parameter is deprecated and will be removed in a future release. Use `show_recording_waveform` instead."
            )
        self.min_length = min_length
        self.max_length = max_length
        self.recording = recording
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = (
            "a filepath to an audio file"
            if self.type == "filepath"
            else "a tuple of [sample_rate: int, data: np.ndarray] of audio data"
        )

    def example_payload(self) -> Any:
        return handle_file(
            "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav"
        )

    def example_value(self) -> Any:
        return "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav"

    def preprocess(
        self, payload: FileData | None
    ) -> str | tuple[int, np.ndarray] | None:
        """
        Parameters:
            payload: audio data as a FileData object, or None.
        Returns:
            passes audio as one of these formats (depending on `type`): a `str` filepath, or `tuple` of (sample rate in Hz, audio data as numpy array). If the latter, the audio data is a 16-bit `int` array whose values range from -32768 to 32767 and shape of the audio data array is (samples,) for mono audio or (samples, channels) for multi-channel audio.
        """
        if payload is None:
            return payload

        if not payload.path:
            raise ValueError("payload path missing")

        needs_conversion = False
        original_suffix = Path(payload.path).suffix.lower()
        if self.format is not None and original_suffix != f".{self.format}":
            needs_conversion = True

        if self.min_length is not None or self.max_length is not None:
            sample_rate, data = processing_utils.audio_from_file(payload.path)
            duration = len(data) / sample_rate
            if self.min_length is not None and duration < self.min_length:
                raise Error(
                    f"Audio is too short, and must be at least {self.min_length} seconds"
                )
            if self.max_length is not None and duration > self.max_length:
                raise Error(
                    f"Audio is too long, and must be at most {self.max_length} seconds"
                )

        if self.type == "numpy":
            return processing_utils.audio_from_file(payload.path)
        elif self.type == "filepath":
            if not needs_conversion:
                return payload.path
            sample_rate, data = processing_utils.audio_from_file(payload.path)
            output_file = str(Path(payload.path).with_suffix(f".{self.format}"))
            assert self.format is not None  # noqa: S101
            processing_utils.audio_to_file(
                sample_rate, data, output_file, format=self.format
            )
            return output_file
        else:
            raise ValueError(
                "Unknown type: "
                + str(self.type)
                + ". Please choose from: 'numpy', 'filepath'."
            )

    def postprocess(
        self, value: str | Path | bytes | tuple[int, np.ndarray] | None
    ) -> FileData | bytes | None:
        """
        Parameters:
            value: expects audio data in any of these formats: a `str` or `pathlib.Path` filepath or URL to an audio file, or a `bytes` object (recommended for streaming), or a `tuple` of (sample rate in Hz, audio data as numpy array). Note: if audio is supplied as a numpy array, the audio will be normalized by its peak value to avoid distortion or clipping in the resulting audio.
        Returns:
            FileData object, bytes, or None.
        """
        orig_name = None
        if value is None:
            return None

        if isinstance(value, bytes):
            if self.streaming:
                return value
            file_path = processing_utils.save_bytes_to_cache(
                value, "audio", cache_dir=self.GRADIO_CACHE
            )
            orig_name = Path(file_path).name
        elif isinstance(value, tuple):
            sample_rate, data = value
            file_path = processing_utils.save_audio_to_cache(
                data,
                sample_rate,
                format=self.format or "wav",
                cache_dir=self.GRADIO_CACHE,
            )
            orig_name = Path(file_path).name
        elif isinstance(value, (str, Path)):
            if client_utils.is_http_url_like(value):
                original_suffix = Path(httpx.URL(str(value)).path).suffix.lower()
            else:
                original_suffix = Path(value).suffix.lower()
            if self.format is not None and original_suffix != f".{self.format}":
                sample_rate, data = processing_utils.audio_from_file(str(value))
                file_path = processing_utils.save_audio_to_cache(
                    data, sample_rate, format=self.format, cache_dir=self.GRADIO_CACHE
                )
            else:
                file_path = str(value)
            orig_name = Path(file_path).name if Path(file_path).exists() else None
        else:
            raise ValueError(f"Cannot process {value} as Audio")
        return FileData(path=file_path, orig_name=orig_name)

    @staticmethod
    def _convert_to_adts(data: bytes):
        if wasm_utils.IS_WASM:
            raise wasm_utils.WasmUnsupportedError(
                "Audio streaming is not supported in the Wasm mode."
            )
        segment = AudioSegment.from_file(io.BytesIO(data))

        buffer = io.BytesIO()
        segment.export(buffer, format="adts")  # ADTS is a container format for AAC
        aac_data = buffer.getvalue()
        return aac_data, len(segment) / 1000.0

    @staticmethod
    async def covert_to_adts(data: bytes) -> tuple[bytes, float]:
        return await anyio.to_thread.run_sync(Audio._convert_to_adts, data)

    async def stream_output(
        self,
        value,
        output_id: str,
        first_chunk: bool,  # noqa: ARG002
    ) -> tuple[MediaStreamChunk | None, FileDataDict]:
        output_file: FileDataDict = {
            "path": output_id,
            "is_stream": True,
            "orig_name": "audio-stream.mp3",
            "meta": {"_type": "gradio.FileData"},
        }
        if value is None:
            return None, output_file
        if isinstance(value, bytes):
            value, duration = await self.covert_to_adts(value)
            return {
                "data": value,
                "duration": duration,
                "extension": ".aac",
            }, output_file
        if client_utils.is_http_url_like(value["path"]):
            response = httpx.get(value["path"])
            binary_data = response.content
        else:
            output_file["orig_name"] = value["orig_name"]
            file_path = value["path"]
            with open(file_path, "rb") as f:
                binary_data = f.read()
        value, duration = await self.covert_to_adts(binary_data)
        return {"data": value, "duration": duration, "extension": ".aac"}, output_file

    async def combine_stream(
        self,
        stream: list[bytes],
        desired_output_format: str | None = None,
        only_file=False,  # noqa: ARG002
    ) -> FileData:
        output_file = FileData(
            path=processing_utils.save_bytes_to_cache(
                b"".join(stream), "audio.mp3", cache_dir=self.GRADIO_CACHE
            ),
            is_stream=False,
            orig_name="audio-stream.mp3",
        )
        if desired_output_format and desired_output_format != "mp3":
            new_path = Path(output_file.path).with_suffix(f".{desired_output_format}")
            AudioSegment.from_file(output_file.path).export(
                new_path, format=desired_output_format
            )
            output_file.path = str(new_path)
        return output_file

    def process_example(
        self, value: tuple[int, np.ndarray] | str | Path | bytes | None
    ) -> str:
        if value is None:
            return ""
        elif isinstance(value, (str, Path)):
            return Path(value).name
        return "(audio)"

    def check_streamable(self):
        if (
            self.sources is not None
            and "microphone" not in self.sources
            and self.streaming
        ):
            raise ValueError(
                "Audio streaming only available if source includes 'microphone'."
            )


=== File: gradio/components/bar_plot.py ===
"""gr.BarPlot() component."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.components.plot import AltairPlot, AltairPlotData, Plot
from gradio.i18n import I18nData

if TYPE_CHECKING:
    import pandas as pd

    from gradio.components import Timer


@document()
class BarPlot(Plot):
    """
    Creates a bar plot component to display data from a pandas DataFrame (as output). As this component does
    not accept user input, it is rarely used as an input component.

    Demos: bar_plot
    """

    data_model = AltairPlotData

    def __init__(
        self,
        value: pd.DataFrame | Callable | None = None,
        x: str | None = None,
        y: str | None = None,
        *,
        color: str | None = None,
        vertical: bool = True,
        group: str | None = None,
        title: str | None = None,
        tooltip: list[str] | str | None = None,
        x_title: str | None = None,
        y_title: str | None = None,
        x_label_angle: float | None = None,
        y_label_angle: float | None = None,
        color_legend_title: str | None = None,
        group_title: str | None = None,
        color_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        height: int | None = None,
        width: int | None = None,
        y_lim: list[int] | None = None,
        caption: str | None = None,
        interactive: bool | None = True,
        label: str | I18nData | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        sort: Literal["x", "y", "-x", "-y"] | None = None,
        show_actions_button: bool = False,
    ):
        """
        Parameters:
            value: The pandas dataframe containing the data to display in a scatter plot. If a callable is provided, the function will be called whenever the app loads to set the initial value of the plot.
            x: Column corresponding to the x axis.
            y: Column corresponding to the y axis.
            color: The column to determine the bar color. Must be categorical (discrete values).
            vertical: If True, the bars will be displayed vertically. If False, the x and y axis will be switched, displaying the bars horizontally. Default is True.
            group: The column with which to split the overall plot into smaller subplots.
            title: The title to display on top of the chart.
            tooltip: The column (or list of columns) to display on the tooltip when a user hovers over a bar.
            x_title: The title given to the x axis. By default, uses the value of the x parameter.
            y_title: The title given to the y axis. By default, uses the value of the y parameter.
            x_label_angle: The angle (in degrees) of the x axis labels. Positive values are clockwise, and negative values are counter-clockwise.
            y_label_angle: The angle (in degrees) of the y axis labels. Positive values are clockwise, and negative values are counter-clockwise.
            color_legend_title: The title given to the color legend. By default, uses the value of color parameter.
            group_title: The label displayed on top of the subplot columns (or rows if vertical=True). Use an empty string to omit.
            color_legend_position: The position of the color legend. If the string value 'none' is passed, this legend is omitted. For other valid position values see: https://vega.github.io/vega/docs/legends/#orientation.
            height: The height of the plot in pixels.
            width: The width of the plot in pixels. If None, expands to fit.
            y_lim: A tuple of list containing the limits for the y-axis, specified as [y_min, y_max].
            caption: The (optional) caption to display below the plot.
            interactive: Whether users should be able to interact with the plot by panning or zooming with their mouse or trackpad.
            label: The (optional) label to display on the top left corner of the plot.
            show_label: Whether the label should be displayed.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            visible: Whether the plot should be visible.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            sort: Specifies the sorting axis as either "x", "y", "-x" or "-y". If None, no sorting is applied.
            show_actions_button: Whether to show the actions button on the top right corner of the plot.
        """
        self.x = x
        self.y = y
        self.color = color
        self.vertical = vertical
        self.group = group
        self.group_title = group_title
        self.tooltip = tooltip
        self.title = title
        self.x_title = x_title
        self.y_title = y_title
        self.x_label_angle = x_label_angle
        self.y_label_angle = y_label_angle
        self.color_legend_title = color_legend_title
        self.group_title = group_title
        self.color_legend_position = color_legend_position
        self.y_lim = y_lim
        self.caption = caption
        self.interactive_chart = interactive
        if isinstance(width, str):
            width = None
            warnings.warn(
                "Width should be an integer, not a string. Setting width to None."
            )
        if isinstance(height, str):
            warnings.warn(
                "Height should be an integer, not a string. Setting height to None."
            )
            height = None
        self.width = width
        self.height = height
        self.sort = sort
        self.show_actions_button = show_actions_button
        if label is None and show_label is None:
            show_label = False
        super().__init__(
            value=value,
            label=label,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            every=every,
            inputs=inputs,
        )

    def get_block_name(self) -> str:
        return "plot"

    @staticmethod
    def create_plot(
        value: pd.DataFrame,
        x: str,
        y: str,
        color: str | None = None,
        vertical: bool = True,
        group: str | None = None,
        title: str | None = None,
        tooltip: list[str] | str | None = None,
        x_title: str | None = None,
        y_title: str | None = None,
        x_label_angle: float | None = None,
        y_label_angle: float | None = None,
        color_legend_title: str | None = None,
        group_title: str | None = None,
        color_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        height: int | None = None,
        width: int | None = None,
        y_lim: list[int] | None = None,
        interactive: bool | None = True,
        sort: Literal["x", "y", "-x", "-y"] | None = None,
    ):
        """Helper for creating the bar plot."""
        import altair as alt

        interactive = True if interactive is None else interactive
        orientation = {"field": group, "title": group_title} if group else {}

        x_title = x_title or x
        y_title = y_title or y

        # If horizontal, switch x and y
        if not vertical:
            y, x = x, y
            x = f"sum({x}):Q"
            y_title, x_title = x_title, y_title
            orientation = {"row": alt.Row(**orientation)} if orientation else {}  # type: ignore
            x_lim = y_lim
            y_lim = None
        else:
            y = f"sum({y}):Q"
            x_lim = None
            orientation = {"column": alt.Column(**orientation)} if orientation else {}  # type: ignore

        encodings = dict(
            x=alt.X(
                x,  # type: ignore
                title=x_title,  # type: ignore
                scale=AltairPlot.create_scale(x_lim),  # type: ignore
                axis=alt.Axis(labelAngle=x_label_angle)
                if x_label_angle is not None
                else alt.Axis(),
                sort=sort if vertical and sort is not None else None,
            ),
            y=alt.Y(
                y,  # type: ignore
                title=y_title,  # type: ignore
                scale=AltairPlot.create_scale(y_lim),  # type: ignore
                axis=alt.Axis(labelAngle=y_label_angle)
                if y_label_angle is not None
                else alt.Axis(),
                sort=sort if not vertical and sort is not None else None,
            ),
            **orientation,
        )
        properties = {}
        if title:
            properties["title"] = title
        if height:
            properties["height"] = height
        if width:
            properties["width"] = width

        if color:
            color_legend_position = color_legend_position or "bottom"
            domain = value[color].unique().tolist()
            range_ = list(range(len(domain)))
            encodings["color"] = {
                "field": color,
                "type": "nominal",
                "scale": {"domain": domain, "range": range_},
                "legend": AltairPlot.create_legend(
                    position=color_legend_position, title=color_legend_title
                ),
            }

        if tooltip:
            encodings["tooltip"] = tooltip  # type: ignore

        chart = (
            alt.Chart(value)  # type: ignore
            .mark_bar()  # type: ignore
            .encode(**encodings)
            .properties(background="transparent", **properties)
        )
        if interactive:
            chart = chart.interactive()

        return chart

    def preprocess(self, payload: AltairPlotData) -> AltairPlotData:
        """
        Parameters:
            payload: The data to display in a bar plot.
        Returns:
            (Rarely used) passes the data displayed in the bar plot as an AltairPlotData dataclass, which includes the plot information as a JSON string, as well as the type of plot (in this case, "bar").
        """
        return payload

    def postprocess(self, value: pd.DataFrame | None) -> AltairPlotData | None:
        """
        Parameters:
            value: Expects a pandas DataFrame containing the data to display in the bar plot. The DataFrame should contain at least two columns, one for the x-axis (corresponding to this component's `x` argument) and one for the y-axis (corresponding to `y`).
        Returns:
            The data to display in a bar plot, in the form of an AltairPlotData dataclass, which includes the plot information as a JSON string, as well as the type of plot (in this case, "bar").
        """
        # if None or update
        if value is None:
            return value
        if self.x is None or self.y is None:
            raise ValueError("No value provided for required parameters `x` and `y`.")
        chart = self.create_plot(
            value=value,
            x=self.x,
            y=self.y,
            color=self.color,
            vertical=self.vertical,
            group=self.group,
            title=self.title,
            tooltip=self.tooltip,
            x_title=self.x_title,
            y_title=self.y_title,
            x_label_angle=self.x_label_angle,
            y_label_angle=self.y_label_angle,
            color_legend_title=self.color_legend_title,
            color_legend_position=self.color_legend_position,  # type: ignore
            group_title=self.group_title,
            y_lim=self.y_lim,
            interactive=self.interactive_chart,
            height=self.height,
            width=self.width,
            sort=self.sort,  # type: ignore
        )

        return AltairPlotData(type="altair", plot=chart.to_json(), chart="bar")

    def example_payload(self) -> Any:
        return None

    def example_value(self) -> Any:
        import pandas as pd

        return pd.DataFrame({self.x: [1, 2, 3], self.y: [4, 5, 6]})


=== File: gradio/components/base.py ===
"""Contains all of the components that can be used with Gradio Interface / Blocks.
Along with the docs for each component, you can find the names of example demos that use
each component. These demos are located in the `demo` directory."""

from __future__ import annotations

import abc
import hashlib
import json
import sys
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import gradio_client.utils as client_utils

from gradio import utils
from gradio.blocks import Block, BlockContext
from gradio.component_meta import ComponentMeta
from gradio.data_classes import (
    BaseModel,
    DeveloperPath,
    FileData,
    FileDataDict,
    GradioDataModel,
    MediaStreamChunk,
)
from gradio.events import EventListener
from gradio.i18n import I18nData
from gradio.layouts import Form
from gradio.processing_utils import move_files_to_cache

if TYPE_CHECKING:
    from typing import TypedDict

    class DataframeData(TypedDict):
        headers: list[str]
        data: list[list[str | int | bool]]

    from gradio.components import Timer


class _Keywords(Enum):
    NO_VALUE = "NO_VALUE"  # Used as a sentinel to determine if nothing is provided as a argument for `value` in `Component.update()`
    FINISHED_ITERATING = "FINISHED_ITERATING"  # Used to skip processing of a component's value (needed for generators + state)


class ComponentBase(ABC, metaclass=ComponentMeta):
    EVENTS: list[EventListener | str] = []

    @abstractmethod
    def preprocess(self, payload: Any) -> Any:
        """
        Any preprocessing needed to be performed on function input.
        Parameters:
            payload: The input data received by the component from the frontend.
        Returns:
            The preprocessed input data sent to the user's function in the backend.
        """
        return payload

    @abstractmethod
    def postprocess(self, value):
        """
        Any postprocessing needed to be performed on function output.
        Parameters:
            value: The output data received by the component from the user's function in the backend.
        Returns:
            The postprocessed output data sent to the frontend.
        """
        return value

    @abstractmethod
    def process_example(self, value):
        """
        Process the input data in a way that can be displayed by the examples dataset component in the front-end.

        For example, only return the name of a file as opposed to a full path. Or get the head of a dataframe.
        The return value must be able to be json-serializable to put in the config.
        """
        pass

    @abstractmethod
    def api_info(self) -> dict[str, list[str]]:
        """
        The typing information for this component as a dictionary whose values are a list of 2 strings: [Python type, language-agnostic description].
        Keys of the dictionary are: raw_input, raw_output, serialized_input, serialized_output
        """
        pass

    @abstractmethod
    def example_inputs(self) -> Any:
        """
        Deprecated and replaced by `example_payload()` and `example_value()`.
        """
        pass

    @abstractmethod
    def flag(self, payload: Any | GradioDataModel, flag_dir: str | Path = "") -> str:
        """
        Write the component's value to a format that can be stored in a csv or jsonl format for flagging.
        """
        pass

    @abstractmethod
    def read_from_flag(self, payload: Any) -> GradioDataModel | Any:
        """
        Convert the data from the csv or jsonl file into the component state.
        """
        return payload

    @property
    @abstractmethod
    def skip_api(self) -> bool:
        """Whether this component should be skipped from the api return value"""

    @classmethod
    def has_event(cls, event: str | EventListener) -> bool:
        return event in cls.EVENTS

    @classmethod
    def get_component_class_id(cls) -> str:
        module_name = cls.__module__
        module_path = sys.modules[module_name].__file__
        module_hash = hashlib.sha256(
            f"{cls.__name__}_{module_path}".encode()
        ).hexdigest()
        return module_hash


def server(fn):
    fn._is_server_fn = True
    return fn


class Component(ComponentBase, Block):
    """
    A base class for defining methods that all input/output components should have.
    """

    def __init__(
        self,
        value: Any = None,
        *,
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
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        load_fn: Callable | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
    ):
        self.server_fns = [
            getattr(self, value)
            for value in dir(self.__class__)
            if callable(getattr(self, value))
            and getattr(getattr(self, value), "_is_server_fn", False)
        ]

        # Svelte components expect elem_classes to be a list
        # If we don't do this, returning a new component for an
        # update will break the frontend
        if not elem_classes:
            elem_classes = []

        # This gets overridden when `select` is called
        self._selectable = False
        if not hasattr(self, "data_model"):
            self.data_model: type[GradioDataModel] | None = None

        Block.__init__(
            self,
            elem_id=elem_id,
            elem_classes=elem_classes,
            visible=visible,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )
        if isinstance(self, StreamingInput):
            self.check_streamable()

        self.label = label
        self.info = info
        if not container:
            if show_label:
                warnings.warn("show_label has no effect when container is False.")
            show_label = False
        if show_label is None:
            show_label = True
        self.show_label = show_label
        self.container = container
        if scale is not None and scale != round(scale):
            warnings.warn(
                f"'scale' value should be an integer. Using {scale} will cause issues."
            )
        self.scale = scale
        self.min_width = min_width
        self.interactive = interactive

        # load_event is set in the Blocks.attach_load_events method
        self.load_event: None | dict[str, Any] = None
        self.load_event_to_attach: (
            None
            | tuple[
                Callable,
                list[tuple[Block, str]],
                Component | Sequence[Component] | set[Component] | None,
            ]
        ) = None
        load_fn, initial_value = self.get_load_fn_and_initial_value(value, inputs)
        initial_value = self.postprocess(initial_value)
        # Serialize the json value so that it gets stored in the
        # config as plain json, for images/audio etc. `move_files_to_cache`
        # will call model_dump
        if isinstance(initial_value, BaseModel):
            initial_value = initial_value.model_dump()
        self.value = move_files_to_cache(
            initial_value,
            self,  # type: ignore
            postprocess=True,
            keep_in_cache=True,
        )
        if client_utils.is_file_obj(self.value):
            self.keep_in_cache.add(self.value["path"])

        if callable(load_fn):
            self.attach_load_event(load_fn, every, inputs)

        self.component_class_id = self.__class__.get_component_class_id()

    TEMPLATE_DIR = DeveloperPath("./templates/")
    FRONTEND_DIR = "../../frontend/"

    def get_config(self):
        config = super().get_config()
        if self.info:
            config["info"] = self.info
        if len(self.server_fns):
            config["server_fns"] = [fn.__name__ for fn in self.server_fns]
        config.pop("render", None)
        return config

    @property
    def skip_api(self):
        return False

    @staticmethod
    def get_load_fn_and_initial_value(value, inputs=None):
        initial_value = None
        if callable(value):
            if not inputs:
                initial_value = value()
            load_fn = value
        else:
            initial_value = value
            load_fn = None
        return load_fn, initial_value

    def attach_load_event(
        self,
        callable: Callable,
        every: Timer | float | None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
    ):
        """Add an event that runs `callable`, optionally at interval specified by `every`."""
        if isinstance(inputs, Component):
            inputs = [inputs]
        changeable_events: list[tuple[Block, str]] = (
            [(i, "change") for i in inputs if hasattr(i, "change")] if inputs else []
        )
        if isinstance(every, (int, float)):
            from gradio.components import Timer

            every = Timer(every)
        if every:
            changeable_events.append((every, "tick"))
        self.load_event_to_attach = (
            callable,
            changeable_events,
            inputs,
        )

    def process_example(self, value):
        """
        Process the input data in a way that can be displayed by the examples dataset component in the front-end.
        By default, this calls the `.postprocess()` method of the component. However, if the `.postprocess()` method is
        computationally intensive, or returns a large payload, a custom implementation may be appropriate.

        For example,  the `process_example()` method of the `gr.Audio()` component only returns the name of the file, not
        the processed audio file. The `.process_example()` method of the `gr.Dataframe()` returns the head of a dataframe
        instead of the full dataframe.

        The return value of this method must be json-serializable to put in the config.
        """
        return self.postprocess(value)

    def as_example(self, value):
        """Deprecated and replaced by `process_example()`."""
        return self.process_example(value)

    def example_inputs(self) -> Any:
        """Deprecated and replaced by `example_payload()` and `example_value()`."""
        return self.example_payload()

    def example_payload(self) -> Any:
        """
        An example input data for this component, e.g. what is passed to this component's preprocess() method.
        This is used to generate the docs for the View API page for Gradio apps using this component.
        """
        raise NotImplementedError()

    def example_value(self) -> Any:
        """
        An example output data for this component, e.g. what is passed to this component's postprocess() method.
        This is used to generate an example value if this component is used as a template for a custom component.
        """
        raise NotImplementedError()

    def api_info(self) -> dict[str, Any]:
        """
        The typing information for this component as a dictionary whose values are a list of 2 strings: [Python type, language-agnostic description].
        Keys of the dictionary are: raw_input, raw_output, serialized_input, serialized_output
        """
        if self.data_model is not None:
            schema = self.data_model.model_json_schema()
            desc = schema.pop("description", None)
            schema["additional_description"] = desc
            return schema
        raise NotImplementedError(
            f"The api_info method has not been implemented for {self.get_block_name()}"
        )

    def api_info_as_input(self) -> dict[str, Any]:
        return self.api_info()

    def api_info_as_output(self) -> dict[str, Any]:
        return self.api_info()

    def flag(self, payload: Any, flag_dir: str | Path = "") -> str:
        """
        Write the component's value to a format that can be stored in a csv or jsonl format for flagging.
        """
        if self.data_model:
            payload = self.data_model.from_json(payload)
            Path(flag_dir).mkdir(exist_ok=True)
            payload = payload.copy_to_dir(flag_dir).model_dump()
        if isinstance(payload, BaseModel):
            payload = payload.model_dump()
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        return payload

    def read_from_flag(self, payload: Any):
        """
        Convert the data from the csv or jsonl file into the component state.
        """
        if self.data_model:
            return self.data_model.from_json(json.loads(payload))
        return payload


class FormComponent(Component):
    """
    A base class for components that are typically used in forms (e.g. Textbox, Dropdown). These
    components will be grouped together in the UI to provide a more condensed layout. Components
    that are not rendered in the UI (e.g. State) should also inherit from this class, as it will
    prevent them from breaking the grouping, see: https://github.com/gradio-app/gradio/issues/10330
    """

    def get_expected_parent(self) -> type[Form] | None:
        if getattr(self, "container", None) is False:
            return None
        return Form

    def preprocess(self, payload: Any) -> Any:
        return payload

    def postprocess(self, value):
        return value


class StreamingOutput(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.streaming: bool

    @abc.abstractmethod
    async def stream_output(
        self, value, output_id: str, first_chunk: bool
    ) -> tuple[MediaStreamChunk | None, FileDataDict | dict]:
        pass

    @abc.abstractmethod
    async def combine_stream(
        self,
        stream: list[bytes],
        desired_output_format: str | None = None,
        only_file=False,
    ) -> GradioDataModel | FileData:
        """Combine all of the stream chunks into a single file.

        This is needed for downloading the stream and for caching examples.
        If `only_file` is True, only the FileData corresponding to the file should be returned (needed for downloading the stream).
        The desired_output_format optionally converts the combined file. Should only be used for cached examples.
        """
        pass


class StreamingInput(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @abc.abstractmethod
    def check_streamable(self):
        """Used to check if streaming is supported given the input."""
        pass


def component(cls_name: str, render: bool) -> Component:
    obj = utils.component_or_layout_class(cls_name)(render=render)
    if isinstance(obj, BlockContext):
        raise ValueError(f"Invalid component: {obj.__class__}")
    if not isinstance(obj, Component):
        raise TypeError(f"Expected a Component instance, but got {obj.__class__}")
    return obj


def get_component_instance(
    comp: str | dict | Component, render: bool = False, unrender: bool = False
) -> Component:
    """
    Returns a component instance from a string, dict, or Component object.
    Parameters:
        comp: the component to instantiate. If a string, must be the name of a component, e.g. "dropdown". If a dict, must have a "name" key, e.g. {"name": "dropdown", "choices": ["a", "b"]}. If a Component object, will be returned as is.
        render: whether to render the component. If True, renders the component (if not already rendered). If False, does not do anything.
        unrender: whether to unrender the component. If True, unrenders the the component (if already rendered) -- this is useful when constructing an Interface or ChatInterface inside of a Blocks. If False, does not do anything.
    """
    if isinstance(comp, str):
        component_obj = component(comp, render=render)
    elif isinstance(comp, dict):
        name = comp.pop("name")
        component_cls = utils.component_or_layout_class(name)
        component_obj = component_cls(**comp, render=render)
        if isinstance(component_obj, BlockContext):
            raise ValueError(f"Invalid component: {name}")
    elif isinstance(comp, Component):
        component_obj = comp
    else:
        raise ValueError(
            f"Component must be provided as a `str` or `dict` or `Component` but is {comp}"
        )

    if render and not component_obj.is_rendered:
        component_obj.render()
    elif unrender and component_obj.is_rendered:
        component_obj.unrender()
    if not isinstance(component_obj, Component):
        raise TypeError(
            f"Expected a Component instance, but got {component_obj.__class__}"
        )
    return component_obj


=== File: gradio/components/browser_state.py ===
"""gr.BrowserState() component."""

from __future__ import annotations

import secrets
import string
from typing import Any

from gradio_client.documentation import document

from gradio.components.base import FormComponent
from gradio.events import Events


@document()
class BrowserState(FormComponent):
    EVENTS = [Events.change]
    """
    Special component that stores state in the browser's localStorage in an encrypted format.
    """

    def __init__(
        self,
        default_value: Any = None,
        *,
        storage_key: str | None = None,
        secret: str | None = None,
        render: bool = True,
    ):
        """
        Parameters:
            default_value: the default value that will be used if no value is found in localStorage. Should be a json-serializable value.
            storage_key: the key to use in localStorage. If None, a random key will be generated.
            secret: the secret key to use for encryption. If None, a random key will be generated (recommended).
            render: should always be True, is included for consistency with other components.
        """
        self.default_value = default_value
        self.secret = secret or "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(16)
        )
        self.storage_key = storage_key or "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(16)
        )
        self._value_description = "any json-serializable value"

        super().__init__(render=render)

    def preprocess(self, payload: Any) -> Any:
        """
        Parameters:
            payload: Value from local storage
        Returns:
            Passes value through unchanged
        """
        if payload is None:
            return self.default_value
        return payload

    def postprocess(self, value: Any) -> Any:
        """
        Parameters:
            value: Value to store in local storage
        Returns:
            Passes value through unchanged
        """
        return value

    def api_info(self) -> dict[str, Any]:
        return {"type": {}, "description": "any json-serializable value"}

    def example_payload(self) -> Any:
        return "test"

    def example_value(self) -> Any:
        return "test"


=== File: gradio/components/button.py ===
"""gr.Button() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Button(Component):
    """
    Creates a button that can be assigned arbitrary .click() events. The value (label) of the button can be used as an input to the function (rarely used) or set via the output of a function.
    """

    EVENTS = [Events.click]

    def __init__(
        self,
        value: str | I18nData | Callable = "Run",
        *,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary", "stop", "huggingface"] = "secondary",
        size: Literal["sm", "md", "lg"] = "lg",
        icon: str | Path | None = None,
        link: str | None = None,
        visible: bool = True,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        scale: int | None = None,
        min_width: int | None = None,
    ):
        """
        Parameters:
            value: default text for the button to display. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            every: continuously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            variant: sets the background and text color of the button. Use 'primary' for main call-to-action buttons, 'secondary' for a more subdued style, 'stop' for a stop button, 'huggingface' for a black background with white text, consistent with Hugging Face's button styles.
            size: size of the button. Can be "sm", "md", or "lg".
            icon: URL or path to the icon file to display within the button. If None, no icon will be displayed.
            link: URL to open when the button is clicked. If None, no link will be used.
            visible: if False, component will be hidden.
            interactive: if False, the Button will be in a disabled state.
            elem_id: an optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: an optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: if False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
        """
        super().__init__(
            every=every,
            inputs=inputs,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            interactive=interactive,
            scale=scale,
            min_width=min_width,
        )
        self.icon = self.serve_static_file(icon)
        self.variant = variant
        self.size = size
        self.link = link

    @property
    def skip_api(self):
        return True

    def preprocess(self, payload: str | None) -> str | None:
        """
        Parameters:
            payload: string corresponding to the button label
        Returns:
            (Rarely used) the `str` corresponding to the button label when the button is clicked
        """
        return payload

    def postprocess(self, value: str | None) -> str | None:
        """
        Parameters:
            value: string corresponding to the button label
        Returns:
            Expects a `str` value that is set as the button label
        """
        return str(value)

    def example_payload(self) -> Any:
        return "Run"

    def example_value(self) -> Any:
        return "Run"


=== File: gradio/components/chatbot.py ===
"""gr.Chatbot() component."""

from __future__ import annotations

import copy
import inspect
import warnings
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Union,
    cast,
)

from gradio_client import utils as client_utils
from gradio_client.documentation import document
from typing_extensions import NotRequired, TypedDict

from gradio import utils
from gradio.component_meta import ComponentMeta
from gradio.components import (
    Component as GradioComponent,
)
from gradio.components.base import Component
from gradio.data_classes import FileData, GradioModel, GradioRootModel
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData


@document()
class MetadataDict(TypedDict):
    """
    A typed dictionary to represent metadata for a message in the Chatbot component. An
    instance of this dictionary is used for the `metadata` field in a ChatMessage when
    the chat message should be displayed as a thought.
    Parameters:
        title: The title of the "thought" message. Required if the message is to be displayed as a thought.
        id: The ID of the message. Only used for nested thoughts. Nested thoughts can be nested by setting the parent_id to the id of the parent thought.
        parent_id: The ID of the parent message. Only used for nested thoughts.
        log: A string message to display next to the thought title in a subdued font.
        duration: The duration of the message in seconds. Appears next to the thought title in a subdued font inside a parentheses.
        status: if set to `"pending"`, a spinner appears next to the thought title and the accordion is initialized open.  If `status` is `"done"`, the thought accordion is initialized closed. If `status` is not provided, the thought accordion is initialized open and no spinner is displayed.
    """

    title: NotRequired[str]
    id: NotRequired[int | str]
    parent_id: NotRequired[int | str]
    log: NotRequired[str]
    duration: NotRequired[float]
    status: NotRequired[Literal["pending", "done"]]


@document()
class OptionDict(TypedDict):
    """
    A typed dictionary to represent an option in a ChatMessage. A list of these
    dictionaries is used for the `options` field in a ChatMessage.
    Parameters:
        value: The value to return when the option is selected.
        label: The text to display in the option, if different from the value.
    """

    value: str
    label: NotRequired[str]


class FileDataDict(TypedDict):
    path: str  # server filepath
    url: NotRequired[Optional[str]]  # normalised server url
    size: NotRequired[Optional[int]]  # size in bytes
    orig_name: NotRequired[Optional[str]]  # original filename
    mime_type: NotRequired[Optional[str]]
    is_stream: NotRequired[bool]
    meta: dict[Literal["_type"], Literal["gradio.FileData"]]


class MessageDict(TypedDict):
    content: str | FileDataDict | tuple | Component
    role: Literal["user", "assistant", "system"]
    metadata: NotRequired[MetadataDict]
    options: NotRequired[list[OptionDict]]


class FileMessage(GradioModel):
    file: FileData
    alt_text: Optional[str] = None


class ComponentMessage(GradioModel):
    component: str
    value: Any
    constructor_args: dict[str, Any]
    props: dict[str, Any]


class ChatbotDataTuples(GradioRootModel):
    root: list[
        tuple[
            Union[str, FileMessage, ComponentMessage, None],
            Union[str, FileMessage, ComponentMessage, None],
        ]
    ]


class Message(GradioModel):
    role: str
    metadata: Optional[MetadataDict] = None
    content: Union[str, FileMessage, ComponentMessage]
    options: Optional[list[OptionDict]] = None


class ExampleMessage(TypedDict):
    icon: NotRequired[
        str | FileDataDict
    ]  # filepath or url to an image to be shown in example box
    display_text: NotRequired[
        str
    ]  # text to be shown in example box. If not provided, main_text will be shown
    text: NotRequired[str]  # text to be added to chatbot when example is clicked
    files: NotRequired[
        Sequence[str | FileDataDict]
    ]  # list of file paths or URLs to be added to chatbot when example is clicked


@document()
@dataclass
class ChatMessage:
    """
    A dataclass that represents a message in the Chatbot component (with type="messages"). The only required field is `content`. The value of `gr.Chatbot` is a list of these dataclasses.
    Parameters:
        content: The content of the message. Can be a string or a Gradio component.
        role: The role of the message, which determines the alignment of the message in the chatbot. Can be "user", "assistant", or "system". Defaults to "assistant".
        metadata: The metadata of the message, which is used to display intermediate thoughts / tool usage. Should be a dictionary with the following keys: "title" (required to display the thought), and optionally: "id" and "parent_id" (to nest thoughts), "duration" (to display the duration of the thought), "status" (to display the status of the thought).
        options: The options of the message. A list of Option objects, which are dictionaries with the following keys: "label" (the text to display in the option), and optionally "value" (the value to return when the option is selected if different from the label).
    """

    content: str | FileData | Component | FileDataDict | tuple | list
    role: Literal["user", "assistant", "system"] = "assistant"
    metadata: MetadataDict = field(default_factory=MetadataDict)
    options: list[OptionDict] = field(default_factory=list)


class ChatbotDataMessages(GradioRootModel):
    root: list[Message]


TupleFormat = Sequence[
    tuple[Union[str, tuple[str], None], Union[str, tuple[str], None]]
    | list[Union[str, tuple[str], None]]
]

if TYPE_CHECKING:
    from gradio.components import Timer


def import_component_and_data(
    component_name: str,
) -> GradioComponent | ComponentMeta | Any | None:
    try:
        for component in utils.get_all_components():
            if component_name == component.__name__ and isinstance(
                component, ComponentMeta
            ):
                return component
    except ModuleNotFoundError as e:
        raise ValueError(f"Error importing {component_name}: {e}") from e
    except AttributeError:
        pass


@document()
class Chatbot(Component):
    """
    Creates a chatbot that displays user-submitted messages and responses. Supports a subset of Markdown including bold, italics, code, tables.
    Also supports audio/video/image files, which are displayed in the Chatbot, and other kinds of files which are displayed as links. This
    component is usually used as an output component.

    Demos: chatbot_simple, chatbot_streaming, chatbot_with_tools, chatbot_core_components
    Guides: creating-a-chatbot-fast, creating-a-custom-chatbot-with-blocks, agents-and-tool-usage
    """

    EVENTS = [
        Events.change,
        Events.select,
        Events.like,
        Events.retry,
        Events.undo,
        Events.example_select,
        Events.option_select,
        Events.clear,
        Events.copy,
        Events.edit,
    ]

    def __init__(
        self,
        value: (list[MessageDict | Message] | TupleFormat | Callable | None) = None,
        *,
        type: Literal["messages", "tuples"] | None = None,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        autoscroll: bool = True,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        height: int | str | None = 400,
        resizable: bool = False,
        resizeable: bool = False,  # Deprecated, TODO: Remove
        max_height: int | str | None = None,
        min_height: int | str | None = None,
        editable: Literal["user", "all"] | None = None,
        latex_delimiters: list[dict[str, str | bool]] | None = None,
        rtl: bool = False,
        show_share_button: bool | None = None,
        show_copy_button: bool = False,
        watermark: str | None = None,
        avatar_images: tuple[str | Path | None, str | Path | None] | None = None,
        sanitize_html: bool = True,
        render_markdown: bool = True,
        feedback_options: list[str] | tuple[str, ...] | None = ("Like", "Dislike"),
        feedback_value: Sequence[str | None] | None = None,
        bubble_full_width=None,
        line_breaks: bool = True,
        layout: Literal["panel", "bubble"] | None = None,
        placeholder: str | None = None,
        examples: list[ExampleMessage] | None = None,
        show_copy_all_button=False,
        allow_file_downloads=True,
        group_consecutive_messages: bool = True,
        allow_tags: list[str] | bool = False,
    ):
        """
        Parameters:
            value: Default list of messages to show in chatbot, where each message is of the format {"role": "user", "content": "Help me."}. Role can be one of "user", "assistant", or "system". Content should be either text, or media passed as a Gradio component, e.g. {"content": gr.Image("lion.jpg")}. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            type: The format of the messages passed into the chat history parameter of `fn`. If "messages", passes the value as a list of dictionaries with openai-style "role" and "content" keys. The "content" key's value should be one of the following - (1) strings in valid Markdown (2) a dictionary with a "path" key and value corresponding to the file to display or (3) an instance of a Gradio component. At the moment Image, Plot, Video, Gallery, Audio, HTML, and Model3D are supported. The "role" key should be one of 'user' or 'assistant'. Any other roles will not be displayed in the output. If this parameter is 'tuples', expects a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message, but this format is deprecated.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            autoscroll: If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will scroll.
            resizable: If True, the user of the Gradio app can resize the chatbot by dragging the bottom right corner.
            max_height: The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will scroll. If messages are shorter than the height, the component will shrink to fit the content. Will not have any effect if `height` is set and is smaller than `max_height`.
            min_height: The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will expand to fit the content. Will not have any effect if `height` is set and is larger than `min_height`.
            editable: Allows user to edit messages in the chatbot. If set to "user", allows editing of user messages. If set to "all", allows editing of assistant messages as well.
            latex_delimiters: A list of dicts of the form {"left": open delimiter (str), "right": close delimiter (str), "display": whether to display in newline (bool)} that will be used to render LaTeX expressions. If not provided, `latex_delimiters` is set to `[{ "left": "$$", "right": "$$", "display": True }]`, so only expressions enclosed in $$ delimiters will be rendered as LaTeX, and in a new line. Pass in an empty list to disable LaTeX rendering. For more information, see the [KaTeX documentation](https://katex.org/docs/autorender.html).
            rtl: If True, sets the direction of the rendered text to right-to-left. Default is False, which renders text left-to-right.
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            show_copy_button: If True, will show a copy button for each chatbot message.
            watermark: If provided, this text will be appended to the end of messages copied from the chatbot, after a blank line. Useful for indicating that the message is generated by an AI model.
            avatar_images: Tuple of two avatar image paths or URLs for user and bot (in that order). Pass None for either the user or bot image to skip. Must be within the working directory of the Gradio app or an external URL.
            sanitize_html: If False, will disable HTML sanitization for chatbot messages. This is not recommended, as it can lead to security vulnerabilities.
            render_markdown: If False, will disable Markdown rendering for chatbot messages.
            feedback_options: A list of strings representing the feedback options that will be displayed to the user. The exact case-sensitive strings "Like" and "Dislike" will render as thumb icons, but any other choices will appear under a separate flag icon.
            feedback_value: A list of strings representing the feedback state for entire chat. Only works when type="messages". Each entry in the list corresponds to that assistant message, in order, and the value is the feedback given (e.g. "Like", "Dislike", or any custom feedback option) or None if no feedback was given for that message.
            bubble_full_width: Deprecated.
            line_breaks: If True (default), will enable Github-flavored Markdown line breaks in chatbot messages. If False, single new lines will be ignored. Only applies if `render_markdown` is True.
            layout: If "panel", will display the chatbot in a llm style layout. If "bubble", will display the chatbot with message bubbles, with the user and bot messages on alterating sides. Will default to "bubble".
            placeholder: a placeholder message to display in the chatbot when it is empty. Centered vertically and horizontally in the Chatbot. Supports Markdown and HTML. If None, no placeholder is displayed.
            examples: A list of example messages to display in the chatbot before any user/assistant messages are shown. Each example should be a dictionary with an optional "text" key representing the message that should be populated in the Chatbot when clicked, an optional "files" key, whose value should be a list of files to populate in the Chatbot, an optional "icon" key, whose value should be a filepath or URL to an image to display in the example box, and an optional "display_text" key, whose value should be the text to display in the example box. If "display_text" is not provided, the value of "text" will be displayed.
            show_copy_all_button: If True, will show a copy all button that copies all chatbot messages to the clipboard.
            allow_file_downloads: If True, will show a download button for chatbot messages that contain media. Defaults to True.
            group_consecutive_messages: If True, will display consecutive messages from the same role in the same bubble. If False, will display each message in a separate bubble. Defaults to True.
            allow_tags: If a list of tags is provided, these tags will be preserved in the output chatbot messages, even if `sanitize_html` is `True`. For example, if this list is ["thinking"], the tags `<thinking>` and `</thinking>` will not be removed. If True, all custom tags (non-standard HTML tags) will be preserved. If False, no tags will be preserved (default behavior).
        """
        if type is None:
            warnings.warn(
                "You have not specified a value for the `type` parameter. Defaulting to the 'tuples' format for chatbot messages, but this is deprecated and will be removed in a future version of Gradio. Please set type='messages' instead, which uses openai-style dictionaries with 'role' and 'content' keys.",
                UserWarning,
                stacklevel=3,
            )
            type = "tuples"
        elif type == "tuples":
            warnings.warn(
                "The 'tuples' format for chatbot messages is deprecated and will be removed in a future version of Gradio. Please set type='messages' instead, which uses openai-style 'role' and 'content' keys.",
                UserWarning,
                stacklevel=3,
            )
        if type not in ["messages", "tuples"]:
            raise ValueError(
                f"The `type` parameter must be 'messages' or 'tuples', received: {type}"
            )
        self.type: Literal["tuples", "messages"] = type
        self._setup_data_model()
        self.autoscroll = autoscroll
        self.height = height
        if resizeable is not False:
            warnings.warn(
                "The 'resizeable' parameter is deprecated and will be removed in a future version. Please use the 'resizable' (note the corrected spelling) parameter instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            self.resizable = resizeable
        self.resizable = resizable
        self.max_height = max_height
        self.min_height = min_height
        self.editable = editable
        self.rtl = rtl
        self.group_consecutive_messages = group_consecutive_messages
        if latex_delimiters is None:
            latex_delimiters = [{"left": "$$", "right": "$$", "display": True}]
        self.latex_delimiters = latex_delimiters
        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        self.render_markdown = render_markdown
        self.show_copy_button = show_copy_button
        self.watermark = watermark
        self.sanitize_html = sanitize_html
        if bubble_full_width is not None:
            warnings.warn(
                "The 'bubble_full_width' parameter is deprecated and will be removed in a future version. This parameter no longer has any effect.",
                DeprecationWarning,
                stacklevel=3,
            )
        self.bubble_full_width = None
        self.line_breaks = line_breaks
        self.layout = layout
        self.show_copy_all_button = show_copy_all_button
        self.allow_file_downloads = allow_file_downloads
        self.feedback_options = feedback_options
        self.feedback_value = feedback_value
        self.allow_tags = allow_tags if allow_tags else False
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self.avatar_images: list[dict | None] = [None, None]
        if avatar_images is None:
            pass
        else:
            self.avatar_images = [
                self.serve_static_file(avatar_images[0]),
                self.serve_static_file(avatar_images[1]),
            ]
        self.placeholder = placeholder

        self.examples = examples
        self._setup_examples()
        self._value_description = (
            "a list of chat message dictionaries in openai format, e.g. {'role': 'user', 'content': 'Hello'}"
            if self.type == "messages"
            else "a list of 2-part tuples, where each tuple contains the user message and the bot response message"
        )

    def _setup_data_model(self):
        if self.type == "messages":
            self.data_model = ChatbotDataMessages
        else:
            self.data_model = ChatbotDataTuples

    def _setup_examples(self):
        if self.examples is not None:
            for i, example in enumerate(self.examples):
                if "icon" in example and isinstance(example["icon"], str):
                    example["icon"] = self.serve_static_file(example["icon"])
                file_info = example.get("files")
                if file_info is not None and not isinstance(file_info, list):
                    raise Error(
                        "Data incompatible with files format. The 'files' passed should be a list of file paths or URLs."
                    )
                if file_info is not None:
                    for i, file in enumerate(file_info):
                        if isinstance(file, str):
                            orig_name = Path(file).name
                            file_data = self.serve_static_file(file)
                            if file_data is not None:
                                file_data["orig_name"] = orig_name
                                file_data["mime_type"] = client_utils.get_mimetype(
                                    orig_name
                                )
                                file_data = FileDataDict(**file_data)
                                file_info[i] = file_data

    @staticmethod
    def _check_format(messages: Any, type: Literal["messages", "tuples"]):
        if type == "messages":
            all_valid = all(
                isinstance(message, dict)
                and "role" in message
                and "content" in message
                or isinstance(message, ChatMessage | Message)
                for message in messages
            )
            if not all_valid:
                raise Error(
                    "Data incompatible with messages format. Each message should be a dictionary with 'role' and 'content' keys or a ChatMessage object."
                )
        elif not all(
            isinstance(message, (tuple, list)) and len(message) == 2
            for message in messages
        ):
            raise Error(
                "Data incompatible with tuples format. Each message should be a list of length 2."
            )

    def _preprocess_content(
        self,
        chat_message: str | FileMessage | ComponentMessage | None,
    ) -> str | GradioComponent | tuple[str | None] | tuple[str | None, str] | None:
        if chat_message is None:
            return None
        elif isinstance(chat_message, FileMessage):
            if chat_message.alt_text is not None:
                return (chat_message.file.path, chat_message.alt_text)
            else:
                return (chat_message.file.path,)
        elif isinstance(chat_message, str):
            return chat_message
        elif isinstance(chat_message, ComponentMessage):
            capitalized_component = (
                chat_message.component.upper()
                if chat_message.component in ("json", "html")
                else "Model3D"
                if chat_message.component == "model3d"
                else chat_message.component.capitalize()
            )
            component = import_component_and_data(capitalized_component)
            if component is not None:
                instance = component()  # type: ignore
                if not instance.data_model:
                    payload = chat_message.value
                elif issubclass(instance.data_model, GradioModel):
                    payload = instance.data_model(**chat_message.value)
                elif issubclass(instance.data_model, GradioRootModel):
                    payload = instance.data_model(root=chat_message.value)
                else:
                    payload = chat_message.value
                value = instance.preprocess(payload)
                return component(value=value, **chat_message.constructor_args)  # type: ignore
            else:
                raise ValueError(
                    f"Invalid component for Chatbot component: {chat_message.component}"
                )
        else:
            raise ValueError(f"Invalid message for Chatbot component: {chat_message}")

    def _preprocess_messages_tuples(
        self, payload: ChatbotDataTuples
    ) -> list[list[str | tuple[str] | tuple[str, str] | None]]:
        processed_messages = []
        for message_pair in payload.root:
            if not isinstance(message_pair, (tuple, list)):
                raise TypeError(
                    f"Expected a list of lists or list of tuples. Received: {message_pair}"
                )
            if len(message_pair) != 2:
                raise TypeError(
                    f"Expected a list of lists of length 2 or list of tuples of length 2. Received: {message_pair}"
                )
            processed_messages.append(
                [
                    self._preprocess_content(message_pair[0]),
                    self._preprocess_content(message_pair[1]),
                ]
            )
        return processed_messages

    def preprocess(
        self,
        payload: ChatbotDataTuples | ChatbotDataMessages | None,
    ) -> list[list[str | tuple[str] | tuple[str, str] | None]] | list[MessageDict]:
        """
        Parameters:
            payload: data as a ChatbotData object
        Returns:
            If type is 'tuples', passes the messages in the chatbot as a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list has 2 elements: the user message and the response message. Each message can be (1) a string in valid Markdown, (2) a tuple if there are displayed files: (a filepath or URL to a file, [optional string alt text]), or (3) None, if there is no message displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports.
        """
        if payload is None:
            return []
        if self.type == "tuples":
            if not isinstance(payload, ChatbotDataTuples):
                raise Error("Data incompatible with the tuples format")
            return self._preprocess_messages_tuples(cast(ChatbotDataTuples, payload))
        if not isinstance(payload, ChatbotDataMessages):
            raise Error("Data incompatible with the messages format")
        message_dicts = []
        for message in payload.root:
            message_dict = cast(MessageDict, message.model_dump())
            message_dict["content"] = self._preprocess_content(message.content)
            message_dicts.append(message_dict)
        return message_dicts

    @staticmethod
    def _get_alt_text(chat_message: dict | list | tuple | GradioComponent):
        if isinstance(chat_message, dict):
            return chat_message.get("alt_text")
        elif not isinstance(chat_message, GradioComponent) and len(chat_message) > 1:
            return chat_message[1]

    @staticmethod
    def _create_file_message(chat_message, filepath):
        mime_type = client_utils.get_mimetype(filepath)

        return FileMessage(
            file=FileData(path=filepath, mime_type=mime_type),
            alt_text=Chatbot._get_alt_text(chat_message),
        )

    def _postprocess_content(
        self,
        chat_message: str
        | tuple
        | list
        | FileDataDict
        | FileData
        | GradioComponent
        | ComponentMessage
        | None,
    ) -> str | FileMessage | ComponentMessage | None:
        if chat_message is None:
            return None
        if isinstance(chat_message, (FileMessage, ComponentMessage, str)):
            return chat_message
        elif isinstance(chat_message, FileData):
            return FileMessage(file=chat_message)
        elif isinstance(chat_message, GradioComponent):
            chat_message.unrender()
            component = import_component_and_data(type(chat_message).__name__)
            if component:
                chat_message.constructor_args["render"] = False
                component = chat_message.__class__(**chat_message.constructor_args)
                chat_message.constructor_args.pop("value", None)
                config = component.get_config()
                return ComponentMessage(
                    component=type(chat_message).__name__.lower(),
                    value=config.get("value", None),
                    constructor_args=chat_message.constructor_args,
                    props=config,
                )
        elif isinstance(chat_message, dict) and "path" in chat_message:
            filepath = chat_message["path"]
            return self._create_file_message(chat_message, filepath)
        elif isinstance(chat_message, (tuple, list)):
            filepath = str(chat_message[0])
            return self._create_file_message(chat_message, filepath)
        else:
            raise ValueError(f"Invalid message for Chatbot component: {chat_message}")

    def _postprocess_messages_tuples(self, value: TupleFormat) -> ChatbotDataTuples:
        processed_messages = []
        for message_pair in value:
            processed_messages.append(
                [
                    self._postprocess_content(message_pair[0]),
                    self._postprocess_content(message_pair[1]),
                ]
            )
        return ChatbotDataTuples(root=processed_messages)

    def _postprocess_message_messages(
        self, message: MessageDict | ChatMessage
    ) -> Message:
        message = copy.deepcopy(message)
        if isinstance(message, dict):
            message["content"] = self._postprocess_content(message["content"])
            msg = Message(**message)  # type: ignore
        elif isinstance(message, ChatMessage):
            message.content = self._postprocess_content(message.content)  # type: ignore
            msg = Message(
                role=message.role,
                content=message.content,  # type: ignore
                metadata=message.metadata,  # type: ignore
                options=message.options,
            )
        elif isinstance(message, Message):
            return message
        else:
            raise Error(
                f"Invalid message for Chatbot component: {message}", visible=False
            )

        msg.content = (
            inspect.cleandoc(msg.content)
            if isinstance(msg.content, str)
            else msg.content
        )
        return msg

    def postprocess(
        self,
        value: TupleFormat | list[MessageDict | Message] | None,
    ) -> ChatbotDataTuples | ChatbotDataMessages:
        """
        Parameters:
            value: If type is `tuples`, expects a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message. The individual messages can be (1) strings in valid Markdown, (2) tuples if sending files: (a filepath or URL to a file, [optional string alt text]) -- if the file is image/video/audio, it is displayed in the Chatbot, or (3) None, in which case the message is not displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports.
        Returns:
            an object of type ChatbotData
        """
        data_model = cast(
            Union[type[ChatbotDataTuples], type[ChatbotDataMessages]], self.data_model
        )
        if value is None:
            return data_model(root=[])
        if self.type == "tuples":
            self._check_format(value, "tuples")
            return self._postprocess_messages_tuples(cast(TupleFormat, value))
        self._check_format(value, "messages")
        processed_messages = [
            self._postprocess_message_messages(cast(MessageDict, message))
            for message in value
        ]
        return ChatbotDataMessages(root=processed_messages)

    def example_payload(self) -> Any:
        if self.type == "messages":
            return [
                Message(role="user", content="Hello!").model_dump(),
                Message(role="assistant", content="How can I help you?").model_dump(),
            ]
        return [["Hello!", None]]

    def example_value(self) -> Any:
        if self.type == "messages":
            return [
                Message(role="user", content="Hello!").model_dump(),
                Message(role="assistant", content="How can I help you?").model_dump(),
            ]
        return [["Hello!", None]]


=== File: gradio/components/checkbox.py ===
"""gr.Checkbox() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio_client.documentation import document

from gradio.components.base import Component, FormComponent
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Checkbox(FormComponent):
    """
    Creates a checkbox that can be set to `True` or `False`. Can be used as an input to pass a boolean value to a function or as an output
    to display a boolean value.

    Demos: sentence_builder, hello_world_3
    """

    EVENTS = [Events.change, Events.input, Events.select]

    def __init__(
        self,
        value: bool | Callable = False,
        *,
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            value: if True, checked by default. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, this checkbox can be checked; if False, checking will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def api_info(self) -> dict[str, Any]:
        return {"type": "boolean"}

    def example_payload(self) -> bool:
        return True

    def example_value(self) -> bool:
        return True

    def preprocess(self, payload: bool | None) -> bool | None:
        """
        Parameters:
            payload: the status of the checkbox
        Returns:
            Passes the status of the checkbox as a `bool`.
        """
        return payload

    def postprocess(self, value: bool | None) -> bool | None:
        """
        Parameters:
            value: Expects a `bool` value that is set as the status of the checkbox
        Returns:
            The same `bool` value that is set as the status of the checkbox
        """
        return bool(value)


=== File: gradio/components/checkboxgroup.py ===
"""gr.CheckboxGroup() component"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component, FormComponent
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class CheckboxGroup(FormComponent):
    """
    Creates a set of checkboxes. Can be used as an input to pass a set of values to a function or as an output to display values, a subset of which are selected.
    Demos: sentence_builder
    """

    EVENTS = [Events.change, Events.input, Events.select]

    def __init__(
        self,
        choices: Sequence[str | int | float | tuple[str, str | int | float]]
        | None = None,
        *,
        value: Sequence[str | float | int] | str | float | int | Callable | None = None,
        type: Literal["value", "index"] = "value",
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            choices: A list of string or numeric options to select from. An option can also be a tuple of the form (name, value), where name is the displayed name of the checkbox button and value is the value to be passed to the function, or returned by the function.
            value: Default selected list of options. If a single choice is selected, it can be passed in as a string or numeric type. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            type: Type of value to be returned by component. "value" returns the list of strings of the choices selected, "index" returns the list of indices of the choices selected.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: If True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: Relative width compared to adjacent Components in a Row. For example, if Component A has scale=2, and Component B has scale=1, A will be twice as wide as B. Should be an integer.
            min_width: Minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: If True, choices in this checkbox group will be checkable; if False, checking will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.choices = (
            # Although we expect choices to be a list of tuples, it can be a list of tuples if the Gradio app
            # is loaded with gr.load() since Python tuples are converted to lists in JSON.
            [tuple(c) if isinstance(c, (tuple, list)) else (str(c), c) for c in choices]
            if choices
            else []
        )
        valid_types = ["value", "index"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = f"one or more of {self.choices}"

    def example_payload(self) -> Any:
        return [self.choices[0][1]] if self.choices else None

    def example_value(self) -> Any:
        return [self.choices[0][1]] if self.choices else None

    def api_info(self) -> dict[str, Any]:
        return {
            "items": {"enum": [c[1] for c in self.choices], "type": "string"},
            "title": "Checkbox Group",
            "type": "array",
        }

    def preprocess(
        self, payload: list[str | int | float]
    ) -> list[str | int | float] | list[int | None]:
        """
        Parameters:
            payload: the list of checked checkboxes' values
        Returns:
            Passes the list of checked checkboxes as a `list[str | int | float]` or their indices as a `list[int]` into the function, depending on `type`.
        """
        choice_values = [value for _, value in self.choices]
        for value in payload:
            if value not in choice_values:
                raise Error(
                    f"Value: {value!r} (type: {type(value)}) is not in the list of choices: {choice_values}"
                )
        if self.type == "value":
            return payload
        elif self.type == "index":
            return [
                choice_values.index(choice) if choice in choice_values else None
                for choice in payload
            ]
        else:
            raise ValueError(
                f"Unknown type: {self.type}. Please choose from: 'value', 'index'."
            )

    def postprocess(
        self, value: list[str | int | float] | str | int | float | None
    ) -> list[str | int | float]:
        """
        Parameters:
            value: Expects a `list[str | int | float]` of values or a single `str | int | float` value, the checkboxes with these values are checked.
        Returns:
            the list of checked checkboxes' values
        """
        if value is None:
            return []
        if not isinstance(value, list):
            value = [value]
        return value


=== File: gradio/components/clear_button.py ===
"""Predefined buttons with bound events that can be included in a gr.Blocks for convenience."""

from __future__ import annotations

import copy
import json
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components import Button, Component
from gradio.context import get_blocks_context
from gradio.data_classes import GradioModel, GradioRootModel
from gradio.utils import resolve_singleton

if TYPE_CHECKING:
    from gradio.components import Timer


@document("add")
class ClearButton(Button):
    """
    Button that clears the value of a component or a list of components when clicked. It is instantiated with the list of components to clear.
    Preprocessing: passes the button value as a {str} into the function
    Postprocessing: expects a {str} to be returned from a function, which is set as the label of the button
    """

    is_template = True

    def __init__(
        self,
        components: None | Sequence[Component] | Component = None,
        *,
        value: str = "Clear",
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary", "stop"] = "secondary",
        size: Literal["sm", "md", "lg"] = "lg",
        icon: str | Path | None = None,
        link: str | None = None,
        visible: bool = True,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        scale: int | None = None,
        min_width: int | None = None,
        api_name: str | None | Literal["False"] = None,
        show_api: bool = False,
    ):
        super().__init__(
            value,
            every=every,
            inputs=inputs,
            variant=variant,
            size=size,
            icon=icon,
            link=link,
            visible=visible,
            interactive=interactive,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            scale=scale,
            min_width=min_width,
        )
        self.api_name = api_name
        self.show_api = show_api

        if get_blocks_context():
            self.add(components)

    def add(self, components: None | Component | Sequence[Component]) -> ClearButton:
        """
        Adds a component or list of components to the list of components that will be cleared when the button is clicked.
        """
        from gradio.components import State  # Avoid circular import

        if not components:
            # This needs to be here because when the ClearButton is created in an gr.Interface, we don't
            # want to create dependencies for it before we have created the dependencies for the submit function.
            # We generally assume that the submit function dependency is the first thing created in an gr.Interface.
            return self

        if isinstance(components, Component):
            components = [components]
        none_values = []
        state_components = []
        initial_states = []
        for component in components:
            if isinstance(component, State):
                state_components.append(component)
                initial_states.append(copy.deepcopy(component.value))
            none = component.postprocess(None)
            if isinstance(none, (GradioModel, GradioRootModel)):
                none = none.model_dump()
            none_values.append(none)
        clear_values = json.dumps(none_values)
        self.click(
            None,
            [],
            components,
            js=f"() => {clear_values}",
            api_name=self.api_name,
            show_api=self.show_api,
        )
        if state_components:
            self.click(
                lambda: copy.deepcopy(resolve_singleton(initial_states)),
                None,
                state_components,
                api_name=self.api_name,
                show_api=self.show_api,
            )
        return self

    def preprocess(self, payload: str | None) -> str | None:
        """
        Parameters:
            payload: string corresponding to the button label
        Returns:
            (Rarely used) the `str` corresponding to the button label when the button is clicked
        """
        return payload

    def postprocess(self, value: str | None) -> str | None:
        """
        Parameters:
            value: string corresponding to the button label
        Returns:
            Expects a `str` value that is set as the button label
        """
        return value

    def example_payload(self) -> Any:
        return "Clear"

    def example_value(self) -> Any:
        return "Clear"


=== File: gradio/components/code.py ===
"""gr.Code() component"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document("languages")
class Code(Component):
    """
    Creates a code editor for viewing code (as an output component), or for entering and editing code (as an input component).
    """

    languages = [
        "python",
        "c",
        "cpp",
        "markdown",
        "latex",
        "json",
        "html",
        "css",
        "javascript",
        "jinja2",
        "typescript",
        "yaml",
        "dockerfile",
        "shell",
        "r",
        "sql",
        "sql-msSQL",
        "sql-mySQL",
        "sql-mariaDB",
        "sql-sqlite",
        "sql-cassandra",
        "sql-plSQL",
        "sql-hive",
        "sql-pgSQL",
        "sql-gql",
        "sql-gpSQL",
        "sql-sparkSQL",
        "sql-esper",
        None,
    ]

    EVENTS = [
        Events.change,
        Events.input,
        Events.focus,
        Events.blur,
    ]

    def __init__(
        self,
        value: str | Callable | None = None,
        language: Literal[
            "python",
            "c",
            "cpp",
            "markdown",
            "latex",
            "json",
            "html",
            "css",
            "javascript",
            "jinja2",
            "typescript",
            "yaml",
            "dockerfile",
            "shell",
            "r",
            "sql",
            "sql-msSQL",
            "sql-mySQL",
            "sql-mariaDB",
            "sql-sqlite",
            "sql-cassandra",
            "sql-plSQL",
            "sql-hive",
            "sql-pgSQL",
            "sql-gql",
            "sql-gpSQL",
            "sql-sparkSQL",
            "sql-esper",
        ]
        | None = None,
        *,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        lines: int = 5,
        max_lines: int | None = None,
        label: str | I18nData | None = None,
        interactive: bool | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        wrap_lines: bool = False,
        show_line_numbers: bool = True,
        autocomplete: bool = False,
    ):
        """
        Parameters:
            value: Default value to show in the code editor. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            language: The language to display the code as. Supported languages listed in `gr.Code.languages`.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            interactive: Whether user should be able to enter code or only view it.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            lines: Minimum number of visible lines to show in the code editor.
            max_lines: Maximum number of visible lines to show in the code editor. Defaults to None and will fill the height of the container.
            wrap_lines: If True, will wrap lines to the width of the container when overflow occurs. Defaults to False.
            show_line_numbers:  If True, displays line numbers, and if False, hides line numbers.
            autocomplete: If True, will show autocomplete suggestions for supported languages. Defaults to False.
        """
        if language not in Code.languages:
            raise ValueError(f"Language {language} not supported.")

        self.language = language
        self.lines = lines
        self.max_lines = max(lines, max_lines) if max_lines is not None else None
        self.wrap_lines = wrap_lines
        self.show_line_numbers = show_line_numbers
        self.autocomplete = autocomplete
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            interactive=interactive,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def preprocess(self, payload: str | None) -> str | None:
        """
        Parameters:
            payload: string corresponding to the code
        Returns:
            Passes the code entered as a `str`.
        """
        return payload

    def postprocess(self, value: str | None) -> None | str:
        """
        Parameters:
            value: Expects a `str` of code.
        Returns:
            Returns the code as a `str` stripped of leading and trailing whitespace.
        """
        if value is None:
            return None
        if isinstance(value, tuple):
            raise ValueError(
                "Code component does not support returning files as tuples anymore. "
                "Please read the file contents and return as str instead."
            )
        return value.strip()

    def api_info(self) -> dict[str, Any]:
        return {"type": "string"}

    def example_payload(self) -> Any:
        return "print('Hello World')"

    def example_value(self) -> Any:
        return "print('Hello World')"

    def process_example(self, value: str | None) -> str | None:
        return super().process_example(value)


=== File: gradio/components/color_picker.py ===
"""gr.ColorPicker() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class ColorPicker(Component):
    """
    Creates a color picker for user to select a color as string input. Can be used as an input to pass a color value to a function or as an output to display a color value.
    Demos: color_picker
    """

    EVENTS = [Events.change, Events.input, Events.submit, Events.focus, Events.blur]

    def __init__(
        self,
        value: str | Callable | None = None,
        *,
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            value: default color hex code to provide in color picker. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will be rendered as an editable color picker; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def example_payload(self) -> str:
        return "#000000"

    def example_value(self) -> str:
        return "#000000"

    def api_info(self) -> dict[str, Any]:
        return {"type": "string"}

    def preprocess(self, payload: str | None) -> str | None:
        """
        Parameters:
            payload: Color as hex string
        Returns:
            Passes selected color value as a hex `str` into the function.
        """
        if payload is None:
            return None
        else:
            return str(payload)

    def postprocess(self, value: str | None) -> str | None:
        """
        Parameters:
            value: Expects a hex `str` returned from function and sets color picker value to it.
        Returns:
            A `str` value that is set as the color picker value.
        """
        if value is None:
            return None
        else:
            return str(value)


=== File: gradio/components/dataframe.py ===
"""gr.Dataframe() component"""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Union,
)

import numpy as np
import semantic_version
from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import GradioModel
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl  # type: ignore
    from pandas.io.formats.style import Styler

    from gradio.components import Timer


def _is_polars_available():
    import importlib.util

    spec = importlib.util.find_spec("polars")
    return bool(spec)


def _import_polars():
    import polars as pl  # type: ignore

    return pl


class DataframeData(GradioModel):
    headers: list[Any]
    data: Union[list[list[Any]], list[tuple[Any, ...]]]
    metadata: Optional[dict[str, Optional[list[Any]]]] = None


@document()
class Dataframe(Component):
    """
    This component displays a table of value spreadsheet-like component. Can be used to display data as an output component, or as an input to collect data from the user.
    Demos: filter_records, matrix_transpose, tax_calculator, sort_records
    """

    EVENTS = [Events.change, Events.input, Events.select]

    data_model = DataframeData

    def __init__(
        self,
        value: pd.DataFrame
        | Styler
        | np.ndarray
        | pl.DataFrame
        | list
        | list[list]
        | dict
        | str
        | Callable
        | None = None,
        *,
        headers: list[str] | None = None,
        row_count: int | tuple[int, str] = (1, "dynamic"),
        col_count: int | tuple[int, str] | None = None,
        datatype: Literal["str", "number", "bool", "date", "markdown", "html", "image"]
        | Sequence[
            Literal["str", "number", "bool", "date", "markdown", "html"]
        ] = "str",
        type: Literal["pandas", "numpy", "array", "polars"] = "pandas",
        latex_delimiters: list[dict[str, str | bool]] | None = None,
        label: str | I18nData | None = None,
        show_label: bool | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        max_height: int | str = 500,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        wrap: bool = False,
        line_breaks: bool = True,
        column_widths: list[str | int] | None = None,
        show_fullscreen_button: bool = False,
        show_copy_button: bool = False,
        show_row_numbers: bool = False,
        max_chars: int | None = None,
        show_search: Literal["none", "search", "filter"] = "none",
        pinned_columns: int | None = None,
        static_columns: list[int] | None = None,
    ):
        """
        Parameters:
            value: Default value to display in the DataFrame. Supports pandas, numpy, polars, and list of lists. If a Styler is provided, it will be used to set the displayed value in the DataFrame (e.g. to set precision of numbers) if the `interactive` is False. If a Callable function is provided, the function will be called whenever the app loads to set the initial value of the component.
            headers: List of str header names. These are used to set the column headers of the dataframe if the value does not have headers. If None, no headers are shown.
            row_count: Limit number of rows for input and decide whether user can create new rows or delete existing rows. The first element of the tuple is an `int`, the row count; the second should be 'fixed' or 'dynamic', the new row behaviour. If an `int` is passed the rows default to 'dynamic'
            col_count: Limit number of columns for input and decide whether user can create new columns or delete existing columns. The first element of the tuple is an `int`, the number of columns; the second should be 'fixed' or 'dynamic', the new column behaviour. If an `int` is passed the columns default to 'dynamic'
            datatype: Datatype of values in sheet. Can be provided per column as a list of strings, or for the entire sheet as a single string. Valid datatypes are "str", "number", "bool", "date", and "markdown". Boolean columns will display as checkboxes.
            type: Type of value to be returned by component. "pandas" for pandas dataframe, "numpy" for numpy array, "polars" for polars dataframe, or "array" for a Python list of lists.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            latex_delimiters: A list of dicts of the form {"left": open delimiter (str), "right": close delimiter (str), "display": whether to display in newline (bool)} that will be used to render LaTeX expressions. If not provided, `latex_delimiters` is set to `[{ "left": "$$", "right": "$$", "display": True }]`, so only expressions enclosed in $$ delimiters will be rendered as LaTeX, and in a new line. Pass in an empty list to disable LaTeX rendering. For more information, see the [KaTeX documentation](https://katex.org/docs/autorender.html). Only applies to columns whose datatype is "markdown".
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            show_label: if True, will display label.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            max_height: The maximum height of the dataframe, specified in pixels if a number is passed, or in CSS units if a string is passed. If more rows are created than can fit in the height, a scrollbar will appear.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will allow users to edit the dataframe; if False, can only be used to display data. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            wrap: If True, the text in table cells will wrap when appropriate. If False and the `column_width` parameter is not set, the column widths will expand based on the cell contents and the table may need to be horizontally scrolled. If `column_width` is set, then any overflow text will be hidden.
            line_breaks: If True (default), will enable Github-flavored Markdown line breaks in chatbot messages. If False, single new lines will be ignored. Only applies for columns of type "markdown."
            column_widths: An optional list representing the width of each column. The elements of the list should be in the format "100px" (ints are also accepted and converted to pixel values) or "10%". The percentage width is calculated based on the viewport width of the table. If not provided, the column widths will be automatically determined based on the content of the cells.
            show_fullscreen_button: If True, will show a button to view the values in the table in fullscreen mode.
            show_copy_button: If True, will show a button to copy the table data to the clipboard.
            show_row_numbers: If True, will display row numbers in a separate column.
            max_chars: Maximum number of characters to display in each cell before truncating (single-clicking a cell value will still reveal the full content). If None, no truncation is applied.
            show_search: Show a search input in the toolbar. If "search", a search input is shown. If "filter", a search input and filter buttons are shown. If "none", no search input is shown.
            pinned_columns: If provided, will pin the specified number of columns from the left.
            static_columns: List of column indices (int) that should not be editable. Only applies when interactive=True. When specified, col_count is automatically set to "fixed" and columns cannot be inserted or deleted.
        """
        self.wrap = wrap
        self.row_count = self.__process_counts(row_count)
        self.static_columns = static_columns or []

        self.col_count = self.__process_counts(
            col_count, len(headers) if headers else 3
        )

        if self.static_columns and isinstance(self.col_count, tuple):
            self.col_count = (self.col_count[0], "fixed")

        self.__validate_headers(headers, self.col_count[0])

        self.headers = (
            headers
            if headers is not None
            else [str(i) for i in (range(1, self.col_count[0] + 1))]
        )
        self.datatype = datatype
        valid_types = ["pandas", "numpy", "array", "polars"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        if type == "polars" and not _is_polars_available():
            raise ImportError(
                "Polars is not installed. Please install using `pip install polars`."
            )
        self.type = type

        if latex_delimiters is None:
            latex_delimiters = [{"left": "$$", "right": "$$", "display": True}]
        self.latex_delimiters = latex_delimiters
        self.max_height = max_height
        self.line_breaks = line_breaks
        self.column_widths = [
            w
            if isinstance(w, str)
            and (w.endswith("px") or w.endswith("%") or w == "auto")
            else f"{w}px"
            for w in (column_widths or [])
        ]
        self.show_fullscreen_button = show_fullscreen_button
        self.show_copy_button = show_copy_button
        self.show_row_numbers = show_row_numbers
        self.max_chars = max_chars
        self.show_search = show_search
        self.pinned_columns = pinned_columns
        if (
            pinned_columns is not None
            and isinstance(col_count, tuple)
            and col_count[1] == "fixed"
            and pinned_columns > self.col_count[0]
        ):
            raise ValueError(
                f"pinned_columns ({pinned_columns}) cannot exceed the total number of columns ({self.col_count[0]}) when using fixed columns"
            )
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = (
            "a pandas dataframe"
            if type == "pandas"
            else "a list of lists"
            if type == "array"
            else "a numpy array"
            if type == "numpy"
            else "a polars dataframe"
        )

    def preprocess(
        self, payload: DataframeData
    ) -> pd.DataFrame | np.ndarray | pl.DataFrame | list[list]:
        """
        Parameters:
            payload: the uploaded spreadsheet data as an object with `headers` and `data` attributes. Note that sorting the columns in the browser will not affect the values passed to this function.
        Returns:
            Passes the uploaded spreadsheet data as a `pandas.DataFrame`, `numpy.array`, `polars.DataFrame`, or native 2D Python `list[list]` depending on `type`
        """
        import pandas as pd

        if self.type == "pandas":
            if payload.headers is not None:
                return pd.DataFrame(
                    [] if payload.data == [[]] else payload.data,
                    columns=payload.headers,  # type: ignore
                )
            else:
                return pd.DataFrame(payload.data)
        if self.type == "polars":
            polars = _import_polars()
            if payload.headers is not None:
                return polars.DataFrame(
                    [] if payload.data == [[]] else payload.data, schema=payload.headers
                )
            else:
                return polars.DataFrame(payload.data)
        if self.type == "numpy":
            return np.array(payload.data)
        elif self.type == "array":
            return payload.data  # type: ignore
        else:
            raise ValueError(
                "Unknown type: "
                + str(self.type)
                + ". Please choose from: 'pandas', 'numpy', 'array', 'polars'."
            )

    @staticmethod
    def is_empty(
        value: pd.DataFrame
        | Styler
        | np.ndarray
        | pl.DataFrame
        | list
        | list[list]
        | dict
        | str
        | None,
    ) -> bool:
        """
        Checks if the value of the dataframe provided is empty.
        """
        import pandas as pd
        from pandas.io.formats.style import Styler

        if value is None:
            return True
        if isinstance(value, pd.DataFrame):
            return value.empty
        elif isinstance(value, Styler):
            return value.data.empty  # type: ignore
        elif isinstance(value, np.ndarray):
            return value.size == 0
        elif _is_polars_available() and isinstance(value, _import_polars().DataFrame):
            return value.is_empty()
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], list):
                return len(value[0]) == 0
            return len(value) == 0
        elif isinstance(value, dict):
            if "data" in value:
                return len(value["data"]) == 0
            return len(value) == 0
        return False

    def get_headers(
        self,
        value: pd.DataFrame
        | Styler
        | np.ndarray
        | pl.DataFrame
        | list
        | list[list]
        | dict
        | str
        | None,
    ) -> list[str]:
        """
        Returns the headers of the dataframes based on the value provided. For values
        that do not have headers, an empty list is returned.
        """
        import pandas as pd
        from pandas.io.formats.style import Styler

        if value is None:
            return []
        if isinstance(value, pd.DataFrame):
            return list(value.columns)
        elif isinstance(value, Styler):
            return list(value.data.columns)  # type: ignore
        elif isinstance(value, str):
            return list(pd.read_csv(value).columns)
        elif _is_polars_available() and isinstance(value, _import_polars().DataFrame):
            return list(value.columns)
        elif isinstance(value, dict):
            return value.get("headers", [])
        elif isinstance(value, (list, np.ndarray)):
            return []
        return []

    @staticmethod
    def get_cell_data(
        value: pd.DataFrame
        | Styler
        | np.ndarray
        | pl.DataFrame
        | list
        | list[list]
        | dict
        | str
        | None,
    ) -> list[list[Any]]:
        """
        Gets the cell data (as a list of lists) from the value provided.
        """
        import pandas as pd
        from pandas.io.formats.style import Styler

        if isinstance(value, dict):
            return value.get("data", [[]])
        if isinstance(value, (str, pd.DataFrame)):
            if isinstance(value, str):
                value = pd.read_csv(value)  # type: ignore
            return value.to_dict(orient="split")["data"]
        elif isinstance(value, Styler):
            df: pd.DataFrame = value.data  # type: ignore
            hidden_columns = getattr(value, "hidden_columns", [])
            visible_cols = [
                i for i, _ in enumerate(df.columns) if i not in hidden_columns
            ]
            df = df.iloc[:, visible_cols]
            return df.to_dict(orient="split")["data"]
        elif _is_polars_available() and isinstance(value, _import_polars().DataFrame):
            df_dict = value.to_dict()  # type: ignore
            data = list(zip(*df_dict.values()))
            return data
        elif isinstance(value, (np.ndarray, list)):
            if isinstance(value, np.ndarray):
                value = value.tolist()
            if not isinstance(value, list):
                raise ValueError("output cannot be converted to list")
            if not isinstance(value[0], list):
                if isinstance(value[0], tuple):
                    return [list(v) for v in value]
                return [[v] for v in value]
            return value
        else:
            raise ValueError(
                f"Cannot process value of type {type(value)} in gr.Dataframe"
            )

    @staticmethod
    def get_metadata(
        value: pd.DataFrame
        | Styler
        | np.ndarray
        | pl.DataFrame
        | list
        | list[list]
        | dict
        | str
        | None,
    ) -> dict[str, list[list]] | None:
        """
        Gets the metadata from the value provided.
        """
        from pandas.io.formats.style import Styler

        if isinstance(value, Styler):
            return Dataframe.__extract_metadata(
                value, [int(c) for c in getattr(value, "hidden_columns", [])]
            )
        elif isinstance(value, dict):
            return value.get("metadata", None)
        return None

    def postprocess(
        self,
        value: pd.DataFrame
        | Styler
        | np.ndarray
        | pl.DataFrame
        | list
        | list[list]
        | dict
        | str
        | None,
    ) -> DataframeData:
        """
        Parameters:
            value: Expects data in any of these formats: `pandas.DataFrame`, `pandas.Styler`, `numpy.array`, `polars.DataFrame`, `list[list]`, `list`, or a `dict` with keys 'data' (and optionally 'headers'), or `str` path to a csv, which is rendered as the spreadsheet.
        Returns:
            the uploaded spreadsheet data as an object with `headers` and `data` keys and optional `metadata` key
        """
        import pandas as pd
        from pandas.io.formats.style import Styler

        if isinstance(value, Styler) and semantic_version.Version(
            pd.__version__
        ) < semantic_version.Version("1.5.0"):
            raise ValueError(
                "Styler objects are only supported in pandas version 1.5.0 or higher. Please try: `pip install --upgrade pandas` to use this feature."
            )
        if isinstance(value, Styler) and self.interactive:
            warnings.warn(
                "Cannot display Styler object in interactive mode. Will display as a regular pandas dataframe instead."
            )

        headers = self.get_headers(value) or self.headers
        data = [] if self.is_empty(value) else self.get_cell_data(value)
        if len(data) == 0:
            return DataframeData(headers=headers, data=[], metadata=None)
        if len(headers) > len(data[0]):
            headers = headers[: len(data[0])]
        elif len(headers) < len(data[0]):
            headers = [
                *headers,
                *[str(i) for i in range(len(headers) + 1, len(data[0]) + 1)],
            ]
        metadata = self.get_metadata(value)
        return DataframeData(
            headers=headers,
            data=data,
            metadata=metadata,  # type: ignore
        )

    @staticmethod
    def __extract_metadata(
        df: Styler, hidden_cols: list[int] | None = None
    ) -> dict[str, list[list]]:
        style_data = df._compute()._translate(None, None)  # type: ignore
        cell_styles = style_data.get("cellstyle", [])
        style_dict = {}
        for style in cell_styles:
            for selector in style.get("selectors", []):
                style_dict[selector] = "; ".join(
                    f"{prop}: {value}" for prop, value in style.get("props", [])
                )
        hidden_cols_set = set(hidden_cols) if hidden_cols is not None else set()
        metadata = {"display_value": [], "styling": []}

        for row in style_data["body"]:
            row_display = []
            row_styling = []
            # First, filter out the column with row numbers (if present).
            # Then, filter out the hidden columns so that column indices map correctly
            cells = [cell for cell in row if cell["type"] == "td"]
            cells = [
                cell
                for col_idx, cell in enumerate(cells)
                if col_idx not in hidden_cols_set
            ]
            for cell in cells:
                row_display.append(cell["display_value"])
                row_styling.append(style_dict.get(cell["id"], ""))
            metadata["display_value"].append(row_display)
            metadata["styling"].append(row_styling)
        return metadata

    @staticmethod
    def __process_counts(count, default=3) -> tuple[int, str]:
        if count is None:
            return (default, "dynamic")
        if isinstance(count, (int, float)):
            return (int(count), "dynamic")
        else:
            return count

    @staticmethod
    def __validate_headers(headers: list[str] | None, col_count: int):
        if headers is not None and len(headers) != col_count:
            raise ValueError(
                f"The length of the headers list must be equal to the col_count int.\n"
                f"The column count is set to {col_count} but `headers` has {len(headers)} items. "
                f"Check the values passed to `col_count` and `headers`."
            )

    def process_example(
        self,
        value: pd.DataFrame
        | Styler
        | np.ndarray
        | pl.DataFrame
        | list
        | list[list]
        | dict
        | str
        | None,
    ):
        import pandas as pd

        if value is None:
            return ""
        value_df_data = self.postprocess(value)
        value_df = pd.DataFrame(value_df_data.data, columns=value_df_data.headers)  # type: ignore
        return value_df.head(n=5).to_dict(orient="split")["data"]

    def example_payload(self) -> Any:
        return {"headers": ["a", "b"], "data": [["foo", "bar"]]}

    def example_value(self) -> Any:
        return {"headers": ["a", "b"], "data": [["foo", "bar"]]}


=== File: gradio/components/dataset.py ===
"""gr.Dataset() component."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import Any, Literal

from gradio_client.documentation import document

from gradio import processing_utils
from gradio.components.base import (
    Component,
    get_component_instance,
)
from gradio.events import Events
from gradio.i18n import I18nData


@document()
class Dataset(Component):
    """
    Creates a gallery or table to display data samples. This component is primarily designed for internal use to display examples.
    However, it can also be used directly to display a dataset and let users select examples.
    """

    EVENTS = [Events.click, Events.select]

    def __init__(
        self,
        *,
        label: str | I18nData | None = None,
        show_label: bool = True,
        components: Sequence[Component] | list[str] | None = None,
        component_props: list[dict[str, Any]] | None = None,
        samples: list[list[Any]] | None = None,
        headers: list[str] | None = None,
        type: Literal["values", "index", "tuple"] = "values",
        layout: Literal["gallery", "table"] | None = None,
        samples_per_page: int = 10,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        proxy_url: str | None = None,
        sample_labels: list[str] | None = None,
    ):
        """
        Parameters:
            label: the label for this component, appears above the component.
            show_label: If True, the label will be shown above the component.
            components: Which component types to show in this dataset widget, can be passed in as a list of string names or Components instances. The following components are supported in a Dataset: Audio, Checkbox, CheckboxGroup, ColorPicker, Dataframe, Dropdown, File, HTML, Image, Markdown, Model3D, Number, Radio, Slider, Textbox, TimeSeries, Video
            samples: a nested list of samples. Each sublist within the outer list represents a data sample, and each element within the sublist represents an value for each component
            headers: Column headers in the Dataset widget, should be the same len as components. If not provided, inferred from component labels
            type: "values" if clicking on a sample should pass the value of the sample, "index" if it should pass the index of the sample, or "tuple" if it should pass both the index and the value of the sample.
            layout: "gallery" if the dataset should be displayed as a gallery with each sample in a clickable card, or "table" if it should be displayed as a table with each sample in a row. By default, "gallery" is used if there is a single component, and "table" is used if there are more than one component. If there are more than one component, the layout can only be "table".
            samples_per_page: how many examples to show per page.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            proxy_url: The URL of the external Space used to load this component. Set automatically when using `gr.load()`. This should not be set manually.
            sample_labels: A list of labels for each sample. If provided, the length of this list should be the same as the number of samples, and these labels will be used in the UI instead of rendering the sample values.
        """
        super().__init__(
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )
        self.container = container
        self.scale = scale
        self.min_width = min_width
        self.layout = layout
        self.show_label = show_label
        self._components = [get_component_instance(c) for c in components or []]
        if component_props is None:
            self.component_props = [
                component.recover_kwargs(
                    component.get_config(),
                    ["value"],
                )
                for component in self._components
            ]
        else:
            self.component_props = component_props

        # Narrow type to Component
        if not all(isinstance(c, Component) for c in self._components):
            raise TypeError(
                "All components in a `Dataset` must be subclasses of `Component`"
            )
        self._components = [c for c in self._components if isinstance(c, Component)]
        self.proxy_url = proxy_url
        for component in self._components:
            component.proxy_url = proxy_url
        self.raw_samples = [[]] if samples is None else samples
        self.samples: list[list] = []
        for example in self.raw_samples:
            self.samples.append([])
            for component, ex in zip(self._components, example, strict=False):
                # If proxy_url is set, that means it is being loaded from an external Gradio app
                # which means that the example has already been processed.
                if self.proxy_url is None:
                    # We do not need to process examples if the Gradio app is being loaded from
                    # an external Space because the examples have already been processed. Also,
                    # the `as_example()` method has been renamed to `process_example()` but we
                    # use the previous name to be backwards-compatible with previously-created
                    # custom components
                    ex = component.as_example(ex)
                self.samples[-1].append(
                    processing_utils.move_files_to_cache(
                        ex, component, keep_in_cache=True
                    )
                )
        self.type = type
        self.label = label
        if headers is not None:
            self.headers = headers
        elif all(c.label is None for c in self._components):
            self.headers = []
        else:
            self.headers = [c.label or "" for c in self._components]
        self.samples_per_page = samples_per_page
        self.sample_labels = sample_labels

    def api_info(self) -> dict[str, str]:
        return {"type": "integer", "description": "index of selected example"}

    def get_config(self):
        config = super().get_config()

        config["components"] = []
        config["component_props"] = self.component_props
        config["sample_labels"] = self.sample_labels
        config["component_ids"] = []

        for component in self._components:
            config["components"].append(component.get_block_name())

            config["component_ids"].append(component._id)

        return config

    def preprocess(self, payload: int | None) -> int | list | tuple[int, list] | None:
        """
        Parameters:
            payload: the index of the selected example in the dataset
        Returns:
            Passes the selected sample either as a `list` of data corresponding to each input component (if `type` is "value") or as an `int` index (if `type` is "index"), or as a `tuple` of the index and the data (if `type` is "tuple").
        """
        if payload is None:
            return None
        if self.type == "index":
            return payload
        elif self.type == "values":
            return self.raw_samples[payload]
        elif self.type == "tuple":
            return payload, self.raw_samples[payload]

    def postprocess(self, value: int | list | None) -> int | None:
        """
        Parameters:
            value: Expects an `int` index or `list` of sample data. Returns the index of the sample in the dataset or `None` if the sample is not found.
        Returns:
            Returns the index of the sample in the dataset.
        """
        if value is None or isinstance(value, int):
            return value
        if isinstance(value, list):
            try:
                index = self.samples.index(value)
            except ValueError:
                index = None
                warnings.warn(
                    "The `Dataset` component does not support updating the dataset data by providing "
                    "a set of list values. Instead, you should return a new Dataset(samples=...) object."
                )
            return index

    def example_payload(self) -> Any:
        return 0

    def example_value(self) -> Any:
        return []


=== File: gradio/components/datetime.py ===
"""gr.DateTime() component."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Literal

import pytz
from gradio_client.documentation import document

from gradio.components.base import FormComponent
from gradio.events import Events
from gradio.i18n import I18nData


@document()
class DateTime(FormComponent):
    """
    Component to select a date and (optionally) a time.
    """

    EVENTS = [
        Events.change,
        Events.submit,
    ]

    def __init__(
        self,
        value: float | str | datetime | None = None,
        *,
        include_time: bool = True,
        type: Literal["timestamp", "datetime", "string"] = "timestamp",
        timezone: str | None = None,
        label: str | I18nData | None = None,
        show_label: bool | None = None,
        info: str | I18nData | None = None,
        every: float | None = None,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        interactive: bool | None = None,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            value: default value for datetime.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            show_label: if True, will display label.
            include_time: If True, the component will include time selection. If False, only date selection will be available.
            type: The type of the value. Can be "timestamp", "datetime", or "string". If "timestamp", the value will be a number representing the start and end date in seconds since epoch. If "datetime", the value will be a datetime object. If "string", the value will be the date entered by the user.
            timezone: The timezone to use for timestamps, such as "US/Pacific" or "Europe/Paris". If None, the timezone will be the local timezone.
            every: If `value` is a callable, run the function 'every' number of seconds while the client connection is open. Has no effect otherwise. The event can be accessed (e.g. to cancel it) via this component's .load_event attribute.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.type = type
        self.include_time = include_time
        self.interactive = interactive
        self.time_format = "%Y-%m-%d %H:%M:%S" if include_time else "%Y-%m-%d"
        self.timezone = timezone
        self._value_description = (
            "a datetime object"
            if self.type == "datetime"
            else "a unix timestamp"
            if self.type == "timestamp"
            else "a %Y-%m-%d %H:%M:%S formatted string"
            if include_time
            else "a %Y-%m-%d formatted string"
        )
        super().__init__(
            every=every,
            scale=scale,
            min_width=min_width,
            visible=visible,
            label=label,
            show_label=show_label,
            info=info,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def preprocess(self, payload: str | None) -> str | float | datetime | None:
        """
        Parameters:
            payload: the text entered in the textarea.
        Returns:
            Passes text value as a {str} into the function.
        """
        if payload is None or payload == "":
            return None
        if self.type == "string" and "now" not in payload:
            return payload
        datetime = self.get_datetime_from_str(payload)
        if self.type == "string":
            return datetime.strftime(self.time_format)
        if self.type == "datetime":
            return datetime
        elif self.type == "timestamp":
            return datetime.timestamp()

    def postprocess(self, value: float | datetime | str | None) -> str | None:
        """
        Parameters:
            value: Expects a tuple pair of datetimes.
        Returns:
            A tuple pair of timestamps.
        """
        if value is None:
            return None

        if isinstance(value, datetime):
            return datetime.strftime(value, self.time_format)
        elif isinstance(value, str):
            return value
        else:
            return datetime.fromtimestamp(
                value, tz=pytz.timezone(self.timezone) if self.timezone else None
            ).strftime(self.time_format)

    def api_info(self) -> dict[str, Any]:
        return {
            "type": "string",
            "description": f"Formatted as YYYY-MM-DD{' HH:MM:SS' if self.include_time else ''}",
        }

    def example_payload(self) -> str:
        return "2020-10-01 05:20:15"

    def example_value(self) -> str:
        return "2020-10-01 05:20:15"

    def get_datetime_from_str(self, date: str) -> datetime:
        now_regex = r"^(?:\s*now\s*(?:-\s*(\d+)\s*([dmhs]))?)?\s*$"

        if "now" in date:
            match = re.match(now_regex, date)
            if match:
                num = int(match.group(1) or 0)
                unit = match.group(2) or "s"
                if unit == "d":
                    delta = timedelta(days=num)
                elif unit == "h":
                    delta = timedelta(hours=num)
                elif unit == "m":
                    delta = timedelta(minutes=num)
                else:
                    delta = timedelta(seconds=num)
                return datetime.now() - delta
            else:
                raise ValueError("Invalid 'now' time format")
        else:
            dt = datetime.strptime(date, self.time_format)
            if self.timezone:
                dt = pytz.timezone(self.timezone).localize(dt)
            return dt


=== File: gradio/components/deep_link_button.py ===
"""Predefined button to copy a shareable link to the current Gradio Space."""

from __future__ import annotations

import textwrap
import time
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from gradio_client.documentation import document

from gradio import utils
from gradio.components.base import Component
from gradio.components.button import Button
from gradio.context import get_blocks_context

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class DeepLinkButton(Button):
    """
    Creates a button that copies a shareable link to the current Gradio Space.
    The link includes the current session hash as a query parameter.
    """

    is_template = True
    n_created = 0

    def __init__(
        self,
        value: str = "Share via Link",
        copied_value: str = "Link Copied!",
        *,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary"] = "secondary",
        size: Literal["sm", "md", "lg"] = "lg",
        icon: str | Path | None = utils.get_icon_path("link.svg"),
        link: str | None = None,
        visible: bool = True,
        interactive: bool = True,
        elem_id: str | None = None,  # noqa: ARG002
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        scale: int | None = None,
        min_width: int | None = None,
        every: Timer | float | None = None,
    ):
        """
        Parameters:
            value: The text to display on the button.
            copied_value: The text to display on the button after the link has been copied.
        """
        self.copied_value = copied_value
        super().__init__(
            value,
            inputs=inputs,
            variant=variant,
            size=size,
            icon=icon,
            link=link,
            visible=visible,
            interactive=interactive,
            elem_id=f"gradio-share-link-button-{self.n_created}",
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            scale=scale,
            min_width=min_width,
            every=every,
        )
        self.elem_id: str
        self.n_created += 1
        if get_blocks_context():
            self.activate()

    def activate(self):
        """Attach the click event to copy the share link."""
        _js = self.get_share_link(self.value, self.copied_value)
        # Need to separate events because can't run .then in a pure js
        # function.
        self.click(fn=None, inputs=[], outputs=[self], js=_js)
        self.click(
            fn=lambda: time.sleep(1) or self.value,
            inputs=[],
            outputs=[self],
            queue=False,
            show_api=False,
        )

    def get_share_link(
        self, value: str = "Share via Link", copied_value: str = "Link Copied!"
    ):
        delete_sign_line = (
            "currentUrl.searchParams.delete('__sign');" if utils.get_space() else ""
        )
        return textwrap.dedent(
            f"""
        () => {{
            const sessionHash = window.__gradio_session_hash__;
            fetch(`/gradio_api/deep_link?session_hash=${{sessionHash}}`)
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error('Network response was not ok');
                    }}
                    return response.text();
                }})
                .then(data => {{
                    const currentUrl = new URL(window.location.href);
                    const cleanData = data.replace(/^"|"$/g, '');
                    if (cleanData) {{
                        currentUrl.searchParams.set('deep_link', cleanData);
                    }}
                    {delete_sign_line}
                    navigator.clipboard.writeText(currentUrl.toString());
                }})
                .catch(error => {{
                    console.error('Error fetching deep link:', error);
                    return "Error";
                }});

            return "BUTTON_COPIED_VALUE";
        }}
        """.replace("BUTTON_DEFAULT_VALUE", value).replace(
                "BUTTON_COPIED_VALUE", copied_value
            )
        ).replace("ID", self.elem_id)


=== File: gradio/components/download_button.py ===
"""gr.DownloadButton() component."""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from gradio_client import handle_file
from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import FileData
from gradio.events import Events

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class DownloadButton(Component):
    """
    Creates a button, that when clicked, allows a user to download a single file of arbitrary type.

    Demos: upload_and_download
    """

    EVENTS = [Events.click]

    def __init__(
        self,
        label: str = "Download",
        value: str | Path | Callable | None = None,
        *,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary", "stop"] = "secondary",
        visible: bool = True,
        size: Literal["sm", "md", "lg"] = "lg",
        icon: str | None = None,
        scale: int | None = None,
        min_width: int | None = None,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            label: Text to display on the button. Defaults to "Download".
            value: A str or pathlib.Path filepath or URL to download, or a Callable that returns a str or pathlib.Path filepath or URL to download.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            variant: 'primary' for main call-to-action, 'secondary' for a more subdued style, 'stop' for a stop button.
            visible: If False, component will be hidden.
            size: size of the button. Can be "sm", "md", or "lg".
            icon: URL or path to the icon file to display within the button. If None, no icon will be displayed.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: If False, the UploadButton will be in a disabled state.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.data_model = FileData
        self.size = size
        self.label = label
        self.variant = variant
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
        )
        self.icon = self.serve_static_file(icon)

    def preprocess(self, payload: FileData | None) -> str | None:
        """
        Parameters:
            payload: File information as a FileData object,
        Returns:
            (Rarely used) passes the file as a `str` into the function.
        """
        if payload is None:
            return None
        file_name = payload.path
        file = tempfile.NamedTemporaryFile(delete=False, dir=self.GRADIO_CACHE)
        file.name = file_name
        return file_name

    def postprocess(self, value: str | Path | None) -> FileData | None:
        """
        Parameters:
            value: Expects a `str` or `pathlib.Path` filepath
        Returns:
            File information as a FileData object
        """
        if value is None:
            return None
        return FileData(path=str(value), orig_name=Path(value).name)

    def example_payload(self) -> dict:
        return handle_file(
            "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
        )

    def example_value(self) -> str:
        return "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"

    @property
    def skip_api(self):
        return False


=== File: gradio/components/dropdown.py ===
"""gr.Dropdown() component."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component, FormComponent
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


class DefaultValue:
    # This sentinel is used to indicate that if the value is not explicitly set,
    # the first choice should be selected in the dropdown if multiselect is False,
    # and an empty list should be selected if multiselect is True.
    pass


DEFAULT_VALUE = DefaultValue()


@document()
class Dropdown(FormComponent):
    """
    Creates a dropdown of choices from which a single entry or multiple entries can be selected (as an input component) or displayed (as an output component).

    Demos: sentence_builder
    """

    EVENTS = [
        Events.change,
        Events.input,
        Events.select,
        Events.focus,
        Events.blur,
        Events.key_up,
    ]

    def __init__(
        self,
        choices: Sequence[str | int | float | tuple[str, str | int | float]]
        | None = None,
        *,
        value: str
        | int
        | float
        | Sequence[str | int | float]
        | Callable
        | DefaultValue
        | None = DEFAULT_VALUE,
        type: Literal["value", "index"] = "value",
        multiselect: bool | None = None,
        allow_custom_value: bool = False,
        max_choices: int | None = None,
        filterable: bool = True,
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            choices: a list of string or numeric options to choose from. An option can also be a tuple of the form (name, value), where name is the displayed name of the dropdown choice and value is the value to be passed to the function, or returned by the function.
            value: the value selected in dropdown. If `multiselect` is true, this should be list, otherwise a single string or number from among `choices`. By default, the first choice in `choices` is initally selected. If set explicitly to None, no value is initally selected. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            type: type of value to be returned by component. "value" returns the string of the choice selected, "index" returns the index of the choice selected.
            multiselect: if True, multiple choices can be selected.
            allow_custom_value: if True, allows user to enter a custom value that is not in the list of choices.
            max_choices: maximum number of choices that can be selected. If None, no limit is enforced.
            filterable: if True, user will be able to type into the dropdown and filter the choices by typing. Can only be set to False if `allow_custom_value` is False.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: if True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, choices in this dropdown will be selectable; if False, selection will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: if False, component will be hidden.
            elem_id: an optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: an optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: if False, component will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
        """
        self.choices = (
            # Although we expect choices to be a list of tuples, it can be a list of lists if the Gradio app
            # is loaded with gr.load() since Python tuples are converted to lists in JSON.
            [tuple(c) if isinstance(c, (tuple, list)) else (str(c), c) for c in choices]
            if choices
            else []
        )
        valid_types = ["value", "index"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        self.multiselect = multiselect

        if value == DEFAULT_VALUE:
            if multiselect:
                value = []
            elif self.choices:
                value = self.choices[0][1]
            else:
                value = None
        if multiselect and isinstance(value, str):
            value = [value]

        if not multiselect and max_choices is not None:
            warnings.warn(
                "The `max_choices` parameter is ignored when `multiselect` is False."
            )
        if not filterable and allow_custom_value:
            filterable = True
            warnings.warn(
                "The `filterable` parameter cannot be set to False when `allow_custom_value` is True. Setting `filterable` to True."
            )
        self.max_choices = max_choices
        self.allow_custom_value = allow_custom_value
        self.filterable = filterable
        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = f"one{' or more' if multiselect else ''} of {[c[1] if isinstance(c, tuple) else c for c in self.choices]}"

    def api_info(self) -> dict[str, Any]:
        if self.multiselect:
            json_type = {
                "type": "array",
                "items": {"type": "string", "enum": [c[1] for c in self.choices]},
            }
        else:
            json_type = {
                "type": "string",
                "enum": [c[1] for c in self.choices],
            }
        return json_type

    def example_payload(self) -> Any:
        if self.multiselect:
            return [self.choices[0][1]] if self.choices else []
        else:
            return self.choices[0][1] if self.choices else None

    def example_value(self) -> Any:
        if self.multiselect:
            return [self.choices[0][1]] if self.choices else []
        else:
            return self.choices[0][1] if self.choices else None

    def preprocess(
        self, payload: str | int | float | list[str | int | float] | None
    ) -> str | int | float | list[str | int | float] | list[int | None] | None:
        """
        Parameters:
            payload: the value of the selected dropdown choice(s)
        Returns:
            Passes the value of the selected dropdown choice as a `str | int | float` or its index as an `int` into the function, depending on `type`. Or, if `multiselect` is True, passes the values of the selected dropdown choices as a list of corresponding values/indices instead.
        """
        if payload is None:
            return None

        choice_values = [value for _, value in self.choices]
        if not self.allow_custom_value:
            if isinstance(payload, list):
                for value in payload:
                    if value not in choice_values:
                        raise Error(
                            f"Value: {value!r} (type: {type(value)}) is not in the list of choices: {choice_values}"
                        )
            elif payload not in choice_values:
                raise Error(
                    f"Value: {payload} is not in the list of choices: {choice_values}"
                )

        if self.type == "value":
            return payload
        elif self.type == "index":
            if isinstance(payload, list):
                return [
                    choice_values.index(choice) if choice in choice_values else None
                    for choice in payload
                ]
            else:
                return (
                    choice_values.index(payload) if payload in choice_values else None
                )
        else:
            raise ValueError(
                f"Unknown type: {self.type}. Please choose from: 'value', 'index'."
            )

    def _warn_if_invalid_choice(self, value):
        if self.allow_custom_value or value in [value for _, value in self.choices]:
            return
        warnings.warn(
            f"The value passed into gr.Dropdown() is not in the list of choices. Please update the list of choices to include: {value} or set allow_custom_value=True."
        )

    def postprocess(
        self, value: str | int | float | list[str | int | float] | None
    ) -> str | int | float | list[str | int | float] | None:
        """
        Parameters:
            value: Expects a `str | int | float` corresponding to the value of the dropdown entry to be selected. Or, if `multiselect` is True, expects a `list` of values corresponding to the selected dropdown entries.
        Returns:
            Returns the values of the selected dropdown entry or entries.
        """
        if value is None:
            return None
        if self.multiselect:
            if not isinstance(value, list):
                value = [value]
            [self._warn_if_invalid_choice(_y) for _y in value]
        else:
            self._warn_if_invalid_choice(value)
        return value


=== File: gradio/components/duplicate_button.py ===
"""gr.DuplicateButton() component"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from gradio_client.documentation import document

from gradio.components import Button, Component
from gradio.context import get_blocks_context
from gradio.utils import get_space

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class DuplicateButton(Button):
    """
    Button that triggers a Spaces Duplication, when the demo is on Hugging Face Spaces. Does nothing locally.
    """

    is_template = True

    def __init__(
        self,
        value: str = "Duplicate Space",
        *,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary", "stop", "huggingface"] = "huggingface",
        size: Literal["sm", "md", "lg"] = "sm",
        icon: str | Path | None = None,
        link: str | None = None,
        visible: bool = True,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        scale: int | None = 0,
        min_width: int | None = None,
        _activate: bool = True,
    ):
        """
        Parameters:
        Parameters:
            value: default text for the button to display. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            every: continuously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            variant: sets the background and text color of the button. Use 'primary' for main call-to-action buttons, 'secondary' for a more subdued style, 'stop' for a stop button, 'huggingface' for a black background with white text, consistent with Hugging Face's button styles.
            size: size of the button. Can be "sm", "md", or "lg".
            icon: URL or path to the icon file to display within the button. If None, no icon will be displayed.
            link: URL to open when the button is clicked. If None, no link will be used.
            visible: if False, component will be hidden.
            interactive: if False, the Button will be in a disabled state.
            elem_id: an optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: an optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: if False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
        """
        super().__init__(
            value=value,
            every=every,
            inputs=inputs,
            variant=variant,
            size=size,
            icon=icon,
            link=link,
            visible=visible,
            interactive=interactive,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            scale=scale,
            min_width=min_width,
        )
        if _activate and get_blocks_context():
            self.activate()

    def activate(self):
        space_name = get_space()
        if space_name is not None:
            self.click(
                fn=None,
                js=f"() => {{ window.open(`https://huggingface.co/spaces/{space_name}?duplicate=true`, '_blank') }}",
            )


=== File: gradio/components/fallback.py ===
from gradio.components.base import Component


class Fallback(Component):
    def preprocess(self, payload):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            payload: the data to be preprocessed, sent from the frontend
        Returns:
            the data after preprocessing, sent to the user's function in the backend
        """
        return payload

    def postprocess(self, value):
        """
        This docstring is used to generate the docs for this custom component.
        Parameters:
            payload: the data to be postprocessed, sent from the user's function in the backend
        Returns:
            the data after postprocessing, sent to the frontend
        """
        return value

    def example_payload(self):
        return {"foo": "bar"}

    def example_value(self):
        return {"foo": "bar"}

    def api_info(self):
        return {"type": {}, "description": "any valid json"}


=== File: gradio/components/file.py ===
"""gr.File() component"""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import gradio_client.utils as client_utils
from gradio_client import handle_file
from gradio_client.documentation import document

from gradio import processing_utils
from gradio.components.base import Component
from gradio.data_classes import FileData, ListFiles
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData
from gradio.utils import NamedString

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class File(Component):
    """
    Creates a file component that allows uploading one or more generic files (when used as an input) or displaying generic files or URLs for download (as output).

        Demo: zip_files, zip_to_json
    """

    EVENTS = [
        Events.change,
        Events.select,
        Events.clear,
        Events.upload,
        Events.delete,
        Events.download,
    ]

    def __init__(
        self,
        value: str | list[str] | Callable | None = None,
        *,
        file_count: Literal["single", "multiple", "directory"] = "single",
        file_types: list[str] | None = None,
        type: Literal["filepath", "binary"] = "filepath",
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        height: int | str | float | None = None,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        allow_reordering: bool = False,
    ):
        """
        Parameters:
            value: Default file(s) to display, given as a str file path or URL, or a list of str file paths / URLs. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            file_count: if single, allows user to upload one file. If "multiple", user uploads multiple files. If "directory", user uploads all files in selected directory. Return type will be list for each file in case of "multiple" or "directory".
            file_types: List of file extensions or types of files to be uploaded (e.g. ['image', '.json', '.mp4']). "file" allows any file to be uploaded, "image" allows only image files to be uploaded, "audio" allows only audio files to be uploaded, "video" allows only video files to be uploaded, "text" allows only text files to be uploaded.
            type: Type of value to be returned by component. "file" returns a temporary file object with the same base name as the uploaded file, whose full path can be retrieved by file_obj.name, "binary" returns an bytes object.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            height: The default height of the file component when no files have been uploaded, or the maximum height of the file component when files are present. Specified in pixels if a number is passed, or in CSS units if a string is passed. If more files are uploaded than can fit in the height, a scrollbar will appear.
            interactive: if True, will allow users to upload a file; if False, can only be used to display files. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            allow_reordering: if True, will allow users to reorder uploaded files by dragging and dropping.
        """
        file_count_valid_types = ["single", "multiple", "directory"]
        self.file_count = file_count

        if self.file_count not in file_count_valid_types:
            raise ValueError(
                f"Parameter file_count must be one of them: {file_count_valid_types}"
            )
        elif self.file_count in ["multiple", "directory"]:
            self.data_model = ListFiles
        else:
            self.data_model = FileData
        self.file_types = file_types
        if file_types is not None and not isinstance(file_types, list):
            raise ValueError(
                f"Parameter file_types must be a list. Received {file_types.__class__.__name__}"
            )
        valid_types = [
            "filepath",
            "binary",
        ]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self.type = type
        self.height = height
        self.allow_reordering = allow_reordering
        self._value_description = (
            "a string filepath"
            if self.file_count == "single"
            else "a list of string filepaths"
        )

    def _process_single_file(self, f: FileData) -> NamedString | bytes:
        file_name = f.path
        if self.type == "filepath":
            if self.file_types and not client_utils.is_valid_file(
                file_name, self.file_types
            ):
                raise Error(
                    f"Invalid file type. Please upload a file that is one of these formats: {self.file_types}"
                )
            file = tempfile.NamedTemporaryFile(delete=False, dir=self.GRADIO_CACHE)
            file.name = file_name
            return NamedString(file_name)
        elif self.type == "binary":
            with open(file_name, "rb") as file_data:
                return file_data.read()
        else:
            raise ValueError(
                "Unknown type: "
                + str(type)
                + ". Please choose from: 'filepath', 'binary'."
            )

    def preprocess(
        self, payload: ListFiles | FileData | None
    ) -> bytes | str | list[bytes] | list[str] | None:
        """
        Parameters:
            payload: File information as a FileData object, or a list of FileData objects.
        Returns:
            Passes the file as a `str` or `bytes` object, or a list of `str` or list of `bytes` objects, depending on `type` and `file_count`.
        """
        if payload is None:
            return None

        if self.file_count == "single":
            if isinstance(payload, ListFiles):
                return self._process_single_file(payload[0])
            return self._process_single_file(payload)
        if isinstance(payload, ListFiles):
            return [self._process_single_file(f) for f in payload]  # type: ignore
        return [self._process_single_file(payload)]  # type: ignore

    def _download_files(self, value: str | list[str]) -> str | list[str]:
        downloaded_files = []
        if isinstance(value, list):
            for file in value:
                if client_utils.is_http_url_like(file):
                    downloaded_file = processing_utils.save_url_to_cache(
                        file, self.GRADIO_CACHE
                    )
                    downloaded_files.append(downloaded_file)
                else:
                    downloaded_files.append(file)
            return downloaded_files
        if client_utils.is_http_url_like(value):
            downloaded_file = processing_utils.save_url_to_cache(
                value, self.GRADIO_CACHE
            )
            return downloaded_file
        else:
            return value

    def postprocess(self, value: str | list[str] | None) -> ListFiles | FileData | None:
        """
        Parameters:
            value: Expects a `str` filepath or URL, or a `list[str]` of filepaths/URLs.
        Returns:
            File information as a FileData object, or a list of FileData objects.
        """
        if value is None:
            return None
        value = self._download_files(value)
        if isinstance(value, list):
            return ListFiles(
                root=[
                    FileData(
                        path=file,
                        orig_name=Path(file).name,
                        size=Path(file).stat().st_size,
                    )
                    for file in value
                ]
            )
        else:
            return FileData(
                path=value,
                orig_name=Path(value).name,
                size=Path(value).stat().st_size,
            )

    def process_example(self, value: str | list | None) -> str:
        if value is None:
            return ""
        elif isinstance(value, list):
            return ", ".join([Path(file).name for file in value])
        else:
            return Path(value).name

    def example_payload(self) -> Any:
        if self.file_count == "single":
            return handle_file(
                "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
            )
        else:
            return [
                handle_file(
                    "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
                )
            ]

    def example_value(self) -> Any:
        if self.file_count == "single":
            return "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
        else:
            return [
                "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
            ]


=== File: gradio/components/file_explorer.py ===
"""gr.FileExplorer() component"""

from __future__ import annotations

import fnmatch
import os
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component, server
from gradio.data_classes import DeveloperPath, GradioRootModel, UserProvidedPath
from gradio.i18n import I18nData
from gradio.utils import safe_join

if TYPE_CHECKING:
    from gradio.components import Timer


class FileExplorerData(GradioRootModel):
    # The outer list is the list of files selected, and the inner list
    # is the path to the file as a list, split by the os.sep.
    root: list[list[str]]


@document()
class FileExplorer(Component):
    """
    Creates a file explorer component that allows users to browse files on the machine hosting the Gradio app. As an input component,
    it also allows users to select files to be used as input to a function, while as an output component, it displays selected files.
    """

    EVENTS = ["change"]
    data_model = FileExplorerData

    def __init__(
        self,
        glob: str = "**/*",
        *,
        value: str | list[str] | Callable | None = None,
        file_count: Literal["single", "multiple"] = "multiple",
        root_dir: str | Path = ".",
        ignore_glob: str | None = None,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        height: int | str | None = None,
        max_height: int | str | None = 500,
        min_height: int | str | None = None,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            glob: The glob-style pattern used to select which files to display, e.g. "*" to match all files, "*.png" to match all .png files, "**/*.txt" to match any .txt file in any subdirectory, etc. The default value matches all files and folders recursively. See the Python glob documentation at https://docs.python.org/3/library/glob.html for more information.
            value: The file (or list of files, depending on the `file_count` parameter) to show as "selected" when the component is first loaded. If a callable is provided, it will be called when the app loads to set the initial value of the component. If not provided, no files are shown as selected.
            file_count: Whether to allow single or multiple files to be selected. If "single", the component will return a single absolute file path as a string. If "multiple", the component will return a list of absolute file paths as a list of strings.
            root_dir: Path to root directory to select files from. If not provided, defaults to current working directory.
            ignore_glob: The glob-style, case-sensitive pattern that will be used to exclude files from the list. For example, "*.py" will exclude all .py files from the list. See the Python glob documentation at https://docs.python.org/3/library/glob.html for more information.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            height: The maximum height of the file component, specified in pixels if a number is passed, or in CSS units if a string is passed. If more files are uploaded than can fit in the height, a scrollbar will appear.
            interactive: if True, will allow users to select file(s); if False, will only display files. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.root_dir = DeveloperPath(os.path.abspath(root_dir))
        self.glob = glob
        self.ignore_glob = ignore_glob
        valid_file_count = ["single", "multiple"]
        if file_count not in valid_file_count:
            raise ValueError(
                f"Invalid value for parameter `file_count`: {file_count}. Please choose from one of: {valid_file_count}"
            )
        self.file_count = file_count
        self.height = height
        self.max_height = max_height
        self.min_height = min_height

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def example_payload(self) -> Any:
        return [["gradio", "app.py"]]

    def example_value(self) -> Any:
        return os.sep.join(["gradio", "app.py"])

    def preprocess(self, payload: FileExplorerData | None) -> list[str] | str | None:
        """
        Parameters:
            payload: List of selected files as a FileExplorerData object.
        Returns:
            Passes the selected file or directory as a `str` path (relative to `root`) or `list[str}` depending on `file_count`
        """
        if payload is None:
            return None

        if self.file_count == "single":
            if len(payload.root) > 1:
                raise ValueError(
                    f"Expected only one file, but {len(payload.root)} were selected."
                )
            elif len(payload.root) == 0:
                return None
            else:
                return os.path.normpath(os.path.join(self.root_dir, *payload.root[0]))
        files = []
        for file in payload.root:
            file_ = os.path.normpath(os.path.join(self.root_dir, *file))
            files.append(file_)
        return files

    def _strip_root(self, path: str) -> str:
        if path.startswith(self.root_dir):
            return path[len(self.root_dir) + 1 :]
        return path

    def postprocess(self, value: str | list[str] | None) -> FileExplorerData | None:
        """
        Parameters:
            value: Expects function to return a `str` path to a file, or `list[str]` consisting of paths to files.
        Returns:
            A FileExplorerData object containing the selected files as a list of strings.
        """
        if value is None:
            return None

        files = [value] if isinstance(value, str) else value
        root = []
        for file in files:
            root.append(self._strip_root(file).split(os.path.sep))

        return FileExplorerData(root=root)

    @server
    def ls(self, subdirectory: list[str] | None = None) -> list[dict[str, str]] | None:
        """
        Returns:
            a list of dictionaries, where each dictionary represents a file or subdirectory in the given subdirectory
        """
        if subdirectory is None:
            subdirectory = []

        full_subdir_path = self._safe_join(subdirectory)

        try:
            subdir_items = sorted(os.listdir(full_subdir_path))
        except FileNotFoundError:
            return []

        files, folders = [], []
        for item in subdir_items:
            full_path = os.path.join(full_subdir_path, item)
            is_file = not os.path.isdir(full_path)
            valid_by_glob = fnmatch.fnmatch(full_path, self.glob)
            if is_file and not valid_by_glob:
                continue
            if self.ignore_glob and fnmatch.fnmatch(full_path, self.ignore_glob):
                continue
            target = files if is_file else folders
            target.append(
                {
                    "name": item,
                    "type": "file" if is_file else "folder",
                    "valid": valid_by_glob,
                }
            )

        return folders + files

    def _safe_join(self, folders: list[str]) -> str:
        if not folders or len(folders) == 0:
            return self.root_dir
        combined_path = UserProvidedPath(os.path.join(*folders))
        if os.name == "nt":
            combined_path = combined_path.replace("\\", "/")
        x = safe_join(self.root_dir, combined_path)
        return x


=== File: gradio/components/gallery.py ===
"""gr.Gallery() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Union,
)
from urllib.parse import quote, urlparse

import numpy as np
import PIL.Image
from gradio_client import handle_file
from gradio_client import utils as client_utils
from gradio_client.documentation import document
from gradio_client.utils import is_http_url_like

from gradio import image_utils, processing_utils, utils, wasm_utils
from gradio.components.base import Component
from gradio.data_classes import FileData, GradioModel, GradioRootModel, ImageData
from gradio.events import EventListener, Events
from gradio.exceptions import Error
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer

GalleryMediaType = Union[np.ndarray, PIL.Image.Image, Path, str]
CaptionedGalleryMediaType = tuple[GalleryMediaType, str]


class GalleryImage(GradioModel):
    image: ImageData
    caption: Optional[str] = None


class GalleryVideo(GradioModel):
    video: FileData
    caption: Optional[str] = None


class GalleryData(GradioRootModel):
    root: list[Union[GalleryImage, GalleryVideo]]


@document()
class Gallery(Component):
    """
    Creates a gallery component that allows displaying a grid of images or videos, and optionally captions. If used as an input, the user can upload images or videos to the gallery.
    If used as an output, the user can click on individual images or videos to view them at a higher resolution.

    Demos: fake_gan
    """

    EVENTS = [
        Events.select,
        Events.upload,
        Events.change,
        EventListener(
            "preview_close",
            doc="This event is triggered when the Gallery preview is closed by the user",
        ),
        EventListener(
            "preview_open",
            doc="This event is triggered when the Gallery preview is opened by the user",
        ),
    ]

    data_model = GalleryData

    def __init__(
        self,
        value: (
            Sequence[np.ndarray | PIL.Image.Image | str | Path | tuple]
            | Callable
            | None
        ) = None,
        *,
        format: str = "webp",
        file_types: list[str] | None = None,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        columns: int | None = 2,
        rows: int | None = None,
        height: int | float | str | None = None,
        allow_preview: bool = True,
        preview: bool | None = None,
        selected_index: int | None = None,
        object_fit: (
            Literal["contain", "cover", "fill", "none", "scale-down"] | None
        ) = None,
        show_share_button: bool | None = None,
        show_download_button: bool | None = True,
        interactive: bool | None = None,
        type: Literal["numpy", "pil", "filepath"] = "filepath",
        show_fullscreen_button: bool = True,
    ):
        """
        Parameters:
            value: List of images or videos to display in the gallery by default. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            format: Format to save images before they are returned to the frontend, such as 'jpeg' or 'png'. This parameter only applies to images that are returned from the prediction function as numpy arrays or PIL Images. The format should be supported by the PIL library.
            file_types: List of file extensions or types of files to be uploaded (e.g. ['image', '.mp4']), when this is used as an input component. "image" allows only image files to be uploaded, "video" allows only video files to be uploaded, ".mp4" allows only mp4 files to be uploaded, etc. If None, any image and video files types are allowed.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            columns: Represents the number of images that should be shown in one row.
            rows: Represents the number of rows in the image grid.
            height: The height of the gallery component, specified in pixels if a number is passed, or in CSS units if a string is passed. If more images are displayed than can fit in the height, a scrollbar will appear.
            allow_preview: If True, images in the gallery will be enlarged when they are clicked. Default is True.
            preview: If True, Gallery will start in preview mode, which shows all of the images as thumbnails and allows the user to click on them to view them in full size. Only works if allow_preview is True.
            selected_index: The index of the image that should be initially selected. If None, no image will be selected at start. If provided, will set Gallery to preview mode unless allow_preview is set to False.
            object_fit: CSS object-fit property for the thumbnail images in the gallery. Can be "contain", "cover", "fill", "none", or "scale-down".
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            show_download_button: If True, will show a download button in the corner of the selected image. If False, the icon does not appear. Default is True.
            interactive: If True, the gallery will be interactive, allowing the user to upload images. If False, the gallery will be static. Default is True.
            type: The format the image is converted to before being passed into the prediction function. "numpy" converts the image to a numpy array with shape (height, width, 3) and values from 0 to 255, "pil" converts the image to a PIL image object, "filepath" passes a str path to a temporary file containing the image. If the image is SVG, the `type` is ignored and the filepath of the SVG is returned.
            show_fullscreen_button: If True, will show a fullscreen icon in the corner of the component that allows user to view the gallery in fullscreen mode. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
        """
        self.format = format
        self.columns = columns
        self.rows = rows
        self.height = height
        self.preview = preview
        self.object_fit = object_fit
        self.allow_preview = allow_preview
        self.show_download_button = (
            (utils.get_space() is not None)
            if show_download_button is None
            else show_download_button
        )
        self.selected_index = selected_index
        self.type = type
        self.show_fullscreen_button = show_fullscreen_button
        self.file_types = file_types

        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            interactive=interactive,
        )
        self._value_description = f"a list of {'string filepaths' if type == 'filepath' else 'numpy arrays' if type == 'numpy' else 'PIL images'}"

    def preprocess(
        self, payload: GalleryData | None
    ) -> (
        list[tuple[str, str | None]]
        | list[tuple[PIL.Image.Image, str | None]]
        | list[tuple[np.ndarray, str | None]]
        | None
    ):
        """
        Parameters:
            payload: a list of images or videos, or list of (media, caption) tuples
        Returns:
            Passes the list of images or videos as a list of (media, caption) tuples, or a list of (media, None) tuples if no captions are provided (which is usually the case). Images can be a `str` file path, a `numpy` array, or a `PIL.Image` object depending on `type`.  Videos are always `str` file path.
        """
        if payload is None or not payload.root:
            return None
        data = []
        for gallery_element in payload.root:
            if isinstance(gallery_element, GalleryVideo):
                file_path = gallery_element.video.path
            else:
                file_path = gallery_element.image.path or ""
            if self.file_types and not client_utils.is_valid_file(
                file_path, self.file_types
            ):
                raise Error(
                    f"Invalid file type. Please upload a file that is one of these formats: {self.file_types}"
                )
            else:
                media = (
                    gallery_element.video.path
                    if (type(gallery_element) is GalleryVideo)
                    else self.convert_to_type(gallery_element.image.path, self.type)  # type: ignore
                )
                data.append((media, gallery_element.caption))
        return data

    def postprocess(
        self,
        value: list[GalleryMediaType | CaptionedGalleryMediaType] | None,
    ) -> GalleryData:
        """
        Parameters:
            value: Expects the function to return a `list` of images or videos, or `list` of (media, `str` caption) tuples. Each image can be a `str` file path, a `numpy` array, or a `PIL.Image` object. Each video can be a `str` file path.
        Returns:
            a list of images or videos, or list of (media, caption) tuples
        """
        if value is None:
            return GalleryData(root=[])
        if isinstance(value, str):
            raise ValueError(
                "The `value` passed into `gr.Gallery` must be a list of images or videos, or list of (media, caption) tuples."
            )
        output = []

        def _save(img):
            url = None
            caption = None
            orig_name = None
            mime_type = None
            if isinstance(img, (tuple, list)):
                img, caption = img
            if isinstance(img, np.ndarray):
                file = processing_utils.save_img_array_to_cache(
                    img, cache_dir=self.GRADIO_CACHE, format=self.format
                )
                file_path = str(utils.abspath(file))
            elif isinstance(img, PIL.Image.Image):
                file = processing_utils.save_pil_to_cache(
                    img, cache_dir=self.GRADIO_CACHE, format=self.format
                )
                file_path = str(utils.abspath(file))
            elif isinstance(img, str):
                mime_type = client_utils.get_mimetype(img)
                if img.lower().endswith(".svg"):
                    svg_content = image_utils.extract_svg_content(img)
                    orig_name = Path(img).name
                    url = f"data:image/svg+xml,{quote(svg_content)}"
                    file_path = None
                elif is_http_url_like(img):
                    url = img
                    orig_name = Path(urlparse(img).path).name
                    file_path = img
                else:
                    url = None
                    orig_name = Path(img).name
                    file_path = img
            elif isinstance(img, Path):
                file_path = str(img)
                orig_name = img.name
                mime_type = client_utils.get_mimetype(file_path)
            else:
                raise ValueError(f"Cannot process type as image: {type(img)}")
            if mime_type is not None and "video" in mime_type:
                return GalleryVideo(
                    video=FileData(
                        path=file_path,  # type: ignore
                        url=url,
                        orig_name=orig_name,
                        mime_type=mime_type,
                    ),
                    caption=caption,
                )
            else:
                return GalleryImage(
                    image=ImageData(
                        path=file_path,
                        url=url,
                        orig_name=orig_name,
                        mime_type=mime_type,
                    ),
                    caption=caption,
                )

        if wasm_utils.IS_WASM:
            for img in value:
                output.append(_save(img))
        else:
            with ThreadPoolExecutor() as executor:
                for o in executor.map(_save, value):
                    output.append(o)
        return GalleryData(root=output)

    @staticmethod
    def convert_to_type(img: str, type: Literal["filepath", "numpy", "pil"]):
        if type == "filepath":
            return img
        else:
            converted_image = PIL.Image.open(img)
            if type == "numpy":
                converted_image = np.array(converted_image)
            return converted_image

    def example_payload(self) -> Any:
        return [
            {
                "image": handle_file(
                    "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
                )
            },
        ]

    def example_value(self) -> Any:
        return [
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
        ]


=== File: gradio/components/highlighted_text.py ===
"""gr.HighlightedText() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Union

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import GradioModel, GradioRootModel
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


class HighlightedToken(GradioModel):
    token: str
    class_or_confidence: Union[str, float, None] = None


class HighlightedTextData(GradioRootModel):
    root: list[HighlightedToken]


@document()
class HighlightedText(Component):
    """
    Displays text that contains spans that are highlighted by category or numerical value.

    Demos: diff_texts
    Guides: named-entity-recognition
    """

    data_model = HighlightedTextData
    EVENTS = [Events.change, Events.select]

    def __init__(
        self,
        value: list[tuple[str, str | float | None]] | dict | Callable | None = None,
        *,
        color_map: dict[str, str]
        | None = None,  # Parameter moved to HighlightedText.style()
        show_legend: bool = False,
        show_inline_category: bool = True,
        combine_adjacent: bool = False,
        adjacent_separator: str = "",
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        interactive: bool | None = None,
        rtl: bool = False,
    ):
        """
        Parameters:
            value: Default value to show. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            color_map: A dictionary mapping labels to colors. The colors may be specified as hex codes or by their names. For example: {"person": "red", "location": "#FFEE22"}
            show_legend: whether to show span categories in a separate legend or inline.
            show_inline_category: If False, will not display span category label. Only applies if show_legend=False and interactive=False.
            combine_adjacent: If True, will merge the labels of adjacent tokens belonging to the same category.
            adjacent_separator: Specifies the separator to be used between tokens if combine_adjacent is True.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            interactive: If True, the component will be editable, and allow user to select spans of text and label them.
            rtl: If True, will display the text in right-to-left direction, and the labels in the legend will also be aligned to the right.
        """
        self.color_map = color_map
        self.show_legend = show_legend
        self.show_inline_category = show_inline_category
        self.combine_adjacent = combine_adjacent
        self.adjacent_separator = adjacent_separator
        self.rtl = rtl
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            interactive=interactive,
        )
        self._value_description = "a list of 2-part tuples, where the first part is a substring of the text and the second part is the category or value of that substring."

    def example_payload(self) -> Any:
        return [
            {"token": "The", "class_or_confidence": None},
            {"token": "quick", "class_or_confidence": "adj"},
        ]

    def example_value(self) -> Any:
        return [("The", None), ("quick", "adj"), ("brown", "adj"), ("fox", "noun")]

    def preprocess(
        self, payload: HighlightedTextData | None
    ) -> list[tuple[str, str | float | None]] | None:
        """
        Parameters:
            payload: An instance of HighlightedTextData
        Returns:
            Passes the value as a list of tuples as a `list[tuple]` into the function. Each `tuple` consists of a `str` substring of the text (so the entire text is included) and `str | float | None` label, which is the category or confidence of that substring.
        """
        if payload is None:
            return None
        return payload.model_dump()  # type: ignore

    def postprocess(
        self, value: list[tuple[str, str | float | None]] | dict | None
    ) -> HighlightedTextData | None:
        """
        Parameters:
            value: Expects a list of (word, category) tuples, or a dictionary of two keys: "text", and "entities", which itself is a list of dictionaries, each of which have the keys: "entity" (or "entity_group"), "start", and "end"
        Returns:
            An instance of HighlightedTextData
        """
        if value is None:
            return None
        if isinstance(value, dict):
            try:
                text = value["text"]
                entities = value["entities"]
            except KeyError as ke:
                raise ValueError(
                    "Expected a dictionary with keys 'text' and 'entities' "
                    "for the value of the HighlightedText component."
                ) from ke
            if len(entities) == 0:
                value = [(text, None)]
            else:
                list_format = []
                index = 0
                entities = sorted(entities, key=lambda x: x["start"])
                for entity in entities:
                    list_format.append((text[index : entity["start"]], None))
                    entity_category = entity.get("entity") or entity.get("entity_group")
                    list_format.append(
                        (text[entity["start"] : entity["end"]], entity_category)
                    )
                    index = entity["end"]
                list_format.append((text[index:], None))
                value = list_format
        if self.combine_adjacent:
            output = []
            running_text, running_category = None, None
            for text, category in value:
                if running_text is None:
                    running_text = text
                    running_category = category
                elif category == running_category:
                    running_text += self.adjacent_separator + text
                elif not text:
                    # Skip fully empty item, these get added in processing
                    # of dictionaries.
                    pass
                else:
                    output.append((running_text, running_category))
                    running_text = text
                    running_category = category
            if running_text is not None:
                output.append((running_text, running_category))
            return HighlightedTextData(
                root=[
                    HighlightedToken(token=o[0], class_or_confidence=o[1])
                    for o in output
                ]
            )
        else:
            return HighlightedTextData(
                root=[
                    HighlightedToken(token=o[0], class_or_confidence=o[1])
                    for o in value
                ]
            )


=== File: gradio/components/html.py ===
"""gr.HTML() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class HTML(Component):
    """
    Creates a component to display arbitrary HTML output. As this component does not accept user input, it is rarely used as an input component.

    Demos: blocks_scroll
    Guides: key-features
    """

    EVENTS = [Events.change, Events.click]

    def __init__(
        self,
        value: str | Callable | None = None,
        *,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool = False,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        min_height: int | None = None,
        max_height: int | None = None,
        container: bool = False,
        padding: bool = True,
    ):
        """
        Parameters:
            value: The HTML content to display. Only static HTML is rendered (e.g. no JavaScript. To render JavaScript, use the `js` or `head` parameters in the `Blocks` constructor). If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            label: The label for this component. Is used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: If True, the label will be displayed. If False, the label will be hidden.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            min_height: The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If HTML content exceeds the height, the component will expand to fit the content.
            max_height: The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If content exceeds the height, the component will scroll.
            container: If True, the HTML component will be displayed in a container. Default is False.
            padding: If True, the HTML component will have a certain padding (set by the `--block-padding` CSS variable) in all directions. Default is True.
        """
        self.min_height = min_height
        self.max_height = max_height
        self.padding = padding
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            container=container,
        )

    def example_payload(self) -> Any:
        return "<p>Hello</p>"

    def example_value(self) -> Any:
        return "<p>Hello</p>"

    def preprocess(self, payload: str | None) -> str | None:
        """
        Parameters:
            payload: string corresponding to the HTML
        Returns:
            (Rarely used) passes the HTML as a `str`.
        """
        return payload

    def postprocess(self, value: str | None) -> str | None:
        """
        Parameters:
            value: Expects a `str` consisting of valid HTML.
        Returns:
            Returns the HTML string.
        """
        return value

    def api_info(self) -> dict[str, Any]:
        return {"type": "string"}


=== File: gradio/components/image.py ===
"""gr.Image() component."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import PIL.Image
from gradio_client import handle_file
from gradio_client.documentation import document

from gradio import image_utils, utils
from gradio.components.base import Component, StreamingInput
from gradio.components.image_editor import WebcamOptions
from gradio.data_classes import Base64ImageData, ImageData
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer

PIL.Image.init()  # fixes https://github.com/gradio-app/gradio/issues/2843


@document()
class Image(StreamingInput, Component):
    """
    Creates an image component that can be used to upload images (as an input) or display images (as an output).

    Demos: sepia_filter, fake_diffusion
    Guides: image-classification-in-pytorch, image-classification-in-tensorflow, image-classification-with-vision-transformers, create-your-own-friends-with-a-gan
    """

    EVENTS = [
        Events.clear,
        Events.change,
        Events.stream,
        Events.select,
        Events.upload,
        Events.input,
    ]

    data_model = ImageData
    image_mode: (
        Literal["1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"]
        | None
    )

    type: Literal["numpy", "pil", "filepath"]

    def __init__(
        self,
        value: str | PIL.Image.Image | np.ndarray | Callable | None = None,
        *,
        format: str = "webp",
        height: int | str | None = None,
        width: int | str | None = None,
        image_mode: (
            Literal[
                "1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"
            ]
            | None
        ) = "RGB",
        sources: (
            list[Literal["upload", "webcam", "clipboard"]]
            | Literal["upload", "webcam", "clipboard"]
            | None
        ) = None,
        type: Literal["numpy", "pil", "filepath"] = "numpy",
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        show_download_button: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        streaming: bool = False,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        mirror_webcam: bool | None = None,
        webcam_options: WebcamOptions | None = None,
        show_share_button: bool | None = None,
        placeholder: str | None = None,
        show_fullscreen_button: bool = True,
        webcam_constraints: dict[str, Any] | None = None,
    ):
        """
        Parameters:
            value: A PIL Image, numpy array, path or URL for the default value that Image component is going to take. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            format: File format (e.g. "png" or "gif"). Used to save image if it does not already have a valid format (e.g. if the image is being returned to the frontend as a numpy array or PIL Image). The format should be supported by the PIL library. Applies both when this component is used as an input or output. This parameter has no effect on SVG files.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.
            width: The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.
            image_mode: The pixel format and color depth that the image should be loaded and preprocessed as. "RGB" will load the image as a color image, or "L" as black-and-white. See https://pillow.readthedocs.io/en/stable/handbook/concepts.html for other supported image modes and their meaning. This parameter has no effect on SVG or GIF files. If set to None, the image_mode will be inferred from the image file type (e.g. "RGBA" for a .png image, "RGB" in most other cases).
            sources: List of sources for the image. "upload" creates a box where user can drop an image file, "webcam" allows user to take snapshot from their webcam, "clipboard" allows users to paste an image from the clipboard. If None, defaults to ["upload", "webcam", "clipboard"] if streaming is False, otherwise defaults to ["webcam"].
            type: The format the image is converted before being passed into the prediction function. "numpy" converts the image to a numpy array with shape (height, width, 3) and values from 0 to 255, "pil" converts the image to a PIL image object, "filepath" passes a str path to a temporary file containing the image. To support animated GIFs in input, the `type` should be set to "filepath" or "pil". To support SVGs, the `type` should be set to "filepath".
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            show_download_button: If True, will display button to download image. Only applies if interactive is False (e.g. if the component is used as an output).
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will allow users to upload and edit an image; if False, can only be used to display images. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            streaming: If True when used in a `live` interface, will automatically stream webcam feed. Only valid is source is 'webcam'. If the component is an output component, will automatically convert images to base64.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            mirror_webcam: If True webcam will be mirrored. Default is True.
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            placeholder: Custom text for the upload area. Overrides default upload messages when provided. Accepts new lines and `#` to designate a heading.
            show_fullscreen_button: If True, will show a fullscreen icon in the corner of the component that allows user to view the image in fullscreen mode. If False, icon does not appear.
            webcam_constraints: A dictionary that allows developers to specify custom media constraints for the webcam stream. This parameter provides flexibility to control the video stream's properties, such as resolution and front or rear camera on mobile devices. See $demo/webcam_constraints
        """
        self.format = format

        self.webcam_options = (
            webcam_options if webcam_options is not None else WebcamOptions()
        )

        if mirror_webcam is not None:
            warnings.warn(
                "The `mirror_webcam` parameter is deprecated. Please use the `webcam_options` parameter with a `gr.WebcamOptions` instance instead."
            )
            self.webcam_options.mirror = mirror_webcam

        if webcam_constraints is not None:
            warnings.warn(
                "The `webcam_constraints` parameter is deprecated. Please use the `webcam_options` parameter with a `gr.WebcamOptions` instance instead."
            )
            self.webcam_options.constraints = webcam_constraints

        valid_types = ["numpy", "pil", "filepath"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        self.height = height
        self.width = width
        self.image_mode = image_mode
        valid_sources = ["upload", "webcam", "clipboard"]
        if sources is None:
            self.sources = (
                ["webcam"] if streaming else ["upload", "webcam", "clipboard"]
            )
        elif isinstance(sources, str):
            self.sources = [sources]  # type: ignore
        else:
            self.sources = sources
        for source in self.sources:  # type: ignore
            if source not in valid_sources:
                raise ValueError(
                    f"`sources` must a list consisting of elements in {valid_sources}"
                )
        self.streaming = streaming
        self.show_download_button = show_download_button
        if streaming and self.sources != ["webcam"]:
            raise ValueError(
                "Image streaming only available if sources is ['webcam']. Streaming not supported with multiple sources."
            )
        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        self.show_fullscreen_button = show_fullscreen_button
        self.placeholder = placeholder

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = (
            "a filepath to an image"
            if self.type == "filepath"
            else (
                "a numpy array representing an image"
                if self.type == "numpy"
                else "a PIL Image"
            )
        )

    def preprocess(
        self, payload: ImageData | None
    ) -> np.ndarray | PIL.Image.Image | str | None:
        """
        Parameters:
            payload: image data in the form of a FileData object
        Returns:
            Passes the uploaded image as a `numpy.array`, `PIL.Image` or `str` filepath depending on `type`.
        """
        return image_utils.preprocess_image(
            payload,
            cache_dir=self.GRADIO_CACHE,
            format=self.format,
            image_mode=self.image_mode,
            type=self.type,
        )

    def postprocess(
        self, value: np.ndarray | PIL.Image.Image | str | Path | None
    ) -> ImageData | Base64ImageData | None:
        """
        Parameters:
            value: Expects a `numpy.array`, `PIL.Image`, or `str` or `pathlib.Path` filepath to an image which is displayed.
        Returns:
            Returns the image as a `FileData` object.
        """
        return image_utils.postprocess_image(
            value,
            cache_dir=self.GRADIO_CACHE,
            format=self.format,
        )

    def api_info_as_output(self) -> dict[str, Any]:
        if self.streaming == "base64":
            schema = Base64ImageData.model_json_schema()
            schema.pop("description", None)
            return schema
        return self.api_info()

    def check_streamable(self):
        if self.streaming and self.sources != ["webcam"]:
            raise ValueError(
                "Image streaming only available if sources is ['webcam']. Streaming not supported with multiple sources."
            )

    def example_payload(self) -> Any:
        return handle_file(
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
        )

    def example_value(self) -> Any:
        return "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"


=== File: gradio/components/image_editor.py ===
r"""gr.ImageEditor() component."""

from __future__ import annotations

import dataclasses
import warnings
from collections.abc import Iterable, Sequence
from io import BytesIO
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Union,
    cast,
)

import numpy as np
import PIL.Image
from gradio_client import handle_file
from gradio_client.documentation import document
from typing_extensions import TypedDict

from gradio import image_utils, utils
from gradio.components.base import Component, server
from gradio.data_classes import FileData, GradioModel
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer

ImageType = Union[np.ndarray, PIL.Image.Image, str]


class EditorValue(TypedDict):
    background: Optional[ImageType]
    layers: list[ImageType]
    composite: Optional[ImageType]


class EditorExampleValue(TypedDict):
    background: Optional[str]
    layers: Optional[list[Union[str, None]]]
    composite: Optional[str]


class EditorData(GradioModel):
    background: Optional[FileData] = None
    layers: list[FileData] = []
    composite: Optional[FileData] = None
    id: Optional[str] = None


class EditorDataBlobs(GradioModel):
    background: Optional[bytes]
    layers: list[Union[bytes, None]]
    composite: Optional[bytes]


class BlobData(TypedDict):
    type: str
    index: Optional[int]
    file: bytes
    id: str


class AcceptBlobs(GradioModel):
    data: BlobData
    files: list[tuple[str, bytes]]


@document()
@dataclasses.dataclass
class Eraser:
    """
    A dataclass for specifying options for the eraser tool in the ImageEditor component. An instance of this class can be passed to the `eraser` parameter of `gr.ImageEditor`.
    Parameters:
        default_size: The default radius, in pixels, of the eraser tool. Defaults to "auto" in which case the radius is automatically determined based on the size of the image (generally 1/50th of smaller dimension).
    """

    default_size: int | Literal["auto"] = "auto"


@document()
@dataclasses.dataclass
class Brush(Eraser):
    """
    A dataclass for specifying options for the brush tool in the ImageEditor component. An instance of this class can be passed to the `brush` parameter of `gr.ImageEditor`.
    Parameters:
        default_size: The default radius, in pixels, of the brush tool. Defaults to "auto" in which case the radius is automatically determined based on the size of the image (generally 1/50th of smaller dimension).
        colors: A list of colors to make available to the user when using the brush. Defaults to a list of 5 colors.
        default_color: The default color of the brush. Defaults to the first color in the `colors` list.
        color_mode: If set to "fixed", user can only select from among the colors in `colors`. If "defaults", the colors in `colors` are provided as a default palette, but the user can also select any color using a color picker.
    """

    colors: list[str | tuple[str, float]] | str | tuple[str, float] | None = None
    default_color: str | tuple[str, float] | None = None
    color_mode: Literal["fixed", "defaults"] = "defaults"

    def __post_init__(self):
        if self.colors is None:
            self.colors = [
                "rgb(204, 50, 50)",
                "rgb(173, 204, 50)",
                "rgb(50, 204, 112)",
                "rgb(50, 112, 204)",
                "rgb(173, 50, 204)",
            ]
        if self.default_color is None:
            self.default_color = (
                self.colors[0] if isinstance(self.colors, list) else self.colors
            )


@document()
@dataclasses.dataclass
class LayerOptions:
    """
    A dataclass for specifying options for the layer tool in the ImageEditor component. An instance of this class can be passed to the `layers` parameter of `gr.ImageEditor`.
    Parameters:
        allow_additional_layers: If True, users can add additional layers to the image. If False, the add layer button will not be shown.
        layers: A list of layers to make available to the user when using the layer tool. One layer must be provided, if the length of the list is 0 then a layer will be generated automatically.
    """

    allow_additional_layers: bool = True
    layers: list[str] | None = None
    disabled: bool = False

    def __post_init__(self):
        if self.layers is None or len(self.layers) == 0:
            self.layers = ["Layer 1"]


@document()
@dataclasses.dataclass
class WebcamOptions:
    """
    A dataclass for specifying options for the webcam tool in the ImageEditor component. An instance of this class can be passed to the `webcam_options` parameter of `gr.ImageEditor`.
    Parameters:
        mirror: If True, the webcam will be mirrored.
        constraints: A dictionary of constraints for the webcam.
    """

    mirror: bool = True
    constraints: dict[str, Any] | None = None


@document()
class ImageEditor(Component):
    """
    Creates an image component that, as an input, can be used to upload and edit images using simple editing tools such
    as brushes, strokes, cropping, and layers. Or, as an output, this component can be used to display images.

    Demos: image_editor
    """

    EVENTS = [
        Events.clear,
        Events.change,
        Events.input,
        Events.select,
        Events.upload,
        Events.apply,
    ]

    data_model = EditorData

    def __init__(
        self,
        value: EditorValue | ImageType | None = None,
        *,
        height: int | str | None = None,
        width: int | str | None = None,
        image_mode: Literal[
            "1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"
        ] = "RGBA",
        sources: (
            Iterable[Literal["upload", "webcam", "clipboard"]]
            | Literal["upload", "webcam", "clipboard"]
            | None
        ) = (
            "upload",
            "webcam",
            "clipboard",
        ),
        type: Literal["numpy", "pil", "filepath"] = "numpy",
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        show_download_button: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        placeholder: str | None = None,
        mirror_webcam: bool | None = None,
        show_share_button: bool | None = None,
        _selectable: bool = False,
        crop_size: tuple[int | float, int | float] | str | None = None,
        transforms: Iterable[Literal["crop", "resize"]] | None = ("crop", "resize"),
        eraser: Eraser | None | Literal[False] = None,
        brush: Brush | None | Literal[False] = None,
        format: str = "webp",
        layers: bool | LayerOptions = True,
        canvas_size: tuple[int, int] = (800, 800),
        fixed_canvas: bool = False,
        show_fullscreen_button: bool = True,
        webcam_options: WebcamOptions | None = None,
    ):
        """
        Parameters:
            value: Optional initial image(s) to populate the image editor. Should be a dictionary with keys: `background`, `layers`, and `composite`. The values corresponding to `background` and `composite` should be images or None, while `layers` should be a list of images. Images can be of type PIL.Image, np.array, or str filepath/URL. Or, the value can be a callable, in which case the function will be called whenever the app loads to set the initial value of the component.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image files or numpy arrays, but will affect the displayed images. Beware of conflicting values with the canvas_size paramter. If the canvas_size is larger than the height, the editing canvas will not fit in the component.
            width: The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image files or numpy arrays, but will affect the displayed images. Beware of conflicting values with the canvas_size paramter. If the canvas_size is larger than the height, the editing canvas will not fit in the component.
            image_mode: "RGB" if color, or "L" if black and white. See https://pillow.readthedocs.io/en/stable/handbook/concepts.html for other supported image modes and their meaning.
            sources: List of sources that can be used to set the background image. "upload" creates a box where user can drop an image file, "webcam" allows user to take snapshot from their webcam, "clipboard" allows users to paste an image from the clipboard.
            type: The format the images are converted to before being passed into the prediction function. "numpy" converts the images to numpy arrays with shape (height, width, 3) and values from 0 to 255, "pil" converts the images to PIL image objects, "filepath" passes images as str filepaths to temporary copies of the images.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            show_download_button: If True, will display button to download image.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will allow users to upload and edit an image; if False, can only be used to display images. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            placeholder: Custom text for the upload area. Overrides default upload messages when provided. Accepts new lines and `#` to designate a heading.
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            crop_size: Deprecated. Used to set the `canvas_size` parameter.
            transforms: The transforms tools to make available to users. "crop" allows the user to crop the image.
            eraser: The options for the eraser tool in the image editor. Should be an instance of the `gr.Eraser` class, or None to use the default settings. Can also be False to hide the eraser tool. [See `gr.Eraser` docs](#eraser).
            brush: The options for the brush tool in the image editor. Should be an instance of the `gr.Brush` class, or None to use the default settings. Can also be False to hide the brush tool, which will also hide the eraser tool. [See `gr.Brush` docs](#brush).
            format: Format to save image if it does not already have a valid format (e.g. if the image is being returned to the frontend as a numpy array or PIL Image).  The format should be supported by the PIL library. This parameter has no effect on SVG files.
            layers: The options for the layer tool in the image editor. Can be a boolean     or an instance of the `gr.LayerOptions` class. If True, will allow users to add layers to the image. If False, the layers option will be hidden. If an instance of `gr.LayerOptions`, it will be used to configure the layer tool. [See `gr.LayerOptions` docs](#layer-options).
            canvas_size: The initial size of the canvas in pixels. The first value is the width and the second value is the height. If `fixed_canvas` is `True`, uploaded images will be rescaled to fit the canvas size while preserving the aspect ratio. Otherwise, the canvas size will change to match the size of an uploaded image.
            fixed_canvas: If True, the canvas size will not change based on the size of the background image and the image will be rescaled to fit (while preserving the aspect ratio) and placed in the center of the canvas.
            show_fullscreen_button: If True, will display button to view image in fullscreen mode.
            webcam_options: The options for the webcam tool in the image editor. Can be an instance of the `gr.WebcamOptions` class, or None to use the default settings. [See `gr.WebcamOptions` docs](#webcam-options).
        """
        self._selectable = _selectable

        self.webcam_options = (
            webcam_options if webcam_options is not None else WebcamOptions()
        )

        if mirror_webcam is not None:
            warnings.warn(
                "The `mirror_webcam` parameter is deprecated. Please use the `webcam_options` parameter with a `gr.WebcamOptions` instance instead."
            )
            self.webcam_options.mirror = mirror_webcam

        valid_types = ["numpy", "pil", "filepath"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        self.height = height
        self.width = width
        self.image_mode = image_mode
        valid_sources = ["upload", "webcam", "clipboard"]
        if isinstance(sources, str):
            sources = [sources]
        if sources is not None:
            for source in sources:
                if source not in valid_sources:
                    raise ValueError(
                        f"`sources` must be a list consisting of elements in {valid_sources}"
                    )
            self.sources = sources
        else:
            self.sources = []

        self.show_download_button = show_download_button

        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )

        if crop_size is not None and canvas_size is None:
            warnings.warn(
                "`crop_size` parameter is deprecated. Please use `canvas_size` instead."
            )
            if isinstance(crop_size, str):
                # convert ratio to tuple
                proportion = [
                    int(crop_size.split(":")[0]),
                    int(crop_size.split(":")[1]),
                ]
                ratio = proportion[0] / proportion[1]
                canvas_size = (
                    (int(800 * ratio), 800) if ratio > 1 else (800, int(800 / ratio))
                )
            else:
                canvas_size = (int(crop_size[0]), int(crop_size[1]))

        self.transforms = transforms
        self.eraser = Eraser() if eraser is None else eraser
        self.brush = Brush() if brush is None else brush
        self.blob_storage: dict[str, EditorDataBlobs] = {}
        self.format = format
        self.layers = (
            LayerOptions()
            if layers is True
            else LayerOptions(disabled=True)
            if layers is False
            else layers
        )
        self.canvas_size = canvas_size
        self.fixed_canvas = fixed_canvas
        self.show_fullscreen_button = show_fullscreen_button
        self.placeholder = placeholder
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = f"a dictionary with structure {{'background': image, 'layers': list of images, 'composite': image}} where each image is {'a filepath' if self.type == 'filepath' else 'a numpy array' if self.type == 'numpy' else 'a PIL Image object'}."

    def convert_and_format_image(
        self,
        file: FileData | None | bytes,
    ) -> np.ndarray | PIL.Image.Image | str | None:
        if file is None:
            return None
        im = (
            PIL.Image.open(file.path)
            if isinstance(file, FileData)
            else PIL.Image.open(BytesIO(file))
        )
        if isinstance(file, (bytes, bytearray, memoryview)):
            name = "image"
            suffix = self.format
        elif file.orig_name:
            p = Path(file.orig_name)
            name = p.stem
            suffix = p.suffix.replace(".", "")
            if suffix in ["jpg", "jpeg"]:
                suffix = "jpeg"
        else:
            name = "image"
            suffix = self.format
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            im = im.convert(self.image_mode)
        return image_utils.format_image(
            im,
            cast(Literal["numpy", "pil", "filepath"], self.type),
            self.GRADIO_CACHE,
            format=suffix,
            name=name,
        )

    def preprocess(self, payload: EditorData | None) -> EditorValue | None:
        """
        Parameters:
            payload: An instance of `EditorData` consisting of the background image, layers, and composite image.
        Returns:
            Passes the uploaded images as an instance of EditorValue, which is just a `dict` with keys: 'background', 'layers', and 'composite'. The values corresponding to 'background' and 'composite' are images, while 'layers' is a `list` of images. The images are of type `PIL.Image`, `np.array`, or `str` filepath, depending on the `type` parameter.
        """
        if payload is None:
            return payload

        if payload.id is not None:
            cached = self.blob_storage.get(payload.id)
            _payload = (
                EditorDataBlobs(
                    background=cached.background,
                    layers=cached.layers,
                    composite=cached.composite,
                )
                if cached
                else None
            )
        else:
            _payload = payload

        bg = None
        layers = None
        composite = None

        if _payload is not None:
            bg = self.convert_and_format_image(_payload.background)
            layers = (
                [self.convert_and_format_image(layer) for layer in _payload.layers]
                if _payload.layers
                else None
            )
            composite = self.convert_and_format_image(_payload.composite)

        if payload.id is not None and payload.id in self.blob_storage:
            self.blob_storage.pop(payload.id)

        return {
            "background": bg,
            "layers": [x for x in layers if x is not None] if layers else [],
            "composite": composite,
        }

    def postprocess(self, value: EditorValue | ImageType | None) -> EditorData | None:
        """
        Parameters:
            value: Expects a EditorValue, which is just a dictionary with keys: 'background', 'layers', and 'composite'. The values corresponding to 'background' and 'composite' should be images or None, while `layers` should be a list of images. Images can be of type `PIL.Image`, `np.array`, or `str` filepath/URL. Or, the value can be simply a single image (`ImageType`), in which case it will be used as the background.
        Returns:
            An instance of `EditorData` consisting of the background image, layers, and composite image.
        """
        if value is None:
            return None
        elif isinstance(value, dict):
            pass
        elif isinstance(value, (np.ndarray, PIL.Image.Image, str)):
            value = {"background": value, "layers": [], "composite": value}
        else:
            raise ValueError(
                "The value to `gr.ImageEditor` must be a dictionary of images or a single image."
            )

        layers = (
            [
                FileData(
                    path=image_utils.save_image(
                        cast(Union[np.ndarray, PIL.Image.Image, str], layer),
                        self.GRADIO_CACHE,
                        format=self.format,
                    )
                )
                for layer in value["layers"]
            ]
            if value["layers"]
            else []
        )

        return EditorData(
            background=(
                FileData(
                    path=image_utils.save_image(
                        value["background"], self.GRADIO_CACHE, format=self.format
                    )
                )
                if value["background"] is not None
                else None
            ),
            layers=layers,
            composite=(
                FileData(
                    path=image_utils.save_image(
                        cast(
                            Union[np.ndarray, PIL.Image.Image, str], value["composite"]
                        ),
                        self.GRADIO_CACHE,
                        format=self.format,
                    )
                )
                if value["composite"] is not None
                else None
            ),
        )

    def example_payload(self) -> Any:
        return {
            "background": handle_file(
                "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
            ),
            "layers": [],
            "composite": None,
        }

    def example_value(self) -> Any:
        return {
            "background": "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",
            "layers": [],
            "composite": None,
        }

    @server
    def accept_blobs(self, data: AcceptBlobs):
        """
        Accepts a dictionary of image blobs, where the keys are 'background', 'layers', and 'composite', and the values are binary file-like objects.
        """

        type = data.data["type"]
        index = (
            int(data.data["index"])
            if data.data["index"] and data.data["index"] != "null"
            else None
        )
        file = data.files[0][1]
        id = data.data["id"]

        current = self.blob_storage.get(
            id, EditorDataBlobs(background=None, layers=[], composite=None)
        )

        if type == "layer" and index is not None:
            if index >= len(current.layers):
                current.layers.extend([None] * (index + 1 - len(current.layers)))
            current.layers[index] = file
        elif type == "background":
            current.background = file
        elif type == "composite":
            current.composite = file

        self.blob_storage[id] = current


=== File: gradio/components/imageslider.py ===
"""gr.ImageSlider() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import PIL.Image
from gradio_client import handle_file
from gradio_client.documentation import document

from gradio import image_utils
from gradio.components.base import Component
from gradio.data_classes import GradioRootModel, ImageData
from gradio.events import Events


class SliderData(GradioRootModel):
    root: tuple[ImageData | None, ImageData | None] | None


image_tuple = tuple[
    str | PIL.Image.Image | np.ndarray | None, str | PIL.Image.Image | np.ndarray | None
]


if TYPE_CHECKING:
    from gradio.components import Timer

PIL.Image.init()  # fixes https://github.com/gradio-app/gradio/issues/2843


@document()
class ImageSlider(Component):
    """
    Creates an image component that can be used to upload images (as an input) or display images (as an output).

    Demos: imageslider
    """

    EVENTS = [
        Events.clear,
        Events.change,
        Events.stream,
        Events.select,
        Events.upload,
        Events.input,
    ]

    data_model = SliderData
    image_mode: (
        Literal["1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"]
        | None
    )
    type: Literal["numpy", "pil", "filepath"]

    def __init__(
        self,
        value: image_tuple | Callable | None = None,
        *,
        format: str = "webp",
        height: int | str | None = None,
        width: int | str | None = None,
        image_mode: (
            Literal[
                "1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"
            ]
            | None
        ) = "RGB",
        type: Literal["numpy", "pil", "filepath"] = "numpy",
        label: str | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        show_download_button: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        show_fullscreen_button: bool = True,
        slider_position: float = 50,
        max_height: int = 500,
    ):
        """
        Parameters:
            value: A tuple of PIL Image, numpy array, path or URL for the default value that ImageSlider component is going to take, this pair of images should be of equal size. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            format: File format (e.g. "png" or "gif"). Used to save image if it does not already have a valid format (e.g. if the image is being returned to the frontend as a numpy array or PIL Image). The format should be supported by the PIL library. Applies both when this component is used as an input or output. This parameter has no effect on SVG files.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed tuple of image file or numpy array, but will affect the displayed image.
            width: The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed tuple of image file or numpy array, but will affect the displayed image.
            image_mode: The pixel format and color depth that the image should be loaded and preprocessed as. "RGB" will load the image as a color image, or "L" as black-and-white. See https://pillow.readthedocs.io/en/stable/handbook/concepts.html for other supported image modes and their meaning. This parameter has no effect on SVG or GIF files. If set to None, the image_mode will be inferred from the image file types (e.g. "RGBA" for a .png image, "RGB" in most other cases).
            type: The format the images are converted to before being passed into the prediction function. "numpy" converts the images to numpy arrays with shape (height, width, 3) and values from 0 to 255, "pil" converts the images to PIL image objects, "filepath" passes str paths to temporary files containing the images. To support animated GIFs in input, the `type` should be set to "filepath" or "pil". To support SVGs, the `type` should be set to "filepath".
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            show_download_button: If True, will display button to download image. Only applies if interactive is False (e.g. if the component is used as an output).
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will allow users to upload and edit an image; if False, can only be used to display images. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            show_fullscreen_button: If True, will show a fullscreen icon in the corner of the component that allows user to view the image in fullscreen mode. If False, icon does not appear.
            slider_position: The position of the slider as a percentage of the width of the image, between 0 and 100.
            max_height: The maximum height of the image.
        """
        self.format = format
        self.slider_position = slider_position
        self.max_height = max_height
        valid_types = ["numpy", "pil", "filepath"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        self.height = height
        self.width = width
        self.image_mode = image_mode
        self.show_download_button = show_download_button
        self.show_fullscreen_button = show_fullscreen_button

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = (
            "a tuple of filepaths to images"
            if self.type == "filepath"
            else (
                "a tuple of numpy arrays representing images"
                if self.type == "numpy"
                else "a tuple of PIL Images"
            )
        )

    def preprocess(self, payload: SliderData | None) -> image_tuple | None:
        """
        Parameters:
            payload: image data in the form of a SliderData object
        Returns:
            Passes the uploaded image as a tuple of `numpy.array`, `PIL.Image` or `str` filepath depending on `type`.
        """
        if payload is None:
            return None
        if payload.root is None:
            raise ValueError("Payload is None.")
        return (
            image_utils.preprocess_image(
                payload.root[0],
                cache_dir=self.GRADIO_CACHE,
                format=self.format,
                image_mode=self.image_mode,
                type=self.type,
            ),
            image_utils.preprocess_image(
                payload.root[1],
                cache_dir=self.GRADIO_CACHE,
                format=self.format,
                image_mode=self.image_mode,
                type=self.type,
            ),
        )

    def postprocess(
        self,
        value: tuple[
            np.ndarray | PIL.Image.Image | str | Path | None,
            np.ndarray | PIL.Image.Image | str | Path | None,
        ]
        | None,
    ) -> SliderData | None:
        """
        Parameters:
            value: Expects a tuple of `numpy.array`, `PIL.Image`, or `str` or `pathlib.Path` filepath to an image which is displayed.
        Returns:
            Returns the image as a `SliderData` object.
        """
        if value is None:
            return None
        return SliderData(
            root=(
                image_utils.postprocess_image(
                    value[0], cache_dir=self.GRADIO_CACHE, format=self.format
                ),
                image_utils.postprocess_image(
                    value[1], cache_dir=self.GRADIO_CACHE, format=self.format
                ),
            )
        )

    def api_info_as_output(self) -> dict[str, Any]:
        return self.api_info()

    def example_payload(self) -> Any:
        return (
            handle_file(
                "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
            ),
            handle_file(
                "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
            ),
        )

    def example_value(self) -> Any:
        return (
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",
        )


=== File: gradio/components/json_component.py ===
"""gr.JSON() component."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
)

import orjson
from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import JsonData
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class JSON(Component):
    """
    Used to display arbitrary JSON output prettily. As this component does not accept user input, it is rarely used as an input component.

    Demos: zip_to_json, blocks_xray
    """

    EVENTS = [Events.change]

    def __init__(
        self,
        value: str | dict | list | Callable | None = None,
        *,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        open: bool = False,
        show_indices: bool = False,
        height: int | str | None = None,
        max_height: int | str | None = 500,
        min_height: int | str | None = None,
    ):
        """
        Parameters:
            value: Default value as a valid JSON `str` -- or a `list` or `dict` that can be serialized to a JSON string. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            open: If True, all JSON nodes will be expanded when rendered. By default, node levels deeper than 3 are collapsed.
            show_indices: Whether to show numerical indices when displaying the elements of a list within the JSON object.
            height: Height of the JSON component in pixels if a number is passed, or in CSS units if a string is passed. Overflow will be scrollable. If None, the height will be automatically adjusted to fit the content.
        """
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

        self.show_indices = show_indices
        self.open = open
        self.height = height
        self.max_height = max_height
        self.min_height = min_height

    def preprocess(self, payload: dict | list | None) -> dict | list | None:
        """
        Parameters:
            payload: JSON value as a `dict` or `list`
        Returns:
            Passes the JSON value as a `dict` or `list` depending on the value.
        """
        return payload

    def postprocess(self, value: dict | list | str | None) -> JsonData | None:
        """
        Parameters:
            value: Expects a valid JSON `str` -- or a `list` or `dict` that can be serialized to a JSON string. The `list` or `dict` value can contain numpy arrays.
        Returns:
            Returns the JSON as a `list` or `dict`.
        """
        if value is None:
            return None
        if isinstance(value, str):
            return JsonData(orjson.loads(value))
        else:
            # Use orjson to convert NumPy arrays and datetime objects to JSON.
            # This ensures a backward compatibility with the previous behavior.
            # See https://github.com/gradio-app/gradio/pull/8041
            return JsonData(
                orjson.loads(
                    orjson.dumps(
                        value,
                        option=orjson.OPT_SERIALIZE_NUMPY
                        | orjson.OPT_PASSTHROUGH_DATETIME,
                        default=str,
                    )
                )
            )

    def example_payload(self) -> Any:
        return {"foo": "bar"}

    def example_value(self) -> Any:
        return {"foo": "bar"}

    def read_from_flag(self, payload: Any):
        return json.loads(payload)

    def api_info(self) -> dict[str, Any]:
        return {"type": {}, "description": "any valid json"}

    def as_example(self, value) -> Any:
        val = self.postprocess(value)
        if val:
            val = val.model_dump()
        return val


=== File: gradio/components/label.py ===
"""gr.Label() component."""

from __future__ import annotations

import json
import operator
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import GradioModel
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


class LabelConfidence(GradioModel):
    label: Optional[Union[str, int, float]] = None
    confidence: Optional[float] = None


class LabelData(GradioModel):
    label: Optional[Union[str, int, float]] = None
    confidences: Optional[list[LabelConfidence]] = None


@document()
class Label(Component):
    """
    Displays a classification label, along with confidence scores of top categories, if provided. As this component does not
    accept user input, it is rarely used as an input component.

    Guides: image-classification-in-pytorch, image-classification-in-tensorflow, image-classification-with-vision-transformers
    """

    CONFIDENCES_KEY = "confidences"
    data_model = LabelData
    EVENTS = [Events.change, Events.select]

    def __init__(
        self,
        value: dict[str, float] | str | float | Callable | None = None,
        *,
        num_top_classes: int | None = None,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        color: str | None = None,
        show_heading: bool = True,
    ):
        """
        Parameters:
            value: Default value to show in the component. If a str or number is provided, simply displays the string or number. If a {Dict[str, float]} of classes and confidences is provided, displays the top class on top and the `num_top_classes` below, along with their confidence bars. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            num_top_classes: number of most confident classes to show.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            color: The background color of the label (either a valid css color name or hexadecimal string).
            show_heading: If False, the heading will not be displayed if a dictionary of labels and confidences is provided. The heading will still be visible if the value is a string or number.
        """
        self.num_top_classes = num_top_classes
        self.color = color
        self.show_heading = show_heading
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = "a dictionary mapping string categories to float values that represent confidence from 0 - 1."

    def preprocess(
        self, payload: LabelData | None
    ) -> dict[str, float] | str | int | float | None:
        """
        Parameters:
            payload: An instance of `LabelData` containing the label and confidences.
        Returns:
            Depending on the value, passes the label as a `str | int | float`, or the labels and confidences as a `dict[str, float]`.
        """
        if payload is None:
            return None
        if payload.confidences is None:
            return payload.label
        return {
            d["label"]: d["confidence"] for d in payload.model_dump()["confidences"]
        }

    def postprocess(
        self, value: dict[str | float, float] | str | int | float | None
    ) -> LabelData | dict | None:
        """
        Parameters:
            value: Expects a `dict[str, float]` of classes and confidences, or `str` with just the class or an `int | float` for regression outputs, or a `str` path to a .json file containing a json dictionary in one of the preceding formats.
        Returns:
            Returns a `LabelData` object with the label and confidences, or a `dict` of the same format, or a `str` or `int` or `float` if the input was a single label.
        """
        if value is None or value == {}:
            return {}
        if isinstance(value, str) and value.endswith(".json") and Path(value).exists():
            return LabelData(**json.loads(Path(value).read_text()))
        if isinstance(value, (str, float, int)):
            return LabelData(label=str(value))
        if isinstance(value, dict):
            if "confidences" in value and isinstance(value["confidences"], dict):
                value = value["confidences"]
                value = {c["label"]: c["confidence"] for c in value}
            sorted_pred = sorted(
                value.items(), key=operator.itemgetter(1), reverse=True
            )
            if self.num_top_classes is not None:
                sorted_pred = sorted_pred[: self.num_top_classes]
            return LabelData(
                label=sorted_pred[0][0],
                confidences=[
                    LabelConfidence(label=pred[0], confidence=pred[1])
                    for pred in sorted_pred
                ],
            )
        raise ValueError(
            "The `Label` output interface expects one of: a string label, or an int label, a "
            "float label, or a dictionary whose keys are labels and values are confidences. "
            f"Instead, got a {type(value)}"
        )

    def example_payload(self) -> Any:
        return {
            "label": "Cat",
            "confidences": [
                {"label": "cat", "confidence": 0.9},
                {"label": "dog", "confidence": 0.1},
            ],
        }

    def example_value(self) -> Any:
        return {"cat": 0.9, "dog": 0.1}


=== File: gradio/components/line_plot.py ===
"""gr.LinePlot() component"""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.components.plot import AltairPlot, AltairPlotData, Plot
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    import pandas as pd

    from gradio.components import Timer


@document()
class LinePlot(Plot):
    """
    Creates a line plot component to display data from a pandas DataFrame (as output). As this component does
    not accept user input, it is rarely used as an input component.

    Demos: live_dashboard
    """

    data_model = AltairPlotData

    EVENTS = [Events.select]

    def __init__(
        self,
        value: pd.DataFrame | Callable | None = None,
        x: str | None = None,
        y: str | None = None,
        *,
        color: str | None = None,
        stroke_dash: str | None = None,
        overlay_point: bool | None = None,
        title: str | None = None,
        tooltip: list[str] | str | None = None,
        x_title: str | None = None,
        y_title: str | None = None,
        x_label_angle: float | None = None,
        y_label_angle: float | None = None,
        color_legend_title: str | None = None,
        stroke_dash_legend_title: str | None = None,
        color_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        stroke_dash_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        height: int | None = None,
        width: int | None = None,
        x_lim: list[int] | None = None,
        y_lim: list[int] | None = None,
        caption: str | I18nData | None = None,
        label: str | I18nData | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        show_actions_button: bool = False,
        interactive: bool | None = None,
    ):
        """
        Parameters:
            value: The pandas dataframe containing the data to display in a scatter plot.
            x: Column corresponding to the x axis. Can be grouped if datetime, e.g. 'yearmonth(date)' or 'minuteseconds(date)' with a column name 'date'. Any time unit supported by altair can be used.
            y: Column corresponding to the y axis. Can be aggregated, e.g. 'sum(price)' or 'count(price)' with a column name 'price'. Any aggregation function supported by altair can be used.
            color: The column to determine the point color. If the column contains numeric data, gradio will interpolate the column data so that small values correspond to light colors and large values correspond to dark values.
            stroke_dash: The column to determine the symbol used to draw the line, e.g. dashed lines, dashed lines with points.
            overlay_point: Whether to draw a point on the line for each (x, y) coordinate pair.
            title: The title to display on top of the chart.
            tooltip: The column (or list of columns) to display on the tooltip when a user hovers a point on the plot. Set to [] to disable tooltips.
            x_title: The title given to the x axis. By default, uses the value of the x parameter.
            y_title: The title given to the y axis. By default, uses the value of the y parameter.
            x_label_angle: The angle for the x axis labels. Positive values are clockwise, and negative values are counter-clockwise.
            y_label_angle: The angle for the y axis labels. Positive values are clockwise, and negative values are counter-clockwise.
            color_legend_title: The title given to the color legend. By default, uses the value of color parameter.
            stroke_dash_legend_title: The title given to the stroke_dash legend. By default, uses the value of the stroke_dash parameter.
            color_legend_position: The position of the color legend. If the string value 'none' is passed, this legend is omitted. For other valid position values see: https://vega.github.io/vega/docs/legends/#orientation.
            stroke_dash_legend_position: The position of the stoke_dash legend. If the string value 'none' is passed, this legend is omitted. For other valid position values see: https://vega.github.io/vega/docs/legends/#orientation.
            height: The height of the plot in pixels.
            width: The width of the plot in pixels. If None, expands to fit.
            x_lim: A tuple or list containing the limits for the x-axis, specified as [x_min, x_max].
            y_lim: A tuple of list containing the limits for the y-axis, specified as [y_min, y_max].
            caption: The (optional) caption to display below the plot.
            interactive: Deprecated.
            label: The (optional) label to display on the top left corner of the plot.
            show_label: Whether the label should be displayed.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            visible: Whether the plot should be visible.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            show_actions_button: Whether to show the actions button on the top right corner of the plot.
        """
        self.x = x
        self.y = y
        self.color = color
        self.stroke_dash = stroke_dash
        self.tooltip = (
            tooltip if tooltip is not None else [elem for elem in [x, y, color] if elem]
        )
        self.title = title
        self.x_title = x_title
        self.y_title = y_title
        self.x_label_angle = x_label_angle
        self.y_label_angle = y_label_angle
        self.color_legend_title = color_legend_title
        self.stroke_dash_legend_title = stroke_dash_legend_title
        self.color_legend_position = color_legend_position
        self.stroke_dash_legend_position = stroke_dash_legend_position
        self.overlay_point = overlay_point
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.caption = caption
        if isinstance(width, str):
            width = None
            warnings.warn(
                "Width should be an integer, not a string. Setting width to None."
            )
        if isinstance(height, str):
            warnings.warn(
                "Height should be an integer, not a string. Setting height to None."
            )
            height = None
        self.width = width
        self.height = height
        self.show_actions_button = show_actions_button
        if label is None and show_label is None:
            show_label = False
        super().__init__(
            value=value,
            label=label,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            every=every,
            inputs=inputs,
        )
        if interactive is not None:
            warnings.warn(
                "The `interactive` parameter is deprecated and will be removed in a future version. "
                "The LinePlot component is always interactive."
            )

    def get_block_name(self) -> str:
        return "plot"

    @staticmethod
    def create_plot(
        value: pd.DataFrame,
        x: str,
        y: str,
        color: str | None = None,
        stroke_dash: str | None = None,
        overlay_point: bool | None = None,
        title: str | None = None,
        tooltip: list[str] | str | None = None,
        x_title: str | None = None,
        y_title: str | None = None,
        x_label_angle: float | None = None,
        y_label_angle: float | None = None,
        color_legend_title: str | None = None,
        stroke_dash_legend_title: str | None = None,
        color_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        stroke_dash_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        height: int | None = None,
        width: int | None = None,
        x_lim: list[int] | None = None,
        y_lim: list[int] | None = None,
    ):
        """Helper for creating the scatter plot."""
        import altair as alt

        encodings = {
            "x": alt.X(
                x,
                title=x_title or x,
                scale=AltairPlot.create_scale(x_lim),
                axis=alt.Axis(labelAngle=x_label_angle)
                if x_label_angle is not None
                else alt.Axis(),
            ),
            "y": alt.Y(
                y,
                title=y_title or y,
                scale=AltairPlot.create_scale(y_lim),
                axis=alt.Axis(labelAngle=y_label_angle)
                if y_label_angle is not None
                else alt.Axis(),
            ),
        }
        properties = {}
        if title:
            properties["title"] = title
        if height:
            properties["height"] = height
        if width:
            properties["width"] = width

        if color:
            color_legend_position = color_legend_position or "bottom"
            domain = value[color].unique().tolist()
            range_ = list(range(len(domain)))
            encodings["color"] = {
                "field": color,
                "type": "nominal",
                "scale": {"domain": domain, "range": range_},
                "legend": AltairPlot.create_legend(
                    position=color_legend_position, title=color_legend_title
                ),
            }

        if stroke_dash:
            stroke_dash_encoding = {
                "field": stroke_dash,
                "legend": AltairPlot.create_legend(
                    position=stroke_dash_legend_position or "bottom",
                    title=stroke_dash_legend_title,
                ),
            }
        else:
            stroke_dash_encoding = alt.value(alt.Undefined)

        if tooltip:
            encodings["tooltip"] = tooltip

        chart = alt.Chart(value).encode(**encodings)

        points = chart.mark_point(clip=True).encode(
            opacity=alt.value(alt.Undefined) if overlay_point else alt.value(0),
        )
        lines = chart.mark_line(clip=True).encode(strokeDash=stroke_dash_encoding)

        highlight = alt.selection_point(
            on="mouseover",
            fields=[c for c in [color, stroke_dash] if c],
            nearest=True,
            clear="mouseout",
            empty=False,
        )
        points = points.add_params(highlight)
        lines = lines.encode(
            size=alt.condition(highlight, alt.value(4), alt.value(2)),
        )
        if not overlay_point:
            highlight_pts = alt.selection_point(
                on="mouseover",
                nearest=True,
                clear="mouseout",
                empty=False,
            )
            points = points.add_params(highlight_pts)

            points = points.encode(
                opacity=alt.condition(highlight_pts, alt.value(1), alt.value(0)),
                size=alt.condition(highlight_pts, alt.value(100), alt.value(0)),
            )

        chart = (lines + points).properties(background="transparent", **properties)

        selection = alt.selection_interval(
            encodings=["x"],
            mark=alt.BrushConfig(fill="gray", fillOpacity=0.3, stroke="none"),
            name="brush",
        )
        chart = chart.add_params(selection)

        return chart

    def preprocess(self, payload: AltairPlotData | None) -> AltairPlotData | None:
        """
        Parameters:
            payload: The data to display in a line plot.
        Returns:
            (Rarely used) passes the data displayed in the line plot as an AltairPlotData dataclass, which includes the plot information as a JSON string, as well as the type of plot (in this case, "line").
        """
        return payload

    def postprocess(
        self, value: pd.DataFrame | dict | None
    ) -> AltairPlotData | dict | None:
        """
        Parameters:
            value: Expects a pandas DataFrame containing the data to display in the line plot. The DataFrame should contain at least two columns, one for the x-axis (corresponding to this component's `x` argument) and one for the y-axis (corresponding to `y`).
        Returns:
            The data to display in a line plot, in the form of an AltairPlotData dataclass, which includes the plot information as a JSON string, as well as the type of plot (in this case, "line").
        """
        # if None or update
        if value is None or isinstance(value, dict):
            return value
        if self.x is None or self.y is None:
            raise ValueError("No value provided for required parameters `x` and `y`.")
        chart = self.create_plot(
            value=value,
            x=self.x,
            y=self.y,
            color=self.color,
            overlay_point=self.overlay_point,
            title=self.title,
            tooltip=self.tooltip,
            x_title=self.x_title,
            y_title=self.y_title,
            x_label_angle=self.x_label_angle,
            y_label_angle=self.y_label_angle,
            color_legend_title=self.color_legend_title,  # type: ignore
            color_legend_position=self.color_legend_position,  # type: ignore
            stroke_dash_legend_title=self.stroke_dash_legend_title,
            stroke_dash_legend_position=self.stroke_dash_legend_position,  # type: ignore
            x_lim=self.x_lim,
            y_lim=self.y_lim,
            stroke_dash=self.stroke_dash,
            height=self.height,
            width=self.width,
        )

        return AltairPlotData(type="altair", plot=chart.to_json(), chart="line")

    def example_payload(self) -> Any:
        return None

    def example_value(self) -> Any:
        import pandas as pd

        return pd.DataFrame({self.x: [1, 2, 3], self.y: [4, 5, 6]})


=== File: gradio/components/login_button.py ===
"""Predefined button to sign in with Hugging Face in a Gradio Space."""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from gradio_client.documentation import document

from gradio import utils
from gradio.components import Button, Component
from gradio.context import get_blocks_context
from gradio.routes import Request

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class LoginButton(Button):
    """
    Creates a button that redirects the user to Sign with Hugging Face using OAuth. If
    created inside of a Blocks context, it will add an event to check if the user is logged in
    and update the button text accordingly. If created outside of a Blocks context, call the
    `LoginButton.activate()` method to add the event.
    """

    is_template = True

    def __init__(
        self,
        value: str = "Sign in with Hugging Face",
        logout_value: str = "Logout ({})",
        *,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary", "stop", "huggingface"] = "huggingface",
        size: Literal["sm", "md", "lg"] = "lg",
        icon: str | Path | None = utils.get_icon_path("huggingface-logo.svg"),
        link: str | None = None,
        visible: bool = True,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        scale: int | None = None,
        min_width: int | None = None,
    ):
        """
        Parameters:
            logout_value: The text to display when the user is signed in. The string should contain a placeholder for the username with a call-to-action to logout, e.g. "Logout ({})".
        """
        self.logout_value = logout_value
        super().__init__(
            value,
            every=every,
            inputs=inputs,
            variant=variant,
            size=size,
            icon=icon,
            link=link,
            visible=visible,
            interactive=interactive,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            scale=scale,
            min_width=min_width,
        )
        if get_blocks_context():
            self.activate()

    def activate(self):
        # Taken from https://cmgdo.com/external-link-in-gradio-button/
        # Taking `self` as input to check if user is logged in
        # ('self' value will be either "Sign in with Hugging Face" or "Signed in as ...")
        _js = _js_handle_redirect.replace(
            "BUTTON_DEFAULT_VALUE", json.dumps(self.value)
        ).replace("REDIRECT_URL", self.page)
        self.click(fn=None, inputs=[self], outputs=None, js=_js)

        self.attach_load_event(self._check_login_status, None)

    def _check_login_status(self, request: Request) -> LoginButton:
        # Each time the page is refreshed or loaded, check if the user is logged in and adapt label
        session = getattr(request, "session", None) or getattr(
            request.request, "session", None
        )

        if session is None or "oauth_info" not in session:
            # Cookie set but user not logged in
            return LoginButton(self.value, interactive=True)

        oauth_info = session["oauth_info"]
        expires_at = oauth_info.get("expires_at")
        if expires_at is not None and expires_at < time.time():
            # User is logged in but token has expired => logout
            session.pop("oauth_info", None)
            return LoginButton(self.value, interactive=True)

        # User is correctly logged in
        username = oauth_info["userinfo"]["preferred_username"]
        return LoginButton(self.logout_value.format(username), interactive=True)


# JS code to redirects to /login/huggingface if user is not logged in.
# If user is logged in, redirect to /logout page. Always happens
# on the same tab.
_js_handle_redirect = """
(buttonValue) => {
    uri = buttonValue === BUTTON_DEFAULT_VALUE ? '/login/huggingface?_target_url=/REDIRECT_URL' : '/logout?_target_url=/REDIRECT_URL';
    window.parent?.postMessage({ type: "SET_SCROLLING", enabled: true }, "*");
    setTimeout(() => {
        window.location.assign(uri + window.location.search);
    }, 500);
}
"""


=== File: gradio/components/logout_button.py ===
"""Predefined button to sign out from Hugging Face in a Gradio Space."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal

from gradio_client.documentation import document

from gradio.components import Button, Component

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class LogoutButton(Button):
    """
    Creates a Button to log out a user from a Space using OAuth.

    Note: `LogoutButton` component is deprecated. Please use `gr.LoginButton` instead
          which handles both the login and logout processes.
    """

    is_template = True

    def __init__(
        self,
        value: str = "Logout",
        *,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary", "stop"] = "secondary",
        size: Literal["sm", "lg"] = "lg",
        icon: str
        | None = "https://huggingface.co/front/assets/huggingface_logo-noborder.svg",
        # Link to logout page (which will delete the session cookie and redirect to landing page).
        link: str | None = "/gradio_api/logout",
        visible: bool = True,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        scale: int | None = 0,
        min_width: int | None = None,
    ):
        warnings.warn(
            "The `gr.LogoutButton` component is deprecated. Please use `gr.LoginButton` instead which handles both the login and logout processes."
        )
        super().__init__(
            value,
            every=every,
            inputs=inputs,
            variant=variant,
            size=size,
            icon=icon,
            link=link,
            visible=visible,
            interactive=interactive,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            scale=scale,
            min_width=min_width,
        )


=== File: gradio/components/markdown.py ===
"""gr.Markdown() component."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Markdown(Component):
    """
    Used to render arbitrary Markdown output. Can also render latex enclosed by dollar signs. As this component does not accept user input,
    it is rarely used as an input component.

    Demos: blocks_hello, blocks_kinematics
    Guides: key-features
    """

    EVENTS = [
        Events.change,
        Events.copy,
    ]

    def __init__(
        self,
        value: str | I18nData | Callable | None = None,
        *,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        rtl: bool = False,
        latex_delimiters: list[dict[str, str | bool]] | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        sanitize_html: bool = True,
        line_breaks: bool = False,
        header_links: bool = False,
        height: int | str | None = None,
        max_height: int | str | None = None,
        min_height: int | str | None = None,
        show_copy_button: bool = False,
        container: bool = False,
        padding: bool = False,
    ):
        """
        Parameters:
            value: Value to show in Markdown component. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            label: This parameter has no effect
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: This parameter has no effect.
            rtl: If True, sets the direction of the rendered text to right-to-left. Default is False, which renders text left-to-right.
            latex_delimiters: A list of dicts of the form {"left": open delimiter (str), "right": close delimiter (str), "display": whether to display in newline (bool)} that will be used to render LaTeX expressions. If not provided, `latex_delimiters` is set to `[{ "left": "$$", "right": "$$", "display": True }]`, so only expressions enclosed in $$ delimiters will be rendered as LaTeX, and in a new line. Pass in an empty list to disable LaTeX rendering. For more information, see the [KaTeX documentation](https://katex.org/docs/autorender.html).
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            sanitize_html: If False, will disable HTML sanitization when converted from markdown. This is not recommended, as it can lead to security vulnerabilities.
            line_breaks: If True, will enable Github-flavored Markdown line breaks in chatbot messages. If False (default), single new lines will be ignored.
            header_links: If True, will automatically create anchors for headings, displaying a link icon on hover.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If markdown content exceeds the height, the component will scroll.
            max_height: The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If markdown content exceeds the height, the component will scroll. If markdown content is shorter than the height, the component will shrink to fit the content. Will not have any effect if `height` is set and is smaller than `max_height`.
            min_height: The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If markdown content exceeds the height, the component will expand to fit the content. Will not have any effect if `height` is set and is larger than `min_height`.
            show_copy_button: If True, includes a copy button to copy the text in the Markdown component. Default is False.
            container: If True, the Markdown component will be displayed in a container. Default is False.
            padding: If True, the Markdown component will have a certain padding (set by the `--block-padding` CSS variable) in all directions. Default is False.
        """
        self.rtl = rtl
        if latex_delimiters is None:
            latex_delimiters = [{"left": "$$", "right": "$$", "display": True}]
        self.latex_delimiters = latex_delimiters
        self.sanitize_html = sanitize_html
        self.line_breaks = line_breaks
        self.header_links = header_links
        self.height = height
        self.max_height = max_height
        self.min_height = min_height
        self.show_copy_button = show_copy_button
        self.padding = padding

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            container=container,
        )

    def preprocess(self, payload: str | None) -> str | None:
        """
        Parameters:
            payload: the `str` of Markdown corresponding to the displayed value.
        Returns:
            Passes the `str` of Markdown corresponding to the displayed value.
        """
        return payload

    def postprocess(self, value: str | I18nData | None) -> str | dict | None:
        """
        Parameters:
            value: Expects a valid `str` that can be rendered as Markdown.
        Returns:
            The same `str` as the input, but with leading and trailing whitespace removed.
            If an I18nData object is provided, returns it serialized for the frontend to translate.
        """
        if value is None:
            return None

        if isinstance(value, I18nData):
            # preserve the I18nData object for frontend translation
            return str(value)

        unindented_y = inspect.cleandoc(value)
        return unindented_y

    def example_payload(self) -> Any:
        return "# Hello!"

    def example_value(self) -> Any:
        return "# Hello!"

    def api_info(self) -> dict[str, Any]:
        return {"type": "string"}


=== File: gradio/components/model3d.py ===
"""gr.Model3D() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from gradio_client import handle_file
from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import FileData
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Model3D(Component):
    """
    Creates a component allows users to upload or view 3D Model files (.obj, .glb, .stl, .gltf, .splat, or .ply).

    Guides: how-to-use-3D-model-component
    """

    EVENTS = [Events.change, Events.upload, Events.edit, Events.clear]

    data_model = FileData

    def __init__(
        self,
        value: str | Callable | None = None,
        *,
        display_mode: Literal["solid", "point_cloud", "wireframe"] | None = None,
        clear_color: tuple[float, float, float, float] | None = None,
        camera_position: tuple[
            int | float | None, int | float | None, int | float | None
        ] = (
            None,
            None,
            None,
        ),
        zoom_speed: float = 1,
        pan_speed: float = 1,
        height: int | str | None = None,
        label: str | I18nData | None = None,
        show_label: bool | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            value: path to (.obj, .glb, .stl, .gltf, .splat, or .ply) file to show in model3D viewer. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            display_mode: the display mode of the 3D model in the scene. Can be "solid" (which renders the model as a solid object), "point_cloud", or "wireframe". For .splat, or .ply files, this parameter is ignored, as those files can only be rendered as solid objects.
            clear_color: background color of scene, should be a tuple of 4 floats between 0 and 1 representing RGBA values.
            camera_position: initial camera position of scene, provided as a tuple of `(alpha, beta, radius)`. Each value is optional. If provided, `alpha` and `beta` should be in degrees reflecting the angular position along the longitudinal and latitudinal axes, respectively. Radius corresponds to the distance from the center of the object to the camera.
            zoom_speed: the speed of zooming in and out of the scene when the cursor wheel is rotated or when screen is pinched on a mobile device. Should be a positive float, increase this value to make zooming faster, decrease to make it slower. Affects the wheelPrecision property of the camera.
            pan_speed: the speed of panning the scene when the cursor is dragged or when the screen is dragged on a mobile device. Should be a positive float, increase this value to make panning faster, decrease to make it slower. Affects the panSensibility property of the camera.
            height: The height of the model3D component, specified in pixels if a number is passed, or in CSS units if a string is passed.
            interactive: if True, will allow users to upload a file; if False, can only be used to display files. If not provided, this is inferred based on whether the component is used as an input or output.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            show_label: if True, will display label.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.display_mode = display_mode
        self.clear_color = clear_color or [0, 0, 0, 0]
        self.camera_position = camera_position
        self.height = height
        self.zoom_speed = zoom_speed
        self.pan_speed = pan_speed
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = (
            "a string path to a (.obj, .glb, .stl, .gltf, .splat, or .ply) file."
        )

    def preprocess(self, payload: FileData | None) -> str | None:
        """
        Parameters:
            payload: the uploaded file as an instance of `FileData`.
        Returns:
            Passes the uploaded file as a {str} filepath to the function.
        """
        if payload is None:
            return payload
        return payload.path

    def postprocess(self, value: str | Path | None) -> FileData | None:
        """
        Parameters:
            value: Expects function to return a {str} or {pathlib.Path} filepath of type (.obj, .glb, .stl, or .gltf)
        Returns:
            The uploaded file as an instance of `FileData`.
        """
        if value is None:
            return value
        return FileData(path=str(value), orig_name=Path(value).name)

    def process_example(self, value: str | Path | None) -> str:
        return Path(value).name if value else ""

    def example_payload(self):
        return handle_file(
            "https://raw.githubusercontent.com/gradio-app/gradio/main/demo/model3D/files/Fox.gltf"
        )

    def example_value(self):
        return "https://raw.githubusercontent.com/gradio-app/gradio/main/demo/model3D/files/Fox.gltf"


=== File: gradio/components/multimodal_textbox.py ===
"""gr.MultimodalTextbox() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast

import gradio_client.utils as client_utils
from gradio_client import handle_file
from gradio_client.documentation import document
from pydantic import Field
from typing_extensions import NotRequired

from gradio.components.base import Component, FormComponent
from gradio.data_classes import FileData, GradioModel
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


class MultimodalData(GradioModel):
    text: str
    files: list[FileData] = Field(default_factory=list)


class MultimodalPostprocess(TypedDict):
    text: str
    files: NotRequired[list[FileData]]


class MultimodalValue(TypedDict):
    text: NotRequired[str]
    files: NotRequired[list[str]]


@document()
class MultimodalTextbox(FormComponent):
    """
    Creates a textarea for users to enter string input or display string output and also allows for the uploading of multimedia files.

    Demos: chatbot_multimodal
    Guides: creating-a-chatbot
    """

    data_model = MultimodalData

    EVENTS = [
        Events.change,
        Events.input,
        Events.select,
        Events.submit,
        Events.focus,
        Events.blur,
        Events.stop,
    ]

    def __init__(
        self,
        value: str | dict[str, str | list] | Callable | None = None,
        *,
        sources: list[Literal["upload", "microphone"]]
        | Literal["upload", "microphone"]
        | None = None,
        file_types: list[str] | None = None,
        file_count: Literal["single", "multiple", "directory"] = "single",
        lines: int = 1,
        max_lines: int = 20,
        placeholder: str | None = None,
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        autofocus: bool = False,
        autoscroll: bool = True,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        text_align: Literal["left", "right"] | None = None,
        rtl: bool = False,
        submit_btn: str | bool | None = True,
        stop_btn: str | bool | None = False,
        max_plain_text_length: int = 1000,
    ):
        """
        Parameters:
            value: Default value to show in MultimodalTextbox. A string value, or a dictionary of the form {"text": "sample text", "files": [{path: "files/file.jpg", orig_name: "file.jpg", url: "http://image_url.jpg", size: 100}]}. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            sources: A list of sources permitted. "upload" creates a button where users can click to upload or drop files, "microphone" creates a microphone input. If None, defaults to ["upload"].
            file_count: if single, allows user to upload one file. If "multiple", user uploads multiple files. If "directory", user uploads all files in selected directory. Return type will be list for each file in case of "multiple" or "directory".
            file_types: List of file extensions or types of files to be uploaded (e.g. ['image', '.json', '.mp4']). "file" allows any file to be uploaded, "image" allows only image files to be uploaded, "audio" allows only audio files to be uploaded, "video" allows only video files to be uploaded, "text" allows only text files to be uploaded.
            lines: minimum number of line rows to provide in textarea.
            max_lines: maximum number of line rows to provide in textarea.
            placeholder: placeholder hint to provide behind textarea.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            autofocus: If True, will focus on the textbox when the page loads. Use this carefully, as it can cause usability issues for sighted and non-sighted users.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            text_align: How to align the text in the textbox, can be: "left", "right", or None (default). If None, the alignment is left if `rtl` is False, or right if `rtl` is True. Can only be changed if `type` is "text".
            rtl: If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.
            autoscroll: If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.
            submit_btn: If False, will not show a submit button. If a string, will use that string as the submit button text.
            stop_btn: If True, will show a stop button (useful for streaming demos). If a string, will use that string as the stop button text.
            max_plain_text_length: Maximum length of plain text in the textbox. If the text exceeds this length, the text will be pasted as a file. Default is 1000.
        """
        valid_sources: list[Literal["upload", "microphone"]] = ["upload", "microphone"]
        if sources is None:
            self.sources = ["upload"]
        elif isinstance(sources, str) and sources in valid_sources:
            self.sources = [sources]
        elif isinstance(sources, list):
            self.sources = sources
        else:
            raise ValueError(
                f"`sources` must be a list consisting of elements in {valid_sources}"
            )
        for source in self.sources:
            if source not in valid_sources:
                raise ValueError(
                    f"`sources` must a list consisting of elements in {valid_sources}"
                )
        self.file_types = file_types
        self.file_count = file_count
        if file_types is not None and not isinstance(file_types, list):
            raise ValueError(
                f"Parameter file_types must be a list. Received {file_types.__class__.__name__}"
            )
        self.lines = lines
        self.max_lines = max(lines, max_lines)
        self.placeholder = placeholder
        self.submit_btn = submit_btn
        self.stop_btn = stop_btn
        self.autofocus = autofocus
        self.autoscroll = autoscroll
        self.max_plain_text_length = max_plain_text_length

        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self.rtl = rtl
        self.text_align = text_align
        self._value_description = "a dictionary with structure {'text': string, 'files': list of string file paths}"

    def preprocess(self, payload: MultimodalData | None) -> MultimodalValue | None:
        """
        Parameters:
            payload: the text and list of file(s) entered in the multimodal textbox.
        Returns:
            Passes text value and list of file(s) as a {dict} into the function.
        """
        if payload is None:
            return None
        if self.file_types is not None:
            for f in payload.files:
                if not client_utils.is_valid_file(f.path, self.file_types):
                    raise Error(
                        f"Invalid file type: {f.mime_type}. Please upload a file that is one of these formats: {self.file_types}"
                    )
        return {
            "text": payload.text,
            "files": [f.path for f in payload.files],
        }

    def postprocess(self, value: MultimodalValue | str | None) -> MultimodalData | None:
        """
        Parameters:
            value: Expects a {dict} with "text" and "files", both optional. The files array is a list of file paths or URLs.
        Returns:
            The value to display in the multimodal textbox. Files information as a list of FileData objects.
        """
        if value is None:
            return None
        if not isinstance(value, (dict, str)):
            raise ValueError(
                f"MultimodalTextbox expects a string or a dictionary with optional keys 'text' and 'files'. Received {value.__class__.__name__}"
            )
        if isinstance(value, str):
            return MultimodalData(text=value, files=[])
        text = value.get("text", "")
        if "files" in value and isinstance(value["files"], list):
            files = [
                cast(FileData, file)
                if isinstance(file, FileData | dict)
                else FileData(
                    path=file,
                    orig_name=Path(file).name,
                    mime_type=client_utils.get_mimetype(file),
                )
                for file in value["files"]
            ]
        else:
            files = []
        if not isinstance(text, str):
            raise TypeError(
                f"Expected 'text' to be a string, but got {type(text).__name__}"
            )
        if not isinstance(files, list):
            raise TypeError(
                f"Expected 'files' to be a list, but got {type(files).__name__}"
            )
        return MultimodalData(text=text, files=files)

    def example_payload(self) -> Any:
        return {
            "text": "Describe this image",
            "files": [
                handle_file(
                    "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
                )
            ],
        }

    def example_value(self) -> Any:
        return {
            "text": "Describe this image",
            "files": [
                "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
            ],
        }


=== File: gradio/components/native_plot.py ===
from __future__ import annotations

import json
import warnings
from collections.abc import Callable, Sequence, Set
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
)

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import GradioModel
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    import pandas as pd

    from gradio.components import Timer


class PlotData(GradioModel):
    columns: list[str]
    data: list[list[Any]]
    datatypes: dict[str, Literal["quantitative", "nominal", "temporal"]]
    mark: str


class NativePlot(Component):
    """
    Creates a native Gradio plot component to display data from a pandas DataFrame. Supports interactivity and updates.

    Demos: native_plots
    """

    EVENTS = [Events.select, Events.double_click]

    def __init__(
        self,
        value: pd.DataFrame | Callable | None = None,
        x: str | None = None,
        y: str | None = None,
        *,
        color: str | None = None,
        title: str | None = None,
        x_title: str | None = None,
        y_title: str | None = None,
        color_title: str | None = None,
        x_bin: str | float | None = None,
        y_aggregate: Literal["sum", "mean", "median", "min", "max", "count"]
        | None = None,
        color_map: dict[str, str] | None = None,
        x_lim: list[float] | None = None,
        y_lim: list[float] | None = None,
        x_label_angle: float = 0,
        y_label_angle: float = 0,
        x_axis_labels_visible: bool = True,
        caption: str | I18nData | None = None,
        sort: Literal["x", "y", "-x", "-y"] | list[str] | None = None,
        tooltip: Literal["axis", "none", "all"] | list[str] = "axis",
        height: int | None = None,
        label: str | I18nData | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | Set[Component] | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        show_fullscreen_button: bool = False,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        **kwargs,
    ):
        """
        Parameters:
            value: The pandas dataframe containing the data to display in the plot.
            x: Column corresponding to the x axis. Column can be numeric, datetime, or string/category.
            y: Column corresponding to the y axis. Column must be numeric.
            color: Column corresponding to series, visualized by color. Column must be string/category.
            title: The title to display on top of the chart.
            x_title: The title given to the x axis. By default, uses the value of the x parameter.
            y_title: The title given to the y axis. By default, uses the value of the y parameter.
            color_title: The title given to the color legend. By default, uses the value of color parameter.
            x_bin: Grouping used to cluster x values. If x column is numeric, should be number to bin the x values. If x column is datetime, should be string such as "1h", "15m", "10s", using "s", "m", "h", "d" suffixes.
            y_aggregate: Aggregation function used to aggregate y values, used if x_bin is provided or x is a string/category. Must be one of "sum", "mean", "median", "min", "max".
            color_map: Mapping of series to color names or codes. For example, {"success": "green", "fail": "#FF8888"}.
            height: The height of the plot in pixels.
            x_lim: A tuple or list containing the limits for the x-axis, specified as [x_min, x_max]. If x column is datetime type, x_lim should be timestamps.
            y_lim: A tuple of list containing the limits for the y-axis, specified as [y_min, y_max].
            x_label_angle: The angle of the x-axis labels in degrees offset clockwise.
            y_label_angle: The angle of the y-axis labels in degrees offset clockwise.
            x_axis_labels_visible: Whether the x-axis labels should be visible. Can be hidden when many x-axis labels are present.
            caption: The (optional) caption to display below the plot.
            sort: The sorting order of the x values, if x column is type string/category. Can be "x", "y", "-x", "-y", or list of strings that represent the order of the categories.
            tooltip: The tooltip to display when hovering on a point. "axis" shows the values for the axis columns, "all" shows all column values, and "none" shows no tooltips. Can also provide a list of strings representing columns to show in the tooltip, which will be displayed along with axis values.
            height: The height of the plot in pixels.
            label: The (optional) label to display on the top left corner of the plot.
            show_label: Whether the label should be displayed.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            visible: Whether the plot should be visible.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            show_fullscreen_button: If True, will show a button to make plot visible in fullscreen mode.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.x = x
        self.y = y
        self.color = color
        self.title = title
        self.x_title = x_title
        self.y_title = y_title
        self.color_title = color_title
        self.x_bin = x_bin
        self.y_aggregate = y_aggregate
        self.color_map = color_map
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.x_label_angle = x_label_angle
        self.y_label_angle = y_label_angle
        self.x_axis_labels_visible = x_axis_labels_visible
        self.caption = caption
        self.sort = sort
        self.tooltip = tooltip
        self.height = height
        self.show_fullscreen_button = show_fullscreen_button

        if label is None and show_label is None:
            show_label = False
        super().__init__(
            value=value,
            label=label,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            every=every,
            inputs=inputs,
        )
        for key_, val in kwargs.items():
            if key_ == "color_legend_title":
                self.color_title = val
            if key_ in [
                "stroke_dash",
                "overlay_point",
                "x_label_angle",
                "y_label_angle",
                "interactive",
                "show_actions_button",
                "color_legend_title",
                "width",
            ]:
                warnings.warn(
                    f"Argument '{key_}' has been deprecated.", DeprecationWarning
                )

    def get_block_name(self) -> str:
        return "nativeplot"

    def get_mark(self) -> str:
        return "native"

    def preprocess(self, payload: PlotData | None) -> PlotData | None:
        """
        Parameters:
            payload: The data to display in a line plot.
        Returns:
            The data to display in a line plot.
        """
        return payload

    def postprocess(self, value: pd.DataFrame | dict | None) -> PlotData | None:
        """
        Parameters:
            value: Expects a pandas DataFrame containing the data to display in the line plot. The DataFrame should contain at least two columns, one for the x-axis (corresponding to this component's `x` argument) and one for the y-axis (corresponding to `y`).
        Returns:
            The data to display in a line plot, in the form of an AltairPlotData dataclass, which includes the plot information as a JSON string, as well as the type of plot (in this case, "line").
        """
        # if None or update
        if value is None or isinstance(value, dict):
            return value

        def get_simplified_type(dtype):
            import pandas as pd

            if pd.api.types.is_numeric_dtype(dtype):
                return "quantitative"
            elif pd.api.types.is_string_dtype(
                dtype
            ) or pd.api.types.is_categorical_dtype(dtype):
                return "nominal"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                return "temporal"
            else:
                raise ValueError(f"Unsupported data type: {dtype}")

        split_json = json.loads(value.to_json(orient="split", date_unit="ms"))
        datatypes = {
            col: get_simplified_type(value[col].dtype) for col in value.columns
        }
        return PlotData(
            columns=split_json["columns"],
            data=split_json["data"],
            datatypes=datatypes,
            mark=self.get_mark(),
        )

    def example_payload(self) -> Any:
        return None

    def example_value(self) -> Any:
        import pandas as pd

        return pd.DataFrame({self.x: [1, 2, 3], self.y: [4, 5, 6]})

    def api_info(self) -> dict[str, Any]:
        return {"type": {}, "description": "any valid json"}


@document()
class BarPlot(NativePlot):
    """
    Creates a bar plot component to display data from a pandas DataFrame.

    Demos: bar_plot_demo
    """

    def get_block_name(self) -> str:
        return "nativeplot"

    def get_mark(self) -> str:
        return "bar"


@document()
class LinePlot(NativePlot):
    """
    Creates a line plot component to display data from a pandas DataFrame.

    Demos: line_plot_demo
    """

    def get_block_name(self) -> str:
        return "nativeplot"

    def get_mark(self) -> str:
        return "line"


@document()
class ScatterPlot(NativePlot):
    """
    Creates a scatter plot component to display data from a pandas DataFrame.

    Demos: scatter_plot_demo
    """

    def get_block_name(self) -> str:
        return "nativeplot"

    def get_mark(self) -> str:
        return "point"


=== File: gradio/components/number.py ===
"""gr.Number() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio_client.documentation import document

from gradio.components.base import Component, FormComponent
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Number(FormComponent):
    """
    Creates a numeric field for user to enter numbers as input or display numeric output.

    Demos: tax_calculator, blocks_simple_squares
    """

    EVENTS = [Events.change, Events.input, Events.submit, Events.focus, Events.blur]

    def __init__(
        self,
        value: float | Callable | None = None,
        *,
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        precision: int | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
        step: float = 1,
    ):
        """
        Parameters:
            value: default value. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will be editable; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            precision: Precision to round input/output to. If set to 0, will round to nearest integer and convert type to int. If None, no rounding happens.
            minimum: Minimum value. Only applied when component is used as an input. If a user provides a smaller value, a gr.Error exception is raised by the backend.
            maximum: Maximum value. Only applied when component is used as an input. If a user provides a larger value, a gr.Error exception is raised by the backend.
            step: The interval between allowed numbers in the component. Can be used along with optional parameters `minimum` and `maximum` to create a range of legal values starting from `minimum` and incrementing according to this parameter.
        """
        self.precision = precision
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    @staticmethod
    def _round_to_precision(num: float | int, precision: int | None) -> float | int:
        """
        Round to a given precision.

        If precision is None, no rounding happens. If 0, num is converted to int.

        Parameters:
            num: Number to round.
            precision: Precision to round to.
        Returns:
            rounded number or the original number if precision is None
        """
        if precision is None:
            return num
        elif precision == 0:
            return int(round(num, precision))
        else:
            return round(num, precision)

    def preprocess(self, payload: float | None) -> float | int | None:
        """
        Parameters:
            payload: the field value.
        Returns:
            Passes field value as a `float` or `int` into the function, depending on `precision`.
        """
        if payload is None:
            return None
        elif self.minimum is not None and payload < self.minimum:
            raise Error(f"Value {payload} is less than minimum value {self.minimum}.")
        elif self.maximum is not None and payload > self.maximum:
            raise Error(
                f"Value {payload} is greater than maximum value {self.maximum}."
            )
        return self._round_to_precision(payload, self.precision)

    def postprocess(self, value: float | int | None) -> float | int | None:
        """
        Parameters:
            value: Expects an `int` or `float` returned from the function and sets field value to it.
        Returns:
            The (optionally rounded) field value as a `float` or `int` depending on `precision`.
        """
        if value is None:
            return None
        return self._round_to_precision(value, self.precision)

    def api_info(self) -> dict[str, str]:
        return {"type": "number"}

    def example_payload(self) -> Any:
        return 3

    def example_value(self) -> Any:
        return 3


=== File: gradio/components/paramviewer.py ===
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Literal, TypedDict

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.events import Events

if TYPE_CHECKING:
    from gradio.components import Timer


class Parameter(TypedDict):
    type: str
    description: str
    default: str | None


@document()
class ParamViewer(Component):
    """
    Displays an interactive table of parameters and their descriptions and default values with syntax highlighting. For each parameter,
    the user should provide a type (e.g. a `str`), a human-readable description, and a default value. As this component does not accept user input,
    it is rarely used as an input component. Internally, this component is used to display the parameters of components in the Custom
    Component Gallery (https://www.gradio.app/custom-components/gallery).
    """

    EVENTS = [
        Events.change,
        Events.upload,
    ]

    def __init__(
        self,
        value: Mapping[str, Parameter] | None = None,
        language: Literal["python", "typescript"] = "python",
        linkify: list[str] | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        header: str | None = "Parameters",
        anchor_links: bool | str = False,
    ):
        """
        Parameters:
            value: A dictionary of dictionaries. The key in the outer dictionary is the parameter name, while the inner dictionary has keys "type", "description", and "default" for each parameter. Markdown links are supported in "description".
            language: The language to display the code in. One of "python" or "typescript".
            linkify: A list of strings to linkify. If any of these strings is found in the description, it will be rendered as a link.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            header: The header to display above the table of parameters, also includes a toggle button that closes/opens all details at once. If None, no header will be displayed.
            anchor_links: If True, creates anchor links for each parameter that can be used to link directly to that parameter. If a string, creates anchor links with the given string as the prefix to prevent conflicts with other ParamViewer components.
        """
        self.value = value or {}
        self.language = language
        self.linkify = linkify
        self.header = header
        self.anchor_links = anchor_links
        super().__init__(
            every=every,
            inputs=inputs,
            value=value,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )

    def preprocess(self, payload: dict[str, Parameter]) -> dict[str, Parameter]:
        """
        Parameters:
            payload: A `dict[str, dict]`. The key in the outer dictionary is the parameter name, while the inner dictionary has keys "type", "description", and "default" for each parameter.
        Returns:
            (Rarely used) passes value as a `dict[str, dict]`. The key in the outer dictionary is the parameter name, while the inner dictionary has keys "type", "description", and "default" for each parameter.
        """
        return payload

    def postprocess(self, value: dict[str, Parameter]) -> dict[str, Parameter]:
        """
        Parameters:
            value: Expects value as a `dict[str, dict]`. The key in the outer dictionary is the parameter name, while the inner dictionary has keys "type", "description", and "default" for each parameter.
        Returns:
            The same value.
        """
        return value

    def example_payload(self):
        return {
            "array": {
                "type": "numpy",
                "description": "any valid json",
                "default": "None",
            }
        }

    def example_value(self):
        return {
            "array": {
                "type": "numpy",
                "description": "any valid json",
                "default": "None",
            }
        }

    def api_info(self):
        return {"type": {}, "description": "any valid json"}


=== File: gradio/components/plot.py ===
"""gr.Plot() component."""

from __future__ import annotations

import json
from collections.abc import Sequence
from types import ModuleType
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio import processing_utils, wasm_utils
from gradio.components.base import Component
from gradio.data_classes import GradioModel
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


class PlotData(GradioModel):
    type: Literal["altair", "bokeh", "plotly", "matplotlib"]
    plot: str


class AltairPlotData(PlotData):
    chart: Literal["bar", "line", "scatter"]
    type: Literal["altair"] = "altair"  # type: ignore


@document()
class Plot(Component):
    """
    Creates a plot component to display various kinds of plots (matplotlib, plotly, altair, or bokeh plots are supported). As this component does
    not accept user input, it is rarely used as an input component.

    Demos: blocks_kinematics, stock_forecast
    Guides: plot-component-for-maps
    """

    data_model = PlotData
    EVENTS = [Events.change]

    def __init__(
        self,
        value: Any | None = None,
        *,
        format: str = "png"
        if wasm_utils.IS_WASM
        else "webp",  # webp is a good default for speed (see #7845) but can't be used in Wasm because the the version of matplotlib used in Wasm (3.5.2 in the case of Pyodide 0.26.1) doesn't support it.
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):
        """
        Parameters:
            value: Optionally, supply a default plot object to display, must be a matplotlib, plotly, altair, or bokeh figure, or a callable. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            format: File format in which to send matplotlib plots to the front end, such as 'jpg' or 'png'.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.format = format
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def get_config(self):
        try:
            import bokeh  # type: ignore

            bokeh_version = bokeh.__version__
        except ImportError:
            bokeh_version = None

        config = super().get_config()
        config["bokeh_version"] = bokeh_version
        return config

    def preprocess(self, payload: PlotData | None) -> PlotData | None:
        """
        Parameters:
            payload: The data to display in the plot.
        Returns:
            (Rarely used) passes the data displayed in the plot as an PlotData dataclass, which includes the plot information as a JSON string, as well as the type of chart and the plotting library.
        """
        return payload

    def example_payload(self) -> Any:
        return None

    def example_value(self) -> Any:
        return None

    def postprocess(self, value: Any) -> PlotData | None:
        """
        Parameters:
            value: Expects plot data in one of these formats: a matplotlib.Figure, bokeh.Model, plotly.Figure, or altair.Chart object.
        Returns:
            PlotData: A dataclass containing the plot data as a JSON string, as well as the type of chart and the plotting library.
        """
        if value is None:
            return None
        if isinstance(value, PlotData):
            return value
        if isinstance(value, ModuleType) or "matplotlib" in value.__module__:
            dtype = "matplotlib"
            out_y = processing_utils.encode_plot_to_base64(value, self.format)
        elif "bokeh" in value.__module__:
            dtype = "bokeh"
            from bokeh.embed import json_item

            out_y = json.dumps(json_item(value))
        else:
            is_altair = "altair" in value.__module__
            dtype = "altair" if is_altair else "plotly"
            out_y = value.to_json()
        return PlotData(type=dtype, plot=out_y)


class AltairPlot:
    @staticmethod
    def create_legend(position, title):
        if position == "none":
            legend = None
        else:
            position = {"orient": position} if position else {}
            legend = {"title": title, **position}

        return legend

    @staticmethod
    def create_scale(limit):
        import altair as alt

        return alt.Scale(domain=limit) if limit else alt.Undefined


=== File: gradio/components/radio.py ===
"""gr.Radio() component."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component, FormComponent
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Radio(FormComponent):
    """
    Creates a set of (string or numeric type) radio buttons of which only one can be selected.

    Demos: sentence_builder, blocks_essay
    """

    EVENTS = [Events.select, Events.change, Events.input]

    def __init__(
        self,
        choices: Sequence[str | int | float | tuple[str, str | int | float]]
        | None = None,
        *,
        value: str | int | float | Callable | None = None,
        type: Literal["value", "index"] = "value",
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        rtl: bool = False,
    ):
        """
        Parameters:
            choices: A list of string or numeric options to select from. An option can also be a tuple of the form (name, value), where name is the displayed name of the radio button and value is the value to be passed to the function, or returned by the function.
            value: The option selected by default. If None, no option is selected by default. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            type: Type of value to be returned by component. "value" returns the string of the choice selected, "index" returns the index of the choice selected.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: Relative width compared to adjacent Components in a Row. For example, if Component A has scale=2, and Component B has scale=1, A will be twice as wide as B. Should be an integer.
            min_width: Minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: If True, choices in this radio group will be selectable; if False, selection will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            rtl: If True, the radio buttons will be displayed in right-to-left order. Default is False.
        """
        self.choices = (
            # Although we expect choices to be a list of tuples, it can be a list of tuples if the Gradio app
            # is loaded with gr.load() since Python tuples are converted to lists in JSON.
            [tuple(c) if isinstance(c, (tuple, list)) else (str(c), c) for c in choices]
            if choices
            else []
        )
        valid_types = ["value", "index"]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        self.rtl = rtl
        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = (
            f"one of {[c[1] if isinstance(c, tuple) else c for c in self.choices]}"
        )

    def example_payload(self) -> Any:
        return self.choices[0][1] if self.choices else None

    def example_value(self) -> Any:
        return self.choices[0][1] if self.choices else None

    def preprocess(self, payload: str | int | float | None) -> str | int | float | None:
        """
        Parameters:
            payload: Selected choice in the radio group
        Returns:
            Passes the value of the selected radio button as a `str | int | float`, or its index as an `int` into the function, depending on `type`.
        """
        if payload is None:
            return None

        choice_values = [value for _, value in self.choices]
        if payload not in choice_values:
            raise Error(
                f"Value: {payload!r} (type: {type(payload)}) is not in the list of choices: {choice_values}"
            )

        if self.type == "value":
            return payload
        elif self.type == "index":
            return choice_values.index(payload)
        else:
            raise ValueError(
                f"Unknown type: {self.type}. Please choose from: 'value', 'index'."
            )

    def postprocess(self, value: str | int | float | None) -> str | int | float | None:
        """
        Parameters:
            value: Expects a `str | int | float` corresponding to the value of the radio button to be selected
        Returns:
            The same value
        """
        return value

    def api_info(self) -> dict[str, Any]:
        return {
            "enum": [c[1] for c in self.choices],
            "title": "Radio",
            "type": "string",
        }


=== File: gradio/components/scatter_plot.py ===
"""gr.ScatterPlot() component."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.components.plot import AltairPlot, AltairPlotData, Plot
from gradio.i18n import I18nData

if TYPE_CHECKING:
    import pandas as pd

    from gradio.components import Timer


@document()
class ScatterPlot(Plot):
    """
    Creates a scatter plot component to display data from a pandas DataFrame (as output). As this component does
    not accept user input, it is rarely used as an input component.

    Guides: creating-a-dashboard-from-bigquery-data
    """

    data_model = AltairPlotData

    def __init__(
        self,
        value: pd.DataFrame | Callable | None = None,
        x: str | None = None,
        y: str | None = None,
        *,
        color: str | None = None,
        size: str | None = None,
        shape: str | None = None,
        title: str | None = None,
        tooltip: list[str] | str | None = None,
        x_title: str | None = None,
        y_title: str | None = None,
        x_label_angle: float | None = None,
        y_label_angle: float | None = None,
        color_legend_title: str | None = None,
        size_legend_title: str | None = None,
        shape_legend_title: str | None = None,
        color_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        size_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        shape_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        height: int | None = None,
        width: int | None = None,
        x_lim: list[int | float] | None = None,
        y_lim: list[int | float] | None = None,
        caption: str | None = None,
        interactive: bool | None = True,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        show_actions_button: bool = False,
    ):
        """
        Parameters:
            value: The pandas dataframe containing the data to display in a scatter plot, or a callable. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            x: Column corresponding to the x axis.
            y: Column corresponding to the y axis.
            color: The column to determine the point color. If the column contains numeric data, gradio will interpolate the column data so that small values correspond to light colors and large values correspond to dark values.
            size: The column used to determine the point size. Should contain numeric data so that gradio can map the data to the point size.
            shape: The column used to determine the point shape. Should contain categorical data. Gradio will map each unique value to a different shape.
            title: The title to display on top of the chart.
            tooltip: The column (or list of columns) to display on the tooltip when a user hovers a point on the plot.
            x_title: The title given to the x-axis. By default, uses the value of the x parameter.
            y_title: The title given to the y-axis. By default, uses the value of the y parameter.
            x_label_angle:  The angle for the x axis labels rotation. Positive values are clockwise, and negative values are counter-clockwise.
            y_label_angle:  The angle for the y axis labels rotation. Positive values are clockwise, and negative values are counter-clockwise.
            color_legend_title: The title given to the color legend. By default, uses the value of color parameter.
            size_legend_title: The title given to the size legend. By default, uses the value of the size parameter.
            shape_legend_title: The title given to the shape legend. By default, uses the value of the shape parameter.
            color_legend_position: The position of the color legend. If the string value 'none' is passed, this legend is omitted. For other valid position values see: https://vega.github.io/vega/docs/legends/#orientation.
            size_legend_position: The position of the size legend. If the string value 'none' is passed, this legend is omitted. For other valid position values see: https://vega.github.io/vega/docs/legends/#orientation.
            shape_legend_position: The position of the shape legend. If the string value 'none' is passed, this legend is omitted. For other valid position values see: https://vega.github.io/vega/docs/legends/#orientation.
            height: The height of the plot in pixels.
            width: The width of the plot in pixels. If None, expands to fit.
            x_lim: A tuple or list containing the limits for the x-axis, specified as [x_min, x_max].
            y_lim: A tuple of list containing the limits for the y-axis, specified as [y_min, y_max].
            caption: The (optional) caption to display below the plot.
            interactive: Whether users should be able to interact with the plot by panning or zooming with their mouse or trackpad.
            label: The (optional) label to display on the top left corner of the plot.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: Whether the label should be displayed.
            visible: Whether the plot should be visible.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            show_actions_button: Whether to show the actions button on the top right corner of the plot.
        """
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.shape = shape
        self.tooltip = tooltip
        self.title = title
        self.x_title = x_title
        self.y_title = y_title
        self.x_label_angle = x_label_angle
        self.y_label_angle = y_label_angle
        self.color_legend_title = color_legend_title
        self.color_legend_position = color_legend_position
        self.size_legend_title = size_legend_title
        self.size_legend_position = size_legend_position
        self.shape_legend_title = shape_legend_title
        self.shape_legend_position = shape_legend_position
        self.caption = caption
        self.interactive_chart = interactive
        if isinstance(width, str):
            width = None
            warnings.warn(
                "Width should be an integer, not a string. Setting width to None."
            )
        if isinstance(height, str):
            warnings.warn(
                "Height should be an integer, not a string. Setting height to None."
            )
            height = None
        self.width = width
        self.height = height
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.show_actions_button = show_actions_button
        if label is None and show_label is None:
            show_label = False
        super().__init__(
            value=value,
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )

    def get_block_name(self) -> str:
        return "plot"

    @staticmethod
    def create_plot(
        value: pd.DataFrame,
        x: str,
        y: str,
        color: str | None = None,
        size: str | None = None,
        shape: str | None = None,
        title: str | None = None,
        tooltip: list[str] | str | None = None,
        x_title: str | None = None,
        y_title: str | None = None,
        x_label_angle: float | None = None,
        y_label_angle: float | None = None,
        color_legend_title: str | None = None,
        size_legend_title: str | None = None,
        shape_legend_title: str | None = None,
        color_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        size_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        shape_legend_position: Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "none",
        ]
        | None = None,
        height: int | None = None,
        width: int | None = None,
        x_lim: list[int | float] | None = None,
        y_lim: list[int | float] | None = None,
        interactive: bool | None = True,
    ):
        """Helper for creating the scatter plot."""
        import altair as alt
        from pandas.api.types import is_numeric_dtype

        interactive = True if interactive is None else interactive
        encodings = {
            "x": alt.X(
                x,  # type: ignore
                title=x_title or x,  # type: ignore
                scale=AltairPlot.create_scale(x_lim),  # type: ignore
                axis=alt.Axis(labelAngle=x_label_angle)
                if x_label_angle is not None
                else alt.Axis(),
            ),  # ignore: type
            "y": alt.Y(
                y,  # type: ignore
                title=y_title or y,  # type: ignore
                scale=AltairPlot.create_scale(y_lim),  # type: ignore
                axis=alt.Axis(labelAngle=y_label_angle)
                if y_label_angle is not None
                else alt.Axis(),
            ),
        }
        properties = {}
        if title:
            properties["title"] = title
        if height:
            properties["height"] = height
        if width:
            properties["width"] = width
        if color:
            if is_numeric_dtype(value[color]):
                domain = [value[color].min(), value[color].max()]
                range_ = [0, 1]
                type_ = "quantitative"
            else:
                domain = value[color].unique().tolist()
                range_ = list(range(len(domain)))
                type_ = "nominal"

            color_legend_position = color_legend_position or "bottom"
            encodings["color"] = {
                "field": color,
                "type": type_,
                "legend": AltairPlot.create_legend(
                    position=color_legend_position, title=color_legend_title
                ),
                "scale": {"domain": domain, "range": range_},
            }
        if tooltip:
            encodings["tooltip"] = tooltip
        if size:
            encodings["size"] = {
                "field": size,
                "type": "quantitative" if is_numeric_dtype(value[size]) else "nominal",
                "legend": AltairPlot.create_legend(
                    position=size_legend_position, title=size_legend_title
                ),
            }
        if shape:
            encodings["shape"] = {
                "field": shape,
                "type": "quantitative" if is_numeric_dtype(value[shape]) else "nominal",
                "legend": AltairPlot.create_legend(
                    position=shape_legend_position, title=shape_legend_title
                ),
            }
        chart = (
            alt.Chart(value)  # type: ignore
            .mark_point(clip=True)  # type: ignore
            .encode(**encodings)
            .properties(background="transparent", **properties)
        )
        if interactive:
            chart = chart.interactive()

        return chart

    def preprocess(self, payload: AltairPlotData | None) -> AltairPlotData | None:
        """
        Parameters:
            payload: The data to display in a scatter plot.
        Returns:
            (Rarely used) passes the data displayed in the scatter plot as an AltairPlotData dataclass, which includes the plot information as a JSON string, as well as the type of plot (in this case, "scatter").
        """
        return payload

    def postprocess(
        self, value: pd.DataFrame | dict | None
    ) -> AltairPlotData | dict | None:
        """
        Parameters:
            value: Expects a pandas DataFrame containing the data to display in the scatter plot. The DataFrame should contain at least two columns, one for the x-axis (corresponding to this component's `x` argument) and one for the y-axis (corresponding to `y`).
        Returns:
            The data to display in a scatter plot, in the form of an AltairPlotData dataclass, which includes the plot information as a JSON string, as well as the type of plot (in this case, "scatter").
        """
        # if None or update
        if value is None or isinstance(value, dict):
            return value
        if self.x is None or self.y is None:
            raise ValueError("No value provided for required parameters `x` and `y`.")
        chart = self.create_plot(
            value=value,
            x=self.x,
            y=self.y,
            color=self.color,
            size=self.size,
            shape=self.shape,
            title=self.title,
            tooltip=self.tooltip,
            x_title=self.x_title,
            y_title=self.y_title,
            x_label_angle=self.x_label_angle,
            y_label_angle=self.y_label_angle,
            color_legend_title=self.color_legend_title,
            size_legend_title=self.size_legend_title,
            shape_legend_title=self.size_legend_title,
            color_legend_position=self.color_legend_position,  # type: ignore
            size_legend_position=self.size_legend_position,  # type: ignore
            shape_legend_position=self.shape_legend_position,  # type: ignore
            interactive=self.interactive_chart,
            height=self.height,
            width=self.width,
            x_lim=self.x_lim,
            y_lim=self.y_lim,
        )

        return AltairPlotData(type="altair", plot=chart.to_json(), chart="scatter")

    def example_payload(self) -> Any:
        return None

    def example_value(self) -> Any:
        import pandas as pd

        return pd.DataFrame({self.x: [1, 2, 3], self.y: [4, 5, 6]})


=== File: gradio/components/slider.py ===
"""gr.Slider() component."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from gradio_client.documentation import document

from gradio.components.base import Component, FormComponent
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Slider(FormComponent):
    """
    Creates a slider that ranges from {minimum} to {maximum} with a step size of {step}.

    Demos: sentence_builder, slider_release, interface_random_slider, blocks_random_slider
    Guides: create-your-own-friends-with-a-gan
    """

    EVENTS = [Events.change, Events.input, Events.release]

    def __init__(
        self,
        minimum: float = 0,
        maximum: float = 100,
        value: float | Callable | None = None,
        *,
        step: float | None = None,
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        randomize: bool = False,
        show_reset_button: bool = True,
    ):
        """
        Parameters:
            minimum: minimum value for slider.
            maximum: maximum value for slider.
            value: default value for slider. If a function is provided, the function will be called each time the app loads to set the initial value of this component. Ignored if randomized=True.
            step: increment between slider values.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, slider will be adjustable; if False, adjusting will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            randomize: If True, the value of the slider when the app loads is taken uniformly at random from the range given by the minimum and maximum.
            show_reset_button: if False, will hide button to reset slider to default value.
        """
        self.minimum = minimum
        self.maximum = maximum
        if step is None:
            difference = maximum - minimum
            power = math.floor(math.log10(difference) - 2)
            self.step = 10**power
        else:
            self.step = step
        self.show_reset_button = show_reset_button
        if randomize:
            value = self.get_random_value
        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def api_info(self) -> dict[str, Any]:
        return {
            "type": "number",
            "description": f"numeric value between {self.minimum} and {self.maximum}",
        }

    def example_payload(self) -> Any:
        return self.minimum

    def example_value(self) -> Any:
        return self.minimum

    def get_random_value(self):
        n_steps = int((self.maximum - self.minimum) / self.step)
        step = random.randint(0, n_steps)
        value = self.minimum + step * self.step
        # Round to number of decimals in step so that UI doesn't display long decimals
        n_decimals = max(str(self.step)[::-1].find("."), 0)
        if n_decimals:
            value = round(value, n_decimals)
        return value

    def postprocess(self, value: float | None) -> float:
        """
        Parameters:
            value: Expects an {int} or {float} returned from function and sets slider value to it as long as it is within range (otherwise, sets to minimum value).
        Returns:
            The value of the slider within the range.
        """
        return self.minimum if value is None else value

    def preprocess(self, payload: float) -> float:
        """
        Parameters:
            payload: slider value
        Returns:
            Passes slider value as a {float} into the function.
        """
        return payload


=== File: gradio/components/state.py ===
"""gr.State() component."""

from __future__ import annotations

import math
from collections.abc import Callable
from copy import deepcopy
from typing import Any

from gradio_client.documentation import document

from gradio.components.base import FormComponent
from gradio.events import Events


@document()
class State(FormComponent):
    EVENTS = [Events.change]
    """
    Special hidden component that stores session state across runs of the demo by the
    same user. Can attach .change listeners that trigger when the state changes.
    Demos: interface_state, blocks_simple_squares, state_cleanup
    Guides: real-time-speech-recognition
    """

    allow_string_shortcut = False

    def __init__(
        self,
        value: Any = None,
        render: bool = True,
        *,
        time_to_live: int | float | None = None,
        delete_callback: Callable[[Any], None] | None = None,
    ):
        """
        Parameters:
            value: the initial value (of arbitrary type) of the state. The provided argument is deepcopied. If a callable is provided, the function will be called whenever the app loads to set the initial value of the state.
            render: should always be True, is included for consistency with other components.
            time_to_live: The number of seconds the state should be stored for after it is created or updated. If None, the state will be stored indefinitely. Gradio automatically deletes state variables after a user closes the browser tab or refreshes the page, so this is useful for clearing state for potentially long running sessions.
            delete_callback: A function that is called when the state is deleted. The function should take the state value as an argument.
        """
        self.time_to_live = self.time_to_live = (
            math.inf if time_to_live is None else time_to_live
        )
        self.delete_callback = delete_callback or (lambda a: None)  # noqa: ARG005
        try:
            value = deepcopy(value)
        except TypeError as err:
            raise TypeError(
                f"The initial value of `gr.State` must be able to be deepcopied. The initial value of type {type(value)} cannot be deepcopied."
            ) from err
        super().__init__(value=value, render=render)
        self.value = value

    @property
    def stateful(self) -> bool:
        return True

    def preprocess(self, payload: Any) -> Any:
        """
        Parameters:
            payload: Value
        Returns:
            Passes a value of arbitrary type through.
        """
        return payload

    def postprocess(self, value: Any) -> Any:
        """
        Parameters:
            value: Expects a value of arbitrary type, as long as it can be deepcopied.
        Returns:
            Passes a value of arbitrary type through.
        """
        return value

    def api_info(self) -> dict[str, Any]:
        return {"type": {}, "description": "any valid json"}

    def example_payload(self) -> Any:
        return None

    def example_value(self) -> Any:
        return None

    @property
    def skip_api(self):
        return True

    def get_config(self):
        config = super().get_config()
        del config["value"]
        return config


=== File: gradio/components/textbox.py ===
"""gr.Textbox() component."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Literal

from gradio_client.documentation import document

from gradio.components.base import Component, FormComponent
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class Textbox(FormComponent):
    """
    Creates a textarea for user to enter string input or display string output.

    Demos: hello_world, diff_texts, sentence_builder
    Guides: creating-a-chatbot, real-time-speech-recognition
    """

    EVENTS = [
        Events.change,
        Events.input,
        Events.select,
        Events.submit,
        Events.focus,
        Events.blur,
        Events.stop,
        Events.copy,
    ]

    def __init__(
        self,
        value: str | I18nData | Callable | None = None,
        *,
        type: Literal["text", "password", "email"] = "text",
        lines: int = 1,
        max_lines: int | None = None,
        placeholder: str | I18nData | None = None,
        label: str | I18nData | None = None,
        info: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        autofocus: bool = False,
        autoscroll: bool = True,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        text_align: Literal["left", "right"] | None = None,
        rtl: bool = False,
        show_copy_button: bool = False,
        max_length: int | None = None,
        submit_btn: str | bool | None = False,
        stop_btn: str | bool | None = False,
    ):
        """
        Parameters:
            value: text to show in textbox. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            type: The type of textbox. One of: 'text' (which allows users to enter any text), 'password' (which masks text entered by the user), 'email' (which suggests email input to the browser). For "password" and "email" types, `lines` must be 1 and `max_lines` must be None or 1.
            lines: minimum number of line rows to provide in textarea.
            max_lines: maximum number of line rows to provide in textarea. Must be at least `lines`. If not provided, the maximum number of lines is max(lines, 20) for "text" type, and 1 for "password" and "email" types.
            placeholder: placeholder hint to provide behind textarea.
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            info: additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.
            every: continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display the label. If False, the copy button is hidden as well as well as the label.
            container: if True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            autofocus: If True, will focus on the textbox when the page loads. Use this carefully, as it can cause usability issues for sighted and non-sighted users.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            text_align: How to align the text in the textbox, can be: "left", "right", or None (default). If None, the alignment is left if `rtl` is False, or right if `rtl` is True. Can only be changed if `type` is "text".
            rtl: If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.
            show_copy_button: If True, includes a copy button to copy the text in the textbox. Only applies if show_label is True.
            autoscroll: If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.
            max_length: maximum number of characters (including newlines) allowed in the textbox. If None, there is no maximum length.
            submit_btn: If False, will not show a submit button. If True, will show a submit button with an icon. If a string, will use that string as the submit button text. When the submit button is shown, the border of the textbox will be removed, which is useful for creating a chat interface.
        """
        if type not in ["text", "password", "email"]:
            raise ValueError('`type` must be one of "text", "password", or "email".')
        if type in ["password", "email"]:
            if lines != 1:
                warnings.warn(
                    "The `lines` parameter must be 1 for `type` of 'password' or 'email'. Setting `lines` to 1."
                )
                lines = 1
            if max_lines not in [None, 1]:
                warnings.warn(
                    "The `max_lines` parameter must be None or 1 for `type` of 'password' or 'email'. Setting `max_lines` to 1."
                )
                max_lines = 1

        self.lines = lines
        self.max_lines = max_lines
        self.placeholder = placeholder
        self.show_copy_button = show_copy_button
        self.submit_btn = submit_btn
        self.stop_btn = stop_btn
        self.autofocus = autofocus
        self.autoscroll = autoscroll

        super().__init__(
            label=label,
            info=info,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self.type = type
        self.rtl = rtl
        self.text_align = text_align
        self.max_length = max_length

    def preprocess(self, payload: str | None) -> str | None:
        """
        Parameters:
            payload: the text entered in the textarea.
        Returns:
            Passes text value as a {str} into the function.
        """
        return None if payload is None else str(payload)

    def postprocess(self, value: str | None) -> str | None:
        """
        Parameters:
            value: Expects a {str} returned from function and sets textarea value to it.
        Returns:
            The value to display in the textarea.
        """
        return None if value is None else str(value)

    def api_info(self) -> dict[str, Any]:
        return {"type": "string"}

    def example_payload(self) -> Any:
        return "Hello!!"

    def example_value(self) -> Any:
        return "Hello!!"


=== File: gradio/components/timer.py ===
"""gr.Timer() component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gradio_client.documentation import document

from gradio.components.base import FormComponent
from gradio.events import Events

if TYPE_CHECKING:
    pass


@document()
class Timer(FormComponent):
    """
    Special component that ticks at regular intervals when active. It is not visible, and only used to trigger events at a regular interval through the `tick` event listener.
    """

    EVENTS = [
        Events.tick,
    ]

    def __init__(
        self,
        value: float = 1,
        *,
        active: bool = True,
        render: bool = True,
    ):
        """
        Parameters:
            value: Interval in seconds between each tick.
            active: Whether the timer is active.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
        """
        self.active = active
        super().__init__(value=value, render=render)

    def preprocess(self, payload: float | None) -> float | None:
        """
        Parameters:
            payload: The interval of the timer as a float or None.
        Returns:
            The interval of the timer as a float.
        """
        return payload

    def postprocess(self, value: float | None) -> float | None:
        """
        Parameters:
            value: The interval of the timer as a float or None.
        Returns:
            The interval of the timer as a float.
        """
        return value

    def api_info(self) -> dict:
        return {"type": "number"}

    def example_payload(self):
        return 1

    def example_value(self):
        return 1


=== File: gradio/components/upload_button.py ===
"""gr.UploadButton() component."""

from __future__ import annotations

import tempfile
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import gradio_client.utils as client_utils
from gradio_client import handle_file
from gradio_client.documentation import document

from gradio import processing_utils
from gradio.components.base import Component
from gradio.data_classes import FileData, ListFiles
from gradio.events import Events
from gradio.exceptions import Error
from gradio.i18n import I18nData
from gradio.utils import NamedString

if TYPE_CHECKING:
    from gradio.components import Timer


@document()
class UploadButton(Component):
    """
    Used to create an upload button, when clicked allows a user to upload files that satisfy the specified file type or generic files (if file_type not set).

    Demos: upload_and_download, upload_button
    """

    EVENTS = [Events.click, Events.upload]

    def __init__(
        self,
        label: str = "Upload a File",
        value: str | I18nData | list[str] | Callable | None = None,
        *,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        variant: Literal["primary", "secondary", "stop"] = "secondary",
        visible: bool = True,
        size: Literal["sm", "md", "lg"] = "lg",
        icon: str | None = None,
        scale: int | None = None,
        min_width: int | None = None,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        type: Literal["filepath", "binary"] = "filepath",
        file_count: Literal["single", "multiple", "directory"] = "single",
        file_types: list[str] | None = None,
    ):
        """
        Parameters:
            label: Text to display on the button. Defaults to "Upload a File".
            value: File or list of files to upload by default.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            variant: 'primary' for main call-to-action, 'secondary' for a more subdued style, 'stop' for a stop button.
            visible: If False, component will be hidden.
            size: size of the button. Can be "sm", "md", or "lg".
            icon: URL or path to the icon file to display within the button. If None, no icon will be displayed.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: If False, the UploadButton will be in a disabled state.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            type: Type of value to be returned by component. "file" returns a temporary file object with the same base name as the uploaded file, whose full path can be retrieved by file_obj.name, "binary" returns an bytes object.
            file_count: if single, allows user to upload one file. If "multiple", user uploads multiple files. If "directory", user uploads all files in selected directory. Return type will be list for each file in case of "multiple" or "directory".
            file_types: List of type of files to be uploaded. "file" allows any file to be uploaded, "image" allows only image files to be uploaded, "audio" allows only audio files to be uploaded, "video" allows only video files to be uploaded, "text" allows only text files to be uploaded.
        """
        valid_types = [
            "filepath",
            "binary",
        ]
        if type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.type = type
        self.file_count = file_count
        if file_count == "directory" and file_types is not None:
            warnings.warn(
                "The `file_types` parameter is ignored when `file_count` is 'directory'."
            )
        if file_types is not None and not isinstance(file_types, list):
            raise ValueError(
                f"Parameter file_types must be a list. Received {file_types.__class__.__name__}"
            )
        if self.file_count in ["multiple", "directory"]:
            self.data_model = ListFiles
        else:
            self.data_model = FileData
        self.size = size
        self.file_types = file_types
        self.label = label
        self.variant = variant
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
        )
        self.icon = self.serve_static_file(icon)

    def api_info(self) -> dict[str, list[str]]:
        if self.file_count == "single":
            return FileData.model_json_schema()
        else:
            return ListFiles.model_json_schema()

    def example_payload(self) -> Any:
        if self.file_count == "single":
            return handle_file(
                "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
            )
        else:
            return [
                handle_file(
                    "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
                )
            ]

    def example_value(self) -> Any:
        if self.file_count == "single":
            return "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
        else:
            return [
                "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf"
            ]

    def _process_single_file(self, f: FileData) -> bytes | NamedString:
        file_name = f.path
        if self.type == "filepath":
            if self.file_types and not client_utils.is_valid_file(
                file_name, self.file_types
            ):
                raise Error(
                    f"Invalid file type. Please upload a file that is one of these formats: {self.file_types}"
                )
            file = tempfile.NamedTemporaryFile(delete=False, dir=self.GRADIO_CACHE)
            file.name = file_name
            return NamedString(file_name)
        elif self.type == "binary":
            with open(file_name, "rb") as file_data:
                return file_data.read()
        else:
            raise ValueError(
                "Unknown type: "
                + str(type)
                + ". Please choose from: 'filepath', 'binary'."
            )

    def preprocess(
        self, payload: ListFiles | FileData | None
    ) -> bytes | str | list[bytes] | list[str] | None:
        """
        Parameters:
            payload: File information as a FileData object, or a list of FileData objects.
        Returns:
            Passes the file as a `str` or `bytes` object, or a list of `str` or list of `bytes` objects, depending on `type` and `file_count`.
        """
        if payload is None:
            return None
        if self.file_count == "single":
            if isinstance(payload, ListFiles):
                return self._process_single_file(payload[0])
            return self._process_single_file(payload)

        if isinstance(payload, ListFiles):
            return [self._process_single_file(f) for f in payload]  # type: ignore
        return [self._process_single_file(payload)]  # type: ignore

    def _download_files(self, value: str | list[str]) -> str | list[str]:
        downloaded_files = []
        if isinstance(value, list):
            for file in value:
                if client_utils.is_http_url_like(file):
                    downloaded_file = processing_utils.save_url_to_cache(
                        file, self.GRADIO_CACHE
                    )
                    downloaded_files.append(downloaded_file)
                else:
                    downloaded_files.append(file)
            return downloaded_files
        if client_utils.is_http_url_like(value):
            downloaded_file = processing_utils.save_url_to_cache(
                value, self.GRADIO_CACHE
            )
            return downloaded_file
        else:
            return value

    def postprocess(self, value: str | list[str] | None) -> ListFiles | FileData | None:
        """
        Parameters:
            value: Expects a `str` filepath or URL, or a `list[str]` of filepaths/URLs.
        Returns:
            File information as a FileData object, or a list of FileData objects.
        """
        if value is None:
            return None
        value = self._download_files(value)
        if isinstance(value, list):
            return ListFiles(
                root=[
                    FileData(
                        path=file,
                        orig_name=Path(file).name,
                        size=Path(file).stat().st_size,
                    )
                    for file in value
                ]
            )
        else:
            return FileData(
                path=value,
                orig_name=Path(value).name,
                size=Path(value).stat().st_size,
            )

    @property
    def skip_api(self):
        return False


=== File: gradio/components/video.py ===
"""gr.Video() component."""

from __future__ import annotations

import asyncio
import json
import subprocess
import tempfile
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional

from gradio_client import handle_file
from gradio_client import utils as client_utils
from gradio_client.documentation import document

import gradio as gr
from gradio import processing_utils, utils, wasm_utils
from gradio.components.base import Component, StreamingOutput
from gradio.components.image_editor import WebcamOptions
from gradio.data_classes import FileData, GradioModel, MediaStreamChunk
from gradio.events import Events
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer


if not wasm_utils.IS_WASM:
    # TODO: Support ffmpeg on Wasm
    from ffmpy import FFmpeg


class VideoData(GradioModel):
    video: FileData
    subtitles: Optional[FileData] = None


@document()
class Video(StreamingOutput, Component):
    """
    Creates a video component that can be used to upload/record videos (as an input) or display videos (as an output).
    For the video to be playable in the browser it must have a compatible container and codec combination. Allowed
    combinations are .mp4 with h264 codec, .ogg with theora codec, and .webm with vp9 codec. If the component detects
    that the output video would not be playable in the browser it will attempt to convert it to a playable mp4 video.
    If the conversion fails, the original video is returned.

    Demos: video_identity_2
    """

    data_model = VideoData

    EVENTS = [
        Events.change,
        Events.clear,
        Events.start_recording,
        Events.stop_recording,
        Events.stop,
        Events.play,
        Events.pause,
        Events.end,
        Events.upload,
    ]

    def __init__(
        self,
        value: (
            str | Path | tuple[str | Path, str | Path | None] | Callable | None
        ) = None,
        *,
        format: str | None = None,
        sources: (
            list[Literal["upload", "webcam"]] | Literal["upload", "webcam"] | None
        ) = None,
        height: int | str | None = None,
        width: int | str | None = None,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        mirror_webcam: bool | None = None,
        webcam_options: WebcamOptions | None = None,
        include_audio: bool | None = None,
        autoplay: bool = False,
        show_share_button: bool | None = None,
        show_download_button: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        loop: bool = False,
        streaming: bool = False,
        watermark: str | Path | None = None,
        webcam_constraints: dict[str, Any] | None = None,
    ):
        """
        Parameters:
            value: path or URL for the default value that Video component is going to take. Can also be a tuple consisting of (video filepath, subtitle filepath). If a subtitle file is provided, it should be of type .srt or .vtt. Or can be callable, in which case the function will be called whenever the app loads to set the initial value of the component.
            format: the file extension with which to save video, such as 'avi' or 'mp4'. This parameter applies both when this component is used as an input to determine which file format to convert user-provided video to, and when this component is used as an output to determine the format of video returned to the user. If None, no file format conversion is done and the video is kept as is. Use 'mp4' to ensure browser playability.
            sources: list of sources permitted for video. "upload" creates a box where user can drop a video file, "webcam" allows user to record a video from their webcam. If None, defaults to both ["upload, "webcam"].
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed video file, but will affect the displayed video.
            width: The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed video file, but will affect the displayed video.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            container: if True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will allow users to upload a video; if False, can only be used to display videos. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: if False, component will be hidden.
            elem_id: an optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: an optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: if False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            include_audio: whether the component should record/retain the audio track for a video. By default, audio is excluded for webcam videos and included for uploaded videos.
            autoplay: whether to automatically play the video when the component is used as an output. Note: browsers will not autoplay video files if the user has not interacted with the page yet.
            show_share_button: if True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            show_download_button: if True, will show a download icon in the corner of the component that allows user to download the output. If False, icon does not appear. By default, it will be True for output components and False for input components.
            min_length: the minimum length of video (in seconds) that the user can pass into the prediction function. If None, there is no minimum length.
            max_length: the maximum length of video (in seconds) that the user can pass into the prediction function. If None, there is no maximum length.
            loop: if True, the video will loop when it reaches the end and continue playing from the beginning.
            streaming: when used set as an output, takes video chunks yielded from the backend and combines them into one streaming video output. Each chunk should be a video file with a .ts extension using an h.264 encoding. Mp4 files are also accepted but they will be converted to h.264 encoding.
            watermark: an image file to be included as a watermark on the video. The image is not scaled and is displayed on the bottom right of the video. Valid formats for the image are: jpeg, png.
            webcam_options: A `gr.WebcamOptions` instance that allows developers to specify custom media constraints for the webcam stream. This parameter provides flexibility to control the video stream's properties, such as resolution and front or rear camera on mobile devices. See $demo/webcam_constraints
        """
        valid_sources: list[Literal["upload", "webcam"]] = ["upload", "webcam"]
        if sources is None:
            self.sources = valid_sources
        elif isinstance(sources, str) and sources in valid_sources:
            self.sources = [sources]
        elif isinstance(sources, list) and all(s in valid_sources for s in sources):
            self.sources = sources
        else:
            raise ValueError(
                f"`sources` must be a list consisting of elements in {valid_sources}"
            )
        for source in self.sources:
            if source not in valid_sources:
                raise ValueError(
                    f"`sources` must a list consisting of elements in {valid_sources}"
                )
        self.format = format
        self.autoplay = autoplay
        self.height = height
        self.width = width
        self.loop = loop
        self.webcam_options = (
            webcam_options if webcam_options is not None else WebcamOptions()
        )

        if mirror_webcam is not None:
            warnings.warn(
                "The `mirror_webcam` parameter is deprecated. Please use the `webcam_options` parameter with a `gr.WebcamOptions` instance instead."
            )
            self.webcam_options.mirror = mirror_webcam

        if webcam_constraints is not None:
            self.webcam_options.constraints = webcam_constraints

        self.include_audio = (
            include_audio if include_audio is not None else "upload" in self.sources
        )
        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        self.show_download_button = show_download_button
        self.min_length = min_length
        self.max_length = max_length
        self.streaming = streaming
        self.watermark = watermark
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = "a string filepath to a video"

    def preprocess(self, payload: VideoData | None) -> str | None:
        """
        Parameters:
            payload: An instance of VideoData containing the video and subtitle files.
        Returns:
            Passes the uploaded video as a `str` filepath or URL whose extension can be modified by `format`.
        """
        if payload is None:
            return None
        if not payload.video.path:
            raise ValueError("Payload path missing")
        file_name = Path(payload.video.path)
        uploaded_format = file_name.suffix.replace(".", "")
        needs_formatting = self.format is not None and uploaded_format != self.format
        flip = self.sources == ["webcam"] and self.webcam_options.mirror

        if self.min_length is not None or self.max_length is not None:
            # With this if-clause, avoid unnecessary execution of `processing_utils.get_video_length`.
            # This is necessary for the Wasm-mode, because it uses ffprobe, which is not available in the browser.
            duration = processing_utils.get_video_length(file_name)
            if self.min_length is not None and duration < self.min_length:
                raise gr.Error(
                    f"Video is too short, and must be at least {self.min_length} seconds"
                )
            if self.max_length is not None and duration > self.max_length:
                raise gr.Error(
                    f"Video is too long, and must be at most {self.max_length} seconds"
                )
        # TODO: Check other image extensions to see if they work.
        valid_watermark_extensions = [".png", ".jpg", ".jpeg"]
        if self.watermark is not None:
            if not isinstance(self.watermark, (str, Path)):
                raise ValueError(
                    f"Provided watermark file not an expected file type. "
                    f"Received: {self.watermark}"
                )
            if Path(self.watermark).suffix not in valid_watermark_extensions:
                raise ValueError(
                    f"Watermark file does not have a supported extension. "
                    f"Expected one of {','.join(valid_watermark_extensions)}. "
                    f"Received: {Path(self.watermark).suffix}."
                )
        if needs_formatting or flip:
            format = f".{self.format if needs_formatting else uploaded_format}"
            output_options = ["-vf", "hflip", "-c:a", "copy"] if flip else []
            output_options += ["-an"] if not self.include_audio else []
            flip_suffix = "_flip" if flip else ""
            output_file_name = str(
                file_name.with_name(f"{file_name.stem}{flip_suffix}{format}")
            )
            output_filepath = Path(output_file_name)
            if output_filepath.exists():
                return str(output_filepath.resolve())
            if wasm_utils.IS_WASM:
                raise wasm_utils.WasmUnsupportedError(
                    "Video formatting is not supported in the Wasm mode."
                )
            ff = FFmpeg(  # type: ignore
                inputs={str(file_name): None},
                outputs={output_file_name: output_options},
            )
            ff.run()
            return str(output_filepath.resolve())
        elif not self.include_audio:
            output_file_name = str(file_name.with_name(f"muted_{file_name.name}"))
            if Path(output_file_name).exists():
                return output_file_name
            if wasm_utils.IS_WASM:
                raise wasm_utils.WasmUnsupportedError(
                    "include_audio=False is not supported in the Wasm mode."
                )
            ff = FFmpeg(  # type: ignore
                inputs={str(file_name): None},
                outputs={output_file_name: ["-an"]},
            )
            ff.run()
            return output_file_name
        else:
            return str(file_name)

    def postprocess(
        self, value: str | Path | tuple[str | Path, str | Path | None] | None
    ) -> VideoData | None:
        """
        Parameters:
            value: Expects a {str} or {pathlib.Path} filepath to a video which is displayed, or a {Tuple[str | pathlib.Path, str | pathlib.Path | None]} where the first element is a filepath to a video and the second element is an optional filepath to a subtitle file.
        Returns:
            VideoData object containing the video and subtitle files.
        """
        if self.streaming:
            return value  # type: ignore
        if value is None or value in ([None, None], (None, None)):
            return None
        if isinstance(value, (str, Path)):
            processed_files = (self._format_video(value), None)

        elif isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError(
                    f"Expected lists of length 2 or tuples of length 2. Received: {value}"
                )

            if not (
                isinstance(value[0], (str, Path)) and isinstance(value[1], (str, Path))
            ):
                raise TypeError(
                    f"If a tuple is provided, both elements must be strings or Path objects. Received: {value}"
                )
            video = value[0]
            subtitle = value[1]
            processed_files = (
                self._format_video(video),
                self._format_subtitle(subtitle),
            )

        else:
            raise Exception(f"Cannot process type as video: {type(value)}")
        if not processed_files[0]:
            raise ValueError("Video data missing")
        return VideoData(video=processed_files[0], subtitles=processed_files[1])

    def _format_video(self, video: str | Path | None) -> FileData | None:
        """
        Processes a video to ensure that it is in the correct format
        and adds a watermark if requested.
        """
        if video is None:
            return None
        video = str(video)
        returned_format = video.split(".")[-1].lower()
        if self.format is None or returned_format == self.format:
            conversion_needed = False
        else:
            conversion_needed = True

        is_url = client_utils.is_http_url_like(video)

        # For cases where the video is a URL and does not need to be converted
        # to another format and have a watermark added, we can just return the URL
        if not self.watermark and (is_url and not conversion_needed):
            return FileData(path=video)

        # For cases where the video needs to be converted to another format
        # or have a watermark added.
        if is_url:
            video = processing_utils.save_url_to_cache(
                video, cache_dir=self.GRADIO_CACHE
            )
        if (
            processing_utils.ffmpeg_installed()
            and not processing_utils.video_is_playable(video)
        ):
            warnings.warn(
                "Video does not have browser-compatible container or codec. Converting to mp4."
            )
            video = processing_utils.convert_video_to_playable_mp4(video)
        # Recalculate the format in case convert_video_to_playable_mp4 already made it the selected format
        returned_format = utils.get_extension_from_file_path_or_url(video).lower()
        if (
            self.format is not None and returned_format != self.format
        ) or self.watermark:
            if wasm_utils.IS_WASM:
                raise wasm_utils.WasmUnsupportedError(
                    "Modifying a video is not supported in the Wasm mode."
                )
            global_option_list = ["-y"]
            inputs_dict = {video: None}
            output_file_name = video[0 : video.rindex(".") + 1]
            if self.format is not None:
                output_file_name += self.format
            else:
                output_file_name += returned_format
            if self.watermark:
                inputs_dict[str(self.watermark)] = None
                watermark_cmd = "overlay=W-w-5:H-h-5"
                global_option_list += ["-filter_complex", watermark_cmd]
                output_file_name = (
                    Path(output_file_name).stem
                    + "_watermarked"
                    + Path(output_file_name).suffix
                )
            ff = FFmpeg(  # type: ignore
                inputs=inputs_dict,
                outputs={output_file_name: None},
                global_options=global_option_list,
            )
            ff.run()
            video = output_file_name

        return FileData(path=video, orig_name=Path(video).name)

    def _format_subtitle(self, subtitle: str | Path | None) -> FileData | None:
        """
        Convert subtitle format to VTT and process the video to ensure it meets the HTML5 requirements.
        """

        def srt_to_vtt(srt_file_path, vtt_file_path):
            """Convert an SRT subtitle file to a VTT subtitle file"""
            with (
                open(srt_file_path, encoding="utf-8") as srt_file,
                open(vtt_file_path, "w", encoding="utf-8") as vtt_file,
            ):
                vtt_file.write("WEBVTT\n\n")
                for subtitle_block in srt_file.read().strip().split("\n\n"):
                    subtitle_lines = subtitle_block.split("\n")
                    subtitle_timing = subtitle_lines[1].replace(",", ".")
                    subtitle_text = "\n".join(subtitle_lines[2:])
                    vtt_file.write(f"{subtitle_timing} --> {subtitle_timing}\n")
                    vtt_file.write(f"{subtitle_text}\n\n")

        if subtitle is None:
            return None

        valid_extensions = (".srt", ".vtt")

        if Path(subtitle).suffix not in valid_extensions:
            raise ValueError(
                f"Invalid value for parameter `subtitle`: {subtitle}. Please choose a file with one of these extensions: {valid_extensions}"
            )

        # HTML5 only support vtt format
        if Path(subtitle).suffix == ".srt":
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".vtt", dir=self.GRADIO_CACHE
            )

            srt_to_vtt(subtitle, temp_file.name)
            subtitle = temp_file.name

        return FileData(path=str(subtitle))

    def example_payload(self) -> Any:
        return {
            "video": handle_file(
                "https://github.com/gradio-app/gradio/raw/main/demo/video_component/files/world.mp4"
            ),
        }

    def example_value(self) -> Any:
        return "https://github.com/gradio-app/gradio/raw/main/demo/video_component/files/world.mp4"

    @staticmethod
    def get_video_duration_ffprobe(filename: str):
        if wasm_utils.IS_WASM:
            raise wasm_utils.WasmUnsupportedError(
                "ffprobe is not supported in the Wasm mode."
            )

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                filename,
            ],
            capture_output=True,
            check=True,
        )

        data = json.loads(result.stdout)

        duration = None
        if "format" in data and "duration" in data["format"]:
            duration = float(data["format"]["duration"])
        else:
            for stream in data.get("streams", []):
                if "duration" in stream:
                    duration = float(stream["duration"])
                    break

        return duration

    @staticmethod
    async def async_convert_mp4_to_ts(mp4_file, ts_file):
        if wasm_utils.IS_WASM:
            raise wasm_utils.WasmUnsupportedError(
                "Streaming is not supported in the Wasm mode."
            )

        ff = FFmpeg(  # type: ignore
            inputs={mp4_file: None},
            outputs={
                ts_file: "-c:v libx264 -c:a aac -f mpegts -bsf:v h264_mp4toannexb -bsf:a aac_adtstoasc"
            },
            global_options=["-y"],
        )

        command = ff.cmd.split(" ")
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode().strip()
            raise RuntimeError(f"FFmpeg command failed: {error_message}")

        return ts_file

    async def combine_stream(
        self,
        stream: list[bytes],
        desired_output_format: str | None = None,  # noqa: ARG002
        only_file=False,
    ) -> VideoData | FileData:
        """Combine video chunks into a single video file.

        Do not take desired_output_format into consideration as
        mp4 is a safe format for playing in browser.
        """
        if wasm_utils.IS_WASM:
            raise wasm_utils.WasmUnsupportedError(
                "Streaming is not supported in the Wasm mode."
            )

        # Use an mp4 extension here so that the cached example
        # is playable in the browser
        output_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=".mp4", dir=self.GRADIO_CACHE
        )

        ts_files = [
            processing_utils.save_bytes_to_cache(
                s, "video_chunk.ts", cache_dir=self.GRADIO_CACHE
            )
            for s in stream
        ]

        command = [
            "ffmpeg",
            "-i",
            f"concat:{'|'.join(ts_files)}",
            "-y",
            "-safe",
            "0",
            "-c",
            "copy",
            output_file.name,
        ]
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode().strip()
            raise RuntimeError(f"FFmpeg command failed: {error_message}")
        video = FileData(
            path=output_file.name,
            is_stream=False,
            orig_name="video-stream.mp4",
        )
        if only_file:
            return video

        output = VideoData(video=video)
        return output

    async def stream_output(
        self,
        value: str | None,
        output_id: str,
        first_chunk: bool,  # noqa: ARG002
    ) -> tuple[MediaStreamChunk | None, dict]:
        output_file = {
            "video": {
                "path": output_id,
                "is_stream": True,
                # Need to set orig_name so that downloaded file has correct
                # extension
                "orig_name": "video-stream.mp4",
                "meta": {"_type": "gradio.FileData"},
            }
        }
        if value is None:
            return None, output_file

        ts_file = value
        if not value.endswith(".ts"):
            if not value.endswith(".mp4"):
                raise RuntimeError(
                    "Video must be in .mp4 or .ts format to be streamed as chunks",
                )
            ts_file = value.replace(".mp4", ".ts")
            await self.async_convert_mp4_to_ts(value, ts_file)

        duration = self.get_video_duration_ffprobe(ts_file)
        if not duration:
            raise RuntimeError("Cannot determine video chunk duration")
        chunk: MediaStreamChunk = {
            "data": Path(ts_file).read_bytes(),
            "duration": duration,
            "extension": ".ts",
        }
        return chunk, output_file

