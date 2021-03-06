import torch
import itertools as it
import torch.nn as nn


class ConvClassifier(nn.Module):
    """
    A convolutional classifier model based on PyTorch nn.Modules.

    The architecture is:
    [(CONV -> ReLU)*P -> MaxPool]*(N/P) -> (Linear -> ReLU)*M -> Linear
    """

    def __init__(self, in_size, out_classes: int, channels: list,
                 pool_every: int, hidden_dims: list):
        """
        :param in_size: Size of input images, e.g. (C,H,W).
        :param out_classes: Number of classes to output in the final layer.
        :param channels: A list of of length N containing the number of
            (output) channels in each conv layer.
        :param pool_every: P, the number of conv layers before each max-pool.
        :param hidden_dims: List of of length M containing hidden dimensions of
            each Linear layer (not including the output layer).
        """
        super().__init__()
        assert channels and hidden_dims

        self.in_size = in_size
        self.out_classes = out_classes
        self.channels = channels
        self.pool_every = pool_every
        self.hidden_dims = hidden_dims
        self.pool_cntr = 0

        self.feature_extractor = self._make_feature_extractor()
        self.classifier = self._make_classifier()

    def _make_feature_extractor(self):
        in_channels, in_h, in_w, = tuple(self.in_size)
        
        layers = []
        # TODO: Create the feature extractor part of the model:
        #  [(CONV -> ReLU)*P -> MaxPool]*(N/P)
        #  Use only dimension-preserving 3x3 convolutions. Apply 2x2 Max
        #  Pooling to reduce dimensions after every P convolutions.
        #  Note: If N is not divisible by P, then N mod P additional
        #  CONV->ReLUs should exist at the end, without a MaxPool after them.
        # ====== YOUR CODE: ======
        # Appending the first conv layer and after that relu
        layers.append(nn.Conv2d(in_channels,self.channels[0],kernel_size = 3,padding =1))
        layers.append(nn.ReLU())
        N = len(self.channels)
        N_divisable = N - N % self.pool_every
        remaining = N % self.pool_every
        # Running on the channel dims and appendin convolution layers and relu accordingly
        # After p convolution apply max pool  
        for idx in range(1,N_divisable):
            layers.append(nn.Conv2d(self.channels[idx-1],self.channels[idx],kernel_size = 3,padding =1,bias=True))
            layers.append(nn.ReLU())
            # Adding maxpool after every p convolutions 
            if (idx-1)%self.pool_every == 0:
                layers.append(nn.MaxPool2d(kernel_size = 2,stride=2))
                self.pool_cntr = self.pool_cntr+1
                
        # Last maxpool layer
        #layers.append(nn.MaxPool2d(kernel_size = 2))
        # Append the remaining convolutions and relu
        for idx in range(remaining):
            layers.append(nn.Conv2d(self.channels[idx + N_divisable-1],self.channels[idx + N_divisable],kernel_size = 3,padding =1,bias=True))
            layers.append(nn.ReLU())
            
        # ========================
        seq = nn.Sequential(*layers)
        return seq

    def _make_classifier(self):
        
        M = len(self.hidden_dims)
        in_channels, in_h, in_w, = tuple(self.in_size)
        layers = []
        # TODO: Create the classifier part of the model:
        #  (Linear -> ReLU)*M -> Linear
        #  You'll first need to calculate the number of features going in to
        #  the first linear layer.
        #  The last Linear layer should have an output dim of out_classes.
        # ====== YOUR CODE: ======
        h_denom = 2**self.pool_cntr
        w_denom = 2**self.pool_cntr
        
        
        mlp_in_dims = self.channels[-1] * (in_h//h_denom)*(in_w//w_denom)

        for idx in range(M):
            layers.append(nn.Linear(mlp_in_dims,self.hidden_dims[idx]))
            layers.append(nn.ReLU())
            mlp_in_dims = self.hidden_dims[idx]

        layers.append(nn.Linear(mlp_in_dims,self.out_classes))
        # ========================
        seq = nn.Sequential(*layers)
        return seq

    def forward(self, x):
        # TODO: Implement the forward pass.
        #  Extract features from the input, run the classifier on them and
        #  return class scores.
        # ====== YOUR CODE: ======
        features = self.feature_extractor(x)
        features = features.view(features.shape[0],-1)
        out = self.classifier(features)
        
        # ========================
        return out


class ResidualBlock(nn.Module):
    """
    A general purpose residual block.
    """

    def __init__(self, in_channels: int, channels: list, kernel_sizes: list,
                 batchnorm=False, dropout=0.):
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
        assert all(map(lambda x: x % 2 == 1, kernel_sizes))

        self.main_path, self.shortcut_path = None, None

        # TODO: Implement a generic residual block.
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
        padding = kernel_sizes[0]//2
        main_layers.append(nn.Conv2d(in_channels,channels[0],kernel_sizes[0],padding = padding))
        main_layers.append(nn.Dropout2d(dropout))
        if batchnorm ==True:    
            main_layers.append(nn.BatchNorm2d(channels[0]))
        main_layers.append(nn.ReLU())
        
        for idx in range(len(channels)-1):
            padding = kernel_sizes[idx+1]//2
            main_layers.append(nn.Conv2d(channels[idx],channels[idx +1],kernel_sizes[idx+1],padding = padding))

            if idx < len(channels)-2:    
                main_layers.append(nn.ReLU())
                main_layers.append(nn.Dropout2d(dropout))
                if batchnorm ==True:    
                    main_layers.append(nn.BatchNorm2d(channels[idx + 1]))
            
        if channels[-1] != in_channels:
            self.shortcut_path = nn.Sequential(nn.Conv2d(in_channels,channels[-1],kernel_size = 1,bias=False)
            )            
        else:    
            self.shortcut_path = nn.Sequential()
            
        self.main_path = nn.Sequential(*main_layers)
        # ========================

    def forward(self, x):
        out = self.main_path(x)
        out += self.shortcut_path(x)
        out = torch.relu(out)
        return out


class ResNetClassifier(ConvClassifier):
    def __init__(self, in_size, out_classes, channels, pool_every,
                 hidden_dims):
        super().__init__(in_size, out_classes, channels, pool_every,
                         hidden_dims)

    def _make_feature_extractor(self):
        in_channels, in_h, in_w, = tuple(self.in_size)

        layers = []
        # TODO: Create the feature extractor part of the model:
        #  [-> (CONV -> ReLU)*P -> MaxPool]*(N/P)
        #   \------- SKIP ------/
        #  Use only dimension-preserving 3x3 convolutions. Apply 2x2 Max
        #  Pooling to reduce dimensions after every P convolutions.
        #  Note: If N is not divisible by P, then N mod P additional
        #  CONV->ReLUs (with a skip over them) should exist at the end,
        #  without a MaxPool after them.
        # ====== YOUR CODE: ======
        
        # Appending the first conv layer and after that relu        
        num_ker = len(self.channels[0:self.pool_every])
        
        layers.append(ResidualBlock(in_channels,self.channels[0:self.pool_every],[3]*num_ker))
        layers.append(nn.MaxPool2d(kernel_size = 2,stride=2))
        self.pool_cntr = self.pool_cntr + 1
        
        N = len(self.channels)
        N_divisable = N - N % self.pool_every
        remaining = N % self.pool_every

        # Running on the channel dims and appending convolution layers and relu accordingly
        # After p convolution apply max pool  
        for idx_int,idx in enumerate(range(0,N_divisable,self.pool_every)):
            if idx == 0:
                continue
            layers.append(ResidualBlock(self.channels[idx-1],self.channels[idx:idx+self.pool_every],[3]*self.pool_every))
            layers.append(nn.MaxPool2d(kernel_size = 2,stride=2))
            self.pool_cntr = self.pool_cntr + 1
            
        
        if remaining > 0 :

            layers.append(ResidualBlock(self.channels[N_divisable-1],self.channels[N_divisable:N_divisable+remaining],[3]*remaining))
        # ========================
        seq = nn.Sequential(*layers)
        return seq




#------------------------------------------------------------------------------
# Few classes for custom network        

class CustomConv(nn.Module):
    """
    A Custom type of convolution 
    does 1x1 3x3 and 5x5 convolutions + BachNorm2d 
    and returns the average of them 
    """
    def __init__(self,in_channels,out_channels,batchnorm = True):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels,out_channels,kernel_size = 1,padding = 0)
        self.conv3 = nn.Conv2d(in_channels,out_channels,kernel_size = 3,padding = 1)
        self.conv5 = nn.Conv2d(in_channels,out_channels,kernel_size = 5,padding = 2)
        self.batchnorm = batchnorm
        self.C_Batchnorm = nn.BatchNorm2d(out_channels)
    def forward(self, x):
        out_1 = self.conv1(x)
        
        out_3 = self.conv3(x)
        out_5 = self.conv5(x)
        out = 0.333*(out_1 + out_3 + out_5)
        if self.batchnorm:
            out = self.C_Batchnorm(out)
        return out





class CustomResidualBlock(nn.Module):
    """
    A general purpose residual block.
    """

    def __init__(self, in_channels: int, channels: list,
                 batchnorm=True, dropout=0.2):
        """
        :param in_channels: Number of input channels to the first convolution.
        :param channels: List of number of output channels for each
        convolution in the block. The length determines the number of
        convolutions.
        be the same as channels. Values should be odd numbers.
        :param batchnorm: True/False whether to apply BatchNorm between
        convolutions.
        :param dropout: Amount (p) of Dropout to apply between convolutions.
        Zero means don't apply dropout.
        """
        super().__init__()
        self.leaky = nn.LeakyReLU() 
        assert channels 
        self.main_path, self.shortcut_path = None, None
        # replacing relu with leaky relu 
        main_layers = []
        # constructing the input layer 
        # we assume kernel sizes are odd so to preserve spacial dimentions we
        # padd with the kernel size divided by 2
        
        main_layers.append(CustomConv(in_channels,channels[0]))
        main_layers.append(nn.Dropout2d(dropout))
        if batchnorm ==True:    
            main_layers.append(nn.BatchNorm2d(channels[0]))
        main_layers.append(nn.LeakyReLU())
        
        for idx in range(len(channels)-1):
            
            
            
            main_layers.append(CustomConv(channels[idx],channels[idx +1]))
        
            main_layers.append(nn.Dropout2d(dropout))
            
            if idx < len(channels)-2:    
                main_layers.append(nn.LeakyReLU())
                main_layers.append(nn.Dropout2d(dropout))
                if batchnorm ==True:    
                    main_layers.append(nn.BatchNorm2d(channels[idx + 1]))
            
        if channels[-1] != in_channels:
            self.shortcut_path = nn.Sequential(nn.Conv2d(in_channels,channels[-1],kernel_size = 1,bias=False)
            )            
        else:    
            self.shortcut_path = nn.Sequential()
            
        self.main_path = nn.Sequential(*main_layers)
        # ========================

    def forward(self, x):
        out = self.main_path(x)
        out += self.shortcut_path(x)
        #out = torch.relu(out)
        out = self.leaky(out)
        return out


class YourCodeNet(ConvClassifier):
    # TODO: Change whatever you want about the ConvClassifier to try to
    #  improve it's results on CIFAR-10.
    #  For example, add batchnorm, dropout, skip connections, change conv
    #  filter sizes etc.
    # ====== YOUR CODE: ======
        def __init__(self, in_size, out_classes, channels, pool_every,
                 hidden_dims):
            super().__init__(in_size, out_classes, channels, pool_every,
                         hidden_dims)
    
        def _make_feature_extractor(self):
            in_channels, in_h, in_w, = tuple(self.in_size)
    
            layers = []        
            # Appending the first conv layer and after that relu        
            
            layers.append(CustomResidualBlock(in_channels,self.channels[0:self.pool_every]))
            layers.append(nn.MaxPool2d(kernel_size = 2,stride=2))
            self.pool_cntr = self.pool_cntr + 1
            
            N = len(self.channels)
            N_divisable = N - N % self.pool_every
            remaining = N % self.pool_every
    
            # Running on the channel dims and appending convolution layers and relu accordingly
            # After p convolution apply max pool  
            for idx_int,idx in enumerate(range(0,N_divisable,self.pool_every)):
                if idx == 0:
                    continue
                layers.append(CustomResidualBlock(self.channels[idx-1],self.channels[idx:idx+self.pool_every]))
                curr_channels = self.channels[idx:idx+self.pool_every]
                layers.append(nn.Conv2d(curr_channels[-1],curr_channels[-1],kernel_size = 2,stride = 2))
                self.pool_cntr = self.pool_cntr + 1
                
            
            if remaining > 0 :
    
                layers.append(CustomResidualBlock(self.channels[N_divisable-1],self.channels[N_divisable:N_divisable+remaining]))
            # ========================
            seq = nn.Sequential(*layers)
            return seq
        
        
        def _make_classifier(self):
            
            M = len(self.hidden_dims)
            in_channels, in_h, in_w, = tuple(self.in_size)
            layers = []
            # TODO: add dropout to classifier
            #  
            # ====== YOUR CODE: ======
            h_denom = 2**self.pool_cntr
            w_denom = 2**self.pool_cntr
            dropout = 0.25
            
            mlp_in_dims = self.channels[-1] * (in_h//h_denom)*(in_w//w_denom)
    
            for idx in range(M):
                layers.append(nn.Linear(mlp_in_dims,self.hidden_dims[idx]))
                layers.append(nn.Dropout(dropout))
                layers.append(nn.ReLU())
                mlp_in_dims = self.hidden_dims[idx]
    
            layers.append(nn.Linear(mlp_in_dims,self.out_classes))
            # ========================
            seq = nn.Sequential(*layers)
            return seq
    
        def forward(self, x):
            # TODO: Implement the forward pass.
            #  Extract features from the input, run the classifier on them and
            #  return class scores.
            # ====== YOUR CODE: ======
            features = self.feature_extractor(x)
            features = features.view(features.shape[0],-1)
            out = self.classifier(features)
            
            # ========================
            return out
        
        # ========================
