# Audio and Speech AI — Interview Q&A

## Beginner Level

**Q1: What is Whisper and what makes it different from earlier STT systems?**
**A:** Whisper is OpenAI's open-source speech-to-text model released in 2022. What sets it apart: (1) trained on 680,000 hours of diverse multilingual audio from the internet, making it robust to noise, accents, and domains; (2) supports 99 languages out of the box; (3) can translate non-English speech directly to English text; (4) produces word-level timestamps; (5) available as an open-source model you can run locally. Earlier STT systems required extensive fine-tuning for different accents, domains, or noise conditions. Whisper handles these generically.

**Q2: What is TTS and what are the main providers?**
**A:** TTS (Text-to-Speech) converts written text to spoken audio. Main providers: OpenAI TTS (voices: alloy, echo, fable, onyx, nova, shimmer — fast and cheap), ElevenLabs (highest quality, voice cloning, slightly more expensive), Google Cloud TTS (WaveNet voices, cheap at scale), Azure TTS (extensive voice library). ElevenLabs is the quality leader for realistic speech; OpenAI TTS is the best value for simple applications.

**Q3: What is a voice agent pipeline?**
**A:** A voice agent chains three AI systems: (1) STT — converts user's spoken words to text, (2) LLM — processes the text and generates a response, (3) TTS — converts the response text to spoken audio. The user speaks, the agent listens (STT), thinks (LLM), and speaks back (TTS). This creates a natural conversational interface similar to a phone call rather than a chatbot.

---

## Intermediate Level

**Q4: What is a log-Mel spectrogram and why does Whisper use it?**
**A:** A log-Mel spectrogram is a 2D representation of audio that shows frequency content over time, scaled to match human auditory perception. To create it: (1) split audio into 25ms frames overlapping every 10ms, (2) apply FFT to get frequency content of each frame, (3) apply mel-scale filterbank (compresses high frequencies, matches how humans hear), (4) take the log (matches how humans perceive loudness). The result is a 2D array of shape (80, time_frames) — essentially a picture of sound that a transformer can process. Whisper uses it because transformers process sequences well, and a spectrogram is a natural sequence representation of audio.

**Q5: What are the main trade-offs between Whisper model sizes?**
**A:** Whisper comes in 5 sizes: tiny (39M params), base (74M), small (244M), medium (769M), large (1.5B). Trade-offs:
- **tiny/base**: Very fast (10–30x real-time), small memory (<2GB), good for English but weaker on accents and noisy audio
- **medium**: Good balance, ~2x real-time, 5GB memory, handles most real-world audio well
- **large-v3**: Best accuracy (~1.9% WER on English), 10GB memory, ~1x real-time, recommended for production accuracy
For production via API (OpenAI Whisper API), always gets large-v3. For local deployment, choose based on hardware and latency requirements.

**Q6: What are the main latency challenges in voice agents and how do you address them?**
**A:** Three sequential latencies add up:
1. **STT**: 1–3s with Whisper (local); 0.5–1s via API
2. **LLM**: 1–5s depending on response length and model
3. **TTS**: 0.5–2s
Total: 3–10s per turn, which feels sluggish. Solutions:
- **Streaming STT**: Deepgram or AssemblyAI provide streaming transcription — output starts arriving before recording ends
- **Streaming LLM + TTS**: Start TTS as soon as the first sentence of the LLM response arrives, stream the rest
- **Smaller models**: Use faster but less capable models if latency is more important than quality
- **Voice Activity Detection**: Detect end of speech faster to start processing immediately

---

## Advanced Level

**Q7: What is voice cloning and what are the ethical considerations?**
**A:** Voice cloning is a TTS technique where the model is conditioned on a short reference recording (typically 5–30 seconds) of a target speaker and learns to mimic that speaker's voice characteristics: pitch, timbre, cadence, accent. ElevenLabs and other providers offer this. Ethical considerations: (1) consent — cloning someone's voice without permission enables fraud and harassment; (2) deepfake risk — cloned voices can be used to impersonate people in audio calls; (3) data privacy — reference recordings may contain personally identifiable data; (4) attribution — generated speech should be labeled as synthetic. Responsible use requires explicit consent from the voice owner. Never clone voices without explicit written consent.

**Q8: How does Whisper handle multilingual audio and translation?**
**A:** Whisper was trained as a multitask model with four tasks simultaneously: transcribe in original language, translate to English, detect language, and detect non-speech. The decoder is conditioned with special task tokens: `<|transcribe|>` or `<|translate|>`. For translation, the model has learned to internally understand content across 99 languages and map it to English output in one step — no separate translation step needed. Language detection is also automatic — you don't need to specify the language. This makes Whisper especially powerful for multilingual environments.

**Q9: System design question: Design a real-time voice meeting assistant that transcribes, diarizes (identifies who is speaking), and summarizes.**
**A:** Architecture:
1. **Audio capture**: Capture meeting audio with participant metadata if available (Zoom SDK, Teams SDK, or WebRTC)
2. **Streaming transcription**: Send audio chunks to streaming STT (Deepgram real-time or AssemblyAI streaming) for low-latency transcription with word timestamps
3. **Speaker diarization**: Use pyannote.audio or AssemblyAI's diarization to label speaker turns ("Speaker 1", "Speaker 2")
4. **Speaker identification**: If reference audio samples are available, match diarized segments to known participant voices
5. **Incremental storage**: Store transcript segments with timestamps and speaker labels in a database in real-time
6. **Live summarization**: Every 5 minutes, run LLM summarization on the latest 10 minutes of transcript → rolling summary
7. **Post-meeting processing**: Full LLM pass over complete transcript → structured meeting notes (action items, decisions, key points)
8. **Output**: Real-time transcript display + post-meeting email with notes
Key technical challenges: latency in diarization (adds 1–3s delay), speaker identification accuracy in noisy calls, handling cross-talk.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Whisper + voice pipeline code |

⬅️ **Prev:** [04 — Using Vision APIs](../04_Using_Vision_APIs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 — Multimodal Embeddings](../06_Multimodal_Embeddings/Theory.md)
