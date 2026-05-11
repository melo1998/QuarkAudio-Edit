# QuarkAudio-Edit — Project Demo Page

A static demo website for the paper
**"Think Before You Edit: Chain-of-Thought Reasoning with RAG for Language-Guided Audio Editing"** (QuarkAudio-Edit).

The design takes inspiration from:
- [SmartDJ](https://zitonglan.github.io/project/smartdj/smartdj.html)
- [SAO-Instruct](https://eth-disco.github.io/sao-instruct/)
- [Audio-Omni](https://zeyuet.github.io/Audio-Omni/)
- [Bagpiper](https://bagpiper-cmu.github.io/)

## Directory Layout

```
demo_page/
├── index.html                  # Main page (hero, overview, method, demos, results, BibTeX)
├── README.md                   # This file
└── assets/
    ├── css/
    │   └── style.css           # All styling (responsive, modern, academic)
    ├── js/
    │   ├── data.js             # Demo-sample metadata (instructions + audio paths)
    │   └── app.js              # Tab switching, filter chips, audio player coordination
    ├── images/                 # Figures referenced in the paper
    │   ├── Edit.png            # Figure 1 — unified audio/speech editing overview
    │   ├── QuarkAudio_edit.jpg # Figure 2 — full framework
    │   ├── data_pipeline.jpg   # Figure 3 — data synthesis pipeline
    │   └── GRPO_training.png   # Figure 4 — progressive GRPO pipeline
    └── audio/
        ├── operations/         # Six atomic operations (Add, Remove, Replace, Speed, Loud, Order)
        ├── complex/            # Complex multi-step instructions (CoT demos)
        ├── speech/             # Speech-editing samples
        └── baselines/          # Side-by-side comparisons vs. baselines
```

## Replacing the Placeholder Assets

Before releasing the page publicly, **drop the real files into `assets/`** with the paths listed in `assets/js/data.js`.

### 1. Figures

Copy the four figure files from the paper repo into `assets/images/`:

| Source (paper repo)            | Destination                           |
|--------------------------------|---------------------------------------|
| `figures/Edit.png`             | `assets/images/Edit.png`              |
| `figures/QuarkAudio_edit.jpg`  | `assets/images/QuarkAudio_edit.jpg`   |
| `figures/data_pipeline.jpg`    | `assets/images/data_pipeline.jpg`     |
| `figures/GRPO_training.png`    | `assets/images/GRPO_training.png`     |

### 2. Audio Samples

Each demo entry in `assets/js/data.js` points to a `.wav` file. Replace each placeholder path with your generated audio. Recommended naming convention (already used in `data.js`):

- `assets/audio/operations/<op>_<idx>_src.wav` (source)
- `assets/audio/operations/<op>_<idx>_edited.wav` (edited)
- `assets/audio/complex/<scenario>_src.wav`
- `assets/audio/complex/<scenario>_edited.wav`
- `assets/audio/speech/speech_<idx>_{src,edited}.wav`
- `assets/audio/baselines/baseline_<idx>_{src,audioeditor,sao,mmedit,ours}.wav`

To **add a new demo**, append an entry to the relevant array in `data.js` — the page will render it automatically on reload.

## Running Locally

Because modern browsers block `file://` `fetch()` and sometimes strict `<audio>` requests, serve the folder through a tiny local HTTP server:

### Python 3 (built-in)

```bash
cd demo_page
python -m http.server 8080
# open http://localhost:8080
```

### Node.js

```bash
cd demo_page
npx serve -l 8080 .
```

### VS Code

Install the "Live Server" extension, right-click `index.html` → *Open with Live Server*.

## Deploying to GitHub Pages

1. Push the `demo_page/` folder (or its contents) to a public repository, e.g. `quarkaudio-edit.github.io`.
2. In *Settings → Pages*, set the branch to `main` and the folder to `/` (if you push the contents of `demo_page/` directly) or `/demo_page` if you keep the folder.
3. Your page will be live at `https://<user>.github.io/<repo>/`.

## Customizing

- **Page colors / gradients** — edit CSS variables at the top of `assets/css/style.css` (`:root { --c-primary: …; }`).
- **Paper & Code button targets** — replace the `href="#"` placeholders in the hero section of `index.html`.
- **BibTeX** — replace the anonymized block in the `#citation` section of `index.html`.
- **Authors / affiliations** — update `.authors` and `.affiliations` inside the hero.

## Browser Support

Tested on current Chrome, Edge, Firefox, and Safari. Uses native `<audio>` controls, CSS grid, CSS custom properties, and `backdrop-filter` — no runtime framework required.

## License

Page template MIT-licensed. Audio samples and figures are governed by the paper's data-license terms (see main paper).
