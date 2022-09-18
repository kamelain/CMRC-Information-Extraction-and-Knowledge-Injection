from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import json
import math
import os
import modeling
import optimization
import tokenization
import six
import tensorflow as tf
import numpy as np

def cqa_gen_batches(features, batch_size, num_epoches, shuffle=False):
    num_examples = len(features)
    
    if shuffle:
        np.random.seed(0)
        idx = np.random.permutation(num_examples)
        features_shuffled = np.asarray(features)[idx]
    else:
        features_shuffled = np.asarray(features)

    num_steps = math.ceil(num_examples / batch_size)
    for _ in range(int(num_epoches)):
        i = 0
        for _ in range(num_steps):
            batch_features = features_shuffled[i: i + batch_size]
            
            batch_unique_ids = []
            batch_input_ids = []
            batch_input_mask = []
            batch_segment_ids = []
            batch_cls_ids = []
            batch_kpos_ids = []
            batch_start_positions = []
            batch_end_positions = []
            batch_history_answer_marker = []
            batch_metadata = []
            for feature in batch_features:
                batch_unique_ids.append(feature.unique_id)
                batch_input_ids.append(feature.input_ids)
                batch_input_mask.append(feature.input_mask)
                batch_segment_ids.append(feature.segment_ids)
                batch_cls_ids.append(feature.cls_ids)
                batch_kpos_ids.append(feature.kpos_ids)
                batch_start_positions.append(feature.start_position)
                batch_end_positions.append(feature.end_position)
                batch_history_answer_marker.append(feature.history_answer_marker)
                batch_metadata.append(feature.metadata)
            
            i += batch_size
            
            yield (batch_unique_ids, batch_input_ids, batch_input_mask, batch_segment_ids, batch_cls_ids, batch_kpos_ids,  
                   batch_start_positions, batch_end_positions, batch_history_answer_marker, batch_metadata)
            
def cqa_gen_example_batches(examples, batch_size, num_epoches, shuffle=False):
    num_examples = len(examples)
    
    if shuffle:
        np.random.seed(0)
        idx = np.random.permutation(num_examples)
        examples_shuffled = np.asarray(examples)[idx]
    else:
        examples_shuffled = np.asarray(examples)

    num_steps = math.ceil(num_examples / batch_size)
    for _ in range(int(num_epoches)):
        i = 0
        for _ in range(num_steps):
            batch_examples = examples_shuffled[i: i + batch_size]
            i += batch_size
            yield batch_examples
        
        
def cqa_gen_example_aware_batches(features, example_tracker, variation_tracker, example_features_nums, batch_size, num_epoches, shuffle=False):
    # generate example-aware batches: generate batches that contain the features for FLAGS.example_batch_size examples
    # the training examples have been shuffled before this function, so no need to shuffle here
    
    # num_examples = len(features)
    
    # if shuffle:
    #     np.random.seed(0)
    #     idx = np.random.permutation(num_examples)
    #     features_shuffled = np.asarray(features)[idx]
    # else:
    #     features_shuffled = np.asarray(features)

    # num_steps = math.ceil(num_examples / batch_size)
    
    for _ in range(int(num_epoches)):
        # we greedily select all the features that are generated by the next example, 
        # as long as the sum of example_features does not exceed FLAGS.train_batch_size        
        start_example_index, end_example_index = 0, 0
        while start_example_index in example_tracker:
            features_sum = example_features_nums[start_example_index]
            while features_sum <= batch_size:
                end_example_index += 1
                try:
                    features_sum += example_features_nums[end_example_index]
                except:
                    break
                
            start_index = example_tracker.index(start_example_index)
            # sometimes an example generates more features than a batch can handle
            if end_example_index == start_example_index:
                end_example_index += 1
            try:
                end_index = example_tracker.index(end_example_index)
            except:
                end_index = None
            
            batch_features = features[start_index: end_index]
            batch_example_tracker = example_tracker[start_index: end_index]
            batch_variation_tracker = variation_tracker[start_index: end_index]    
                
            start_example_index = end_example_index
            assert len(batch_features) > 0
            yield batch_features, batch_example_tracker, batch_variation_tracker
            
        print('epoch finished!')
    
    
    
#     for _ in range(int(num_epoches)):
#         start_example_index = 0
#         end_example_index = start_example_index + example_batch_size # this is actually the first example index in the next batch
        
#         while start_example_index in example_tracker:
#             start_index = example_tracker.index(start_example_index)
#             try:
#                 end_index = example_tracker.index(end_example_index)
#             except:
#                 end_index = None
#             batch_features = features[start_index: end_index]
#             batch_example_tracker = example_tracker[start_index: end_index]
#             batch_variation_tracker = variation_tracker[start_index: end_index]
            
#             start_example_index += example_batch_size
#             end_example_index += example_batch_size
            
#             yield batch_features, batch_example_tracker, batch_variation_tracker
            
#         print('epoch finished!')
            