# docker-registry-cleaner

Installation:
  virtualenv .
  ./bin/pip install -r requirements.txt

List images with outdated tags:
  ./bin/python docker-registry-cleaner.py registry.example.net

List all tags for a given image:
  ./bin/python docker-registry-cleaner.py registry.example.net image

Delete image tag(s):
  ./bin/python docker-registry-cleaner.py registry.example.net image tag1 tag2
