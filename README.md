<p align="center">
⭐ Please remember to star this repo if you find it useful and cite our work if you use it in your research! ⭐
</p>
<p align="center">
🩺 If you have any questions or feedback, please create an <a href="https://github.com/yahskapar/HealthChat/issues">issue</a>! 🩺
</p>

# <img src="./figures/title_icon.png" alt="HealthChat Icon" width="25" /> HealthChat-11K

This repository contains the official code to reconstruct **HealthChat-11K**, a curated dataset of approx. 11,000 real-world conversations where users seek healthcare information from Large Language Models (LLMs). The goal of this work is to provide a high-quality resource for systematically studying and improving health conversations involving humans and AI (e.g., LLMs). **HealthChat-11K** corresponds to an EMNLP 2025 Findings paper - ["What's Up, Doc?": Analyzing How Users Seek Health Information in Large-Scale Conversational AI Datasets](https://arxiv.org/abs/2506.21532).

This codebase fetches conversational data from large-scale source datasets and merges it with our detailed annotations to produce the final, ready-to-use dataset.

## 📝 Project Status

- [x] Release `v1.0.0` of the master annotations and dataset artifacts generation script.
- [x] Complete additional, minor taxonomy revisions and update master annotations.
- [x] Release `v2.0.0` of the master annotations and dataset artifacts generation script.
- [x] Release `v2.1.0` — dual-license-by-upstream-source reissue (same data and schema as `v2.0.0`; only license metadata changed). See [Licensing](#-licensing) for details.

## 🗂️ Dataset Composition

The final dataset is a composition of three parts: two large-scale source datasets and our own layer of annotations. The script in this repository automates the process of combining them.

1.  **Source Datasets (The Raw Text):** Our conversations are filtered from two public datasets:
    * [lmsys/lmsys-chat-1m](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)
    * [allenai/WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M)

2.  **HealthChat Annotations (Our Contribution):** We provide a master annotation file containing our core analysis, including a clinician-driven taxonomy, specialty classifications, and sycophancy analysis. This file is hosted on the Hugging Face Hub:
    * [yahskapar/HealthChat-11K](https://huggingface.co/datasets/yahskapar/HealthChat-11K)

3.  **Final Dataset (The Output):** The script in this repo uses our annotations file to pull the correct conversations from the source datasets and generate the final, merged `HealthChat-11K_v2.1.0.jsonl` file.

## 🔧 Setup

This project uses Conda for environment management. The following steps will create a clean environment and install all necessary dependencies.

**STEP 1: Clone the repository**
```bash
git clone https://github.com/yahskapar/HealthChat.git
cd HealthChat
```

**STEP 2: Run the setup script**
This will create a `healthchat` conda environment with Python 3.13 and install the required packages.
```bash
bash setup.sh
```

**STEP 3: Activate the environment**
```bash
conda activate healthchat
```

## 💻 Generating HealthChat-11K

Once the setup is complete, you can generate the full `HealthChat-11K` dataset and the accompanying review files by running the main script.

```bash
python generate_artifacts.py
```

This will perform the following steps:
1.  Download the master annotation file (`v2.1.0`) from the Hugging Face Hub.
2.  Stream the source datasets (`lmsys-chat-1m` and `WildChat-1M`) to find the required conversations.
3.  Merge the source data with the annotations.
4.  Save all generated files into a new directory named **`HealthChat-11K_v2.1.0_artifacts/`**.

This output directory will contain:
* `HealthChat-11K_v2.1.0.jsonl`: The final, complete dataset.
* `HealthChat-11K_v2.1.0_full_review.csv`: A CSV with every conversation turn for review.
* `HealthChat-11K_v2.1.0_sycophancy_review.csv`: A CSV with leading questions seeking treatment (LQST) annotations marked for review.

## 📜 Citation

If you use the HealthChat dataset or the code in this toolbox for your research, please cite our work.
```bibtex
@article{paruchuri2025s,
  title={" What's Up, Doc?": Analyzing How Users Seek Health Information in Large-Scale Conversational AI Datasets},
  author={Paruchuri, Akshay and Aziz, Maryam and Vartak, Rohit and Ali, Ayman and Uchehara, Best and Liu, Xin and Chatterjee, Ishan and Agrawal, Monica},
  journal={arXiv preprint arXiv:2506.21532},
  year={2025}
}
```

## ⚖️ Licensing

Starting with `v2.1.0`, the dataset is **dual-licensed by upstream source**. Each subset inherits the terms of its upstream corpus — no new restrictive prose has been added. Downstream users can filter by the existing `dataset_source` field to select the subset that matches their use case.

* **Code:** All source code in this repository (e.g., `generate_artifacts.py`, `setup.sh`) is licensed under the **MIT License**.

* **Data Annotations — LMSYS-derived subset** (`dataset_source == "lmsys"`, ~61.8% of conversations / 6,780 conversations): Licensed under the **[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)** License. The non-commercial restriction is inherited from [LMSYS-Chat-1M's upstream terms](https://huggingface.co/datasets/lmsys/lmsys-chat-1m); commercial use is **not** permitted on this subset.

* **Data Annotations — WildChat-derived subset** (`dataset_source == "wildchat"`, ~38.2% of conversations / 4,185 conversations): Licensed under the **[Open Data Commons Attribution License 1.0 (ODC-BY 1.0)](https://opendatacommons.org/licenses/by/1-0/)**, matching [WildChat-1M's upstream license](https://huggingface.co/datasets/allenai/WildChat-1M) (relicensed by AI2 from the prior ImpACT terms on 2024-06-26, retroactive). Commercial use **is** permitted with attribution.

**Attribution:** When using either subset, please cite the HealthChat-11K paper (see [Citation](#-citation)) and the applicable upstream dataset (LMSYS-Chat-1M and/or WildChat-1M).

Users are responsible for independently complying with each upstream dataset's terms in addition to the annotation license above.
