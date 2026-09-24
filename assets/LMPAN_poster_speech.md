# LMPAN Poster 现场讲解讲稿

> **Interspeech 2027 · Poster Session**  
> LMPAN: A Lightweight Multi-Path Alignment Network for Joint Full-Duplex Acoustic Echo Cancellation and Noise Suppression

---

## 使用指南

| 项目 | 说明 |
|------|------|
| **总时长** | 主线 5 分钟 + Q&A 机动 3 分钟 |
| **动线建议** | 从海报**左栏顶部**（§1 Motivation）开始，按 §1→§2→§3→§4→§5 顺序从上到下、从左到右移动 |
| **语速提示** | 英文讲稿以 ~140 wpm 节奏朗读；关键数字放慢、加重语气；过渡句可稍快 |
| **手势原则** | 始终用靠近海报一侧的手指向当前区块；切换区块时用"walking gesture"引导听众视线 |
| **备用策略** | 若听众只有 2 分钟耐心，跳到 §4 三个 callout 数字 → §5 结论即可 |

---

## §0 Opening / 开场

**时间：30 秒**

（→ 站在海报正前方，面带微笑，目光接触听众）

### English Script

> Hi, I'm Chengwei Liu from the Qwen Business Unit at Alibaba. Thanks for stopping by!  
> In one sentence — we built a **480K-parameter** neural network that runs on your phone and jointly cancels echo and suppresses noise in real time, so full-duplex voice assistants can actually hear you clearly while they're talking.  
> Let me walk you through our poster — it'll take about five minutes.

### 中文对照

> 你好，我是来自阿里巴巴通义千问事业部的刘成伟，感谢驻足！  
> 一句话概括——我们构建了一个仅 **48 万参数**的神经网络，可以在手机端实时运行，同时完成回声消除与噪声抑制，让全双工语音助手在播放语音的同时也能清晰地听到用户说话。  
> 接下来我按海报顺序为您介绍，大约五分钟。

---

## §1 Motivation & Objectives

**时间：60 秒**

（→ 指向左栏 Figure 1 全双工架构图）

### English Script

> So here's the scenario — Figure 1 shows a typical full-duplex spoken dialogue system on a mobile device. The phone is playing far-end speech through the loudspeaker **while** the user is talking at the same time. The microphone picks up everything: near-end speech, echo, and background noise.  
>
> Now the challenge: different phones have **different hardware distortions** — speaker nonlinearity, ADC latency, and time-varying delays ranging from milliseconds up to a hundred milliseconds. This causes both **temporal misalignment** and **energy mismatch** between the reference signal and the microphone signal.  
>
>（→ 指向贡献 bullets）  
> Our four contributions address exactly these issues:  
> First, a **multi-path alignment** stage that explicitly corrects time and energy mismatches.  
> Second, an **attention fusion** mechanism — no auxiliary VAD or double-talk detector needed.  
> Third, a **post-filter with dynamic target** generation to avoid over-suppression.  
> And fourth, a **two-stage SSL training** framework using WavLM to boost perceptual quality.

### 中文对照

> 场景如下——Figure 1 展示了移动端的典型全双工语音对话系统。手机扬声器正在播放远端语音，**同时**用户也在说话。麦克风会拾取所有信号：近端语音、回声和背景噪声。  
>
> 挑战在于：不同手机有**不同的硬件失真**——扬声器非线性、ADC 延迟、以及从几毫秒到上百毫秒的时变延迟。这导致参考信号与麦克风信号之间出现**时间失配**和**能量失配**。  
>
> 我们的四项贡献正好解决这些问题：  
> 第一，**多路径对齐**模块，显式修正时延和能量失配。  
> 第二，**注意力融合**机制——无需辅助 VAD 或双讲检测器。  
> 第三，**后滤波 + 动态目标**生成，避免过度抑制。  
> 第四，**两阶段 SSL 训练**框架，利用 WavLM 提升感知质量。

---

## §2 Proposed Algorithm

**时间：90 秒**

（→ 移到左栏/中栏 Figure 2 LMPAN 系统总图）

### English Script — A) Multi-Path Alignment

>（→ 指向 Figure 2(b) Alignment Block）  
> Let's dive into the architecture. Figure 2 shows the full LMPAN pipeline. Starting with the alignment stage — we have **three pairwise alignment blocks** processing ref–mic, mic–LAEC, and ref–LAEC pairs.  
>
> Each block performs a **soft temporal alignment**: we project queries and keys from the input features, then compute a similarity score for every candidate delay $d$ from 0 to 100 frames — that's up to one second. A softmax gives us a probabilistic delay distribution, and we apply weighted shifting. This is differentiable, so it trains end-to-end.  
>
> On top of that, **learnable per-path energy scaling** normalizes amplitude levels before fusion, compensating for hardware gain differences.

### 中文对照 — A) 多路径对齐

> 来看整体架构。Figure 2 展示了 LMPAN 的完整流程。首先是对齐阶段——我们有**三个成对对齐模块**，分别处理 ref–mic、mic–LAEC、ref–LAEC 三对信号。  
>
> 每个模块执行**软时域对齐**：从输入特征中投影 Query 和 Key，对 0 到 100 帧（约 1 秒）的每个候选延迟 $d$ 计算相似度得分，经过 softmax 得到概率延迟分布，然后加权移位。整个过程可微分，支持端到端训练。  
>
> 此外，**可学习的逐路径能量缩放因子**在融合前归一化幅度，补偿硬件增益差异。

---

### English Script — B) Attention Fusion

>（→ 指向 Figure 2(c) Attention Fusion Module）  
> After alignment, two GTCRN branches refine the LAEC stream and the mic stream separately. Then our attention fusion module combines them with a multi-scale channel-attention mask $M$:  
>
> $$Y_f = M \odot Y_l + (1 - M) \odot Y_m$$  
>
> The key insight: this mask is **learned implicitly** — we don't need any auxiliary VAD or double-talk detector. The network figures out when to trust LAEC more (echo-dominant) and when to trust the mic more (near-end-dominant), all from the data.

### 中文对照 — B) 注意力融合

> 对齐之后，两个 GTCRN 分支分别增强 LAEC 流和 Mic 流。然后注意力融合模块通过多尺度通道注意力掩码 $M$ 将二者组合：  
>
> $$Y_f = M \odot Y_l + (1 - M) \odot Y_m$$  
>
> 关键洞察：这个掩码是**隐式学习**的——不需要任何辅助 VAD 或双讲检测器。网络自动学会何时更信任 LAEC（回声主导时），何时更信任 Mic（近端主导时），完全从数据中驱动。

---

### English Script — C) Post-filtering & Dynamic Target

>（→ 指向海报 §2C 区域）  
> Finally, a post-filtering module with residual scaling $\alpha = 0.4$ prevents over-suppression artifacts.  
>
> And for training, we design a **dynamic target**: instead of training toward perfectly clean speech, our target is  
> $t = s + \gamma\, n' + \beta\, e'$,  
> where $\gamma$ and $\beta$ are controlled by desired target SNR and SER. This retains a small amount of natural residual, which actually **helps downstream ASR and VAD** because it avoids the spectral holes that aggressive suppression creates.

### 中文对照 — C) 后滤波与动态目标

> 最后，后滤波模块以残差缩放系数 $\alpha = 0.4$ 防止过度抑制产生的伪影。  
>
> 训练时我们设计了**动态目标**：不以完全干净的语音为目标，而是  
> $t = s + \gamma\, n' + \beta\, e'$，  
> 其中 $\gamma$ 和 $\beta$ 由期望的目标 SNR 和 SER 控制。这保留了少量自然残留，实际上**有利于下游 ASR 和 VAD**，因为避免了激进抑制造成的频谱空洞。

---

## §3 Two-Stage SSL Training

**时间：45 秒**

（→ 移到 Figure 3 两阶段训练流程图）

### English Script

> Now for the training recipe — Figure 3 shows our two-stage strategy.  
>
> **Stage 1**: We freeze a pretrained WavLM-Large model and train LMPAN purely on the SSL loss — minimizing MSE between WavLM embeddings of the enhanced output and the clean reference. This teaches the network what "good speech" looks like in a rich semantic space.  
>
> **Stage 2**: We jointly optimize the full task loss — spectral reconstruction, echo-aware loss, SI-SNR, and PMSQE perceptual loss — combined as:  
> $\mathcal{L} = 10\,\mathcal{L}_{\text{total}} + 0.5\,\mathcal{L}_{\text{SSL}}$  
> The SSL loss stays as a **consistency regularizer** to preserve semantic fidelity.  
>
> This two-stage approach gains +0.10 MOS over one-stage training, and +0.05 over SSL-only — you can see that in Table 1, Experiments 4 and 5.

### 中文对照

> 接下来是训练策略——Figure 3 展示了我们的两阶段方案。  
>
> **阶段一**：冻结预训练的 WavLM-Large 模型，仅用 SSL 损失训练 LMPAN——最小化增强输出与干净参考在 WavLM 嵌入空间的 MSE。这教会网络在丰富的语义空间中"什么是好语音"。  
>
> **阶段二**：联合优化完整任务损失——频谱重建、回声感知损失、SI-SNR 和 PMSQE 感知损失——组合为：  
> $\mathcal{L} = 10\,\mathcal{L}_{\text{total}} + 0.5\,\mathcal{L}_{\text{SSL}}$  
> SSL 损失作为**一致性正则项**保留语义保真度。  
>
> 两阶段方法比单阶段训练 MOS 提升 +0.10，比仅 SSL 提升 +0.05——可在 Table 1 的 Experiment 4 和 5 中看到。

---

## §4 Experimental Results

**时间：90 秒**

（→ 移到右栏 §4 区域，先指三个 callout 大数字）

### English Script — Key Numbers

> Let me highlight three headline numbers:  
>（→ 依次指向三个 callout box）  
> **MOS 4.49** on the AEC Challenge 2023 blind test — with only 0.48M parameters and 126M MACs.  
> **WER drops by 9.87 percentage points** — from 24.25% down to 14.38% in the hardest condition.  
> And **48.22 dB ERLE** — the best echo suppression among all compared methods.

### 中文对照 — 核心数字

> 让我先强调三个核心数字：  
> **MOS 4.49**——在 AEC Challenge 2023 盲测集上取得，仅用 0.48M 参数和 126M MACs。  
> **WER 下降 9.87 个百分点**——在最难条件下从 24.25% 降至 14.38%。  
> **ERLE 48.22 dB**——所有对比方法中最优的回波抑制。

---

### English Script — Table 1 Ablation

>（→ 指向 Table 1）  
> Table 1 shows the full ablation on the AEC Challenge blind test. Starting from a lightweight base model at MOS 4.17:  
> Adding multi-path alignment (+MA) → 4.31.  
> Adding attention fusion (+AFM) → 4.39, and ERLE jumps to 48.22 dB.  
> Two-stage SSL (+STL) → **4.49**, our best configuration.  
>
> Compare with baselines: DeepVQE achieves 4.40 with 0.82M params and 315M MACs — we beat it with **1.7× fewer parameters** and **2.5× fewer MACs**.

### 中文对照 — Table 1 消融

> Table 1 展示了 AEC Challenge 盲测集上的完整消融实验。从轻量基线模型 MOS 4.17 出发：  
> 加入多路径对齐（+MA）→ 4.31。  
> 加入注意力融合（+AFM）→ 4.39，ERLE 跃升至 48.22 dB。  
> 两阶段 SSL（+STL）→ **4.49**，最佳配置。  
>
> 与基线对比：DeepVQE 以 0.82M 参数和 315M MACs 达到 4.40——我们以**少 1.7 倍的参数**和**少 2.5 倍的计算量**超越它。

---

### English Script — Table 2 Downstream Tasks

>（→ 指向 Table 2）  
> Table 2 evaluates real downstream tasks — VAD, ASR, and full-duplex interruption rate — on a real-world double-talk test set.  
>
> In the harder SER range of −20 to −15 dB, our full pipeline improves DCF from 9.38 to **3.75**, WER from 24.25 to **14.38**, and TIR from 85.17 to **93.85**. That's substantial gains for real deployment.

### 中文对照 — Table 2 下游任务

> Table 2 在真实双讲测试集上评估下游任务——VAD、ASR 和全双工打断率。  
>
> 在更难的 SER −20 到 −15 dB 范围内，完整流水线将 DCF 从 9.38 降至 **3.75**，WER 从 24.25 降至 **14.38**，TIR 从 85.17 提升至 **93.85**。这对实际部署意义重大。

---

### English Script — Table 3 DTA Analysis

>（→ 指向 Table 3）  
> Table 3 shows our dynamic target adaptation analysis. The target SER during training is a tunable knob:  
> SER_t = 25 dB gives the best WER at 10.24% — optimal for ASR.  
> SER_t = 30 dB maximizes PESQ at 2.39 — optimal for speech quality.  
> SER_t = 35 dB maximizes ERLE at 45.11 dB — optimal for echo suppression.  
> So you pick the operating point based on your downstream task.

### 中文对照 — Table 3 DTA 分析

> Table 3 展示了动态目标适配分析。训练时的目标 SER 是一个可调旋钮：  
> SER_t = 25 dB 取得最优 WER 10.24%——最适合 ASR。  
> SER_t = 30 dB 最大化 PESQ 2.39——最适合语音质量。  
> SER_t = 35 dB 最大化 ERLE 45.11 dB——最适合回声抑制。  
> 因此根据下游任务选择工作点即可。

---

### English Script — Figure 4 Spectrograms

>（→ 指向 Figure 4 频谱图）  
> Finally, Figure 4 gives you a visual intuition. You can see the spectrogram evolution from the noisy microphone input, through LAEC, through our alignment stage, to the final output. Notice how the near-end speech harmonics are well preserved while the echo components are cleanly removed — no musical noise, no spectral holes.

### 中文对照 — Figure 4 频谱图

> 最后，Figure 4 给出直观视觉对比。可以看到频谱从含噪麦克风输入，经 LAEC、经对齐阶段，到最终输出的演变。注意近端语音谐波被良好保留，而回声成分被干净去除——没有音乐噪声，没有频谱空洞。

---

## §5 Conclusions / 收尾

**时间：30 秒**

（→ 移到右栏底部 §5 结论区块）

### English Script

> To wrap up — three takeaways:  
> **One**: LMPAN achieves state-of-the-art performance with only 480K parameters and 126M MACs — real-time on ARM Cortex-A78 with RTF 0.18.  
> **Two**: The combination of multi-path alignment, attention fusion, two-stage SSL training, and dynamic target adaptation jointly guarantee speech integrity for downstream tasks.  
> **Three**: DTA provides a tunable trade-off — you can optimize for ASR, for perceptual quality, or for echo suppression by simply adjusting one hyperparameter.  
>
> Thank you! We have a live demo running on a phone — feel free to try it, and I'm happy to discuss any details or potential collaborations.

### 中文对照

> 总结——三个要点：  
> **第一**：LMPAN 仅用 48 万参数和 126M MACs 即达到最先进性能——在 ARM Cortex-A78 上实时运行，RTF 为 0.18。  
> **第二**：多路径对齐 + 注意力融合 + 两阶段 SSL 训练 + 动态目标适配的联合设计保证了下游任务所需的语音完整性。  
> **第三**：DTA 提供可调的权衡——只需调整一个超参数，即可针对 ASR、感知质量或回声抑制分别优化。  
>
> 谢谢！我们有一个手机端实时 demo——欢迎体验，也很乐意讨论任何细节或潜在合作。

---

## Q&A 预案（机动 3 分钟）

以下为高概率提问及中英应答要点，现场根据实际情况选用。

---

### Q1: 为什么不用辅助 VAD/DTD？

**English Answer:**

> Great question. Traditional AEC pipelines rely on a separate VAD or double-talk detector to decide when to freeze the adaptive filter. But these modules add latency, introduce their own errors, and create a chicken-and-egg problem — you need clean speech to detect double-talk, but you need double-talk detection to get clean speech.  
>
> Our attention fusion module learns this implicitly from data. The mask $M$ naturally assigns higher weight to the LAEC stream during far-end single-talk and shifts to the mic stream during near-end activity. We validated this: removing the auxiliary VAD/DTD doesn't degrade performance, and the end-to-end training makes it more robust to edge cases.

**中文要点：**

> 传统 AEC 依赖独立 VAD/DTD 决定何时冻结自适应滤波器，但带来额外延迟、自身误差和鸡生蛋问题。我们的注意力融合模块从数据中隐式学习：掩码 $M$ 在远端单讲时自动偏向 LAEC 流，近端活动时偏向 Mic 流。端到端训练使其对边界情况更鲁棒，无需额外模块。

---

### Q2: 480K 参数如何在端侧部署？RTF 和内存情况？

**English Answer:**

> LMPAN has 0.48M parameters — that's about 1.9 MB in FP16. We measured RTF = 0.18 on an ARM Cortex-A78 core, meaning it processes audio 5.5× faster than real time. Memory footprint including intermediate buffers is under 10 MB.  
>
> The model uses STFT with 32 ms frames and 16 ms hop, so the algorithmic latency is just 32 ms. It's designed to sit in the audio HAL pipeline alongside the existing LAEC module, which is a standard NLMS adaptive filter that's already on every phone.

**中文要点：**

> 0.48M 参数约 1.9 MB（FP16）。ARM Cortex-A78 上 RTF = 0.18，处理速度为实时的 5.5 倍。含中间缓冲区内存占用 < 10 MB。STFT 帧长 32 ms、帧移 16 ms，算法延迟仅 32 ms。设计为嵌入音频 HAL 流水线，与已有 LAEC（NLMS 自适应滤波器）模块串联。

---

### Q3: SSL 两阶段 vs 单阶段，收益来源是什么？

**English Answer:**

> The gain comes from two aspects. First, Stage 1 with frozen WavLM forces the network to learn a **semantically meaningful** representation of speech — it understands what speech should sound like, not just what the spectral magnitude should be.  
>
> Second, keeping a small SSL loss (weight 0.5) in Stage 2 acts as a **regularizer** that prevents the task-specific losses from collapsing fine spectral details. Quantitatively: one-stage gives MOS 4.17, SSL-only gives 4.44, and two-stage gives **4.49**. The +0.05 from SSL-only to two-stage shows that task losses still contribute meaningfully.

**中文要点：**

> 收益来自两方面：阶段一冻结 WavLM 迫使网络学习语义有意义的语音表征——理解语音"应该是什么样"，而非仅拟合频谱幅度。阶段二保留小权重 SSL 损失（0.5）作为正则项，防止任务损失坍缩细节。量化：单阶段 4.17 → SSL-only 4.44 → 两阶段 **4.49**。

---

### Q4: DTA 的 γ/β 如何选择？有自动策略吗？

**English Answer:**

> Currently $\gamma$ and $\beta$ are determined by target SNR and target SER respectively:  
> $\gamma = \min(1,\; 10^{(\text{SNR}_\text{in} - \text{SNR}_t)/20})$  
> $\beta = \min(1,\; 10^{(\text{SER}_\text{in} - \text{SER}_t)/20})$  
>
> So the only hyperparameter is $\text{SER}_t$ (we set $\text{SNR}_t = \text{SER}_t$ in practice). As Table 3 shows, $\text{SER}_t = 25$ dB is best for ASR, 30 dB for PESQ, and 35 dB for ERLE. For deployment, you pick based on your downstream priority.  
>
> An automatic adaptation strategy — for example, switching $\text{SER}_t$ based on detected use case — is something we're exploring for future work.

**中文要点：**

> $\gamma$ 和 $\beta$ 由目标 SNR/SER 公式确定，唯一超参为 $\text{SER}_t$（实践中 $\text{SNR}_t = \text{SER}_t$）。Table 3 表明：25 dB 最优 ASR、30 dB 最优 PESQ、35 dB 最优 ERLE。部署时按下游优先级选取。自动切换策略为未来工作方向。

---

### Q5: 与 DeepVQE 的本质差异？

**English Answer:**

> DeepVQE is a fully end-to-end model — it takes mic and ref signals and directly outputs enhanced speech, handling alignment, echo cancellation, noise suppression, and dereverberation all in one shot. It's elegant but heavy: 0.82M parameters and 315M MACs.  
>
> LMPAN takes a **hybrid approach**: we keep the traditional LAEC (NLMS adaptive filter) as a first stage — it's already on every phone and handles linear echo well — then our neural network focuses on what's left: nonlinear residual echo, noise, and critically, **explicit alignment correction**.  
>
> This division of labor means our neural part only needs 0.48M params / 126M MACs, yet achieves better MOS (4.49 vs 4.40). The key architectural difference is our multi-path alignment, which DeepVQE handles only implicitly.

**中文要点：**

> DeepVQE 是全端到端模型（0.82M/315M），一步处理对齐+AEC+NS+DRB。LMPAN 采用**混合架构**：保留传统 LAEC（NLMS）处理线性回声，神经网络专注非线性残余+噪声+**显式对齐校正**。分工使得神经部分仅需 0.48M/126M 却达到更优 MOS（4.49 vs 4.40）。核心架构差异在于我们的多路径显式对齐。

---

### Q6: 多路径对齐的计算开销大吗？

**English Answer:**

> The alignment stage adds about 0.08M parameters and 17M MACs compared to the base model — going from 0.24M/65M to 0.32M/82M. That's roughly a 26% increase in compute, but it brings a +0.14 MOS improvement (4.17 → 4.31), which is the single largest module-level gain in our ablation.  
>
> The key efficiency trick: we downsample along frequency by 4× with max-pooling before computing the delay likelihood, so the dot-product search over 100 candidate delays is done on a much smaller representation.

**中文要点：**

> 对齐模块增加约 0.08M 参数和 17M MACs（0.24M/65M → 0.32M/82M），计算量增加约 26%，但带来 +0.14 MOS（4.17→4.31），为消融中单模块最大增益。效率关键：在计算延迟似然前沿频率维度 4× 下采样（max-pooling），使 100 个候选延迟的点积搜索在更小的表示上完成。

---

### Q7: 真实部署中遇到哪些硬件失真类型？

**English Answer:**

> We collected data from **40 different smartphone models** at playback volumes from 30% to 100%. The main distortion types we observe are:  
> 1. **Speaker nonlinearity** — especially at high volumes, producing harmonic distortion in the echo path.  
> 2. **Time-varying latency** — from the audio framework buffering, ranging from a few ms to over 100 ms, and it can drift during a call.  
> 3. **Gain mismatch** — different AGC settings and codec pipelines cause energy level differences between the reference and what actually comes out of the speaker.  
> 4. **Frequency response coloration** — each phone's speaker has its own frequency characteristic, distorting the echo spectrum.  
>
> Our multi-path alignment handles items 2 and 3 explicitly, and the neural network learns to deal with items 1 and 4 from the training data diversity.

**中文要点：**

> 我们从 **40 款不同手机**采集数据（音量 30%–100%）。主要失真类型：①扬声器非线性（高音量谐波失真）；②时变延迟（音频框架缓冲，几 ms 到 100+ ms，通话中可漂移）；③增益失配（不同 AGC/编解码管线造成能量差异）；④频响着色（每款手机扬声器频响不同）。多路径对齐显式处理②③，神经网络从数据多样性中学习处理①④。

---

### Q8: 未来工作方向？

**English Answer:**

> Three directions:  
> **First**, further reducing compute — we're exploring structured pruning and INT8 quantization to push below 100M MACs while maintaining quality.  
> **Second**, extending to multi-microphone scenarios — many phones now have 2–3 mics, and spatial information could significantly improve robustness.  
> **Third**, adaptive $\text{SER}_t$ selection — automatically choosing the dynamic target operating point based on the detected downstream use case, whether it's ASR, voice commands, or natural conversation.

**中文要点：**

> 三个方向：①进一步降低计算量——探索结构化剪枝和 INT8 量化，目标 < 100M MACs 同时保持质量。②扩展到多麦克风场景——利用空间信息提升鲁棒性。③自适应 $\text{SER}_t$ 选择——根据检测到的下游用例自动选择动态目标工作点。

---

## 时间分配总览

| 区块 | 内容 | 时间 |
|------|------|------|
| §0 Opening | 自我介绍 + 一句话问题定义 | 30s |
| §1 Motivation & Objectives | 挑战 + 四个贡献概述 | 60s |
| §2 Proposed Algorithm | 对齐 → 融合 → 后滤波/动态目标 | 90s |
| §3 Two-Stage SSL Training | WavLM 冻结 → 联合优化 | 45s |
| §4 Experimental Results | Callout 数字 → Table 1/2/3 → Figure 4 | 90s |
| §5 Conclusions | 三条结论 + 开放邀请 | 30s |
| **主线合计** | | **5 min 45s** |
| Q&A 预案 | 8 个高概率问题 | ~3 min 机动 |

---

## 演讲小贴士

1. **数字要慢说**：4.49、48.22、9.87 pp 这些关键数字，说之前微停顿，说时加重语气
2. **过渡要自然**：用 "Now let's move to..." / "Building on that..." / "Here's where it gets interesting..." 衔接
3. **互动感**：开场可以问 "Have you ever tried talking to a voice assistant while it's still speaking?" 引起共鸣
4. **指向要明确**：手指伸直，对准具体区域，避免大幅度挥手
5. **时间控制**：如果发现听众注意力下降，跳到 §4 的三个 callout 数字直接给结论
6. **结尾留钩子**：提到 live demo 或 open-source plan，增加后续交流机会
