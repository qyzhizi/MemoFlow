#!/usr/bin/env python
# coding=utf-8
import io
import json
import logging

from PIL import Image
import torch
import torch.nn.functional as F
from torch import nn
from torchvision import transforms as T
from torchvision.models import resnet50

from web_dl.common import dependency
from web_dl.common import manager


log = logger.getLogger(__name__)


@dependency.provider('predict_image_api')
class Manager(object):
    def prepare_image(self, req, image, target_size=(224, 224)):
        """Do image preprocessing before prediction on any data.
        :param image:       original image
        :param target_size: target image size
        :return: preprocessed image
        """

#        # Read the image in PIL format
#        log.info("read image, type of readed image: %s", type(image))
#        image = image.read()
#        image = Image.open(io.BytesIO(image))
#        log.info("type of Image.opened image: %s", type(image))

 
        # Preprocess the image and prepare it for classification.
        if image.mode != 'RGB':
            log.info("convert to RGB")
            image = image.convert("RGB")

        # Resize the input image nad preprocess it.
        log.info("prepare image size: %s", image.shape)
        image = T.Resize(target_size)(image)
        image = T.ToTensor()(image)
            
        # Convert to Torch.Tensor and normalize.
        image = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(image)

        # Add batch_size axis.
        image = image[None]
        log.info("prepare image size (Add batch_size axis): %s", image.shape)
        if Model.use_gpu:
            log.info('use_gup')
            image = image.cuda()
        log.debug("image requires_grad: %s", image.requires_grad)
        return image

    def predict_image(req, image):
        """
        predict image after preprocessing 

        """
            # Classify the input image and then initialize the list of
            # predictions to return to the client.
            with torch.no_grad():
                logger.debug("Model.model type : %s", type(Model.model))
                res = Model.model(image)
            preds = F.softmax(res, dim=1)
            logger.debug("type of res: %s, res requires_grad: %s",
                         type(res), res.requires_grad)
            results = torch.topk(preds.cpu().data, k=3, dim=1)
            logger.debug(results)

            data['predictions'] = list()

            # Loop over the results and add them to the list of returned
            # predictions
            for prob, label in zip(results[0][0], results[1][0]):
                logger.debug("prob(%s), label(%s)", prob, label)
                label_name = Model.idx2label[label.item()]
                r = {"label": label_name, "probability": float(prob)}
                data['predictions'].append(r)

            # Indicate that the request was a success.
            data["success"] = True

        
