# !/usr/bin/env python
# -*- coding: utf-8 -*-

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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import warnings

warnings.simplefilter("ignore")

import tensorflow as tf

import horovod.tensorflow as hvd
from utils import hvd_utils

from runtime import Runner

from utils.cmdline_helper import parse_cmdline

if __name__ == "__main__":

  tf.logging.set_verbosity(tf.logging.ERROR)

  FLAGS = parse_cmdline()

  RUNNING_CONFIG = tf.contrib.training.HParams(
    mode=FLAGS.mode,

    # ======= Directory HParams ======= #
    log_dir=FLAGS.results_dir,
    model_dir=FLAGS.model_dir,
    summaries_dir=FLAGS.results_dir,
    data_dir=FLAGS.data_dir,
    storage_bucket_dir=FLAGS.storage_bucket_dir,

    # ========= Model HParams ========= #
    # n_classes=1001,
    n_classes=10,
    input_format='NHWC',
    compute_format=FLAGS.data_format,
    dtype=tf.float32 if FLAGS.precision == "fp32" else tf.float16,
    height=32,
    width=32,
    n_channels=3,

    # ======= Training HParams ======== #
    iter_unit=FLAGS.iter_unit,
    num_iter=FLAGS.num_iter,
    warmup_steps=FLAGS.warmup_steps,
    batch_size=FLAGS.batch_size,
    log_every_n_steps=FLAGS.display_every,
    learning_rate_init=FLAGS.lr_init,
    weight_decay=FLAGS.weight_decay,
    momentum=FLAGS.momentum,
    loss_scale=FLAGS.loss_scale,
    use_auto_loss_scaling=FLAGS.use_auto_loss_scaling,
    distort_colors=False,

    # ======= Optimization HParams ======== #
    use_xla=FLAGS.use_xla,
    use_tf_amp=FLAGS.use_tf_amp,
    use_fast_math=FLAGS.use_fast_math,

    seed=FLAGS.seed,
  )

  # ===================================

  runner = Runner(
    # ========= Model HParams ========= #
    n_classes=RUNNING_CONFIG.n_classes,
    input_format=RUNNING_CONFIG.input_format,
    compute_format=RUNNING_CONFIG.compute_format,
    dtype=RUNNING_CONFIG.dtype,
    n_channels=RUNNING_CONFIG.n_channels,
    height=RUNNING_CONFIG.height,
    width=RUNNING_CONFIG.width,
    distort_colors=RUNNING_CONFIG.distort_colors,
    model_dir=RUNNING_CONFIG.model_dir,
    log_dir=RUNNING_CONFIG.log_dir,
    data_dir=RUNNING_CONFIG.data_dir,
    storage_bucket_dir=RUNNING_CONFIG.storage_bucket_dir,

    # ======= Optimization HParams ======== #
    use_xla=RUNNING_CONFIG.use_xla,
    use_tf_amp=RUNNING_CONFIG.use_tf_amp,
    use_fast_math=RUNNING_CONFIG.use_fast_math,

    seed=RUNNING_CONFIG.seed
  )

  if RUNNING_CONFIG.mode in ["train", "train_and_evaluate", "training_benchmark"]:
    runner.train(
      iter_unit=RUNNING_CONFIG.iter_unit,
      num_iter=RUNNING_CONFIG.num_iter,
      batch_size=RUNNING_CONFIG.batch_size,
      warmup_steps=RUNNING_CONFIG.warmup_steps,
      log_every_n_steps=RUNNING_CONFIG.log_every_n_steps,
      weight_decay=RUNNING_CONFIG.weight_decay,
      learning_rate_init=RUNNING_CONFIG.learning_rate_init,
      momentum=RUNNING_CONFIG.momentum,
      loss_scale=RUNNING_CONFIG.loss_scale,
      use_auto_loss_scaling=FLAGS.use_auto_loss_scaling,
      is_benchmark=RUNNING_CONFIG.mode == 'training_benchmark',
    )

  if RUNNING_CONFIG.mode in ["train_and_evaluate", 'evaluate', 'inference_benchmark']:

    if RUNNING_CONFIG.mode == 'inference_benchmark' and hvd_utils.is_using_hvd():
      raise NotImplementedError("Only single GPU inference is implemented.")

    elif not hvd_utils.is_using_hvd() or hvd.rank() == 0:

      runner.evaluate(
        iter_unit=RUNNING_CONFIG.iter_unit if RUNNING_CONFIG.mode != "train_and_evaluate" else "epoch",
        num_iter=RUNNING_CONFIG.num_iter if RUNNING_CONFIG.mode != "train_and_evaluate" else 1,
        warmup_steps=RUNNING_CONFIG.warmup_steps,
        batch_size=RUNNING_CONFIG.batch_size,
        log_every_n_steps=RUNNING_CONFIG.log_every_n_steps,
        is_benchmark=RUNNING_CONFIG.mode == 'inference_benchmark'
      )
