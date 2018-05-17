import torch
import torch.nn
import torch.optim as optim

from torchvision import datasets
import torchvision.transforms as transforms

from hyperparameters import *
from models import Generator32 as Generator, Discriminator32 as Discriminator
from utils import *

import matplotlib.pyplot as plt
import matplotlib.image as image

class DCGANTrainer():
    def __init__(self, save_path=SAVE_PATH, beta1=BETA1, beta2=BETA2, 
                 nb_image_to_gen=NB_IMAGE_TO_GENERATE, latent_input=LATENT_INPUT,
                 image_size=IMAGE_SIZE, weights_mean=WEIGHTS_MEAN, weights_std=WEIGHTS_STD,
                 model_complexity=COMPLEXITY, learning_rate=LEARNING_RATE, packing=PACKING,
                 real_label_smoothing=REAL_LABEL_SMOOTHING, fake_label_smoothing=FAKE_LABEL_SMOOTHING,
                 dropout_prob=DROPOUT_PROB, nb_discriminator_step=NB_DISCRIMINATOR_STEP):

        self.latent_input = latent_input
        self.nb_image_to_gen = nb_image_to_gen
        self.image_size = image_size
        self.save_path = save_path
        self.packing = packing
        self.real_label_smoothing = real_label_smoothing
        self.fake_label_smoothing = fake_label_smoothing
        self.nb_discriminator_step = nb_discriminator_step
        
        # Device (cpu or gpu)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # Models
        self.generator = Generator(latent_input, model_complexity, dropout_prob, weights_mean, weights_std).to(self.device)
        self.discriminator = Discriminator(model_complexity, weights_mean, weights_std, packing).to(self.device)

        # Optimizers
        self.D_optimiser = optim.Adam(self.discriminator.parameters(), lr = learning_rate, betas = (beta1, beta2))
        self.G_optimiser = optim.Adam(self.generator.parameters(), lr = learning_rate, betas = (beta1, beta2))

        self.generator_losses = []
        self.discriminator_losses = []

        self.saved_latent_input = torch.randn((nb_image_to_gen, latent_input, 1, 1)).to(self.device)

    def load_dataset(self, path_to_data=DATA_PATH):
        print("Loading dataset in : ", path_to_data)

        transform = transforms.Compose([
                        transforms.ToTensor(),
                        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])

        train_set = datasets.ImageFolder(root=path_to_data, transform=transform)

        print('Number of images: ', len(train_set))
        print('Sample image shape: ', train_set[0][0].shape, end='\n\n')
        
        self.train_loader = torch.utils.data.DataLoader(train_set, batch_size=MINIBATCH_SIZE, shuffle=True, num_workers=2)
    

    def train(self, nb_epoch = NB_EPOCH):
        print("Start training.")

        for epoch in range(nb_epoch):

            print("Epoch : " + str(epoch))
            g_loss = []
            d_loss = []

            for batch_id, (x, target) in enumerate(self.train_loader):

                real_batch_data = x.to(self.device)
                current_batch_size = x.shape[0]

                packed_real_data = pack(real_batch_data, self.packing)
                packed_batch_size = packed_real_data.shape[0]

                # labels
                label_real = torch.full((packed_batch_size,), 1, device=self.device)
                label_fake = torch.full((packed_batch_size,), 0, device=self.device)
                # smoothed real labels between 0.7 and 1, and fake between 0 and 0.3
                label_real_smooth = torch.rand((packed_batch_size,)).to(self.device) * 0.3 + 0.7
                label_fake_smooth = torch.rand((packed_batch_size,)).to(self.device) * 0.3

                ### Train discriminator multiple times
                for i in range(self.nb_discriminator_step):
                    loss_discriminator_total = self.train_discriminator(packed_real_data, 
                                                        current_batch_size,
                                                        label_real_smooth if self.real_label_smoothing else label_real,
                                                        label_fake_smooth if self.fake_label_smoothing else label_fake)

                ### Train generator
                loss_generator = self.train_generator(current_batch_size, label_real)

                ### Keep track of losses
                d_loss.append(loss_discriminator_total.item())
                g_loss.append(loss_generator.item())

            self.discriminator_losses.append(torch.mean(torch.tensor(d_loss)))
            self.generator_losses.append(torch.mean(torch.tensor(g_loss)))

            self.write_image(epoch)
            self.write_plots()

        print("Training finished.")
        

    def train_discriminator(self, real_data, current_batch_size, real_label, fake_label):
        
        # Generate with noise
        latent_noise = torch.randn(current_batch_size, self.latent_input, 1, 1, device=self.device)
        generated_batch = self.generator(latent_noise)
        fake_data = pack(generated_batch, self.packing)

        ### Train discriminator
        self.discriminator.zero_grad()

        # Train on real data
        real_prediction = self.discriminator(real_data).squeeze()
        loss_discriminator_real = self.discriminator.loss(real_prediction, real_label)
        #loss_discriminator_real.backward()

        # Train on fake data
        fake_prediction = self.discriminator(fake_data.detach()).squeeze()
        loss_discriminator_fake = self.discriminator.loss(fake_prediction, fake_label)
        #loss_discriminator_fake.backward()

        # Add losses
        loss_discriminator_total = loss_discriminator_real + loss_discriminator_fake
        loss_discriminator_total.backward()
        self.D_optimiser.step()

        return loss_discriminator_total


    def train_generator(self, current_batch_size, real_label):

        # Generate with noise
        latent_noise = torch.randn(current_batch_size, self.latent_input, 1, 1, device=self.device)
        generated_batch = self.generator(latent_noise)
        fake_data = pack(generated_batch, self.packing)

        ### Train generator
        self.generator.zero_grad()

        fake_prediction = self.discriminator(fake_data).squeeze()

        # Loss
        loss_generator = self.generator.loss(fake_prediction, real_label)
        loss_generator.backward()
        self.G_optimiser.step()

        return loss_generator

    def write_image(self, epoch):
        image_data = self.generator(self.saved_latent_input).permute(0, 2, 3, 1).contiguous().view(self.image_size * self.nb_image_to_gen, self.image_size, 3)
        image_data = rescale_for_rgb_image(image_data)
        image.imsave(self.save_path + "gen_epoch_" + str(epoch) + ".png", image_data.data)

    def write_plots(self):
        # Plot losses
        plt.plot(self.generator_losses, label="G loss")
        plt.plot(self.discriminator_losses, label="D loss")

        plt.legend(loc="best")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")

        plt.savefig(self.save_path + "losses.png")

        plt.clf()
 
    def save_models(self, prefix):
        print("Saving models to : " + self.save_path)
        torch.save(self.discriminator.state_dict(), self.save_path + prefix + "_discriminator" + ".pt")
        torch.save(self.generator.state_dict(), self.save_path + prefix + "_generator" + ".pt")
    
    def save_parameters(self):
        from shutil import copyfile
        copyfile("hyperparameters.py", self.save_path + "hyperparameters.py")


