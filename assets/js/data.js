/* ============================================================
   QuarkAudio-Edit Demo Page · Data Definitions
   Real audio samples from audio_vs comparison directory.
   
   Key numbers (from paper):
   - 6 atomic operations: Add, Remove, Replace, Speed, Loudness, Order
   - 500K+ training triplets per epoch (150K offline + ~350K online)
   - 550K+ RAG index entries (FAISS)
   - 50K CoT instruction-decomposition pairs
   - FAD 3.27 (21.2% reduction over SmartDJ)
   - Inference: 9.94s (8× faster than AudioEditor)
   ============================================================ */

/* ---------- 6 Atomic Operations ----------
   Real audio samples from audio_vs directory.
   Each item provides: op, instruction, src (source), edited (QuarkAudio-Edit output), gt (ground truth)
------------------------------------------------------------ */
const OPERATION_DEMOS = [
  // ADD
  {
    op: 'add',
    opLabel: 'Add',
    instruction: 'Add the sound of Heartbeat singing.',
    src: 'assets/audio_vs/0nZzsoe77Zk_ori.flac',
    edited: 'assets/audio_vs/0nZzsoe77Zk__QuarkAudio-Edit.wav',
    gt: 'assets/audio_vs/0nZzsoe77Zk_ground_truth.wav',
  },

  // REMOVE
  {
    op: 'remove',
    opLabel: 'Remove',
    instruction: 'Remove the sound of Harmonica and singing.',
    src: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_remove_ori.wav',
    edited: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000__QuarkAudio-Edit.wav',
    gt: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_Ground%20Truth.wav',
  },

  // REPLACE
  {
    op: 'replace',
    opLabel: 'Replace',
    instruction: 'Change the sound of Whistle blowing to the sound of Baby crying, Woman consoling.',
    src: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_replace_ori.wav',
    edited: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_QuarkAudio-Edit.wav',
    gt: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_Ground%20Truth.wav',
  },

  // SPEED
  {
    op: 'speed',
    opLabel: 'Speed',
    instruction: 'Slow down the sound of Coin dropping, Rustling.',
    src: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_ori.wav',
    edited: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_QuarkAudio-Edit.wav',
    gt: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_Ground_truth.wav',
  },

  // LOUDNESS
  {
    op: 'loud',
    opLabel: 'Loudness',
    instruction: 'Turn up the volume of Livestock vocalizing.',
    src: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_LOUD_ori.wav',
    edited: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_QuarkAudio-Edit.wav',
    gt: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_Ground%20Truth.wav',
  },

  // ORDER
  {
    op: 'order',
    opLabel: 'Order',
    instruction: 'Swap the order of the two audio segments.',
    src: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_order_ori.wav',
    edited: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_our_QuarkAudio-Edit.wav',
    gt: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_Ground%20Truth.wav',
  },
];

/* ---------- Complex Multi-Step Instructions ----------
   Each item provides: title, instruction, src, edited, cot, plan (atomic chain)
------------------------------------------------------------ */
const COMPLEX_DEMOS = [
  {
    title: 'Urban → Countryside Transformation',
    instruction: 'Transform this urban street recording into a peaceful countryside morning.',
    src: 'assets/audio/complex/urban_countryside_src.wav',
    edited: 'assets/audio/complex/urban_countryside_edited.wav',
    specSrc: 'assets/images/spectrograms/urban_countryside_src.png',
    specEdited: 'assets/images/spectrograms/urban_countryside_edited.png',
    cot: 'The source contains traffic noise, car horns, and city ambience. A countryside morning requires bird songs, gentle wind, and the absence of urban sounds. I will first remove urban elements, then add natural sounds, and finally reduce loudness for a peaceful atmosphere.',
    plan: [
      { op: 'remove',  text: 'traffic noise' },
      { op: 'remove',  text: 'car horns' },
      { op: 'add',     text: 'bird chirping (+5 dB)' },
      { op: 'add',     text: 'gentle wind (+3 dB)' },
      { op: 'replace', text: 'city ambience → rooster' },
      { op: 'loud',    text: '−3 dB' },
    ],
  },
  {
    title: 'Rainy Evening Café Scene',
    instruction: 'Make it a rainy evening café scene.',
    src: 'assets/audio/complex/rainy_cafe_src.wav',
    edited: 'assets/audio/complex/rainy_cafe_edited.wav',
    specSrc: 'assets/images/spectrograms/rainy_cafe_src.png',
    specEdited: 'assets/images/spectrograms/rainy_cafe_edited.png',
    cot: 'The source audio contains birds chirping, traffic noise, and piano. I will remove traffic, replace the birds with rain, then add soft café chatter while preserving the piano line.',
    plan: [
      { op: 'remove',  text: 'traffic noise' },
      { op: 'replace', text: 'birds → rain' },
      { op: 'add',     text: 'café chatter (+3 dB)' },
      { op: 'loud',    text: '−2 dB' },
    ],
  },
  {
    title: 'Cinematic Chase Scene Design',
    instruction: 'Design an intense cinematic chase through city streets.',
    src: 'assets/audio/complex/chase_scene_src.wav',
    edited: 'assets/audio/complex/chase_scene_edited.wav',
    specSrc: 'assets/images/spectrograms/chase_scene_src.png',
    specEdited: 'assets/images/spectrograms/chase_scene_edited.png',
    cot: 'A cinematic chase needs fast-paced, intense sounds. The source has birds, traffic, and a park fountain. I will remove tranquil elements, keep traffic as a base but speed it up, then add screeching tires and a police siren, boosting overall loudness for intensity.',
    plan: [
      { op: 'remove', text: 'birds chirping' },
      { op: 'remove', text: 'park fountain' },
      { op: 'speed',  text: 'traffic × 1.5' },
      { op: 'add',    text: 'screeching tires (+6 dB)' },
      { op: 'add',    text: 'police siren (+4 dB)' },
      { op: 'loud',   text: '+5 dB' },
    ],
  },
  {
    title: 'Energetic Tempo Remix',
    instruction: 'Make this track feel more energetic and upbeat.',
    src: 'assets/audio/complex/energetic_remix_src.wav',
    edited: 'assets/audio/complex/energetic_remix_edited.wav',
    specSrc: 'assets/images/spectrograms/energetic_remix_src.png',
    specEdited: 'assets/images/spectrograms/energetic_remix_edited.png',
    cot: 'The source is a mellow acoustic piece with slow tempo. To increase energy, I will speed up the track, boost the percussion to emphasize rhythm, add a driving electric bass groove, and slightly reduce vocal prominence.',
    plan: [
      { op: 'speed', text: '× 1.3' },
      { op: 'loud',  text: 'percussion +6 dB' },
      { op: 'add',   text: 'electric bass (+4 dB)' },
      { op: 'loud',  text: 'vocals −2 dB' },
    ],
  },
];

/* ---------- Speech Editing Demos ----------
   Word/phrase-level replacement and insertion
------------------------------------------------------------ */
const SPEECH_DEMOS = [
  {
    op: 'replace',
    opLabel: 'Word Replace',
    instruction: 'Replace "Monday" with "Friday".',
    src: 'assets/audio/speech/speech_01_src.wav',
    edited: 'assets/audio/speech/speech_01_edited.wav',
  },
  {
    op: 'add',
    opLabel: 'Word Insert',
    instruction: 'Insert the word "really" before "love".',
    src: 'assets/audio/speech/speech_02_src.wav',
    edited: 'assets/audio/speech/speech_02_edited.wav',
  },
  {
    op: 'replace',
    opLabel: 'Phrase Replace',
    instruction: 'Change "in the morning" to "in the evening".',
    src: 'assets/audio/speech/speech_03_src.wav',
    edited: 'assets/audio/speech/speech_03_edited.wav',
  },
  {
    op: 'remove',
    opLabel: 'Word Delete',
    instruction: 'Remove the filler word "um".',
    src: 'assets/audio/speech/speech_04_src.wav',
    edited: 'assets/audio/speech/speech_04_edited.wav',
  },
];

/* ---------- Baseline Comparison ----------
   Real multi-model comparison from audio_vs directory.
   Each item pairs one source + instruction with outputs from multiple systems.
------------------------------------------------------------ */
const BASELINE_DEMOS = [
  {
    title: 'Add: Heartbeat Singing',
    instruction: 'Add the sound of Heartbeat singing.',
    op: 'add',
    src: 'assets/audio_vs/0nZzsoe77Zk_ori.flac',
    gt: 'assets/audio_vs/0nZzsoe77Zk_ground_truth.wav',
    outputs: [
      { name: 'QuarkAudio-Edit',   path: 'assets/audio_vs/0nZzsoe77Zk__QuarkAudio-Edit.wav', ours: true },
      { name: 'MMEdit',            path: 'assets/audio_vs/0nZzsoe77Zk_mmedit.wav' },
      { name: 'AudioEditor',       path: 'assets/audio_vs/0nZzsoe77Zk_866e094e_AudioEditor.wav' },
      { name: 'SAO-Instruct',      path: 'assets/audio_vs/0nZzsoe77Zk_SAO-Instruct.wav' },
      { name: 'SmartDJ',           path: 'assets/audio_vs/0nZzsoe77Zk_smartdj_editor.wav' },
    ],
  },
  {
    title: 'Remove: Harmonica and Singing',
    instruction: 'Remove the sound of Harmonica and singing.',
    op: 'remove',
    src: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_remove_ori.wav',
    gt: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_Ground%20Truth.wav',
    outputs: [
      { name: 'QuarkAudio-Edit',   path: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000__QuarkAudio-Edit.wav', ours: true },
      { name: 'MMEdit',            path: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_MMedit.wav' },
      { name: 'AudioEditor',       path: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_AudioEditor.wav' },
      { name: 'SAO-Instruct',      path: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_SAO-Instruct.wav' },
      { name: 'SmartDJ',           path: 'assets/audio_vs/-xYsfYZOI-Y_add_mUtztENAXKQ_000000_remove_smartdj_editor.wav' },
    ],
  },
  {
    title: 'Replace: Whistle → Baby Crying',
    instruction: 'Change the sound of Whistle blowing to the sound of Baby crying, Woman consoling.',
    op: 'replace',
    src: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_replace_ori.wav',
    gt: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_Ground%20Truth.wav',
    outputs: [
      { name: 'QuarkAudio-Edit',   path: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_QuarkAudio-Edit.wav', ours: true },
      { name: 'MMEdit',            path: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_MMedit.wav' },
      { name: 'AudioEditor',       path: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_AudioEditor.wav' },
      { name: 'SAO-Instruct',      path: 'assets/audio_vs/-628WBAudFs_add_dZTXjShlFDo_000020_SAO-Instruct.wav' },
    ],
  },
  {
    title: 'Speed: Slow Down Audio',
    instruction: 'Slow down the sound of Coin dropping, Rustling.',
    op: 'speed',
    src: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_ori.wav',
    gt: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_Ground_truth.wav',
    outputs: [
      { name: 'QuarkAudio-Edit',   path: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_QuarkAudio-Edit.wav', ours: true },
      { name: 'MMEdit',            path: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_MMedit.wav' },
      { name: 'SmartDJ',           path: 'assets/audio_vs/_429zJA1qvc_add_68SWNa2TUPI_000102_speed2_smartdj.wav' },
    ],
  },
  {
    title: 'Loudness: Volume Up',
    instruction: 'Turn up the volume of Livestock vocalizing.',
    op: 'loud',
    src: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_LOUD_ori.wav',
    gt: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_Ground%20Truth.wav',
    outputs: [
      { name: 'QuarkAudio-Edit',   path: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_QuarkAudio-Edit.wav', ours: true },
      { name: 'MMEdit',            path: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_MMedit.wav' },
      { name: 'SmartDJ',           path: 'assets/audio_vs/_CZzm6jUxbo_add_5lLZXLW5knw_000004_low_LOUD_smartdj.wav' },
    ],
  },
  {
    title: 'Order: Swap Segments',
    instruction: 'Swap the order of the two audio segments.',
    op: 'order',
    src: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_order_ori.wav',
    gt: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_Ground%20Truth.wav',
    outputs: [
      { name: 'QuarkAudio-Edit',   path: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_our_QuarkAudio-Edit.wav', ours: true },
      { name: 'MMEdit',            path: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_MMedit.wav' },
      { name: 'SmartDJ',           path: 'assets/audio_vs/0LcRpzwseS4_000008_cat_J9wzev494_k_000105_order_smartdj.wav' },
    ],
  },
];

/* ---------- Failure Cases & Limitations ----------
   Organized into four diagnostic categories aligned with the pipeline stages.
   Each case documents:
     - category:    which pipeline stage is at fault
     - title:       short human-readable label
     - caption:     source-audio content description (SAO-Instruct style)
     - instruction: the free-form instruction we gave the model
     - src / edited: source & failed-output audio paths
     - expected:    what a correct edit would have produced
     - observed:    what the model actually produced (the failure symptom)
     - diagnosis:   root cause along the CoT-RAG-MMDiT-GRPO pipeline
     - mitigation:  concrete future-work direction tied to the roadmap
------------------------------------------------------------ */
const FAILURE_CASES = [
  // ---------- Category 1: Ambiguous phrasing (CoT Planner) ----------
  {
    category: 'cot',
    categoryLabel: 'Ambiguous Phrasing',
    roadmapRef: 'R1',
    title: 'Negated vs. removal phrasing diverge',
    caption: 'An alarm beeps while a woman speaks.',
    instruction: 'The alarm should be silent!',
    src:    'assets/audio/failures/fail_cot_01_src.wav',
    edited: 'assets/audio/failures/fail_cot_01_edited.wav',
    expected: 'Planner emits [Remove alarm] — identical to "remove the alarm".',
    observed: 'Planner emits [Loud alarm −40 dB] instead of a clean removal, leaving faint residual beeps audible under the speech.',
    diagnosis: 'The RAG retriever returns loudness-reduction exemplars when the instruction phrasing uses "silent" rather than "remove". Top-3 exemplars contain no removal template, so the CoT falls back to an attenuation plan.',
    mitigation: 'R1 · Planner robustness — augment with paraphrase-invariance training so "silent", "mute", and "remove" map to the same atomic plan when the target is a discrete event.',
  },
  {
    category: 'cot',
    categoryLabel: 'Ambiguous Phrasing',
    roadmapRef: 'R1',
    title: 'Idiomatic instruction mis-parsed',
    caption: 'A busy street with car horns and pedestrians chatting.',
    instruction: 'Turn the volume of this scene down to a whisper.',
    src:    'assets/audio/failures/fail_cot_02_src.wav',
    edited: 'assets/audio/failures/fail_cot_02_edited.wav',
    expected: 'Planner emits [Loud −20 dB] on the full mix.',
    observed: 'Planner mis-triggers [Replace chatter → whispering voices] because "whisper" is treated as a target sound rather than a loudness modifier.',
    diagnosis: 'The word "whisper" has strong co-occurrence with speech-editing exemplars in the RAG index; the planner over-weights retrieval signal over instructional context.',
    mitigation: 'R1 · Inject a small supervised sub-task that asks the planner to first classify the instruction as (loudness | event-op | temporal) before decomposing, reducing lexical over-fitting.',
  },

  // ---------- Category 2: Long-tail retrieval miss (RAG Index) ----------
  {
    category: 'rag',
    categoryLabel: 'Long-tail Retrieval Miss',
    roadmapRef: 'R2',
    title: 'Rare instrument not in RAG index',
    caption: 'A guitar strumming outdoors.',
    instruction: 'Add a didgeridoo playing a low drone in the background.',
    src:    'assets/audio/failures/fail_rag_01_src.wav',
    edited: 'assets/audio/failures/fail_rag_01_edited.wav',
    expected: 'Added didgeridoo-characteristic rumble with circular-breathing pulses.',
    observed: 'Model produces a generic low-frequency drone that lacks the characteristic buzzing overtones and circular-breathing pattern of a real didgeridoo.',
    diagnosis: 'Only 7 didgeridoo clips exist in the current 510K-entry RAG index, and none among top-3 retrieved. The MMDiT editor falls back to a generic "low drone" prior learned from general AudioSet data.',
    mitigation: 'R2 · Long-tail coverage — extend the RAG index with FSD50K + Clotho-Detail, and switch to hybrid dense + BM25 retrieval so that rare lexical terms like "didgeridoo" are not washed out by embedding similarity.',
  },
  {
    category: 'rag',
    categoryLabel: 'Long-tail Retrieval Miss',
    roadmapRef: 'R2',
    title: 'Compound event not decomposed',
    caption: 'A quiet library with occasional page turns.',
    instruction: 'Add a grandfather-clock striking midnight with 12 deep chimes.',
    src:    'assets/audio/failures/fail_rag_02_src.wav',
    edited: 'assets/audio/failures/fail_rag_02_edited.wav',
    expected: '12 distinct deep-pitched bell strikes at roughly 3-second intervals.',
    observed: 'Only 3–4 loosely-timed chimes are generated, with incorrect inter-onset intervals.',
    diagnosis: 'RAG retrieves generic "bell" exemplars; the planner loses the count constraint ("12 chimes") during CoT decomposition because atomic operations do not currently carry numeric-count arguments.',
    mitigation: 'R2 + add a structured slot for numeric/temporal constraints in atomic operations, and train the planner to emit e.g. Add(event=chime, count=12, interval=3s).',
  },

  // ---------- Category 3: Dense-scene confusion (MMDiT Editor) ----------
  {
    category: 'edit',
    categoryLabel: 'Dense-Scene Confusion',
    roadmapRef: 'R3',
    title: 'Non-target event also altered',
    caption: 'Drums, footsteps, frogs, and crickets are heard.',
    instruction: 'Replace the drums with claps.',
    src:    'assets/audio/failures/fail_edit_01_src.wav',
    edited: 'assets/audio/failures/fail_edit_01_edited.wav',
    expected: 'Only the drum track is swapped for claps; footsteps, frogs, and crickets are preserved verbatim.',
    observed: 'Drums are replaced as requested, but the footstep cadence becomes irregular and the cricket chirps are partially muted.',
    diagnosis: 'When the source audio contains ≥ 4 simultaneous events, the MMDiT cross-attention cannot cleanly localize the drum track; gradient leakage during denoising alters neighbouring events.',
    mitigation: 'R3 · Event-level control — add a frozen sound-event detector to produce per-event attention masks during training, and apply a preservation loss on non-target segments.',
  },
  {
    category: 'edit',
    categoryLabel: 'Dense-Scene Confusion',
    roadmapRef: 'R3',
    title: 'Speech intelligibility degraded',
    caption: 'A woman speaks over café ambience with a distant jazz band.',
    instruction: 'Replace the jazz band with classical piano.',
    src:    'assets/audio/failures/fail_edit_02_src.wav',
    edited: 'assets/audio/failures/fail_edit_02_edited.wav',
    expected: 'Jazz swapped to piano while speech and ambience are untouched.',
    observed: 'Piano appears correctly, but the speech exhibits slight phonetic smearing — especially on fricatives — reducing intelligibility.',
    diagnosis: 'Stable-Audio-Open\'s latent space compresses speech and music into overlapping dimensions. Editing in that latent unavoidably perturbs speech formants even when the speech token mask is preserved.',
    mitigation: 'R3 + train a speech-specific preservation head on top of MMDiT, or fall back to waveform-domain stitching when a speech-event mask is detected.',
  },

  // ---------- Category 4: Unnatural overlay (MMDiT Editor) ----------
  {
    category: 'blend',
    categoryLabel: 'Unnatural Overlay',
    roadmapRef: 'R4',
    title: 'Added event sounds "pasted on"',
    caption: 'A cat meowing in a small apartment.',
    instruction: 'Add a dog howling in the distance.',
    src:    'assets/audio/failures/fail_blend_01_src.wav',
    edited: 'assets/audio/failures/fail_blend_01_edited.wav',
    expected: 'A distant, reverberated howl consistent with the apartment\'s acoustic space.',
    observed: 'The dog howl is clearly present but sits in the foreground with anechoic dryness, making it sound overlaid rather than co-located.',
    diagnosis: 'The model has no explicit acoustic-scene prior. It learns to inject events at average SNR/RT60 rather than matching the source scene\'s impulse response.',
    mitigation: 'R4 · Natural blending — condition MMDiT on a scene embedding extracted from the source (e.g., RT60 + noise floor + band-energy profile) and add a loudness-aware reward in Stage-2 GRPO.',
  },
  {
    category: 'blend',
    categoryLabel: 'Unnatural Overlay',
    roadmapRef: 'R4',
    title: 'SNR mismatch on inserted event',
    caption: 'Gentle rain on a tin roof.',
    instruction: 'Add a thunderclap.',
    src:    'assets/audio/failures/fail_blend_02_src.wav',
    edited: 'assets/audio/failures/fail_blend_02_edited.wav',
    expected: 'A thunderclap ≈ 15 dB above the rain floor, with brief masking of the rain during the transient.',
    observed: 'Thunder appears at roughly the same level as the rain, without the natural loudness contrast; the rain is not momentarily masked.',
    diagnosis: 'The atomic [Add] operation currently uses a fixed default SNR when the instruction contains no explicit dB value, regardless of the source scene\'s dynamics.',
    mitigation: 'R4 + equip the planner with a learned SNR predictor conditioned on the event category + source loudness histogram, removing the fixed-default fallback.',
  },
];

/* ---------- External Baseline Gallery ----------
   Real audio samples from published baseline systems, crawled from their demo pages.
   Organized by editing operation type with multi-system comparison.
------------------------------------------------------------ */
const EXTERNAL_GALLERY = {
  /* --- SmartDJ (whole pipeline comparison) --- */
  smartdj: {
    label: 'SmartDJ',
    url: 'https://zitonglan.github.io/project/smartdj/smartdj',
    description: 'Multi-step complex audio editing with whole-pipeline comparison across systems.',
    samples: [
      {
        id: 'smartdj_pipeline_02',
        title: 'Complex Edit #1',
        systems: {
          'Original': 'assets/smartdj/whole_pipeline/original/0002.wav',
          'ZETA': 'assets/smartdj/whole_pipeline/edited_zeta/0002.wav',
          'AudioEditor': 'assets/smartdj/whole_pipeline/edited_audioeditor/0002.wav',
          'AUDIT': 'assets/smartdj/whole_pipeline/edited_audit/0002.wav',
          'SmartDJ': 'assets/smartdj/whole_pipeline/edited_smartdj/0002.wav',
        },
      },
      {
        id: 'smartdj_pipeline_04',
        title: 'Complex Edit #2',
        systems: {
          'Original': 'assets/smartdj/whole_pipeline/original/0004.wav',
          'ZETA': 'assets/smartdj/whole_pipeline/edited_zeta/0004.wav',
          'AudioEditor': 'assets/smartdj/whole_pipeline/edited_audioeditor/0004.wav',
          'AUDIT': 'assets/smartdj/whole_pipeline/edited_audit/0004.wav',
          'SmartDJ': 'assets/smartdj/whole_pipeline/edited_smartdj/0004.wav',
        },
      },
      {
        id: 'smartdj_pipeline_05',
        title: 'Complex Edit #3',
        systems: {
          'Original': 'assets/smartdj/whole_pipeline/original/0005.wav',
          'ZETA': 'assets/smartdj/whole_pipeline/edited_zeta/0005.wav',
          'AudioEditor': 'assets/smartdj/whole_pipeline/edited_audioeditor/0005.wav',
          'AUDIT': 'assets/smartdj/whole_pipeline/edited_audit/0005.wav',
          'SmartDJ': 'assets/smartdj/whole_pipeline/edited_smartdj/0005.wav',
        },
      },
      {
        id: 'smartdj_pipeline_06',
        title: 'Complex Edit #4',
        systems: {
          'Original': 'assets/smartdj/whole_pipeline/original/0006.wav',
          'ZETA': 'assets/smartdj/whole_pipeline/edited_zeta/0006.wav',
          'AudioEditor': 'assets/smartdj/whole_pipeline/edited_audioeditor/0006.wav',
          'AUDIT': 'assets/smartdj/whole_pipeline/edited_audit/0006.wav',
          'SmartDJ': 'assets/smartdj/whole_pipeline/edited_smartdj/0006.wav',
        },
      },
    ],
  },

  /* --- MMEditing (per-operation comparison) --- */
  mmediting: {
    label: 'MMEditing',
    url: 'https://ty0402.github.io/MMEditing/',
    description: 'Per-operation audio editing: Add, Drop, Replace, Loudness, Speed, Reorder.',
    samples: [
      {
        id: 'mmedit_add_1',
        title: 'Add: Mix in dog barking',
        instruction: 'Mix in dog barking in the middle.',
        op: 'add',
        systems: {
          'Original': 'assets/mmediting/raw/add_audiocaps_1.wav',
          'AUDIT': 'assets/mmediting/audit/add_audiocaps_1.wav',
          'AudioEditor': 'assets/mmediting/audioediter/add_audiocaps_1.wav',
          'MMEdit': 'assets/mmediting/add/add_audiocaps_1.wav',
        },
      },
      {
        id: 'mmedit_add_6',
        title: 'Add: Include typing as background',
        instruction: 'Include typing as a background sound.',
        op: 'add',
        systems: {
          'Original': 'assets/mmediting/raw/add_audiocaps_6.wav',
          'AUDIT': 'assets/mmediting/audit/add_audiocaps_6.wav',
          'AudioEditor': 'assets/mmediting/audioediter/add_audiocaps_6.wav',
          'MMEdit': 'assets/mmediting/add/add_audiocaps_6.wav',
        },
      },
      {
        id: 'mmedit_drop_1',
        title: 'Remove: Eliminate event',
        instruction: 'Eliminate the specified sound from the audio.',
        op: 'remove',
        systems: {
          'Original': 'assets/mmediting/raw/drop1_013146.wav',
          'AUDIT': 'assets/mmediting/audit/drop1_013146.wav',
          'AudioEditor': 'assets/mmediting/audioediter/drop1_013146.wav',
          'MMEdit': 'assets/mmediting/drop/drop1_013146.wav',
        },
      },
      {
        id: 'mmedit_replace_1',
        title: 'Replace: Swap sound event',
        instruction: 'Replace one sound event with another.',
        op: 'replace',
        systems: {
          'Original': 'assets/mmediting/raw/replace_093574.wav',
          'AUDIT': 'assets/mmediting/audit/replace_093574.wav',
          'AudioEditor': 'assets/mmediting/audioediter/replace_093574.wav',
          'MMEdit': 'assets/mmediting/replace/replace_093574.wav',
        },
      },
      {
        id: 'mmedit_speed_1',
        title: 'Speed: Change tempo',
        instruction: 'Adjust the playback speed of the audio.',
        op: 'speed',
        systems: {
          'Original': 'assets/mmediting/raw/speed_audiocaps_10.wav',
          'AUDIT': 'assets/mmediting/audit/speed_audiocaps_10.wav',
          'AudioEditor': 'assets/mmediting/audioediter/speed_audiocaps_10.wav',
          'MMEdit': 'assets/mmediting/speed/speed_audiocaps_10.wav',
        },
      },
      {
        id: 'mmedit_loud_1',
        title: 'Loudness: Adjust volume',
        instruction: 'Adjust the loudness of the audio.',
        op: 'loud',
        systems: {
          'Original': 'assets/mmediting/raw/loud_audiocaps_1.wav',
          'AUDIT': 'assets/mmediting/audit/loud_audiocaps_1.wav',
          'AudioEditor': 'assets/mmediting/audioediter/loud_audiocaps_1.wav',
          'MMEdit': 'assets/mmediting/loud/loud_audiocaps_1.wav',
        },
      },
      {
        id: 'mmedit_order_1',
        title: 'Reorder: Rearrange events',
        instruction: 'Reorder the temporal structure of the audio.',
        op: 'order',
        systems: {
          'Original': 'assets/mmediting/raw/reorder_audiocaps_1.wav',
          'AUDIT': 'assets/mmediting/audit/reorder_audiocaps_1.wav',
          'AudioEditor': 'assets/mmediting/audioediter/reorder_audiocaps_1.wav',
          'MMEdit': 'assets/mmediting/reorder/reorder_audiocaps_1.wav',
        },
      },
    ],
  },

  /* --- SAO-Instruct (comparison section) --- */
  saoinstruct: {
    label: 'SAO-Instruct',
    url: 'https://eth-disco.github.io/sao-instruct/',
    description: 'Instruction-guided audio editing with free-form natural language.',
    samples: [
      {
        id: 'sao_comp_102849',
        title: 'Comparison Sample #1',
        systems: {
          'Reference': 'assets/sao-instruct/comparison/reference/102849.mp3',
          'ZETA-50': 'assets/sao-instruct/comparison/zeta50/102849.mp3',
          'ZETA-75': 'assets/sao-instruct/comparison/zeta75/102849.mp3',
          'AudioEditor': 'assets/sao-instruct/comparison/audioeditor/102849.mp3',
          'SAO-Instruct': 'assets/sao-instruct/comparison/sao-instruct/102849.mp3',
        },
      },
      {
        id: 'sao_comp_103256',
        title: 'Comparison Sample #2',
        systems: {
          'Reference': 'assets/sao-instruct/comparison/reference/103256.mp3',
          'ZETA-50': 'assets/sao-instruct/comparison/zeta50/103256.mp3',
          'ZETA-75': 'assets/sao-instruct/comparison/zeta75/103256.mp3',
          'AudioEditor': 'assets/sao-instruct/comparison/audioeditor/103256.mp3',
          'SAO-Instruct': 'assets/sao-instruct/comparison/sao-instruct/103256.mp3',
        },
      },
      {
        id: 'sao_comp_103362',
        title: 'Comparison Sample #3',
        systems: {
          'Reference': 'assets/sao-instruct/comparison/reference/103362.mp3',
          'ZETA-50': 'assets/sao-instruct/comparison/zeta50/103362.mp3',
          'ZETA-75': 'assets/sao-instruct/comparison/zeta75/103362.mp3',
          'AudioEditor': 'assets/sao-instruct/comparison/audioeditor/103362.mp3',
          'SAO-Instruct': 'assets/sao-instruct/comparison/sao-instruct/103362.mp3',
        },
      },
      {
        id: 'sao_env_frogs',
        title: 'Environment: Frogs (multi-edit)',
        instruction: 'Add footsteps / rain / river to frog sounds.',
        systems: {
          'Source (frogs)': 'assets/sao-instruct/10_frogs.mp3',
          '+Footsteps': 'assets/sao-instruct/10_frogs_footsteps.mp3',
          '+Rain': 'assets/sao-instruct/10_frogs_rain.mp3',
          '+River': 'assets/sao-instruct/10_frogs_river.mp3',
        },
      },
      {
        id: 'sao_env_helicopter',
        title: 'Environment: Helicopter (multi-edit)',
        instruction: 'Add thunder / fireworks / plane to helicopter.',
        systems: {
          'Source': 'assets/sao-instruct/1_helicopter.mp3',
          '+Thunder': 'assets/sao-instruct/1_helicopter_thunder.mp3',
          '+Fireworks': 'assets/sao-instruct/1_helicopter_fireworks.mp3',
          '+Plane': 'assets/sao-instruct/1_helicopter_plane.mp3',
        },
      },
    ],
  },

  /* --- VoiceCraft-X (Speech Editing) --- */
  voicecraftx: {
    label: 'VoiceCraft-X',
    url: 'https://voicecraft-x.github.io',
    description: 'Multilingual speech editing with autoregressive codec language model.',
    samples: [
      {
        id: 'vcx_en_1',
        title: 'English Speech Edit #1',
        systems: {
          'Source/Prompt': 'assets/voicecraft-x/EN/prompt/1.wav',
          'VoiceCraft-X': 'assets/voicecraft-x/EN/voicecraftx/1.wav',
        },
      },
      {
        id: 'vcx_en_2',
        title: 'English Speech Edit #2',
        systems: {
          'Source/Prompt': 'assets/voicecraft-x/EN/prompt/2.wav',
          'VoiceCraft-X': 'assets/voicecraft-x/EN/voicecraftx/2.wav',
        },
      },
      {
        id: 'vcx_zh_1',
        title: 'Chinese Speech Edit #1',
        systems: {
          'Source/Prompt': 'assets/voicecraft-x/ZH/prompt/1.wav',
          'VoiceCraft-X': 'assets/voicecraft-x/ZH/voicecraftx/1.wav',
        },
      },
      {
        id: 'vcx_ja_1',
        title: 'Japanese Speech Edit #1',
        systems: {
          'Source/Prompt': 'assets/voicecraft-x/JA/prompt/1.wav',
          'VoiceCraft-X': 'assets/voicecraft-x/JA/voicecraftx/1.wav',
        },
      },
      {
        id: 'vcx_es_1',
        title: 'Spanish Speech Edit #1',
        systems: {
          'Source/Prompt': 'assets/voicecraft-x/ES/prompt/1.wav',
          'VoiceCraft-X': 'assets/voicecraft-x/ES/voicecraftx/1.wav',
        },
      },
    ],
  },

  /* --- Audio-Omni (Editing tasks) --- */
  audioomni: {
    label: 'Audio-Omni',
    url: 'https://zeyuet.github.io/Audio-Omni/',
    description: 'Unified audio model with add, remove, extract, transfer, and speech editing capabilities.',
    samples: [
      {
        id: 'aomni_add_22',
        title: 'Add Sound Event',
        op: 'add',
        systems: {
          'Input': 'assets/audio-omni/add/22/input.wav',
          'Audio-Omni': 'assets/audio-omni/add/22/result.wav',
          'Ground Truth': 'assets/audio-omni/add/22/gt.mp3',
        },
      },
      {
        id: 'aomni_add_40',
        title: 'Add Sound Event #2',
        op: 'add',
        systems: {
          'Input': 'assets/audio-omni/add/40/input.wav',
          'Audio-Omni': 'assets/audio-omni/add/40/result.wav',
          'Ground Truth': 'assets/audio-omni/add/40/gt.mp3',
        },
      },
      {
        id: 'aomni_remove_1226',
        title: 'Remove Sound Event',
        op: 'remove',
        systems: {
          'Input': 'assets/audio-omni/remove/1226/input.mp3',
          'Audio-Omni': 'assets/audio-omni/remove/1226/result.wav',
          'Ground Truth': 'assets/audio-omni/remove/1226/gt.wav',
        },
      },
      {
        id: 'aomni_extract_608',
        title: 'Extract Sound Event',
        op: 'remove',
        systems: {
          'Input': 'assets/audio-omni/extract/608/input.mp3',
          'Audio-Omni': 'assets/audio-omni/extract/608/result.wav',
          'Ground Truth': 'assets/audio-omni/extract/608/gt.wav',
        },
      },
      {
        id: 'aomni_transfer_1903',
        title: 'Style Transfer',
        op: 'replace',
        systems: {
          'Input': 'assets/audio-omni/transfer/1903/input.mp3',
          'Audio-Omni': 'assets/audio-omni/transfer/1903/result.wav',
          'Ground Truth': 'assets/audio-omni/transfer/1903/gt.wav',
        },
      },
      {
        id: 'aomni_speech_1',
        title: 'Speech Editing #1',
        op: 'replace',
        systems: {
          'Source': 'assets/audio-omni/speechedit/1/source.wav',
          'Audio-Omni': 'assets/audio-omni/speechedit/1/edit.wav',
        },
      },
      {
        id: 'aomni_speech_2',
        title: 'Speech Editing #2',
        op: 'replace',
        systems: {
          'Source': 'assets/audio-omni/speechedit/2/source.wav',
          'Audio-Omni': 'assets/audio-omni/speechedit/2/edit.wav',
        },
      },
    ],
  },
};
