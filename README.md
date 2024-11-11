---
title: GRID 6X
emoji: 🪨
colorFrom: red
colorTo: gray
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: true
license: creativeml-openrail-m
short_description: Generate images fast with SD3.5 turbo
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference


# GRID-6X : Layout for Seamless Image Assembly

The grid functionality in this Gradio app is designed to arrange generated images in a grid layout, based on a user-selected grid size. Here’s an explanation of how it works and a diagram to illustrate its operation.

![image/png](https://cdn-uploads.huggingface.co/production/uploads/65bb837dbfb878f46c77de4c/rZcxkwjj50ejnshCv_0Yl.png)

| Space Name | Description | Link |
|------------|-------------|------|
| GRID-6X    | A model for image generation and manipulation | [GRID-6X on Hugging Face](https://huggingface.co/spaces/prithivMLmods/GRID-6X) |

### Model Description

| Model Name                                  | Description                               | Link                                                      |
|---------------------------------------------|-------------------------------------------|-----------------------------------------------------------|
| **stabilityai/stable-diffusion-3.5-large-turbo** | Base model for high-quality image generation | [Stable Diffusion 3.5 Large Turbo](https://huggingface.co/stabilityai/stable-diffusion-3.5-large-turbo) |
| **prithivMLmods/SD3.5-Turbo-Realism-2.0-LoRA** | Turbo adapter LoRA for enhanced realism   | [SD3.5-Turbo-Realism-2.0-LoRA](https://huggingface.co/prithivMLmods/SD3.5-Turbo-Realism-2.0-LoRA) |


### How the Grid Works
1. **Grid Size Selection**: The user selects the grid size from options like "2x1", "1x2", "2x2", "2x3", "3x2", and "1x1". Each option corresponds to the arrangement of images:
   - **2x1**: 2 images in a single row
   - **1x2**: 1 image in two rows (column layout)
   - **2x2**: 2 rows with 2 images each
   - **2x3**: 2 rows with 3 images each
   - **3x2**: 3 rows with 2 images each
   - **1x1**: A single image (default)

2. **Image Generation**: Based on the grid size selection, the app calculates the number of images to generate. For example:
   - If the grid size is "2x2", the app generates 4 images.
   - For "3x2", it generates 6 images.

3. **Image Arrangement**: The generated images are arranged in a blank canvas (`grid_img`) using the grid dimensions, placing each image in its corresponding position:
   - Each image is "pasted" onto `grid_img` at coordinates determined by the grid layout.
   - This canvas is sized according to the total width and height of the images, ensuring a perfect grid fit.

### Code Explanation for Grid Creation
In the `infer` function:
```python
grid_img = Image.new('RGB', (width * grid_size_x, height * grid_size_y))
for i, img in enumerate(result.images[:num_images]):
    grid_img.paste(img, (i % grid_size_x * width, i // grid_size_x * height))
```
1. **Image Initialization**: `grid_img` is a blank canvas that will hold the images in a grid format.
2. **Image Placement**: Images are pasted onto the canvas using a loop:
   - **Horizontal Position**: `(i % grid_size_x) * width` calculates the x-coordinate.
   - **Vertical Position**: `(i // grid_size_x) * height` calculates the y-coordinate.

### Diagram of Grid Layouts
Below is an example layout for different grid options:

| Grid Option | Layout Example | Explanation                              |
|-------------|----------------|------------------------------------------|
| 2x1         | [Image1] [Image2] | 2 images in a single row               |
| 1x2         | [Image1]        | 1 image per row (vertical arrangement)  |
|             | [Image2]        |                                          |
| 2x2         | [Image1] [Image2] | 2 rows with 2 images each              |
|             | [Image3] [Image4] |                                          |
| 2x3         | [Image1] [Image2] [Image3] | 2 rows with 3 images each |
|             | [Image4] [Image5] [Image6] |                             |
| 3x2         | [Image1] [Image2] | 3 rows with 2 images each              |
|             | [Image3] [Image4] |                                          |
|             | [Image5] [Image6] |                                          |
| 1x1         | [Image1]         | Single image layout                     |

Each option arranges images accordingly, providing flexibility in viewing multiple images in one output.


Here is a functional architecture diagram for the grid operations in your Gradio app. This will outline the flow from user input through image generation and grid assembly.

### Functional Architecture Diagram for Grid Operations

```plaintext
                    +-----------------------------+
                    |       User Interface        |
                    +-----------------------------+
                                |
                 User selects grid size, style, prompt, etc.
                                |
                                v
+-------------------------------+----------------------------------+
|                  Gradio Interface Component                     |
|                                                                 |
| 1. Accepts user inputs for:                                     |
|    - Prompt                                                     |
|    - Negative prompt                                            |
|    - Style selection                                            |
|    - Grid size selection                                        |
|    - Seed options (randomize or specific seed)                  |
|    - Image resolution (width, height)                           |
|                                                                 |
| 2. Passes user inputs to the `infer` function for processing.   |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                           Infer Function                        |
|                                                                 |
| 1. **Select Style**:                                            |
|    - Matches selected style and customizes prompt accordingly.  |
|                                                                 |
| 2. **Generate Images**:                                         |
|    - Uses Diffusion Pipeline to generate images.                |
|    - Number of images generated based on grid size.             |
|    - Applies seed, guidance scale, and steps from user inputs.  |
|                                                                 |
| 3. **Create Grid Canvas**:                                      |
|    - Initializes blank canvas based on grid dimensions.         |
|    - Canvas size = width * grid columns, height * grid rows.    |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                        Grid Assembly Process                    |
|                                                                 |
| 1. **Loop through images**:                                     |
|    - For each image generated:                                  |
|       * Calculate x-coordinate based on column position.        |
|       * Calculate y-coordinate based on row position.           |
|    - Paste image onto the blank canvas at the calculated        |
|      coordinates.                                               |
|                                                                 |
| 2. **Return Grid Image**:                                       |
|    - Final grid canvas (containing all images) returned         |
|      to the Gradio interface.                                   |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                   Gradio Image Display Component                |
|                                                                 |
| 1. Receives grid image from `infer` function.                   |
| 2. Displays assembled image grid to the user.                   |
|                                                                 |
|       +----------------------------------------------+          |
|       |   +---------+    +---------+    +---------+  |          |
|       |   | Image1  |    | Image2  |    | Image3  |  |          |
|       |   +---------+    +---------+    +---------+  |          |
|       |   | Image4  |    | Image5  |    | Image6  |  |          |
|       |   +---------+    +---------+    +---------+  |          |
|       +----------------------------------------------+          |
+-----------------------------------------------------------------+
```

### Explanation of Each Component
1. **User Interface**: Takes in user inputs for the image generation process, including the prompt, grid size, style, etc.
2. **Gradio Interface Component**: Passes these inputs to the `infer` function.
3. **Infer Function**:
   - **Style Selection**: Customizes the prompt based on the selected style.
   - **Image Generation**: Generates the required number of images using the Diffusion Pipeline.
   - **Grid Canvas Creation**: Initializes a blank canvas sized according to the grid selection.
4. **Grid Assembly Process**:
   - Loops through each image, calculates its position, and pastes it on the canvas.
5. **Gradio Image Display Component**: The final grid image is returned and displayed in the Gradio app interface. 

This architecture allows for flexible grid options and ensures that images are arranged neatly according to user preferences.



## Generated Images

| Image 1                                                                                     | Image 2                                                                                     | Image 3                                                                                     |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| ![Image 1](https://cdn-uploads.huggingface.co/production/uploads/65bb837dbfb878f46c77de4c/YgKMv7GypUF-VaYXovsqS.webp) | ![Image 2](https://cdn-uploads.huggingface.co/production/uploads/65bb837dbfb878f46c77de4c/3h2U2XgDWGpW4AuOe32eW.webp) | ![Image 3](https://cdn-uploads.huggingface.co/production/uploads/65bb837dbfb878f46c77de4c/cQMH9xCJNlfLpc64OwPWy.webp) |

| Image 4                                                                                     | Image 5                                                                                     | Image 6                                                                                     |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| ![Image 4](https://cdn-uploads.huggingface.co/production/uploads/65bb837dbfb878f46c77de4c/AoSjzBtwUvG4Bm0f1x0nd.webp) | ![Image 5](https://cdn-uploads.huggingface.co/production/uploads/65bb837dbfb878f46c77de4c/v4vL-uuP4kvQNliOeY7MB.webp) | ![Image 6](https://cdn-uploads.huggingface.co/production/uploads/65bb837dbfb878f46c77de4c/qfn65JORQMWBb18fpAR_S.webp) |



To add both of these spaces that support the GRID functionality Layout for Seamless Image Assembly : 


| Space Name       | Description                          | Link                                                     |
|------------------|--------------------------------------|----------------------------------------------------------|
| **GRID-6X**      | A model for image generation and manipulation | [GRID-6X on Hugging Face](https://huggingface.co/spaces/prithivMLmods/GRID-6X) |
| **IMAGINEO-4K**  | A high-resolution image generation model | [IMAGINEO-4K on Hugging Face](https://huggingface.co/spaces/prithivMLmods/IMAGINEO-4K) |



| Project Name       | Description                        | Link                                               |
|--------------------|------------------------------------|----------------------------------------------------|
| GRID-6X            | A model for image stitching        | [GRID-6X GitHub Repository](https://github.com/PRITHIVSAKTHIUR/GRID-6X) |


- *End of Article, Thanks for Reading 🤗!.*

### **Try It Out!**

| Space | [GRID 6X](https://huggingface.co/spaces/prithivMLmods/GRID-6X) |
| Hugging Face | [prithivMLmods](https://huggingface.co/prithivMLmods) |
