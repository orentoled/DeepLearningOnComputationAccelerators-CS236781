import torch
import torch.nn as nn
import torch.nn.functional as F


class EncoderConv(nn.Module):
    """
    a convolution block for the encoder
    """

    def __init__(self, in_channels: int, channels: list, kernel_sizes: list,
                 stride_list:list,padding_list:list ,batchnorm=True, dropout=0.1,bias_flag = False):
        """
        :param in_channels: Number of input channels to the first convolution.
        :param channels: List of number of output channels for each
        convolution in the block. The length determines the number of
        convolutions.
        :param kernel_sizes: List of kernel sizes (spatial). Length should
        be the same as channels. Values should be odd numbers.
        :param batchnorm: True/False whether to apply BatchNorm between
        convolutions.
        :param dropout: Amount (p) of Dropout to apply between convolutions.
        Zero means don't apply dropout.
        """
        super().__init__()
        assert channels and kernel_sizes
        assert len(channels) == len(kernel_sizes) 
        assert len(channels) == len(stride_list) 
        assert len(channels) == len(padding_list) 

        #assert all(map(lambda x: x % 2 == 1, kernel_sizes))
        self.out_channels = channels[-1]
        self.main_path= None

        # DONE: Implement a generic residual block.
        #  Use the given arguments to create two nn.Sequentials:
        #  the main_path, which should contain the convolution, dropout,
        #  batchnorm, relu sequences, and the shortcut_path which should
        #  represent the skip-connection.
        #  Use convolutions which preserve the spatial extent of the input.
        #  For simplicity of implementation, we'll assume kernel sizes are odd.
        # ====== YOUR CODE: ======
        main_layers = []
        
        # constructing the input layer 
        # we assume kernel sizes are odd so to preserve spacial dimentions we 
        # padd with the kernel size divided by 2

        main_layers.append(nn.Conv2d(in_channels,channels[0],kernel_sizes[0],padding = padding_list[0]
                                     ,stride = stride_list[0],bias = bias_flag))
        main_layers.append(nn.Dropout2d(dropout))
        if batchnorm ==True:    
            main_layers.append(nn.BatchNorm2d(channels[0]))
        main_layers.append(nn.ELU(alpha = 0.5)) 
        
        
        for idx in range(len(channels)-1):
            
            main_layers.append(nn.Conv2d(channels[idx],channels[idx +1],kernel_sizes[idx+1],padding =padding_list[idx+1],
                                         stride = stride_list[idx+1],bias = bias_flag))

            if idx < len(channels)-2:    
                main_layers.append(nn.ReLU())
                #main_layers.append(nn.ELU(alpha = 0.5))
                main_layers.append(nn.Dropout2d(dropout))
                if batchnorm ==True:    
                    main_layers.append(nn.BatchNorm2d(channels[idx + 1]))
        
        main_layers.append(nn.Sigmoid())              
        self.main_path = nn.Sequential(*main_layers)
        self.layers_list = main_layers
        # ========================

    def forward(self, x):
        out = self.main_path(x)
        out = torch.relu(out)
        return out



class DecoderConv(nn.Module):
    """
    a convolution block for the encoder
    """

    def __init__(self, in_channels: int, channels: list, kernel_sizes: list,
                 stride_list:list,padding_list:list ,batchnorm=True, dropout=0.1,bias_flag = False):
        """
        :param in_channels: Number of input channels to the first convolution.
        :param channels: List of number of output channels for each
        convolution in the block. The length determines the number of
        convolutions.
        :param kernel_sizes: List of kernel sizes (spatial). Length should
        be the same as channels. Values should be odd numbers.
        :param batchnorm: True/False whether to apply BatchNorm between
        convolutions.
        :param dropout: Amount (p) of Dropout to apply between convolutions.
        Zero means don't apply dropout.
        """
        super().__init__()
        assert channels and kernel_sizes
        assert len(channels) == len(kernel_sizes) 
        assert len(channels) == len(stride_list) 
        assert len(channels) == len(padding_list) 

        #assert all(map(lambda x: x % 2 == 1, kernel_sizes))
        self.out_channels = channels[-1]
        self.main_path= None

        # DONE: Implement a generic residual block.
        #  Use the given arguments to create two nn.Sequentials:
        #  the main_path, which should contain the convolution, dropout,
        #  batchnorm, relu sequences, and the shortcut_path which should
        #  represent the skip-connection.
        #  Use convolutions which preserve the spatial extent of the input.
        #  For simplicity of implementation, we'll assume kernel sizes are odd.
        # ====== YOUR CODE: ======
        main_layers = []
        
        # constructing the input layer 
        # we assume kernel sizes are odd so to preserve spacial dimentions we 
        # padd with the kernel size divided by 2

        main_layers.append(nn.ConvTranspose2d(in_channels,channels[0],kernel_sizes[0],padding = padding_list[0]
                                     ,stride = stride_list[0],bias = bias_flag))
        main_layers.append(nn.Dropout2d(dropout))
        if batchnorm ==True:    
            main_layers.append(nn.BatchNorm2d(channels[0]))
        main_layers.append(nn.ELU(alpha = 0.5)) 
        
        
        for idx in range(len(channels)-1):
            
            main_layers.append(nn.ConvTranspose2d(channels[idx],channels[idx +1],kernel_sizes[idx+1],padding =padding_list[idx+1],
                                         stride = stride_list[idx+1],bias = bias_flag))

            if idx < len(channels)-2:    
                #main_layers.append(nn.ReLU())
                main_layers.append(nn.ReLU())
                main_layers.append(nn.Dropout2d(dropout))
                if batchnorm ==True:    
                    main_layers.append(nn.BatchNorm2d(channels[idx + 1]))
                        
        self.main_path = nn.Sequential(*main_layers)
        self.layers_list = main_layers
        # ========================

    def forward(self, x):
        out = self.main_path(x)
        out = torch.relu(out)
        return out


class EncoderCNN(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()

        modules = []
        # TODO:
        #  Implement a CNN. Save the layers in the modules list.
        #  The input shape is an image batch: (N, in_channels, H_in, W_in).
        #  The output shape should be (N, out_channels, H_out, W_out).
        #  You can assume H_in, W_in >= 64.
        #  Architecture is up to you, but it's recommended to use at
        #  least 3 conv layers. You can use any Conv layer parameters,
        #  use pooling or only strides, use any activation functions,
        #  use BN or Dropout, etc.
        # ====== YOUR CODE: ======
        self.in_channels = in_channels 
        self.out_channels = out_channels 
        self.channels_list = [256,512,1024,self.out_channels]
        self.kernels_list = [4]*len(self.channels_list)
        self.stride_list = [2]*(len(self.channels_list)-1)+[1]
        self.padding_list = [1]*(len(self.channels_list)-1) + [0]
        
        modules = EncoderConv(self.in_channels, self.channels_list,self.kernels_list,
                             self.stride_list,self.padding_list)
        modules = modules.layers_list
        # ========================
        self.cnn = nn.Sequential(*modules)
         
    def forward(self, x):
        return self.cnn(x)

        
    
class DecoderCNN(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()

        modules = []

        # TODO:
        #  Implement the "mirror" CNN of the encoder.
        #  For example, instead of Conv layers use transposed convolutions,
        #  instead of pooling do unpooling (if relevant) and so on.
        #  The architecture does not have to exactly mirror the encoder
        #  (although you can), however the important thing is that the
        #  output should be a batch of images, with same dimensions as the
        #  inputs to the Encoder were.
        # ====== YOUR CODE: ======
        self.in_channels = in_channels 
        self.out_channels = out_channels 
        self.channels_list = [1024,512,256,self.out_channels]
        self.kernels_list = [4]*len(self.channels_list)
        self.stride_list = [1]+[2]*(len(self.channels_list)-1)
        self.padding_list = [0]+[1]*(len(self.channels_list)-1) 
        
        modules = DecoderConv(self.in_channels, self.channels_list,self.kernels_list,
                             self.stride_list,self.padding_list)
        modules = modules.layers_list        
        # ========================
        self.cnn = nn.Sequential(*modules)

    def forward(self, h):
        # Tanh to scale to [-1, 1] (same dynamic range as original images).
        return torch.tanh(self.cnn(h))
    



class VAE(nn.Module):
    def __init__(self, features_encoder, features_decoder, in_size, z_dim):
        """
        :param features_encoder: Instance of an encoder the extracts features
        from an input.
        :param features_decoder: Instance of a decoder that reconstructs an
        input from it's features.
        :param in_size: The size of one input (without batch dimension).
        :param z_dim: The latent space dimension.
        """
        super().__init__()
        self.features_encoder = features_encoder
        self.features_decoder = features_decoder
        self.z_dim = z_dim
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') 
        self.features_shape, n_features = self._check_features(in_size)
        
        # TODO: Add more layers as needed for encode() and decode().
        # ====== YOUR CODE: ======
        self.enc_out_dim = self._check_features(in_size)

        self.in_fc_dim = self.enc_out_dim[1]
        # Adding fc layers to represent the NN for mu and sigma

        self.mu_fc = nn.Sequential(nn.Linear(self.in_fc_dim,self.z_dim))
        
        self.log_sigma2_fc = nn.Sequential(nn.Linear(self.in_fc_dim,self.z_dim))

        self.rec_fc = nn.Sequential(nn.Linear(self.z_dim,self.in_fc_dim))
        
        
        # ========================

    def _check_features(self, in_size):
        device = next(self.parameters()).device
        with torch.no_grad():
            # Make sure encoder and decoder are compatible
            x = torch.randn(1, *in_size, device=device)
            h = self.features_encoder(x)
            xr = self.features_decoder(h)
            assert xr.shape == x.shape
            # Return the shape and number of encoded features
            return h.shape[1:], torch.numel(h)//h.shape[0]

    def encode(self, x):
        # TODO:
        #  Sample a latent vector z given an input x from the posterior q(Z|x).
        #  1. Use the features extracted from the input to obtain mu and
        #     log_sigma2 (mean and log variance) of q(Z|x).
        #  2. Apply the reparametrization trick to obtain z.
        # ====== YOUR CODE: ======
        encoded_features = self.features_encoder(x)

        mu = self.mu_fc(encoded_features.view(encoded_features.shape[0],-1))
        log_sigma2 = self.log_sigma2_fc(encoded_features.view(encoded_features.shape[0],-1))
        u = torch.randn(encoded_features.shape[0],self.z_dim, requires_grad=True).to(self.device )
        
        #u = torch.normal(torch.zeros_like(mu), torch.ones_like(mu))
        
        z = torch.exp(0.5*log_sigma2)*u + mu
        # ========================

        return z, mu, log_sigma2

    def decode(self, z):
        # TODO:
        #  Convert a latent vector back into a reconstructed input.
        #  1. Convert latent z to features h with a linear layer.
        #  2. Apply features decoder.
        # ====== YOUR CODE: ======
        
        z_dec = self.rec_fc(z)        
        z_dec = z_dec.view(z.shape[0],self.features_shape[0],self.features_shape[1],self.features_shape[2])        
        x_rec = self.features_decoder(z_dec)
        # ========================

        # Scale to [-1, 1] (same dynamic range as original images).
        return torch.tanh(x_rec)

    def sample(self, n):
        samples = []
        device = next(self.parameters()).device
        with torch.no_grad():
            # TODO:
            #  Sample from the model.
            #  Generate n latent space samples and return their
            #  reconstructions.
            #  Remember that this mean using the model for inference.
            #  Also note that we're ignoring the sigma2 parameter here.
            #  Instead of sampling from N(psi(z), sigma2 I), we'll just take
            #  the mean, i.e. psi(z).
            # ====== YOUR CODE: ======
            z = torch.randn((n, self.z_dim), device=device)
            x = self.decode(z)
            samples = x.cpu() 
            # ========================
        return samples

    def forward(self, x):
        z, mu, log_sigma2 = self.encode(x)
        return self.decode(z), mu, log_sigma2
    

def vae_loss(x, xr, z_mu, z_log_sigma2, x_sigma2):
    """
    Point-wise loss function of a VAE with latent space of dimension z_dim.
    :param x: Input image batch of shape (N,C,H,W).
    :param xr: Reconstructed (output) image batch.
    :param z_mu: Posterior mean (batch) of shape (N, z_dim).
    :param z_log_sigma2: Posterior log-variance (batch) of shape (N, z_dim).
    :param x_sigma2: Likelihood variance (scalar).
    :return:
        - The VAE loss
        - The data loss term
        - The KL divergence loss term
    all three are scalars, averaged over the batch dimension.
    """
    loss, data_loss, kldiv_loss = None, None, None
    # TODO:
    #  Implement the VAE pointwise loss calculation.
    #  Remember:
    #  1. The covariance matrix of the posterior is diagonal.
    #  2. You need to average over the batch dimension.
    # ====== YOUR CODE: ======
    N = x.shape[0]
   # dim_z = z_mu.shape[-1]
   # dim_x = x.shape[-1]
    
    err = (x-xr)
    
    
    dz = z_mu.shape[1]
    dx = x.shape[0]*x.shape[1]*x.shape[2]*x.shape[3]
    
    data_loss = ((1/x_sigma2) * (err.norm())**2 / dx)
    kldiv_loss = ((torch.exp(z_log_sigma2)).sum() + (z_mu.norm())**2 - (z_log_sigma2.sum())) / N - dz

    loss = data_loss + kldiv_loss    
    
    
    # ========================

    return loss, data_loss, kldiv_loss
