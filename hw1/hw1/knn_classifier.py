import numpy as np
import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader, Subset

import cs236781.dataloader_utils as dataloader_utils
from . import dataloaders


class KNNClassifier(object):
    def __init__(self, k):
        self.k = k
        self.x_train = None
        self.y_train = None
        self.n_classes = None

    def train(self, dl_train: DataLoader):
        """
        Trains the KNN model. KNN training is memorizing the training data.
        Or, equivalently, the model parameters are the training data itself.
        :param dl_train: A DataLoader with labeled training sample (should
            return tuples).
        :return: self
        """
        x, y = next(iter(dl_train))  
        x_train = x
        y_train = y
        # TODO:
        #  Convert the input dataloader into x_train, y_train and n_classes.
        #  1. You should join all the samples returned from the dataloader into
        #     the (N,D) matrix x_train and all the labels into the (N,) vector
        #     y_train.
        #  2. Save the number of classes as n_classes.
        # ====== YOUR CODE: ======
        count = 0
        for x,y in dl_train:
            if count == 0:
                pass
            else:
                x_train = torch.cat((x_train,x))
                y_train = torch.cat((y_train,y))
                
            count = count+1
        # ========================
        self.x_train = x_train
        self.y_train = y_train
        self.n_classes = x_train.shape[0]
        return self

    def predict(self, x_test: Tensor):
        """
        Predict the most likely class for each sample in a given tensor.
        :param x_test: Tensor of shape (N,D) where N is the number of samples.
        :return: A tensor of shape (N,) containing the predicted classes.
        """

        # Calculate distances between training and test samples
        dist_matrix = l2_dist(self.x_train,x_test)
        
        
        # TODO:
        #  Implement k-NN class prediction based on distance matrix.
        #  For each training sample we'll look for it's k-nearest neighbors.
        #  Then we'll predict the label of that sample to be the majority
        #  label of it's nearest neighbors.

        n_test = x_test.shape[0]
        y_pred = torch.zeros(n_test, dtype=torch.int64)
        for i in range(n_test):
            # TODO:
            #  - Find indices of k-nearest neighbors of test sample i
            #  - Set y_pred[i] to the most common class among them
            #  - Don't use an explicit loop.
            # ====== YOUR CODE: ======
            curr_dist = dist_matrix[:,i]
            _,top_idx = torch.topk(curr_dist,self.k,largest = False)
            labels = self.y_train[top_idx]
            y_pred[i] = torch.bincount(labels).argmax()
            # ========================

        return y_pred


def l2_dist(x1: Tensor, x2: Tensor):
    """
    Calculates the L2 (euclidean) distance between each sample in x1 to each
    sample in x2.
    :param x1: First samples matrix, a tensor of shape (N1, D).
    :param x2: Second samples matrix, a tensor of shape (N2, D).
    :return: A distance matrix of shape (N1, N2) where the entry i, j
    represents the distance between x1 sample i and x2 sample j.
    """

    # TODO:
    #  Implement L2-distance calculation efficiently as possible.
    #  Notes:
    #  - Use only basic pytorch tensor operations, no external code.
    #  - Solution must be a fully vectorized implementation, i.e. use NO
    #    explicit loops (yes, list comprehensions are also explicit loops).
    #    Hint: Open the expression (a-b)^2. Use broadcasting semantics to
    #    combine the three terms efficiently.

    # ====== YOUR CODE: ======
    x1_sum_vec = (x1**2).sum(dim=1)
    x2_sum_vec = (x2**2).sum(dim=1)
    
    mul_mat = x1@x2.T
    x1_sum_vec = x1_sum_vec.view(-1,1)
   # x2_sum_vec = x2_sum_vec.view(1,-1)
    
    total_sum = x1_sum_vec + x2_sum_vec
    dists = total_sum - 2*mul_mat
    dists = dists ** 0.5
    
    '''
    x2_singletons = x2.view(x2_dims[0], 1, x2_dims[1])

    # every x1 sample minus every x2 sample via broadcasting
    sub_t = x1 - x2_singletons;
    sqr_t = sub_t ** 2
    #sqr_t = (x1 - x2_singletons)**2
    sqr_singletons = sqr_t.view(x1_dims[0] * x2_dims[0], x1_dims[1]) # rearrange vectors
    sum_singletons = sqr_singletons.sum(1)

    # we use a transposed dims of the requested tensor for a faster
    # arrangment of the data
    dists = (sum_singletons ** 0.5).view(x2_dims[0], x1_dims[0])
    
    # and now rearrange as needed
    dists = dists.T
    '''
    # ========================

    return dists


def accuracy(y: Tensor, y_pred: Tensor):
    """
    Calculate prediction accuracy: the fraction of predictions in that are
    equal to the ground truth.
    :param y: Ground truth tensor of shape (N,)
    :param y_pred: Predictions vector of shape (N,)
    :return: The prediction accuracy as a fraction.
    """
    assert y.shape == y_pred.shape
    assert y.dim() == 1

    # TODO: Calculate prediction accuracy. Don't use an explicit loop.
    accuracy = None
    # ====== YOUR CODE: ======
    accuracy = float((y == y_pred).sum())/len(y)
    # ========================

    return accuracy


def find_best_k(ds_train: Dataset, k_choices, num_folds):
    """
    Use cross validation to find the best K for the kNN model.

    :param ds_train: Training dataset.
    :param k_choices: A sequence of possible value of k for the kNN model.
    :param num_folds: Number of folds for cross-validation.
    :return: tuple (best_k, accuracies) where:
        best_k: the value of k with the highest mean accuracy across folds
        accuracies: The accuracies per fold for each k (list of lists).
    """

    accuracies = []
    fold_size = int(np.floor(len(ds_train)/num_folds))
    indices = np.random.choice(len(ds_train), len(ds_train), replace=False)
    
    for i, k in enumerate(k_choices):
        model = KNNClassifier(k)

        # TODO:
        #  Train model num_folds times with different train/val data.
        #  Don't use any third-party libraries.
        #  You can use your train/validation splitter from part 1 (note that
        #  then it won't be exactly k-fold CV since it will be a
        #  random split each iteration), or implement something else.

        # ====== YOUR CODE: ======
        ith_acc = []
        for i_fold in range(num_folds):
            
            test_indices = indices[i_fold * fold_size : (i_fold + 1) * fold_size]
            train_indices = np.concatenate((indices[:i_fold * fold_size], indices[(i_fold + 1) * fold_size:]))
            
            # test_subset = torch.utils.data.Subset(ds_train, test_indices)
            test_sampler = torch.utils.data.sampler.SubsetRandomSampler(test_indices)                 
            train_sampler = torch.utils.data.sampler.SubsetRandomSampler(train_indices)
            
            model.train(DataLoader(ds_train, sampler=train_sampler))
            dl_test = DataLoader(ds_train, sampler=test_sampler)
            x_test, y_test = dataloader_utils.flatten(dl_test)
             
            y_pred = model.predict(x_test)
            ith_acc.append(accuracy(y_test, y_pred))

        accuracies.append(ith_acc)    
        # ========================

    best_k_idx = np.argmax([np.mean(acc) for acc in accuracies])
    best_k = k_choices[best_k_idx]

    return best_k, accuracies