import tensorflow as tf
from tensorflow import keras

def import_data():

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(5,1)),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(2, activation=tf.nn.softmax)
])

model.fit(training_data, training_labels, epochs=5)
test_loss, test_acc = model.evaluate(test_data, test_labels)

predictions = model.predict(input)