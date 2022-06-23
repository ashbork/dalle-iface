# Alternative Dall-e interface

I was dissatisfied with [the original](https://github.com/saharmor/dalle-playground) dalle interface - while it was simple and looked pretty neat it lacked some features which were a dealbreaker for me (and I think they're really important, especially since image generation can take a while).

## Installation

First follow the steps from [dalle-playground](https://github.com/saharmor/dalle-playground) - GPU setup is tricky in particular.

After launching the backend replace `BACKEND_URL` within `interface.py`  with your own backend URL (should be visible on backend launch, if not you could try localhost:8080/dalle).

```bash
python -m venv venv 
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

As of now, the interface has two commands:

* `collage` - generates 9 images each for every prompt and combines them into a collage.

* `oneshot` - generates n images for every prompt.

i.e

```bash
python interface.py collage "Landscape" "People" -n 10
```

The results are saved into a subdirectory `results/<prompt>` and are indexed in order of creation.

## Why?

* The lack of a queue bothered me - wait times can be long, especially since generation is hit-or-miss so you may want to overgenerate a lot. This interface addresses that - you can enqueue as many prompts as you like in any amount.

* Huggingface returned the results in a nice form - a 3x3 grid, which could easily be screenshot and shared. So I made something similar, although not as neat.
