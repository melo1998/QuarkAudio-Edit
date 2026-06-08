"""
Speech Enhancement Inference Tool
==================================
Standalone inference script for multi-channel speech enhancement.
Input:  4-channel audio (B, 4, T) at 16kHz
Output: 2-channel enhanced audio (B, 2, T)

Usage:
    python inference.py --input input.wav --output output.wav --ckpt checkpoint.ckpt
"""

import argparse
import time
import numpy as np
import torch
import torch.nn as nn
import soundfile as sf


# ============================================================
# ERB Filter Bank
# ============================================================
class ERB(nn.Module):
    def __init__(self, erb_subband_1=64, erb_subband_2=64, nfft=512, high_lim=8000, fs=16000):
        super().__init__()
        self.erb_subband_1 = erb_subband_1
        nfreqs = nfft // 2 + 1
        erb_filters = self._build_erb_filters(erb_subband_1, erb_subband_2, nfft, high_lim, fs)
        self.erb_fc = nn.Linear(nfreqs - erb_subband_1, erb_subband_2, bias=False)
        self.ierb_fc = nn.Linear(erb_subband_2, nfreqs - erb_subband_1, bias=False)
        self.erb_fc.weight = nn.Parameter(erb_filters, requires_grad=False)
        self.ierb_fc.weight = nn.Parameter(erb_filters.T, requires_grad=False)

    @staticmethod
    def _hz2erb(freq_hz):
        return 21.4 * np.log10(0.00437 * freq_hz + 1)

    @staticmethod
    def _erb2hz(erb_f):
        return (10 ** (erb_f / 21.4) - 1) / 0.00437

    def _build_erb_filters(self, erb_subband_1, erb_subband_2, nfft, high_lim, fs):
        low_lim = erb_subband_1 / nfft * fs
        erb_low = self._hz2erb(low_lim)
        erb_high = self._hz2erb(high_lim)
        erb_points = np.linspace(erb_low, erb_high, erb_subband_2)
        bins = np.round(self._erb2hz(erb_points) / fs * nfft).astype(np.int32)
        erb_filters = np.zeros([erb_subband_2, nfft // 2 + 1], dtype=np.float32)
        erb_filters[0, bins[0]:bins[1]] = (bins[1] - np.arange(bins[0], bins[1]) + 1e-12) / (bins[1] - bins[0] + 1e-12)
        for i in range(erb_subband_2 - 2):
            erb_filters[i + 1, bins[i]:bins[i + 1]] = (np.arange(bins[i], bins[i + 1]) - bins[i] + 1e-12) / (bins[i + 1] - bins[i] + 1e-12)
            erb_filters[i + 1, bins[i + 1]:bins[i + 2]] = (bins[i + 2] - np.arange(bins[i + 1], bins[i + 2]) + 1e-12) / (bins[i + 2] - bins[i + 1] + 1e-12)
        erb_filters[-1, bins[-2]:bins[-1] + 1] = 1 - erb_filters[-2, bins[-2]:bins[-1] + 1]
        erb_filters = erb_filters[:, erb_subband_1:]
        return torch.from_numpy(np.abs(erb_filters))

    def bm(self, x):
        """Forward ERB transform: (B,C,T,F) -> (B,C,T,F_erb)"""
        x_low = x[..., :self.erb_subband_1]
        x_high = self.erb_fc(x[..., self.erb_subband_1:])
        return torch.cat([x_low, x_high], dim=-1)

    def bs(self, x_erb):
        """Inverse ERB transform: (B,C,T,F_erb) -> (B,C,T,F)"""
        x_erb_low = x_erb[..., :self.erb_subband_1]
        x_erb_high = self.ierb_fc(x_erb[..., self.erb_subband_1:])
        return torch.cat([x_erb_low, x_erb_high], dim=-1)


# ============================================================
# DPRNN Block
# ============================================================
class DPRNN_GRU(nn.Module):
    def __init__(self, emb_dim, hidden_dim):
        super().__init__()
        self.intra_rnn = nn.GRU(input_size=emb_dim, hidden_size=hidden_dim, batch_first=True, bidirectional=True)
        self.intra_fc = nn.Linear(hidden_dim * 2, emb_dim)
        self.inter_rnn = nn.GRU(input_size=emb_dim, hidden_size=hidden_dim, batch_first=True, bidirectional=False)
        self.inter_fc = nn.Linear(hidden_dim, emb_dim)

    def forward(self, x):
        b, c, t, f = x.shape
        x = x.permute(0, 2, 3, 1)
        intra_x = x.reshape(b * t, f, c)
        intra_x, _ = self.intra_rnn(intra_x)
        intra_x = self.intra_fc(intra_x)
        intra_x = intra_x.reshape(b, t, f, c)
        intra_out = x + intra_x

        x = intra_out.permute(0, 2, 1, 3)
        inter_x = x.reshape(b * f, t, c)
        inter_x, _ = self.inter_rnn(inter_x)
        inter_x = self.inter_fc(inter_x)
        inter_x = inter_x.reshape(b, f, t, c)
        inter_out = inter_x + x
        return inter_out.permute(0, 3, 2, 1)


# ============================================================
# SE-UNet Network
# ============================================================
class SE_UNET(nn.Module):
    def __init__(self, emb_dim=64, in_channels=3, out_channels=2, n_freqs=128, dprnn_num=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dprnn_num = dprnn_num

        self.en_conv1_1 = nn.Sequential(
            nn.ConstantPad2d((2, 2, 1, 0), 0.0),
            nn.Conv2d(in_channels, emb_dim, kernel_size=(2, 5), stride=(1, 2)),
            nn.ReLU(),
        )

        self.en_conv1_2 = nn.Sequential(
            nn.ConstantPad2d((2, 2, 1, 0), 0.0),
            nn.Conv2d(in_channels, emb_dim, kernel_size=(2, 5), stride=(1, 2)),
            nn.ReLU(),
        )

        self.en_conv1_3 = nn.Sequential(
            nn.ConstantPad2d((2, 2, 1, 0), 0.0),
            nn.Conv2d(in_channels, emb_dim, kernel_size=(2, 5), stride=(1, 2)),
            nn.ReLU(),
        )

        self.en_conv1_4 = nn.Sequential(
            nn.ConstantPad2d((2, 2, 1, 0), 0.0),
            nn.Conv2d(in_channels, emb_dim, kernel_size=(2, 5), stride=(1, 2)),
            nn.ReLU(),
        )

        # self.en_conv1_5 = nn.Sequential(
        #     nn.ConstantPad2d((2, 2, 1, 0), 0.0),
        #     nn.Conv2d(in_channels, emb_dim, kernel_size=(2, 5), stride=(1, 2)),
        #     nn.ReLU(),
        # )

        self.en_conv2 = nn.Sequential(
            nn.ConstantPad2d((2, 2, 1, 0), 0.0),
            nn.Conv2d(emb_dim, emb_dim, kernel_size=(2, 5), stride=(1, 2)),
            nn.ReLU(),
        )

        # self.en_conv1 = nn.Sequential(
        #     nn.ConstantPad2d((0, 0, 1, 0), 0.0),
        #     nn.Conv2d(in_channels, emb_dim, kernel_size=(2, 5), stride=(1, 2), padding=(0, 2)),
        #     nn.ReLU(),
        # )
        # self.en_conv2 = nn.Sequential(
        #     nn.ConstantPad2d((0, 0, 1, 0), 0.0),
        #     nn.Conv2d(emb_dim, emb_dim, kernel_size=(2, 5), stride=(1, 2), padding=(0, 2)),
        #     nn.ReLU(),
        # )

        # GRU for downsampled features
        # n_freqs = math.ceil(n_freqs / 2)
        # n_freqs = math.ceil(n_freqs / 2)
        self.dprnn_list = nn.ModuleList([DPRNN_GRU(emb_dim=emb_dim, hidden_dim=emb_dim * 2) for i in range(dprnn_num)])
        # self.dprnn1 = DPRNN_GRU(emb_dim=emb_dim, hidden_dim=emb_dim * 2)
        # self.dprnn2 = DPRNN_GRU(emb_dim=emb_dim, hidden_dim=emb_dim * 2)
        # self.dprnn3 = DPRNN_GRU(emb_dim=emb_dim, hidden_dim=emb_dim * 2)
        self.de_conv2 = nn.Sequential(
            nn.ConvTranspose2d(emb_dim, emb_dim, kernel_size=(1, 6), stride=(1, 2), padding=(0, 2)),
            nn.ReLU(),
        )
        self.de_conv1 = nn.Sequential(
            nn.ConvTranspose2d(emb_dim, emb_dim, kernel_size=(1, 6), stride=(1, 2), padding=(0, 2)),
            nn.ReLU(),
        )
        self.final_conv = nn.Conv2d(emb_dim, out_channels, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))

    def forward(self, spec1, spec2, spec3, spec4):
        """
        spec: (B, 3, T, F), F=128
        """
        #print("00000000000")
        en_conv1_1 = self.en_conv1_1(spec1)  # (B,D,T,64)
        en_conv1_2 = self.en_conv1_2(spec2)
        en_conv1_3 = self.en_conv1_3(spec3)
        en_conv1_4 = self.en_conv1_4(spec4)
        #en_conv1_5 = self.en_conv1_5(spec5)
        en_conv1 = en_conv1_1 + en_conv1_2 + en_conv1_3 + en_conv1_4 
        en_conv2 = self.en_conv2(en_conv1)  # (B,D,T,32)
        # print('encoder:',spec1.shape,en_conv1.shape,en_conv2.shape)
        
        for i in range(self.dprnn_num):
            if i==0:
                gru_out = self.dprnn_list[0](en_conv2)
            else:
                gru_out = self.dprnn_list[i](gru_out)
        # gru_out1 = self.dprnn1(en_conv2)
        # gru_out2 = self.dprnn2(gru_out1)
        # gru_out3 = self.dprnn3(gru_out2)
        de_conv2 = self.de_conv2(gru_out + en_conv2)
        # print(de_conv2.shape)
        de_conv1 = self.de_conv1(de_conv2 + en_conv1)
        # print(de_conv1.shape)
        final_conv = self.final_conv(de_conv1)
        # print('decoder:',gru_out.shape, de_conv2.shape, de_conv1.shape, final_conv.shape)
        return final_conv, gru_out

# ============================================================
# Inference Engine
# ============================================================
class SpeechEnhancer:
    """Self-contained speech enhancement inference engine."""

    N_FFT = 512
    HOP_LENGTH = 256
    COMPRESS_FACTOR = 0.3
    SAMPLE_RATE = 16000
    MAX_SEGMENT_SAMPLES = 16000 * 60 * 3  # 3 minutes max per segment

    def __init__(self, ckpt_path, device="cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.erb = ERB(erb_subband_1=64, erb_subband_2=64, nfft=512, high_lim=8000, fs=16000)
        self.dnn = SE_UNET(emb_dim=96, in_channels=3, out_channels=4, n_freqs=128, dprnn_num=8)
        self._load_checkpoint(ckpt_path)
        self.erb.to(self.device).eval()
        self.dnn.to(self.device).eval()
        self.window = torch.hann_window(self.N_FFT).sqrt().to(self.device)

    def _load_checkpoint(self, ckpt_path):
        """Load weights from .ckpt or .pt file."""
        checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        if "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint

        # Remove Lightning prefix and non-model keys
        cleaned_state_dict = {}
        for key, value in state_dict.items():
            clean_key = key
            for prefix in ["model.", "dnn.", "erb."]:
                if clean_key.startswith(prefix):
                    break
            # Keep dnn.* and erb.* keys, strip the top-level prefix if present
            if clean_key.startswith("model.dnn."):
                clean_key = clean_key[len("model."):]
            elif clean_key.startswith("model.erb."):
                clean_key = clean_key[len("model."):]
            # Skip teacher/adapter/pmsqe keys
            if any(skip in clean_key for skip in ["teacher", "adapter", "pmsqe"]):
                continue
            cleaned_state_dict[clean_key] = value

        # Load into sub-modules
        dnn_state = {k[4:]: v for k, v in cleaned_state_dict.items() if k.startswith("dnn.")}
        erb_state = {k[4:]: v for k, v in cleaned_state_dict.items() if k.startswith("erb.")}

        if dnn_state:
            self.dnn.load_state_dict(dnn_state, strict=False)
            print(f"  Loaded DNN weights: {len(dnn_state)} params")
        if erb_state:
            self.erb.load_state_dict(erb_state, strict=False)
            print(f"  Loaded ERB weights: {len(erb_state)} params")

    def _stft_compress(self, x):
        """STFT with magnitude compression. x: (B, T) -> (B, T_frames, F)"""
        spec = torch.stft(
            x, self.N_FFT, self.HOP_LENGTH,
            window=self.window, onesided=True, pad_mode="constant", return_complex=True,
        ).transpose(1, 2)
        mag = spec.abs() ** self.COMPRESS_FACTOR
        pha = spec.angle()
        return torch.complex(mag * pha.cos(), mag * pha.sin())

    def _decompress_istft(self, x, length):
        """Inverse STFT with magnitude decompression. x: (B, T_frames, F) -> (B, T)"""
        mag = x.abs() ** (1.0 / self.COMPRESS_FACTOR)
        pha = x.angle()
        x_decompressed = torch.complex(mag * pha.cos(), mag * pha.sin())
        return torch.istft(
            x_decompressed.transpose(-2, -1),
            self.N_FFT, self.HOP_LENGTH,
            window=self.window, onesided=True, length=length, return_complex=False,
        )

    @torch.no_grad()
    def enhance(self, wav_tensor):
        """
        Enhance 4-channel audio to 2-channel.

        Args:
            wav_tensor: (B, 4, T) float32 tensor at 16kHz

        Returns:
            (B, 2, T) enhanced audio tensor
        """
        assert wav_tensor.ndim == 3 and wav_tensor.shape[1] == 4, \
            f"Expected (B, 4, T), got {tuple(wav_tensor.shape)}"

        wav_tensor = wav_tensor.to(self.device)
        batch_size, num_channels, total_length = wav_tensor.shape

        # Process in segments to avoid OOM
        all_est1, all_est2 = [], []
        segment_length = self.MAX_SEGMENT_SAMPLES
        num_segments = total_length // segment_length + 1

        for seg_idx in range(num_segments):
            start = seg_idx * segment_length
            end = min((seg_idx + 1) * segment_length, total_length)
            if end - start < self.SAMPLE_RATE:
                continue
            #-----效果最好
            src1 = wav_tensor[:, 1, start:end]
            src2 = wav_tensor[:, 2, start:end]
            src3 = wav_tensor[:, 0, start:end]
            src4 = wav_tensor[:, 3, start:end]
            #-----效果最好次优
            # src1 = wav_tensor[:, 1, start:end]
            # src2 = wav_tensor[:, 2, start:end]
            # src3 = wav_tensor[:, 3, start:end]
            # src4 = wav_tensor[:, 0, start:end]
            # STFT + compress
            src1_spec = self._stft_compress(src1)
            feat2 = torch.stack([src1_spec.abs(), src1_spec.real, src1_spec.imag], dim=1)
            feat3 = torch.stack([self._stft_compress(src2).abs(), self._stft_compress(src2).real, self._stft_compress(src2).imag], dim=1)
            feat4 = torch.stack([self._stft_compress(src3).abs(), self._stft_compress(src3).real, self._stft_compress(src3).imag], dim=1)
            feat5 = torch.stack([self._stft_compress(src4).abs(), self._stft_compress(src4).real, self._stft_compress(src4).imag], dim=1)

            # ERB forward
            feat2 = self.erb.bm(feat2)
            feat3 = self.erb.bm(feat3)
            feat4 = self.erb.bm(feat4)
            feat5 = self.erb.bm(feat5)

            # Network forward (uses channels 2,3,4,1 as input order matching training)
            outputs, outputs_2 = self.dnn(feat2, feat3, feat4, feat5)

            outputs = self.erb.bs(outputs)  # (b,2,t,f)
            mask1 = torch.complex(outputs[:, 0], outputs[:, 1])
            mask2 = torch.complex(outputs[:, 2], outputs[:, 3])

            est_spec1 = src1_spec * mask1  
            est_spec2 = src1_spec * mask2

            # # Apply masks
            # mask1 = torch.complex(outputs_1[:, 0], outputs_1[:, 1])
            # mask2 = torch.complex(outputs_2[:, 0], outputs_2[:, 1])
            # est_spec1 = src1_spec * mask1
            # est_spec2 = src1_spec * mask2

            # ISTFT
            est1 = self._decompress_istft(est_spec1, length=src2.size(-1))
            est2 = self._decompress_istft(est_spec2, length=src2.size(-1))

            all_est1.append(est1)
            all_est2.append(est2)

        est1_full = torch.cat(all_est1, dim=-1)
        est2_full = torch.cat(all_est2, dim=-1)
        return torch.stack([est1_full, est2_full], dim=1)


# ============================================================
# Main Entry Point
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Speech Enhancement Inference")
    parser.add_argument("--input", default='./dataset/chat_0330.wav', help="Input 4-channel WAV file path")
    parser.add_argument("--output", default='./dataset/chat_0330_enh03.wav',  help="Output 2-channel WAV file path")
    parser.add_argument("--ckpt", type=str,
                        default="./epoch=16-step=70821-pesq=4.15.ckpt",
                        help="Checkpoint path (.ckpt or .pt)")
    parser.add_argument("--device", type=str, default="cuda:5", help="Device: cuda or cpu")
    args = parser.parse_args()
     
    # Load audio
    print(f"Loading audio: {args.input}")
    wav, sample_rate = sf.read(args.input, dtype="float32")
    assert sample_rate == 16000, f"Expected 16kHz, got {sample_rate}Hz"
    if wav.ndim == 1:
        raise ValueError("Input must be multi-channel audio, got mono")
    assert wav.shape[1] >= 4, f"Expected at least 4 channels, got {wav.shape[1]}"
    wav = wav[:, :4].T  # (T, 4) -> (4, T)
    wav_tensor = torch.from_numpy(wav).unsqueeze(0)  # (1, 4, T)
    print(f"  Input shape: {tuple(wav_tensor.shape)}, duration: {wav_tensor.shape[-1] / 16000:.1f}s")

    # Load model
    print(f"Loading checkpoint: {args.ckpt}")
    enhancer = SpeechEnhancer(args.ckpt, device=args.device)

    # Inference
    print("Running inference...")
    start_time = time.time()
    enhanced = enhancer.enhance(wav_tensor)
    elapsed = time.time() - start_time
    print(f"  Inference time: {elapsed:.3f}s")

    # Save output
    enhanced_np = enhanced.squeeze(0).cpu().numpy().T  # (2, T) -> (T, 2)
    enhanced_np = enhanced_np / (np.max(np.abs(enhanced_np)) + 1e-8)
    sf.write(args.output, enhanced_np, sample_rate)
    print(f"Saved enhanced audio: {args.output}")
    print(f"  Output shape: {enhanced_np.shape}, duration: {enhanced_np.shape[0] / 16000:.1f}s")


if __name__ == "__main__":
    main()