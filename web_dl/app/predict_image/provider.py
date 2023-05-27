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

from web_dl.conf import CONF
from web_dl.common import dependency
from web_dl.common import manager


LOG = logging.getLogger(__name__)


IMAGENET_ID2CLASS_FILEPATH = CONF.predict_image['imagenet_id2class_filepath']
# GPU inference is not used by default
IMAGENET_PREDICT_USE_GPU = CONF.predict_image['IMAGENET_PREDICT_USE_GPU']
INDEX_HTML_PATH = CONF.predict_image['index_html_path']

class Model(object):
    model = None
    idx2label = None
    use_gpu = None
    model_already_loaded = False

    def __init__(self, file_path, use_gpu=True):
        with open(file_path, 'r') as f:
            Model.idx2label = eval(f.read())
            Model.use_gpu = use_gpu

    def load_model(self):
        """Load the pre-trained model, you can use your model just as easily.

        """
        # 全局变量，服务启动的时候只需要加载一次
        Model.model = resnet50(pretrained=True)
        Model.model.eval()
        if Model.use_gpu:
            Model.model.cuda()

@dependency.provider('predict_image_api')
class Manager(object):
    def prepare_image(self, req, image, target_size=(224, 224)):
        """Do image preprocessing before prediction on any data.
        :param image:       original image
        :param target_size: target image size
        :return: preprocessed image
        """

#        # Read the image in PIL format
#        LOG.info("read image, type of readed image: %s", type(image))
#        image = image.read()
#        image = Image.open(io.BytesIO(image))
#        LOG.info("type of Image.opened image: %s", type(image))

 
        # Preprocess the image and prepare it for classification.
        if image.mode != 'RGB':
            LOG.info("convert to RGB")
            image = image.convert("RGB")

        # Resize the input image and preprocess it.
        image = T.Resize(target_size)(image)
        image = T.ToTensor()(image)
        LOG.info("prepare image size: %s", image.shape)
            
        # Convert to Torch.Tensor and normalize.
        image = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(image)

        # Add batch_size axis.
        image = image[None]
        LOG.info("prepare image size (Add batch_size axis): %s", image.shape)
        if Model.use_gpu:
            LOG.info('use_gup')
            image = image.cuda()
        LOG.debug("image requires_grad: %s", image.requires_grad)
        return image

    def predict_image(self, req, image):
        """
        predict image after preprocessing 

        """
        LOG.debug("**********************start predict***********************")
        data = {"success": False}

        # If the model is not loaded, then load the model
        if Model.model_already_loaded == False:
            Model(file_path=IMAGENET_ID2CLASS_FILEPATH,
                  use_gpu=IMAGENET_PREDICT_USE_GPU).load_model()
            Model.model_already_loaded = True
        
        # Classify the input image and then initialize the list of
        # predictions to return to the client.
        with torch.no_grad():
            LOG.debug("Model.model type : %s", type(Model.model))
            res = Model.model(image)
        preds = F.softmax(res, dim=1)
        LOG.debug("type of res: %s, res requires_grad: %s",
                        type(res), res.requires_grad)
        results = torch.topk(preds.cpu().data, k=3, dim=1)
        LOG.debug(results)

        data['predictions'] = list()

        # Loop over the results and add them to the list of returned
        # predictions
        for prob, label in zip(results[0][0], results[1][0]):
            LOG.debug("prob(%s), label(%s)", prob, label)
            label_name = Model.idx2label[label.item()]
            r = {"label": label_name, "probability": float(prob)}
            data['predictions'].append(r)

        # Indicate that the request was a success.
        data["success"] = True
        LOG.info("data : %s", data)
        return  data


    def get_html(self, index_html_path=INDEX_HTML_PATH):
        with open(index_html_path, "r", encoding='UTF-8')as f:
            res = f.read()
        return res

        
