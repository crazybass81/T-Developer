#!/bin/bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
echo "$HOME/.cargo/bin" >> $GITHUB_PATH