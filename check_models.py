from transformers import TRANSFORMERS_CACHE
import os

# Print the path of the cache directory
print(f"Cache directory: {TRANSFORMERS_CACHE}")

# List all the items in the cache directory
for item in os.listdir(TRANSFORMERS_CACHE):
    if os.path.isdir(os.path.join(TRANSFORMERS_CACHE, item)):
        print(item)