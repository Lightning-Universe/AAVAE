import numpy as np
import torchvision.transforms as transforms
from pl_bolts.transforms.dataset_normalizations import cifar10_normalization

from typing import Optional


class SimCLRTrainDataTransform(object):
    """
    Transforms for SimCLR

    Transform::

        RandomResizedCrop(size=self.input_height)
        RandomHorizontalFlip()
        RandomApply([color_jitter], p=0.8)
        RandomGrayscale(p=0.2)
        GaussianBlur(kernel_size=int(0.1 * self.input_height))
        transforms.ToTensor()

    Example::

        from pl_bolts.models.self_supervised.simclr.transforms import SimCLRTrainDataTransform

        transform = SimCLRTrainDataTransform(input_height=32)
        x = sample()
        (xi, xj) = transform(x)
    """

    def __init__(
        self,
        input_height: int = 224,
        gaussian_blur: bool = True,
        flip: bool = False,
        jitter_strength: float = 1.0,
        normalize: Optional[transforms.Normalize] = None,
    ) -> None:

        self.jitter_strength = jitter_strength
        self.input_height = input_height
        self.gaussian_blur = gaussian_blur
        self.flip = flip
        self.normalize = normalize

        self.color_jitter = transforms.ColorJitter(
            0.8 * self.jitter_strength,
            0.8 * self.jitter_strength,
            0.8 * self.jitter_strength,
            0.2 * self.jitter_strength,
        )

        data_transforms = []

        if self.flip:
            data_transforms.append(transforms.RandomHorizontalFlip())

        data_transforms.append(transforms.RandomApply([self.color_jitter], p=0.8))
        data_transforms.append(transforms.RandomGrayscale(p=0.2))

        """
        if self.gaussian_blur:
            data_transforms.append(GaussianBlur(kernel_size=int(0.1 * self.input_height, p=0.5)))
        """

        data_transforms.append(transforms.ToTensor())
        eval_transform = [transforms.Resize(self.input_height), transforms.ToTensor()]

        if self.normalize:
            data_transforms.append(normalize)
            eval_transform.append(normalize)

        self.train_transform = transforms.Compose(data_transforms)
        self.eval_transform = transforms.Compose(eval_transform)

    def __call__(self, sample):
        transform = self.train_transform

        xi = transform(sample)
        xj = transform(sample)

        return xi, xj, self.eval_transform(sample)


class SimCLREvalDataTransform(object):
    """
    Transforms for SimCLR

    Transform::

        Resize(input_height + 10, interpolation=3)
        transforms.CenterCrop(input_height),
        transforms.ToTensor()

    Example::

        from pl_bolts.models.self_supervised.simclr.transforms import SimCLREvalDataTransform

        transform = SimCLREvalDataTransform(input_height=32)
        x = sample()
        (xi, xj) = transform(x)
    """

    def __init__(
        self, input_height: int = 224, normalize: Optional[transforms.Normalize] = None
    ):
        self.input_height = input_height
        self.normalize = normalize

        data_transforms = [transforms.Resize(self.input_height), transforms.ToTensor()]

        if self.normalize:
            data_transforms.append(normalize)

        self.test_transform = transforms.Compose(data_transforms)

    def __call__(self, sample):
        transform = self.test_transform

        xi = transform(sample)
        xj = transform(sample)

        return xi, xj, transform(sample)


"""
class GaussianBlur(object):
    # Implements Gaussian blur as described in the SimCLR paper
    def __init__(self, kernel_size, p=0.5, min=0.1, max=2.0):
        self.min = min
        self.max = max

        # kernel size is set to be 10% of the image height/width
        self.kernel_size = kernel_size
        self.p = p

    def __call__(self, sample):
        sample = np.array(sample)

        # blur the image with a 50% chance
        prob = np.random.random_sample()

        if prob < self.p:
            sigma = (self.max - self.min) * np.random.random_sample() + self.min
            sample = cv2.GaussianBlur(sample, (self.kernel_size, self.kernel_size), sigma)

        return sample
"""
