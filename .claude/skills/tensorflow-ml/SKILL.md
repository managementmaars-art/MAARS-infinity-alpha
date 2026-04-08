---
name: tensorflow-ml
description: TensorFlow and Keras for custom training, SavedModel export, TF Serving, mixed precision, and distributed training.
---

# TensorFlow / Keras

## Overview

TensorFlow with Keras provides a high-level API for building and training models with first-class support for SavedModel export, TF Serving, TFLite, and distributed training strategies.

## Installation

```bash
pip install tensorflow[and-cuda]  # GPU support
pip install tensorflow-cpu         # CPU only
pip install tensorflow-datasets    # tfds
pip install keras                  # Standalone Keras 3
```

## Custom Model with Keras Functional API

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
import keras_tuner as kt

# Functional API (recommended for complex architectures)
def build_cnn_classifier(input_shape=(224, 224, 3), num_classes=10):
    inputs = keras.Input(shape=input_shape)

    # Feature extraction
    x = layers.Conv2D(32, 3, padding="same", use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.MaxPooling2D()(x)

    for filters in [64, 128, 256]:
        residual = x
        x = layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
        x = layers.BatchNormalization()(x)

        # Residual connection
        if residual.shape[-1] != filters:
            residual = layers.Conv2D(filters, 1, use_bias=False)(residual)
            residual = layers.BatchNormalization()(residual)

        x = layers.Add()([x, residual])
        x = layers.Activation("relu")(x)
        x = layers.MaxPooling2D()(x)

    # Classification head
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(512, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    return Model(inputs, outputs, name="cnn_classifier")


# Subclass API for complex logic
class TransformerEncoder(keras.Model):
    def __init__(self, d_model, num_heads, d_ff, num_layers, dropout_rate=0.1):
        super().__init__()
        self.embedding = layers.Embedding(vocab_size, d_model)
        self.pos_encoding = self.positional_encoding(max_len=512, d_model=d_model)
        self.enc_layers = [
            self.build_encoder_layer(d_model, num_heads, d_ff, dropout_rate)
            for _ in range(num_layers)
        ]
        self.dropout = layers.Dropout(dropout_rate)

    def build_encoder_layer(self, d_model, num_heads, d_ff, dropout_rate):
        return {
            "attn": layers.MultiHeadAttention(num_heads=num_heads, key_dim=d_model // num_heads),
            "ff": keras.Sequential([
                layers.Dense(d_ff, activation="gelu"),
                layers.Dropout(dropout_rate),
                layers.Dense(d_model),
            ]),
            "norm1": layers.LayerNormalization(epsilon=1e-6),
            "norm2": layers.LayerNormalization(epsilon=1e-6),
            "drop1": layers.Dropout(dropout_rate),
            "drop2": layers.Dropout(dropout_rate),
        }

    def call(self, x, training=False, mask=None):
        seq_len = tf.shape(x)[1]
        x = self.embedding(x)
        x += self.pos_encoding[:, :seq_len, :]
        x = self.dropout(x, training=training)

        for layer in self.enc_layers:
            attn_out = layer["attn"](x, x, attention_mask=mask)
            attn_out = layer["drop1"](attn_out, training=training)
            x = layer["norm1"](x + attn_out)
            ff_out = layer["ff"](x, training=training)
            ff_out = layer["drop2"](ff_out, training=training)
            x = layer["norm2"](x + ff_out)

        return x
```

## Custom Training Loop

```python
# Mixed precision setup
tf.keras.mixed_precision.set_global_policy("mixed_float16")

model = build_cnn_classifier()
optimizer = keras.optimizers.AdamW(learning_rate=1e-4, weight_decay=0.01)
loss_fn = keras.losses.SparseCategoricalCrossentropy()

train_acc = keras.metrics.SparseCategoricalAccuracy()
val_acc = keras.metrics.SparseCategoricalAccuracy()

@tf.function(jit_compile=True)  # XLA compilation for speed
def train_step(images, labels):
    with tf.GradientTape() as tape:
        predictions = model(images, training=True)
        loss = loss_fn(labels, predictions)
        # Scale for mixed precision
        scaled_loss = optimizer.get_scaled_loss(loss)

    scaled_gradients = tape.gradient(scaled_loss, model.trainable_variables)
    gradients = optimizer.get_unscaled_gradients(scaled_gradients)
    gradients, _ = tf.clip_by_global_norm(gradients, clip_norm=1.0)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    train_acc.update_state(labels, predictions)
    return loss

@tf.function
def val_step(images, labels):
    predictions = model(images, training=False)
    val_acc.update_state(labels, predictions)
    return loss_fn(labels, predictions)


# Training loop
for epoch in range(50):
    train_acc.reset_state()
    val_acc.reset_state()

    for step, (images, labels) in enumerate(train_dataset):
        loss = train_step(images, labels)

    for images, labels in val_dataset:
        val_step(images, labels)

    print(f"Epoch {epoch+1}: train_acc={train_acc.result():.4f}, val_acc={val_acc.result():.4f}")
```

## Keras Compile API with Callbacks

```python
model = build_cnn_classifier(num_classes=10)

model.compile(
    optimizer=keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=0.01),
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=[keras.metrics.SparseCategoricalAccuracy()],
    jit_compile=True,              # XLA
)

callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath="checkpoints/model_{epoch:02d}_{val_sparse_categorical_accuracy:.4f}.keras",
        monitor="val_sparse_categorical_accuracy",
        save_best_only=True,
        mode="max",
    ),
    keras.callbacks.EarlyStopping(
        monitor="val_sparse_categorical_accuracy",
        patience=10,
        restore_best_weights=True,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=5,
        min_lr=1e-7,
    ),
    keras.callbacks.TensorBoard(log_dir="./logs", histogram_freq=1),
    keras.callbacks.CSVLogger("training_log.csv"),
]

history = model.fit(
    train_dataset,
    epochs=100,
    validation_data=val_dataset,
    callbacks=callbacks,
    verbose=1,
)
```

## TF Data Pipeline

```python
import tensorflow_datasets as tfds
import tensorflow as tf

AUTOTUNE = tf.data.AUTOTUNE

def preprocess_image(image, label):
    image = tf.cast(image, tf.float32) / 255.0
    image = tf.image.resize(image, [224, 224])
    return image, label

def augment(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, max_delta=0.2)
    image = tf.image.random_contrast(image, 0.8, 1.2)
    image = tf.image.random_saturation(image, 0.8, 1.2)
    return image, label

# Build efficient pipeline
def build_dataset(raw_dataset, batch_size=32, is_train=True):
    ds = raw_dataset.map(preprocess_image, num_parallel_calls=AUTOTUNE)

    if is_train:
        ds = ds.shuffle(buffer_size=1000)
        ds = ds.map(augment, num_parallel_calls=AUTOTUNE)

    ds = ds.batch(batch_size)
    ds = ds.prefetch(AUTOTUNE)
    ds = ds.cache()  # Cache after expensive ops
    return ds

# Load with tensorflow_datasets
(ds_train, ds_val), info = tfds.load(
    "imagenet_resized/32x32",
    split=["train", "validation"],
    as_supervised=True,
    with_info=True,
)

train_dataset = build_dataset(ds_train, batch_size=256, is_train=True)
val_dataset = build_dataset(ds_val, batch_size=512, is_train=False)
```

## SavedModel & TF Serving

```python
# Save in SavedModel format
model.save("saved_model/my_model")          # Keras .keras format
tf.saved_model.save(model, "saved_model/")  # TF SavedModel

# With custom serving signature
@tf.function(input_signature=[tf.TensorSpec(shape=[None, 224, 224, 3], dtype=tf.float32)])
def serving_fn(inputs):
    outputs = model(inputs, training=False)
    return {"predictions": outputs, "class_ids": tf.argmax(outputs, axis=-1)}

tf.saved_model.save(
    model,
    "saved_model/",
    signatures={"serving_default": serving_fn},
)

# TFLite conversion for mobile
converter = tf.lite.TFLiteConverter.from_saved_model("saved_model/")
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Dynamic quantization
tflite_model = converter.convert()
with open("model.tflite", "wb") as f:
    f.write(tflite_model)

# INT8 quantization
def representative_dataset():
    for images, _ in val_dataset.take(100):
        yield [images]

converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.representative_dataset = representative_dataset
```

## Distributed Training

```python
# Multi-GPU training with MirroredStrategy
strategy = tf.distribute.MirroredStrategy()
print(f"Number of devices: {strategy.num_replicas_in_sync}")

with strategy.scope():
    model = build_cnn_classifier(num_classes=1000)
    model.compile(
        optimizer=keras.optimizers.AdamW(learning_rate=1e-3 * strategy.num_replicas_in_sync),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )

# Multi-node training with MultiWorkerMirroredStrategy
cluster_resolver = tf.distribute.cluster_resolver.TFConfigClusterResolver()
strategy = tf.distribute.MultiWorkerMirroredStrategy(cluster_resolver=cluster_resolver)

# TPU training
resolver = tf.distribute.cluster_resolver.TPUClusterResolver(tpu="")
tf.config.experimental_connect_to_cluster(resolver)
tf.tpu.experimental.initialize_tpu_system(resolver)
strategy = tf.distribute.TPUStrategy(resolver)
```

## Key Patterns

- **`@tf.function` + `jit_compile=True`** for XLA compilation — 2-5x speedup
- **`tf.data` pipelines** with `prefetch(AUTOTUNE)` and `cache()` eliminate GPU starvation
- **Mixed precision** (`mixed_float16`) halves memory use and speeds up training
- **`MirroredStrategy`** for single-machine multi-GPU with minimal code changes
- **SavedModel format** is the deployment-ready format for TF Serving and TFLite
- **Gradient clipping** is essential for transformer and RNN stability

## Models to Use

- **claude-opus-4-5**: Research paper implementations, distributed training architecture, custom ops
- **claude-sonnet-4-5**: Model building, training pipelines, SavedModel export
- **claude-haiku-3-5**: Simple Keras layers, callback additions, TFLite conversion
