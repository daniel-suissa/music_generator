# Music Generation with LSTMs

This project uses LSTMs to learn musical sequences and produces new sequences. The original MIDI data is not uploaded to the repo. Only the final preprocessed tracks are included in the "Smushed" folder. Smushed because the guitar tracks were extracted from original pop/rock songs and merged into one track. Of course this process distorts the melody slightly, but it is a small sacrifice that helps the training process. 


**Preprocessing**: refers to the process of extracting tracks and putting them in the "Smushed folder" merged into each other. The Full documentation of how to do it is not present in this repo at the moment, but the code is in the preprocessing.py file.

**Filtering**: refers to the process of choosing only desired sample sequences out of the data. This is done in the "filtering" jupyter notebook and documented there.

### If you just want to run it the model on the preprocessed & filtered data:
Run the "music_generator" notebook, it is currently set to load to final filtered data. If you want to load your own filtered data, make sure to change the appropriate filenames.

### If you want to run and configure the filtering
Run the "filter" notebook and play around with the parameters. The files will be saved to the "saved_data" folder. Make sure to not override existing files (you can always redownload them, but it can lead to confusion when things go wrong)

This project was originally done by [Beamlak Hailemariam
](https://www.linkedin.com/in/hailbeam/) and [Daniel Suissa
](https://www.linkedin.com/in/daniel-suissa-690823113/)