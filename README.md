

# Image Generation

This repository contains pytorch implementations of various generative models to generate images on multiple datasets. I wanted to use datasets other than MNIST to make it a bi more interesting, so I tried some models on a dataset of paintings of a painter that I like a lot ([Odilon Redon](https://www.odilon-redon.org/)), and on a dataset of all pokemon sprites from every game. Datasets are covered mode in details in the following sections.

## Table of content
- [Getting started](https://github.com/dvidbruhm/ImageGeneration#getting-started)
- [Datasets](https://github.com/dvidbruhm/ImageGeneration#datasets)
- [Models](https://github.com/dvidbruhm/ImageGeneration#models)
  - [GANs](https://github.com/dvidbruhm/ImageGeneration#generative-adversarial-networks-gan)
    - [DCGAN](https://github.com/dvidbruhm/ImageGeneration#dcgan)
    - [LSGAN](https://github.com/dvidbruhm/ImageGeneration#lsgan)
    - [CGAN](https://github.com/dvidbruhm/ImageGeneration#conditional-gan-cgan)
  - [Autoencoders](https://github.com/dvidbruhm/ImageGeneration#autoencoders)
    - [Autoencoder](https://github.com/dvidbruhm/ImageGeneration#autoencoder)
    - [VAE](https://github.com/dvidbruhm/ImageGeneration#variational-autoencoder-vae)

# Getting started

## Prerequisites

- [Python 3](https://www.python.org/downloads/)
- [Pytorch](https://pytorch.org/) (with torchvision)
- [Matplotlib](https://matplotlib.org/)
  ```
  pip3 install matplotlib
  ```
  
## Usage

Each model resides in a folder of its own. To run a model, first clone the repository:

```
git clone https://github.com/dvidbruhm/PokeGeneration.git
```

Then, while in the folder of the model you wish to run:

```
python3 <model name>.py
```

For example, if you wish to run the DCGAN model, ```cd``` to the DCGAN folder, then:

```
python3 DCGAN.py
```

The results for every epoch will be (by default) in a folder named ```results_<dataset name>/```. For every epoch there will be an example of generated images and a plot of the loss. At the end of the training all models are saved in this folder.

## Customization

Every model folder has a file named ```hyperparameters.py```. If you want to use different parameters for a model, modify any parameters in this file to your liking and rerun the script. The names of the parameters should be mostly self-explanatory. Note that I use a file instead of command line options to modify parameters because I find it more convenient.

# Datasets

The paintings and pokemon datasets used can be found on [this google drive](https://drive.google.com/open?id=1WpPrdORSTyya1aGTeobGbC8BlOSYlNoC). MNIST and FASHIONMNIST will automatically be downloaded if you don't have them.

Images of all datasets are resized to either 32x32 of 64x64 pixels before using them.

### MNIST

MNIST is a dataset containing 60000 grayscale handwritten digits images. There are 10 classes (digits from 0 to 9) and all images have been normalized and centered to fit into a 28x28 pixels bounding box. It is a standard dataset to test and see if your model works. 

### Fashion MNIST

[FASHIONMNIST](https://github.com/zalandoresearch/fashion-mnist) is a MNIST-like dataset of fashion product. It also has 60000 grayscale 28x28 pixels images. It has 10 classes (T-shirt, trouser, pullover, ...). It has been created because MNIST might be too easy to test your models, and because the creators think MNIST is overused. 

### Paintings

This is a custom made dataset containing all 590 paintings of [Odilon Redon](https://www.odilon-redon.org/). All images have been resized (and croped if the original image wasn't square) to 64x64 pixels. The images in this dataset are in color, so they have three channels instead of only one like MNIST and FASHIONMNIST.

### Pokemon

This is also a custom make dataset containg all the 4744 images of all pokemon sprites of all games. The background of the sprites have been modified to white for unicity (some of them were black or pink). The images are in colors, so have three channels.

# Models

Here is the detail implementation and results of each model and the results for each one on every dataset.

## Generative adversarial networks (GAN)
**[[Paper arxiv link](https://arxiv.org/abs/1406.2661)]**

In a GAN, two networks try to outperform each other. The first one, the generator, generates new data and tries to fool the second network, the discriminator, into thinking it is a real data (from the dataset) and not a new generated data. 

The generator is a network that takes a vector of random numbers in input and outputs an image. The input of the generator, so the vector of random numbers, is called the latent space. The vector associated to an image is called the latent representation of the image.

The discrimator is a network that takes an image in input and returns a single number between 0 and 1. The number represents the probability that the image is real. If the discrimator outputs a 1, it really thinks that the image is real. If it outputs a 0, it really thinks that the image is fake (generated by the generator). If it outputs anything in between, it is not sure if the image is real or fake.

Let's take for example the MNIST dataset. The goal of the generator is to produce new handwritten digits that are so close to real ones that the discriminator can't distinguish between the generated digits and the original handwritten ones. And the goal of the discriminator is to not let itself being fooled by the generator. Every iteration, both networks are trained one after the other. The steps, for one iteration, are:

Training of the discriminator:
- The generator takes in a batch of vectors of random numbers sampled from a gaussian distribution and generates a batch of images
- The discriminator takes in the batch of generated images and returns its predictions
- The discriminator takes in a batch of real data from the dataset and returns its predictions
- Update the discriminator according to this loss:

<img src="https://latex.codecogs.com/svg.latex?\Large&space;Loss_D=log(D(real\_data))+log(1-D(G(latent\_input)))" title="discriminator loss" />

Training of the generator:
- The generator takes in a batch of vectors of random numbers sampled from a gaussian distribution and generates a batch of images
- The discriminator takes in the batch of generated images and returns its predictions
- Update the generator according to this loss:

<img src="https://latex.codecogs.com/svg.latex?\Large&space;Loss_G=log(D(G(latent\_input)))" title="discriminator loss" />

In general, GANs can suffer of mode collapse or vanishing gradients. Some techniques I used to help the training process includes:
- [Label smoothing](https://arxiv.org/abs/1606.03498)
- [Packing](https://arxiv.org/pdf/1712.04086.pdf)
- Using multiple steps for the generator and/or discriminator for each iteration

### DCGAN
**[[Paper arxiv link](https://arxiv.org/abs/1511.06434)]**

DCGAN is the same as a standard GAN, but the generator and discriminator are composed of convolutional layers instead of fully connected layers. They are more suited for images and are faster to train due to them having less weights.

#### Results

*MNIST*

<img src="images/dcgan_results_mnist.gif">

*FASHIONMNIST*

<img src="images/dcgan_results_fashionmnist.gif" width="320">

*Paintings*

<img src="images/dcgan_results_paintings.gif">

*Pokemon*

<img src="images/dcgan_results_pokemon.gif">

### LSGAN
**[[Paper arxiv link](https://arxiv.org/abs/1611.04076)]**

LSGAN is the same as DCGAN, but the loss functions are changed. For the discriminator:

<img src="https://latex.codecogs.com/svg.latex?\Large&space;Loss_D=(D(real\_data)-1)^2+D(G(latent\_input))^2" title="discriminator loss" />

and for the generator:

<img src="https://latex.codecogs.com/svg.latex?\Large&space;Loss_G=(D(G(latent\_input))-1)^2" title="discriminator loss" />

#### Results

### Conditional GAN (CGAN)
**[[Paper arxiv link](https://arxiv.org/abs/1411.1784)]**

TODO: add explication of CGAN

#### Results

*FASHIONMNIST*

<img src="images/cgan_results_fashionmnist.gif">

## Autoencoders

TODO: add explication of autoencoders

### Autoencoder

#### Results

*Pokemon*

![encoded](images/autoencoder/pokemon/result.png)

### Variational autoencoder (VAE)
**[[Paper arxiv link](https://arxiv.org/pdf/1312.6114.pdf)]**

TODO: add explication of VAEs

#### Results

*Pokemon*

<img src="images/VAE_results_pokemon.gif">
