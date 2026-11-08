Write-Host "Creating Conda environment ai-env..."
conda env create -f environment.yml -n ai-env 2>$null
if ($LASTEXITCODE -ne 0) {
    conda create -n ai-env python=3.12 -y
}
conda activate ai-env
python -m pip install --upgrade pip uv
uv pip install -r requirements.txt
Write-Host "Done. Activate with: conda activate ai-env"