# Copyright (c) 2018, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script launches ResNet50 training in FP32 on 1 GPUs using 128 batch size (128 per GPU)
# Usage ./RN50_FP32_1GPU.sh <path to this repository> <path to dataset> <path to results directory>

python main.py --num_iter=180 --iter_unit=epoch --data_dir=$1  --batch_size=2048 --results_dir=$2
