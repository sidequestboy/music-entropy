music-entropy
=============

Finds Shannon's relative entropy of .wav files

For now, only handles stereo, 16-bit sample width .wav files.

Usage
------
For usage information type:
```
./music.py help
```

Examples
---------
### Plots
```
./music.py plot time '~/01 Roar.wav'
./music.py plot freq '~/01 Roar.wav'

```

### Shannon's Relative Entropy
```
./music.py get_shannon_rel_entropy '~/02 - De Praestigiis Daemonum.wav'
```
