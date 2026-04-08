---
name: pytorch-ml
description: PyTorch model building, custom training loops, DataLoader pipelines, PyTorch Lightning, custom layers, and CUDA optimization.
---

# PyTorch Machine Learning

## Overview

PyTorch is the leading research and production deep learning framework. It provides dynamic computation graphs, CUDA acceleration, and a rich ecosystem including Lightning for structured training.

## Installation

```bash
# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CPU only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Lightning
pip install lightning
```

## Custom Model Architecture

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_k = d_model // num_heads
        self.num_heads = num_heads

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: Tensor, mask: Tensor = None) -> Tensor:
        B, T, C = x.shape

        qkv = self.qkv(x).reshape(B, T, 3, self.num_heads, self.d_k)
        q, k, v = qkv.permute(2, 0, 3, 1, 4).unbind(0)

        scale = self.d_k ** -0.5
        attn = (q @ k.transpose(-2, -1)) * scale

        if mask is not None:
            attn = attn.masked_fill(mask == 0, float("-inf"))

        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn)

        out = (attn @ v).transpose(1, 2).reshape(B, T, C)
        return self.out_proj(out)


class TransformerBlock(nn.Module):
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attn = MultiHeadSelfAttention(d_model, num_heads, dropout)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: Tensor, mask: Tensor = None) -> Tensor:
        # Pre-norm (more stable than post-norm)
        x = x + self.dropout(self.attn(self.norm1(x), mask))
        x = x + self.dropout(self.ff(self.norm2(x)))
        return x


class ImageClassifier(nn.Module):
    def __init__(self, num_classes: int = 1000, pretrained: bool = True):
        super().__init__()
        import torchvision.models as models

        backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT if pretrained else None)
        # Remove final classification layer
        self.features = nn.Sequential(*list(backbone.children())[:-1])

        # Custom classification head
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, x: Tensor) -> Tensor:
        features = self.features(x).flatten(1)
        return self.classifier(features)
```

## DataLoader Pipeline

```python
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd
import os

class ImageDataset(Dataset):
    def __init__(self, df: pd.DataFrame, img_dir: str, transform=None, is_train: bool = True):
        self.df = df
        self.img_dir = img_dir
        self.transform = transform or self.default_transform(is_train)

    def default_transform(self, is_train: bool):
        if is_train:
            return transforms.Compose([
                transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.RandomGrayscale(p=0.1),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        image = Image.open(os.path.join(self.img_dir, row["filename"])).convert("RGB")
        image = self.transform(image)
        label = torch.tensor(row["label"], dtype=torch.long)
        return image, label


def create_dataloaders(df, img_dir, batch_size=32, num_workers=4):
    train_df = df[df["split"] == "train"]
    val_df = df[df["split"] == "val"]

    train_dataset = ImageDataset(train_df, img_dir, is_train=True)
    val_dataset = ImageDataset(val_df, img_dir, is_train=False)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,        # Faster GPU transfer
        persistent_workers=True,
        prefetch_factor=2,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size * 2,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True,
    )
    return train_loader, val_loader
```

## Training Loop (Manual)

```python
import torch
from torch.cuda.amp import GradScaler, autocast
from torch.optim.lr_scheduler import OneCycleLR

def train_epoch(model, loader, optimizer, criterion, scaler, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad(set_to_none=True)  # Faster than zero_grad()

        # Mixed precision training
        with autocast():
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

    return total_loss / len(loader), correct / total


def train(model, train_loader, val_loader, epochs=50, device="cuda"):
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
    scheduler = OneCycleLR(optimizer, max_lr=1e-3, epochs=epochs, steps_per_epoch=len(train_loader))
    scaler = GradScaler()

    best_val_acc = 0
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, scaler, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        print(f"Epoch {epoch+1}/{epochs}: Train {train_acc:.3f} | Val {val_acc:.3f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": val_acc,
            }, "best_model.pt")
```

## PyTorch Lightning

```python
import lightning as L
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
from lightning.pytorch.loggers import WandbLogger

class LightningModel(L.LightningModule):
    def __init__(self, num_classes: int, lr: float = 1e-4):
        super().__init__()
        self.save_hyperparameters()
        self.model = ImageClassifier(num_classes=num_classes)
        self.criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
        self.train_acc = torchmetrics.Accuracy(task="multiclass", num_classes=num_classes)
        self.val_acc = torchmetrics.Accuracy(task="multiclass", num_classes=num_classes)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        self.train_acc(logits.softmax(dim=-1), y)
        self.log_dict({"train/loss": loss, "train/acc": self.train_acc}, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        self.val_acc(logits.softmax(dim=-1), y)
        self.log_dict({"val/loss": loss, "val/acc": self.val_acc}, on_epoch=True, prog_bar=True)

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.hparams.lr, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
        return {"optimizer": optimizer, "lr_scheduler": scheduler}


def run_training():
    model = LightningModel(num_classes=10)

    trainer = L.Trainer(
        max_epochs=100,
        precision="16-mixed",          # AMP
        accelerator="auto",
        devices="auto",
        strategy="ddp",                 # Multi-GPU
        callbacks=[
            ModelCheckpoint(monitor="val/acc", mode="max", save_top_k=3),
            EarlyStopping(monitor="val/acc", patience=10, mode="max"),
            LearningRateMonitor(),
        ],
        logger=WandbLogger(project="my-project"),
        gradient_clip_val=1.0,
        accumulate_grad_batches=4,      # Effective batch size * 4
        log_every_n_steps=10,
    )

    trainer.fit(model, train_loader, val_loader)
    trainer.test(model, test_loader, ckpt_path="best")
```

## CUDA Optimization

```python
# Compile model for faster inference (PyTorch 2.0+)
model = torch.compile(model)

# TorchScript for deployment
scripted_model = torch.jit.script(model)
scripted_model.save("model.pt")

# Memory-efficient inference
@torch.inference_mode()  # Faster than no_grad
def predict(model, images, device):
    model.eval()
    images = images.to(device, non_blocking=True)
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        outputs = model(images)
    return outputs.cpu()

# Profile GPU memory
print(torch.cuda.memory_summary(device=None, abbreviated=False))
torch.cuda.empty_cache()  # Free cached memory

# Multi-GPU with DataParallel (simple) or DDP (preferred)
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)
```

## Key Patterns

- **`pin_memory=True`** + `non_blocking=True` for faster CPU-GPU transfers
- **Mixed precision** (`torch.autocast`) gives 2-3x speedup on Ampere+ GPUs
- **`torch.compile()`** (PyTorch 2.0+) provides 20-40% speedup with no code changes
- **`set_to_none=True`** in `zero_grad` is faster than setting to zeros
- **Lightning** handles distributed training, checkpointing, and logging boilerplate
- **Gradient clipping** prevents training instability in transformers

## Models to Use

- **claude-opus-4-5**: Novel architecture design, research paper implementation, distributed training
- **claude-sonnet-4-5**: Custom layers, training loops, Lightning module development
- **claude-haiku-3-5**: Simple model modifications, hyperparameter changes, data preprocessing
