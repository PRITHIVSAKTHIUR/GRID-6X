import gradio as gr
import spaces
import numpy as np
import random
from diffusers import DiffusionPipeline
import torch
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model_repo_id = "stabilityai/stable-diffusion-3.5-large-turbo"

torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

pipe = DiffusionPipeline.from_pretrained(model_repo_id, torch_dtype=torch_dtype)
pipe = pipe.to(device)

pipe.load_lora_weights("prithivMLmods/SD3.5-Turbo-Realism-2.0-LoRA", weight_name="SD3.5-Turbo-Realism-2.0-LoRA.safetensors")
trigger_word = "Turbo Realism"  
pipe.fuse_lora(lora_scale=1.0)

MAX_SEED = np.iinfo(np.int32).max
MAX_IMAGE_SIZE = 1024

# Define styles
style_list = [
    {
        "name": "3840 x 2160",
        "prompt": "hyper-realistic 8K image of {prompt}. ultra-detailed, lifelike, high-resolution, sharp, vibrant colors, photorealistic",
        "negative_prompt": "cartoonish, low resolution, blurry, simplistic, abstract, deformed, ugly",
    },
    {
        "name": "2560 x 1440",
        "prompt": "hyper-realistic 4K image of {prompt}. ultra-detailed, lifelike, high-resolution, sharp, vibrant colors, photorealistic",
        "negative_prompt": "cartoonish, low resolution, blurry, simplistic, abstract, deformed, ugly",
    },
    {
        "name": "HD+",
        "prompt": "hyper-realistic 2K image of {prompt}. ultra-detailed, lifelike, high-resolution, sharp, vibrant colors, photorealistic",
        "negative_prompt": "cartoonish, low resolution, blurry, simplistic, abstract, deformed, ugly",
    },
    {
        "name": "Style Zero",
        "prompt": "{prompt}",
        "negative_prompt": "",
    },
]

STYLE_NAMES = [style["name"] for style in style_list]
DEFAULT_STYLE_NAME = STYLE_NAMES[0]

grid_sizes = {
    "2x1": (2, 1),
    "1x2": (1, 2),
    "2x2": (2, 2),
    "2x3": (2, 3),
    "3x2": (3, 2),
    "1x1": (1, 1)
}

@spaces.GPU(duration=60)
def infer(
    prompt,
    negative_prompt="",
    seed=42,
    randomize_seed=False,
    width=1024,
    height=1024,
    guidance_scale=7.5,
    num_inference_steps=10,
    style="Style Zero",
    grid_size="1x1",
    progress=gr.Progress(track_tqdm=True),
):
    selected_style = next(s for s in style_list if s["name"] == style)
    styled_prompt = selected_style["prompt"].format(prompt=prompt)
    styled_negative_prompt = selected_style["negative_prompt"]

    if randomize_seed:
        seed = random.randint(0, MAX_SEED)

    generator = torch.Generator().manual_seed(seed)

    grid_size_x, grid_size_y = grid_sizes.get(grid_size, (1, 1))
    num_images = grid_size_x * grid_size_y

    options = {
        "prompt": styled_prompt,
        "negative_prompt": styled_negative_prompt,
        "guidance_scale": guidance_scale,
        "num_inference_steps": num_inference_steps,
        "width": width,
        "height": height,
        "generator": generator,
        "num_images_per_prompt": num_images,
    }

    torch.cuda.empty_cache()  # Clear GPU memory
    result = pipe(**options)

    grid_img = Image.new('RGB', (width * grid_size_x, height * grid_size_y))

    for i, img in enumerate(result.images[:num_images]):
        grid_img.paste(img, (i % grid_size_x * width, i // grid_size_x * height))

    return grid_img, seed

examples = [
    "A tiny astronaut hatching from an egg on the moon, 4k, planet theme",
    "An anime-style illustration of a delicious, golden-brown wiener schnitzel on a plate, served with fresh lemon slices, parsley --style raw5",
    "Cold coffee in a cup bokeh --ar 85:128 --v 6.0 --style raw5, 4K, Photo-Realistic",
    "A cat holding a sign that says hello world --ar 85:128 --v 6.0 --style raw"
]

css = '''
.gradio-container{max-width: 585px !important}
h1{text-align:center}
footer {
    visibility: hidden
}
'''

with gr.Blocks(css=css, theme="bethecloud/storj_theme") as demo:
    with gr.Column(elem_id="col-container"):
        gr.Markdown("## GRID 6X🪨")

        with gr.Row():
            prompt = gr.Text(
                label="Prompt",
                show_label=False,
                max_lines=1,
                placeholder="Enter your prompt",
                container=False,
            )

            run_button = gr.Button("Run", scale=0, variant="primary")

        result = gr.Image(label="Result", show_label=False)


        with gr.Row(visible=True):
            grid_size_selection = gr.Dropdown(
                choices=["2x1", "1x2", "2x2", "2x3", "3x2", "1x1"],
                value="1x1",
                label="Grid Size"
            )

        with gr.Accordion("Advanced Settings", open=False):
            negative_prompt = gr.Text(
                label="Negative prompt",
                max_lines=1,
                placeholder="Enter a negative prompt",
                value="(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation",
                visible=False,
            )

            seed = gr.Slider(
                label="Seed",
                minimum=0,
                maximum=MAX_SEED,
                step=1,
                value=0,
            )

            randomize_seed = gr.Checkbox(label="Randomize seed", value=True)

            with gr.Row():
                width = gr.Slider(
                    label="Width",
                    minimum=512,
                    maximum=MAX_IMAGE_SIZE,
                    step=32,
                    value=1024,
                )

                height = gr.Slider(
                    label="Height",
                    minimum=512,
                    maximum=MAX_IMAGE_SIZE,
                    step=32,
                    value=1024,
                )

            with gr.Row():
                guidance_scale = gr.Slider(
                    label="Guidance scale",
                    minimum=0.0,
                    maximum=7.5,
                    step=0.1,
                    value=0.0,
                )

                num_inference_steps = gr.Slider(
                    label="Number of inference steps",
                    minimum=1,
                    maximum=50,
                    step=1,
                    value=10,
                )       
                
                style_selection = gr.Radio(
                    show_label=True,
                    container=True,
                    interactive=True,
                    choices=STYLE_NAMES,
                    value=DEFAULT_STYLE_NAME,
                    label="Quality Style",
                )

        gr.Examples(examples=examples, 
                    inputs=[prompt], 
                    outputs=[result, seed], 
                    fn=infer, 
                    cache_examples=False)

    gr.on(
        triggers=[run_button.click, prompt.submit],
        fn=infer,
        inputs=[
            prompt,
            negative_prompt,
            seed,
            randomize_seed,
            width,
            height,
            guidance_scale,
            num_inference_steps,
            style_selection,
            grid_size_selection,
        ],
        outputs=[result, seed],
    )

if __name__ == "__main__":
    demo.launch()