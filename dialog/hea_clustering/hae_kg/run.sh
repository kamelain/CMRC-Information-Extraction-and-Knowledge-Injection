CUDA_VISIBLE_DEVICES=1 python hae.py \
    --history=6 \
    --num_train_epochs=3.0 \
    --train_steps=24000 \
    --max_considered_history_turns=11 \
    --learning_rate=3e-05 \
    --warmup_proportion=0.1 \
    --evaluation_steps=1000 \
    --evaluate_after=20000 \
    --load_small_portion=False \
    --train_batch_size=8 \
    --max_answer_length=40>run_wn_seg.log