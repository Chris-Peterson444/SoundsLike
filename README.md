# Project code for LIN205A Project -- UC Davis, Spring 2022

## Single Word Model
There is a Google Colab [demonstration notebook](https://colab.research.google.com/drive/1i-BlN8wgqDfthOz1rfex_xnF51yx8jTh?usp=sharing) on how to run inference using our final model. There is also the [data generation notebook](https://colab.research.google.com/drive/1icJxHyUS4I7S46zckqTQylqiVknvyy8g?usp=sharing)

## Multi-word span
There is a [single notebook](https://colab.research.google.com/drive/1uq0Tw5ogphnFONg9CtlKdVRI8WkzROQu?usp=sharing) for generating the context span data and training the model. No inference. 

### Running the nearest pronunciation FST
See the single word model demonstration notebook. Didn't want to turn Kenji's code into a package and fiddle with making the FST pickling work. So I had to port most of the working code into google colab to make sure it worked there.


# To-Do
- [x] Finish Generative Grammar Vectors
- [x] Geneate FST
- [x] Decide on a dataset(s) for classification
- [x] Generate Sequence Classifier
- [x] Write Report
- [x] Tidy up Presentation
