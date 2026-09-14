import os
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add backend directory to sys.path to import modules
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_dir))

from app.services.ocr.ocr_service import extract_text

def test_dataset():
    console = Console()
    dataset_dir = Path(__file__).parent.parent / "datasets" / "MIDV-500"
    
    if not dataset_dir.exists() or not any(dataset_dir.iterdir()):
        console.print("[bold red]Dataset directory is empty or does not exist![/bold red]")
        console.print(f"Please run [bold]python scripts/setup_midv500.py[/bold] first and populate {dataset_dir}")
        return

    # Find first 10 images
    images = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.tif", "*.bmp"]:
        images.extend(list(dataset_dir.rglob(ext)))
        if len(images) >= 10:
            break
            
    images = images[:10]
    
    if not images:
        console.print(f"[bold red]No images found in {dataset_dir}[/bold red]")
        return
        
    table = Table(title="PaddleOCR MIDV-500 Benchmark (10 samples)")
    table.add_column("Filename", justify="left", style="cyan")
    table.add_column("Extracted Name", style="magenta")
    table.add_column("Confidence/Lines", justify="right", style="green")
    table.add_column("Time (s)", justify="right", style="yellow")
    
    total_time = 0
    for img_path in images:
        t0 = time.time()
        # Document ID is just the filename for this test
        response = extract_text(str(img_path), img_path.name)
        t1 = time.time()
        
        elapsed = t1 - t0
        total_time += elapsed
        
        # Get average confidence
        if response.detections:
            avg_conf = sum(d.confidence for d in response.detections) / len(response.detections)
        else:
            avg_conf = 0.0
            
        table.add_row(
            img_path.name,
            str(response.extracted_fields.name),
            f"{avg_conf:.2f} ({len(response.detections)} lines)",
            f"{elapsed:.2f}"
        )
        
    console.print(table)
    console.print(f"\n[bold]Total Time:[/bold] {total_time:.2f} seconds")
    console.print(f"[bold]Average Time per image:[/bold] {total_time/len(images):.2f} seconds")

if __name__ == "__main__":
    test_dataset()
