#!/usr/bin/python
#-*- encoding:utf-8 -*-
'''Trains a simple convnet on the MNIST dataset.
Gets to 99.25% test accuracy after 12 epochs
(there is still a lot of margin for parameter tuning).
16 seconds per epoch on a GRID K520 GPU.
'''

from __future__ import print_function
import keras
from keras.models import  model_from_json
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import os

# public define
import sys
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.3
set_session(tf.Session(config=config))

py_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(py_dir)
sys.path.append(project_dir)
import train.dataload as dataload
import creatTrainDataSet.mydataset as mydataset


def train(trainpath,testpath):
    batch_size = 128
    num_classes = 11
    epochs = 12
    # input image dimensions
    img_rows, img_cols = 28, 28

    #加载数据
    (x_train, y_train), (x_test, y_test) = dataload.loadNumberAndX_data(trainpath, testpath)

    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    modelArgs=['../trainmodel/architecture_number_X3.json','../trainmodel/weights_number_X3.h5']

    if os.path.exists(modelArgs[0]) and os.path.exists(modelArgs[1]):
        model = model_from_json(open(modelArgs[0]).read())
        model.load_weights(modelArgs[1])
    else:
        model = Sequential()
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu', input_shape=input_shape))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.5))
        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(num_classes, activation='softmax'))

    model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.Adadelta(),
                      metrics=['accuracy'])

    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              verbose=1,
              validation_data=(x_test, y_test))
    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    #保存神经网络的结构与训练好的参数
    json_string = model.to_json() #等价于 json_string = model.get_config()
    open(modelArgs[0],'w').write(json_string)
    model.save_weights(modelArgs[1])

(img_from_dir,img_to_dir) = mydataset.getmydatasetdir(0)
trainpaths = [[img_to_dir+'/numberAndX/X_train/']
    ,[img_to_dir+'/numberAndX/number_train/']]
testpaths = [[img_to_dir+'/numberAndX/X_test/']
    ,[img_to_dir+'/numberAndX/number_test/']]

train(trainpaths,testpaths)