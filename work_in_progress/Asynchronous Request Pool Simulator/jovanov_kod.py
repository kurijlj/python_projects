def wrapper(func, arg, queue):
    queue.put(func(arg))

def execute_task_in_queues(my_func, my_chunks, queue_size=10):
    total = len(my_chunks)
    q_results = []
        for i in range((total//queue_size)+1):
            queues = []
            for j in range(min(queue_size, total-i*queue_size)):
                queues.append(Queue())
                Thread(
                    target=wrapper,
                    args=(my_func,
                          my_chunks[i*queue_size+j],
                          queues[j]
                         )
                    ).start()

                for q in tqdm(queues):  # what is tqdm?
                    q_results.append(q.get())

            if i < (total//queue_size):
            time.sleep(30)

    return q_results

#------------------------------------------------------------------------------------------------------------------------
# Primer pozivanja:

def transcribe_segment(input_data):
    t0 = time.time()
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        ffmpeg.input(str(input_data['audio_filepath']))\
            .filter("atrim", start=input_data['start'], end=input_data['end'])\
                .output(f.name)\
                    .overwrite_output()\
                        .run(quiet=True)

        with open(f.name, 'rb') as audio_file:
            result = openai.Audio.transcribe(
                "whisper-1",
                audio_file,
                response_format='verbose_json',
                language="en"
            )
            result_dict = result.to_dict()
            result_dict['segments'] = [res.to_dict() for res in result_dict['segments']]

            # Add back offsets.
            for segment in result_dict["segments"]:
                segment["start"] += input_data['start']
                segment["end"] += input_data['start']

    return result_dict

q_results = execute_task_in_queues(
    transcribe_segment,
    input_data,
    queue_size=30
)