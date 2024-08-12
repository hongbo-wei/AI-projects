# Set up
As describe by [OpenAI](https://github.com/openai/whisper), Whisper is expected to be compatible with Python 3.8-3.11 and recent PyTorch versions.

## Activate virtual environment
    pipenv shell
    pipenv install

### Run the program
<span style="color:red">programs/apps/main.py</span>

#### Available models and languages

install the library of Whisper by OpenAI (should be included in `pipenv install`)

    pip install -U openai-whisper

|  Size  | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
|:------:|:----------:|:------------------:|:------------------:|:-------------:|:--------------:|
|  tiny  |    39 M    |     `tiny.en`      |       `tiny`       |     ~1 GB     |      ~32x      |
|  base  |    74 M    |     `base.en`      |       `base`       |     ~1 GB     |      ~16x      |
| small  |   244 M    |     `small.en`     |      `small`       |     ~2 GB     |      ~6x       |
| medium |   769 M    |    `medium.en`     |      `medium`      |     ~5 GB     |      ~2x       |
| large  |   1550 M   |        N/A         |      `large`       |    ~10 GB     |       1x       |