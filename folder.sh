#!/bin/bash

ROOT="AI-Basics"

# Sub-structure for Machine Learning
ml_files=(
  "$ROOT/Machine_Learning/Deep_Learning/Basics/01_Perceptron.md"
  "$ROOT/Machine_Learning/Deep_Learning/Basics/02_MLPs.md"
  "$ROOT/Machine_Learning/Deep_Learning/Basics/03_Activation_Functions.md"
  "$ROOT/Machine_Learning/Deep_Learning/Basics/04_Loss_Functions.md"
  "$ROOT/Machine_Learning/Deep_Learning/Basics/05_Optimizers.md"
  "$ROOT/Machine_Learning/Deep_Learning/Basics/06_Regularization.md"
  "$ROOT/Machine_Learning/Deep_Learning/Basics/07_Training_Techniques.md"

  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/CNNs/01_Image_Classification.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/CNNs/02_Object_Detection.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/CNNs/03_Segmentation.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/CNNs/04_Advanced_CNNs.md"

  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/RNNs/01_Vanilla_RNNs.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/RNNs/02_LSTMs.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/RNNs/03_GRUs.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/RNNs/04_Seq2Seq.md"

  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/Transformers/01_Attention_Mechanism.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/Transformers/02_BERT.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/Transformers/03_GPT.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/Transformers/04_Vision_Transformers.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/Transformers/05_Hybrid_Models.md"

  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/GANs/01_Vanilla_GAN.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/GANs/02_DCGAN.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/GANs/03_Conditional_GAN.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/GANs/04_CycleGAN.md"
  "$ROOT/Machine_Learning/Deep_Learning/Neural_Nets/GANs/05_Diffusion_Models.md"

  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/LLMs/01_Pretraining.md"
  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/LLMs/02_FineTuning.md"
  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/LLMs/03_Prompt_Engineering.md"
  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/LLMs/04_Evaluation.md"

  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/Text_to_Image/01_Diffusion.md"
  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/Text_to_Image/02_StyleGAN.md"
  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/Text_to_Image/03_Applications.md"

  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/Text_to_Video/01_Diffusion.md"
  "$ROOT/Machine_Learning/Deep_Learning/Gen_AI/Text_to_Video/02_Applications.md"

)


# Create all folders and numbered files
for file in "${ml_files[@]}"; do
  mkdir -p "$(dirname "$file")"
  echo "# ${file##*/}" | sed 's/.md$//' | sed 's/_/ /g' > "$file"
done


echo "✅ AI-Basics repo structure created with numbered .md files."
